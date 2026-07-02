"""
KPI 변동 요인분해 — CPA = CPC / CVR 의 기간 변화(A→B)를 CPC효과·CVR효과로 로그분해.
ln(CPA_b/CPA_a) = ln(CPC_b/CPC_a) - ln(CVR_b/CVR_a). 각 효과의 %기여 정확.
원자료(spend/clicks/conv) 또는 직접 CPC/CVR 입력.

Usage:
  python kpi_decomp.py --cpc-a 500 --cvr-a 0.05 --cpc-b 600 --cvr-b 0.04
  python kpi_decomp.py --a 1800000,3600,180 --b 2400000,3600,144   # spend,clicks,conv
"""
import argparse, math
def parse(t):
    sp,ck,cv=[float(x) for x in t.split(",")]
    return sp/ck, cv/ck  # cpc, cvr
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--a"); ap.add_argument("--b")
    ap.add_argument("--cpc-a",type=float); ap.add_argument("--cvr-a",type=float)
    ap.add_argument("--cpc-b",type=float); ap.add_argument("--cvr-b",type=float)
    x=ap.parse_args()
    if x.a and x.b:
        cpc_a,cvr_a=parse(x.a); cpc_b,cvr_b=parse(x.b)
    elif None not in (x.cpc_a,x.cvr_a,x.cpc_b,x.cvr_b):
        cpc_a,cvr_a,cpc_b,cvr_b=x.cpc_a,x.cvr_a,x.cpc_b,x.cvr_b
    else:
        ap.error("입력 필요: --a/--b (spend,clicks,conv) 쌍 또는 --cpc-a/--cvr-a/--cpc-b/--cvr-b 4개 모두")
    if min(cpc_a,cvr_a,cpc_b,cvr_b)<=0:
        ap.error("CPC/CVR 값이 모두 0 초과여야 합니다 (로그분해에 비율·나눗셈 필요).")
    cpa_a=cpc_a/cvr_a; cpa_b=cpc_b/cvr_b
    L=math.log(cpa_b/cpa_a)
    lc=math.log(cpc_b/cpc_a); lv=-math.log(cvr_b/cvr_a)
    # %contribution to total log-change
    tot=lc+lv
    print(f"\n=== KPI DECOMPOSITION: CPA = CPC / CVR ===")
    print(f"A: CPC {cpc_a:,.0f}, CVR {cvr_a:.2%} → CPA {cpa_a:,.0f}")
    print(f"B: CPC {cpc_b:,.0f}, CVR {cvr_b:.2%} → CPA {cpa_b:,.0f}")
    print(f"CPA 변화 {(cpa_b/cpa_a-1):+.1%}")
    print(f"  · CPC 효과: {lc:+.4f} log ({(math.exp(lc)-1):+.1%} CPA 영향)")
    print(f"  · CVR 효과: {lv:+.4f} log ({(math.exp(lv)-1):+.1%} CPA 영향)")
    if abs(tot)>1e-9:
        print(f"  기여 비중 → CPC {lc/tot:+.0%}, CVR {lv/tot:+.0%}")
    print(f"  해석: CPA 상승 주범이 단가(CPC)인지 전환율(CVR) 하락인지 분리.")
if __name__=="__main__": main()
