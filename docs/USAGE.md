# Usage Guide

A practical guide to running **Swarm Agent Lab** — the agents, the marketing skill,
the reconciliation engine, and the evolutionary optimization loop.

---

## 1. Using the agents in Claude Code

The agents live in `.claude/agents/` and auto-load when Claude Code runs in this repo.

### `smartest` — general swarm orchestrator
Best for hard reasoning/analysis/implementation where **robustness** matters. It decomposes a task
into a **parallel Solver swarm** (diverse strategies) → **Verifier swarm** (adversarial cross-check)
→ **Synthesizer** (verified majority).

### `madup-marketer` — marketing specialist
Best for ad performance analysis, spreadsheet summaries, campaign/event analysis, and the
creative lifecycle. Its prime directive: **never report a number that hasn't been reconciled.**

Invoke implicitly by asking, e.g.:
> "Summarize this campaign CSV and check the numbers."
> "Which creatives are winners? Watch for fatigue."
> "Plan 3 hook variations for a 15s video, then QA them."

---

## 2. The `marketing-analyst` skill

`.claude/skills/marketing-analyst/SKILL.md` packages the routine workflow so the agent runs it
the same way every time:

1. **Restore context** — read `marketing/knowledge/<account>.md` + recent `history/`.
2. **Reconcile** — recompute every derived metric from raw, check breakdown sums = totals.
3. **Report** — verified numbers only; inconsistencies surfaced as ⚠, never hidden.
4. **Record** — promote verified learnings to the knowledge assets (compounding).

---

## 3. The reconciliation engine

```bash
python marketing/reconcile.py <your_data.csv> [--tol 0.01]
```

Checks performed:
- Per-row derived metrics (CTR/CPC/CPM/CPA/ROAS) recomputed from raw vs reported.
- Breakdown rows sum to the TOTAL row.
- Ratio metrics use **weighted** averaging (catches the Simpson trap).
- Unit/format normalization (commas, %, currency, blanks).

Column names are matched flexibly (English + Korean aliases: `impressions/노출`, `spend/비용/광고비`, …).

---

## 4. Running the optimization yourself

```bash
# 1) Build the code-verified benchmark
python benchmark/build_benchmark.py

# 2) Generate a self-contained evaluation workflow (LF-only, ASCII — permission-hook safe)
python make_eval_script.py \
  --designs results/finalists.json --pids all --trials 1 \
  --name finals --out results/finals.js

# 3) Run results/finals.js via the Claude Code Workflow tool (background swarm)

# 4) Merge shards, majority-vote, rank
python merge_and_rank.py --pids all results/<run>.output

# 5) Track fitness across generations
python track.py
```

### Operational lessons (baked in)
- **`args` arrives as a string** in workflow scripts → `JSON.parse(args)`.
- **CRLF breaks the approval hook** → write scripts with `newline="\n"` (LF only).
- **1000-agent cap per workflow** → shard large runs.
- **Keep concurrent workflows to 1–2** → avoid server rate limits.

---

## 5. Extending

- Add benchmark problems in `benchmark/build_benchmark.py` (compute the ground truth in code).
- Add a strategy family in `gen_designs.js` and regenerate the population.
- Add marketing knowledge to `marketing/knowledge/<account>.md` — it compounds across sessions.
