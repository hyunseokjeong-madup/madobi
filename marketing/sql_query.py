"""
sql_query — DuckDB 공존(coexistence) 레이어 (ChatGPT 제안 구현).

DuckDB 가 있으면 SQL 로 빠르게 GROUP BY 집계하고, 없으면 stdlib csv 로 같은
계산을 파이썬에서 수행한다. 핵심 불변식:
  - 공식은 단 하나 — marketing/safemath.py (78개 도구의 source of truth)
  - 지표 '정의'는 marketing/semantic_layer.py 가 SQL 식으로 보유
  - DuckDB 는 '추가 교차검증기'일 뿐, 불일치 시 파이썬이 진실(source of truth)

비율지표는 SUM(a)/SUM(b) 가중평균으로 계산(단순 AVG(ratio) = Simpson 함정, 금지).

DuckDB 없이도 import·동작한다(소량 데이터 한정 stdlib 폴백).
parquet 은 DuckDB 필요 — 없으면 명확히 에러.

  python marketing/sql_query.py marketing/samples/sample_campaign.csv --group-by creative --metric roas
  python marketing/sql_query.py <csv> --group-by channel --metric roas cpa --verify
"""
import csv
import sys
import argparse
from pathlib import Path
from collections import defaultdict

try:
    from . import safemath, semantic_layer
except ImportError:  # 스크립트 직접 실행
    import safemath
    import semantic_layer

# duckdb 는 가드된 옵셔널 의존성. 없어도 모듈은 import·동작해야 한다.
try:
    import duckdb  # noqa: F401
    HAS_DUCKDB = True
except ImportError:
    duckdb = None
    HAS_DUCKDB = False


_NO_DUCKDB_MSG = (
    "duckdb not installed — pip install madobi[duckdb] "
    "(또는 stdlib 폴백 사용: engine='python')"
)


# ----------------------------------------------------------------------------
# 공통: 용어 → canonical 지표 해석 (semantic_layer 경유, 표류 방지)
# ----------------------------------------------------------------------------
def _resolve_metrics(metrics):
    """비즈니스 용어 리스트 → canonical 지표명 리스트."""
    return [semantic_layer.canonical(m) for m in metrics]


# ----------------------------------------------------------------------------
# STDLIB 경로 — csv 로 읽어 group-by 를 파이썬에서 (source of truth)
# ----------------------------------------------------------------------------
def _query_python(path, group_by, filters, metrics):
    """순수 stdlib CSV 집계. raw 는 SUM, 파생은 safemath 공식(가중평균).

    반환: 행 리스트. 각 행 = {그룹컬럼...: 값, 지표명: 값}. 그룹키로 정렬.
    """
    path = Path(path)
    if path.suffix.lower() in (".parquet", ".pq"):
        raise RuntimeError(
            f"parquet 은 DuckDB 가 필요합니다(stdlib 불가): {path}. {_NO_DUCKDB_MSG}"
        )

    acc = defaultdict(lambda: {m: 0 for m in safemath._RAW_ALIASES})
    all_rows = safemath.load_rows(path)   # 파일 없음/빈 데이터/cp949 를 한 줄 안내로 처리
    colmap = safemath.map_headers(all_rows[0].keys())   # canonical → 원본 헤더 (대소문자 무시)
    for r in all_rows:
        if not _passes_filters(r, filters):
            continue
        # 합계 행 제외 — 판정은 safemath.is_total_label 공용 기준.
        # 과거 5종 완전일치는 'Grand Total' 을 못 걸러 2배 이중계산됐다.
        label = next(iter(r.values()), "")
        if safemath.is_total_label(label):
            continue
        key = tuple(_cell(r, g) for g in group_by) if group_by else ("ALL",)
        for m in safemath._RAW_ALIASES:
            src = colmap.get(m)
            v = safemath._finite(_clean(r.get(src))) if src else None
            acc[key][m] += v if v is not None else 0.0

    rows = []
    for key in sorted(acc):
        raw = acc[key]
        derived = safemath.recompute_metrics(raw)
        row = {g: key[i] for i, g in enumerate(group_by)}
        for m in metrics:
            if m in safemath._RAW_ALIASES:
                row[m] = raw[m]
            else:
                row[m] = derived.get(m)  # 분모 0이면 None
        rows.append(row)
    return rows


def _clean(s):
    """콤마/통화/퍼센트 기호 제거 후 문자열 반환(숫자 캐스팅은 _finite 가 처리)."""
    if s is None:
        return None
    s = str(s).strip().replace(",", "").replace("₩", "").replace("$", "").replace("%", "")
    if s in ("", "-", "—", "N/A", "na", "NaN"):
        return None
    return s


