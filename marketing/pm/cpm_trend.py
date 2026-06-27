"""
CPM 추세 — 일별 CPM의 선형 추세로 경매 경쟁/시즌 압력 진단. CPM 상승 = 경쟁 심화·인벤토리 부족.
일별 CPM = spend/impressions×1000. OLS 기울기 + 시작→끝 변화율. 계산 정확.

입력 CSV: date, impressions, spend
Usage: python cpm_trend.py daily.csv
"""
import argparse, csv
from datetime import datetime
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    dcol=next((h for h in rows[0] if h.lower() in ("date","날짜","일자","day")),None)
    h={c.lower():c for c in rows[0]}; ic=h.get("impressions") or h.get("impr"); spc=h.get("spend")
    s=[]
    for r in rows:
        try: d=datetime.strptime(r[dcol].strip(),"%Y-%m-%d")
        except: continue
        I=num(r.get(ic)); S=num(r.get(spc))
        if I>0: s.append((d, S/I*1000))
    s.sort()
    n=len(s)
    if n<3: print("데이터 부족"); return
    d0=s[0][0]; xs=[(d-d0).days for d,_ in s]; ys=[c for _,c in s]
    mx=sum(xs)/n; my=sum(ys)/n
    sxx=sum((x-mx)**2 for x in xs) or 1e-9; sxy=sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    slope=sxy/sxx
    chg=(ys[-1]-ys[0])/ys[0] if ys[0] else 0
    print(f"\n=== CPM TREND ({n}일) ===")
    print(f"시작 CPM {ys[0]:,.0f} → 끝 CPM {ys[-1]:,.0f}  (변화 {chg:+.1%})")
    print(f"일평균 추세 {slope:+,.0f}/일")
    if slope>0 and chg>0.1:
        print("🔴 CPM 상승 추세 — 경매 경쟁/시즌 압력. 타게팅 효율·소재 관련성으로 방어, 예산 시점 조정.")
    elif slope<0:
        print("🟢 CPM 하락 — 효율 개선/경쟁 완화. 증액 기회 검토.")
    else:
        print("🟡 안정.")
    print("  · 추세 추정. 소재 관련성↑이 CPM 완화에 기여.")
if __name__=="__main__": main()
