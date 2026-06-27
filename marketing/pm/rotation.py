"""소재 로테이션/리프레시. 노출 충분한데 CTR 낮은 소재 → 교체 후보. 신선도 우선순위 제시."""
import argparse, csv, re
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--min-impr",type=float,default=30000)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    name=list(rows[0])[0]
    def find(p): return next((c for c in rows[0] if re.fullmatch(p,c,re.I)),None)
    ic,cc=find("impressions|impr|노출"),find("clicks|클릭")
    ent=[]
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(name) or ""),re.I): continue
        im=num(r.get(ic)); ck=num(r.get(cc)); ctr=ck/im if im else 0
        ent.append(((r.get(name) or "").strip(),im,ctr))
    qualified=[e for e in ent if e[1]>=a.min_impr]
    avg=sum(e[2] for e in qualified)/len(qualified) if qualified else 0
    refresh=sorted([e for e in qualified if e[2]<avg*0.8],key=lambda e:-e[1])
    print(f"\n=== CREATIVE ROTATION (평균 CTR {avg:.2%}, min impr {a.min_impr:,.0f}) ===")
    if refresh:
        print(f"교체/리프레시 후보 {len(refresh)} (노출 큰 순):")
        for n,im,ctr in refresh: print(f"  🔄 {n}  impr={im:,.0f} CTR={ctr:.2%} (평균 대비 낮음)")
    else:
        print("✅ 즉시 교체 후보 없음")
    print("  원칙: 신규 소재 상시 파이프라인 + 피로(빈도↑·CTR↓) 모니터.")
if __name__=="__main__": main()
