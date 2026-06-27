"""
CTR 벤치마크 — 각 항목 CTR을 포트폴리오 가중 CTR(ΣClk/ΣImpr) 대비 비교해 과/저성과 표시.
ratio = CTR/벤치마크. <0.7 저조, >1.3 우수. 계산 정확.

입력 CSV: name + impressions, clicks
Usage: python ctr_benchmark.py data.csv
"""
import argparse, csv, re
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    name=list(rows[0])[0]; h={c.lower():c for c in rows[0]}
    ic=h.get("impressions") or h.get("impr"); cc=h.get("clicks")
    ents=[]; ti=tc=0
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(name) or ""),re.I): continue
        I=num(r.get(ic)); C=num(r.get(cc))
        if I>0: ents.append(((r.get(name) or "").strip(),I,C,C/I)); ti+=I; tc+=C
    bench=tc/ti if ti else 0
    print(f"\n=== CTR BENCHMARK (포트폴리오 CTR {bench:.2%}) ===")
    for nm,I,C,ctr in sorted(ents,key=lambda x:-x[3]):
        ratio=ctr/bench if bench else 0
        tag="🟢 우수" if ratio>1.3 else ("🔴 저조" if ratio<0.7 else "—")
        print(f"  {nm.ljust(16)} CTR {ctr:>6.2%} (벤치 {ratio:.2f}x) {tag}")
    print("  · 가중 벤치마크 대비. 저조 항목 후크/타깃/소재 개선.")
if __name__=="__main__": main()
