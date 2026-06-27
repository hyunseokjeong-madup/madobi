"""
전환 지연(conversion lag) 분포 — 클릭→전환 소요일 분포로 어트리뷰션 윈도우 적정성 진단.
중앙값/평균 지연, 1·3·7·14·30일 내 누적 전환 비중. 계산 정확.

입력 CSV: click_date, conv_date (YYYY-MM-DD; 전환 1건당 1행)
Usage: python conversion_lag.py conv.csv
"""
import argparse, csv
from datetime import datetime
from pathlib import Path
from statistics import median, mean
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    h={c.lower():c for c in rows[0]}
    clc=h.get("click_date") or h.get("click"); cvc=h.get("conv_date") or h.get("conversion_date")
    lags=[]
    for r in rows:
        try:
            cl=datetime.strptime(r.get(clc).strip(),"%Y-%m-%d"); cv=datetime.strptime(r.get(cvc).strip(),"%Y-%m-%d")
            lags.append((cv-cl).days)
        except: continue
    n=len(lags)
    if not n: print("데이터 없음"); return
    lags.sort()
    print(f"\n=== CONVERSION LAG ({n} conversions) ===")
    print(f"중앙값 {median(lags):.0f}일 · 평균 {mean(lags):.1f}일 · 최대 {max(lags)}일")
    print("누적 전환 비중:")
    for w in [1,3,7,14,30]:
        c=sum(1 for l in lags if l<=w); print(f"  ≤{w:>2}일: {c/n:>5.1%}")
    rec=next((w for w in [1,3,7,14,30] if sum(1 for l in lags if l<=w)/n>=0.9),30)
    print(f"→ 전환의 90% 포착 윈도우 ≈ {rec}일. 더 짧은 윈도우는 전환 과소집계.")
if __name__=="__main__": main()
