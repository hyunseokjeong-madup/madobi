"""
예측 정확도 — 실제 vs 예측의 MAE/MAPE/RMSE/bias 산출. 모델 신뢰도 평가. 계산 정확.

입력 CSV: actual, forecast (열 이름 자유: actual/forecast 또는 a/f)
Usage: python forecast_accuracy.py af.csv
"""
import argparse, csv, math
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return None
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=load_rows(a.csv)
    h={c.lower():c for c in rows[0]}
    ac=h.get("actual") or h.get("a"); fc=h.get("forecast") or h.get("pred") or h.get("f")
    pairs=[(num(r.get(ac)),num(r.get(fc))) for r in rows]
    pairs=[(x,y) for x,y in pairs if x is not None and y is not None]
    n=len(pairs)
    if not n: print("데이터 없음"); return
    mae=sum(abs(x-y) for x,y in pairs)/n
    nz=sum(1 for x,_ in pairs if x)  # actual이 0이 아닌 표본 수(MAPE 분모)
    mape=sum(abs(x-y)/abs(x) for x,y in pairs if x)/nz if nz else None
    rmse=math.sqrt(sum((x-y)**2 for x,y in pairs)/n)
    bias=sum(y-x for x,y in pairs)/n
    print(f"\n=== FORECAST ACCURACY (n={n}) ===")
    print(f"MAE  = {mae:,.2f}")
    print(f"MAPE = {mape:.2%}" if mape is not None else "MAPE = N/A(actual 전부 0)")
    print(f"RMSE = {rmse:,.2f}")
    print(f"Bias = {bias:+,.2f}  ({'과대예측' if bias>0 else '과소예측' if bias<0 else '무편향'})")
    if mape is not None:
        g="우수" if mape<0.1 else ("양호" if mape<0.2 else "개선필요")
        print(f"판정: MAPE {mape:.1%} → {g}. 편향 크면 모델 보정.")
    else:
        print("판정: actual 전부 0 → MAPE 산출 불가. MAE/RMSE/bias로 평가.")
if __name__=="__main__": main()