def _cell(row, col):
    return (row.get(col) or "").strip()


def _passes_filters(row, filters):
    """filters: {col: value} 동등, {col: set/list/tuple} 포함, {col: callable} 술어."""
    for col, cond in (filters or {}).items():
        v = _cell(row, col)
        if callable(cond):
            if not cond(v):
                return False
        elif isinstance(cond, (set, list, tuple)):
            if v not in cond:
                return False
        else:
            if v != str(cond):
                return False
    return True


# ----------------------------------------------------------------------------
# DUCKDB 경로 — semantic_layer 의 SQL 식으로 GROUP BY (옵셔널 교차검증기)
# ----------------------------------------------------------------------------
def _query_duckdb(path, group_by, filters, metrics):
    """DuckDB 로 CSV/parquet 을 직접 스캔하여 집계. 없으면 RuntimeError."""
    if not HAS_DUCKDB:
        raise RuntimeError(_NO_DUCKDB_MSG)

    path = Path(path)
    if path.suffix.lower() in (".parquet", ".pq"):
        src = f"read_parquet('{path.as_posix()}')"
    else:
        # all_varchar 로 읽어 콤마/통화 포맷을 우리가 직접 정제(엔진 추론 불일치 방지)
        src = f"read_csv_auto('{path.as_posix()}', all_varchar=true)"

    # 포맷 셀 정제 SQL: 콤마/₩/$/% 제거 후 DOUBLE 캐스팅, 실패/빈값은 0.
    def cleaned(colexpr_inner):
        return colexpr_inner

    # raw 컬럼을 정제한 CTE 를 만들고, 그 위에서 SUM(...) 집계.
    raw_cols = list(safemath._RAW_ALIASES)
    clean_exprs = []
    for rc in raw_cols:
        # 존재하는 alias 중 첫 컬럼을 COALESCE 로 선택
        aliases = safemath._RAW_ALIASES[rc]
        # 실제 존재하는 컬럼만 참조하기 위해 컬럼 목록을 먼저 조회
        clean_exprs.append((rc, aliases))

    cols = _duckdb_columns(src)
    lowcols = {str(c).lower().strip(): c for c in cols}   # 대소문자 무시 (python 엔진과 동일 규칙)
    select_clean = []
    for rc, aliases in clean_exprs:
        present = [lowcols[a] for a in aliases if a in lowcols]
        if present:
            col = present[0]
            expr = (f"COALESCE(TRY_CAST(NULLIF(REGEXP_REPLACE("
                    f"CAST(\"{col}\" AS VARCHAR), '[,₩$%]', '', 'g'), '') AS DOUBLE), 0) AS {rc}")
        else:
            expr = f"0.0 AS {rc}"
        select_clean.append(expr)

    # 그룹 컬럼도 패스스루 — 식별자는 항상 인용(공백/특수문자 컬럼명 안전)
    gq = ['"' + g.replace('"', '""') + '"' for g in group_by]
    group_select = ", ".join(f"{q} AS {q}" for q in gq)
    base_select = ", ".join(select_clean)
    if group_by:
        base = f"SELECT {group_select}, {base_select} FROM {src}"
    else:
        base = f"SELECT {base_select} FROM {src}"

    # 합계 행 제외(첫 컬럼이 total/합계 류)
    first_col = cols[0] if cols else None
    where = _build_where(filters, group_by, first_col)

    # 집계 SELECT 구성: 그룹 + 각 지표 SQL 식
    agg_select = list(gq)
    for m in metrics:
        agg_select.append(f"({semantic_layer.sql_for(m)}) AS {m}")
    group_clause = f"GROUP BY {', '.join(gq)}" if group_by else ""
    order_clause = f"ORDER BY {', '.join(gq)}" if group_by else ""

    sql = (
        f"WITH base AS ({base}{where}) "
        f"SELECT {', '.join(agg_select)} FROM base {group_clause} {order_clause}"
    )

    con = duckdb.connect()
    try:
        cur = con.execute(sql)
        colnames = [d[0] for d in cur.description]
        out = [dict(zip(colnames, r)) for r in cur.fetchall()]
    finally:
        con.close()
    return out


def _duckdb_columns(src):
    con = duckdb.connect()
    try:
        cur = con.execute(f"SELECT * FROM {src} LIMIT 0")
        return [d[0] for d in cur.description]
    finally:
        con.close()


