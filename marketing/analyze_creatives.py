"""
Creative performance analyzer (광고 소재 분석).
Ranks creatives into winners / losers by a chosen KPI, with a minimum-impression
threshold (small-sample guard), recomputes all metrics from raw (정합성), and—if a
date column is present—flags creative fatigue (CTR decline over time).

Usage:
  python analyze_creatives.py data.csv [--kpi roas|cpa|ctr|cvr] [--min-impr 1000] [--md out.md]

Reuses metric/parse logic from reconcile.py (same directory).
"""
import sys, argparse, re
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent))
from reconcile import num, find_col, ALIASES, RAW, derive
import safemath

HIGHER_BETTER = {"roas", "ctr", "cvr", "revenue", "conversions"}  # else lower-better (cpa, cpc, cpm)

def load(csvpath):
    rows = safemath.load_rows(csvpath)   # 파일 없음/빈 데이터/cp949 를 한 줄 안내로 처리
    headers = list(rows[0].keys())
    colmap = {k: find_col(headers, k) for k in ALIASES}
    date_col = next((h for h in headers if re.search(r"date|날짜|일자|day", h, re.I)), None)
    label_col = headers[0]
    recs = []
    for r in rows:
        # 합계행 제외는 safemath.is_total_label 공용 기준 —
        # 부분매칭('sum')이 'Summer_Sale' 승자를 폐기하고 반대 추천을 내던 사고 방지.
        if safemath.is_total_label(r.get(label_col)):
            continue
        rec = {k: (num(r.get(colmap[k])) if colmap[k] else None) for k in ALIASES}
        rec["_label"] = (r.get(label_col) or "").strip()
        rec["_date"] = (r.get(date_col) or "").strip() if date_col else None
        recs.append(rec)
    return recs, (date_col is not None)

def aggregate(recs):
    """Aggregate raw metrics per creative label (sum), then derive metrics from the sums."""
    agg = defaultdict(lambda: {k: 0.0 for k in RAW})
    for r in recs:
        for k in RAW:
            if r.get(k) is not None: agg[r["_label"]][k] += r[k]
    out = {}
    for label, raw in agg.items():
        d = derive(raw)
        out[label] = {**raw, **d}
    return out

def fatigue(recs):
    """If dated: per creative, compare CTR of first half vs second half of its dates."""
    byc = defaultdict(list)
    for r in recs:
        if r["_date"]:
            byc[r["_label"]].append(r)
    flags = {}
    for label, rs in byc.items():
        rs = sorted(rs, key=lambda x: x["_date"])
        if len(rs) < 4: continue
        mid = len(rs) // 2
        def ctr(part):
            imp = sum(x["impressions"] or 0 for x in part)
            clk = sum(x["clicks"] or 0 for x in part)
            return (clk / imp) if imp else None
        a, b = ctr(rs[:mid]), ctr(rs[mid:])
        if a and b and b < a * 0.8:  # >20% CTR drop in 2nd half
            flags[label] = (a, b, (b - a) / a)
    return flags

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--kpi", default="roas", choices=["roas", "cpa", "ctr", "cvr", "cpc", "cpm"])
    ap.add_argument("--min-impr", type=float, default=1000)
    ap.add_argument("--md", default=None)
    a = ap.parse_args()

    recs, dated = load(a.csv)
    agg = aggregate(recs)
    kpi = a.kpi
    higher = kpi in HIGHER_BETTER

    qualified = {l: m for l, m in agg.items() if (m.get("impressions") or 0) >= a.min_impr and kpi in m}
    skipped = [l for l in agg if l not in qualified]
    ranked = sorted(qualified.items(), key=lambda kv: kv[1][kpi], reverse=higher)
    fat = fatigue(recs) if dated else {}

    def fmt(m):
        def g(k, p=""):
            v = m.get(k)
            return f"{v:{p}}" if v is not None else "-"
        return (f"impr={g('impressions',',.0f')} ctr={ (m['ctr'] if 'ctr' in m else 0):.2%} "
                f"cpc={g('cpc',',.0f')} cpa={g('cpa',',.0f')} roas={ (m['roas'] if 'roas' in m else 0):.2f}x")

    print(f"\n=== CREATIVE ANALYSIS: {a.csv}  (KPI={kpi}, {'higher' if higher else 'lower'} better, min_impr={a.min_impr:,.0f}) ===")
    print(f"qualified={len(qualified)}  skipped(low-sample)={len(skipped)}  dated={dated}")
    print(f"\n-- ranked by {kpi} --")
    for i, (label, m) in enumerate(ranked, 1):
        tag = "WINNER" if (i <= max(1, len(ranked)//3) ) else ("LOSER" if i > len(ranked) - max(1, len(ranked)//3) else "")
        fa = "  [FATIGUE]" if label in fat else ""
        print(f"{i:>2} {label:<28} {kpi}={m[kpi]:.3g}  | {fmt(m)} {tag}{fa}")
    if skipped:
        print(f"\n  ! low-sample (skipped, impr < {a.min_impr:,.0f}): {', '.join(skipped)}")
    if fat:
        print(f"\n-- fatigue (CTR dropped >20% over time) --")
        for l, (x, y, d) in fat.items():
            print(f"  {l}: CTR {x:.2%} -> {y:.2%} ({d:+.0%})")

    # recommendations
    print(f"\n-- recommendations --")
    if ranked:
        print(f"  • scale: {ranked[0][0]} (best {kpi}={ranked[0][1][kpi]:.3g})")
        print(f"  • cut/refresh: {ranked[-1][0]} (worst {kpi}={ranked[-1][1][kpi]:.3g})")
    for l in fat: print(f"  • refresh creative (fatigue): {l}")
    if skipped: print(f"  • gather more data before judging: {', '.join(skipped)}")

    if a.md:
        L = [f"# Creative Analysis — `{Path(a.csv).name}`", "",
             f"KPI: **{kpi}** ({'higher' if higher else 'lower'} better) · min impressions: {a.min_impr:,.0f}", "",
             "| # | creative | " + kpi + " | impr | CTR | CPA | ROAS | tag |",
             "|---|---|---|---|---|---|---|---|"]
        for i, (label, m) in enumerate(ranked, 1):
            tag = "🏆" if i <= max(1, len(ranked)//3) else ("🛑" if i > len(ranked)-max(1, len(ranked)//3) else "")
            if label in fat: tag += "😴"
            cpa_s = f"{m['cpa']:,.0f}" if m.get("cpa") is not None else "-"
            L.append(f"| {i} | {label} | {m[kpi]:.3g} | {m.get('impressions',0):,.0f} | "
                     f"{m.get('ctr',0):.2%} | {cpa_s} | {m.get('roas',0):.2f}x | {tag} |")
        Path(a.md).write_text("\n".join(L) + "\n", encoding="utf-8")
        print(f"\n[md] -> {a.md}")

if __name__ == "__main__":
    main()
