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

# 멀티통화 함정용 상수. 기존 spend/revenue 컬럼은 항상 KRW로 정규화되어 저장되고(=ground_truth
# 와 verify_bench가 검증하는 값), 추가 컬럼 spend_native/revenue_native 는 행의 native 통화 단위로
# 저장된다. 정답 경로는 currency/fx_rate 로 명시 환산 후 합산, 순진 오답은 ₩/$ 기호만 떼고 합산.
USD_KRW = 1350                       # USD→KRW 고정 환율(벤치 결정론용 상수)
CURRENCIES = {"KRW": 1, "USD": USD_KRW}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=100000)
    ap.add_argument("--days", type=int, default=90)
    a = ap.parse_args()
    random.seed(42)

    dates = [f"2026-{1 + d//30:02d}-{1 + d%30:02d}" for d in range(a.days)]
    # 멀티통화 컬럼은 additive: 기존 컬럼/분포를 바꾸지 않도록 헤더 끝에만 덧붙인다.
    headers = ["date"] + list(DIMS) + RAWM + ["currency", "fx_rate", "spend_native", "revenue_native"]
    rows = []
    # ground-truth accumulators
    gt_total = {m: 0 for m in RAWM}
    gt_dim = {dim: defaultdict(lambda: {m: 0 for m in RAWM}) for dim in DIMS}
    gt_dim["date"] = defaultdict(lambda: {m: 0 for m in RAWM})

    for _i in range(a.rows):
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
        # 멀티통화(additive): 통화는 행 인덱스로 결정론적 배정 → 기존 random 스트림·컬럼 불변(byte-identical).
        # spend/revenue 는 항상 KRW 정규화값 유지, native 는 통화 단위(USD면 환율로 나눈 값).
        cur = "USD" if _i % 4 == 0 else "KRW"          # 1/4은 USD로 기록
        rate = CURRENCIES[cur]
        rec["currency"] = cur
        rec["fx_rate"] = rate
        rec["spend_native"] = spend if cur == "KRW" else round(spend / rate)
        rec["revenue_native"] = revenue if cur == "KRW" else round(revenue / rate)
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
            # native 컬럼: USD 행은 $ 기호를 붙여 기록 → 순진 num()이 기호만 떼고 합산하면 통화 혼재로 오답.
            if r["currency"] == "USD":
                sp_native = f"${r['spend_native']:,}"
                rv_native = f"${r['revenue_native']:,}"
            else:
                sp_native = str(r["spend_native"])
                rv_native = str(r["revenue_native"])
            w.writerow([r["date"]] + [r[d] for d in DIMS] +
                       [f"{r['impressions']:,}", r["clicks"], spend, r["conversions"], revenue] +
                       [r["currency"], r["fx_rate"], sp_native, rv_native])

    # weighted derived metrics (the correct way)
    def derived(t):
        I, C, S, V, R = (t[m] for m in RAWM)
        return {
            "ctr": C / I if I else None, "cpc": S / C if C else None,
            "cpm": S / I * 1000 if I else None, "cpa": S / V if V else None,
            "cvr": V / C if C else None, "roas": R / S if S else None,
        }
    # 멀티통화 ground truth(additive, "by" 밖에 별도 키로 저장 → verify_bench 는 이 키를 안 봄).
    #   correct : native 를 통화별 환율로 KRW 환산 후 합산 → 정의상 정규화 spend/revenue 총합과 일치.
    #   naive   : ₩/$ 기호만 떼고 native 를 그대로 합산(통화 혼재) → 순진 오답(값이 다름).
    fx_correct = {"spend": 0, "revenue": 0}
    fx_naive = {"spend": 0, "revenue": 0}
    for r in rows:
        rate = CURRENCIES[r["currency"]]
        fx_correct["spend"] += r["spend_native"] * rate
        fx_correct["revenue"] += r["revenue_native"] * rate
        fx_naive["spend"] += r["spend_native"]
        fx_naive["revenue"] += r["revenue_native"]
    gt = {
        "rows": a.rows,
        "total": gt_total,
        "derived": derived(gt_total),
        "by": {dim: {k: dict(v) for k, v in gt_dim[dim].items()} for dim in gt_dim},
        "fx": {"rate": {c: CURRENCIES[c] for c in CURRENCIES},
               "correct": fx_correct, "naive": fx_naive},
    }
    (HERE / "ground_truth.json").write_text(json.dumps(gt, ensure_ascii=False), encoding="utf-8")
    print(f"wrote dataset.csv ({a.rows:,} rows, {len(headers)} fields) + ground_truth.json")
    print("grand totals:", {m: f"{gt_total[m]:,}" for m in RAWM})
    print("derived:", {k: (round(v, 6) if v else v) for k, v in gt["derived"].items()})

if __name__ == "__main__":
    main()
