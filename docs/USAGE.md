# Usage Guide

A practical guide to running **MADOBI** — the agents, the marketing skill, the chat REPL,
the reconciliation engine, and the evolutionary optimization loop.

---

## 1. Using the agents in Claude Code

The agents live in `.claude/agents/` and auto-load when Claude Code runs in this repo.

### `smartest` — general swarm orchestrator
Best for hard reasoning/analysis/implementation where **robustness** matters. It decomposes a task
into a **parallel Solver swarm** (diverse strategies) → **Verifier swarm** (adversarial cross-check)
→ **Synthesizer** (verified majority).

### `madobi` — marketing specialist
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

1. **Restore context** — `recall.py` searches the 213-asset knowledge base (no full read) + the account memory.
2. **Reconcile** — recompute every derived metric from raw, check breakdown sums = totals.
3. **Report** — verified numbers only; inconsistencies surfaced as ⚠, never hidden.
4. **Record** — promote verified learnings to the knowledge assets (`curate.py`, dedup-aware; compounding).

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

## 3.5 Searchable memory & extra verification (stdlib, zero deps)

**Searchable knowledge (FTS5 full-text recall)** — the 213 knowledge assets are indexed, not bulk-read:
```bash
python marketing/knowledge/search.py --build                 # build/refresh the index (~1s)
python marketing/knowledge/search.py 'ROAS high CPA' --category diagnostics --limit 5
python marketing/knowledge/recall.py --account demo_ecommerce --query 'weekend CPA' --limit 5
```
SQLite FTS5 + bm25 ranking. No external deps; degrades to a stdlib grep fallback if the index is absent.

**Dedup-aware learning** — append a lesson without duplicating an existing one:
```bash
python marketing/knowledge/curate.py --upsert marketing/knowledge/<account>.md --tag report --feedback '...'
python marketing/knowledge/curate.py --onboard <account> --vertical ecommerce --baseline 'CTR 1.2%, ROAS 3.5x'
```
Same feedback → its date is refreshed ("재검증"), not appended twice.

**Extra verification layers:**
```bash
python marketing/sql_query.py marketing/samples/sample_campaign.csv --group-by creative --metric roas   # DuckDB↔Python triple-verify (opt-in; group-by an existing column)
python -c "import sys; sys.path.insert(0,'marketing'); import safemath; print(safemath.safe_div(10,0))"  # 0/0·inf guards
```
`sql_query.py` runs DuckDB (if installed) **and** the pure-python path, passing only if they agree —
python is the source of truth on mismatch. Without DuckDB it transparently uses python alone.

**End-to-end demo** — the whole flow on one campaign CSV:
```bash
python marketing/demo_e2e.py marketing/samples/sample_campaign.csv --account demo_ecommerce
python marketing/demo_e2e.py --selftest          # non-interactive (exit 0/1)
```
recall → reconcile → summarize (TOTAL-row excluded) → triple-verify → consistency verdict.

---

## 3.6 Chat mode (deterministic REPL — no LLM calls)

Talk to MADOBI straight from the terminal. Routing is **deterministic**: same question → same answer.

```bash
python marketing/madobi.py chat                    # interactive REPL (매도비> )
python marketing/chat.py --ask "숫자 검산해줘"        # one-shot (for scripts/agents)
```

What it understands:
- **Metric Q&A** — "ROAS가 뭐야?" → definition/formula/SQL straight from the semantic layer glossary.
- **Tool routing** — Korean/English intent ("검산", "예산 재배분", "이탈 위험", …) → best of 89 tools,
  with a **verified, runnable command** (example args are reused from `tests/run_all.py`, never duplicated).
- **Knowledge recall** — "지난번에 배운 교훈?" → delegates to `knowledge/recall.py`.
- In the REPL, `run` (or `run 2`) executes the last suggestion; `list` shows every tool.

---

## 4. Running the optimization yourself

```bash
cd research    # everything below lives in research/

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
- Add marketing knowledge to `marketing/knowledge/<account>.md` — it compounds across sessions
  (use `curate.py --upsert` to avoid duplicates; `search.py --build` to re-index for recall).
