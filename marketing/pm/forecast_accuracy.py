"""
예측 정확도 — 실제 vs 예측의 MAE/MAPE/RMSE/bias 산출. 모델 신뢰도 평가. 계산 정확.

입력 CSV: actual, forecast (열 이름 자유: actual/forecast 또는 a/f)
Usage: python forecast_accuracy.py af.csv
"""
import argparse, csv, math
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return None
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    h={c.lower():c for c in rows[0]}
    ac=h.get("actual") or h.get("a"); fc=h.get("forecast") or h.get("pred") or h.get("f")
    pairs=[(num(r.get(ac)),num(r.get(fc))) for r in rows]
    pairs=[(x,y) for x,y in pairs if x is not None and y is not None]
    n=len(pairs)
    if not n: print("데이터 없음"); return
    mae=sum(abs(x-y) for x,y in pairs)/n
    mape=sum(abs(x-y)/abs(x) for x,y in pairs if x)/sum(1 for x,_ in pairs if x)
    rmse=math.sqrt(sum((x-y)**2 for x,y in pairs)/n)
    bias=sum(y-x for x,y in pairs)/n
    print(f"\n=== FORECAST ACCURACY (n={n}) ===")
    print(f"MAE  = {mae:,.2f}")
    print(f"MAPE = {mape:.2%}")
    print(f"RMSE = {rmse:,.2f}")
    print(f"Bias = {bias:+,.2f}  ({'과대예측' if bias>0 else '과소예측' if bias<0 else '무편향'})")
    g="우수" if mape<0.1 else ("양호" if mape<0.2 else "개선필요")
    print(f"판정: MAPE {mape:.1%} → {g}. 편향 크면 모델 보정.")
if __name__=="__main__": main()
