"""
믹스-시프트 분해 — 블렌디드 CPA 변화를 '믹스 효과'(채널 비중 변화)와 '단가 효과'(채널별 CPA 변화)로 분해.
blended CPA = Σ w_i·cpa_i (w=전환 비중). Δ = 믹스 + 단가 + 상호작용 (합=실제 Δ, 정확).

입력 CSV: channel, conv_a, spend_a, conv_b, spend_b
Usage: python mix_shift.py data.csv
"""
import argparse, csv
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=load_rows(a.csv)
    name=list(rows[0])[0]
    ch=[]
    for r in rows:
        ca,sa,cb,sb=(num(r.get(k)) for k in ("conv_a","spend_a","conv_b","spend_b"))
        ch.append(((r.get(name) or "").strip(),ca,sa,cb,sb))
    TA=sum(x[1] for x in ch); TB=sum(x[3] for x in ch)
    blendedA=sum(x[2] for x in ch)/TA if TA else 0
    blendedB=sum(x[4] for x in ch)/TB if TB else 0
    mix=rate=inter=0
    for nm,ca,sa,cb,sb in ch:
        wa=ca/TA if TA else 0; wb=cb/TB if TB else 0
        cpaa=sa/ca if ca else 0; cpab=sb/cb if cb else 0
        mix+=(wb-wa)*cpaa; rate+=wa*(cpab-cpaa); inter+=(wb-wa)*(cpab-cpaa)
    delta=blendedB-blendedA
    print(f"\n=== MIX-SHIFT (blended CPA {blendedA:,.0f} → {blendedB:,.0f}, Δ {delta:+,.0f}) ===")
    print(f"  믹스 효과(비중 변화)  : {mix:+,.0f}")
    print(f"  단가 효과(CPA 변화)   : {rate:+,.0f}")
    print(f"  상호작용             : {inter:+,.0f}")
    print(f"  합계 {mix+rate+inter:+,.0f} = 실제 Δ {delta:+,.0f}  {'✅' if abs(mix+rate+inter-delta)<1 else '⚠️'}")
    print("  · 믹스효과 크면 채널 배분 변화가 주범, 단가효과 크면 채널 자체 효율 변화.")
if __name__=="__main__": main()
