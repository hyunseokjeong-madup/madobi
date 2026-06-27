export const meta = {
  name: `finals`,
  description: `swarm eval: 12 designs x 20 problems x 1 trials`,
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
  { name: `F01_decomp_b`, manual: `1. Identify the asked quantity and required output format.
2. METHOD A: break into parts, compute each with care (chunked sums of 5, digit-by-digit products).
3. METHOD B: re-derive the SAME answer differently — reorder terms, use a formula vs direct count, or complementary counting.
4. Compare A and B. If they disagree, locate the diverging part, recompute only it, repeat until they match.
5. For probabilities/fractions: count numerator and denominator separately; reduce by GCD; confirm the format (reduced a/b).
6. Flag classic traps before finalizing: base-rate (build a small Bayes table), 'exactly' vs 'at least', endpoints.
7. Output only the value in the exact required format.` },
  { name: `F02_verify_bayes_table`, manual: `1. Spot base-rate/conditional problems. Pre-flag: the prior is NOT the answer.
2. METHOD A (formula): write Bayes explicitly, P(H|E)=P(E|H)P(H)/P(E); compute P(E) via total probability.
3. METHOD B (counts): imagine a concrete population (e.g. 10,000). Fill a 2x2 table of true/false x positive/negative using the given rates. Read the answer directly off the table cells.
4. The two answers must match. If not, recheck which rate is conditional on which.
5. Keep numerator and denominator as integers; reduce by GCD; confirm requested format (decimal vs reduced fraction).
6. Re-add column/row totals in groups of 5 to verify the table is internally consistent.
7. Output exactly the required format, nothing more.` },
  { name: `F11_metacog_b`, manual: `1. Identify what is asked and the exact output format. Note any trap words ('exactly', 'at least', 'distinct', 'strictly', 'reduced').
2. Produce a first answer.
3. Assign a confidence 0-100 and write one sentence justifying it.
4. If confidence >=85: do a single sanity check (units, parity, rough magnitude, boundary) then finish.
5. If confidence <85: re-derive by a genuinely DIFFERENT method. For arithmetic-heavy work, recompute digit-by-digit and group additions in fives. Continue until two independent methods agree.
6. Adversarially attack your answer: 'Here is why this is wrong...' If the attack succeeds, fix it.
7. Recompute confidence. Only output when >=90.
8. Emit the answer in EXACTLY the required format; reduce fractions, confirm integer-only if demanded.` },
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
  { name: `F01_decomp_d`, manual: `1. PLAN phase (no arithmetic yet): list the exact sequence of operations needed and the final format. Freeze this plan.
2. EXECUTE phase: perform one planned block at a time. Within a block, show intermediate digits/terms.
3. Sums: chunk into fives, subtotal, then total. Products: digit-by-digit with aligned place value.
4. After finishing a block, VERIFY it alone — recompute by reverse operation (subtract back, divide back). Fix before proceeding.
5. Watch traps flagged in the plan: 'exactly' vs 'at least', whole-word vs substring, distinct vs identical.
6. For fractions: separate numerator/denominator counts, reduce by GCD, confirm reduced form.
7. Re-read required format; output only that.` },
  { name: `F03_adversarial_c`, manual: `Roleplay two adversaries on your draft answer.
1. Solve once to get a DRAFT.
2. PROSECUTOR: argue the draft is wrong. Cite the most damaging concrete flaw — a specific miscount, an arithmetic line, a misread constraint, a boundary case. Be ruthless; find the strongest objection, not a weak one.
3. DEFENDER: respond to the prosecutor's exact charge by re-deriving that piece independently (different method if possible).
4. JUDGE: if defender's independent re-derivation disagrees with the draft, the draft loses — adopt the corrected value. If they agree, draft survives.
5. Repeat the debate once on the surviving answer only if the first round changed anything.
6. Re-read the output contract; emit exactly that token.` },
  { name: `C0_baseline`, manual: `No operating manual. Solve the problem directly and give the final answer in the required format.` },
  { name: `C2_selfverify`, manual: `# Decompose + Independent Self-Verification
Phase A: restate, list constraints, decompose, produce a candidate answer.
Phase B (mandatory, DIFFERENT method): re-derive by an independent route (complementary count, plug back into constraints, different formula, small base case). If methods disagree, find the error and redo. Check sign/magnitude/units/format. Commit only when an independent check agrees.` }
];
const PROBLEMS = [
  { pid: `P1`, prompt: `5000 미만의 소수(prime) 중에서 7로 나눈 나머지가 3인 것들을 모두 더한 값은?`, format: `정수 하나만 출력` },
  { pid: `P2`, prompt: `공정한 6면체 주사위 4개를 동시에 굴린다. '정확히 세 개'의 주사위 눈이 서로 같을 (나머지 한 개는 다른 값) 확률을 기약분수로 구하라.`, format: `기약분수 a/b 형식 (예: 5/18)` },
  { pid: `P3`, prompt: `왼쪽부터 1~5번 위치에 집 5채가 있다. 각 집은 색(red,green,blue,yellow,white), 음료(tea,coffee,milk,juice,water), 애완동물(dog,cat,bird,fish,horse)이 모두 서로 다르다. 단서: (1) green 집은 red 집 바로 오른쪽이다. (2) blue 집은 1번이다. (3) milk는 3번 집이 마신다. (4) coffee는 green 집이 마신다. (5) white 집은 tea를 마신다. (6) dog는 red 집에 있다. (7) cat은 fish 집 바로 오른쪽이다. (8) bird 주인은 coffee를 마신다. (9) yellow 집은 2번이다. (10) horse는 5번 집에 있다. 질문: fish를 키우는 집의 '색'은 무엇인가?`, format: `색 이름 영어 소문자 단어 하나 (예: red)` },
  { pid: `P4`, prompt: `함수 f(n)은 n이 짝수면 n/2, 홀수면 3n+1 이다. 어떤 양의 정수 n에서 시작해 f를 반복 적용하여 1에 도달할 때까지의 적용 횟수를 steps(n)이라 하자(steps(1)=0). n=1부터 200까지의 steps(n)을 모두 더한 값은?`, format: `정수 하나만 출력` },
  { pid: `P5`, prompt: `다음 문단에서 정확히 'results'라는 단어(소문자, 단어 단위)가 몇 번 나오는지 세어라. 문단: "The strategy meeting started at eleven, and the team reviewed the quarterly results, the regional results, and the preliminary results before agreeing that the results were better than the last results."`, format: `정수 하나만 출력` },
  { pid: `P6`, prompt: `어떤 병의 유병률은 1000명 중 1명이다. 검사의 민감도(sensitivity)는 99%, 특이도(specificity)는 95%다. 무작위로 검사한 사람이 '양성'이 나왔을 때 실제로 그 병에 걸렸을 확률을 기약분수로 구하라.`, format: `기약분수 a/b 형식` },
  { pid: `P7`, prompt: `물건 8개의 (무게,가치)는 다음과 같다: (2,3),(3,4),(4,5),(5,6),(9,10),(7,8),(1,1),(6,7). 배낭 용량(무게 합 한도)은 15다. 각 물건은 0개 또는 1개만 담을 수 있다. 담을 수 있는 최대 가치 합은?`, format: `정수 하나만 출력` },
  { pid: `P8`, prompt: `다음 괄호 문자열의 최대 중첩 깊이(maximum nesting depth)를 구하라: (()((())())(()))(())((((()))))`, format: `정수 하나만 출력` },
  { pid: `P9`, prompt: `수조에 파이프 A는 6시간 만에 가득 채우고, B는 8시간 만에 채운다. 배수구 C는 가득 찬 수조를 12시간 만에 비운다. 빈 수조에서 A,B,C를 동시에 열면 수조가 가득 차는 데 걸리는 시간(시간 단위)을 기약분수로 구하라.`, format: `기약분수 a/b 형식 (정수면 a/1)` },
  { pid: `P10`, prompt: `단어 'MISSISSIPPI'의 글자들을 일렬로 배열하는 서로 다른 경우의 수는?`, format: `정수 하나만 출력` },
  { pid: `P11`, prompt: `1부터 100000까지의 정수 중에서 30과 서로소(coprime, 최대공약수가 1)인 정수의 개수는?`, format: `정수 하나만 출력` },
  { pid: `P12`, prompt: `공정한 6면체 주사위 2개를 굴렸더니 눈의 합이 짝수였다. 이 조건에서 눈의 합이 8 이상일 조건부확률을 기약분수로 구하라.`, format: `기약분수 a/b 형식` },
  { pid: `P13`, prompt: `A,B,C,D 네 사람이 1~4번 자리에 일렬로 선다. 조건: (1) A는 1번이 아니다. (2) B 바로 뒤(오른쪽)에 C가 선다. (3) D는 4번(맨 뒤)이다. 1번 자리에 서는 사람은 누구인가?`, format: `사람 이름 한 글자 (A/B/C/D)` },
  { pid: `P14`, prompt: `2의 200제곱(2^200)을 10진수로 적었을 때, 모든 자릿수의 숫자를 더한 값은?`, format: `정수 하나만 출력` },
  { pid: `P15`, prompt: `다음 문장에서 정확히 5글자(영문자 5개)로 이루어진 단어의 개수를 세어라. 문장: "Seven brave miners found three large rocks below their dusty rural camp after seven hours of steady labor under bright skies near a small green river"`, format: `정수 하나만 출력` },
  { pid: `P16`, prompt: `어떤 가정에 아이가 둘 있다. 각 아이가 남(B)/녀(G)일 확률은 동일하고 독립이다. '적어도 한 명은 남자아이'라는 사실이 주어졌을 때, 두 아이가 모두 남자아이일 조건부확률을 기약분수로 구하라.`, format: `기약분수 a/b 형식` },
  { pid: `P17`, prompt: `다음 수열에서 '엄격히 증가하는' 가장 긴 부분수열(연속일 필요 없음)의 길이를 구하라: 3,1,4,1,5,9,2,6,5,3,5,8,9,7,9,3,2,3,8,4,6,2,6`, format: `정수 하나만 출력` },
  { pid: `P18`, prompt: `두 문자열 'intention'과 'execution' 사이의 최소 편집 거리(Levenshtein distance; 한 글자 삽입/삭제/교체를 1로 센다)를 구하라.`, format: `정수 하나만 출력` },
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
