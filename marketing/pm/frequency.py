"""빈도(frequency) 캡 점검. freq=노출/도달. 캡 초과 시 피로·예산낭비 경보."""
import argparse
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--impressions",type=float,required=True); ap.add_argument("--reach",type=float,required=True)
    ap.add_argument("--cap",type=float,default=3.0)
    a=ap.parse_args()
    f=a.impressions/a.reach if a.reach else 0
    over=f>a.cap
    print(f"\n=== FREQUENCY ===")
    print(f"노출 {a.impressions:,.0f} / 도달 {a.reach:,.0f} = 빈도 {f:.2f}  (캡 {a.cap})")
    print(f"{'🔴 캡 초과 — 피로/낭비 위험, 도달 확대 또는 빈도 제한' if over else '🟢 정상 범위'}")
if __name__=="__main__": main()
