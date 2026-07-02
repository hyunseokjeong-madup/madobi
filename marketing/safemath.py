"""
safemath — 수치 안정성 + 지표별 허용오차 헬퍼 (stdlib 전용).

reconcile.py 의 검산 로직을 라이브러리로 떼어낸 ADDITIVE 모듈.
reconcile.py 는 그대로 동작하고, 새 도구가 원하면 여기 함수를 골라 쓴다.

핵심:
  - safe_div : 0/0, x/0, inf, nan 을 터지지 않고 default 로 흡수
  - pct      : 안전 퍼센트 (part/whole*100)
  - DEFAULT_TOL / close : 지표별 상대허용오차 비교
  - recompute_metrics : raw(노출/클릭/비용/전환/매출) → 파생지표 dict
  - is_total_label : 합계행 판정 단일 기준 (도구 간 표류 방지)
  - map_headers / load_rows : 헤더 alias 매핑 · 견고한 CSV 로더 (utf-8-sig→cp949)

의존성 0개. duckdb 같은 외부 모듈은 절대 import 하지 않는다.

  python marketing/safemath.py        # 인라인 자가검증 실행
"""
import csv
import math
import re
from pathlib import Path


def _finite(x):
    """float 로 캐스팅 가능하고 유한한 값이면 float, 아니면 None."""
    if x is None:
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def safe_div(num, den, default=0.0):
    """안전 나눗셈.

    0/0, x/0, inf/x, x/inf, nan 등 어떤 경우에도 예외 없이 default 반환.
    num/den 둘 다 유한한 실수이고 den!=0 이며 결과가 유한할 때만 몫을 돌려준다.
    default=None 으로 주면 '계산 불가'를 None 으로 표현할 수 있다.
    """
    n = _finite(num)
    d = _finite(den)
    if n is None or d is None or d == 0:
        return default
    q = n / d
    if math.isnan(q) or math.isinf(q):
        return default
    return q


def pct(part, whole, default=0.0):
    """안전 퍼센트: part/whole*100. whole 가 0/nan/inf 면 default."""
    r = safe_div(part, whole, default=None)
    if r is None:
        return default
    return r * 100.0


# 지표별 상대 허용오차. ratio 계열(ctr/cvr/roas)은 빡빡하게, 금액 계열은 느슨하게.
DEFAULT_TOL = {
    "ctr": 1e-4,
    "cvr": 1e-4,
    "roas": 1e-4,
    "ecpm": 0.01,
    "cpa": 0.01,
    "cpc": 0.01,
    "cpm": 0.01,
}
# 지표를 모르거나 DEFAULT_TOL 에 없을 때 쓰는 기본 허용오차.
FALLBACK_TOL = 0.01


def tol_for(metric=None):
    """지표명으로 허용오차 조회 (대소문자 무시). 없으면 FALLBACK_TOL."""
    if metric is None:
        return FALLBACK_TOL
    return DEFAULT_TOL.get(str(metric).lower(), FALLBACK_TOL)


def close(a, b, metric=None, tol=None):
    """지표 인식 근사 비교.

    상대오차 |a-b| / max(|a|,|b|,1e-9) <= tol 이면 True.
    tol 미지정 시 metric 으로 DEFAULT_TOL 조회 (reconcile.py 의 close 와 동일 척도).
    a 나 b 가 None/nan/inf 면 비교 불가 → None 반환(= reconcile.py 관례).
    """
    fa = _finite(a)
    fb = _finite(b)
    if fa is None or fb is None:
        return None
    t = tol if tol is not None else tol_for(metric)
    denom = max(abs(fa), abs(fb), 1e-9)
    return abs(fa - fb) / denom <= t


# --- 합계행 판정 (도구 공통 단일 기준) --------------------------------------
# 과거엔 도구마다 기준이 달랐다: reconcile/report/summarize/analyze_creatives 는
# re.search(부분문자열)라 'Summer_Sale' 이 'sum' 에 걸려 조용히 폐기됐고,
# sql_query 는 5종 완전일치라 'Grand Total' 을 못 걸러 2배 이중계산됐다.
# → 정규화(공백/구분자/콜론 제거 + lower) 후 전체 일치만 인정. 전 도구가 이 함수를 쓴다.
_TOTAL_PAT = r"(grand)?(sub)?(totals?|sum)|총?(합계|총계|소계|총합)"


