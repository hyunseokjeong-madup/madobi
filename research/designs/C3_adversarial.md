# Operating manual: Decompose + Adversarial Self-Refutation

Phase A — Solve carefully:
1. Restate the exact quantity asked. Note the required output format and any "exactly/at least/at most".
2. List every given constraint, one per line. Flag any wording that is a common trap
   (off-by-one, "exactly" vs "at least", base-rate neglect, inclusive/exclusive bounds,
   whole-word vs substring, distinct vs identical, reduced fraction required).
3. Decompose and solve, writing every intermediate result.

Phase B — Red-team your own answer (assume it is WRONG and try to prove it):
4. Name the single most likely way THIS answer is wrong, then check that specific failure.
5. Re-derive by a fully independent method. Verify with a small/extreme case where the answer is obvious.
6. Recompute any arithmetic from scratch, digit by digit.
7. Confirm the output format is exactly as required (fraction reduced? integer only? one word?).

Commit only after the adversarial pass fails to break the answer. Output exactly the required format.
