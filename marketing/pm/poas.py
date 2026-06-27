"""POAS — 마진 반영 수익성 ROAS. POAS=매출×마진/광고비. 손익분기 마진도 계산."""
import argparse
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--revenue",type=float,required=True); ap.add_argument("--spend",type=float,required=True)
    ap.add_argument("--margin",type=float,required=True,help="제품 마진율 0~1 (예: 0.3)")
    a=ap.parse_args()
    roas=a.revenue/a.spend if a.spend else 0
    poas=a.revenue*a.margin/a.spend if a.spend else 0
    be_margin=a.spend/a.revenue if a.revenue else 0
    print(f"\n=== POAS (margin {a.margin:.0%}) ===")
    print(f"ROAS {roas:.2f}x · 마진반영 POAS {poas:.2f}x  ({'🟢 수익' if poas>=1 else '🔴 손실'})")
    print(f"손익분기 마진율 = {be_margin:.1%} (이 이상이어야 광고가 흑자)")
if __name__=="__main__": main()