def is_total_label(label):
    """라벨이 합계/총계/소계 행인지 판정. 'Summer_Sale' 같은 실데이터는 절대 안 걸림."""
    s = re.sub(r"[\s_:\-–—]+", "", str(label or "").strip().lower())
    return bool(re.fullmatch(_TOTAL_PAT, s))


# duckdb 등 SQL 경로가 같은 규칙을 이식할 때 쓰는 원형 패턴 (regexp_replace 후 fullmatch).
TOTAL_LABEL_SQL_PATTERN = "^(" + _TOTAL_PAT + ")$"
TOTAL_LABEL_STRIP_PATTERN = r"[\s_:\-]+"


# recompute_metrics 가 raw 에서 읽는 키 (reconcile.py RAW 와 동일 의미).
# 단일 소스: reconcile.ALIASES 의 raw 부분도 여기서 가져다 쓴다 (표류 방지).
_RAW_ALIASES = {
    "impressions": ("impressions", "impr", "imp", "노출", "노출수"),
    "clicks": ("clicks", "click", "클릭", "클릭수"),
    "spend": ("spend", "cost", "비용", "광고비", "spend(krw)", "cost(krw)"),
    "conversions": ("conversions", "conv", "conversion", "전환", "전환수",
                    "installs", "purchases"),
    "revenue": ("revenue", "rev", "매출", "수익", "sales"),
}


def map_headers(headers):
    """헤더 목록 → {canonical: 원본 헤더}. 대소문자/양끝공백 무시.

    report/summarize 가 'Impressions'·'노출'·'cost' 같은 실무 헤더를
    조용히 0 으로 만들지 않도록, 집계 전에 이걸로 매핑하고 미매핑을 표면화한다."""
    low = {str(h).lower().strip(): h for h in headers if h is not None}
    out = {}
    for key, aliases in _RAW_ALIASES.items():
        for a in aliases:
            if a in low:
                out[key] = low[a]
                break
    return out


def load_rows(path):
    """견고한 CSV 로더 — traceback 대신 한 줄 한국어 안내로 종료.

    - 파일 없음 → SystemExit("[오류] 파일 없음: ...")
    - 인코딩: utf-8-sig 우선(BOM 제거), 실패 시 cp949(엑셀 한국어 기본 저장) 재시도
    - 데이터 행 0개 → SystemExit (헤더만 있는 export 등)
    """
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"[오류] 파일 없음: {path}")
    try:
        text = p.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = p.read_text(encoding="cp949")
        except UnicodeDecodeError:
            raise SystemExit(f"[오류] CSV 인코딩 인식 불가(utf-8/cp949 모두 실패): {path}")
    rows = list(csv.DictReader(text.splitlines()))
    if not rows:
        raise SystemExit(f"[오류] CSV에 데이터 행이 없습니다: {path}")
    return rows


def _pick(row, key):
    """row 에서 alias 들을 훑어 첫 유한값을 float 로. 없으면 None.

    헤더 대소문자/양끝공백 무시 — 'Impressions'/'Spend ' 도 인식 (과거엔 조용히 0)."""
    low = {str(k).lower().strip(): v for k, v in row.items() if k is not None}
    for a in _RAW_ALIASES[key]:
        if a in low:
            v = _finite(low[a])
            if v is not None:
                return v
    return None


