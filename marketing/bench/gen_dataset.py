"""
Generate a LARGE, many-field synthetic marketing dataset with CODE-COMPUTED ground truth.
Proves that aggregation/summarization is exactly correct at scale.

Outputs (in this dir):
  dataset.csv         ~N rows, many dimensions + raw metrics (some cells comma/%/currency formatted)
  ground_truth.json   grand totals, per-dimension breakdown sums, weighted derived metrics

Deterministic (seeded). Pure stdlib.
"""
import csv, json, random, argparse
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

DIMS = {
    "channel": ["meta", "google", "tiktok", "youtube", "naver"],
    "device": ["mobile", "desktop", "tablet"],
    "region": ["seoul", "gyeonggi", "busan", "daegu", "gwangju"],
    "age": ["13-17", "18-24", "25-34", "35-44", "45+"],
    "gender": ["m", "f", "u"],
    "campaign": [f"C{i:02d}" for i in range(1, 11)],
    "creative": [f"CR{i:03d}" for i in range(1, 51)],
}
RAWM = ["impressions", "clicks", "spend", "conversions", "revenue"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=100000)
    ap.add_argument("--days", type=int, default=90)
    a = ap.parse_args()
    random.seed(42)

    dates = [f"2026-{1 + d//30:02d}-{1 + d%30:02d}" for d in range(a.days)]
    headers = ["date"] + list(DIMS) + RAWM
    rows = []
    # ground-truth accumulators
    gt_total = {m: 0 for m in RAWM}
    gt_dim = {dim: defaultdict(lambda: {m: 0 for m in RAWM}) for dim in DIMS}
    gt_dim["date"] = defaultdict(lambda: {m: 0 for m in RAWM})

    for _ in range(a.rows):
        rec = {"date": random.choice(dates)}
        for dim, vals in DIMS.items():
            rec[dim] = random.choice(vals)
        impr = random.randint(100, 20000)
        ctr = random.uniform(0.003, 0.08)
        clicks = min(impr, int(impr * ctr))
        cpc = random.uniform(150, 1200)          # KRW
        spend = int(clicks * cpc)
        cvr = random.uniform(0.01, 0.15)
        conv = int(clicks * cvr)
        aov = random.uniform(8000, 60000)
        revenue = int(conv * aov)
        rec.update(impressions=impr, clicks=clicks, spend=spend, conversions=conv, revenue=revenue)
        rows.append(rec)
        for m in RAWM:
            gt_total[m] += rec[m]
        for dim in list(DIMS) + ["date"]:
            for m in RAWM:
                gt_dim[dim][rec[dim]][m] += rec[m]

    # write CSV with MIXED formatting to test robust parsing (다양한 필드/포맷)
    with open(HERE / "dataset.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for i, r in enumerate(rows):
            spend = f"{r['spend']:,}" if i % 2 == 0 else str(r["spend"])      # half comma-formatted
            revenue = f"₩{r['revenue']:,}" if i % 3 == 0 else str(r["revenue"])  # third currency-prefixed
            w.writerow([r["date"]] + [r[d] for d in DIMS] +
                       [f"{r['impressions']:,}", r["clicks"], spend, r["conversions"], revenue])

    # weighted derived metrics (the correct way)
    def derived(t):
        I, C, S, V, R = (t[m] for m in RAWM)
        return {
            "ctr": C / I if I else None, "cpc": S / C if C else None,
            "cpm": S / I * 1000 if I else None, "cpa": S / V if V else None,
            "cvr": V / C if C else None, "roas": R / S if S else None,
        }
    gt = {
        "rows": a.rows,
        "total": gt_total,
        "derived": derived(gt_total),
        "by": {dim: {k: dict(v) for k, v in gt_dim[dim].items()} for dim in gt_dim},
    }
    (HERE / "ground_truth.json").write_text(json.dumps(gt, ensure_ascii=False), encoding="utf-8")
    print(f"wrote dataset.csv ({a.rows:,} rows, {len(headers)} fields) + ground_truth.json")
    print("grand totals:", {m: f"{gt_total[m]:,}" for m in RAWM})
    print("derived:", {k: (round(v, 6) if v else v) for k, v in gt["derived"].items()})

if __name__ == "__main__":
    main()
