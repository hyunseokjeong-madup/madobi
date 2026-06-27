"""목표 CPA/ROAS 가드레일 체커. 엔티티별로 목표 위반을 경보."""
import argparse, csv, re
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--by",default=None)
    ap.add_argument("--target-cpa",type=float,default=None)
    ap.add_argument("--target-roas",type=float,default=None)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    by=a.by or list(rows[0])[0]
    def find(p): return next((c for c in rows[0] if re.fullmatch(p,c,re.I)),None)
    sc,cc,rc=find("spend|cost|비용|광고비"),find("conversions|conv|전환"),find("revenue|매출|수익")
    agg={}
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(by) or ""),re.I): continue
        k=(r.get(by) or "").strip(); agg.setdefault(k,[0,0,0])
        agg[k][0]+=num(r.get(sc)); agg[k][1]+=num(r.get(cc)); agg[k][2]+=num(r.get(rc))
    print(f"\n=== GUARDRAILS (target CPA≤{a.target_cpa}, ROAS≥{a.target_roas}) ===")
    breaches=0
    for k,(sp,cv,rv) in sorted(agg.items(),key=lambda x:-x[1][0]):
        cpa=sp/cv if cv else None; roas=rv/sp if sp else None
        flags=[]
        if a.target_cpa and cpa is not None and cpa>a.target_cpa: flags.append(f"CPA {cpa:,.0f}>{a.target_cpa:,.0f}")
        if a.target_roas and roas is not None and roas<a.target_roas: flags.append(f"ROAS {roas:.2f}<{a.target_roas:.2f}")
        if flags: breaches+=1
        tag="⚠️ "+", ".join(flags) if flags else "✅"
        print(f"  {k.ljust(16)} spend={sp:>12,.0f} CPA={cpa or 0:>8,.0f} ROAS={roas or 0:>5.2f}x  {tag}")
    print(f"\n위반 {breaches}건 — 입찰/예산 조정 또는 일시중지 검토")
if __name__=="__main__": main()
