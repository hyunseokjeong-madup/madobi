"""예산 낭비 탐지. ROAS가 기준 미만인데 지출이 큰 엔티티 → 절감 후보."""
import argparse, csv, re
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--by",default=None); ap.add_argument("--min-roas",type=float,default=1.0)
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
    waste=[(k,sp,rv,(rv/sp if sp else 0)) for k,(sp,rv) in agg.items() if sp and (rv/sp)<a.min_roas]
    waste.sort(key=lambda x:-x[1])
    total_waste=sum(w[1] for w in waste)
    print(f"\n=== WASTE FINDER (ROAS < {a.min_roas:.2f}x) ===")
    if not waste: print("  ✅ 기준 미만 지출 없음"); return
    for k,sp,rv,ro in waste:
        print(f"  {k.ljust(16)} spend={sp:>12,.0f} revenue={rv:>12,.0f} ROAS={ro:.2f}x  ⚠️ 절감/개선")
    print(f"\n낭비 의심 지출 합 {total_waste:,.0f} — 소재/타깃/LP 개선 또는 예산 회수 검토")
if __name__=="__main__": main()
