export const meta = {
  name: 'swarm-eval-gen1',
  description: 'Closed-book swarm evaluation of agent operating-manual designs over a verified benchmark',
  phases: [{ title: 'Evaluate', detail: 'design x problem closed-book reasoning nodes' }],
}

const ANSWER_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: { answer: { type: 'string', description: 'ONLY the final answer in the exact required format (integer, reduced fraction a/b, or one lowercase word)' } },
  required: ['answer'],
}

const DESIGNS = [
  { name: 'C0_baseline', manual: `No operating manual. Solve the problem directly and give the final answer in the required format.` },
  { name: 'C1_decompose', manual: `# Operating manual: Structured Decomposition
Before answering, work in explicit steps:
1. Restate the problem and identify exactly what is asked.
2. List the given facts and constraints, one per line.
3. Break into the smallest sub-steps, each producing an intermediate result.
4. Solve each sub-step in order, writing the intermediate result.
5. Combine intermediates into the final answer.
6. Re-read the required output format and produce exactly that.
Be careful and methodical. Do not skip steps. Do not round unless asked.` },
  { name: 'C2_selfverify', manual: `# Operating manual: Decompose + Independent Self-Verification
Phase A - Solve:
1. Restate what is asked and list all constraints.
2. Decompose into sub-steps; solve each, writing intermediates.
3. Produce a candidate answer.
Phase B - Verify (MANDATORY, use a DIFFERENT method than Phase A):
4. Re-derive by an independent route (count complementary case, plug answer back into constraints, use a different formula, or check a small base case).
5. If the two methods disagree, find the error and redo until they agree.
6. Check sanity bounds (sign, magnitude, units, format).
Commit only once an independent check agrees. Output exactly the required format.` },
  { name: 'C3_adversarial', manual: `# Operating manual: Decompose + Adversarial Self-Refutation
Phase A - Solve carefully:
1. Restate the exact quantity asked. Note required format and any 'exactly/at least/at most'.
2. List every constraint, one per line. Flag common traps (off-by-one, 'exactly' vs 'at least', base-rate neglect, inclusive/exclusive bounds, whole-word vs substring, distinct vs identical, reduced fraction required).
3. Decompose and solve, writing every intermediate result.
Phase B - Red-team your own answer (assume it is WRONG and try to prove it):
4. Name the single most likely way THIS answer is wrong, then check that failure.
5. Re-derive by a fully independent method. Verify with a small/extreme case.
6. Recompute any arithmetic from scratch, digit by digit.
7. Confirm output format is exactly as required.
Commit only after the adversarial pass fails to break the answer. Output exactly the required format.` },
]

const PROBLEMS = [
  { pid: 'P1', format: '정수 하나만 출력', prompt: `5000 미만의 소수(prime) 중에서 7로 나눈 나머지가 3인 것들을 모두 더한 값은?` },
  { pid: 'P2', format: '기약분수 a/b 형식 (예: 5/18)', prompt: `공정한 6면체 주사위 4개를 동시에 굴린다. '정확히 세 개'의 주사위 눈이 서로 같을 (나머지 한 개는 다른 값) 확률을 기약분수로 구하라.` },
  { pid: 'P3', format: '색 이름 영어 소문자 단어 하나 (예: red)', prompt: `왼쪽부터 1~5번 위치에 집 5채가 있다. 각 집은 색(red,green,blue,yellow,white), 음료(tea,coffee,milk,juice,water), 애완동물(dog,cat,bird,fish,horse)이 모두 서로 다르다. 단서: (1) green 집은 red 집 바로 오른쪽이다. (2) blue 집은 1번이다. (3) milk는 3번 집이 마신다. (4) coffee는 green 집이 마신다. (5) white 집은 tea를 마신다. (6) dog는 red 집에 있다. (7) cat은 fish 집 바로 오른쪽이다. (8) bird 주인은 coffee를 마신다. (9) yellow 집은 2번이다. (10) horse는 5번 집에 있다. 질문: fish를 키우는 집의 '색'은 무엇인가?` },
  { pid: 'P4', format: '정수 하나만 출력', prompt: `함수 f(n)은 n이 짝수면 n/2, 홀수면 3n+1 이다. 어떤 양의 정수 n에서 시작해 f를 반복 적용하여 1에 도달할 때까지의 적용 횟수를 steps(n)이라 하자(steps(1)=0). n=1부터 200까지의 steps(n)을 모두 더한 값은?` },
  { pid: 'P5', format: '정수 하나만 출력', prompt: `다음 문단에서 정확히 'results'라는 단어(소문자, 단어 단위)가 몇 번 나오는지 세어라. 문단: "The strategy meeting started at eleven, and the team reviewed the quarterly results, the regional results, and the preliminary results before agreeing that the results were better than the last results."` },
  { pid: 'P6', format: '기약분수 a/b 형식', prompt: `어떤 병의 유병률은 1000명 중 1명이다. 검사의 민감도(sensitivity)는 99%, 특이도(specificity)는 95%다. 무작위로 검사한 사람이 '양성'이 나왔을 때 실제로 그 병에 걸렸을 확률을 기약분수로 구하라.` },
  { pid: 'P7', format: '정수 하나만 출력', prompt: `물건 8개의 (무게,가치)는 다음과 같다: (2,3),(3,4),(4,5),(5,6),(9,10),(7,8),(1,1),(6,7). 배낭 용량(무게 합 한도)은 15다. 각 물건은 0개 또는 1개만 담을 수 있다. 담을 수 있는 최대 가치 합은?` },
  { pid: 'P8', format: '정수 하나만 출력', prompt: `다음 괄호 문자열의 최대 중첩 깊이(maximum nesting depth)를 구하라: (()((())())(()))(())((((()))))` },
  { pid: 'P9', format: '기약분수 a/b 형식 (정수면 a/1)', prompt: `수조에 파이프 A는 6시간 만에 가득 채우고, B는 8시간 만에 채운다. 배수구 C는 가득 찬 수조를 12시간 만에 비운다. 빈 수조에서 A,B,C를 동시에 열면 수조가 가득 차는 데 걸리는 시간(시간 단위)을 기약분수로 구하라.` },
  { pid: 'P10', format: '정수 하나만 출력', prompt: `단어 'MISSISSIPPI'의 글자들을 일렬로 배열하는 서로 다른 경우의 수는?` },
]

phase('Evaluate')
const tasks = []
for (const d of DESIGNS) {
  for (const p of PROBLEMS) {
    tasks.push(() =>
      agent(
        'You are taking a CLOSED-BOOK reasoning exam.\n' +
        'STRICT RULES: do NOT use any tools, do NOT execute code, do NOT call Bash or python or any calculator. Reason entirely on your own.\n\n' +
        '=== OPERATING MANUAL (follow it exactly) ===\n' + d.manual + '\n\n' +
        '=== PROBLEM (' + p.pid + ') ===\n' + p.prompt + '\n\n' +
        '=== REQUIRED OUTPUT FORMAT ===\n' + p.format + '\n\n' +
        'Think carefully step by step in your reasoning. Then output ONLY the final answer in exactly the required format.',
        { label: d.name + ':' + p.pid, phase: 'Evaluate', schema: ANSWER_SCHEMA }
      ).then(r => ({ design: d.name, pid: p.pid, answer: r ? r.answer : null }))
    )
  }
}
const rows = await parallel(tasks)
log('collected ' + rows.filter(Boolean).length + ' answers')
return rows.filter(Boolean)
