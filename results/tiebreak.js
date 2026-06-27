export const meta = {
  name: `tiebreak`,
  description: `swarm eval: 4 designs x 6 problems x 5 trials`,
  phases: [{ title: 'Evaluate', detail: 'closed-book reasoning nodes' }],
}
const ANSWER_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: { answer: { type: 'string', description: 'ONLY the final answer in the exact required format (integer, reduced fraction a/b, or one short word/letter)' } },
  required: ['answer'],
}
const DESIGNS = [
  { name: `F02_verify_smallcase`, manual: `1. Solve the general problem to get a formula or answer A.
2. INDEPENDENTLY brute-force the smallest 2-3 instances (n=1,2,3) by hand-enumeration — list outcomes, do not use formula A.
3. Plug those n into formula A; the outputs MUST match the enumerated values.
4. If any mismatch: the formula is wrong (off-by-one, wrong base case, mis-set bound). Fix and re-test all small cases.
5. Also sanity-check monotonicity/limits (does it grow the right way? boundary n=0?).
6. Apply the validated formula to the actual input. Compute carefully: digit-by-digit, group long sums in 5s.
7. Re-read the output contract and emit exactly that token (integer / reduced fraction / single word).` },
  { name: `F02_verify_dual_track`, manual: `1. Set up TWO independent solution tracks before computing: e.g. enumeration vs formula, or forward vs backward, or units/dimensional reasoning vs direct.
2. Break the problem into 2-3 checkpoints. At each checkpoint, compute the intermediate quantity on BOTH tracks and confirm they match before proceeding. Early divergence localizes the error fast.
3. If tracks differ at a checkpoint, resolve it there (recompute the suspect step slowly) before moving on.
4. Keep arithmetic clean: digit-by-digit, group long additions in 5s, recheck each group.
5. For probability/fractions, carry numerator and denominator separately; reduce by GCD at the end; confirm the required format.
6. Pre-flag the classic trap relevant here (exactly/at-least, inclusive bounds, distinct/identical) and ensure both tracks honor the same interpretation.
7. When both tracks finish in agreement, emit EXACTLY the requested output format.` },
  { name: `F03_adversarial_c`, manual: `Roleplay two adversaries on your draft answer.
1. Solve once to get a DRAFT.
2. PROSECUTOR: argue the draft is wrong. Cite the most damaging concrete flaw — a specific miscount, an arithmetic line, a misread constraint, a boundary case. Be ruthless; find the strongest objection, not a weak one.
3. DEFENDER: respond to the prosecutor's exact charge by re-deriving that piece independently (different method if possible).
4. JUDGE: if defender's independent re-derivation disagrees with the draft, the draft loses — adopt the corrected value. If they agree, draft survives.
5. Repeat the debate once on the surviving answer only if the first round changed anything.
6. Re-read the output contract; emit exactly that token.` },
  { name: `C2_selfverify`, manual: `# Decompose + Independent Self-Verification
Phase A: restate, list constraints, decompose, produce a candidate answer.
Phase B (mandatory, DIFFERENT method): re-derive by an independent route (complementary count, plug back into constraints, different formula, small base case). If methods disagree, find the error and redo. Check sign/magnitude/units/format. Commit only when an independent check agrees.` }
];
const PROBLEMS = [
  { pid: `P1`, prompt: `5000 미만의 소수(prime) 중에서 7로 나눈 나머지가 3인 것들을 모두 더한 값은?`, format: `정수 하나만 출력` },
  { pid: `P4`, prompt: `함수 f(n)은 n이 짝수면 n/2, 홀수면 3n+1 이다. 어떤 양의 정수 n에서 시작해 f를 반복 적용하여 1에 도달할 때까지의 적용 횟수를 steps(n)이라 하자(steps(1)=0). n=1부터 200까지의 steps(n)을 모두 더한 값은?`, format: `정수 하나만 출력` },
  { pid: `P11`, prompt: `1부터 100000까지의 정수 중에서 30과 서로소(coprime, 최대공약수가 1)인 정수의 개수는?`, format: `정수 하나만 출력` },
  { pid: `P14`, prompt: `2의 200제곱(2^200)을 10진수로 적었을 때, 모든 자릿수의 숫자를 더한 값은?`, format: `정수 하나만 출력` },
  { pid: `P18`, prompt: `두 문자열 'intention'과 'execution' 사이의 최소 편집 거리(Levenshtein distance; 한 글자 삽입/삭제/교체를 1로 센다)를 구하라.`, format: `정수 하나만 출력` },
  { pid: `P19`, prompt: `1원, 5원, 10원, 25원 동전을 사용해 100원을 만드는 서로 다른 방법(동전 개수 제한 없음, 순서 무관)의 가짓수는?`, format: `정수 하나만 출력` }
];
const TRIALS = 5;
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
