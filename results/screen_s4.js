export const meta = {
  name: `screen-s4`,
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
  { name: `F01_decomp_e`, manual: `1. Note the question and the exact output format.
2. Produce THREE independent attempts. Vary the decomposition order or method each time so errors are uncorrelated.
3. In every attempt apply hygiene: add long lists in chunks of 5 with written subtotals; do products digit-by-digit.
4. Collect the three final answers. Take the MAJORITY value.
5. If all three differ, do a fourth careful attempt focusing on the step where they diverged, then pick the value with most support.
6. Before locking in, check traps: inclusive/exclusive endpoints, 'exactly' vs 'at least', strictly-increasing.
7. For probability, reduce the fraction by GCD and verify format.
8. Emit exactly the required format.` },
  { name: `F02_verify_complement`, manual: `1. Identify the universe size N (total outcomes/arrangements) exactly. Flag traps: exactly vs at-least, distinct vs identical, substring vs whole-word.
2. DIRECT: count the favorable set, call it F.
3. COMPLEMENT: independently count the UNfavorable set, call it U, by a different argument.
4. CHECK: F + U must equal N. If not, one count is wrong — locate and fix before continuing.
5. For probability: keep numerator and denominator as separate integers; reduce by GCD only at the end; confirm the format (reduced a/b).
6. Sum hygiene: tally in chunks of 5, re-add each chunk twice.
7. Once F, U, N are mutually consistent, state the answer in EXACTLY the requested format.` },
  { name: `F02_verify_invert`, manual: `1. Solve forward to obtain candidate answer A. Note the output format.
2. INVERSE CHECK: substitute A back into the original conditions/equations and reconstruct the given quantities. Every stated constraint must be satisfied exactly.
3. For counting: pick the answer's structure and verify it reproduces the required totals; for equations: plug roots back; for word/algorithm problems: trace the process with A and confirm it yields the stated outcome.
4. If any condition fails, A is wrong — adjust and re-verify all conditions, not just the failing one.
5. Watch traps: distinct vs identical, reduced fraction, off-by-one on bounds.
6. Compute checks carefully, re-adding sums in chunks of 5.
7. Output exactly the required token.` },
  { name: `F03_adversarial_d`, manual: `1. Produce an answer.
2. PRE-MORTEM: 'It is graded — and it's WRONG. Why?' Brainstorm the 2-3 most probable causes ranked by likelihood for THIS problem (counting boundary, dropped case, sign error, wrong total in denominator, format violation).
3. Take the #1 cause and prove or disprove it by re-examining that exact step with fresh computation. Then #2 if time allows.
4. For any sum or long iteration, recompute partial sums in blocks and reconcile the running total — naive re-adding end-to-end is error-prone.
5. Correct anything the pre-mortem exposes; otherwise confirm.
6. Emit the answer in EXACTLY the required format (integer / reduced fraction / single lowercase word).` },
  { name: `F04_trapcheck_a`, manual: `Before computing, scan the problem against this trap list and write a one-line note for each that applies:
1. Base-rate: probabilities with a test/condition? Build a Bayes table (counts of TP, FP, FN, TN) instead of intuiting.
2. "Exactly" vs "at least" vs "at most": underline the quantifier; pick the matching count.
3. Whole-word vs substring: does 'contains' mean the full token or any letters?
4. Strictly vs non-strictly increasing/decreasing: are equal adjacent values allowed?
5. Distinct vs repeats-allowed: ordered or unordered, with or without replacement.
6. Fraction must be reduced: plan to divide by GCD.
7. Inclusive vs exclusive bounds: count endpoints carefully.
Solve only after this scan. When summing many terms, add in groups of 5, keep running partial totals. Re-derive the flagged-trap quantity by a second method; if the two disagree, redo. Re-read the output format and emit exactly it (integer / reduced a/b / one lowercase word).` },
  { name: `F04_trapcheck_f`, manual: `Scan the six-letter trap mnemonic SEWDFB before answering:
S - Strictness: strictly vs non-strictly increasing/decreasing; equality allowed?
E - Exactly vs at-least/at-most: match the quantifier precisely.
W - Whole-word vs substring (and case sensitivity).
D - Distinct vs repeated; ordered vs unordered; with/without replacement.
F - Fraction: reduce by GCD and check requested format.
B - Base-rate / Bounds: for conditional probability use a Bayes count table; for ranges check inclusive vs exclusive endpoints.
Write one clarifying line per letter that applies. Then solve. For long arithmetic, add in groups of 5 keeping subtotals. Produce TWO independent attempts (different orderings or methods); if they match, take it; if not, run a third and take the majority. Emit the answer in exactly the required format and nothing else.` },
  { name: `F05_constraint_elimination_table`, manual: `Use an elimination matrix (classic logic-grid method).
1. Build a table: categories on axes, every pairing as a cell. Mark nothing yet.
2. Translate each clue into X (impossible) or O (must) marks. A single O in a row/column forces X on all others in that line; propagate immediately.
3. Cross-infer: if A=B and B≠C, then A≠C. Apply transitively after every new mark. Loop until stable.
4. Track which clues you've fully exploited vs partially; revisit partial ones after new deductions.
5. If marks don't fully resolve, hypothesize the most-constrained open cell as O, propagate, and reject on contradiction.
6. Watch traps: 'exactly one', negations, ordering clues (left/right, before/after) — encode direction carefully.
7. Verify by re-reading EACH clue against the finished grid; all must hold. Output exactly the requested fields in the requested format.` },
  { name: `F05_constraint_bound_tighten`, manual: `Bound-tightening search for numeric/combinatorial constraints.
1. List variables, integer/real domains, and all constraints (equalities and inequalities). Flag inclusive vs exclusive bounds explicitly.
2. Derive the tightest lower and upper bound for each variable by combining constraints (substitute known sums, use min/max). Shrink each domain to its true feasible interval.
3. Re-substitute tightened bounds into other constraints to tighten further. Loop until bounds stop moving.
4. When intervals collapse to single integers, those variables are forced — propagate.
5. Enumerate only the small residual ranges; reject assignments breaking any constraint.
6. For sums/totals, compute in chunks and re-add in groups of 5 to avoid arithmetic slips.
7. Adversarial check: try to find a counterexample assignment that satisfies your bounds but breaks a constraint — if found, you missed one. Verify the final answer satisfies all constraints; emit the exact output format.` },
  { name: `F06_comphygiene_e`, manual: `COMPUTATION HYGIENE — DUAL-METHOD AGREEMENT.
1. Note the exact target quantity and output format.
2. METHOD A: compute directly, showing all intermediate arithmetic with chunked partial sums (groups of 5) and explicit carries.
3. METHOD B: compute the SAME quantity by a structurally different route — e.g. complement counting, closed-form formula vs enumeration, factoring vs expanding, or summation in a different grouping order.
4. Compare A and B. If they disagree, locate the discrepancy by checking the smallest sub-result of each; do not average — find the bug.
5. Only when A == B, accept the value.
6. Magnitude bound: confirm the answer's size is plausible (rough estimate).
7. Re-read the required format and emit exactly it.
Keep both methods terse for small problems; the cost is low and it catches most slips.` },
  { name: `F07_estimate_b`, manual: `1) Estimate the answer's ORDER OF MAGNITUDE first: how many digits, roughly what size? Write one sentence: 'Answer should be near ___.'
2) Identify which trap applies (base-rate/Bayes, substring vs whole word, strictly-increasing, exactly vs at least) and note its effect on size.
3) Compute exactly. On long arithmetic go digit-by-digit; carry explicitly; re-add groups of 5.
4) Compare exact result to your magnitude estimate. A 10x mismatch means a misplaced factor, dropped term, or off-by-one — hunt it.
5) Verify the final step by ONE different method (reverse the operation, or plug back in). Two methods must agree.
6) Output exactly the requested format, fractions reduced by GCD.` },
  { name: `F07_estimate_g`, manual: `1) Quickly estimate a plausible range [L,U] for the answer.
2) Solve the problem exactly THREE independent times, varying method or order. Use chunked partial sums (groups of 5) each time to limit arithmetic drift.
3) Discard any attempt whose result falls outside [L,U] — it failed the sanity gate.
4) Among surviving attempts, take the MAJORITY value. If all three disagree, redo the cleanest method slowly, digit-by-digit, and trust that.
5) Confirm the winner against the traps list (base-rate, reduced fraction, strictly-increasing, distinct vs identical).
6) Reduce fractions, re-read the format requirement, emit exactly the required output.` },
  { name: `F08_reduce_d`, manual: `Reduce paths/optimization/sequence-count problems to a recurrence (DP):
1. Define the state in words and the value f(state) precisely (e.g. number of ways to reach cell, min cost to position i).
2. Write the transition: f(s) in terms of smaller states. State base cases explicitly.
3. Identify evaluation order (smallest to largest). Build a small table of f-values, filling row by row, writing each cell.
4. Keep a running ledger; recompute any cell that feeds many others.
5. Read off the answer state. Verify by recomputing the final 2-3 cells via a different decomposition (e.g. count by last step).
6. Watch traps: off-by-one in bounds, inclusive endpoints, whether the start cell counts.
7. Emit exactly the required format (integer only unless stated).` },
  { name: `F09_firstprin_a`, manual: `1) DEFINE: List every technical term in the problem. Write its exact mathematical definition (set, condition, formula). Note edge cases the definition includes/excludes. 2) RESTATE: Rewrite the question using only your definitions, no informal words. 3) TRAP-CHECK each definition: 'exactly' vs 'at least', distinct vs identical, strictly vs weakly increasing, inclusive vs exclusive bounds, whole-word vs substring, reduced-fraction-required. 4) DERIVE step by step, citing which definition justifies each move. Never invoke a remembered result without re-deriving it from the definitions. 5) COMPUTE with hygiene: chunk sums in groups of 5, add digit-by-digit, keep running totals. 6) VERIFY by re-deriving the answer a DIFFERENT way; if the two disagree, find which definition you misapplied. 7) OUTPUT: re-read the required format and emit EXACTLY it (integer only / reduced a/b / one lowercase word).` },
  { name: `F09_firstprin_f`, manual: `1) DEFINE every term exactly; note inclusion/exclusion edges. 2) GROUND: Apply each definition to the smallest cases (n=0,1,2) by hand to confirm you understand it correctly; fix misreadings now (especially 'exactly' vs 'at least', strictly-increasing, distinct vs identical). 3) GENERALIZE: derive the general rule/recurrence from what the small cases reveal, justified by the definitions — not by guessing a pattern alone; confirm the rule reproduces every small case. 4) COMPUTE to the target size with hygiene: partial sums chunked in 5s, digit-by-digit arithmetic, written running totals, re-add groups. 5) For probabilities, count numerator and denominator separately, reduce by GCD, confirm format. 6) VERIFY the final number by an independent method (direct vs complement); if they disagree, recheck the small-case grounding. 7) Emit exactly the required output form, nothing more.` },
  { name: `F10_dualprocess_c`, manual: `1. FAST LANE: In under 15 seconds, give a rough estimate or ballpark (order of magnitude, parity, sign). Write it down.
2. SLOW LANE: Solve rigorously step by step. Keep a running partial result.
3. SANITY GATE: Check the rigorous answer falls inside the fast-lane band (right magnitude, right parity, plausible). A violation means a bug — locate it before proceeding.
4. For heavy sums/iterations: never decompose without hygiene — list values in rows of 5, total each row, sum the row-totals; recompute once.
5. Pre-flag traps relevant here: inclusive bounds, strictly-increasing, reduced fraction, distinct vs identical.
6. Confirm exact form; reduce fractions by GCD; emit only the contracted output.` },
  { name: `F10_dualprocess_h`, manual: `1. Before answering, name the single most likely TRAP this problem sets (off-by-one, base-rate, exactly-vs-at-least, identical-vs-distinct, unreduced fraction, exclusive bound).
2. Give your fast intuitive answer AND note whether it might have stepped into that trap.
3. Deliberate slowly to specifically neutralize the named trap: handle boundaries explicitly, build a counts table for Bayes, separate numerator/denominator for fractions.
4. Cross-check the deliberate answer by an independent route; if it disagrees with intuition, prefer deliberation unless intuition exposes a flaw in it.
5. Arithmetic hygiene: chunk and re-add sums in fives; verify each multiplication twice.
6. Reduce fractions by GCD, confirm exact value, and emit precisely the required output format and nothing else.` },
  { name: `F11_metacog_e`, manual: `1. Read carefully; record the exact output contract and any trap phrasing.
2. Produce a candidate answer.
3. PRE-MORTEM: imagine you have been told this answer is wrong. Write the three most likely reasons (miscount, off-by-one boundary, misread condition, arithmetic slip, unreduced fraction).
4. Investigate each reason concretely against the original problem. Recheck boundaries inclusive/exclusive and 'exactly' vs 'at least'.
5. Recompute any suspect arithmetic in chunks of 5, digit-by-digit, re-adding partials.
6. Fix whatever the pre-mortem exposed.
7. Final calibration: 'Am I now confident enough to bet on this?' If not, re-derive by a different method until two agree.
8. Output EXACTLY as required; confirm fraction reduced, integer-only, or single lowercase word.` },
  { name: `F12_swarmteam_b`, manual: `Run a team of three independent solvers plus an adversary.
1. Generate THREE independent attempts, each starting from a different representation (equation, enumeration, recursion). Keep each short.
2. ADVERSARY: actively try to REFUTE each attempt — find an off-by-one, a miscounted case, an unjustified assumption, an arithmetic slip. For sums/iterations re-add in groups of five, digit by digit.
3. Trap scan before deciding: base-rate (build a Bayes table if conditional probability), 'exactly' vs 'at least', strictly-increasing, distinct vs identical, reduced fraction, inclusive bounds.
4. SYNTHESIZE: keep attempts the adversary could NOT break; take their majority value. If the adversary broke all, repair the strongest and re-verify by a second method until two methods agree.
5. Confirm the output contract: re-read exactly what format is requested.
Emit only the final answer in the exact required format (integer / reduced a/b / single lowercase word).` },
  { name: `F12_swarmteam_g`, manual: `Form a team: two constructive solvers and one skeptic.
1. OPTIMIST-1 and OPTIMIST-2 independently solve using different framings (e.g., direct construction vs complement/inclusion-exclusion). Keep arithmetic clean: sum in chunks of five, re-add, check parity and last digit.
2. SKEPTIC assumes both are wrong and hunts the specific failure: off-by-one on bounds, 'exactly' vs 'at least' misread, double-counted or missing cases, distinct-vs-identical confusion, fraction not reduced.
3. VERIFIER/MERGE: back-substitute each candidate into the original constraints; keep those that satisfy all. Take the majority among survivors.
4. If skeptic invalidates both optimists, produce a corrected third solution and confirm it by an independent recomputation (two methods must agree).
5. Fractions: count numerator and denominator separately, divide by GCD, verify lowest terms.
6. FORMAT GATE: re-read the exact output spec and emit ONLY that (integer / reduced a/b / one lowercase word).` },
  { name: `F13_formatdiscipline_d`, manual: `1. Pass A (solve): reason to an answer.
2. Pass B (refute): assume the answer is wrong. Re-derive with a different approach and try to break it. Reconcile any difference; keep the survivor.
3. FORMAT AUDIT (checklist, answer yes to each):
 - Did I emit the exact type asked (int / a/b / word / phrase)?
 - Fraction fully reduced (gcd=1)?
 - No stray units, symbols, commas, or prose?
 - Correct case for words?
 - Boundary traps resolved (inclusive/exclusive, exactly/at least, strict/non-strict)?
4. For large arithmetic, re-add numbers in chunks of 5 and compare totals.
5. Output only the audited token. If any checklist item failed, fix and re-audit before answering. Never include the reasoning in the final line.` },
  { name: `F14_invariants_basecase_ladder`, manual: `1. Compute the answer by brute force for n=0,1,2,3,4 exactly. Lay results in a table; double-check each by hand.
2. Look for the pattern: differences, ratios, known sequences (powers, factorials, Fibonacci, binomials). State a closed-form conjecture.
3. Verify the conjecture against EVERY base case computed; if one fails, discard and re-look.
4. Justify the step n→n+1 with a one-line recurrence or combinatorial argument (don't just pattern-match).
5. Test an extreme/degenerate case (n=0, empty, all-equal) and a large case where the formula's growth must stay sane.
6. Re-read what is asked: exact count vs at-least, inclusive bounds, distinct vs identical. Plug the target n.
7. If arithmetic is heavy, evaluate the formula digit-by-digit and re-add in groups of 5.
Output EXACTLY the required format (integer / reduced a/b / one word).` },
  { name: `F14_invariants_mod_classes`, manual: `1. Suspect modular structure: choose a small modulus k (2,3,4,9,10, or a period in the recurrence).
2. Split the range/objects into residue classes mod k. Within each class behavior is uniform.
3. Count items per class with floor/ceiling formulas; be meticulous about endpoints (inclusive vs exclusive).
4. Verify class counts by hand on a small range (e.g., 1..12) against direct enumeration.
5. Recombine per-class results into the total; ensure classes partition without overlap or gap.
6. Pre-flag traps: 'exactly k' vs 'at least k', distinct vs repeated, reduced-fraction requirement.
7. Re-derive the total a different way (complementary count: total minus excluded) and require the two match.
8. For sums, chunk into groups of 5 and re-add; check each digit.
Emit precisely the required output format and nothing more.` }
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
