"""요일별 성과 히트맵. 날짜 컬럼 → 요일별 지표 집계(가중) + 막대."""
import argparse, csv, re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
DOW=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--metric",default="revenue")
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    dcol=next((h for h in rows[0] if h.lower() in ("date","날짜","일자","day")),None)
    if not dcol: print("날짜 컬럼 없음"); return
    agg=defaultdict(float)
    for r in rows:
        try: wd=datetime.strptime((r.get(dcol) or "").strip(),"%Y-%m-%d").weekday()
        except: continue
        agg[wd]+=num(r.get(a.metric))
    mx=max(agg.values()) if agg else 1
    print(f"\n=== DAY-OF-WEEK HEATMAP ({a.metric}) ===")
    for i,d in enumerate(DOW):
        v=agg.get(i,0); bar="█"*int(round(v/mx*30)) if mx else ""
        print(f"  {d} {v:>14,.0f} {bar}")
    if agg:
        best=max(agg,key=agg.get); worst=min(agg,key=agg.get)
        print(f"\n최고 {DOW[best]} · 최저 {DOW[worst]} → 요일별 예산/입찰 가중 검토")
if __name__=="__main__": main()
