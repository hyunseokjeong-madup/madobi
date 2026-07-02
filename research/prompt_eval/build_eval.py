"""
프롬프트 평가 워크플로 생성기 — 서비스 프롬프트(madobi 에이전트+스킬)를 행동계약으로 실측.

make_eval_script.py 와 같은 규약(백틱 리터럴·LF 전용·자기완결 JS)으로, 두 arm 을 비교한다:
  - madobi   : .claude/agents/madobi.md + skills/marketing-analyst/SKILL.md 전문을 운영 매뉴얼로 주입
  - baseline : 매뉴얼 없는 일반 어시스턴트 (프롬프트의 부가가치를 증명하는 대조군)

각 노드는 리포 안에서 실제 도구(Bash/python)를 쓸 수 있다 — 계약 중 일부(검산 총계 수치)는
도구를 실행해야만 알 수 있어, '검산을 실제로 돌렸는가'의 결정론적 증거가 된다.

Usage:
  python research/prompt_eval/build_eval.py --out research/prompt_eval/eval.js
  # → Claude Code Workflow 도구로 eval.js 실행 → 결과 JSON 저장 → grade.py 로 채점
"""
import json
import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

BASELINE_MANUAL = (
    "You are a helpful marketing data assistant working inside this repository. "
    "Answer the user's message in Korean. You may run repo tools via Bash if useful."
)

TEMPLATE = r'''export const meta = {
  name: __NAME__,
  description: __DESC__,
  phases: [{ title: 'Evaluate', detail: 'behavior-contract scenarios x 2 arms' }],
}
const ANSWER_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: { answer: { type: 'string', description: 'The exact reply you would give the user, in Korean. Nothing else.' } },
  required: ['answer'],
}
const ARMS = __ARMS__;
const SCENARIOS = __SCENARIOS__;
phase('Evaluate')
const tasks = []
for (const arm of ARMS) {
  for (const s of SCENARIOS) {
    tasks.push(() =>
      agent(
        'You are role-playing a marketing analyst chatbot operating INSIDE the repo at __ROOT__ (cwd).\n' +
        'You MAY run the repo tools via Bash (e.g. python marketing/reconcile.py <csv>) when your manual tells you to, and you should when numbers are involved.\n' +
        'Do NOT modify any files. Reply in Korean.\n\n' +
        '=== OPERATING MANUAL (follow it exactly; this IS your system prompt) ===\n' + arm.manual + '\n\n' +
        '=== USER MESSAGE ===\n' + s.prompt + '\n\n' +
        'Return via StructuredOutput ONLY the reply you would send the user (the chat answer itself, not a description of it).',
        { label: arm.name + ':' + s.id, phase: 'Evaluate', schema: ANSWER_SCHEMA }
      ).then(r => ({ arm: arm.name, scenario: s.id, answer: r ? r.answer : null }))
    )
  }
}
const rows = await parallel(tasks)
log('collected ' + rows.filter(Boolean).length + ' / ' + tasks.length + ' answers')
return rows.filter(Boolean)
'''


def bt(s):
    """백틱 템플릿 리터럴 이스케이프 — make_eval_script.py 와 동일 규약(원시 개행/유니코드 허용)."""
    s = str(s).replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    return "`" + s + "`"


def strip_frontmatter(text):
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].lstrip()
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "eval.js"))
    ap.add_argument("--scenarios", default=str(HERE / "scenarios.json"))
    ap.add_argument("--ids", default="all", help="쉼표구분 시나리오 id 필터 (재측정용)")
    a = ap.parse_args()

    agent_md = strip_frontmatter((ROOT / ".claude" / "agents" / "madobi.md").read_text(encoding="utf-8"))
    skill_md = strip_frontmatter(
        (ROOT / ".claude" / "skills" / "marketing-analyst" / "SKILL.md").read_text(encoding="utf-8"))
    madobi_manual = agent_md + "\n\n--- 스킬 (실행 절차) ---\n\n" + skill_md

    scenarios = json.loads(Path(a.scenarios).read_text(encoding="utf-8"))
    if a.ids != "all":
        keep = set(a.ids.split(","))
        scenarios = [s for s in scenarios if s["id"] in keep]

    arms_js = "[\n" + ",\n".join(
        "  { name: %s, manual: %s }" % (bt(n), bt(m))
        for n, m in (("madobi", madobi_manual), ("baseline", BASELINE_MANUAL))) + "\n]"
    scen_js = "[\n" + ",\n".join(
        "  { id: %s, prompt: %s }" % (bt(s["id"]), bt(s["prompt"])) for s in scenarios) + "\n]"

    js = (TEMPLATE
          .replace("__NAME__", bt("prompt-eval"))
          .replace("__DESC__", bt(f"prompt behavior-contract eval: 2 arms x {len(scenarios)} scenarios"))
          .replace("__ROOT__", str(ROOT))
          .replace("__ARMS__", arms_js)
          .replace("__SCENARIOS__", scen_js))
    Path(a.out).write_text(js, encoding="utf-8", newline="\n")  # LF only
    print(f"wrote {a.out}: 2 arms x {len(scenarios)} scenarios = {2 * len(scenarios)} nodes")


if __name__ == "__main__":
    main()
