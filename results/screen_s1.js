export const meta = {
  name: `screen-s1`,
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
  { name: `F01_decomp_b`, manual: `1. Identify the asked quantity and required output format.
2. METHOD A: break into parts, compute each with care (chunked sums of 5, digit-by-digit products).
3. METHOD B: re-derive the SAME answer differently — reorder terms, use a formula vs direct count, or complementary counting.
4. Compare A and B. If they disagree, locate the diverging part, recompute only it, repeat until they match.
5. For probabilities/fractions: count numerator and denominator separately; reduce by GCD; confirm the format (reduced a/b).
6. Flag classic traps before finalizing: base-rate (build a small Bayes table), 'exactly' vs 'at least', endpoints.
7. Output only the value in the exact required format.` },
  { name: `F01_decomp_g`, manual: `1. Identify the quantity and output format.
2. For iterative/recursive problems (sequences, Collatz-style, prime sums), process terms in ORDER, smallest unit first.
3. CHECKPOINT rule: after every 5 terms, stop and re-add those 5 from scratch; confirm the checkpoint subtotal, then fold it into the grand total kept as a separate number.
4. Keep two columns: current-term value and cumulative total; update deliberately.
5. Do each arithmetic step digit-by-digit; never batch a long mental sum.
6. At the end, re-add all checkpoint subtotals as the final cross-check.
7. Trap scan: inclusive vs exclusive count of terms, 'exactly' vs 'at least', off-by-one on range length.
8. Output the exact format only.` },
  { name: `F02_verify_bayes_table`, manual: `1. Spot base-rate/conditional problems. Pre-flag: the prior is NOT the answer.
2. METHOD A (formula): write Bayes explicitly, P(H|E)=P(E|H)P(H)/P(E); compute P(E) via total probability.
3. METHOD B (counts): imagine a concrete population (e.g. 10,000). Fill a 2x2 table of true/false x positive/negative using the given rates. Read the answer directly off the table cells.
4. The two answers must match. If not, recheck which rate is conditional on which.
5. Keep numerator and denominator as integers; reduce by GCD; confirm requested format (decimal vs reduced fraction).
6. Re-add column/row totals in groups of 5 to verify the table is internally consistent.
7. Output exactly the required format, nothing more.` },
  { name: `F03_adversarial_a`, manual: `1. Solve the problem once, normally, showing key steps.
2. STOP. Declare: 'Assume this answer is WRONG.' Name the single most likely reason in one sentence (e.g., miscounted, off-by-one, used 'at least' as 'exactly', forgot to reduce fraction, arithmetic slip).
3. Attack only that named weakness: redo the exact sub-step it touches. For sums/iterations, re-add in groups of 5 and recheck each term.
4. If the attack reveals an error, fix it and re-attack the new answer once more. If no error found, the answer stands.
5. Re-read the required output format and emit EXACTLY it (integer only / reduced a/b / one lowercase word). Nothing else.
Keep the refutation short for easy problems; spend effort only where the named weakness lives.` },
  { name: `F03_adversarial_f`, manual: `1. Solve via Method A.
2. Commit to actively DISPROVING the answer using Method B — a genuinely different route (complement counting, direct enumeration, algebra vs casework, Bayes table for any base-rate problem). Try to make B disagree.
3. If B disagrees with A: at least one is wrong. Find which by checking the divergent step with careful chunked arithmetic; resolve to the correct value.
4. If B confirms A despite honest effort to break it, trust the result.
5. For probabilities: count numerator and denominator separately in B, reduce by GCD, and confirm the reduced form matches.
6. Re-read the output spec and emit exactly that.` },
  { name: `F04_trapcheck_c`, manual: `Treat the problem as a designed trap. For each item below, actively try to catch yourself making the naive error, then state why your reading is correct:
1. Did I read 'exactly' as 'at least' (or vice versa)? Quote the exact phrase.
2. Did I treat a substring as a whole word, or ignore word boundaries?
3. Did I allow equal values where 'strictly' forbids them?
4. Did I assume items are distinct when they may repeat (or repeat when distinct)?
5. Did I forget to reduce the fraction, or misformat it?
6. Did I include/exclude an endpoint wrongly?
7. For conditional probability, did I confuse P(A|B) with P(B|A)? Build a Bayes table.
Only after refuting each likely trap, compute. For long additions, sum in groups of 5 and recheck each group. Produce the answer, then a one-line independent re-derivation. Emit exactly the required format.` },
  { name: `F04_trapcheck_h`, manual: `Solve the problem normally first, with arithmetic hygiene (sums in chunks of 5, running subtotals, digit-by-digit for large numbers). Then run a targeted verification pass - for each trap that applies, perform the specific check:
- Base-rate: rebuild the conditional probability via a Bayes table of raw counts; compare.
- Exactly/at-least: recount the boundary cases (k and k+/-1) to confirm the quantifier.
- Whole-word/substring: re-test on the literal tokens.
- Strict-increase: re-scan for any equal adjacent pair.
- Distinct: confirm no element was double-counted or wrongly merged.
- Reduced fraction: recompute GCD; divide; confirm coprime.
- Inclusive bounds: recount endpoints.
If any check contradicts your answer, fix and re-verify that trap. Keep it tight on easy problems. Finally, re-read the output contract and emit exactly the demanded format (integer / reduced a/b / one lowercase word).` },
  { name: `F05_constraint_invariant_parity`, manual: `Exploit invariants before brute search.
1. Model the configuration (grid, tiling, moves, assignment) and write the constraints.
2. BEFORE enumerating, look for an invariant: parity, sum mod n, coloring (checkerboard), conserved quantity, or counting argument. Such invariants often forbid whole classes of states instantly — proving impossibility or fixing values.
3. Apply the invariant to prune the domain; record what it rules out.
4. Propagate remaining forced cells from the constraints. Loop until stable.
5. Enumerate only the residual small space, case by case, discarding constraint violations.
6. For counts, tally carefully in chunks of 5; for existence, one valid construction suffices.
7. Cross-verify: confirm your answer satisfies BOTH the invariant and every explicit constraint, derived a second way. Re-read the question (exactly/at least, distinct/identical) and emit the exact required format.` },
  { name: `F06_comphygiene_b`, manual: `COMPUTATION HYGIENE — DIGIT-BY-DIGIT.
For every multi-digit add/subtract/multiply, work columns right-to-left, writing each carry explicitly.
1. Identify the exact quantity required and its output format.
2. Align numbers by place value, padding with leading zeros.
3. Process the units column, then tens, then hundreds; record the digit kept and the carry carried.
4. For multiplication, compute one partial product per digit, then add partials using the columnar method above.
5. Verify by a different route: cast out nines (digit-sum mod 9 of inputs must equal digit-sum mod 9 of the result), OR recompute via rounding (round inputs, estimate, compare).
6. Bound-check magnitude: number of digits in the answer should match input sizes.
7. Re-read required format; output exactly that.
Never do multi-digit math "in your head" in one leap — always show carries.` },
  { name: `F06_comphygiene_g`, manual: `COMPUTATION HYGIENE — BASE-RATE TABLE.
1. Spot conditional-probability or base-rate wording. Flag the trap: the answer is NOT the test accuracy.
2. Pick a concrete population size (e.g. 10,000 or 100,000) that makes all cells whole numbers.
3. Build a 2x2 table: rows = true condition (yes/no), columns = test/observed (positive/negative). Fill each cell by multiplying population × base rate × conditional rate, digit-by-digit.
4. Sum the row and column margins; confirm all four cells add to the chosen population.
5. The requested conditional = target cell / (sum of the relevant row or column). Count numerator and denominator separately.
6. Reduce by GCD if a fraction is required; convert to the requested format (decimal/percent/fraction).
7. Sanity-bound: compare against the naive intuition to confirm the table-corrected value differs sensibly.
8. Re-read the output contract and emit exactly it.` },
  { name: `F07_estimate_d`, manual: `1) Build a quick APPROXIMATION using a simplifying assumption (uniformity, independence, rounding, a closed-form near-formula). Compute it fast → estimate E.
2) Note WHY the exact answer should differ from E and in which direction (the correction term's sign).
3) Compute the exact answer with computation hygiene: group terms, partial sums of 5, explicit carries.
4) Reconcile: exact − E should match the predicted direction/size of the correction. If the sign is wrong, your exact work or your model is flawed — re-examine.
5) Pre-flag the classic trap relevant here and confirm you handled it.
6) Emit exactly the required format (integer / reduced a/b / one lowercase word).` },
  { name: `F08_reduce_a`, manual: `1. Before computing, write one sentence: "This is a ___ problem" (Bayes update, inclusion-exclusion, stars-and-bars, binomial, pigeonhole, Euler totient, linearity of expectation, DP shortest path, modular arithmetic).
2. Write the canonical formula for that template with named symbols.
3. Map each problem quantity to a symbol; list the substitutions explicitly so none is dropped.
4. Flag the matching trap NOW: "exactly" vs "at least", distinct vs identical, inclusive vs exclusive bounds, reduced fraction required.
5. Substitute and compute. Do heavy sums in chunks of 5 terms, writing each partial total.
6. Re-derive the answer by a second method (e.g. complement counting, or direct enumeration of a small case) until two methods agree.
7. Re-read the required output format and emit EXACTLY it (integer only / reduced a⁄b / one lowercase word).` },
  { name: `F08_reduce_f`, manual: `Solve by mapping to a known problem TWICE, via different templates:
1. Identify the problem type and a primary standard model (formula A).
2. Identify an alternative model that should give the same answer (e.g. direct count vs complement; expectation by linearity vs by cases; combinations vs path-counting).
3. Solve A fully with computation hygiene: expand factorials/sums in chunks of 5, log partial results.
4. Solve B independently, not reusing A's intermediate numbers.
5. If A=B, accept. If they differ, find the discrepancy: re-check which trap applies (exactly/at-least, distinct/identical, ordered/unordered) and redo the wrong one.
6. For fractions, count numerator and denominator separately, reduce by GCD, confirm lowest terms.
7. Re-read the output contract and emit precisely that.` },
  { name: `F09_firstprin_c`, manual: `1) UNIVERSE: From definitions, write precisely what the full set of objects/outcomes is. State its size and how an element is uniquely specified. 2) CONSTRAINT: Translate every condition into a membership test on that universe. Flag 'exactly' vs 'at least', distinct vs identical, ordered vs unordered. 3) For small universes, ENUMERATE elements in a fixed canonical order; mark which pass. For large ones, derive the count via the multiplication/addition principle, justified per step. 4) COMPUTE carefully: chunked partial sums in groups of 5, digit-by-digit addition, running totals written down. 5) PROBABILITY: numerator = passing count, denominator = universe size, computed separately; reduce by GCD; confirm reduced form. 6) VERIFY by an independent recount (different ordering or complementary count); reconcile if they differ. 7) Emit EXACTLY the required output format.` },
  { name: `F09_firstprin_h`, manual: `1) DEFINE all terms exactly; flag traps (exactly vs at least, distinct vs identical, strict inequality, inclusive bounds, reduced fraction, substring vs word). 2) DERIVE the answer purely from those definitions, justifying each step — no formula recall without re-derivation. 3) REDO from scratch via a genuinely different route (e.g., complementary counting, bijection, direct enumeration), again definitions-only. 4) Do a THIRD independent pass if cheap. 5) ARITHMETIC HYGIENE on every pass: chunk sums in 5s, digit-by-digit addition, written running totals. 6) MAJORITY: compare the independent answers; take the value that agrees across passes. If all differ, locate the misapplied definition and rerun. 7) Fractions: numerator and denominator counted separately each pass, reduced by GCD. 8) Re-read the output contract and emit EXACTLY the required format (integer only / reduced a/b / one lowercase word).` },
  { name: `F10_dualprocess_e`, manual: `1. PRIOR: State your instinctive answer and your confidence (low/med/high) in one line.
2. EVIDENCE: Deliberately work the problem, generating at least two checkable facts (a boundary case, a known sub-result, a parity/divisibility constraint).
3. UPDATE: If evidence contradicts the prior, abandon the prior immediately — do not anchor. If confidence was low, weight the audit more.
4. For Bayes/conditional problems, build an explicit table of counts (true-pos, false-pos, totals) rather than reasoning verbally; watch for base-rate neglect.
5. Sum hygiene: groups of 5, re-add; fractions: numerator and denominator separately, reduce by GCD.
6. Re-read the output contract and emit exactly the demanded format.` },
  { name: `F11_metacog_b`, manual: `1. Identify what is asked and the exact output format. Note any trap words ('exactly', 'at least', 'distinct', 'strictly', 'reduced').
2. Produce a first answer.
3. Assign a confidence 0-100 and write one sentence justifying it.
4. If confidence >=85: do a single sanity check (units, parity, rough magnitude, boundary) then finish.
5. If confidence <85: re-derive by a genuinely DIFFERENT method. For arithmetic-heavy work, recompute digit-by-digit and group additions in fives. Continue until two independent methods agree.
6. Adversarially attack your answer: 'Here is why this is wrong...' If the attack succeeds, fix it.
7. Recompute confidence. Only output when >=90.
8. Emit the answer in EXACTLY the required format; reduce fractions, confirm integer-only if demanded.` },
  { name: `F11_metacog_g`, manual: `1. Note output format and trap words.
2. PASS 1 (estimate): quickly get an approximate answer or bound (magnitude, parity, rough probability). This is your guardrail.
3. PASS 2 (exact): solve precisely. Keep heavy arithmetic hygienic: digit-by-digit, partial sums in fives, re-add.
4. Reconcile: does the exact answer sit inside the guardrail? If it violates the estimate, one of them is wrong — find which before proceeding.
5. Ask the single-fault question: 'What one misreading would flip this?' Check that condition (inclusive/exclusive, exactly/at-least, distinct/identical).
6. For fractions, count top and bottom separately, reduce by GCD, confirm reduced form required.
7. Only when estimate and exact agree in magnitude and the trap is cleared, emit EXACTLY the required format.` },
  { name: `F12_swarmteam_d`, manual: `Act as a swarm requiring consensus.
1. Spawn three solver lines with diverse starting assumptions/orderings so errors are uncorrelated.
2. Each line solves end to end. For heavy addition or long iterations, write partial sums in blocks of five and re-add the blocks; verify each digit.
3. VERIFIER rule: an answer is ACCEPTED only if reproduced by two independent methods. Re-derive any single-line answer a second way (algebraic check, reverse computation, unit/parity check).
4. Pre-flag traps: Bayes base-rate, 'exactly' vs 'at least', whole-word vs substring, reduced-fraction-required, inclusive/exclusive endpoints, distinct vs identical objects.
5. SYNTHESIZER: report the consensus value (>=2 agree). If no pair agrees, run a clean fourth attempt as tie-breaker.
6. For fractions: separately count numerator and denominator, divide by GCD, confirm lowest terms.
Finally re-read the requested format and emit EXACTLY it (integer only / a/b reduced / one lowercase word). Nothing else.` },
  { name: `F13_formatdiscipline_a`, manual: `1. FIRST read the question's final ask and write the exact output contract: integer? reduced fraction a/b? one lowercase word? exact phrase? Note units and bounds.
2. Solve the problem normally, but keep the target type in view.
3. Before answering, run a 2-line check: re-derive the result by a DIFFERENT method; if the two disagree, redo.
4. Trap scan: 'exactly' vs 'at least', inclusive vs exclusive bounds, distinct vs identical, whole-word vs substring, strictly vs non-strictly increasing. Confirm which applies.
5. If a fraction: compute numerator and denominator separately, divide both by gcd, verify lowest terms.
6. Heavy sums: add in groups of 5, write partial totals, re-add once.
7. Emit ONLY the contract token. No words, no units unless required, no explanation, no trailing punctuation. If the answer is a word, lowercase unless told otherwise.` },
  { name: `F13_formatdiscipline_f`, manual: `For high-variance problems.
1. Produce THREE independent attempts using different orderings or methods; do not let earlier attempts bias later ones.
2. Take the majority answer. If all three differ, run a fourth as tiebreaker by the cleanest method.
3. Before finalizing, scan classic traps on the winning answer: inclusive/exclusive bounds, exactly vs at least, strictly increasing, distinct vs identical, reduced-fraction-required.
4. Computation hygiene for any heavy sum/iteration: chunk into groups of 5, write partial sums, re-add once.
5. FORMAT lock: match the exact contract (integer only / reduced a/b via gcd / one lowercase word). Strip all units, symbols, and prose.
6. Emit only the single final token. No mention of the voting or alternatives.` },
  { name: `F14_invariants_symmetry_fold`, manual: `1. Spot symmetries: swap, reflection, rotation, relabeling that leave the problem invariant.
2. Use symmetry to reduce to canonical cases (e.g., fix the largest element, assume a<=b<=c). Solve the reduced case.
3. Multiply back by the orbit size, but CAREFULLY correct overcounting: subtract/adjust configurations fixed by the symmetry (Burnside-style: average fixed points over the group).
4. Verify on a tiny instance by full enumeration that your multiply-and-correct gives the brute-force count.
5. Pre-flag traps: distinct vs identical objects, ordered vs unordered, whether reflections count as the same.
6. Count numerator and denominator separately if it's a probability; reduce by GCD; confirm format.
7. Cross-check the total against an independent global count (sum over a different partition) — both must match.
Return EXACTLY the required output form.` },
  { name: `F14_invariants_majority_vote`, manual: `1. Solve the problem THREE independent ways, each using a different lens: (a) a conserved invariant or parity, (b) small-case pattern + recurrence, (c) direct enumeration or complementary counting.
2. Keep each attempt short and self-contained; do not let one bias the next.
3. Compare the three results. If at least two agree, adopt that majority answer.
4. If all three differ, find the error: re-test each method on a tiny base case and on one extreme case; discard the one that fails.
5. Pre-flag traps before voting: exactly-vs-at-least, distinct-vs-identical, inclusive endpoints, whole-word-vs-substring, reduced fraction needed.
6. For the winning answer, do final arithmetic carefully — group sums by 5, verify digits; for fractions reduce by GCD.
7. Re-read the output contract and emit EXACTLY that (integer / reduced a/b / one lowercase word), with no explanation.` }
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
