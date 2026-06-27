"""
한계 CPA — 두 구간(증액 전/후)의 추가 지출당 추가 전환 비용. marginal CPA=Δspend/Δconv.
평균 CPA보다 한계 CPA가 높으면 증액 효율 체감(추가 획득이 비쌈). 계산 정확.

입력 CSV: channel, spend_a, conv_a, spend_b, conv_b
Usage: python marginal_cpa.py data.csv
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
    name=list(rows[0])[0]
    print(f"\n=== MARGINAL CPA ===")
    print("channel".ljust(12)+"평균CPA(b)".rjust(12)+"한계CPA".rjust(12)+"  판정")
    for r in rows:
        c=(r.get(name) or "").strip()
        sa,ca,sb,cb=(num(r.get(k)) for k in ("spend_a","conv_a","spend_b","conv_b"))
        avg=sb/cb if cb else 0
        dconv=cb-ca; dspend=sb-sa
        mcpa=dspend/dconv if dconv>0 else float('inf')
        if dconv<=0:
            verdict="⚠️ 증액에도 전환 정체/감소(포화·낭비)"
            mstr="∞"
        else:
            mstr=f"{mcpa:,.0f}"
            verdict="🔴 한계>평균(효율 체감)" if mcpa>avg*1.2 else ("🟢 한계≤평균(증액 여지)" if mcpa<=avg else "🟡 비슷")
        print(f"{c.ljust(12)}{avg:>12,.0f}{mstr:>12}  {verdict}")
    print("  · 한계 CPA가 목표 초과 채널은 증액 중단/재배분. 평균만 보면 놓침.")
if __name__=="__main__": main()
