"""
Deterministic aggregation/summarization engine — the "무조건 맞추는" aggregator.
Robust to formatted cells (commas, ₩/$ , %, blanks). Group-by any field; weighted derived metrics.

Usage:
  python summarize.py dataset.csv --by channel
  python summarize.py dataset.csv --by overall --md out.md
"""
import csv, json, argparse, re
from pathlib import Path
from collections import defaultdict

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
    groups = defaultdict(lambda: {m: 0 for m in RAWM})
    with open(csvpath, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key = "ALL" if by in (None, "overall") else (r.get(by) or "").strip()
            g = groups[key]
            for m in RAWM:
                g[m] += num(r.get(m))
    return groups

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--by", default="overall")
    ap.add_argument("--md", default=None)
    ap.add_argument("--json", default=None)
    ap.add_argument("--kpi", default="roas")
    a = ap.parse_args()
    groups = aggregate(a.csv, a.by)

    out = {}
    for k, t in groups.items():
        out[k] = {**t, **derived(t)}

    # ranked print
    order = sorted(out.items(), key=lambda kv: (kv[1].get(a.kpi) or -1), reverse=True)
    print(f"\n=== SUMMARY by {a.by}  ({len(out)} groups) ===")
    print("group".ljust(14) + "impr".rjust(14) + "clicks".rjust(11) + "spend".rjust(15) +
          "conv".rjust(9) + "revenue".rjust(15) + "  CTR    ROAS")
    for k, m in order:
        print(k.ljust(14) + f"{m['impressions']:>14,}" + f"{m['clicks']:>11,}" +
              f"{m['spend']:>15,}" + f"{m['conversions']:>9,}" + f"{m['revenue']:>15,}" +
              f"  {(m['ctr'] or 0):.2%}  {(m['roas'] or 0):.2f}x")

    if a.json:
        Path(a.json).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8", newline="\n")
    if a.md:
        L = [f"# Summary by `{a.by}` ({len(out)} groups)", "",
             "| group | impressions | clicks | spend | conv | revenue | CTR | CPA | ROAS |",
             "|---|---|---|---|---|---|---|---|---|"]
        for k, m in order:
            cpa = f"{m['cpa']:,.0f}" if m.get("cpa") else "-"
            L.append(f"| {k} | {m['impressions']:,} | {m['clicks']:,} | {m['spend']:,} | "
                     f"{m['conversions']:,} | {m['revenue']:,} | {(m['ctr'] or 0):.2%} | {cpa} | {(m['roas'] or 0):.2f}x |")
        Path(a.md).write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    return out

if __name__ == "__main__":
    main()
