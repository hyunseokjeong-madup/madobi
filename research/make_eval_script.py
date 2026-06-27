"""
Emit a self-contained swarm-eval Workflow JS file.
Embeds designs + problems + trial count directly (args transmission is unreliable),
so the workflow needs no external input.

Usage:
  python make_eval_script.py --designs results/seeds.json --pids all --trials 3 \
      --name eval-seeds --out results/eval_seeds.js
  python make_eval_script.py --designs results/pop.json --shard 0 --nshards 5 \
      --pids P2,P3,P6,P7,P8,P16,P17,P19 --trials 1 --name screen-s0 --out results/screen_s0.js
"""
import json, argparse
from pathlib import Path

ROOT = Path(__file__).parent

TEMPLATE = r'''export const meta = {
  name: __NAME__,
  description: __DESC__,
  phases: [{ title: 'Evaluate', detail: 'closed-book reasoning nodes' }],
}
const ANSWER_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: { answer: { type: 'string', description: 'ONLY the final answer in the exact required format (integer, reduced fraction a/b, or one short word/letter)' } },
  required: ['answer'],
}
const DESIGNS = __DESIGNS__;
const PROBLEMS = __PROBLEMS__;
const TRIALS = __TRIALS__;
phase('Evaluate')
const tasks = []
for (const d of DESIGNS) {
  for (const p of PROBLEMS) {
    for (let t = 0; t < TRIALS; t++) {
      tasks.push(() =>
        agent(
          'You are taking a CLOSED-BOOK reasoning exam.\n' +
          'STRICT RULES: do NOT use any tools, do NOT execute code, do NOT call Bash or python or any calculator. Reason entirely on your own.\n\n' +
          '=== OPERATING MANUAL (follow it exactly) ===\n' + d.manual + '\n\n' +
          '=== PROBLEM (' + p.pid + ') ===\n' + p.prompt + '\n\n' +
          '=== REQUIRED OUTPUT FORMAT ===\n' + p.format + '\n\n' +
          'Think carefully step by step in your reasoning. Then output ONLY the final answer in exactly the required format.',
          { label: d.name + ':' + p.pid + (TRIALS > 1 ? ':' + t : ''), phase: 'Evaluate', schema: ANSWER_SCHEMA }
        ).then(r => ({ design: d.name, pid: p.pid, trial: t, answer: r ? r.answer : null }))
      )
    }
  }
}
const rows = await parallel(tasks)
log('collected ' + rows.filter(Boolean).length + ' / ' + tasks.length + ' answers')
return rows.filter(Boolean)
'''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--designs", required=True)
    ap.add_argument("--problems", default=str(ROOT/"benchmark"/"problems.json"))
    ap.add_argument("--pids", default="all")
    ap.add_argument("--trials", type=int, default=1)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--name", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    designs = json.loads(Path(a.designs).read_text(encoding="utf-8"))
    # shard the design list across parallel teams
    if a.nshards > 1:
        designs = [d for i, d in enumerate(designs) if i % a.nshards == a.shard]
    problems = json.loads(Path(a.problems).read_text(encoding="utf-8"))
    problems = [{"pid": p["id"], "prompt": p["prompt"], "format": p["format"]} for p in problems]
    if a.pids != "all":
        keep = set(a.pids.split(","))
        problems = [p for p in problems if p["pid"] in keep]

    # Emit data as BACKTICK template literals with RAW characters (real newlines, raw unicode).
    # The permission hook rejects \n / \uXXXX escape sequences (treats them as hidden control chars),
    # but accepts raw chars inside backticks (verified: swarm_eval.js passed this way).
    def bt(s):
        s = str(s).replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        return "`" + s + "`"
    designs_js = "[\n" + ",\n".join(
        "  { name: %s, manual: %s }" % (bt(d["name"]), bt(d["manual"])) for d in designs) + "\n]"
    problems_js = "[\n" + ",\n".join(
        "  { pid: %s, prompt: %s, format: %s }" % (bt(p["pid"]), bt(p["prompt"]), bt(p["format"]))
        for p in problems) + "\n]"
    js = (TEMPLATE
          .replace("__NAME__", bt(a.name))
          .replace("__DESC__", bt(f"swarm eval: {len(designs)} designs x {len(problems)} problems x {a.trials} trials"))
          .replace("__DESIGNS__", designs_js)
          .replace("__PROBLEMS__", problems_js)
          .replace("__TRIALS__", str(a.trials)))
    Path(a.out).write_text(js, encoding="utf-8", newline="\n")  # LF only: Windows text-mode \r\n trips the permission hook
    print(f"wrote {a.out}: {len(designs)} designs x {len(problems)} problems x {a.trials} trials "
          f"= {len(designs)*len(problems)*a.trials} nodes")

if __name__ == "__main__":
    main()
