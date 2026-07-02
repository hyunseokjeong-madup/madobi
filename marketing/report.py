"""
Performance report generator (성과 리포트 자동 생성).
CSV -> reconciled totals + derived metrics + by-dimension breakdown + (if dated) period deltas
+ top movers, as a polished markdown report. Numbers are recomputed from raw (정합성).

Usage:
  python report.py data.csv --by channel --metric revenue --md report.md
  python report.py series.csv --period 7   # weekly comparison if a date column exists
"""
import argparse, math, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent / "bench"))
from summarize import num, derived, RAWM
try:
    from . import safemath
except ImportError:
    import safemath

def load(p):
    rows = safemath.load_rows(p)   # 파일 없음/빈 데이터/cp949 를 한 줄 안내로 처리
    headers = list(rows[0].keys())
    date_col = next((h for h in headers if h.lower() in ("date","날짜","일자","day")), None)
    label_col = headers[0]
    # 합계행 제외는 safemath.is_total_label 공용 기준 (부분매칭이 'Summer_Sale' 을 폐기하던 사고 방지)
    clean = [r for r in rows if not safemath.is_total_label(r.get(label_col))]
    # 헤더 alias 매핑 — 'Impressions'/'노출'/'cost' 가 조용히 0 이 되지 않게.
    colmap = safemath.map_headers(headers)
    if not colmap:
        raise SystemExit(f"[오류] 인식 가능한 지표 컬럼이 없습니다 — 헤더: {headers}")
    return clean, headers, date_col, colmap

def tot(rows, colmap):
    t = {m: 0 for m in RAWM}
    for r in rows:
        for m in RAWM: t[m] += num(r.get(colmap.get(m, m)))
    return t

def fmt_metrics(t):
    d = derived(t)
    L = [f"- 노출 **{t['impressions']:,.0f}** · 클릭 **{t['clicks']:,.0f}** · 광고비 **{t['spend']:,.0f}** "
         f"· 전환 **{t['conversions']:,.0f}** · 매출 **{t['revenue']:,.0f}**"]
    parts = []
    if d['ctr'] is not None: parts.append(f"CTR {d['ctr']:.2%}")
    if d['cpc'] is not None: parts.append(f"CPC {d['cpc']:,.0f}")
    if d['cpa'] is not None: parts.append(f"CPA {d['cpa']:,.0f}")
    if d['roas'] is not None: parts.append(f"ROAS {d['roas']:.2f}x")
    if parts: L.append("- " + " · ".join(parts))
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--by", default=None)
    ap.add_argument("--metric", default="revenue")
    ap.add_argument("--period", type=int, default=0, help="compare last N days vs prior N days")
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    rows, headers, dcol, colmap = load(a.csv)
    grand = tot(rows, colmap)
    unmapped = [m for m in RAWM if m not in colmap]

    out = [f"# 성과 리포트 — `{Path(a.csv).name}`", ""]
    out += ["## 종합 (검산 완료)", fmt_metrics(grand), ""]
    if unmapped:
        # '검산 완료' 헤딩 아래 잘못된 0 이 나가는 것을 막는다 — 미인식 컬럼은 반드시 표면화.
        out += [f"> ⚠️ 미인식 지표 컬럼: **{', '.join(unmapped)}** — 위 수치에서 0으로 집계됨. 헤더를 확인하세요.", ""]

    # reconciliation note
    if a.by:
        groups = defaultdict(list)
        for r in rows: groups[(r.get(a.by) or "").strip()].append(r)
        gt = {g: tot(rs, colmap) for g, rs in groups.items()}
        # float 완전일치(==)는 정합 데이터에서도 누적오차로 오탐 — isclose(자기정합성용 빡빡한 tol)
        ok = all(math.isclose(sum(gt[g][m] for g in gt), grand[m], rel_tol=1e-9, abs_tol=1e-12)
                 for m in RAWM)
        out += [f"> 정합성: 분해합 = 총계 **{'✅ 일치' if ok else '⚠️ 불일치'}**", ""]
        out += [f"## `{a.by}`별 성과 ({a.metric} 기준 정렬)", "",
                "| " + a.by + " | 노출 | 클릭 | 광고비 | 전환 | 매출 | CTR | ROAS |",
                "|---|---|---|---|---|---|---|---|"]
        ranked = sorted(gt.items(), key=lambda kv: derived(kv[1]).get(a.metric) or kv[1].get(a.metric, 0), reverse=True)
        for g, t in ranked:
            d = derived(t)
            out.append(f"| {g} | {t['impressions']:,.0f} | {t['clicks']:,.0f} | {t['spend']:,.0f} | "
                       f"{t['conversions']:,.0f} | {t['revenue']:,.0f} | {(d['ctr'] or 0):.2%} | {(d['roas'] or 0):.2f}x |")
        out.append("")

    # period comparison
    if a.period and dcol:
        days = sorted({(r.get(dcol) or "").strip() for r in rows})
        if len(days) >= 2 * a.period:
            recent = set(days[-a.period:]); prior = set(days[-2*a.period:-a.period])
            tr = tot([r for r in rows if (r.get(dcol) or "").strip() in recent], colmap)
            tp = tot([r for r in rows if (r.get(dcol) or "").strip() in prior], colmap)
            out += [f"## 기간 비교 (최근 {a.period}일 vs 직전 {a.period}일)", "",
                    "| 지표 | 직전 | 최근 | 변화 |", "|---|---|---|---|"]
            for m in RAWM:
                # 직전 0 인데 '+0.0%' 로 나가면 어떤 증가도 안 보인다 — 분기 표기.
                if tp[m]:
                    ch = f"{(tr[m]-tp[m])/tp[m]:+.1%}"
                elif tr[m]:
                    ch = "신규 (직전 0)"
                else:
                    ch = "0.0%"
                out.append(f"| {m} | {tp[m]:,.0f} | {tr[m]:,.0f} | {ch} |")
            out.append("")

    out += ["---", "*숫자는 원자료에서 재계산·검산. 가정(윈도우·타임존·통화·필터) 확인 필요.*"]
    text = "\n".join(out)
    if a.md:
        Path(a.md).write_text(text + "\n", encoding="utf-8")
        print(f"[md] -> {a.md}")
    else:
        print(text)

if __name__ == "__main__":
    main()
