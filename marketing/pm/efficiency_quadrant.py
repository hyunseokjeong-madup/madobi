"""
효율 사분면 — 채널/소재를 볼륨(지출)×효율(ROAS) 2×2로 분류해 액션 매트릭스 제시.
중앙값 분할: 고볼륨·고효율=Scale / 고볼륨·저효율=Fix / 저볼륨·고효율=Grow / 저볼륨·저효율=Cut. 계산 정확.

입력 CSV: name, spend, revenue
Usage: python efficiency_quadrant.py data.csv
"""
import argparse, csv, re
from pathlib import Path
from statistics import median
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    name=list(rows[0])[0]; h={c.lower():c for c in rows[0]}; sc,rc=h.get("spend"),h.get("revenue")
    ents=[]
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(name) or ""),re.I): continue
        sp=num(r.get(sc)); rv=num(r.get(rc)); ents.append(((r.get(name) or "").strip(),sp,rv/sp if sp else 0))
    if len(ents)<2: print("데이터 부족"); return
    mv=median(e[1] for e in ents); me=median(e[2] for e in ents)
    quad={"Scale(증액)":[],"Fix(개선)":[],"Grow(육성)":[],"Cut(축소)":[]}
    for nm,sp,ro in ents:
        hv=sp>=mv; he=ro>=me
        q="Scale(증액)" if hv and he else "Fix(개선)" if hv and not he else "Grow(육성)" if (not hv) and he else "Cut(축소)"
        quad[q].append((nm,sp,ro))
    print(f"\n=== EFFICIENCY QUADRANT (볼륨중앙값 {mv:,.0f}, ROAS중앙값 {me:.2f}x) ===")
    for q in ["Scale(증액)","Grow(육성)","Fix(개선)","Cut(축소)"]:
        items=", ".join(f"{nm}({ro:.1f}x)" for nm,_,ro in quad[q]) or "—"
        print(f"  {q.ljust(12)}: {items}")
    print("  · Scale=고볼륨고효율 증액 · Grow=저볼륨고효율 확대 · Fix=고볼륨저효율 개선 · Cut=저볼륨저효율 축소.")
if __name__=="__main__": main()
