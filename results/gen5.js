export const meta = {
  name: `gen5-marketing`,
  description: `swarm eval: 2 designs x 10 problems x 3 trials`,
  phases: [{ title: 'Evaluate', detail: 'closed-book reasoning nodes' }],
}
const ANSWER_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: { answer: { type: 'string', description: 'ONLY the final answer in the exact required format (integer, reduced fraction a/b, or one short word/letter)' } },
  required: ['answer'],
}
const DESIGNS = [
  { name: `F03_adversarial_c`, manual: `Roleplay two adversaries on your draft answer.
1. Solve once to get a DRAFT.
2. PROSECUTOR: argue the draft is wrong. Cite the most damaging concrete flaw — a specific miscount, an arithmetic line, a misread constraint, a boundary case. Be ruthless; find the strongest objection, not a weak one.
3. DEFENDER: respond to the prosecutor's exact charge by re-deriving that piece independently (different method if possible).
4. JUDGE: if defender's independent re-derivation disagrees with the draft, the draft loses — adopt the corrected value. If they agree, draft survives.
5. Repeat the debate once on the surviving answer only if the first round changed anything.
6. Re-read the output contract; emit exactly that token.` },
  { name: `C0_baseline`, manual: `No operating manual. Solve the problem directly and give the final answer in the required format.` }
];
const PROBLEMS = [
  { pid: `M1`, prompt: `광고비 1,800,000원, 클릭 3,600회일 때 CPC(클릭당 비용, 원)는?`, format: `정수(원)` },
  { pid: `M2`, prompt: `광고비 1,800,000원, 노출 120,000회일 때 CPM(1000노출당 비용, 원)은?`, format: `정수(원)` },
  { pid: `M3`, prompt: `매출 5,400,000원, 광고비 1,800,000원일 때 ROAS(배수)는? 소수 첫째자리.`, format: `소수 한자리 (예: 2.5)` },
  { pid: `M4`, prompt: `전환 180건, 광고비 1,800,000원일 때 CPA(전환당 비용, 원)는?`, format: `정수(원)` },
  { pid: `M5`, prompt: `캠페인 A: 노출 100,000 클릭 2,000. 캠페인 B: 노출 300,000 클릭 3,000. 두 캠페인을 합친 '가중' CTR(%)은? 소수 둘째자리. (단순평균 금지)`, format: `퍼센트 소수 둘째자리 (예: 1.25)` },
  { pid: `M6`, prompt: `총예산 30,000,000원, 하루 광고비 1,500,000원으로 일정할 때 예산 소진까지 며칠 걸리나?`, format: `정수(일)` },
  { pid: `M7`, prompt: `목표 CPA가 8,000원이고 전환율(CVR)이 4%일 때, 허용 가능한 최대 CPC(원)는?`, format: `정수(원)` },
  { pid: `M8`, prompt: `채널별 광고비가 1,200,000 / 900,000 / 1,250,000 / 150,000원이다. 보고서 총합은 3,600,000원으로 적혀있다. 실제 합계와의 차이(원)는?`, format: `정수(원, 차이의 절대값)` },
  { pid: `M9`, prompt: `매출 5,400,000원, 광고비 1,800,000원일 때 ROI(%)는? (ROI=(매출-비용)/비용)`, format: `정수(%)` },
  { pid: `M10`, prompt: `총노출 600,000회, 도달(reach) 150,000명일 때 평균 빈도(frequency)는?`, format: `정수` }
];
const TRIALS = 3;
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
