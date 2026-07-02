"""
윈백 우선순위 — 과거가치(monetary) × 이탈위험(recency/기대주기)으로 재유치 대상 순위화.
priority = monetary × min(risk, cap). 고가치·고위험 고객을 먼저. 계산 정확.

입력 CSV: customer_id, date, amount
Usage: python winback_priority.py tx.csv [--asof 2026-02-15] [--top 10]
"""
import argparse, csv
from datetime import datetime
from pathlib import Path
from _pmutil import load_rows, expected_cycle  # 빈 데이터 우아한 처리 + freq=1 주기 폴백
from collections import defaultdict
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv")
    ap.add_argument("--asof",default=None); ap.add_argument("--top",type=int,default=10); ap.add_argument("--risk-cap",type=float,default=5.0)
    a=ap.parse_args()
    rows=load_rows(a.csv)
    h={c.lower():c for c in rows[0]}; cid=h.get("customer_id") or list(rows[0])[0]; dc=h.get("date"); ac=h.get("amount") or h.get("revenue")
    tx=defaultdict(list)
    for r in rows: tx[r[cid].strip()].append((datetime.strptime(r.get(dc).strip(),"%Y-%m-%d"),num(r.get(ac))))
    asof=datetime.strptime(a.asof,"%Y-%m-%d") if a.asof else max(d for v in tx.values() for d,_ in v)
    # freq>=2 고객의 평균 구매간격 → freq=1 고객의 주기 폴백 근거
    repeat_cycles=[]
    for items in tx.values():
        if len(items)>1:
            it=sorted(items); repeat_cycles.append(max((it[-1][0]-it[0][0]).days,1)/(len(it)-1))
    res=[]
    for c,items in tx.items():
        items=sorted(items); freq=len(items); monetary=sum(x for _,x in items)
        span=max((items[-1][0]-items[0][0]).days,1)
        expected=expected_cycle(freq,span,repeat_cycles)  # freq=1은 재구매 중앙값 폴백(없으면 None)
        recency=(asof-items[-1][0]).days
        if expected is None:
            risk=0.0  # 1회 구매 — 주기 추정 불가 → 위험 0
        else:
            risk=min(recency/expected if expected else 0, a.risk_cap)
        res.append((c,monetary,recency,risk,monetary*risk))
    res.sort(key=lambda x:-x[4])
    print(f"\n=== WINBACK PRIORITY (asof {asof.date()}) ===")
    print("customer".ljust(10)+"가치".rjust(12)+"recency".rjust(9)+"위험".rjust(7)+"우선점수".rjust(14))
    for c,m,rec,risk,pri in res[:a.top]:
        print(f"{c.ljust(10)}{m:>12,.0f}{rec:>9}{risk:>7.2f}{pri:>14,.0f}")
    print("  · 고가치×고위험 우선 윈백(쿠폰/리마인드). 단순 신규획득보다 ROI 우수한 경우 多.")
if __name__=="__main__": main()
