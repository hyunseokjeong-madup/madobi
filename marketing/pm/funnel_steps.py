"""
다단계 퍼널 누수 — 단계별 사용자 수에서 통과율/이탈률 계산, 최대 누수 단계 식별. 계산 정확.

입력 CSV: step(첫 열, 순서대로), users
Usage: python funnel_steps.py funnel.csv
"""
import argparse, csv
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    sname=list(rows[0])[0]; h={c.lower():c for c in rows[0]}; uc=h.get("users") or list(rows[0])[1]
    steps=[((r.get(sname) or "").strip(),num(r.get(uc))) for r in rows]
    if len(steps)<2: print("단계 부족"); return
    print(f"\n=== FUNNEL ({len(steps)} steps) ===")
    print("step".ljust(18)+"users".rjust(12)+"통과율".rjust(9)+"이탈률".rjust(9))
    worst=None
    for i,(nm,u) in enumerate(steps):
        if i==0: print(f"{nm.ljust(18)}{u:>12,.0f}{'—':>9}{'—':>9}"); continue
        prev=steps[i-1][1]; rate=u/prev if prev else 0; drop=1-rate
        if worst is None or drop>worst[1]: worst=((steps[i-1][0],nm),drop)
        print(f"{nm.ljust(18)}{u:>12,.0f}{rate:>8.1%}{drop:>8.1%}")
    overall=steps[-1][1]/steps[0][1] if steps[0][1] else 0
    print(f"\n전체 전환율(첫→끝) {overall:.2%}")
    if worst: print(f"🔴 최대 누수: {worst[0][0]} → {worst[0][1]} (이탈 {worst[1]:.1%}) — 우선 개선 대상")
if __name__=="__main__": main()