def _build_where(filters, group_by, first_col):
    clauses = []
    # 합계 행 제외 — python 엔진의 safemath.is_total_label 과 동일 규칙을 SQL 로 이식
    # ('Grand Total' 누락 + 'Summer_Sale' 오폐기 를 모두 막는 정규화 후 전체 일치).
    if first_col:
        fq = '"' + str(first_col).replace('"', '""') + '"'
        clauses.append(
            f"NOT regexp_matches(regexp_replace(lower(trim(CAST({fq} AS VARCHAR))), "
            f"'{safemath.TOTAL_LABEL_STRIP_PATTERN}', '', 'g'), "
            f"'{safemath.TOTAL_LABEL_SQL_PATTERN}')"
        )
    for col, cond in (filters or {}).items():
        if callable(cond):
            # callable 필터는 SQL 로 못 옮김 → DuckDB 경로에서는 미지원(파이썬에서만).
            raise RuntimeError(
                "callable 필터는 DuckDB 경로에서 지원하지 않습니다(engine='python' 사용)."
            )
        if isinstance(cond, (set, list, tuple)):
            vals = ", ".join("'" + str(v).replace("'", "''") + "'" for v in cond)
            clauses.append(f"CAST(\"{col}\" AS VARCHAR) IN ({vals})")
        else:
            v = str(cond).replace("'", "''")
            clauses.append(f"CAST(\"{col}\" AS VARCHAR) = '{v}'")
    return (" WHERE " + " AND ".join(clauses)) if clauses else ""


# ----------------------------------------------------------------------------
# 공개 API
# ----------------------------------------------------------------------------
def _columns(path):
    """파일의 헤더 컬럼 목록. CSV 는 첫 줄만 읽음(utf-8-sig→cp949), parquet 은 duckdb."""
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"[오류] 파일 없음: {path}")
    if path.suffix.lower() in (".parquet", ".pq"):
        if not HAS_DUCKDB:
            raise RuntimeError(_NO_DUCKDB_MSG)
        return _duckdb_columns(f"read_parquet('{path.as_posix()}')")
    head = path.read_bytes().split(b"\n", 1)[0]
    for enc in ("utf-8-sig", "cp949"):
        try:
            return next(csv.reader([head.decode(enc)]), [])
        except UnicodeDecodeError:
            continue
    raise SystemExit(f"[오류] CSV 인코딩 인식 불가(utf-8/cp949 모두 실패): {path}")


def _validate_group_by(path, group_by):
    """group-by 컬럼 실재 검증 — 없는 컬럼이면 두 엔진이 '같은 방식으로' 실패해야 한다.

    과거: python 엔진은 조용히 빈 라벨 단일 그룹(무의미한 답), duckdb 는 BinderException
    traceback — 같은 입력에 다른 결과 클래스를 내 '파이썬이 진실' 불변식의 신뢰를 깎았다."""
    if not group_by:
        return
    cols = _columns(path)
    missing = [g for g in group_by if g not in cols]
    if missing:
        raise ValueError(f"group-by 컬럼 없음: {missing} — 사용 가능한 컬럼: {cols}")


def query(path, group_by=None, filters=None, metrics=None, engine="auto"):
    """CSV/parquet 위에서 GROUP BY 집계.

    engine: 'auto'(duckdb 있으면 duckdb, 없으면 python) | 'duckdb' | 'python'.
    group_by: 그룹 컬럼명 리스트. filters: {col: value|set|callable}.
    metrics: 비즈니스 용어 리스트(semantic_layer 로 canonical 해석).
    반환: 행 dict 리스트. 그룹 컬럼 + 각 지표값(파생 분모 0 → None).
    모르는 metric 은 KeyError, 없는 group-by 컬럼은 ValueError (양 엔진 동일).
    """
    group_by = list(group_by or [])
    filters = dict(filters or {})
    metrics = _resolve_metrics(metrics or ["roas"])
    _validate_group_by(path, group_by)

    if engine == "duckdb" or (engine == "auto" and HAS_DUCKDB):
        return _query_duckdb(path, group_by, filters, metrics)
    if engine == "duckdb" and not HAS_DUCKDB:
        raise RuntimeError(_NO_DUCKDB_MSG)
    return _query_python(path, group_by, filters, metrics)


