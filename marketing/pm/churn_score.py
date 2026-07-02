"""
이탈위험 스코어 — 최근성 대비 기대 구매주기로 위험 산출.
기대주기 = 관측기간/빈도. 위험비 = 최근성(미구매일)/기대주기. >1.5 경고. 계산 정확(해석가능).

입력 CSV: customer_id, date(YYYY-MM-DD), amount
Usage: python churn_score.py tx.csv [--asof 2026-01-31] [--threshold 1.5]
"""
import argparse, csv
from datetime import datetime
from pathlib import Path
from _pmutil import load_rows, expected_cycle  # 빈 데이터 우아한 처리 + freq=1 주기 폴백
from collections import defaultdict
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv")
    ap.add_argument("--asof",default=None); ap.add_argument("--threshold",type=float,default=1.5)
    ap.add_argument("--risk-cap",type=float,default=5.0,help="위험비 상한(1회구매 폴백 등 극단값 방지)")
    a=ap.parse_args()
    rows=load_rows(a.csv)
    h={c.lower():c for c in rows[0]}; cid=h.get("customer_id") or list(rows[0])[0]; dc=h.get("date")
    tx=defaultdict(list)
    for r in rows: tx[r[cid].strip()].append(datetime.strptime(r.get(dc).strip(),"%Y-%m-%d"))
    asof=datetime.strptime(a.asof,"%Y-%m-%d") if a.asof else max(d for v in tx.values() for d in v)
    # freq>=2 고객의 평균 구매간격 → freq=1 고객의 주기 폴백 근거
    repeat_cycles=[]
    for ds in tx.values():
        if len(ds)>1:
            ds2=sorted(ds); repeat_cycles.append(max((ds2[-1]-ds2[0]).days,1)/(len(ds2)-1))
    res=[]
    for c,ds in tx.items():
        ds=sorted(ds); first=ds[0]; last=ds[-1]; freq=len(ds)
        span=max((last-first).days,1)
        expected=expected_cycle(freq,span,repeat_cycles)  # freq=1은 재구매 중앙값 폴백(없으면 None)
        recency=(asof-last).days
        if expected is None:
            risk=0.0; note="(1회 구매 — 주기 추정 불가)"
        else:
            risk=min(recency/expected if expected else 0, a.risk_cap); note=""
        res.append((c,freq,recency,expected,risk,note))
    res.sort(key=lambda x:-x[4])
    atrisk=[r for r in res if r[4]>=a.threshold]
    print(f"\n=== CHURN RISK ({len(tx)} customers, asof {asof.date()}, thr {a.threshold}) ===")
    print("customer".ljust(10)+"freq".rjust(6)+"recency".rjust(9)+"기대주기".rjust(10)+"위험비".rjust(8))
    for c,f,rec,exp,risk,note in res:
        tag=" ⚠️" if risk>=a.threshold else ""
        exp_s=f"{exp:>10.0f}" if exp is not None else "N/A".rjust(10)
        print(f"{c.ljust(10)}{f:>6}{rec:>9}{exp_s}{risk:>8.2f}{tag}{note}")
    print(f"\n이탈위험 {len(atrisk)}명 (위험비≥{a.threshold}) → 윈백 캠페인 대상")
if __name__=="__main__": main()
