"""
Welch t-검정 — 두 그룹 평균 차이의 유의성(분산 다름 허용). 예: 세그먼트별 AOV 비교.
t=(mb−ma)/√(sa²/na+sb²/nb), Welch df. |t|>임계면 유의. p-value는 정규근사(대표본). 계산 정확.

Usage: python ttest.py --a-mean 50000 --a-sd 12000 --a-n 200 --b-mean 54000 --b-sd 15000 --b-n 180
"""
import argparse, math
def cdf(z): return 0.5*(1+math.erf(z/math.sqrt(2)))
def main():
    ap=argparse.ArgumentParser()
    for g in ("a","b"):
        ap.add_argument(f"--{g}-mean",type=float,required=True); ap.add_argument(f"--{g}-sd",type=float,required=True); ap.add_argument(f"--{g}-n",type=int,required=True)
    a=ap.parse_args()
    ma,sa,na=a.a_mean,a.a_sd,a.a_n; mb,sb,nb=a.b_mean,a.b_sd,a.b_n
    se=math.sqrt(sa*sa/na+sb*sb/nb)
    t=(mb-ma)/se if se else 0
    # Welch df
    df=(sa*sa/na+sb*sb/nb)**2/((sa*sa/na)**2/(na-1)+(sb*sb/nb)**2/(nb-1))
    p=2*(1-cdf(abs(t)))
    print(f"\n=== WELCH t-TEST ===")
    print(f"A: 평균 {ma:,.0f} (sd {sa:,.0f}, n {na})")
    print(f"B: 평균 {mb:,.0f} (sd {sb:,.0f}, n {nb})")
    print(f"차이 {mb-ma:+,.0f} · SE {se:,.1f} · t={t:+.3f} · df≈{df:.0f}")
    print(f"p-value(정규근사) ≈ {p:.4f}  →  {'유의(✅ 95%)' if p<0.05 else '비유의(❌)'}")
    print("  · 대표본 정규근사. 소표본은 t분포표 사용. 분산 이질성 허용(Welch).")
if __name__=="__main__": main()
