"""
LTV 예측 — 관측 리텐션에서 기하감쇠(retention_n = r1 * d^(n-1)) 추정 후 horizon까지 외삽,
누적 LTV = arpu * Σretention. d는 연속 비율의 기하평균(정확). * 외삽은 추정 라벨.

입력 CSV: period(1,2,...), retention(0~1)  또는 관측 리텐션을 직접 입력.
Usage: python ltv_forecast.py retention.csv --arpu 10000 --horizon 12
"""
import argparse
from _pmutil import load_rows  # 빈 데이터 우아한 처리
def num(s):
    s=str(s or "").replace(",","").replace("%","").strip()
    try:
        v=float(s); return v/100 if v>1.5 else v
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv")
    ap.add_argument("--arpu",type=float,required=True,help="유지 사용자 1인당 기간 매출")
    ap.add_argument("--horizon",type=int,default=12)
    a=ap.parse_args()
    recs=[]
    for r in load_rows(a.csv):
        try: p=int(float(str(r.get("period")).strip()))
        except (TypeError, ValueError): continue
        recs.append((p, num(r.get("retention"))))
    recs.sort()
    if not recs:
        print("데이터 없음 — period/retention 컬럼의 유효한 행이 없습니다."); return
    obs={p:v for p,v in recs}
    # estimate decay d = geometric mean of consecutive ratios
    ratios=[]
    ps=sorted(obs)
    for i in range(1,len(ps)):
        if obs[ps[i-1]]>0: ratios.append(obs[ps[i]]/obs[ps[i-1]])
    d=(__import__("math").prod(ratios))**(1/len(ratios)) if ratios else 0.5
    r1=obs[ps[0]]
    proj={}
    for n in range(1,a.horizon+1):
        proj[n]=obs.get(n, r1*(d**(n-1)))
    cum=0; ltv=[]
    for n in range(1,a.horizon+1):
        cum+=proj[n]*a.arpu; ltv.append((n,proj[n],cum))
    print(f"\n=== LTV FORECAST (arpu={a.arpu:,.0f}, decay d={d:.3f}, horizon={a.horizon}) ===")
    print("period  retention  누적LTV")
    for n,ret,c in ltv:
        tag="(관측)" if n in obs else "(추정)"
        print(f"  P{n:<4}{ret*100:>7.1f}%   {c:>12,.0f}  {tag}")
    print(f"\n예상 {a.horizon}기 LTV/유저 = {ltv[-1][2]:,.0f}  · 외삽은 추정(감쇠 일정 가정).")
if __name__=="__main__": main()
