"""
Marketing number RECONCILIATION engine (정합성 검산).
Reads a CSV of marketing breakdown data and checks consistency:
  - derived metrics (CTR/CPC/CPM/CPA/ROAS) recomputed from raw vs reported
  - breakdown rows sum to the TOTAL row (or computed total)
  - ratio metrics use weighted (not simple) averaging  [Simpson trap]
  - unit/format cleaning (commas, %, currency)
Outputs a report with PASS (v) / WARN (!). Pure stdlib; no pandas needed.

Usage: python reconcile.py data.csv [--tol 0.01] [--json] [--md report.md]
"""
import csv, sys, re, json, argparse
from pathlib import Path

try:
    from . import safemath
except ImportError:  # 스크립트로 직접 실행될 때
    import safemath

RAW = ["impressions", "clicks", "spend", "conversions", "revenue"]
# raw alias 는 safemath._RAW_ALIASES 가 단일 소스 (도구 간 표류 방지). 파생지표 alias 만 여기 추가.
ALIASES = {k: list(safemath._RAW_ALIASES[k]) for k in RAW}
ALIASES.update({
    "ctr": ["ctr"], "cpc": ["cpc"], "cpm": ["cpm"], "cpa": ["cpa", "cpi"], "roas": ["roas"],
})

def num(s):
    if s is None: return None
    s = str(s).strip().replace(",", "").replace("₩", "").replace("$", "").replace("%", "")
    if s in ("", "-", "—", "N/A", "na", "NaN"): return None
    try: return float(s)
    except ValueError: return None

def num2(s):
    """num() + '%' 명시 여부 플래그 — CTR 스케일(분수 vs 퍼센트) 판정용."""
    return num(s), isinstance(s, str) and "%" in s

def find_col(headers, key):
    low = {h.lower().strip(): h for h in headers}
    for a in ALIASES[key]:
        if a in low: return low[a]
    return None

def derive(r):
    out = {}
    imp, clk, sp, cv, rv = (r.get(k) for k in RAW)
    if imp and clk is not None: out["ctr"] = clk / imp
    if clk and sp is not None: out["cpc"] = sp / clk
    if imp and sp is not None: out["cpm"] = sp / imp * 1000
    if cv and sp is not None: out["cpa"] = sp / cv
    if sp and rv is not None: out["roas"] = rv / sp
    if clk and cv is not None: out["cvr"] = cv / clk          # 전환율
    if imp and rv is not None: out["ecpm"] = rv / imp * 1000  # 퍼블리셔 eCPM
    return out

def close(a, b, tol):
    if a is None or b is None: return None
    denom = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / denom <= tol

