<div align="center">

<img src="assets/logo.svg" alt="MADOBI" width="680">

# MADOBI · 매도비

**매드업이 만드는 마케팅 특화 AI 에이전트 — 숫자를 절대 틀리지 않는다.**

*스웜 최적화로 선별된 검증-우선 전략 · 정합성 보장 · 소재 분석 · 쓸수록 자라는 놀리지에셋*

`진화적 스웜 최적화` · `Doer–Verifier 검증` · `마케팅 애널리틱스`

![license](https://img.shields.io/badge/license-MIT-green)
![checks](https://img.shields.io/badge/checks-8%2F8%20green-brightgreen)
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

> **핵심 결과:** 승리 전략(**검증 우선**) + **다수결**은 *무거운 산술에서도 무실점*에 도달합니다.
> 이것이 일반 에이전트가 스프레드/캠페인 분석에서 "숫자를 틀리는" 실패 모드를 정면으로 해결합니다.

## 🏆 핵심 성과

| 단계 | 내용 | 결과 |
|------|------|------|
| Gen 1 | 시드 4종 × 10문항 | 순수 분해는 무거운 산술에 **해롭다**, 검증이 **고친다** |
| Gen 2 | **112 설계** × 어려운 문항 (5팀 병렬) | 검증 계열 압도, 만점 13종 |
| Gen 3 | 결선: 12 finalist × 20문항 | **4종이 20/20** |
| Gen 4 | 결정전: 4 챔피언 × 오류多 × 5시행 | 챔피언 **`F03_adversarial_c`** (단일샷 29/30); **다수결 → 6/6 완벽** |

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
$ python marketing/reconcile.py marketing/sample_campaign.csv
-- checks: 16 PASS, 2 WARN --
  ! [C_carousel] ctr: reported=9.9% recomputed=5.0000%      # 보고값과 실제 불일치 적발
  ! [SUM] spend: rows_sum=4,100,000 vs total_row=4,200,000   # 합계 ≠ 총계 적발
VERDICT: 2 INCONSISTENCY(IES) - investigate raw data
```

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
                  reconcile.py · summarize · analyze_creatives · pm/(퍼마 도구 25+)
                  knowledge/(212+ 자산) · bench/(집계+추론 벤치) · samples
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
A marketing-specialized AI agent by **Madup** that **never gets the numbers wrong**. Its operating
strategy was not hand-written — it was **selected by evolutionary swarm optimization**: 112 candidate
manuals across 14 strategy families, scored on a **code-verified benchmark** over 4 generations.
Champion strategy = **verification-first** (`decompose → independent verify → adversarial refute → majority vote`),
which reaches **perfect accuracy even on heavy arithmetic** — exactly the failure mode behind "wrong numbers"
in spreadsheet/campaign analysis.

## Key results
- Gen2: 112 designs → verification family dominates (13 perfect on the hard subset).
- Gen3 finals: 4 designs score 20/20. Gen4 tie-break: champion `F03_adversarial_c` (29/30 single-shot; majority-vote → 6/6).

## Use it in Claude Code
Agents/skill under `.claude/` auto-load. `git clone … && cd madobi && claude`. Then ask
*"summarize this campaign CSV and check the numbers"* — it reconciles before reporting. Routing is automatic
via skill/agent `description`s, under the user's control.

## Aggregation benchmark
`marketing/bench/` — 100k rows × 13 fields with code-computed ground truth, a 30-level difficulty ladder
(multi-pivot incl. a 4-dimension/225-group pivot, filters, top-N, share-of, derived-of-derived). **29/29 pass.**

## Self-improving loop
`learn.py` turns your feedback into a knowledge asset and **auto-commits/pushes to git** — the repo becomes the
team's compounding, version-controlled knowledge base.

## Why stronger than Hermes / Pi (single-loop agents)
Evidence-based strategy · verification-swarm robustness · parallel orchestration · compounding knowledge.
See `ADVANTAGES.md`. MIT licensed. Made by Madup.

</details>

<div align="center"><sub>MADOBI · made by Madup · built with Claude Code · evolutionary swarm optimization</sub></div>
