"""
멀티터치 어트리뷰션(MTA) 엔진 — 경로(touchpoint) CSV에서 채널 기여를 5개 모델로 배분.
모델: first-touch / last-touch / linear / time-decay(반감기) / position-based(40-20-40).

입력 CSV 컬럼: path_id, step(순서 정수 또는 timestamp), channel, value(전환가치; 경로당 동일/마지막에 표기), converted(1/0; 생략 시 value>0를 전환으로 간주)
경로 단위로 정렬해 전환 경로에만 가치를 배분한다.

Usage: python attribution_mta.py paths.csv --half-life 2 --md out.md
"""
import argparse, csv, math, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
from collections import defaultdict, OrderedDict

def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return 0.0

def load(path):
    rows=load_rows(path)
    h={c.lower():c for c in rows[0]}
    def col(*names):
        for n in names:
            if n in h: return h[n]
        return None
    pid,stp,ch,val,cv = col("path_id","path","user_id"),col("step","order","timestamp","time"),col("channel","source"),col("value","revenue","conv_value"),col("converted","conversion")
    paths=defaultdict(list)
    for r in rows:
        paths[r[pid]].append((r.get(stp,""), r.get(ch,"").strip(), num(r.get(val)), (num(r.get(cv)) if cv else None)))
    return paths

def credit(paths, half_life):
    models=["first","last","linear","time_decay","position"]
    out={m:defaultdict(float) for m in models}
    def step_key(t):
        # step은 숫자('1','2',…,'10') 또는 timestamp 문자열 — 문자열 사전순은 '10'<'2' 오정렬.
        # 숫자면 (0, 실수값)로 먼저 정렬, 비숫자(timestamp 등)는 (1, 원문)로 뒤에 사전순.
        try:
            return (0, float(t[0]))
        except (ValueError, TypeError):
            return (1, str(t[0]))
    for pid,touches in paths.items():
        touches=sorted(touches, key=step_key)
        chans=[t[1] for t in touches]
        # conversion value: last non-zero value, or sum; converted if any cv==1 or any value>0
        conv=any((t[3]==1) for t in touches) if any(t[3] is not None for t in touches) else any(t[2]>0 for t in touches)
        value=max([t[2] for t in touches] or [0]) or sum(t[2] for t in touches)
        if not conv or not chans or value<=0: continue
        n=len(chans)
        out["first"][chans[0]]+=value
        out["last"][chans[-1]]+=value
        for c in chans: out["linear"][c]+=value/n
        # time-decay: weight 2^(-(distance from last)/half_life)
        w=[2**(-((n-1-i))/half_life) for i in range(n)]; sw=sum(w)
        for i,c in enumerate(chans): out["time_decay"][c]+=value*w[i]/sw
        # position-based 40/20/40
        if n==1: out["position"][chans[0]]+=value
        elif n==2:
            out["position"][chans[0]]+=value*0.5; out["position"][chans[-1]]+=value*0.5
        else:
            out["position"][chans[0]]+=value*0.4; out["position"][chans[-1]]+=value*0.4
            for c in chans[1:-1]: out["position"][c]+=value*0.2/(n-2)
    return models,out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--half-life",type=float,default=2.0); ap.add_argument("--md",default=None)
    a=ap.parse_args()
    paths=load(a.csv); models,out=credit(paths,a.half_life)
    chans=sorted({c for m in models for c in out[m]})
    print(f"\n=== MULTI-TOUCH ATTRIBUTION ({len(paths)} paths, half-life {a.half_life}) ===")
    hdr="channel".ljust(14)+"".join(m.ljust(13) for m in models)
    print(hdr)
    for c in chans:
        print(c.ljust(14)+"".join(f"{out[m][c]:>12,.0f} " for m in models))
    print("\n해석: last/first는 단일터치 편향, linear는 균등, time_decay는 최근 가중, position은 처음·끝 강조.")
    if a.md:
        L=[f"# MTA — `{Path(a.csv).name}` ({len(paths)} paths, half-life {a.half_life})","",
           "| channel | "+" | ".join(models)+" |","|"+"---|"*(len(models)+1)]
        for c in chans: L.append("| "+c+" | "+" | ".join(f"{out[m][c]:,.0f}" for m in models)+" |")
        Path(a.md).write_text("\n".join(L)+"\n",encoding="utf-8"); print(f"[md] -> {a.md}")

if __name__=="__main__": main()