def fmt(v):
    """사람이 읽는 수 표기 — 지수표기 금지(4.1e+06 → 4,100,000), 천단위 콤마.
    None(계산 불가)은 '-' — num() 이 결측으로 되읽는 문자라 라운드트립 일관."""
    if v is None: return "-"
    if abs(v) >= 100:
        s = f"{v:,.2f}"
        return s[:-3] if s.endswith(".00") else s
    return f"{v:.4g}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--tol", type=float, default=0.01)
    ap.add_argument("--md", default=None, help="write a markdown report to this path")
    ap.add_argument("--json", action="store_true",
                    help="사람용 텍스트 대신 JSON 한 줄 출력 (에이전트/스크립트 연동)")
    a = ap.parse_args()
    # 파일 없음 / 빈 데이터 / cp949(엑셀 한국어 저장) 를 traceback 없이 한 줄 안내로 처리
    rows = safemath.load_rows(a.csv)
    headers = list(rows[0].keys())
    colmap = {k: find_col(headers, k) for k in ALIASES}
    label_col = headers[0]

    parsed, total_row = [], None
    for r in rows:
        rec, pctf = {}, {}
        for k in ALIASES:
            rec[k], pctf[k] = num2(r.get(colmap[k])) if colmap[k] else (None, False)
        rec["_pct"] = pctf
        rec["_label"] = (r.get(label_col) or "").strip()
        # 합계행 판정은 safemath.is_total_label 공용 기준 —
        # 과거 부분매칭(re.search)이 'Summer_Sale' 의 'Sum' 에 걸려 실데이터를 조용히 폐기했다.
        if safemath.is_total_label(rec["_label"]):
            total_row = rec
        else:
            parsed.append(rec)

    warns, passes, notes = [], [], []

    # 0) CTR 스케일(분수 vs 퍼센트)은 컬럼 단위로 1회 결정.
    #    행마다 1배/100배 양쪽을 OR 로 허용하면 실제 100배(단위) 오류가 CONSISTENT 로 통과한다.
    ctr_scale, _ratios = None, []
    for rec in parsed:
        d = derive(rec)
        rep = rec.get("ctr")
        if rep is not None and d.get("ctr"):
            if rec["_pct"].get("ctr"):
                ctr_scale = 100          # 셀에 '%' 명시 → 이 컬럼은 퍼센트 표기 확정
                break
            _ratios.append(rep / d["ctr"])
    if ctr_scale is None and _ratios:
        med = sorted(_ratios)[len(_ratios) // 2]
        if 0.5 <= med <= 2:
            ctr_scale = 1
        elif 50 <= med <= 200:
            ctr_scale = 100
            notes.append("~ [SCALE] ctr: '%' 미표기 컬럼을 중앙값 기준 percent 스케일로 추정 — 원자료 확인 권장")
        # 그 외(중앙값이 1도 100도 아님) → None 유지: 아래에서 SCALE AMBIGUOUS WARN

    # 1) per-row derived metric reconciliation
    for rec in parsed:
        d = derive(rec)
        for m in ["ctr", "cpc", "cpm", "cpa", "roas"]:
            rep = rec.get(m)
            if rep is not None and m in d:
                if m == "ctr":
                    if ctr_scale == 100:
                        ok = bool(close(rep, d[m] * 100, a.tol))
                        shown = f"reported={rep:g}% recomputed={d[m]:.4%}"
                    elif ctr_scale == 1:
                        ok = bool(close(rep, d[m], a.tol))
                        shown = f"reported={fmt(rep)} recomputed={d[m]:.4f} (fraction)"
                    else:
                        ok = False
                        shown = (f"reported={rep:g} recomputed={d[m]:.4%} "
                                 f"[SCALE AMBIGUOUS - 분수/퍼센트 판별 불가]")
                else:
                    ok = bool(close(rep, d[m], a.tol))
                    shown = f"reported={fmt(rep)} recomputed={fmt(d[m])}"
                msg = f"[{rec['_label']}] {m}: {shown}"
                (passes if ok else warns).append(("v " if ok else "! ") + msg)

    # 2) breakdown sum == total row
    sums = {k: sum(r[k] for r in parsed if r.get(k) is not None) for k in RAW}
    if total_row:
        for k in RAW:
            if total_row.get(k) is not None:
                ok = close(sums[k], total_row[k], a.tol)
                msg = f"[SUM] {k}: rows_sum={fmt(sums[k])} vs total_row={fmt(total_row[k])}"
                (passes if ok else warns).append(("v " if ok else "! ") + msg)

    # 3) Simpson / weighted-vs-simple ratio trap
    ctrs = [derive(r).get("ctr") for r in parsed if derive(r).get("ctr") is not None]
    if ctrs and sums["impressions"]:
        weighted = sums["clicks"] / sums["impressions"]
        simple = sum(ctrs) / len(ctrs)
        if close(weighted, simple, 0.05) is False:
            warns.append(f"! [RATIO] CTR simple-avg={simple:.4%} != weighted={weighted:.4%} "
                         f"(use weighted Sigma-clicks/Sigma-impr)")
        else:
            passes.append(f"v [RATIO] CTR weighted={weighted:.4%} (simple avg close)")

    # 가중 파생지표 — 0 분모는 None('-') 으로. max(x,1e-9) 나눗셈은 쓰레기 값(1e15) 을 만들었다.
    dw = {
        "ctr": safemath.safe_div(sums["clicks"], sums["impressions"], default=None),
        "cpc": safemath.safe_div(sums["spend"], sums["clicks"], default=None),
        "cpm": safemath.safe_div(sums["spend"], sums["impressions"], default=None),
        "roas": safemath.safe_div(sums["revenue"], sums["spend"], default=None),
    }
    if dw["cpm"] is not None:
        dw["cpm"] *= 1000.0

    # verdict 는 stdout·--md·--json 세 출력이 공유하는 단일 판정 —
    # "인식된 컬럼 0개인데 CONSISTENT" 같은 거짓 양성을 막는다.
    raw_found = [k for k in RAW if colmap[k]]
    derived_found = [m for m in ("ctr", "cpc", "cpm", "cpa", "roas") if colmap[m]]
    if not raw_found and not derived_found:
        verdict, sym = "NO DATA RECOGNIZED - 인식 가능한 지표 컬럼이 없습니다 (헤더를 확인하세요)", " !"
    elif not passes and not warns:
        verdict, sym = "NO CHECKS RUN - 검산할 보고값/합계행이 없습니다 (재계산 totals 만 제공)", " ~"
    elif warns:
        verdict, sym = f"{len(warns)} INCONSISTENCY(IES) - investigate raw data", " !"
    else:
        verdict, sym = "CONSISTENT", " v"

    if a.json:
        payload = {
            "file": a.csv, "rows": len(parsed), "total_row": bool(total_row), "tol": a.tol,
            "totals": {k: sums[k] for k in RAW}, "derived_weighted": dw,
            "checks": {"pass": len(passes), "warn": len(warns)},
            "warnings": [w[2:] for w in warns], "notes": [n[2:] for n in notes],
            "verdict": verdict,
        }
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"\n=== RECONCILIATION: {a.csv}  (tol={a.tol:.0%}) ===")
        print(f"rows={len(parsed)}  total_row={'yes' if total_row else 'no'}")
        print(f"\n-- weighted totals --")
        print(f"  impressions={sums['impressions']:,.0f}  clicks={sums['clicks']:,.0f}  "
              f"spend={sums['spend']:,.0f}  conversions={sums['conversions']:,.0f}  revenue={sums['revenue']:,.0f}")
        if dw["ctr"] is not None:
            roas_s = f"{fmt(dw['roas'])}x" if dw["roas"] is not None else "-"
            print(f"  CTR={dw['ctr']:.4%}  CPC={fmt(dw['cpc'])}  CPM={fmt(dw['cpm'])}  ROAS={roas_s}")
        print(f"\n-- checks: {len(passes)} PASS, {len(warns)} WARN --")
        for n in notes: print("  " + n)
        for w in warns: print("  " + w)
        if not warns: print("  (all consistency checks passed)")
        print(f"\nVERDICT: {verdict}{sym}")

    if a.md:
        ok_mark = "✅ " if verdict == "CONSISTENT" else "⚠️ "
        lines = [f"# Reconciliation Report — `{Path(a.csv).name}`", "",
                 f"- rows: **{len(parsed)}**  ·  total row: **{'yes' if total_row else 'no'}**  ·  tol: {a.tol:.0%}",
                 f"- verdict: **{ok_mark}{verdict}**", "",
                 "## Totals (weighted)", "",
                 "| metric | value |", "|---|---|",
                 f"| impressions | {sums['impressions']:,.0f} |", f"| clicks | {sums['clicks']:,.0f} |",
                 f"| spend | {sums['spend']:,.0f} |", f"| conversions | {sums['conversions']:,.0f} |",
                 f"| revenue | {sums['revenue']:,.0f} |"]
        if dw["ctr"] is not None:
            lines += [f"| CTR | {dw['ctr']:.4%} |", f"| CPC | {fmt(dw['cpc'])} |",
                      f"| CPM | {fmt(dw['cpm'])} |",
                      f"| ROAS | {fmt(dw['roas'])}{'x' if dw['roas'] is not None else ''} |"]
        lines += ["", "## Consistency checks", ""]
        if warns:
            lines += [f"- ⚠️ {w[2:]}" for w in warns]
        else:
            lines += ["- ✅ all consistency checks passed"]
        Path(a.md).write_text("\n".join(lines) + "\n", encoding="utf-8")
        if not a.json:
            print(f"\n[md] report written -> {a.md}")

if __name__ == "__main__":
    main()
