"""MER (Marketing Efficiency Ratio) = 총매출/총광고비. 채널귀속 무관 전사 효율."""
import argparse
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--revenue",type=float,required=True); ap.add_argument("--spend",type=float,required=True)
    a=ap.parse_args()
    mer=a.revenue/a.spend if a.spend else 0
    print(f"\n=== MER ===")
    print(f"총매출 {a.revenue:,.0f} / 총광고비 {a.spend:,.0f} = MER {mer:.2f}x")
    print(f"광고비 비중(매출 대비) {a.spend/a.revenue:.1%}  ({'🟢' if mer>=3 else '🟡'})")
    print("  MER은 어트리뷰션 무관 총량 지표 — 플랫폼 ROAS 합산 왜곡 보완.")
if __name__=="__main__": main()
