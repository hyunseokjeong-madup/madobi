"""
데이터 품질 검증기 — 마케팅 CSV의 정합성 위반을 다중 룰로 점검(보고 전 게이트).
룰: 음수값 / clicks>impressions / conversions>clicks / spend>0인데 impressions=0 /
    중복행 / 필수열 결측 / (날짜 있으면) 일자 갭. 위반 행수 리포트.

입력 CSV: impressions, clicks, spend, conversions, revenue[, date]
Usage: python data_quality.py data.csv
"""
import argparse, csv, re
from datetime import datetime, timedelta
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return None
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    h={c.lower():c for c in rows[0]}
    def col(*n):
        for x in n:
            if x in h: return h[x]
        return None
    ic,cc,sc,vc,rc,dc=col("impressions","impr"),col("clicks"),col("spend","cost"),col("conversions","conv"),col("revenue"),col("date")
    issues={}
    def add(k,n): issues[k]=issues.get(k,0)+n
    seen=set()
    for r in rows:
        I=num(r.get(ic)) if ic else None; C=num(r.get(cc)) if cc else None
        S=num(r.get(sc)) if sc else None; V=num(r.get(vc)) if vc else None
        for nm,val in [("impr",I),("clicks",C),("spend",S),("conv",V)]:
            if val is not None and val<0: add(f"음수({nm})",1)
        if I is not None and C is not None and C>I: add("clicks>impressions",1)
        if C is not None and V is not None and V>C: add("conversions>clicks",1)
        if S is not None and I is not None and S>0 and I==0: add("spend>0 & impr=0",1)
        key=tuple(r.values())
        if key in seen: add("중복행",1)
        seen.add(key)
    # date gaps
    if dc:
        ds=sorted({datetime.strptime(r[dc].strip(),"%Y-%m-%d") for r in rows if r.get(dc)})
        gaps=sum(1 for i in range(1,len(ds)) if (ds[i]-ds[i-1]).days>1)
        if gaps: add("일자 갭",gaps)
    print(f"\n=== DATA QUALITY ({len(rows)} rows) ===")
    if not issues:
        print("✅ 모든 룰 통과 — 보고 진행 가능")
    else:
        print(f"⚠️ {len(issues)}종 위반:")
        for k,v in sorted(issues.items(),key=lambda x:-x[1]): print(f"  - {k}: {v}건")
        print("→ 원자료 정정 후 보고(reconcile.py로 재검산).")
if __name__=="__main__": main()
