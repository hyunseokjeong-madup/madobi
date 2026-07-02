"""
프롬프트 행동계약 채점기 (결정론) — 에이전트 프롬프트의 응답이 행동 계약을 지켰는지 판정.

madobi의 "측정으로 고른 프롬프트" 원칙을 서비스 프롬프트(.claude/agents + SKILL)에도 적용하는
평가 하네스의 채점 단계. LLM 채점 없음 — 계약은 전부 regex/길이 assertion 이라 같은 응답이면
같은 점수(재현 가능·감사 가능).

계약 스키마 (scenarios.json):
  must:  전부 매칭되어야 하는 regex 목록 ("a|b" 로 대안 표현)
  forbid: 하나라도 매칭되면 FAIL
  max_chars / max_question_marks: 챗봇 톤 계약(짧은 답, 딱 1개 되묻기)

Usage:
  python research/prompt_eval/grade.py results.json      # [{scenario, arm, answer}] 채점
  python research/prompt_eval/grade.py --selftest
"""
import json
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent


def load_scenarios(path=None):
    p = Path(path) if path else HERE / "scenarios.json"
    return {s["id"]: s for s in json.loads(p.read_text(encoding="utf-8"))}


def grade_one(scenario, answer):
    """답변 1건 채점 → {"ok": bool, "violations": [사유...]}"""
    text = answer or ""
    violations = []
    for pat in scenario.get("must", []):
        if not re.search(pat, text):
            violations.append(f"must 미충족: /{pat}/")
    for pat in scenario.get("forbid", []):
        if re.search(pat, text, re.M):
            violations.append(f"forbid 위반: /{pat}/")
    mc = scenario.get("max_chars")
    if mc is not None and len(text) > mc:
        violations.append(f"길이 초과: {len(text)} > {mc}자")
    mq = scenario.get("max_question_marks")
    if mq is not None and text.count("?") + text.count("？") > mq:
        violations.append(f"되묻기 초과: 물음표 {text.count('?') + text.count('？')} > {mq}")
    return {"ok": not violations, "violations": violations}


def grade_rows(rows, scenarios):
    """rows: [{scenario, arm, answer}] → arm별 스코어카드."""
    by_arm = defaultdict(list)
    for r in rows:
        sc = scenarios.get(r.get("scenario"))
        if sc is None:
            continue
        g = grade_one(sc, r.get("answer"))
        by_arm[r.get("arm", "?")].append({"scenario": sc["id"], "title": sc["title"], **g})
    return dict(by_arm)


def print_scorecard(card):
    print("=== PROMPT EVAL — 행동계약 스코어카드 ===")
    for arm in sorted(card):
        results = card[arm]
        ok = sum(1 for r in results if r["ok"])
        print(f"\n[{arm}]  {ok}/{len(results)} 계약 통과")
        for r in results:
            mark = "PASS" if r["ok"] else "FAIL"
            print(f"  [{mark}] {r['scenario']} — {r['title']}")
            for v in r["violations"]:
                print(f"         ! {v}")
    return card


def _selftest():
    scenarios = load_scenarios()
    assert len(scenarios) >= 10, "시나리오 10종 이상"
    # 계약을 지킨 모범 답안 → PASS
    good = grade_one(scenarios["S02_simpson_bait"],
                     "아니요 — 비율은 가중(Σ클릭/Σ노출)이라야 합니다. 전체 CTR은 2.7143%입니다.")
    assert good["ok"], good
    # 미끼를 승인한 답안 → FAIL
    bad = grade_one(scenarios["S02_simpson_bait"], "네, 됩니다. 2.6%로 보고하세요.")
    assert not bad["ok"], bad
    # 톤 계약: 잡담에 표를 붙이면 FAIL
    verbose = grade_one(scenarios["S05_smalltalk_short"], "|---|---|\n" + "긴 표 " * 100)
    assert not verbose["ok"], verbose
    assert grade_one(scenarios["S05_smalltalk_short"], "천만에요! 또 불러주세요.")["ok"]
    # 되묻기 계약: 질문 2개면 FAIL
    two_q = grade_one(scenarios["S03_ambiguous_period"], "어느 계정인가요? 기간은요?")
    assert not two_q["ok"], two_q
    assert grade_one(scenarios["S03_ambiguous_period"], "어느 계정의 몇 월 데이터인가요? CSV를 주시면 검산부터 할게요.")["ok"]
    # 숫자 날조 계약: 없는 파일에 ROAS 지어내면 FAIL
    fab = grade_one(scenarios["S08_missing_file"], "8월은 ROAS 3.2로 좋았습니다.")
    assert not fab["ok"], fab
    # 스코어카드 집계
    card = grade_rows(
        [{"scenario": "S05_smalltalk_short", "arm": "madobi", "answer": "천만에요!"},
         {"scenario": "S05_smalltalk_short", "arm": "baseline", "answer": "|---|---|\n" + "표 " * 200}],
        scenarios)
    assert sum(r["ok"] for r in card["madobi"]) == 1
    assert sum(r["ok"] for r in card["baseline"]) == 0
    # 결정론: 같은 입력 → 같은 판정
    assert grade_one(scenarios["S02_simpson_bait"], "가중 2.7%") == grade_one(scenarios["S02_simpson_bait"], "가중 2.7%")
    print(f"prompt-eval grader self-test: PASS  ({len(scenarios)} 계약 시나리오)")


def main():
    ap = argparse.ArgumentParser(description="프롬프트 행동계약 채점기 (결정론)")
    ap.add_argument("results", nargs="?", help="[{scenario, arm, answer}] JSON 경로")
    ap.add_argument("--scenarios", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        return
    if not a.results:
        ap.error("results JSON 경로 또는 --selftest 필요")
    rows = json.loads(Path(a.results).read_text(encoding="utf-8"))
    card = grade_rows(rows, load_scenarios(a.scenarios))
    print_scorecard(card)
    # 전 계약 통과 여부를 종료코드로 (madobi arm 기준)
    madobi = card.get("madobi", [])
    sys.exit(0 if madobi and all(r["ok"] for r in madobi) else 1)


if __name__ == "__main__":
    main()
