"""
파레토(80/20) 분석 — 상위 몇 %의 항목이 가치의 80%를 차지하는지. 누적 기여 산출(정확).

입력 CSV: name(첫 열), value(revenue/spend/conversions 등)
Usage: python pareto.py data.csv --value revenue --threshold 0.8
"""
import argparse, csv, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv")
    ap.add_argument("--value",default=None); ap.add_argument("--threshold",type=float,default=0.8)
    a=ap.parse_args()
    rows=load_rows(a.csv)
    name=list(rows[0])[0]; vc=a.value or next((c for c in rows[0] if c.lower() in ("revenue","value","spend","conversions")),list(rows[0])[1])
    items=[((r.get(name) or "").strip(),num(r.get(vc))) for r in rows if not re.search(r"total|합계|총계",(r.get(name) or ""),re.I)]
    items.sort(key=lambda x:-x[1])
    raw_tot=sum(v for _,v in items); n=len(items)
    if raw_tot<=0:
        print(f"\n=== PARETO ({n} items, {vc}) ===")
        print(f"[안내] {vc} 합계가 0 — 파레토 분석 불가. 값 컬럼(--value) 또는 데이터 확인 필요.")
        return
    tot=raw_tot
    print(f"\n=== PARETO ({n} items, {vc}) ===")
    cum=0; hit=None
    print("rank  name".ljust(24)+"value".rjust(14)+"누적%".rjust(9))
    for i,(nm,v) in enumerate(items,1):
        cum+=v
        print(f"{i:>3}  {nm.ljust(16)}{v:>14,.0f}{cum/tot:>8.1%}")
        if hit is None and cum/tot>=a.threshold: hit=i
    print(f"\n→ 상위 {hit}개 ({hit/n:.0%}의 항목)가 가치의 {a.threshold:.0%}+ 차지")
    print(f"  · 집중 관리 대상. 롱테일은 효율/정리 검토.")
if __name__=="__main__": main()
