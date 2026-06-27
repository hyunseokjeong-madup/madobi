"""
증분성(홀드아웃 RCT) — 노출군 vs PSA/홀드아웃 대조군의 전환율 차이로 순증분 추정.
incremental = test_conv − test_n×control_rate. lift% = (tr−cr)/cr. 95% CI(두 비율 SE). 계산 정확.

Usage: python incrementality_ab.py --test-n 100000 --test-conv 3000 --control-n 100000 --control-conv 2500
"""
import argparse, math
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--test-n",type=int,required=True); ap.add_argument("--test-conv",type=int,required=True)
    ap.add_argument("--control-n",type=int,required=True); ap.add_argument("--control-conv",type=int,required=True)
    a=ap.parse_args()
    tr=a.test_conv/a.test_n; cr=a.control_conv/a.control_n
    diff=tr-cr
    inc=a.test_conv-a.test_n*cr
    lift=diff/cr if cr else 0
    se=math.sqrt(tr*(1-tr)/a.test_n + cr*(1-cr)/a.control_n)
    lo,hi=diff-1.96*se, diff+1.96*se
    z=diff/se if se else 0
    print(f"\n=== INCREMENTALITY (holdout RCT) ===")
    print(f"노출군 전환율 {tr:.3%} ({a.test_conv}/{a.test_n})")
    print(f"대조군 전환율 {cr:.3%} ({a.control_conv}/{a.control_n})")
    print(f"절대 리프트 {diff:+.3%}  ·  상대 리프트 {lift:+.1%}")
    print(f"순증분 전환 = {inc:,.0f}건")
    print(f"95% CI(절대리프트) [{lo:+.3%}, {hi:+.3%}]  ·  z={z:.2f} {'유의(✅)' if abs(z)>1.96 else '비유의(❌)'}")
    print("  · 증분=광고로 인한 순증가(플랫폼 전환과 다름). CI가 0 포함 시 무의미.")
if __name__=="__main__": main()
