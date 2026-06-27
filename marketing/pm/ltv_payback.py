"""LTV·페이백. CAC 회수 기간(개월)과 LTV/CAC 비율. 마진 반영."""
import argparse
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cac",type=float,required=True,help="고객획득비용")
    ap.add_argument("--arpu",type=float,required=True,help="월 ARPU(고객당 월매출)")
    ap.add_argument("--margin",type=float,default=1.0,help="공헌마진율 0~1")
    ap.add_argument("--lifetime",type=float,default=12,help="평균 수명(개월)")
    a=ap.parse_args()
    monthly=a.arpu*a.margin
    payback=a.cac/monthly if monthly else float('inf')
    ltv=monthly*a.lifetime
    ratio=ltv/a.cac if a.cac else 0
    print(f"\n=== LTV / PAYBACK ===")
    print(f"월 공헌 {monthly:,.0f} · CAC {a.cac:,.0f} → 페이백 {payback:.1f}개월")
    print(f"LTV({a.lifetime:.0f}개월) {ltv:,.0f} · LTV/CAC = {ratio:.1f}x  "
          f"({'🟢 건전(≥3x)' if ratio>=3 else '🟡 점검(<3x)'})")
if __name__=="__main__": main()
