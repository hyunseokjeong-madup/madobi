<div align="center">

<img src="assets/logo.svg" alt="MADOBI" width="680">

# MADOBI · 매도비

**매드업이 만드는 마케팅 특화 AI 에이전트 — 산술은 코드가 보장하고, 통찰은 LLM이 판단한다.**

*검증된 수학 × 사람의 판단 — 스웜 최적화로 선별된 검증-우선 전략 · 정합성 검산 · 소재 분석 · 쓸수록 자라는 놀리지에셋*

`진화적 스웜 최적화` · `Doer–Verifier 검증` · `마케팅 애널리틱스`

![license](https://img.shields.io/badge/license-MIT-green)
![checks](https://img.shields.io/badge/integration%20checks-passing-brightgreen)
![tools](https://img.shields.io/badge/pm%20tools-79-7c83ff)
![tests](https://img.shields.io/badge/integration-95%2F95%20green-brightgreen)
![numbers](https://img.shields.io/badge/aggregation-100k%20rows%20exact-6ee7ff)
![made by](https://img.shields.io/badge/made%20by-Madup-7c83ff)
![built with](https://img.shields.io/badge/built%20with-Claude%20Code-b072ff)

</div>

---

> 📌 이 README는 **계속 업데이트되는 살아있는 문서**입니다. 새 기능·개선·교훈은 전부 여기 반영됩니다.
> 🌐 한국어가 기본입니다. 영어는 맨 아래 [English](#-english) 접이식 섹션에 있습니다.

## 🎯 MADOBI가 뭔가요?

대부분의 "에이전트"는 **손으로 쓴** 시스템 프롬프트를 그냥 씁니다. MADOBI는 다릅니다 — **측정으로** 최고 전략을 찾았습니다.

1. **Designer 스웜**이 14개 전략 계열에서 **112개 운영 매뉴얼**을 생성
2. 각각을 **코드로 정답이 검증된 벤치마크**(20문항, LLM 채점 없음)로 평가
3. **4세대 진화 토너먼트**(스크리닝 → 결선 → 결정전)로 챔피언 선발
4. 승자 전략을 **에이전트 + 스킬**로 패키징하고, **마케팅 분석**에 특화 — 숫자를 *맞히는* 게 전부인 영역

> **핵심 결과:** 승리 전략(**검증 우선**) + **다수결**은 *코드로 정답이 검증된 산술 벤치마크에서 무실점*에 도달합니다.
> 이것이 일반 에이전트가 스프레드/캠페인 분석에서 "숫자를 틀리는" 실패 모드를 정면으로 해결합니다.
>
> **분업이 핵심입니다 — 산술은 LLM이 하지 않습니다.** 합계·ROAS·CTR·CVR·CPA 같은 계산은
> **결정론적 파이썬 코드**(`reconcile.py`·`summarize.py`·`pm/`의 79개 도구)가 수행하고 교차검증합니다.
> LLM은 *무엇을 계산할지 고르고, 결과를 해석·설명·보고*합니다. 그래서 신뢰의 근거가 "AI가 똑똑해서"가
> 아니라 **"계산을 코드가 보증해서"** 입니다 — 검증 가능하고, 재현 가능하고, 감사 가능합니다.

## 🏆 핵심 성과

| 단계 | 내용 | 결과 |
|------|------|------|
| Gen 1 | 시드 4종 × 10문항 | 순수 분해는 무거운 산술에 **해롭다**, 검증이 **고친다** |
| Gen 2 | **112 설계** × 어려운 문항 (5팀 병렬) | 검증 계열 압도, 만점 13종 |
| Gen 3 | 결선: 12 finalist × 20문항 | **4종이 20/20** |
| Gen 4 | 결정전: 4 챔피언 × 오류多 추론셋 × 5시행 | 챔피언 **`F03_adversarial_c`** (단일샷 29/30 = 96.7%); 선별 6문항 **다수결 → 6/6** |

**승리 레시피:** `분해 → 독립 자기검증 → 적대적 반박 → 다수결`

## 🤖 에이전트 & 스킬

| 구성 | 역할 |
|------|------|
| [`madobi`](.claude/agents/madobi.md) | **마케팅 특화** — 숫자 정합성, 소재 기획/생성/점검, 성장형 메모리 |
| [`smartest`](.claude/agents/smartest.md) | 범용 스웜 오케스트레이터 (병렬 Solver → Verifier → Synthesizer) |
| [`marketing-analyst` 스킬](.claude/skills/marketing-analyst/SKILL.md) | 루틴 마케팅 업무 자동화(요약/분석/소재) |

## ⚡ 클로드(Claude Code)에서 바로 쓰기

`.claude/` 아래의 에이전트·스킬은 **클로드 코드가 자동 로드**합니다 — 설치 단계 없음:

```bash
git clone https://github.com/hyunseokjeong-madup/madobi
cd madobi
claude       # madobi / smartest 에이전트 + marketing-analyst 스킬이 바로 활성화
```

다른 프로젝트에서 쓰려면 폴더만 복사:
```bash
cp -r .claude/agents/*  <프로젝트>/.claude/agents/
cp -r .claude/skills/*  <프로젝트>/.claude/skills/
cp -r marketing/        <프로젝트>/
```
그다음 그냥 요청하면 됩니다: **"이 캠페인 CSV 요약하고 숫자 검산해줘"** → 보고 전에 정합성 검산을 먼저 합니다.

**작동 방식(자동 라우팅):** 사용자가 자연어로 요청하면, 스킬/에이전트의 `description`을 보고 클로드가
**알아서 적절한 기능으로 라우팅**합니다 (사용자 판단 아래에서). 마케팅/스프레드/소재 → `marketing-analyst`,
어려운 추론 → `smartest`. 개선을 말하면 `learn.py`가 **놀리지에셋에 학습 + 깃 자동 커밋·푸시**합니다.

## 🔢 집계 벤치마크 — "대규모에서도 안 틀린다"

크고, 필드 많고, 지저분한 데이터에서 숫자를 맞히는 게 진짜 어렵습니다. 그래서 증명합니다:

- `marketing/bench/`가 **10만 행 × 13필드**(콤마·₩·혼합 포맷) 데이터와 **코드로 계산한 정답**을 만들고,
  **30단계 난이도 사다리**로 집계를 검증 — 단일·**멀티 피벗(말도 안 되는 4중 피벗 225그룹 포함)**,
  필터, top-N, having, 주간 롤업, share-of, 파생의 파생. 각 레벨은 **두 가지 독립 방법 + 재합산 불변식**으로 교차검증.

```text
$ python marketing/bench/gen_dataset.py --rows 100000 && python marketing/bench/levels.py
=== GRADED BENCHMARK: 29/29 levels PASS ===
✅ ALL LEVELS PASS — 멀티피벗/필터/top-N/4D 피벗 전부 정확.
```

**정합성 검산 엔진** (`marketing/reconcile.py`) 실전 예:
```text
$ python marketing/reconcile.py marketing/samples/sample_campaign.csv
-- checks: 16 PASS, 2 WARN --
  ! [C_carousel] ctr: reported=9.9% recomputed=5.0000%      # 보고값과 실제 불일치 적발
  ! [SUM] spend: rows_sum=4,100,000 vs total_row=4,200,000   # 합계 ≠ 총계 적발
VERDICT: 2 INCONSISTENCY(IES) - investigate raw data
```

## 🎯 바로 쓰는 3가지 (MVP)

마케터 입장에서 "리포트 작성 자동화"가 아니라 **"리포트 숫자 사고 방지 장치"** 입니다:

| # | 무엇 | 어떻게 |
|---|------|--------|
| 1 | **CSV → 지표 재계산** | ROAS·CTR·CVR·CPC·CPA·CPM·매출·비용 합계를 원자료에서 코드로 재계산. 눈대중 0. |
| 2 | **보고서 숫자 대조** | "보고서에 적힌 수치" vs "원본 데이터" 불일치를 보고 전에 적발 (`reconcile.py`). |
| 3 | **근거 첨부 코멘트** | 마케팅 코멘트를 생성하되, **각 문장에 근거 수치를 자동 첨부**. |

> SA/DA 운영, 월간 리포트, 광고주 보고, iROAS·CAPI 성과 검산까지 — 데이터 기반 마케팅 운영에 바로 붙습니다.

## ⚖️ 정직한 한계 (무엇을 보장하고, 무엇은 못 하나)

신뢰는 과장이 아니라 정확한 경계에서 나옵니다:

- ✅ **보장**: 코드가 수행하는 **산술의 정확성** — 합계·파생지표·집계·교차검증. 동일 입력 → 동일 출력.
- ⚠️ **보장 못 함**: **데이터 품질** 자체. `reconcile.py`는 *산술 오류*는 잡지만, 채널 오분류·잘못된
  태깅·누락된 전환 같은 *원천 데이터 이슈*는 못 잡습니다. **원본 데이터는 항상 spot-check 하세요.**
- ⚠️ **LLM의 판단 영역**(해석·추천·코멘트)은 결정론이 아닙니다 — 그래서 *근거 수치를 함께* 제시해
  사람이 검증할 수 있게 합니다.

## 🔁 자기개선 루프 (쓸수록 똑똑해짐)

"이건 개선해 / 항상 이렇게 해 / 그거 틀렸어"라고 하면, MADOBI가 **피드백을 학습 → 놀리지에셋에 승격
→ 로그 → 깃 자동 커밋·푸시**(중앙 규칙이면 전체 반영). 레포 자체가 팀의 복리형·버전관리되는 지식이 됩니다.

```bash
python learn.py --feedback "ROAS는 항상 배수(x)로 표기"   # 자동 커밋·푸시 (기본 ON)
```
자세히: [`marketing/LEARNING_LOOP.md`](marketing/LEARNING_LOOP.md)

## 🗂 저장소 구조

```
.claude/agents/   madobi.md, smartest.md          # 제품 에이전트
.claude/skills/   marketing-analyst/SKILL.md      # 루틴 자동화 스킬
.claude/settings.json                             # 자기개선 Stop 훅(autosync)
marketing/        STRATEGY · METRICS · CREATIVE_PLAYBOOK · MEMORY_PROTOCOL · LEARNING_LOOP
                  reconcile.py · summarize · analyze_creatives · pm/(퍼마 도구 79개)
                  knowledge/(214 자산) · bench/(집계+추론 벤치) · samples
learn.py          피드백 → 놀리지에셋 → 깃 (자기개선)
tools/autosync.py 세션 종료 시 놀리지 변경 자동 커밋·푸시
tests/run_all.py  통합 검증 — 모든 결정론적 보장 green (회귀 방지)
docs/             USAGE · DEMO
ROADMAP · CYCLES · SUBSTANTIAL · ADVANTAGES   # 로드맵·진행·경쟁우위
research/         에이전트 선별 실험 아카이브(스웜 최적화) — 제품엔 불필요
```

## 🆚 기존 에이전트(Hermes·Pi) 대비 강점

둘 다 **단일 루프**입니다. MADOBI는 4가지 구조적 우위를 더합니다: **증거기반 전략 · 검증 스웜 견고성
· 병렬 오케스트레이션 · 복리형 놀리지에셋**. 그들의 강점(영속 메모리·스킬 생성·미니멀 코어)은 흡수했습니다.
자세히: [`ADVANTAGES.md`](ADVANTAGES.md)

## 📜 라이선스
MIT — [LICENSE](LICENSE) · Made by **Madup**

---

<details>
<summary>🌐 <b>English</b></summary>

## What is MADOBI?
A marketing-specialized AI agent by **Madup** where **code guarantees the arithmetic and the LLM does the
judgment** — not the other way around. Sums, ROAS, CTR, CVR, CPA and every aggregation are computed and
cross-checked by **deterministic Python** (`reconcile.py`, `summarize.py`, the 79 tools in `pm/`); the LLM
*chooses what to compute and interprets/explains the result*. That is the whole point of the split: **the LLM
does not do the math.** So the basis for trust is not "the AI is smart" but **"the arithmetic is backed by
code"** — verifiable, reproducible, auditable.

Its operating strategy was not hand-written — it was **selected by evolutionary swarm optimization**: a
Designer swarm generated **112 candidate manuals across 14 strategy families**, each scored on a
**code-verified benchmark** (20 items, no LLM grading) across **4 generations** of an evolutionary tournament
(screening → finals → tie-break). Champion strategy = **verification-first**
(`decompose → independent self-verify → adversarial refute → majority vote`), which reaches **perfect accuracy
on the code-verified arithmetic benchmark** — exactly the failure mode behind "wrong numbers" in
spreadsheet/campaign analysis.

## Key results
| Stage | What | Result |
|-------|------|--------|
| Gen 1 | 4 seeds × 10 items | pure decomposition **hurts** on heavy arithmetic; verification **fixes** it |
| Gen 2 | **112 designs** × hard items (5 teams in parallel) | verification family dominates, 13 perfect |
| Gen 3 | finals: 12 finalists × 20 items | **4 score 20/20** |
| Gen 4 | tie-break: 4 champions × error-heavy reasoning set × 5 trials | champion **`F03_adversarial_c`** (29/30 single-shot = 96.7%); 6 selected items with **majority vote → 6/6** |

**Winning recipe:** `decompose → independent self-verify → adversarial refute → majority vote`

## Use it in Claude Code
Agents/skill under `.claude/` **auto-load** — no install step:

```bash
git clone https://github.com/hyunseokjeong-madup/madobi
cd madobi
claude    # madobi / smartest agents + marketing-analyst skill activate immediately
```

Then just ask *"summarize this campaign CSV and check the numbers"* — it **reconciles before reporting**.
Routing is automatic via skill/agent `description`s (under the user's control): marketing/spreadsheet/creative
→ `marketing-analyst`, hard reasoning → `smartest`. Say "improve this / always do X / that's wrong" and
`learn.py` promotes the feedback into a knowledge asset and **auto-commits/pushes to git**.

## The 3 things you use immediately (MVPs)
From a marketer's view this is not "report-writing automation" — it is a **safeguard against wrong numbers in
reports**:

| # | What | How |
|---|------|-----|
| 1 | **CSV → recompute metrics** | ROAS·CTR·CVR·CPC·CPA·CPM·revenue·spend totals recomputed from raw data in code. Zero eyeballing. |
| 2 | **Cross-check report numbers** | Catch mismatches between "what the report claims" and "the source data" **before** it ships (`reconcile.py`). |
| 3 | **Evidence-attached comments** | Generate marketing commentary, but **auto-attach the supporting figure to every sentence**. |

Fits SA/DA operations, monthly reports, advertiser reporting, and iROAS·CAPI performance checks — data-driven
marketing operations out of the box.

## Aggregation benchmark — "still correct at scale"
Getting numbers right on big, many-field, messy data is the hard part, so we prove it: `marketing/bench/`
generates **100k rows × 13 fields** (commas, ₩, mixed formats) with **code-computed ground truth** and a
**30-level difficulty ladder** — single and **multi-pivot (incl. an absurd 4-dimension / 225-group pivot)**,
filters, top-N, having, weekly rollups, share-of, derived-of-derived. Each level is cross-checked by **two
independent methods + a re-sum invariant**.

```text
$ python marketing/bench/gen_dataset.py --rows 100000 && python marketing/bench/levels.py
=== GRADED BENCHMARK: 29/29 levels PASS ===
✅ ALL LEVELS PASS — multi-pivot / filter / top-N / 4D pivot all exact.
```

The **reconciliation engine** (`marketing/reconcile.py`) in action:
```text
$ python marketing/reconcile.py marketing/samples/sample_campaign.csv
-- checks: 16 PASS, 2 WARN --
  ! [C_carousel] ctr: reported=9.9% recomputed=5.0000%      # reported vs actual mismatch caught
  ! [SUM] spend: rows_sum=4,100,000 vs total_row=4,200,000   # sum ≠ grand-total caught
VERDICT: 2 INCONSISTENCY(IES) - investigate raw data
```

## Honest limits (what it guarantees, what it can't)
Trust comes from precise boundaries, not hype:

- ✅ **Guaranteed:** the **correctness of the arithmetic code performs** — sums, derived metrics, aggregations,
  cross-checks. Same input → same output.
- ⚠️ **Not guaranteed:** **data quality** itself. `reconcile.py` catches *arithmetic* errors, but not
  *source-data* issues like channel mis-tagging, wrong tagging, or missing conversions. **Always spot-check
  raw data.**
- ⚠️ The **LLM's judgment** (interpretation, recommendations, commentary) is not deterministic — so it ships
  *with the supporting figures* attached, so a human can verify it.

## Self-improving loop (smarter the more you use it)
Say "improve this / always do it this way / that's wrong" and MADOBI **learns the feedback → promotes it into a
knowledge asset → logs it → auto-commits/pushes to git** (central rules propagate everywhere). The repo itself
becomes the team's compounding, version-controlled knowledge.

```bash
python learn.py --feedback "Always write ROAS as a multiple (x)"   # auto commit/push (ON by default)
```
More: [`marketing/LEARNING_LOOP.md`](marketing/LEARNING_LOOP.md)

## Searchable knowledge (FTS5 full-text recall)
The 214 knowledge assets are searchable via **SQLite FTS5 + bm25 ranking** (`marketing/knowledge/search.py`) —
**still zero external dependencies** (stdlib `sqlite3` only). If a Python build lacks FTS5 it **degrades
gracefully** to an empty result instead of crashing.

```bash
python marketing/knowledge/search.py --build           # (re)build the index
python marketing/knowledge/search.py 'ROAS high CPA'   # bm25-ranked recall, with snippets
```

## DuckDB-coexistence verify layer
`marketing/sql_query.py` adds an **optional** DuckDB path for fast SQL `GROUP BY` aggregation on large CSV /
parquet, with a **stdlib `csv` fallback** when DuckDB is absent (the module still imports and runs either way,
so the zero-dependency core is preserved). Crucially, **DuckDB is only an extra cross-checker — on any
mismatch, the deterministic Python path is the source of truth.**

## Why stronger than Hermes / Pi (single-loop agents)
Both are **single-loop**. MADOBI adds four structural edges: **evidence-based strategy · verification-swarm
robustness · parallel orchestration · compounding knowledge** — while absorbing their strengths (persistent
memory, skill generation, minimal core). See [`ADVANTAGES.md`](ADVANTAGES.md). MIT licensed. Made by **Madup**.

</details>

<div align="center"><sub>MADOBI · made by Madup · built with Claude Code · evolutionary swarm optimization</sub></div>
