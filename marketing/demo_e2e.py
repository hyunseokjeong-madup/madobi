"""
E2E 데모 — 마케터가 캠페인 CSV를 던졌을 때 MADOBI가 하는 전체 흐름을 한 번에 보여준다.
"산술은 코드가 보장, 통찰은 LLM이 판단"의 *코드 보장* 파트를 실제로 실행한다.

흐름: 맥락 회상 → 검산(reconcile) → 집계(summarize, TOTAL행 제외) → 삼중검증(있으면) → 정합성 판정.
이 스크립트는 기존 도구를 오케스트레이션만 한다(새 계산 로직 없음). 순수 stdlib.

사용:
  python marketing/demo_e2e.py                                  # 기본 샘플로 데모
  python marketing/demo_e2e.py marketing/samples/sample_campaign.csv --account demo_ecommerce
  python marketing/demo_e2e.py <your.csv> --selftest            # 비대화 검증(종료코드 0/1)
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo root
MARKETING = ROOT / "marketing"
DEFAULT_CSV = MARKETING / "samples" / "sample_campaign.csv"


def run(cmd):
    """도구 하나를 실행하고 (returncode, stdout) 반환. 순수 stdlib subprocess."""
    r = subprocess.run(
        [sys.executable, *cmd], cwd=str(ROOT),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def step(title):
    print(f"\n{'─' * 56}\n▶ {title}\n{'─' * 56}")


# prefetch 할 후보 카테고리 — 마케팅 분석에서 가장 자주 회상하는 지식 영역.
_PREFETCH_ARMS = ["metrics", "diagnostics", "budget_models", "creative", "audience"]


def _bandit_prefetch_category(query):
    """후보 카테고리별 recall_quality(코드산물 보상)로 UCB1 이 prefetch arm 을 고른다.

    부품(recall.recall_quality + bandit_policy.select_ucb1)을 실제로 잇는 시너지 조립.
    각 arm 을 한 번씩 관측(pulls=1)했다 보고 reward=회상품질로 점수화 → 결정론적 선택.
    import/계산 실패 시 None → 회상은 카테고리 없이도 정상 동작(우아한 폴백).
    """
    try:
        kdir = MARKETING / "knowledge"
        if str(kdir) not in sys.path:
            sys.path.insert(0, str(kdir))
        if str(MARKETING / "pm") not in sys.path:
            sys.path.insert(0, str(MARKETING / "pm"))
        import recall
        import bandit_policy
        arms = []
        for cat in _PREFETCH_ARMS:
            q = recall.recall_quality(query=query, category=cat, limit=3)
            arms.append((cat, q, 1))   # reward_sum=품질, pulls=1 (각 1회 관측)
        if not arms:
            return None
        choice, _scored = bandit_policy.select_ucb1(arms)
        return choice
    except Exception:
        return None


def demo(csv_path, account=None, quiet=False):
    """전체 E2E 흐름. 각 단계의 핵심 출력을 모아 dict로 반환(셀프테스트용)."""
    csv_path = Path(csv_path)
    out = {"csv": str(csv_path), "steps": {}}

    # 1) 맥락 회상 (계정 지정 시) — 검색 기반, 214개 전체 read 금지.
    #    어느 카테고리를 먼저 prefetch 할지는 bandit(UCB1)이 *회상 품질 보상*으로 고른다:
    #    recall_quality(코드 산물) → bandit arm 선택 → 그 카테고리로 회상. '돌수록 똑똑'의 실전.
    if account:
        if not quiet:
            step(f"1. 맥락 회상 — bandit(UCB1)이 회상품질로 prefetch 카테고리 선택 → recall.py (account={account})")
        picked = _bandit_prefetch_category("ROAS CPA")
        out["steps"]["prefetch_category"] = picked
        cmd = ["marketing/knowledge/recall.py", "--account", account, "--query", "ROAS CPA", "--limit", "3"]
        if picked:
            cmd += ["--category", picked]
        rc, o = run(cmd)
        out["steps"]["recall"] = rc
        if not quiet:
            if picked:
                print(f"  → bandit 선택 prefetch 카테고리: **{picked}** (UCB1 · 보상=recall_quality, 코드산물)")
            print(o.strip()[:600] or "(회상 결과 없음)")

    # 2) 검산 — reconcile.py: 보고값 vs 원자료 불일치 적발
    if not quiet:
        step("2. 검산 — reconcile.py (산술 오류·합계≠총계 적발)")
    rc, o = run(["marketing/reconcile.py", str(csv_path)])
    out["steps"]["reconcile_rc"] = rc
    out["steps"]["reconcile_verdict"] = "INCONSISTENCY" if "INCONSISTENCY" in o else "CONSISTENT"
    if not quiet:
        print(o.strip()[-700:])

    # 3) 집계 — summarize.py (TOTAL행 제외 = 이중계산 방지)
    if not quiet:
        step("3. 집계 — summarize.py (가중평균 Σ/Σ, TOTAL행 제외)")
    rc, o = run(["marketing/bench/summarize.py", str(csv_path), "--by", "creative"])
    out["steps"]["summarize_rc"] = rc
    if not quiet:
        print(o.strip()[:700])

    # 4) 삼중검증 — sql_query.py (duckdb 있으면 SQL↔파이썬 일치 확인, 없으면 자동 스킵)
    if not quiet:
        step("4. 삼중검증 — sql_query.py (DuckDB↔Python, 없으면 파이썬만)")
    rc, o = run(["marketing/sql_query.py", str(csv_path), "--group-by", "creative", "--metric", "roas"])
    out["steps"]["sql_query_rc"] = rc
    if not quiet:
        verdict = "VERIFIED" if "VERIFIED" in o or "verified" in o.lower() else "PYTHON-ONLY"
        print(f"  → {verdict}\n" + o.strip()[:400])

    # 5) 정합성 판정 한 줄
    if not quiet:
        step("5. 정합성 판정")
        verdict = out["steps"].get("reconcile_verdict")
        if verdict == "CONSISTENT":
            print("  ✅ CONSISTENT — 보고 가능 (산술 검산 통과)")
        else:
            print("  ⚠️  INCONSISTENCY 발견 — 원자료 spot-check 권고 (보고 전 점검)")
        print("\n  ※ 코드가 보장하는 것: 위 산술의 정확성. 보장 못 하는 것: 데이터 품질(채널 오분류 등).")

    return out


def _loop_roundtrip():
    """자기개선 루프 라운드트립: curate.upsert(중복=재검증) → recall(회상) 검증.

    learn.py 를 직접 부르지 않는다 — 그건 _GLOBAL.md 고정 + 기본 commit=True 라
    CI에서 실제 push 를 유발한다. 대신 같은 쓰기경로(curate.upsert_lesson)를
    marketing/knowledge/ 하위 임시 계정 파일에 적용하고, recall 로 노출까지 확인한 뒤
    임시 파일을 완전히 청소한다(부작용 0).
    """
    sys.path.insert(0, str(MARKETING / "knowledge"))
    import curate, recall  # 같은 폴더, stdlib only

    acct = "_e2e_selftest_tmp"
    kpath = MARKETING / "knowledge" / f"{acct}.md"
    try:
        if kpath.exists():
            kpath.unlink()
        fb = "주말 저녁 CPA가 평일보다 낮다 — 예산 가중"
        r1 = curate.upsert_lesson(kpath, "pacing", fb)
        r2 = curate.upsert_lesson(kpath, "pacing", "  주말   저녁 CPA가 평일보다 낮다 — 예산 가중 ")  # 변형
        assert r1 == "appended" and r2 == "updated", f"dedup 실패: {r1}/{r2}"
        lessons = [l for l in kpath.read_text(encoding="utf-8").splitlines() if l.startswith("- [")]
        assert len(lessons) == 1, f"중복 누적됨: {len(lessons)}줄"
        # 회상: 임시 계정 자산이 recall 에 노출되는가
        recalled = recall.recall(account=acct, query="CPA 주말", limit=3)
        assert acct in recalled or "CPA" in recalled.upper(), "회상이 임시 자산을 못 노출"
    finally:
        if kpath.exists():
            kpath.unlink()  # 임시 자산 청소 — 213개 실데이터 불변
    print("[selftest] 루프 라운드트립 OK — curate dedup(2→1줄, 재검증) → recall 노출")


def selftest():
    """비대화 검증: 기본 샘플로 흐름이 끝까지 도는지 + 알려진 불일치를 잡는지 + 루프 라운드트립."""
    # DEFAULT_CSV 부재를 '로직 결함'으로 오인하지 않도록 main() 과 대칭으로 먼저 확인.
    if not Path(DEFAULT_CSV).exists():
        print(f"[error] 기본 샘플 CSV 없음: {DEFAULT_CSV}", file=sys.stderr)
        return 1
    res = demo(DEFAULT_CSV, account="demo_ecommerce", quiet=True)
    s = res["steps"]
    # sample_campaign.csv 엔 의도된 불일치(C_carousel CTR, SUM spend)가 있음 → 반드시 적발해야 함
    assert s.get("reconcile_verdict") == "INCONSISTENCY", "reconcile이 알려진 불일치를 놓침"
    assert s.get("summarize_rc") == 0, "summarize 실행 실패"
    assert s.get("sql_query_rc") == 0, "sql_query 실행 실패"
    # 시너지 조립: bandit 이 회상품질 보상으로 prefetch 카테고리를 골랐는지 + 결정론
    picked = s.get("prefetch_category")
    assert picked in _PREFETCH_ARMS, f"bandit prefetch 선택 실패: {picked}"
    assert _bandit_prefetch_category("ROAS CPA") == picked, "prefetch 선택 비결정적"
    print(f"[selftest] 시너지 OK — bandit prefetch 카테고리='{picked}' (회상품질 보상·결정론)")
    _loop_roundtrip()
    print("[selftest] OK — E2E 흐름 정상 + 알려진 불일치 적발(reconcile=INCONSISTENCY)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="MADOBI E2E 데모 — 검산→집계→삼중검증 흐름")
    ap.add_argument("csv", nargs="?", default=str(DEFAULT_CSV), help="캠페인 CSV (기본: sample_campaign.csv)")
    ap.add_argument("--account", default=None, help="맥락 회상할 계정(예: demo_ecommerce)")
    ap.add_argument("--selftest", action="store_true", help="비대화 검증(종료코드 0/1)")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not Path(a.csv).exists():
        print(f"[error] CSV 없음: {a.csv}")
        return 1
    print("MADOBI E2E 데모 — '산술은 코드가 보장, 통찰은 LLM이 판단'")
    demo(a.csv, account=a.account)
    return 0


if __name__ == "__main__":
    sys.exit(main())
