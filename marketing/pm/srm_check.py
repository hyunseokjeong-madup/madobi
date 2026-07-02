"""
SRM(표본비율 불일치) 점검 — A/B 트래픽 배분이 기대비율(기본 50/50)에서 유의하게 벗어났는지 카이제곱 검정.
SRM이면 무작위배정·트래킹이 깨진 것 → 테스트 결과 무효. chi²=Σ(obs−exp)²/exp, df=1 임계 3.841(95%). 정확.

Usage: python srm_check.py --a-n 10000 --b-n 9000 [--expected 0.5]
"""
import argparse
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--a-n",type=int,required=True); ap.add_argument("--b-n",type=int,required=True)
    ap.add_argument("--expected",type=float,default=0.5,help="A 그룹 기대 비율")
    a=ap.parse_args()
    if not (0<a.expected<1):
        ap.error("--expected 는 0 초과 1 미만이어야 합니다 (기대 배분 비율).")
    tot=a.a_n+a.b_n
    if tot<=0:
        ap.error("--a-n + --b-n 합이 1 이상이어야 합니다 (관측 표본 0 불가).")
    ea=tot*a.expected; eb=tot*(1-a.expected)
    chi=(a.a_n-ea)**2/ea + (a.b_n-eb)**2/eb
    crit=3.841
    print(f"\n=== SRM CHECK (chi-square, df=1) ===")
    print(f"관측 A={a.a_n:,} ({a.a_n/tot:.2%}) · B={a.b_n:,} ({a.b_n/tot:.2%})")
    print(f"기대 A={ea:,.0f} · B={eb:,.0f}")
    print(f"chi² = {chi:.3f}  (임계 {crit} @95%)")
    if chi>crit:
        print("🔴 SRM 감지 — 배분/트래킹 결함 의심. 테스트 결과 신뢰 불가, 원인 점검 후 재시작.")
    else:
        print("🟢 SRM 없음 — 배분 정상. 테스트 진행 가능.")
if __name__=="__main__": main()
