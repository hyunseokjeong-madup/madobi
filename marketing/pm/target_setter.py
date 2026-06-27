"""
목표 역산(goal-seek) — 목표 ROAS/CPA 달성에 필요한 입력값 역산.
ROAS = (CVR×AOV)/CPC → 최대 허용 CPC = CVR×AOV/목표ROAS. 또는 필요 CVR = 목표ROAS×CPC/AOV.
목표 CPA = CPC/CVR → 필요 CVR = CPC/목표CPA. 계산 정확(대수 항등식).

Usage:
  python target_setter.py --target-roas 3 --aov 50000 --cvr 0.05         # 최대 CPC
  python target_setter.py --target-roas 3 --aov 50000 --cpc 1000         # 필요 CVR
  python target_setter.py --target-cpa 8000 --cpc 400                     # 필요 CVR
"""
import argparse
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--target-roas",type=float); ap.add_argument("--target-cpa",type=float)
    ap.add_argument("--aov",type=float); ap.add_argument("--cvr",type=float); ap.add_argument("--cpc",type=float)
    a=ap.parse_args()
    print(f"\n=== TARGET SETTER ===")
    if a.target_roas and a.aov and a.cvr:
        cpc=a.cvr*a.aov/a.target_roas
        print(f"목표 ROAS {a.target_roas}x · AOV {a.aov:,.0f} · CVR {a.cvr:.1%}")
        print(f"→ 최대 허용 CPC = {cpc:,.0f}원 (이하로 입찰해야 목표 달성)")
    elif a.target_roas and a.aov and a.cpc:
        cvr=a.target_roas*a.cpc/a.aov
        print(f"목표 ROAS {a.target_roas}x · AOV {a.aov:,.0f} · CPC {a.cpc:,.0f}")
        print(f"→ 필요 CVR = {cvr:.2%} (LP/오퍼로 이 이상 달성해야)")
    elif a.target_cpa and a.cpc:
        cvr=a.cpc/a.target_cpa
        print(f"목표 CPA {a.target_cpa:,.0f} · CPC {a.cpc:,.0f}")
        print(f"→ 필요 CVR = {cvr:.2%}")
    else:
        print("입력 조합 필요: (target-roas, aov, cvr) | (target-roas, aov, cpc) | (target-cpa, cpc)"); return
    print("  · 대수 항등식 역산(정확). 실제 달성은 입찰·LP·타깃 최적화로.")
if __name__=="__main__": main()
