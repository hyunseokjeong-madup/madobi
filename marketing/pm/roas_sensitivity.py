"""
ROAS 민감도 — ROAS=(CVR×AOV)/CPC 에서 각 드라이버 ±변화가 ROAS에 미치는 영향 표.
폐형식(곱셈 모델)이라 변화는 정확. 어떤 레버가 ROAS를 가장 크게 움직이는지.

Usage: python roas_sensitivity.py --cvr 0.05 --aov 50000 --cpc 1000 [--pcts 10,20]
"""
import argparse
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cvr",type=float,required=True); ap.add_argument("--aov",type=float,required=True); ap.add_argument("--cpc",type=float,required=True)
    ap.add_argument("--pcts",default="10,20")
    a=ap.parse_args()
    base=a.cvr*a.aov/a.cpc
    pcts=[float(p)/100 for p in a.pcts.split(",")]
    print(f"\n=== ROAS SENSITIVITY (base ROAS {base:.2f}x) ===")
    print("driver".ljust(8)+"".join(f"{p:+.0%}".rjust(10) for p in [-pcts[-1],-pcts[0],pcts[0],pcts[-1]]))
    drivers={"CVR":lambda f:(a.cvr*(1+f))*a.aov/a.cpc,
             "AOV":lambda f:a.cvr*(a.aov*(1+f))/a.cpc,
             "CPC":lambda f:a.cvr*a.aov/(a.cpc*(1+f))}
    for d,fn in drivers.items():
        cells="".join(f"{fn(s):.2f}x".rjust(10) for s in [-pcts[-1],-pcts[0],pcts[0],pcts[-1]])
        print(d.ljust(8)+cells)
    print("  · CVR·AOV는 비례(↑→ROAS↑), CPC는 반비례(↑→ROAS↓). 곱셈모델이라 같은 %면 효과 대칭.")
if __name__=="__main__": main()
