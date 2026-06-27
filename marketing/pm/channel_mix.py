"""채널 믹스 분석. 현재 지출 배분(%)과 ROAS를 비교해 과/저투자 채널을 식별."""
import argparse, csv, re
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--by",default=None)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    by=a.by or list(rows[0])[0]
    def find(p): return next((c for c in rows[0] if re.fullmatch(p,c,re.I)),None)
    sc,rc=find("spend|cost|비용|광고비"),find("revenue|매출|수익")
    agg={}
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(by) or ""),re.I): continue
        k=(r.get(by) or "").strip(); agg.setdefault(k,[0,0])
        agg[k][0]+=num(r.get(sc)); agg[k][1]+=num(r.get(rc))
    tot=sum(v[0] for v in agg.values()) or 1
    avg_roas=sum(v[1] for v in agg.values())/ (sum(v[0] for v in agg.values()) or 1)
    print(f"\n=== CHANNEL MIX (총지출 {tot:,.0f}, 평균 ROAS {avg_roas:.2f}x) ===")
    for k,(sp,rv) in sorted(agg.items(),key=lambda x:-x[1][0]):
        ro=rv/sp if sp else 0; share=sp/tot
        sig="🔼 증액 검토" if ro>avg_roas else ("🔽 감액 검토" if ro<avg_roas else "—")
        print(f"  {k.ljust(14)} 지출비중 {share:>6.1%}  ROAS {ro:>5.2f}x  {sig}")
    print("  원칙: 평균 ROAS 상회 채널로 점진 이동(한계 체감 고려, 테스트 병행).")
if __name__=="__main__": main()
