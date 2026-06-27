export const meta = {
  name: `screen-s3`,
  description: `swarm eval: 22 designs x 10 problems x 1 trials`,
  phases: [{ title: 'Evaluate', detail: 'closed-book reasoning nodes' }],
}
const ANSWER_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: { answer: { type: 'string', description: 'ONLY the final answer in the exact required format (integer, reduced fraction a/b, or one short word/letter)' } },
  required: ['answer'],
}
const DESIGNS = [
  { name: `F01_decomp_d`, manual: `1. PLAN phase (no arithmetic yet): list the exact sequence of operations needed and the final format. Freeze this plan.
2. EXECUTE phase: perform one planned block at a time. Within a block, show intermediate digits/terms.
3. Sums: chunk into fives, subtotal, then total. Products: digit-by-digit with aligned place value.
4. After finishing a block, VERIFY it alone — recompute by reverse operation (subtract back, divide back). Fix before proceeding.
5. Watch traps flagged in the plan: 'exactly' vs 'at least', whole-word vs substring, distinct vs identical.
6. For fractions: separate numerator/denominator counts, reduce by GCD, confirm reduced form.
7. Re-read required format; output only that.` },
  { name: `F02_verify_two_method`, manual: `1. Read the question twice; note the exact output format and one trap (exactly vs at-least, distinct vs identical, inclusive bounds, reduced fraction).
2. METHOD A: solve directly. Show key steps. State the answer.
3. METHOD B: re-derive using a genuinely DIFFERENT route (e.g. complementary counting vs direct; algebra vs enumeration; closed form vs small-case sum). Do NOT reuse Method A's intermediate numbers.
4. Compare the two answers.
5. If they DISAGREE: find the specific error (recompute the suspicious step), pick a third method if needed, repeat until two methods agree.
6. Computation hygiene: for long sums add in groups of 5, carry digit-by-digit, recheck each chunk.
7. Emit EXACTLY the required format: integer only, or reduced a/b (divide by GCD), or one lowercase word. Nothing else.` },
  { name: `F02_verify_refute`, manual: `1. Solve the problem; record answer A with its key steps.
2. ADVERSARIAL PASS: assume A is wrong. Attack it: test edge/boundary cases, re-check every trap (inclusive vs exclusive bounds, exactly vs at-least, strictly increasing, whole-word vs substring, reduced fraction required), and recompute the single riskiest arithmetic step independently.
3. If the attack exposes a flaw, fix it and re-attack the new answer.
4. CONFIRM by a second independent method (different route, not reusing A's numbers); it must agree.
5. Arithmetic hygiene: long sums in groups of 5, verify each group; carry digits explicitly.
6. Only when the answer survives refutation AND a second method, output it in EXACTLY the required format.` },
  { name: `F03_adversarial_c`, manual: `Roleplay two adversaries on your draft answer.
1. Solve once to get a DRAFT.
2. PROSECUTOR: argue the draft is wrong. Cite the most damaging concrete flaw — a specific miscount, an arithmetic line, a misread constraint, a boundary case. Be ruthless; find the strongest objection, not a weak one.
3. DEFENDER: respond to the prosecutor's exact charge by re-deriving that piece independently (different method if possible).
4. JUDGE: if defender's independent re-derivation disagrees with the draft, the draft loses — adopt the corrected value. If they agree, draft survives.
5. Repeat the debate once on the surviving answer only if the first round changed anything.
6. Re-read the output contract; emit exactly that token.` },
  { name: `F03_adversarial_h`, manual: `1. Solve, but write each assumption/step on its own numbered line.
2. DEVIL'S ADVOCATE: go line by line and challenge each: 'What if this is wrong?' Mark the riskiest 1-2 lines (usually a count, a boundary, or an arithmetic result).
3. Re-derive only the marked lines independently. For arithmetic, redo digit-by-digit; for counts, enumerate a small slice explicitly.
4. Specifically interrogate classic traps present: base-rate (build a 2x2 Bayes table), exactly-vs-at-least, distinct-vs-identical, substring-vs-word, fraction-must-be-reduced.
5. Propagate any correction through later lines and recompute the final value.
6. Confirm the output format requirement and return precisely that token, no commentary.` },
  { name: `F04_trapcheck_e`, manual: `1. List the traps that could plausibly apply here (base-rate, exactly/at-least, whole-word, strict-increase, distinct, reduced-fraction, inclusive bounds) and rate each High/Low risk for THIS problem.
2. For every High-risk trap, write the precise correct interpretation and the wrong one you are avoiding.
3. Solve using the correct interpretations. Keep arithmetic clean: heavy sums in chunks of 5 with running totals; fractions as separate numerator/denominator then GCD-reduced.
4. Self-refute: pick your most likely mistake and argue against your own answer for one sentence; fix if the attack lands.
5. Quick second method on the High-risk quantity only (keep it short so easy problems aren't over-thought). If two methods agree, commit.
6. Re-read the required output format and emit exactly it - integer only, reduced a/b, or one lowercase word.` },
  { name: `F05_constraint_mrv_branch`, manual: `Solve as a CSP with smart ordering.
1. Enumerate variables and full domains. Write all constraints, including hidden ones implied by wording (flag 'whole word vs substring', reduced-fraction-required, etc.).
2. Apply unary constraints to shrink each domain immediately.
3. Repeat: assign the variable with the FEWEST legal values left (MRV). After each assignment, remove now-illegal values from neighbors (forward-checking). If any domain empties, backtrack that choice.
4. Keep a running assignment table so state is always visible; never hold it only in your head.
5. When all variables are assigned, you have one solution. For counting, continue exhausting the branch tree systematically; tally in chunks of 5 and re-add.
6. Independent verify: re-derive the same answer by scanning constraints in a DIFFERENT variable order; the two must agree.
7. Emit the answer in the exact required format.` },
  { name: `F05_constraint_pencilmark_domains`, manual: `Pencil-mark candidate elimination (Sudoku-style).
1. For every cell/variable, write the full set of candidate values it could take given unary constraints.
2. Elimination pass: for each constraint, delete candidates it forbids from the relevant cells. A cell reduced to one candidate is solved — propagate that value, removing it from peers.
3. Hidden singles: if within a constraint-group a value can go in only one cell, place it there.
4. Loop passes 2-3 until no candidate changes (a fixpoint).
5. If unsolved, take the cell with two candidates, assume one, continue elimination; on contradiction, the other is forced.
6. Keep the candidate grid written down at every step; never track mentally.
7. Verify: every constraint satisfied, every cell filled legally — recheck independently. Output precisely the format requested, nothing extra.` },
  { name: `F06_comphygiene_d`, manual: `COMPUTATION HYGIENE — ITERATION TABLE.
For sequences, recurrences, Collatz-style or simulation problems:
1. Define the state variables and the stopping condition explicitly.
2. Build a table: one ROW per iteration, columns for step index, current value, and the operation applied. Fill rows one at a time; never skip or batch steps.
3. After every 5 rows, pause and re-read the last value to confirm continuity (output of row n = input of row n+1).
4. If accumulating a sum, keep a separate running-total column and add the new term explicitly each row.
5. Verify the step count matches the stopping condition exactly (off-by-one guard: is the final value included?).
6. Sanity-bound the result against a rough expectation.
7. Re-read the output contract and emit exactly the required value (final term? count of steps? sum?).
Untabulated iteration is the #1 error source — always tabulate.` },
  { name: `F07_estimate_a`, manual: `1) Before any computation, write a crude LOWER and UPPER bound for the answer using rounding or limiting cases (e.g. round terms, ignore small corrections). State the interval [L,U].
2) Now compute the exact answer carefully. For heavy sums/iterations, chunk into groups of 5, keep running partial totals, and re-add each group twice.
3) Check the exact value lies in [L,U]. If it escapes, you made an arithmetic or setup error: recompute the offending chunk, not the whole thing.
4) Flag traps before finalizing: 'exactly' vs 'at least', inclusive/exclusive bounds, distinct vs identical, reduced fraction required.
5) Re-read the required output format and emit EXACTLY it (integer only / reduced a/b / one lowercase word). Nothing else.` },
  { name: `F07_estimate_f`, manual: `1) Replace every messy number with the nearest round number and compute a PROXY answer instantly. Write it down as the target ballpark.
2) Predict whether the true answer is slightly above or below the proxy (based on how you rounded).
3) Compute the exact answer. For iterative processes (sequences, repeated steps) record state every 5 steps and verify the running total there.
4) Compare exact vs proxy: the difference must be small and in the predicted direction. A large or wrong-direction gap = error; locate it.
5) Quick adversarial pass: did I confuse substring/whole-word, inclusive/exclusive, exactly/at-least?
6) Output exactly the demanded format.` },
  { name: `F08_reduce_c`, manual: `Reduce counting problems to inclusion-exclusion or complementary counting:
1. Decide: is it easier to count the wanted set directly or its complement (total minus bad)? Pick the smaller.
2. State the universe size precisely. Flag distinct-vs-identical objects and ordered-vs-unordered selection BEFORE counting.
3. For overlapping conditions use |A∪B∪C| = Σ|A| - Σ|A∩B| + |A∩B∩C|. Write every term with its sign.
4. Compute each term; for products/factorials, expand step by step, not in one leap.
5. Add the signed terms in groups, re-adding to confirm.
6. Cross-check with a tiny instance (n=2 or 3) computed by brute enumeration; ensure the formula reproduces it.
7. Re-read 'exactly' vs 'at least' and adjust. Output exactly the requested format.` },
  { name: `F08_reduce_h`, manual: `For 'expected value', 'average', or aggregate-count problems, reduce via linearity or generating functions:
1. Express the target as a SUM of simple indicators or per-item contributions: Total = Σ X_i.
2. Compute E[X_i] or the count for ONE generic item using a standard sub-formula (probability, binomial coefficient).
3. Multiply by the number of items / sum over i. Linearity holds even when items are dependent—state this to avoid an independence trap.
4. For combinatorial coefficient extraction, set up the generating function and identify the needed coefficient term.
5. Carry out arithmetic in small chunks, recording partial sums in groups of 5.
6. Verify by computing a small case exhaustively and matching.
7. If a fraction, reduce by GCD and confirm format; emit exactly the requested output.` },
  { name: `F09_firstprin_e`, manual: `Pattern-matching fails when a formula's hypotheses don't hold. 1) For each formula/theorem you're tempted to use, WRITE its exact statement AND its preconditions. 2) VERIFY each precondition holds in this problem by checking the definitions (independence? mutually exclusive? distinct items? with/without replacement?). If any fails, derive the correct expression from first principles instead. 3) Re-derive Bayes for base-rate problems via a concrete frequency table (imagine 10,000 cases) rather than recalling the formula. 4) DERIVE the answer; justify each transition by a checked definition. 5) ARITHMETIC: chunk long sums into 5s, add digit-by-digit, keep written running totals. 6) VERIFY by a structurally different derivation; reconcile any mismatch. 7) Probability/fraction: numerator and denominator separately, reduce by GCD. 8) Output exactly the required format (integer / a/b / one lowercase word).` },
  { name: `F10_dualprocess_b`, manual: `1. Record your gut answer as HYPOTHESIS in one line.
2. Become the prosecutor: actively try to PROVE the hypothesis wrong. List the top 2 ways a problem like this fools people (base-rate neglect, off-by-one, 'exactly' vs 'at least', counting identical-as-distinct).
3. Test the hypothesis against a small concrete case or boundary you can verify by hand.
4. If refutation succeeds, discard and recompute carefully; if it survives all attacks, accept.
5. Computation hygiene: do arithmetic digit-by-digit; re-add long sums in groups of 5; for probability count numerator and denominator separately, then divide by GCD.
6. State the final reduced/exact value, re-read the output contract, and emit exactly that format.` },
  { name: `F10_dualprocess_g`, manual: `1. Snap an intuitive answer and rate its reliability.
2. If the problem is short/clean AND confidence is high: do ONE quick independent check (plug back in, test a boundary). If it confirms, finalize — do not over-think.
3. If the problem is heavy (long sums, casework, multi-step) OR confidence is low: run a full second derivation by a different method and require agreement.
4. Always apply sum hygiene on heavy arithmetic: partial sums in groups of 5, then total the partials; digit-by-digit on big multiplications.
5. Trap flags scaled to problem type: probability→reduce by GCD and check 'exactly/at least'; counting→inclusive bounds, distinct vs identical; strings→whole word vs substring.
6. Output exactly the contracted format.` },
  { name: `F11_metacog_d`, manual: `1. Note the question and exact output format, flagging trap words.
2. Solve the problem three times INDEPENDENTLY, each time using a fresh approach or order; do not look at prior attempts while working.
3. For each attempt with heavy arithmetic, chunk sums in fives and re-add to avoid slips.
4. Compare the three answers. If all agree, that is your answer. If two agree, take the majority but re-examine the dissenter to confirm it was an error, not a missed subtlety.
5. If all three differ, you are likely missing an assumption: list assumptions, identify the divergence point, and solve a fourth time resolving it.
6. Before output, ask 'what single thing would make even the majority wrong?' and check it.
7. Emit EXACTLY the required format; reduce any fraction by GCD.` },
  { name: `F12_swarmteam_a`, manual: `Simulate a 4-person team in your head.
1. SOLVER-A (forward): solve directly, step by step. Use chunked partial sums (group additions in 5s, re-add) for any heavy arithmetic.
2. SOLVER-B (alternative): re-solve by a genuinely DIFFERENT method (work backward, complementary count, or algebra vs enumeration).
3. SOLVER-C (estimate/structural): get an independent answer via bounding, symmetry, or small-case pattern.
4. VERIFIER: list each answer; flag classic traps relevant here — 'exactly' vs 'at least', distinct vs identical, inclusive/exclusive bounds, substring vs whole-word, reduced-fraction-required. Plug each answer back into the problem's constraints.
5. SYNTHESIZER: take the value that >=2 solvers agree on. If all differ, re-run the cheapest method carefully and break the tie.
For probabilities/fractions, count numerator and denominator separately, reduce by GCD.
Re-read the required output format and emit EXACTLY it (integer only / reduced a/b / one lowercase word). Output only the final answer.` },
  { name: `F12_swarmteam_f`, manual: `Use a shared blackboard with three solvers, a verifier, a synthesizer.
1. Each solver posts an answer WITH its key steps and any assumption made. Strategies must differ: enumeration, closed-form, and reverse/working-backward.
2. For long sums/iterations, post partial sums in groups of five so the verifier can audit; re-add to confirm.
3. VERIFIER annotates the board: mark each step valid/suspect, recompute one risky arithmetic step independently, and tag the relevant classic trap (base-rate Bayes table, 'exactly' vs 'at least', distinct vs identical, reduced-fraction, inclusive/exclusive, whole-word vs substring).
4. SYNTHESIZER resolves: adopt the answer supported by clean steps AND majority; discard any answer with a verifier-confirmed error.
5. If consensus fails, isolate the disagreeing step, recompute it alone, propagate.
6. For probability: numerator and denominator counted separately, reduce by GCD, confirm format.
Re-read the output requirement and emit EXACTLY it. Final answer only.` },
  { name: `F13_formatdiscipline_c`, manual: `Optimized for probability and ratio answers.
1. Identify the contract: most likely 'reduced fraction a/b' or 'decimal' or 'integer'. Lock it.
2. Count the DENOMINATOR (total outcomes) independently; recount once.
3. Count the NUMERATOR (favorable) independently; pre-check 'exactly' vs 'at least' and distinct vs identical objects.
4. Form a/b. Compute gcd(a,b) by listing factors or Euclid; divide both. State the gcd you used.
5. Sanity: 0<=value<=1 for probability; if value=1 or 0, express as required (1/1 or 0/1 vs '1'/'0' per contract).
6. Cross-check by complement (1 minus opposite event) when feasible; must match.
7. Emit exactly the reduced fraction with a single slash, no spaces (e.g., 3/8). No '=', no words, no percent. If an integer is required instead, drop the denominator only when b=1.` },
  { name: `F13_formatdiscipline_h`, manual: `Goal: the answer line contains the answer and NOTHING else.
1. Solve the core problem; keep work in scratch, never in the final line.
2. Independent verification: re-derive once by a different route; if mismatch, resolve before proceeding. Keep this brief for simple problems.
3. Determine forbidden extras for this contract: prose, 'The answer is', units, %, $, commas in numbers, equals signs, quotation marks, trailing periods, leading zeros.
4. If fraction: reduce by gcd, single slash, no spaces. If integer: bare digits. If word: exact, lowercase by default.
5. Trap pass: exactly vs at least, distinct vs identical, strict vs non-strict, inclusive vs exclusive, whole-word vs substring.
6. Emit the minimal token. Then silently confirm the line has no forbidden extras. Do not restate the question or reasoning.` },
  { name: `F14_invariants_extreme_first`, manual: `1. Before general work, solve the EXTREMES: smallest input, largest, all-equal, all-distinct, empty/zero case.
2. Note which extremes give clean answers — they reveal the controlling structure or formula skeleton.
3. Form a hypothesis for the general case consistent with all extremes simultaneously.
4. Test the hypothesis on one mid-sized case via independent direct enumeration.
5. If they disagree, locate which extreme assumption broke and patch the formula.
6. Explicitly flag classic traps surfaced by extremes: boundary inclusivity, off-by-one, exactly-vs-at-least, substring-vs-whole-word, strictly-increasing.
7. For probability/fraction answers, compute numerator and denominator independently, reduce by GCD, confirm reduced form is required.
8. Re-add long sums in groups of 5; verify each digit.
State the final answer EXACTLY as specified (integer only / a/b reduced / one lowercase word).` }
];
const PROBLEMS = [
  { pid: `P1`, prompt: `5000 미만의 소수(prime) 중에서 7로 나눈 나머지가 3인 것들을 모두 더한 값은?`, format: `정수 하나만 출력` },
  { pid: `P4`, prompt: `함수 f(n)은 n이 짝수면 n/2, 홀수면 3n+1 이다. 어떤 양의 정수 n에서 시작해 f를 반복 적용하여 1에 도달할 때까지의 적용 횟수를 steps(n)이라 하자(steps(1)=0). n=1부터 200까지의 steps(n)을 모두 더한 값은?`, format: `정수 하나만 출력` },
  { pid: `P6`, prompt: `어떤 병의 유병률은 1000명 중 1명이다. 검사의 민감도(sensitivity)는 99%, 특이도(specificity)는 95%다. 무작위로 검사한 사람이 '양성'이 나왔을 때 실제로 그 병에 걸렸을 확률을 기약분수로 구하라.`, format: `기약분수 a/b 형식` },
  { pid: `P11`, prompt: `1부터 100000까지의 정수 중에서 30과 서로소(coprime, 최대공약수가 1)인 정수의 개수는?`, format: `정수 하나만 출력` },
  { pid: `P12`, prompt: `공정한 6면체 주사위 2개를 굴렸더니 눈의 합이 짝수였다. 이 조건에서 눈의 합이 8 이상일 조건부확률을 기약분수로 구하라.`, format: `기약분수 a/b 형식` },
  { pid: `P14`, prompt: `2의 200제곱(2^200)을 10진수로 적었을 때, 모든 자릿수의 숫자를 더한 값은?`, format: `정수 하나만 출력` },
  { pid: `P16`, prompt: `어떤 가정에 아이가 둘 있다. 각 아이가 남(B)/녀(G)일 확률은 동일하고 독립이다. '적어도 한 명은 남자아이'라는 사실이 주어졌을 때, 두 아이가 모두 남자아이일 조건부확률을 기약분수로 구하라.`, format: `기약분수 a/b 형식` },
  { pid: `P17`, prompt: `다음 수열에서 '엄격히 증가하는' 가장 긴 부분수열(연속일 필요 없음)의 길이를 구하라: 3,1,4,1,5,9,2,6,5,3,5,8,9,7,9,3,2,3,8,4,6,2,6`, format: `정수 하나만 출력` },
  { pid: `P19`, prompt: `1원, 5원, 10원, 25원 동전을 사용해 100원을 만드는 서로 다른 방법(동전 개수 제한 없음, 순서 무관)의 가짓수는?`, format: `정수 하나만 출력` },
  { pid: `P20`, prompt: `100! (100 팩토리얼)을 10진수로 적었을 때 끝에 연속으로 붙는 0의 개수는?`, format: `정수 하나만 출력` }
];
const TRIALS = 1;
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