def verify_against_python(path, group_by=None, filters=None, metrics=None, tol=None):
    """삼중 검증 게이트: DuckDB 경로 와 파이썬 경로를 둘 다 돌려 일치 확인.

    파이썬이 진실(source of truth). 불일치 시 raise (게이트가 막는다).
    DuckDB 가 없으면 검증 불가 → {'verified': None, ...} 로 안전 degrade.
    각 지표는 safemath.close(metric=...) 의 지표별 허용오차로 비교.
    """
    group_by = list(group_by or [])
    filters = dict(filters or {})
    canon = _resolve_metrics(metrics or ["roas"])
    _validate_group_by(path, group_by)

    py = _query_python(path, group_by, filters, canon)
    if not HAS_DUCKDB:
        return {
            "verified": None,
            "reason": "duckdb 미설치 — 교차검증 건너뜀, 파이썬 결과만 신뢰",
            "python": py,
            "duckdb": None,
            "mismatches": [],
        }

    dk = _query_duckdb(path, group_by, filters, canon)

    # 그룹키로 정렬·정렬키 맞춰 비교
    def keyf(row):
        return tuple(str(row.get(g)) for g in group_by)

    py_by = {keyf(r): r for r in py}
    dk_by = {keyf(r): r for r in dk}

    mismatches = []
    all_keys = sorted(set(py_by) | set(dk_by))
    for k in all_keys:
        pr = py_by.get(k)
        dr = dk_by.get(k)
        if pr is None or dr is None:
            mismatches.append({"group": k, "metric": "<row>",
                               "python": pr, "duckdb": dr,
                               "reason": "한쪽에만 존재하는 그룹"})
            continue
        for m in canon:
            pv, dv = pr.get(m), dr.get(m)
            ok = safemath.close(pv, dv, metric=m, tol=tol)
            if ok is False:
                mismatches.append({"group": k, "metric": m,
                                   "python": pv, "duckdb": dv})
            # ok is None (한쪽 None) 은 '둘 다 정의 안 됨'이 아니면 점검
            elif ok is None and not (pv is None and dv in (None, 0) or dv is None and pv in (None, 0)):
                mismatches.append({"group": k, "metric": m,
                                   "python": pv, "duckdb": dv,
                                   "reason": "비교 불가(한쪽만 None)"})

    if mismatches:
        raise AssertionError(
            f"verify_against_python: DuckDB↔Python 불일치 {len(mismatches)}건 "
            f"(파이썬이 진실): {mismatches[:5]}"
        )

    return {
        "verified": True,
        "reason": f"{len(all_keys)} 그룹 × {len(canon)} 지표 일치(허용오차 내)",
        "python": py,
        "duckdb": dk,
        "mismatches": [],
    }


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def _fmt(v):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:,.4f}".rstrip("0").rstrip(".") if v != int(v) else f"{int(v):,}"
    return str(v)


def main(argv=None):
    ap = argparse.ArgumentParser(description="DuckDB 공존 SQL 집계 (없으면 stdlib 폴백)")
    ap.add_argument("path", help="CSV 또는 parquet 경로")
    ap.add_argument("--group-by", nargs="*", default=[], help="그룹 컬럼들")
    ap.add_argument("--metric", nargs="*", default=["roas"], help="비즈니스 용어(roas, cpa, 전환...)")
    ap.add_argument("--filter", nargs="*", default=[], help="col=value 형식 필터(반복 가능)")
    ap.add_argument("--engine", choices=["auto", "duckdb", "python"], default="auto")
    ap.add_argument("--verify", action="store_true", help="DuckDB↔Python 삼중 검증 게이트 실행")
    a = ap.parse_args(argv)

    filters = {}
    for f in a.filter:
        if "=" in f:
            col, val = f.split("=", 1)
            filters[col.strip()] = val.strip()

    mode = "duckdb" if (a.engine == "duckdb" or (a.engine == "auto" and HAS_DUCKDB)) else "python"
    print(f"=== SQL QUERY  (engine={mode}, duckdb={'present' if HAS_DUCKDB else 'absent'}) ===")
    print(f"path={a.path}  group_by={a.group_by}  metric={a.metric}  filter={filters}")

    try:
        rows = query(a.path, group_by=a.group_by, filters=filters,
                     metrics=a.metric, engine=a.engine)
    except (KeyError, ValueError) as e:
        # 모르는 지표/없는 컬럼은 traceback 대신 usage + 한 줄 안내 (semantic_layer 의
        # KeyError 메시지가 이미 known metrics 목록을 포함한다).
        ap.error(str(e))

    cols = list(a.group_by) + _resolve_metrics(a.metric)
    print("  " + "  ".join(c.ljust(14) for c in cols))
    for r in rows:
        print("  " + "  ".join(_fmt(r.get(c)).ljust(14) for c in cols))

    if a.verify:
        print("\n=== TRIPLE VERIFICATION GATE (DuckDB ↔ Python) ===")
        res = verify_against_python(a.path, group_by=a.group_by,
                                    filters=filters, metrics=a.metric)
        if res["verified"] is True:
            print(f"  ✅ VERIFIED — {res['reason']}")
        elif res["verified"] is None:
            print(f"  ⚠️  SKIPPED — {res['reason']}")
        else:
            print(f"  ❌ MISMATCH — {res['mismatches']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
