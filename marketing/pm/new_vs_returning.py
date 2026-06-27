"""
신규 vs 재구매 분해 — 거래 데이터에서 각 거래를 첫구매(신규)/재구매로 판정해 매출·주문 분해.
첫구매 = 해당 고객의 최초 거래일. 계산 정확. 재구매율·재구매 매출비중 산출.

입력 CSV: customer_id, date, amount
Usage: python new_vs_returning.py tx.csv
"""
import argparse, csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    h={c.lower():c for c in rows[0]}; cid=h.get("customer_id") or list(rows[0])[0]; dc=h.get("date"); ac=h.get("amount") or h.get("revenue")
    tx=defaultdict(list)
    for r in rows: tx[r[cid].strip()].append((datetime.strptime(r.get(dc).strip(),"%Y-%m-%d"), num(r.get(ac))))
    new_rev=new_ord=ret_rev=ret_ord=0; repeaters=0
    for c,items in tx.items():
        items=sorted(items)
        first_day=items[0][0]
        if len(items)>1: repeaters+=1
        for d,amt in items:
            if d==first_day and (d,amt)==items[0]:
                new_rev+=amt; new_ord+=1
            else:
                ret_rev+=amt; ret_ord+=1
    cust=len(tx); tot_rev=new_rev+ret_rev
    print(f"\n=== NEW vs RETURNING ({cust} customers) ===")
    print(f"신규(첫구매): 주문 {new_ord} · 매출 {new_rev:,.0f} ({new_rev/max(tot_rev,1):.1%})")
    print(f"재구매:       주문 {ret_ord} · 매출 {ret_rev:,.0f} ({ret_rev/max(tot_rev,1):.1%})")
    print(f"재구매율(2회+ 고객/전체) = {repeaters/cust:.1%}")
    print("  · 재구매 매출비중↑ = 충성 기반 견고. 신규 의존도 모니터.")
if __name__=="__main__": main()