def recompute_metrics(row):
    """raw → 파생지표 dict (reconcile.py derive 와 같은 정의, 전부 safe_div).

    입력 row: impressions/clicks/spend/conversions/revenue (또는 한글/약어 alias).
    반환: ctr/cpc/cpm/cpa/cvr/roas/ecpm 중 계산 가능한 것만.
      - ctr  = clicks / impressions            (분수, 0.03 = 3%)
      - cpc  = spend  / clicks
      - cpm  = spend  / impressions * 1000
      - cpa  = spend  / conversions
      - cvr  = conversions / clicks
      - roas = revenue / spend
      - ecpm = revenue / impressions * 1000
    분모가 0/None 인 지표는 키 자체를 생략(잘못된 0 을 만들지 않음).
    """
    imp = _pick(row, "impressions")
    clk = _pick(row, "clicks")
    sp = _pick(row, "spend")
    cv = _pick(row, "conversions")
    rv = _pick(row, "revenue")

    out = {}
    # 분모로 쓸 값이 양수일 때만 지표를 만든다. safe_div 가 default 로 흡수하지만
    # '의미 있는 분모'가 없으면 키를 빼서 reconcile 의 derive() 와 동작을 맞춘다.
    if imp and clk is not None:
        out["ctr"] = safe_div(clk, imp)
    if clk and sp is not None:
        out["cpc"] = safe_div(sp, clk)
    if imp and sp is not None:
        out["cpm"] = safe_div(sp, imp) * 1000.0
    if cv and sp is not None:
        out["cpa"] = safe_div(sp, cv)
    if clk and cv is not None:
        out["cvr"] = safe_div(cv, clk)
    if sp and rv is not None:
        out["roas"] = safe_div(rv, sp)
    if imp and rv is not None:
        out["ecpm"] = safe_div(rv, imp) * 1000.0
    return out


