export const meta = {
  name: 'design-generation-swarm',
  description: 'Designer swarm generates ~100 diverse closed-book reasoning operating-manuals across 14 strategy families',
  phases: [{ title: 'Generate', detail: '14 family-generators x 8 manuals' }],
}

const MANUAL_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    manuals: {
      type: 'array',
      minItems: 6,
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          name: { type: 'string', description: 'short unique slug, e.g. verify_two_method' },
          strategy: { type: 'string', description: 'one-line strategy summary' },
          manual: { type: 'string', description: 'the operating manual / meta-prompt, concise and concrete (<170 words)' },
        },
        required: ['name', 'strategy', 'manual'],
      },
    },
  },
  required: ['manuals'],
}

const KNOWHOW = [
  'Naive decomposition INCREASES arithmetic error on heavy sums/iterations (Gen1: prime-sum, Collatz-sum got worse). Always pair decomposition with computation hygiene: chunked partial sums, digit-by-digit, re-add in groups of 5.',
  'Independent self-verification (re-derive by a DIFFERENT method until two agree) and adversarial self-refutation reliably fix mistakes with little downside. Keep verification concise so short problems are not over-thought.',
  'Pre-flag classic traps: base-rate (Bayes table), "exactly" vs "at least", whole-word vs substring, strictly-increasing, distinct vs identical, reduced-fraction-required, inclusive/exclusive bounds.',
  'For probability/fractions: count numerator and denominator separately, then reduce by GCD and confirm format.',
  'Self-consistency: produce multiple independent attempts and take the majority — raises accuracy on high-variance problems.',
  'Output-contract discipline: re-read the required format and emit EXACTLY it (integer only / reduced a/b / one lowercase word).',
]

const FAMILIES = [
  { key: 'F01_decomp', desc: 'Structured decomposition WITH built-in computation hygiene (chunked sums, digit-by-digit, recheck partial totals). Must avoid the naive-decomposition arithmetic pitfall.' },
  { key: 'F02_verify', desc: 'Independent self-verification: solve, then re-derive by a genuinely different method; reconcile until two methods agree.' },
  { key: 'F03_adversarial', desc: 'Adversarial self-refutation: assume your answer is wrong, name the most likely failure, attack it, recompute.' },
  { key: 'F04_trapcheck', desc: 'Trap-taxonomy checklist: explicitly scan for known traps (base-rate, exactly/at-least, whole-word, strict-increase, distinct, reduced fraction) before answering.' },
  { key: 'F05_constraint', desc: 'Constraint propagation & systematic search for logic/combinatorics: fill a grid, propagate forced cells, enumerate the small remaining space.' },
  { key: 'F06_comphygiene', desc: 'Computation hygiene specialist: tabulate, compute digit-by-digit, sum in groups, double-add, sanity-bound magnitudes.' },
  { key: 'F07_estimate', desc: 'Estimate-then-verify: first bound/estimate the answer, then compute exactly and check it falls within the bound.' },
  { key: 'F08_reduce', desc: 'Reduce-to-known-problem: map the task to a standard problem/formula (Bayes, inclusion-exclusion, DP, Euler totient) and apply it carefully.' },
  { key: 'F09_firstprin', desc: 'First-principles: write exact definitions of every term, derive from definitions, avoid pattern-matching shortcuts.' },
  { key: 'F10_dualprocess', desc: 'Dual-process: record a fast intuitive guess, then run a slow deliberate audit; only trust the intuition if the audit confirms it.' },
  { key: 'F11_metacog', desc: 'Metacognitive calibration: state assumptions, ask "what single thing would make this wrong?", check that thing, report only when confident.' },
  { key: 'F12_swarmteam', desc: 'Swarm/team orchestration (in-head): simulate 3 independent sub-solvers using different strategies, a verifier that cross-checks them, and a synthesizer that takes the verified majority. This mirrors a parallel team.' },
  { key: 'F13_formatdiscipline', desc: 'Format & precision discipline: treat the output format as a strict contract; reduce fractions, integers only, exact word; never add prose.' },
  { key: 'F14_invariants', desc: 'Case-enumeration & invariants: test tiny base cases, exploit parity/symmetry/invariants, then generalize; verify on an extreme case.' },
]

const PER_FAMILY = 8

phase('Generate')
const tasks = FAMILIES.map(fam => () =>
  agent(
    'You are a DESIGNER in a swarm-optimization team. Your job: invent operating manuals (meta-prompts) that, when prepended to a problem, maximize an LLM\'s CLOSED-BOOK reasoning accuracy on hard math / logic / counting / probability / algorithm problems (no tools, no code execution).\n\n' +
    'STRATEGY FAMILY for you: ' + fam.key + ' — ' + fam.desc + '\n\n' +
    'Produce ' + PER_FAMILY + ' DISTINCT manuals within this family. Vary the concrete tactics, ordering, and emphasis so they are genuinely different candidates (not paraphrases).\n' +
    'Each manual: concrete, actionable, <170 words, numbered steps where useful, NO fluff. It must be self-contained operating instructions for the solver.\n\n' +
    'Apply these empirically-derived principles where relevant:\n- ' + KNOWHOW.join('\n- ') + '\n\n' +
    'Return the manuals. Use short unique slug names prefixed with ' + fam.key + '_ (e.g. ' + fam.key + '_a).',
    { label: 'design:' + fam.key, phase: 'Generate', schema: MANUAL_SCHEMA }
  ).then(r => (r && r.manuals ? r.manuals.map((m, i) => ({
    family: fam.key,
    name: (m.name && m.name.startsWith(fam.key)) ? m.name : (fam.key + '_' + (i + 1)),
    strategy: m.strategy || '',
    manual: m.manual,
  })) : []))
)

const groups = await parallel(tasks)
const flat = groups.filter(Boolean).flat()
// ensure unique names
const seen = {}
for (const d of flat) {
  let nm = d.name
  while (seen[nm]) nm = nm + 'x'
  seen[nm] = 1
  d.name = nm
}
log('generated ' + flat.length + ' manuals across ' + FAMILIES.length + ' families')
return flat
