export const meta = {
  name: `screen-s2`,
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
  { name: `F01_decomp_c`, manual: `1. Write the target and output contract at top.
2. Build a LEDGER: one row per subtask with columns [step | computed value | running total].
3. Solve subtasks top to bottom. After each row, recheck the partial value by a quick independent estimate or reverse operation; only then update running total.
4. Heavy sums: add in groups of 5, record each group subtotal as its own ledger row.
5. Carry digits explicitly in multi-digit arithmetic; never hold large numbers in your head.
6. At the end, re-scan the ledger top-to-bottom confirming each running-total increment is consistent.
7. Pre-flag: distinct vs identical, strictly-increasing, reduced-fraction-required, inclusive bounds.
8. Emit exactly the contracted format.` },
  { name: `F01_decomp_h`, manual: `1. List ALL explicit and implicit constraints; restate the required output format verbatim.
2. Decompose by constraint: handle one constraint per step, narrowing the candidate set.
3. For counting/probability, count favorable and total SEPARATELY; build each via chunked sums of 5, digit-by-digit where large.
4. Classify each constraint: distinct vs identical, ordered vs unordered, strictly-increasing, inclusive/exclusive — and apply the matching formula.
5. Reduce any fraction by GCD; confirm it is in lowest terms.
6. VERIFY by re-deriving the count a different way (complement or direct) and require agreement; recompute the diverging part if not.
7. Final trap check: 'exactly' vs 'at least', whole-word vs substring.
8. Emit exactly the contracted answer, nothing extra.` },
  { name: `F02_verify_three_vote`, manual: `1. Note the output contract and one likely trap.
2. Solve the problem THREE times, each as an independent fresh attempt using a different framing where possible (direct, complementary, algebraic/substitution). Do not look back at prior attempts while working a new one.
3. Collect the three answers.
4. If all three agree: done. If two agree and one differs: re-examine the outlier to confirm it's the error, then take the majority. If all three differ: identify the most error-prone step across them, recompute it slowly (digit-by-digit, sums in groups of 5), and run a tie-break fourth attempt.
5. For fractions, reduce by GCD and verify format; for 'exactly/at-least' confirm interpretation matches all attempts.
6. Emit the majority answer in EXACTLY the requested format.` },
  { name: `F03_adversarial_b`, manual: `1. Before solving, list the trap that fits this problem type: 'exactly' vs 'at least', inclusive vs exclusive bounds, whole-word vs substring, distinct vs identical, strictly vs non-strictly increasing, reduce-fraction-required, base-rate neglect.
2. Solve the problem to a candidate answer.
3. Write THREE specific wrong answers you could plausibly have produced (one per trap above when applicable). For each, state precisely what mistake would yield it.
4. Check your candidate against all three: if it coincides with a trap answer, you likely fell in — redo with the correct interpretation.
5. Recompute any heavy arithmetic digit-by-digit or in chunks to confirm.
6. Output EXACTLY the demanded format, nothing more.` },
  { name: `F03_adversarial_g`, manual: `1. Produce Attempt 1 and Attempt 2 INDEPENDENTLY (do not let the first bias the second; ideally use different framings).
2. If they AGREE: run one quick adversarial pass — name the single most likely shared mistake and check it. If clean, done.
3. If they DISAGREE: treat each as a suspect. Adversarially attack both — for each, name why it might be wrong and recompute the contested step. Keep the one that survives scrutiny.
4. If still unsure, run a third independent attempt and take the majority value.
5. Recompute any large sums in groups of 5 to break ties reliably.
6. Emit the final answer in EXACTLY the required output format.` },
  { name: `F04_trapcheck_d`, manual: `Pass 1 (Parse, do not compute): copy every constraint word verbatim and tag its trap class - quantifier (exactly/at least/at most), strictness (strict/non-strict), distinctness (distinct/repeats), membership (whole-word/substring), bounds (inclusive/exclusive), output (reduced fraction / integer / single word). Resolve each tag explicitly in words.
Pass 2 (Solve): use the locked constraints. For sums or iterated processes, never add everything at once - chunk into groups of 5, write partial sums, then total the partials; for big numbers work digit-by-digit. For probability, count numerator and denominator separately, then reduce by GCD.
Verify: re-derive the final number by a different route (e.g., complement counting, or summing in reverse). If they disagree, find the error before answering. Final line: the answer in exactly the demanded format.` },
  { name: `F05_constraint_grid_forced`, manual: `Constraint-propagation first; search last.
1. Draw the explicit structure: list variables/cells, their domains (allowed values), and every constraint verbatim.
2. Pre-flag traps: distinct vs identical, strictly-increasing, 'exactly' vs 'at least', inclusive/exclusive bounds. Note each as a constraint.
3. PROPAGATION LOOP: scan for any cell whose value is now forced (only one domain value survives the constraints). Fill it, then rescan. Repeat until no cell is forced. Record each deduction with its reason.
4. If fully determined, stop. Else pick the variable with the SMALLEST remaining domain and branch on its values one at a time; re-run propagation inside each branch; discard contradictions.
5. Count solutions if asked (don't stop at one). Re-add counts in groups of 5.
6. Verify: re-check every original constraint against your solution. Re-read the output format and emit exactly it.` },
  { name: `F05_constraint_two_pass_count`, manual: `Exhaustive ordered enumeration for counting/probability.
1. Fix a canonical order (e.g. lexicographic, smallest-first) so every valid configuration is generated once and only once — prevents double-count and omission.
2. Write constraints; flag 'distinct vs identical', 'strictly increasing', 'exactly k'.
3. Walk the ordered space, pruning partial prefixes that already violate a constraint (don't expand dead prefixes).
4. Count favorable outcomes (numerator) and, separately, the total sample space (denominator) — never conflate them. Tally each in groups of 5 and re-add.
5. For probability, form numerator/denominator, then reduce by GCD; confirm reduced form if required.
6. Self-consistency: recount once using a complementary method (total minus bad, or a symmetry/combinatorial formula); the two counts must match.
7. Emit exactly the requested format (integer, or reduced a/b).` },
  { name: `F06_comphygiene_c`, manual: `COMPUTATION HYGIENE — FRACTION/PROBABILITY DISCIPLINE.
1. Read the question; flag traps NOW: 'exactly' vs 'at least', distinct vs identical, with/without replacement, inclusive/exclusive bounds.
2. Count the DENOMINATOR (total outcomes) independently. Show the formula and the arithmetic.
3. Count the NUMERATOR (favorable outcomes) independently, by a method NOT reused from the denominator.
4. Sanity-bound: the fraction must be between 0 and 1; estimate roughly and compare.
5. Reduce: compute GCD of numerator and denominator step by step (Euclid), divide both.
6. Re-derive the numerator a second way (complement, or direct enumeration of a small case) and confirm the same value.
7. Check the required output format: reduced a/b? decimal? percent? Emit EXACTLY that, lowest terms.
Never leave a fraction unreduced when 'reduced' is required.` },
  { name: `F06_comphygiene_h`, manual: `COMPUTATION HYGIENE — MAJORITY VOTE.
For high-variance arithmetic/counting problems:
1. Note the exact quantity and output format.
2. Produce THREE independent attempts. For each, vary the approach: different grouping order for sums, different counting decomposition, or different formula. Show each attempt's key arithmetic with explicit carries.
3. Within each attempt, re-add long sums in groups of 5 to suppress per-attempt slips.
4. Collect the three results. Take the MAJORITY value. If all three differ, run a fourth attempt and recheck the most error-prone step in each.
5. For the chosen value, do one magnitude sanity-bound (rough estimate must match).
6. If a fraction, ensure it is reduced (GCD) and in the required form.
7. Re-read the output contract and emit EXACTLY the required format — nothing else.
Keep each attempt lean so the three-fold cost stays affordable.` },
  { name: `F07_estimate_e`, manual: `1) Make TWO independent rough estimates by different reasoning paths (e.g. one by averaging, one by a representative case). Call them E1, E2; treat them as a soft interval.
2) Compute the exact answer carefully — chunk long sums into fives, re-add each chunk, track carries digit-by-digit.
3) The exact answer should sit near or between E1 and E2. If it's far outside both, distrust it and recompute.
4) If E1 and E2 disagree wildly, that signals a conceptual ambiguity (which trap? exactly/at-least, distinct/identical) — resolve it before trusting the exact value.
5) Final check: reduce any fraction by GCD, re-read the output contract, output exactly that and nothing more.` },
  { name: `F08_reduce_b`, manual: `For any conditional-probability or 'given that' problem, reduce to a Bayes table:
1. Identify hypotheses H and evidence E. Pre-flag the base-rate trap: the prior matters even when the test is accurate.
2. Build a 2x2 (or NxM) table of counts over a concrete population (e.g. 100000 people). Fill: prior*likelihood for each cell.
3. P(H|E) = (cell for H and E) / (sum of all cells with E). Count numerator and denominator separately.
4. Sanity-check: does the posterior move in the intuitive direction and stay in [0,1]?
5. Reduce the fraction by GCD; if a decimal is asked, divide carefully digit-by-digit.
6. Verify independently: recompute via the odds form (prior odds x likelihood ratio) and confirm it matches.
7. Emit exactly the requested format.` },
  { name: `F08_reduce_g`, manual: `Lead with trap detection, then reduce to the standard formula:
1. Scan the prompt for trap keywords and circle them: 'exactly', 'at least', 'at most', 'distinct', 'strictly increasing', 'whole word' vs substring, 'reduced fraction', inclusive/exclusive, 'non-empty'.
2. For each trap, write the one adjustment it forces (e.g. 'at least one' -> use complement 1 - P(none)).
3. Now name the canonical problem and its formula consistent with those adjustments.
4. Substitute values; compute heavy arithmetic digit-by-digit and re-add sums in groups.
5. Adversarially self-refute: try to argue the answer is wrong by one (off-by-one, double-count, missed case). Fix if the attack lands.
6. Reduce fractions via GCD if needed.
7. Output exactly the required form, nothing else.` },
  { name: `F09_firstprin_d`, manual: `1) SYMBOLIZE: Assign symbols to all objects, sets, quantifiers. Rewrite the claim as a precise logical/set-theoretic statement (use ∀, ∃, ∈, |·|). 2) DEFINE each predicate by its exact membership condition; pin down trap-prone words: 'exactly'=equality, 'at least'=≥, strictly-increasing=<, distinct=pairwise unequal, inclusive bounds. 3) DERIVE by valid symbolic manipulation only; cite the rule (definition, distributivity, inclusion-exclusion) at each step, re-deriving any identity you use. 4) Convert to numbers only at the end. ARITHMETIC HYGIENE: sums in chunks of 5, digit-by-digit, re-add. 5) Fractions: separate numerator/denominator, reduce by GCD, confirm format. 6) VERIFY: re-evaluate the symbolic statement by a second method (e.g., complement, bijection) until two agree. 7) Re-read and output exactly the demanded format.` },
  { name: `F10_dualprocess_a`, manual: `1. SNAP: Write one fast intuitive answer in a line marked GUESS. Do not refine it yet.
2. AUDIT: Solve the problem again from scratch using a DIFFERENT method (different order, different formula, complementary counting). Do not look at GUESS while doing this.
3. COMPARE: If audit == GUESS, accept. If they differ, find which is wrong; the disagreement is a red flag — re-derive a third time to break the tie.
4. HYGIENE: For any sum/iteration, write terms in chunks of 5, add each chunk, then add chunk totals. Never sum a long list in one pass.
5. TRAP CHECK before finalizing: 'exactly' vs 'at least', inclusive/exclusive bounds, distinct vs identical, substring vs whole word, reduced fraction required.
6. OUTPUT: Re-read the requested format and emit EXACTLY it (integer only / reduced a/b / one lowercase word). Nothing else.` },
  { name: `F10_dualprocess_f`, manual: `1. Write your fast answer, then mentally SEAL it — commit to ignoring it.
2. Solve the problem deliberately as if you had no guess: define variables, set up the exact relation, compute with care.
3. Keep computation honest: for iterations/sums, track state in a small table row-by-row; re-add long totals in chunks of 5; recompute any product twice.
4. UNSEAL: compare deliberate result to the sealed guess. Agreement → high trust. Disagreement → the deliberate path wins unless you find a concrete bug in it.
5. Final trap pass: exactly-vs-at-least, inclusive/exclusive, distinct vs identical, strictly-increasing, reduced fraction.
6. Emit only the exact required output format.` },
  { name: `F11_metacog_c`, manual: `1. Run the trap checklist before solving. For each that applies, write a one-word note: base-rate(Bayes table)? 'exactly' vs 'at least'? whole-word vs substring? strictly-increasing? distinct vs identical? reduced fraction required? inclusive/exclusive bounds?
2. State your reading of each flagged trap so the setup is unambiguous.
3. Solve. Keep heavy computations clean: partial sums in groups of 5, re-add the partials.
4. Verify by a second independent method (different counting order, complementary count, algebra vs enumeration).
5. If the two answers differ, locate the error explicitly; do not average.
6. Final metacognitive question: 'Which trap am I most likely still falling into?' Re-examine that one.
7. Output EXACTLY the demanded format: integer only, or reduced a/b confirmed by GCD, or one lowercase word.` },
  { name: `F11_metacog_h`, manual: `1. Classify the problem: TRIVIAL (one step, low trap risk) or HARD (multi-step, heavy arithmetic, or trap-prone).
2. Always state the output format and scan for trap words ('exactly', 'at least', 'distinct', 'strictly', 'reduced', inclusive/exclusive).
3. If TRIVIAL: solve once, do one quick sanity check, output. Do not over-deliberate short problems.
4. If HARD: solve once; then re-derive by a DIFFERENT method. For long sums/iterations, chunk in fives and re-add partials; verify each boundary.
5. Run one adversarial refutation: actively argue the answer is wrong and see if the argument holds.
6. Resolve any disagreement by locating the specific error, not by guessing.
7. Confirm the single most-likely trap is handled.
8. Emit EXACTLY the required format: integer only, reduced a/b (GCD-confirmed), or one lowercase word.` },
  { name: `F12_swarmteam_e`, manual: `Run a size-adaptive team.
1. Gauge difficulty. EASY/SHORT: one careful solve plus one quick second-method check — do not over-think.
2. HARD/HIGH-VARIANCE: spawn three independent solvers using distinct strategies (direct, complementary, small-case induction).
3. Every solver applies arithmetic hygiene: chunk sums into 5s, keep subtotals, re-add; for products check magnitude/last digit.
4. VERIFIER: cross-check answers, back-substitute into constraints, and run the trap checklist that applies: 'exactly' vs 'at least', distinct vs identical, strictly-increasing, inclusive bounds, substring vs whole-word, reduced fraction (count num/den separately, GCD-reduce).
5. SYNTHESIZE by majority; on a tie, the verifier re-solves the contested step.
6. Output-contract pass: re-read the exact format and emit ONLY it (integer / reduced a/b / single lowercase word).
Spend effort proportional to risk; let independent agreement, not length, drive confidence.` },
  { name: `F13_formatdiscipline_b`, manual: `Treat formatting as a final compiler pass.
1. Solve and get a candidate answer with full reasoning.
2. Verify by a second independent method; require agreement before continuing.
3. NORMALIZE pass (apply in order): strip leading/trailing spaces; remove '$', '%', commas, and explanatory words unless the format demands them; convert decimals to required form; if a fraction, reduce by gcd and confirm denominator>0 and lowest terms; if an integer, ensure no '.0' tail; if a word, force exact spelling and lowercase.
4. Re-read the prompt's literal request and ask: 'Is my token character-for-character what they want?'
5. Trap recheck before output: counting boundaries (off-by-one), 'at least' vs 'exactly', rounding direction.
6. Output the single normalized token alone on its own line. Nothing else.` },
  { name: `F13_formatdiscipline_g`, manual: `The most common error is answering a different quantity than asked.
1. Quote (mentally) the LAST sentence of the prompt. Identify the precise quantity and its required form.
2. Confirm you are solving for THAT quantity, not an intermediate (e.g., they want the remainder, not the quotient; the count of ways, not the probability).
3. Solve; verify by a second method until two agree.
4. Trap pre-flag tied to phrasing: 'how many' -> integer count; 'probability' -> reduced fraction unless decimal asked; 'which word' -> exact token. Resolve exactly/at least and boundary inclusivity.
5. Arithmetic hygiene: digit-by-digit for multiplication, group-of-5 re-adds for long sums.
6. Final equality check: 'My token answers the literal final question in the demanded format.' 
7. Output exactly that token, nothing else, no units unless the contract includes them.` },
  { name: `F14_invariants_monovariant_bound`, manual: `1. Define a non-negative integer quantity (a potential) that strictly decreases (or increases toward a cap) with every move.
2. Its starting value bounds the number of steps; the floor/ceiling gives termination or a min/max.
3. Hand-simulate 2-3 tiny cases to confirm the monovariant truly moves monotonically each step.
4. For min-steps problems: the monovariant gives a lower bound; build an explicit sequence achieving it for the upper bound. The answer is where they meet.
5. Adversarially try a move that might violate monotonicity; if found, refine the potential.
6. Watch 'at least' vs 'exactly' and inclusive endpoints when reading off the bound.
7. Re-derive the bound by a second framing (e.g., counting argument) and require agreement before committing.
8. Heavy arithmetic: chunk partial sums, re-add in groups of 5.
Output strictly in the demanded format.` }
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
