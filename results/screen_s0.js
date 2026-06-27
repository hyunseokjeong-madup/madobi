export const meta = {
  name: `screen-s0`,
  description: `swarm eval: 23 designs x 10 problems x 1 trials`,
  phases: [{ title: 'Evaluate', detail: 'closed-book reasoning nodes' }],
}
const ANSWER_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: { answer: { type: 'string', description: 'ONLY the final answer in the exact required format (integer, reduced fraction a/b, or one short word/letter)' } },
  required: ['answer'],
}
const DESIGNS = [
  { name: `F01_decomp_a`, manual: `1. Restate the goal in one line; copy the exact output format (integer / a/b / one word).
2. Split the problem into labeled subtasks S1..Sn. Solve each independently.
3. COMPUTATION HYGIENE for any sum/iteration: list terms in order, add in chunks of 5, write each chunk subtotal, then sum the subtotals. Never add a long list in one sweep.
4. For multiplications/large numbers, work digit-by-digit and keep place values aligned.
5. Re-add each chunk a second time; if a subtotal disagrees, redo that chunk only.
6. Pre-flag traps: 'exactly' vs 'at least', inclusive vs exclusive bounds, distinct vs identical, strictly-increasing, substring vs whole-word.
7. Recombine subtask results; state the running total.
8. Re-read the format and emit EXACTLY it, nothing else.` },
  { name: `F01_decomp_f`, manual: `1. State target and output contract.
2. Decompose into subtasks; solve each with careful arithmetic (chunked sums of 5; digit-by-digit products).
3. After each subresult, play ADVERSARY: 'How is this wrong?' Check off-by-one, miscount, dropped term, sign, wrong base case. Repair any flaw found.
4. Pre-attack classic traps: base-rate neglect (lay out a Bayes table), 'exactly' vs 'at least', substring vs whole-word, distinct vs identical, reduced-fraction-required.
5. Recombine; then attack the FINAL answer once more — does it satisfy every constraint and the exact wording?
6. For fractions, recount numerator and denominator independently, reduce by GCD.
7. Output strictly in the required format.` },
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
  { name: `F03_adversarial_e`, manual: `1. Solve to a candidate answer.
2. ADVERSARIAL PERTURBATION: test your method on tiny/edge versions of the SAME problem where you can verify the true answer by hand (n=1, n=2, empty set, smallest bound). If your method gives the wrong small-case answer, your method is flawed — fix it, then re-apply.
3. Flip every boundary word and recheck which the problem actually uses: inclusive/exclusive, <=/<, exactly/at least, distinct/repeatable.
4. Re-verify the heavy arithmetic by a second grouping (chunks of 5) to catch addition/multiplication slips.
5. If small-case and full computation are consistent, accept.
6. Output strictly in the demanded format, nothing extra.` },
  { name: `F04_trapcheck_b`, manual: `Step 1 - Classify: is this counting, probability, number theory, or string/logic? Step 2 - Load the matching traps:
- Counting: distinct vs identical objects, ordered vs unordered, off-by-one on inclusive ranges, overcounting symmetric cases.
- Probability: base-rate (use a Bayes count table), "exactly k" vs "at least k", with/without replacement, reduce the final fraction by GCD.
- Number theory: strict vs non-strict inequalities, primes excluding 1, divisor counting includes 1 and n.
- String/logic: whole-word vs substring, case sensitivity, inclusive bounds.
Step 3 - Solve, doing heavy sums in chunks of 5 with running subtotals (never one long mental addition). Step 4 - Verify the single trap most likely to bite here by re-deriving that piece differently. Step 5 - Output contract: re-read the exact format demanded and emit precisely that, nothing else.` },
  { name: `F04_trapcheck_g`, manual: `First, rewrite the problem in your own words with every ambiguity nailed down. As you rewrite, force a decision on each trap:
- Replace vague quantifiers with explicit 'exactly k' / 'at least k' / 'at most k'.
- State whether sequences must be STRICTLY increasing or allow equality.
- State whether elements are DISTINCT and whether order matters.
- State whether matching is WHOLE-WORD or substring.
- State inclusive/exclusive for every bound.
- Note if the answer must be a REDUCED fraction or plain integer or single word.
Solve the rewritten, unambiguous version. Manage arithmetic: chunk sums into groups of 5, track partial totals, work big multiplications digit-by-digit. For probability, build numerator and denominator separately and reduce by GCD. Verify by re-deriving via a complementary method. Emit only the answer, in the exact required format.` },
  { name: `F05_constraint_case_split_prune`, manual: `Disciplined case-splitting with early pruning.
1. State all constraints and the goal (find one solution / count all / find max).
2. Identify the single unknown that appears in the MOST constraints — splitting it prunes hardest. List its possible values as exhaustive, mutually-exclusive cases.
3. For each case: substitute, then propagate forced consequences. Kill the branch the instant any constraint is violated (adversarial check: actively try to break it).
4. Recurse on surviving branches, always splitting the most-constrained unknown next.
5. Maintain a tree sketch so no branch is dropped or double-counted.
6. Aggregate: for counting, sum leaf counts in groups of 5 and re-add; for optimization, compare leaf values.
7. Verify the winning leaf independently by plugging values back into ALL original constraints. Re-read and match the output contract exactly.` },
  { name: `F06_comphygiene_a`, manual: `COMPUTATION HYGIENE — TABULATE & CHUNK.
1. Restate what must be summed/counted. Note the output format NOW (integer / a-b / one word).
2. List every term explicitly in a vertical table with an index. Do not sum while listing.
3. Group terms into blocks of 5. Compute each block's subtotal separately, writing it down.
4. Add the block subtotals one at a time, keeping a running total. Re-add the block subtotals in reverse order; both passes must match.
5. Sanity-bound: estimate the answer's order of magnitude (count of terms × average term). Confirm your total lands inside that bound.
6. Re-read the format and emit EXACTLY it — integer only, no commas, no words.
If any check disagrees, find the offending block and recompute only it. Never trust a single-pass sum on more than 4 terms.` },
  { name: `F06_comphygiene_f`, manual: `COMPUTATION HYGIENE — BOUND-FIRST.
1. Before any exact work, ESTIMATE: compute a quick lower bound and upper bound for the answer (round terms, count items × typical size, use powers of ten). Write both bounds down.
2. Identify the output format.
3. Now compute exactly, using chunked partial sums in groups of 5 and explicit digit-by-digit carries for multi-digit steps.
4. Check the exact result falls strictly inside [lower, upper]. If it escapes the bound, your exact computation has an error OR your bound was wrong — recheck both, fix the real one.
5. Re-add any long sum in a different grouping to confirm.
6. Watch unit/scale traps (thousands vs millions, percent vs proportion).
7. Re-read the format; output exactly that.
The bound is your tripwire: a magnitude mismatch almost always signals a dropped digit, a place-value slip, or a miscounted term.` },
  { name: `F07_estimate_c`, manual: `1) Probe limiting cases to bound the answer: smallest possible value, largest possible value, and an 'average' guess. Record min, max.
2) For counting/probability, separately bound numerator and denominator (max count, min count).
3) Compute the exact answer. Keep partial sums in chunks of 5; never sum a long list in one pass.
4) Confirm exact value sits between min and max and is plausible vs the average guess.
5) Adversarially refute your own answer once: 'What single mistake would make this wrong?' Check that specific risk (off-by-one, double count, wrong base rate).
6) Reduce fractions, re-read the contract, emit exactly the required token.` },
  { name: `F07_estimate_h`, manual: `1) Spend two lines deriving the TIGHTEST easy bounds you can: a lower bound that's clearly too small and an upper bound clearly too big, each justified in one phrase.
2) Name the trap most likely here and pre-commit how you'll handle it (e.g. Bayes table for base-rate; count numerator and denominator separately for probability).
3) Compute exactly; for big additions, sum in blocks of 5 and write each block subtotal so errors are localizable.
4) Audit: does the exact value fall strictly inside your bounds? If borderline or outside, re-derive by a second method until two agree.
5) Reduce any fraction by GCD; confirm 'exactly' vs 'at least' was respected.
6) Re-read the output contract and print only the required token.` },
  { name: `F08_reduce_e`, manual: `For divisibility/coprime/remainder/cyclic problems, reduce to a number-theory tool:
1. Pick the tool: Euler totient φ(n) for coprime counts, CRT for simultaneous remainders, Fermat/Euler for large powers mod m, gcd/lcm for periods.
2. Factor the modulus/number into primes first; write the factorization explicitly.
3. Apply the formula on prime powers, then combine multiplicatively. e.g. φ(n)=n∏(1-1/p).
4. Do exponent reduction mod φ(m) before powering; reduce the base mod m early.
5. Compute step by step, keeping numbers small via repeated mod.
6. Verify on a tiny modulus by direct listing (e.g. count coprimes to 12 by hand) to confirm the method.
7. Confirm inclusive/exclusive range bounds. Output exactly as requested.` },
  { name: `F09_firstprin_b`, manual: `Treat the problem as if no formulas exist. 1) AXIOMS: state the most primitive facts (counting principle, definition of probability = favorable/total, definition of divisibility, etc.) relevant here. 2) FORBID SHORTCUTS: explicitly write 'I will NOT apply a memorized formula without deriving it.' If you recall one, derive it from the axioms in two lines and check it on a tiny case (n=1,2). 3) CONSTRUCT the answer by composing atomic operations only. 4) ARITHMETIC HYGIENE: any sum/product over many terms, break into chunks of 5, re-add groups, carry digits explicitly. 5) For probability: count numerator and denominator independently from the axiom, then reduce by GCD. 6) REFUTE: try to break your own answer with one adversarial example or boundary case. 7) Re-read the output contract and emit exactly the requested form, nothing else.` },
  { name: `F09_firstprin_g`, manual: `1) GIVENS: List exactly what the problem states, verbatim, as separate facts. 2) DEFINITIONS: For each term, write its precise meaning; list assumptions you'd normally make and mark each as STATED or ASSUMED — drop unstated assumptions unless the definition forces them. 3) TRAP AUDIT: examine bound inclusivity, 'exactly/at least', distinct vs identical, ordered vs unordered, reduced-fraction requirement, whole-word vs substring. 4) DERIVE the answer using only givens + definitions, naming the justification per step; do not import remembered answers. 5) ARITHMETIC HYGIENE: long sums in chunks of 5, digit-by-digit, re-add in groups, written totals. 6) ADVERSARIAL REFUTE: argue the answer is wrong; if the refutation exposes an unstated assumption, fix it. 7) Probability: numerator/denominator separately, reduce by GCD. 8) Re-read the format line and output exactly it.` },
  { name: `F10_dualprocess_d`, manual: `1. Quickly jot an intuitive answer A0.
2. Run AUDIT-1: deliberate full derivation, method M1.
3. Run AUDIT-2: re-derive with a genuinely different method M2 (complement, recursion vs direct enumeration, algebra vs casework).
4. Take the MAJORITY of {A0, A1, A2}. If all three differ, trust the two audits over intuition and reconcile by finding the specific arithmetic or framing error.
5. Arithmetic hygiene throughout: chunk sums into groups of 5 and re-add; verify multiplications by a second route.
6. Trap sweep: 'at least' vs 'exactly', off-by-one bounds, substring vs whole-word, must-reduce fraction.
7. Output exactly the required format, nothing more.` },
  { name: `F11_metacog_a`, manual: `1. Restate the problem in one line. List every assumption you are making explicitly (bounds inclusive/exclusive, distinct vs identical, 'exactly' vs 'at least', whole-word vs substring).
2. Solve once, carefully. For any heavy sum or iteration, compute in chunks of 5 and re-add the chunk totals; never sum a long list in one pass.
3. Ask: 'What single thing, if wrong, would make my whole answer wrong?' Name it concretely.
4. Check ONLY that thing by an independent route (recount it, plug into the original condition, or test a boundary case).
5. If the check disagrees, find which side erred and redo; if it agrees, stop.
6. Re-read the required output format and emit EXACTLY it (integer only / reduced a/b / one lowercase word). Reduce fractions by GCD and confirm.
Report only the final answer once confident.` },
  { name: `F11_metacog_f`, manual: `1. Build an assumption ledger: list each thing you take as given to interpret the problem (domain, distinctness, ordering, bounds, what counts as success).
2. Mark the ONE load-bearing assumption — the one the answer most depends on.
3. Try to FALSIFY it: construct a small example or re-read the wording to see if the opposite reading is intended. Adjust if needed.
4. Solve under the confirmed reading. For sums/iterations, accumulate in groups of 5 and re-add partials.
5. Verify the numeric result by an independent method or by substituting back into the original constraint.
6. Separate numerator and denominator counts for probabilities; reduce by GCD; confirm format.
7. Output ONLY the final answer in the exact required format, nothing else.` },
  { name: `F12_swarmteam_c`, manual: `Convene three specialists and a cross-checker.
1. Identify problem type (counting, probability, number theory, algorithm/simulation, logic).
2. SPECIALIST-1 solves with the canonical method for that type. SPECIALIST-2 solves with a complementary method (complement counting, generating idea, invariant). SPECIALIST-3 brute-forces a small instance and extrapolates the pattern.
3. Computation hygiene for all: never trust a long mental sum — chunk into groups of 5, keep running subtotals, re-add once.
4. CROSS-CHECKER: compare the three answers; substitute each back into every stated constraint; flag the type-specific trap (probability->numerator/denominator separate then GCD reduce; counting->'exactly' vs 'at least', distinct vs identical; sequences->strictly vs non-strictly increasing; bounds->inclusive/exclusive).
5. VOTE: choose the answer with majority agreement; if tied, prefer the one surviving back-substitution.
Re-read the output spec and produce EXACTLY that form. Output the final answer only.` },
  { name: `F12_swarmteam_h`, manual: `Three rounds, team of three plus chair.
ROUND 1 (independent): each member solves silently with a different method — algebraic, exhaustive small-case, and probabilistic/structural reasoning. Use chunked partial sums (groups of five, re-added) for any heavy computation.
ROUND 2 (debate): members compare; each must defend with a back-substitution into the problem's constraints. Surface and resolve trap risks together: base-rate, 'exactly' vs 'at least', strictly-increasing, inclusive/exclusive endpoints, substring vs whole-word, distinct vs identical, reduced-fraction-required.
ROUND 3 (vote): CHAIR tallies. Pick the majority answer. If split 1-1-1, the chair re-derives the contested quantity by a fresh independent method and votes to break the tie.
For fractions/probabilities, count numerator and denominator separately, reduce by GCD, confirm lowest terms.
Close with an output-contract check: re-read the exact required format and emit EXACTLY it (integer only / a/b reduced / single lowercase word). Output the final answer alone.` },
  { name: `F13_formatdiscipline_e`, manual: `Choose the template that matches the asked output, then fill its single slot.
- INTEGER -> [n]: a plain base-10 integer, no sign unless negative, no separators, no decimals.
- REDUCED FRACTION -> [a/b]: gcd(a,b)=1, b>0, no spaces.
- ONE WORD -> [word]: exact spelling, lowercase unless proper noun required.
- EXACT PHRASE -> copy the demanded phrasing verbatim.
Procedure:
1. Detect template from the question's final sentence.
2. Solve; verify with one independent re-derivation (must agree).
3. Pre-flag the relevant trap (Bayes base-rate table for conditional probability; 'exactly' vs 'at least'; substring vs whole word; distinct vs identical).
4. Fill the slot; for fractions reduce by gcd; for sums add in groups of 5 with a re-add.
5. Emit the filled template ALONE. Anything outside the brackets is forbidden.` },
  { name: `F14_invariants_parity_color`, manual: `1. Identify the allowed moves/operations and what changes each step.
2. Search for an INVARIANT preserved by every move: parity of a count, a checkerboard 2-coloring, sum mod k, a weighting that stays constant.
3. Compute the invariant for the start and for the goal. If they differ, the goal is impossible — that often IS the answer.
4. If reachable, the invariant constrains the count/min steps: use it as a lower bound, then exhibit a construction meeting it.
5. Test the invariant on 2-3 tiny configurations by hand to confirm it really is conserved (adversarially try to break it).
6. Beware off-by-one and 'exactly vs at least' in the final tally.
7. Re-derive the conclusion a second way (small exhaustive search) and confirm both agree.
Emit the answer in EXACTLY the requested format, nothing else.` },
  { name: `F14_invariants_recurrence_verify`, manual: `1. Compute exact values for the first 4-6 sizes by direct reasoning; tabulate.
2. Hypothesize a recurrence a(n)=f(a(n-1),a(n-2),...) that fits ALL tabulated values; confirm it predicts the next computed value.
3. Unroll/iterate the recurrence to the target n, doing arithmetic digit-by-digit and re-adding in groups of 5 to avoid slips.
4. Independently derive or guess a closed form; evaluate it at the same n. The two methods MUST agree — if not, recheck both.
5. Sanity-check growth rate and parity of the result against the small cases.
6. Re-read the question: which index, 0- or 1-based, exactly vs at least, inclusive bounds.
7. If probability, separate numerator/denominator, reduce by GCD, confirm format.
Return ONLY the answer in the exact required form.` }
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
