"""검색어 분석. 지출은 큰데 전환 0인 검색어 → 네거티브 키워드 후보. 전환 좋은 검색어 → 확대 후보."""
import argparse, csv, re
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--min-spend",type=float,default=50000)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    h=rows[0]; term=list(h)[0]
    def find(p): return next((c for c in h if re.fullmatch(p,c,re.I)),None)
    sc,cc=find("spend|cost|비용|광고비"),find("conversions|conv|전환")
    neg=[]; win=[]
    for r in rows:
        t=(r.get(term) or "").strip(); sp=num(r.get(sc)); cv=num(r.get(cc))
        if sp>=a.min_spend and cv==0: neg.append((t,sp))
        elif cv>0: win.append((t,sp,cv,sp/cv))
    neg.sort(key=lambda x:-x[1]); win.sort(key=lambda x:x[3])
    print(f"\n=== SEARCH TERMS ===")
    print(f"네거티브 후보(지출≥{a.min_spend:,.0f}, 전환0): {len(neg)}")
    for t,sp in neg[:10]: print(f"  ⛔ '{t}' spend={sp:,.0f} → 네거티브 추가 검토")
    print(f"\n확대 후보(전환 발생, 낮은 CPA순): {len(win)}")
    for t,sp,cv,cpa in win[:10]: print(f"  ✅ '{t}' conv={cv:.0f} CPA={cpa:,.0f}")
    waste=sum(x[1] for x in neg)
    print(f"\n네거티브 후보 낭비 지출 합 {waste:,.0f}")
if __name__=="__main__": main()