def _selftest():
    """인라인 자가검증: 0/0, x/0, 정상, 지표 허용오차, recompute. 실패 시 AssertionError."""
    inf = float("inf")
    nan = float("nan")

    # --- safe_div: 위험 케이스 전부 default 로 흡수 ---
    assert safe_div(0, 0) == 0.0, "0/0"
    assert safe_div(5, 0) == 0.0, "x/0"
    assert safe_div(5, 0, default=None) is None, "x/0 default=None"
    assert safe_div(1, inf) == 0.0, "1/inf"
    assert safe_div(inf, 1) == 0.0, "inf/1"
    assert safe_div(nan, 1) == 0.0, "nan/1"
    assert safe_div(1, nan) == 0.0, "1/nan"
    assert safe_div("10", "4") == 2.5, "string numerics"
    assert safe_div(7, 2) == 3.5, "normal"
    assert safe_div(-6, 3) == -2.0, "negative"

    # --- pct ---
    assert pct(0, 0) == 0.0, "pct 0/0"
    assert pct(36, 1200) == 3.0, "pct normal (36/1200=3%)"
    assert pct(1, 0, default=-1.0) == -1.0, "pct x/0 default"

    # --- close: 지표 인식 ---
    # ctr 허용오차 1e-4: 0.03 vs 0.0300001 은 같다고 봐야 함
    assert close(0.03, 0.0300001, metric="ctr") is True, "ctr within tol"
    # cpa 허용오차 0.01(1%): 10000 vs 10050 은 0.5% → 같음
    assert close(10000, 10050, metric="cpa") is True, "cpa within 1%"
    # 같은 두 값이라도 ctr(1e-4)에선 다르고 cpa(1%)에선 같다 — 지표 인식 증명
    assert close(0.03, 0.0303, metric="ctr") is False, "ctr 1% diff fails tight tol"
    assert close(0.03, 0.0303, metric="cpa") is True, "cpa 1% diff passes loose tol"
    # 미지정 metric → FALLBACK_TOL(1%)
    assert close(100, 100.5, metric=None) is True, "fallback tol"
    # None/inf → 비교 불가
    assert close(None, 1, metric="ctr") is None, "None -> None"
    assert close(inf, 1, metric="ctr") is None, "inf -> None"
    # 명시 tol 이 metric 보다 우선
    assert close(0.03, 0.0303, metric="ctr", tol=0.05) is True, "explicit tol overrides"

    # --- recompute_metrics: 실제 캠페인 행 ---
    row = {"impressions": "120,000".replace(",", ""), "clicks": "3600",
           "spend": "1800000", "conversions": "180", "revenue": "5400000"}
    m = recompute_metrics(row)
    assert close(m["ctr"], 0.03, metric="ctr"), f"ctr {m['ctr']}"      # 3600/120000
    assert close(m["cpc"], 500.0, metric="cpc"), f"cpc {m['cpc']}"     # 1.8M/3600
    assert close(m["cpm"], 15000.0, metric="cpm"), f"cpm {m['cpm']}"   # 1.8M/120k*1000
    assert close(m["cpa"], 10000.0, metric="cpa"), f"cpa {m['cpa']}"   # 1.8M/180
    assert close(m["cvr"], 0.05, metric="cvr"), f"cvr {m['cvr']}"      # 180/3600
    assert close(m["roas"], 3.0, metric="roas"), f"roas {m['roas']}"   # 5.4M/1.8M

    # --- recompute_metrics: 0 분모는 키를 생략, 절대 안 터짐 ---
    zero = {"impressions": 0, "clicks": 0, "spend": 0, "conversions": 0, "revenue": 0}
    mz = recompute_metrics(zero)
    assert mz == {}, f"all-zero row -> no metrics, got {mz}"
    # 빈/결측 행도 예외 없이 빈 dict
    assert recompute_metrics({}) == {}, "empty row"

    # --- recompute_metrics: 잘못된 보고값 탐지 (sample C_carousel: 보고 9.9% vs 실제 5%) ---
    carousel = {"impressions": 50000, "clicks": 2500, "spend": 1250000,
                "conversions": 100, "revenue": 3000000}
    mc = recompute_metrics(carousel)
    assert close(mc["ctr"], 0.05, metric="ctr"), f"carousel ctr {mc['ctr']}"
    assert close(mc["ctr"], 0.099, metric="ctr") is False, "reported 9.9% != recomputed 5%"

    # --- is_total_label: 합계행은 잡고, 실데이터는 절대 안 잡는다 ---
    for yes in ("TOTAL", "total", "Total:", "Grand Total", "Subtotal", "SUM",
                "합계", "총계", "소계", "총합", "총 합계", " totals "):
        assert is_total_label(yes), f"should be total: {yes!r}"
    for no in ("Summer_Sale", "Consumer", "Assumption", "sum_of_x", "A_video_15s",
               "총알색상", "", None, "Winter_Promo"):
        assert not is_total_label(no), f"should NOT be total: {no!r}"

    # --- map_headers / _pick: 대소문자·한글·확장 alias ---
    hm = map_headers(["Campaign", "Impressions", "클릭", "cost", "전환", "Sales"])
    assert hm == {"impressions": "Impressions", "clicks": "클릭", "spend": "cost",
                  "conversions": "전환", "revenue": "Sales"}, hm
    up = recompute_metrics({"Impressions": 1000, "Clicks": 30, "Spend": 15000})
    assert close(up["ctr"], 0.03, metric="ctr"), f"case-insensitive pick: {up}"

    return m, mc


if __name__ == "__main__":
    m, mc = _selftest()
    print("safemath self-test: ALL ASSERTIONS PASS")
    print(f"  safe_div(0,0)={safe_div(0,0)}  safe_div(5,0)={safe_div(5,0)}  "
          f"safe_div(5,0,None)={safe_div(5,0,default=None)}")
    print(f"  pct(36,1200)={pct(36,1200)}%  close(0.03,0.0303,'ctr')={close(0.03,0.0303,metric='ctr')}  "
          f"close(0.03,0.0303,'cpa')={close(0.03,0.0303,metric='cpa')}")
    print(f"  recompute A_video_15s -> ctr={m['ctr']:.4f} cpc={m['cpc']:.0f} "
          f"cpm={m['cpm']:.0f} cpa={m['cpa']:.0f} cvr={m['cvr']:.4f} roas={m['roas']:.2f}")
    print(f"  recompute C_carousel -> ctr={mc['ctr']:.4f} (reported 9.9% is WRONG, real 5.0%)")
