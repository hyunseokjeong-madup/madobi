"""퍼널 드롭오프 분석 (impr→click→conv). 가장 약한 단계 식별. CSV 합계 또는 직접 인자."""
import argparse, csv, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv_pos", nargs="?", help="집계할 CSV 경로 (positional; --csv 와 동일)")
    ap.add_argument("--csv", help="집계할 CSV 경로 (--csv 스타일 하위호환)")
    ap.add_argument("--impr", type=float); ap.add_argument("--clicks", type=float); ap.add_argument("--conv", type=float)
    a=ap.parse_args()
    csv_path=a.csv or a.csv_pos
    if not csv_path and a.impr is None and a.clicks is None and a.conv is None:
        ap.error("--csv(또는 positional CSV) 또는 --impr/--clicks/--conv 필요")
    if csv_path:
        rows=load_rows(csv_path)
        def col(k):
            h=next((h for h in rows[0] if re.fullmatch(k,h,re.I)),None)
            if h is None:
                ap.error(f"CSV에 {k} 컬럼 없음 (헤더: {', '.join(rows[0])})")
            return sum(num(r.get(h)) for r in rows)
        impr,clk,cv=col("impressions|impr|노출"),col("clicks|클릭"),col("conversions|conv|전환")
    else:
        impr,clk,cv=a.impr or 0,a.clicks or 0,a.conv or 0
    if impr<=0:
        ap.error("노출(impressions)이 0 — 퍼널 산출 불가. 입력 데이터 확인 필요.")
    ctr=clk/impr if impr else 0; cvr=cv/clk if clk else 0; o=cv/impr if impr else 0
    stages=[("노출→클릭 통과", ctr),("클릭→전환 통과", cvr)]
    weakest=min(stages,key=lambda s:s[1])
    print(f"\n=== FUNNEL ===")
    print(f"노출 {impr:,.0f} → 클릭 {clk:,.0f} (CTR {ctr:.2%}) → 전환 {cv:,.0f} (CVR {cvr:.2%})")
    print(f"전체 전환율(노출대비) {o:.3%}")
    print(f"가장 약한 단계: **{weakest[0]} ({weakest[1]:.2%})** → 여기 개선이 레버리지 최대")
    print(f"  · 노출→클릭 약하면: 후크/타깃/소재. 클릭→전환 약하면: LP/오퍼/메시지매치.")
if __name__=="__main__": main()
