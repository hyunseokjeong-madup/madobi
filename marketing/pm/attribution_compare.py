"""어트리뷰션 비교. 두 전환 소스(예: 플랫폼 vs GA/내부)의 합계와 격차(%)를 대사."""
import argparse, csv, re
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--a-col",required=True); ap.add_argument("--b-col",required=True)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    sa=sum(num(r.get(a.a_col)) for r in rows); sb=sum(num(r.get(a.b_col)) for r in rows)
    diff=sa-sb; pct=diff/sb if sb else 0
    print(f"\n=== ATTRIBUTION COMPARE ===")
    print(f"{a.a_col} 합 {sa:,.0f}  vs  {a.b_col} 합 {sb:,.0f}")
    print(f"격차 {diff:+,.0f} ({pct:+.1%})")
    if abs(pct)>0.1:
        print("⚠️ 10% 초과 격차 — 윈도우/모델/중복귀속/뷰스루 차이 점검, 실매출 기준 합의 필요.")
    else:
        print("🟢 격차 10% 이내 — 허용 범위(기준 명시).")
if __name__=="__main__": main()
