"""
가격 최적화 — 일정탄력성 수요(q=k·p^e)에서 이익 최대 가격의 폐형식 해.
profit=(p−c)·q, dπ/dp=0 → p* = c·e/(e+1)  (e<−1에서 유한 최적). 계산 정확.
* 일정탄력성 가정. e≥−1이면 상한 없음(다른 모델 필요).

Usage: python price_optimizer.py --cost 10000 --elasticity -2 [--current-price 15000]
"""
import argparse
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cost",type=float,required=True); ap.add_argument("--elasticity",type=float,required=True)
    ap.add_argument("--current-price",type=float,default=None)
    a=ap.parse_args()
    e=a.elasticity
    print(f"\n=== PRICE OPTIMIZER (cost {a.cost:,.0f}, elasticity {e}) ===")
    if e>=-1:
        print("⚠️ |e|≤1 (비탄력적) → 이론상 가격 상한 없음. 시장가·경쟁 고려 필요."); return
    p=a.cost*e/(e+1)
    margin=(p-a.cost)/p
    print(f"이익 최대 가격 p* = {p:,.0f}  (마진율 {margin:.1%}, 마크업 {(p/a.cost-1):.0%})")
    if a.current_price:
        cur_m=(a.current_price-a.cost)/a.current_price
        print(f"현재가 {a.current_price:,.0f} (마진 {cur_m:.1%}) → {'인상' if p>a.current_price else '인하'} 여지 {abs(p-a.current_price):,.0f}")
    print("  · 폐형식 최적(일정탄력성). 실제는 경쟁·재고·브랜드 동시 고려, 테스트로 검증.")
if __name__=="__main__": main()
