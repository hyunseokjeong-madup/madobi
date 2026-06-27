"""
Marketing number RECONCILIATION engine (정합성 검산).
Reads a CSV of marketing breakdown data and checks consistency:
  - derived metrics (CTR/CPC/CPM/CPA/ROAS) recomputed from raw vs reported
  - breakdown rows sum to the TOTAL row (or computed total)
  - ratio metrics use weighted (not simple) averaging  [Simpson trap]
  - unit/format cleaning (commas, %, currency)
Outputs a report with PASS (v) / WARN (!). Pure stdlib; no pandas needed.

Usage: python reconcile.py data.csv [--tol 0.01]
"""
import csv, sys, re, argparse
from pathlib import Path

RAW = ["impressions", "clicks", "spend", "conversions", "revenue"]
ALIASES = {
    "impressions": ["impressions", "impr", "imp", "노출", "노출수"],
    "clicks": ["clicks", "click", "클릭", "클릭수"],
    "spend": ["spend", "cost", "비용", "광고비", "spend(krw)", "cost(krw)"],
    "conversions": ["conversions", "conv", "conversion", "전환", "전환수", "installs", "purchases"],
    "revenue": ["revenue", "rev", "매출", "수익", "sales"],
    "ctr": ["ctr"], "cpc": ["cpc"], "cpm": ["cpm"], "cpa": ["cpa", "cpi"], "roas": ["roas"],
}

def num(s):
    if s is None: return None
    s = str(s).strip().replace(",", "").replace("₩", "").replace("$", "").replace("%", "")
    if s in ("", "-", "—", "N/A", "na", "NaN"): return None
    try: return float(s)
    except ValueError: return None

def find_col(headers, key):
    low = {h.lower().strip(): h for h in headers}
    for a in ALIASES[key]:
        if a in low: return low[a]
    return None

def derive(r):
    out = {}
    imp, clk, sp, cv, rv = (r.get(k) for k in RAW)
    if imp and clk is not None: out["ctr"] = clk / imp
    if clk and sp is not None: out["cpc"] = sp / clk
    if imp and sp is not None: out["cpm"] = sp / imp * 1000
    if cv and sp is not None: out["cpa"] = sp / cv
    if sp and rv is not None: out["roas"] = rv / sp
    if clk and cv is not None: out["cvr"] = cv / clk          # 전환율
    if imp and rv is not None: out["ecpm"] = rv / imp * 1000  # 퍼블리셔 eCPM
    return out

