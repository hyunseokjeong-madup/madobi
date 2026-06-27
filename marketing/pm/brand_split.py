"""
브랜드 vs 논브랜드 분리 — 검색어를 브랜드 키워드 포함 여부로 분류해 성과 분해.
논브랜드는 신규 수요(증분), 브랜드는 기존 수요 방어. 집계 정확.

입력 CSV: term(첫 열), spend, conversions[, revenue]
Usage: python brand_split.py terms.csv --brand 브랜드명,brandname
"""
import argparse, csv, re
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--brand",required=True)
    a=ap.parse_args()
    bkw=[b.strip().lower() for b in a.brand.split(",") if b.strip()]
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    tcol=list(rows[0])[0]; h={c.lower():c for c in rows[0]}
    sc,cc,rc=h.get("spend"),h.get("conversions") or h.get("conv"),h.get("revenue")
    agg={"brand":[0.0,0.0,0.0],"nonbrand":[0.0,0.0,0.0]}
    for r in rows:
        t=(r.get(tcol) or "").strip().lower()
        seg="brand" if any(b in t for b in bkw) else "nonbrand"
        agg[seg][0]+=num(r.get(sc)); agg[seg][1]+=num(r.get(cc)); agg[seg][2]+=num(r.get(rc))
    tsp=sum(v[0] for v in agg.values()) or 1; tcv=sum(v[1] for v in agg.values()) or 1
    print(f"\n=== BRAND vs NON-BRAND ===")
    for seg in ("brand","nonbrand"):
        sp,cv,rv=agg[seg]; cpa=sp/cv if cv else 0; roas=rv/sp if sp else 0
        print(f"  {seg.ljust(9)} spend {sp:>12,.0f} ({sp/tsp:>5.1%}) · conv {cv:>6,.0f} ({cv/tcv:>5.1%}) · CPA {cpa:>8,.0f} · ROAS {roas:.2f}x")
    print(f"\n논브랜드 전환 비중 {agg['nonbrand'][1]/tcv:.1%} = 신규 수요 기여. 브랜드 잠식/방어 균형 점검.")
if __name__=="__main__": main()
