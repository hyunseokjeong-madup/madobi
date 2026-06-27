"""
매출 워터폴 — 두 기간 사이 총매출 변화를 채널별 기여로 분해(워터폴). 합=총변화(정확).
어느 채널이 증감을 주도했는지 순서대로 표시.

입력 CSV: channel, period_a, period_b (또는 prev/curr)
Usage: python revenue_waterfall.py rev.csv
"""
import argparse, csv, re
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    h={c.lower():c for c in rows[0]}
    ac=h.get("period_a") or h.get("prev") or h.get("a"); bc=h.get("period_b") or h.get("curr") or h.get("b")
    name=list(rows[0])[0]
    items=[]
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(name) or ""),re.I): continue
        items.append(((r.get(name) or "").strip(), num(r.get(ac)), num(r.get(bc))))
    ta=sum(x[1] for x in items); tb=sum(x[2] for x in items); change=tb-ta
    items.sort(key=lambda x:(x[2]-x[1]))  # 가장 감소한 것부터
    print(f"\n=== REVENUE WATERFALL ===")
    print(f"기준 총매출 {ta:,.0f} → 현재 {tb:,.0f}  (변화 {change:+,.0f}, {change/ta*100 if ta else 0:+.1f}%)")
    print("\n채널별 기여(증감순):")
    run=ta
    for nm,va,vb in sorted(items,key=lambda x:-(x[2]-x[1])):
        d=vb-va; run+=0
        arrow="▲" if d>0 else ("▼" if d<0 else "—")
        print(f"  {arrow} {nm.ljust(14)} {d:+,.0f}  ({d/change*100 if change else 0:+.0f}% of 변화)")
    chk=sum(vb-va for _,va,vb in items)
    print(f"\n분해 합 {chk:+,.0f} = 총변화 {change:+,.0f}  {'✅' if abs(chk-change)<1e-6 else '⚠️'}")
if __name__=="__main__": main()