def close(a, b, tol):
    if a is None or b is None: return None
    denom = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / denom <= tol

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--tol", type=float, default=0.01)
    ap.add_argument("--md", default=None, help="write a markdown report to this path")
    a = ap.parse_args()
    rows = list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    if not rows:
        print("empty csv"); return
    headers = list(rows[0].keys())
    colmap = {k: find_col(headers, k) for k in ALIASES}
    label_col = headers[0]

    parsed, total_row = [], None
    for r in rows:
        rec = {k: num(r.get(colmap[k])) if colmap[k] else None for k in ALIASES}
        rec["_label"] = (r.get(label_col) or "").strip()
        if re.search(r"total|합계|sum|총계|소계", rec["_label"], re.I):
            total_row = rec
        else:
            parsed.append(rec)

    warns, passes = [], []

    # 1) per-row derived metric reconciliation
    for rec in parsed:
        d = derive(rec)
        for m in ["ctr", "cpc", "cpm", "cpa", "roas"]:
            rep = rec.get(m)
            if rep is not None and m in d:
                # ratios (ctr) may be reported as fraction OR percent -> accept either scale
                if m == "ctr":
                    ok = bool(close(rep, d[m], a.tol) or close(rep, d[m] * 100, a.tol))
                    shown = f"reported={rep:g}% recomputed={d[m]:.4%}"
                else:
                    ok = bool(close(rep, d[m], a.tol))
                    shown = f"reported={rep:g} recomputed={d[m]:.4g}"
                msg = f"[{rec['_label']}] {m}: {shown}"
                (passes if ok else warns).append(("v " if ok else "! ") + msg)

    # 2) breakdown sum == total row
    sums = {k: sum(r[k] for r in parsed if r.get(k) is not None) for k in RAW}
    if total_row:
        for k in RAW:
            if total_row.get(k) is not None:
                ok = close(sums[k], total_row[k], a.tol)
                msg = f"[SUM] {k}: rows_sum={sums[k]:,.4g} vs total_row={total_row[k]:,.4g}"
                (passes if ok else warns).append(("v " if ok else "! ") + msg)

    # 3) Simpson / weighted-vs-simple ratio trap
    ctrs = [derive(r).get("ctr") for r in parsed if derive(r).get("ctr") is not None]
    if ctrs and sums["impressions"]:
        weighted = sums["clicks"] / sums["impressions"]
        simple = sum(ctrs) / len(ctrs)
        if close(weighted, simple, 0.05) is False:
            warns.append(f"! [RATIO] CTR simple-avg={simple:.4%} != weighted={weighted:.4%} "
                         f"(use weighted Sigma-clicks/Sigma-impr)")
        else:
            passes.append(f"v [RATIO] CTR weighted={weighted:.4%} (simple avg close)")

    # report
    print(f"\n=== RECONCILIATION: {a.csv}  (tol={a.tol:.0%}) ===")
    print(f"rows={len(parsed)}  total_row={'yes' if total_row else 'no'}")
    print(f"\n-- weighted totals --")
    print(f"  impressions={sums['impressions']:,.0f}  clicks={sums['clicks']:,.0f}  "
          f"spend={sums['spend']:,.0f}  conversions={sums['conversions']:,.0f}  revenue={sums['revenue']:,.0f}")
    if sums["impressions"]:
        print(f"  CTR={sums['clicks']/sums['impressions']:.4%}  "
              f"CPC={sums['spend']/max(sums['clicks'],1e-9):,.2f}  "
              f"CPM={sums['spend']/sums['impressions']*1000:,.2f}  "
              f"ROAS={sums['revenue']/max(sums['spend'],1e-9):.2f}x")
    print(f"\n-- checks: {len(passes)} PASS, {len(warns)} WARN --")
    for w in warns: print("  " + w)
    if not warns: print("  (all consistency checks passed)")
    verdict = "CONSISTENT" if not warns else f"{len(warns)} INCONSISTENCY(IES) - investigate raw data"
    print(f"\nVERDICT: {verdict}{' v' if not warns else ' !'}")

    if a.md:
        I, C, S = sums["impressions"], sums["clicks"], sums["spend"]
        lines = [f"# Reconciliation Report — `{Path(a.csv).name}`", "",
                 f"- rows: **{len(parsed)}**  ·  total row: **{'yes' if total_row else 'no'}**  ·  tol: {a.tol:.0%}",
                 f"- verdict: **{'✅ ' + verdict if not warns else '⚠️ ' + verdict}**", "",
                 "## Totals (weighted)", "",
                 "| metric | value |", "|---|---|",
                 f"| impressions | {I:,.0f} |", f"| clicks | {C:,.0f} |",
                 f"| spend | {S:,.0f} |", f"| conversions | {sums['conversions']:,.0f} |",
                 f"| revenue | {sums['revenue']:,.0f} |"]
        if I:
            lines += [f"| CTR | {C/I:.4%} |", f"| CPC | {S/max(C,1e-9):,.2f} |",
                      f"| CPM | {S/I*1000:,.2f} |", f"| ROAS | {sums['revenue']/max(S,1e-9):.2f}x |"]
        lines += ["", "## Consistency checks", ""]
        if warns:
            lines += [f"- ⚠️ {w[2:]}" for w in warns]
        else:
            lines += ["- ✅ all consistency checks passed"]
        Path(a.md).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"\n[md] report written -> {a.md}")

if __name__ == "__main__":
    main()
