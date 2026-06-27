"""
포화곡선 기반 예산배분 — 채널별 Hill 반응(y=Vmax·x/(K+x))에서 한계전환 균등화로 총전환 최대 배분.
한계 dy/dx=Vmax·K/(K+x)^2. 작은 단위로 한계 최대 채널에 그리디 배분(라그랑주 최적 동치). 배분 산술 정확.

입력 CSV: channel, vmax, k   (saturation_fit.py 결과 활용)
Usage: python budget_response_alloc.py params.csv --budget 30000000 [--steps 3000]
"""
import argparse, csv
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv")
    ap.add_argument("--budget",type=float,required=True); ap.add_argument("--steps",type=int,default=3000)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    h={c.lower():c for c in rows[0]}; nc=list(rows[0])[0]; vc=h.get("vmax"); kc=h.get("k")
    ch={(r.get(nc) or "").strip():(num(r.get(vc)),num(r.get(kc))) for r in rows}
    alloc={c:0.0 for c in ch}
    step=a.budget/a.steps
    def marg(c):
        V,K=ch[c]; x=alloc[c]; return V*K/((K+x)**2) if (K+x) else 0
    rem=a.budget
    while rem>1e-9:
        c=max(ch,key=marg); add=min(step,rem); alloc[c]+=add; rem-=add
    print(f"\n=== BUDGET RESPONSE ALLOCATION (budget {a.budget:,.0f}) ===")
    print("channel".ljust(14)+"배분".rjust(14)+"전환(추정)".rjust(13)+"한계효율".rjust(12))
    tot=0
    for c in sorted(ch,key=lambda c:-alloc[c]):
        V,K=ch[c]; x=alloc[c]; conv=V*x/(K+x) if (K+x) else 0; tot+=conv
        print(f"{c.ljust(14)}{x:>14,.0f}{conv:>13,.1f}{marg(c):>12.6f}")
    print(f"\n총 추정전환 {tot:,.1f} · 배분합 {sum(alloc.values()):,.0f}(=예산)")
    print("  · 한계전환 균등화가 최적. 곡선은 추정 → 점진 집행·재적합으로 검증.")
if __name__=="__main__": main()
