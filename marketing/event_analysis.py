"""
Event / campaign time-series analyzer (이벤트·캠페인 분석).
Pre/post lift around an event date, budget pacing, and anomaly detection (z-score).
Recomputes from raw (정합성). Pure stdlib.

Usage:
  python event_analysis.py series.csv --metric revenue --event 2026-01-10 --budget 30000000 --md out.md
"""
import argparse, statistics as st
from pathlib import Path
try:
    from . import safemath
except ImportError:
    import safemath

def num(s):
    if s is None: return 0.0
    s = str(s).strip().replace(",", "").replace("₩", "").replace("$", "").replace("%", "")
    if s in ("", "-", "—", "N/A"): return 0.0
    try: return float(s)
    except ValueError: return 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--metric", default="revenue")
    ap.add_argument("--event", default=None, help="YYYY-MM-DD split (pre < event <= post)")
    ap.add_argument("--budget", type=float, default=None)
    ap.add_argument("--z", type=float, default=2.0)
    ap.add_argument("--md", default=None)
    a = ap.parse_args()

    rows = safemath.load_rows(a.csv)   # 파일 없음/빈 데이터/cp949 를 한 줄 안내로 처리
    if a.metric not in rows[0]:
        # 존재하지 않는 metric(오타)을 조용히 전부 0으로 분석하던 사고 방지
        raise SystemExit(f"[오류] metric '{a.metric}' 컬럼이 없습니다 — 컬럼: {sorted(rows[0])}")
    dcol = next((h for h in rows[0] if h.lower() in ("date", "날짜", "일자", "day")), list(rows[0])[0])
    series = sorted(((r[dcol].strip(), num(r.get(a.metric))) for r in rows), key=lambda x: x[0])
    days = [d for d, _ in series]; vals = [v for _, v in series]
    total = sum(vals); mean = st.mean(vals); sd = st.pstdev(vals) if len(vals) > 1 else 0

    # anomalies — segment-aware (pre/post split avoids regime-shift variance inflation)
    def detect(seg):
        vs = [v for _, v in seg]
        if len(vs) < 3: return []
        m = st.mean(vs); s = st.pstdev(vs)
        return [(d, v, (v - m)/s) for d, v in seg if s and abs((v - m)/s) >= a.z]
    if a.event:
        anomalies = detect([(d, v) for d, v in series if d < a.event]) + \
                    detect([(d, v) for d, v in series if d >= a.event])
    else:
        anomalies = detect(series)

    # pre/post lift
    lift = None
    if a.event:
        pre = [v for d, v in series if d < a.event]
        post = [v for d, v in series if d >= a.event]
        if pre and post:
            pa, qa = st.mean(pre), st.mean(post)
            lift = (pa, qa, (qa - pa)/pa if pa else None, len(pre), len(post))

    # pacing (assumes metric or a spend col)
    pacing = None
    if a.budget:
        spend_total = sum(num(r.get("spend", r.get(a.metric))) for r in rows)
        elapsed = len(days)
        daily = spend_total/elapsed if elapsed else 0
        pacing = (spend_total, spend_total/a.budget, daily)

    print(f"\n=== EVENT/CAMPAIGN ANALYSIS: {a.csv} (metric={a.metric}) ===")
    print(f"days={len(days)} ({days[0]}..{days[-1]})  total={total:,.0f}  mean/day={mean:,.0f}")
    if lift:
        pa, qa, lf, npre, npost = lift
        # 과거엔 print 전체를 감싼 조건식 때문에 pre 평균이 0이면 LIFT 줄이 통째로 사라졌다.
        lift_s = f"lift={lf:+.1%}" if lf is not None else "lift=계산불가(pre_avg=0)"
        print(f"\nLIFT around {a.event}: pre_avg={pa:,.0f} ({npre}d) -> post_avg={qa:,.0f} ({npost}d)  {lift_s}")
    if pacing:
        sp, pct, daily = pacing
        print(f"\nPACING: spend={sp:,.0f} / budget={a.budget:,.0f} = {pct:.1%}  (daily≈{daily:,.0f})")
    print(f"\nANOMALIES (|z|>={a.z}): {len(anomalies)}")
    for d, v, z in anomalies:
        print(f"  {d}: {v:,.0f}  (z={z:+.1f})  -> 원자료/타임존/중복 점검")
    if not anomalies: print("  (none)")

    if a.md:
        L = [f"# Event Analysis — `{Path(a.csv).name}` ({a.metric})", "",
             f"- days: {len(days)} ({days[0]}..{days[-1]}) · total: {total:,.0f} · mean/day: {mean:,.0f}"]
        if lift and lift[2] is not None:
            L.append(f"- **lift around {a.event}: {lift[2]:+.1%}** (pre {lift[0]:,.0f} → post {lift[1]:,.0f})")
        if pacing:
            L.append(f"- pacing: {pacing[1]:.1%} of budget ({pacing[0]:,.0f} / {a.budget:,.0f})")
        L += ["", f"**anomalies (|z|≥{a.z}): {len(anomalies)}**"]
        L += [f"- ⚠️ {d}: {v:,.0f} (z={z:+.1f})" for d, v, z in anomalies] or ["- none"]
        Path(a.md).write_text("\n".join(L) + "\n", encoding="utf-8")
        print(f"\n[md] -> {a.md}")

if __name__ == "__main__":
    main()
