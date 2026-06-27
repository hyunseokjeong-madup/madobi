"""
AGGREGATION BENCHMARK: prove summarize.py reproduces the code-computed ground truth EXACTLY,
on a large many-field dataset with messy formatting.

Checks:
  - grand totals (impr/clicks/spend/conv/revenue) match exactly (integers)
  - every dimension's per-group breakdown sums match exactly
  - weighted derived metrics (CTR/CPC/CPM/CPA/CVR/ROAS) match within 1e-9
Exit 0 = all pass.
"""
import json, sys
from pathlib import Path
from summarize import aggregate, derived, RAWM

HERE = Path(__file__).parent

def main():
    gt = json.loads((HERE / "ground_truth.json").read_text(encoding="utf-8"))
    csvp = HERE / "dataset.csv"
    fails = []
    checks = 0

    # 1) overall totals
    overall = aggregate(csvp, "overall")["ALL"]
    for m in RAWM:
        checks += 1
        if overall[m] != gt["total"][m]:
            fails.append(f"TOTAL {m}: got {overall[m]:,} != gt {gt['total'][m]:,}")
    # derived overall
    d = derived(overall)
    for k, v in gt["derived"].items():
        checks += 1
        if v is None: continue
        if abs((d[k] or 0) - v) > 1e-9 * max(1, abs(v)):
            fails.append(f"DERIVED {k}: got {d[k]} != gt {v}")

    # 2) every dimension breakdown
    for dim, groups in gt["by"].items():
        agg = aggregate(csvp, dim)
        for gname, gt_vals in groups.items():
            for m in RAWM:
                checks += 1
                got = agg.get(gname, {}).get(m, 0)
                if got != gt_vals[m]:
                    fails.append(f"[{dim}={gname}] {m}: got {got:,} != gt {gt_vals[m]:,}")
        # breakdown must also re-sum to grand total
        for m in RAWM:
            checks += 1
            s = sum(agg[g][m] for g in agg)
            if s != gt["total"][m]:
                fails.append(f"[{dim}] sum {m} {s:,} != grand total {gt['total'][m]:,}")

    print(f"\n=== AGGREGATION BENCHMARK ===")
    print(f"dataset: {gt['rows']:,} rows · dimensions: {len(gt['by'])} · checks run: {checks:,}")
    if fails:
        print(f"\nFAIL: {len(fails)} mismatch(es):")
        for f in fails[:30]:
            print("  ! " + f)
        sys.exit(1)
    print(f"\nRESULT: ✅ ALL {checks:,} CHECKS PASS — aggregation is EXACT at scale (큰 데이터·다양한 필드·무실점).")

if __name__ == "__main__":
    main()
