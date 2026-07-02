"""
Deterministic aggregation/summarization engine — the "무조건 맞추는" aggregator.
Robust to formatted cells (commas, ₩/$ , %, blanks). Group-by any field; weighted derived metrics.

Usage:
  python summarize.py dataset.csv --by channel
  python summarize.py dataset.csv --by overall --md out.md
"""
import json, argparse, sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # marketing/
import safemath

RAWM = ["impressions", "clicks", "spend", "conversions", "revenue"]

def num(s):
    if s is None: return 0
    s = str(s).strip().replace(",", "").replace("₩", "").replace("$", "").replace("%", "")
    if s in ("", "-", "—", "N/A", "na", "NaN"): return 0
    try:
        f = float(s)
        return int(f) if f.is_integer() else f
    except ValueError:
        return 0

def derived(t):
    I, C, S, V, R = (t[m] for m in RAWM)
    return {
        "ctr": C / I if I else None, "cpc": S / C if C else None,
        "cpm": S / I * 1000 if I else None, "cpa": S / V if V else None,
        "cvr": V / C if C else None, "roas": R / S if S else None,
    }

def aggregate(csvpath, by):
    """CSV → {그룹: raw 합계}. 헤더는 alias(한글/대소문자/cost 등) 매핑, 합계행은 라벨 컬럼만 판정.

    반환에 "_unmapped" 키를 넣지 않는다(verify_bench 호환) — 미매핑 경고는 aggregate_info() 로."""
    groups, _ = aggregate_info(csvpath, by)
    return groups

def aggregate_info(csvpath, by):
    """aggregate + 헤더 매핑 정보. 인식 컬럼 0개면 조용한 0 리포트 대신 명시적 종료."""
    rows = safemath.load_rows(csvpath)   # 파일 없음/빈 데이터/cp949 를 한 줄 안내로 처리
    headers = list(rows[0].keys())
    colmap = safemath.map_headers(headers)   # canonical → 원본 헤더
    if not colmap:
        raise SystemExit(f"[오류] 인식 가능한 지표 컬럼이 없습니다 — 헤더: {headers} "
                         f"(인식 alias 예: impressions/노출, clicks/클릭, spend/비용/cost, ...)")
    label_col = headers[0]
    groups = defaultdict(lambda: {m: 0 for m in RAWM})
    for r in rows:
        # TOTAL/소계 행 제외(이중계산 방지). 판정은 safemath.is_total_label 공용 기준 —
        # 과거 '모든 셀 join + 부분매칭'은 'Summer_Sale' 행까지 조용히 폐기했다.
        if safemath.is_total_label(r.get(label_col)):
            continue
        key = "ALL" if by in (None, "overall") else (r.get(by) or "").strip()
        g = groups[key]
        for m in RAWM:
            g[m] += num(r.get(colmap.get(m, m)))
    unmapped = [m for m in RAWM if m not in colmap]
    return groups, unmapped

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--by", default="overall")
    ap.add_argument("--md", default=None)
    ap.add_argument("--json", default=None)
    ap.add_argument("--kpi", default="roas")
    a = ap.parse_args()
    groups, unmapped = aggregate_info(a.csv, a.by)

    out = {}
    for k, t in groups.items():
        out[k] = {**t, **derived(t)}

    # ranked print
    order = sorted(out.items(), key=lambda kv: (kv[1].get(a.kpi) or -1), reverse=True)
    print(f"\n=== SUMMARY by {a.by}  ({len(out)} groups) ===")
    if unmapped:
        # 조용한 0 은 '보증된 숫자'처럼 읽힌다 — 미인식 컬럼은 반드시 표면화.
        print(f"⚠ 미인식 지표 컬럼: {', '.join(unmapped)} (아래 표에서 0으로 표시 — 헤더 확인)")
    print("group".ljust(14) + "impr".rjust(14) + "clicks".rjust(11) + "spend".rjust(15) +
          "conv".rjust(9) + "revenue".rjust(15) + "  CTR    ROAS")
    for k, m in order:
        print(k.ljust(14) + f"{m['impressions']:>14,}" + f"{m['clicks']:>11,}" +
              f"{m['spend']:>15,}" + f"{m['conversions']:>9,}" + f"{m['revenue']:>15,}" +
              f"  {(m['ctr'] or 0):.2%}  {(m['roas'] or 0):.2f}x")

    if a.json:
        Path(a.json).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    if a.md:
        L = [f"# Summary by `{a.by}` ({len(out)} groups)", "",
             "| group | impressions | clicks | spend | conv | revenue | CTR | CPA | ROAS |",
             "|---|---|---|---|---|---|---|---|---|"]
        for k, m in order:
            cpa = f"{m['cpa']:,.0f}" if m.get("cpa") else "-"
            L.append(f"| {k} | {m['impressions']:,} | {m['clicks']:,} | {m['spend']:,} | "
                     f"{m['conversions']:,} | {m['revenue']:,} | {(m['ctr'] or 0):.2%} | {cpa} | {(m['roas'] or 0):.2f}x |")
        Path(a.md).write_text("\n".join(L) + "\n", encoding="utf-8")
    return out

if __name__ == "__main__":
    main()
