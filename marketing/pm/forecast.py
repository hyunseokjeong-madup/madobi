"""월말/기간말 예측. 현재 추세(일평균)로 목표 일수까지 spend/conversions/revenue 선형 투영."""
import argparse, csv, re
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--total-days",type=int,required=True,help="기간 총 일수(예: 월 30일)")
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    dcol=next((h for h in rows[0] if h.lower() in ("date","날짜","일자","day")),None)
    days=sorted({(r.get(dcol) or "").strip() for r in rows if dcol}) if dcol else []
    elapsed=len(days) or 1
    mets=["spend","conversions","revenue"]
    tot={m:sum(num(r.get(m)) for r in rows) for m in mets}
    print(f"\n=== FORECAST (경과 {elapsed}일 → {a.total_days}일 투영) ===")
    for m in mets:
        daily=tot[m]/elapsed; proj=daily*a.total_days
        print(f"  {m.ljust(12)} 현재 {tot[m]:>14,.0f}  · 일평균 {daily:>12,.0f}  → 예상 {proj:>15,.0f}")
    print("  주의: 선형 가정(시즌성·페이싱 변화 미반영). 추세 변동 시 재투영.")
if __name__=="__main__": main()
