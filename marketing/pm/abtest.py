"""A/B 테스트 유의성 (two-proportion z-test). 전환율 A vs B가 통계적으로 유의한가."""
import argparse, math
def cdf(z): return 0.5*(1+math.erf(z/math.sqrt(2)))
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--a-n", type=int, required=True, help="A 시행수(클릭/노출)")
    ap.add_argument("--a-x", type=int, required=True, help="A 성공수(전환/클릭)")
    ap.add_argument("--b-n", type=int, required=True)
    ap.add_argument("--b-x", type=int, required=True)
    a=ap.parse_args()
    if a.a_n<=0 or a.b_n<=0:
        ap.error("--a-n, --b-n 은 1 이상이어야 합니다 (시행수 0 이하 불가).")
    pa=a.a_x/a.a_n; pb=a.b_x/a.b_n
    p=(a.a_x+a.b_x)/(a.a_n+a.b_n)
    se=math.sqrt(p*(1-p)*(1/a.a_n+1/a.b_n))
    z=(pb-pa)/se if se else 0
    pval=2*(1-cdf(abs(z)))
    sig=pval<0.05
    lift=(pb-pa)/pa if pa else 0
    print(f"\n=== A/B TEST ===")
    print(f"A: {a.a_x}/{a.a_n} = {pa:.3%}   B: {a.b_x}/{a.b_n} = {pb:.3%}   (B lift {lift:+.1%})")
    print(f"z = {z:+.2f}   p-value = {pval:.4f}")
    print(f"결론: {'✅ 유의함(95%) — 승자 채택 가능' if sig else '❌ 유의하지 않음 — 표본 더 필요'}")
    if not sig: print("  · 소표본 과해석 금지. 표본/기간을 늘려 재검정.")
if __name__=="__main__": main()
