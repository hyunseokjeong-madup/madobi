"""
반응곡선 적합(포화) — Hill/Michaelis 곡선 y = Vmax·x/(K+x) 을 (지출,전환) 점들에서 적합.
선형화 1/y = 1/Vmax + (K/Vmax)·(1/x) 의 OLS로 Vmax,K 복원(정확). 현재 한계효율·포화도 산출.

입력 CSV: spend, conversions(또는 revenue)
Usage: python saturation_fit.py curve.csv
"""
import argparse, csv
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    h={c.lower():c for c in rows[0]}
    xc=h.get("spend") or h.get("cost"); yc=h.get("conversions") or h.get("conv") or h.get("revenue")
    xs=[]; ys=[]
    for r in rows:
        x=num(r.get(xc)); y=num(r.get(yc))
        if x>0 and y>0: xs.append(1/x); ys.append(1/y)
    n=len(xs)
    if n<2: print("데이터 부족"); return
    mx=sum(xs)/n; my=sum(ys)/n
    sxx=sum((x-mx)**2 for x in xs); sxy=sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    slope=sxy/sxx; intercept=my-slope*mx
    Vmax=1/intercept if intercept else 0; K=slope*Vmax
    xmax=max(num(r.get(xc)) for r in rows)
    # marginal dy/dx = Vmax*K/(K+x)^2
    marg=Vmax*K/((K+xmax)**2) if (K+xmax) else 0
    cur=Vmax*xmax/(K+xmax) if (K+xmax) else 0
    print(f"\n=== SATURATION FIT (Hill, n={n}) ===")
    print(f"Vmax(상한) = {Vmax:,.1f} · K(반포화 지출) = {K:,.0f}")
    print(f"현재 최대지출 {xmax:,.0f}에서: 전환 {cur:,.1f} (= 상한의 {cur/Vmax:.0%}, 포화도)")
    print(f"한계효율 dy/dx = {marg:.6f} 전환/원  (지출↑ 시 체감)")
    print("  · 포화도 높으면 증액 효율↓ → 타 채널/소재로 분산 검토. 적합은 추정.")
if __name__=="__main__": main()
