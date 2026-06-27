"""
계절성 반영 예측 — 선형 추세 × 요일 계절지수로 향후 N일 예측.
추세: 일자 인덱스 OLS. 계절지수: 요일평균/전체평균. 예측 = 추세값 × 요일지수. 계산 정확. * 추정.

입력 CSV: date, <metric>
Usage: python seasonal_forecast.py series.csv --metric revenue --days 7
"""
import argparse, csv
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv")
    ap.add_argument("--metric",default="revenue"); ap.add_argument("--days",type=int,default=7)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    dcol=next((h for h in rows[0] if h.lower() in ("date","날짜","일자","day")),None)
    s=sorted(((datetime.strptime(r[dcol].strip(),"%Y-%m-%d"),num(r.get(a.metric))) for r in rows),key=lambda x:x[0])
    d0=s[0][0]; xs=[(d-d0).days for d,_ in s]; ys=[v for _,v in s]; n=len(xs)
    mx=sum(xs)/n; my=sum(ys)/n
    sxx=sum((x-mx)**2 for x in xs) or 1e-9; sxy=sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    slope=sxy/sxx; intercept=my-slope*mx
    # weekday index on detrended ratio
    overall=my or 1
    wd=defaultdict(list)
    for i,(d,v) in enumerate(s):
        trend=intercept+slope*xs[i]
        if trend>0: wd[d.weekday()].append(v/trend)
    widx={k:(sum(v)/len(v)) for k,v in wd.items()}
    DOW=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    last=s[-1][0]
    print(f"\n=== SEASONAL FORECAST ({a.metric}, +{a.days}일) ===")
    print(f"추세: 절편 {intercept:,.0f} + 기울기 {slope:,.0f}/일")
    for i in range(1,a.days+1):
        d=last+timedelta(days=i); xi=(d-d0).days
        base=intercept+slope*xi; idx=widx.get(d.weekday(),1.0)
        print(f"  {d.date()} ({DOW[d.weekday()]}) 예측 {base*idx:,.0f}  (추세 {base:,.0f} × 지수 {idx:.2f})")
    print("  · 추세×요일계절. 단기 예측. 시즌이벤트는 별도 보정.")
if __name__=="__main__": main()
