// Static swarm-eval workflow. All data comes via `args` (keeps script small + ASCII).
// args = { designs:[{name,manual}], problems:[{pid,prompt,format}], trials:int }
export const meta = {
  name: 'swarm-eval-args',
  description: 'Closed-book swarm evaluation; designs/problems supplied via args',
  phases: [{ title: 'Evaluate', detail: 'design x problem x trial reasoning nodes' }],
}
const ANSWER_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: { answer: { type: 'string', description: 'ONLY the final answer in the exact required format (integer, reduced fraction a/b, or one short word/letter)' } },
  required: ['answer'],
}
const designs = (args && args.designs) || []
const problems = (args && args.problems) || []
const trials = (args && args.trials) || 1
log('eval: ' + designs.length + ' designs x ' + problems.length + ' problems x ' + trials + ' trials = ' + (designs.length*problems.length*trials) + ' nodes')
phase('Evaluate')
const tasks = []
for (const d of designs) {
  for (const p of problems) {
    for (let t = 0; t < trials; t++) {
      tasks.push(() =>
        agent(
          'You are taking a CLOSED-BOOK reasoning exam.\n' +
          'STRICT RULES: do NOT use any tools, do NOT execute code, do NOT call Bash or python or any calculator. Reason entirely on your own.\n\n' +
          '=== OPERATING MANUAL (follow it exactly) ===\n' + d.manual + '\n\n' +
          '=== PROBLEM (' + p.pid + ') ===\n' + p.prompt + '\n\n' +
          '=== REQUIRED OUTPUT FORMAT ===\n' + p.format + '\n\n' +
          'Think carefully step by step in your reasoning. Then output ONLY the final answer in exactly the required format.',
          { label: d.name + ':' + p.pid + (trials > 1 ? ':' + t : ''), phase: 'Evaluate', schema: ANSWER_SCHEMA }
        ).then(r => ({ design: d.name, pid: p.pid, trial: t, answer: r ? r.answer : null }))
      )
    }
  }
}
const rows = await parallel(tasks)
log('collected ' + rows.filter(Boolean).length + ' / ' + tasks.length)
return rows.filter(Boolean)
