"""시즌성(요일) 지수. 요일 평균/전체 평균 = 지수(>1 강세, <1 약세). 입찰·예산 가중 가이드."""
import argparse, csv
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
    s=defaultdict(list)
    for r in rows:
        try: wd=datetime.strptime((r.get(dcol) or "").strip(),"%Y-%m-%d").weekday()
        except: continue
        s[wd].append(num(r.get(a.metric)))
    allv=[v for vs in s.values() for v in vs]; overall=sum(allv)/len(allv) if allv else 1
    print(f"\n=== SEASONALITY INDEX ({a.metric}) — 전체평균 {overall:,.0f} ===")
    for i,d in enumerate(DOW):
        if s.get(i):
            avg=sum(s[i])/len(s[i]); idx=avg/overall if overall else 0
            tag="🔼" if idx>1.1 else ("🔽" if idx<0.9 else "—")
            print(f"  {d} 지수 {idx:.2f} {tag}  (평균 {avg:,.0f})")
    print("  지수>1 요일에 예산/입찰 가중, <1은 절감 검토.")
if __name__=="__main__": main()
