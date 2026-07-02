---
name: marketing-analyst
description: 매드업 마케팅 분석가 스킬. 광고 성과 분석·스프레드시트 요약·이벤트/캠페인 분석·광고 소재(creative) 기획/생성/점검을 숫자 정합성(reconciliation) 보장과 함께 자동 수행한다. 스프레드/시트/CSV 요약, CTR·CPC·CPA·ROAS·CPM 계산, 소재 성과·승자 분석, 소재 카피/후크 기획, 리포트 작성 같은 루틴 업무와, 지표 정의·성과 원인 질문("ROAS가 뭐야", "CPA 왜 올랐어"), 예산/페이싱·이탈·코호트·LTV·어트리뷰션·A/B·이상탐지·대시보드·임원보고 요청에 사용. 산술은 결정론적 코드가 계산·교차검증하고 LLM은 판단·해석만 한다 — 숫자 정합성이 최우선.
---

# Marketing-Analyst Skill (MADOBI)

매드업 분석가의 **루틴 업무를 정합성 보장과 함께 자동화**한다.
핵심 원칙: **모든 숫자는 원자료에서 재계산 + 독립 교차검증한 값만 보고한다.** ("느낌" 금지.)

## 0. 시작 시 (맥락 복원 — 검색 기반)
- **놀리지에셋이 213개로 커졌으므로 전체를 읽지 말고 검색으로 회상한다.**
  `python marketing/knowledge/recall.py --account <account> --query "<이번 작업 핵심어>" --limit 5`
  → 계정 메모리(`knowledge/<account>.md`+`history/<account>-log.md`) + 관련 놀리지를 붙여넣기용 마크다운으로 회상.
  (FTS5 색인이 있으면 의미 랭킹, 없으면 grep 폴백 — 둘 다 결정론적. 의존성 0.)
- 색인이 없거나 오래됐으면 `python marketing/knowledge/search.py --build` 로 갱신(213개 1초 내).
- 회상된 기준선·통하는 앵글·금칙어·선호 리포트 포맷을 작업에 반영한다. → `marketing/MEMORY_PROTOCOL.md`

## 1. 작업 라우팅
| 요청 | 절차 |
|------|------|
| 어떤 도구가 맞을지 애매한 자연어 질문 | `python marketing/chat.py --ask "<질문>"` → 결정론 라우터의 추천 도구·검증된 명령을 받아 실행 |
| 지표 정의/공식 질문 ("ROAS가 뭐야?") | `python marketing/semantic_layer.py <용어>` 또는 chat.py 즉답 — 용어집 밖 정의를 임의로 만들지 않는다 |
| 과거 교훈/계정 맥락 질문 | `python marketing/knowledge/recall.py --query "<핵심어>" --limit 5` |
| 스프레드/CSV 요약, 성과 리포트 | §2 정합성 파이프라인 → 검산된 총계+파생지표+⚠경고 |
| 채널/캠페인/소재 분석 | §2 + `METRICS.md` D(소재) → 승자/패자·피로·추천 |
| 이벤트/캠페인 분석 | §2 + `METRICS.md` E → pre/post·리프트·페이싱·이상치 |
| 소재 기획/생성/점검 | `CREATIVE_PLAYBOOK.md` + `analyze_creatives.py`(분석) + `creative_gen.py`(변주매트릭스 생성) |
| 이벤트/캠페인 효과 | `event_analysis.py` — pre/post 리프트·페이싱·이상치(구간별) |
| 성과 리포트(일/주/월) | `report.py` — 검산된 종합·차원별·기간비교 마크다운 |
| 퍼마 일상 루틴 | `pm/pacing.py`(페이싱) · `pm/funnel.py`(퍼널) · `pm/abtest.py`(유의성) · `pm/reallocate.py`(예산 재배분) |
| 대시보드/임원보고/아침점검 | `pm/dashboard.py <csv> --by <dim> --out <html>` · `pm/exec_report.py <csv> --target-roas <t>` · `pm/alert_digest.py <csv> --by <dim>` |
| 차원별 SQL 집계(삼중검증) | `sql_query.py <csv> --group-by <dim> --metric <m> [--verify]` — duckdb 없으면 자동 파이썬 폴백, 불일치 시 파이썬이 진실 |
| 피드백/교정 발화 ("앞으로 항상 ~", "그거 틀렸어") | `python learn.py --feedback "<발화>"` — 기본 **자동 커밋+푸시**, 검토 후로 미루려면 `--no-commit` |

## 2. 숫자 정합성 파이프라인 (검증 스웜)
1. **파싱**: 단위/통화/콤마/%/결측 정리(`METRICS.md` A,B). 헤더·합계행·소계행 구분(이중계산 방지).
2. **재계산(Solver)**: 파생지표를 원자료에서 계산 — CTR=clicks/impr, CPC=spend/clicks, CPM=spend/impr×1000,
   CPA=spend/conv, ROAS=rev/spend. **비율은 가중**(Σ/Σ), 단순평균 금지(Simpson).
3. **검산(Verifier)**: 정합성 불변식 — 분해합=총계, 파생 역산 일치, 기간합, 단위/반올림.
   **데이터가 CSV면 `python marketing/reconcile.py <file>` 를 실행해 자동 검산**하고 결과를 보고에 반영.
   - 지표별 허용오차가 필요하면 `marketing/safemath.py`(0/0·inf 가드 + per-metric tolerance: ctr/roas 1e-4, 금액 1%).
   - **삼중검증(선택)**: duckdb가 있으면 `python marketing/sql_query.py <file> --group-by <dim> --metric roas`
     → SQL 경로와 파이썬 경로 결과가 일치할 때만 통과(불일치 시 파이썬이 정답). 의존성 없으면 자동으로 파이썬만.
   - 지표 용어 매핑(ROAS/신규회원/전환→정규 공식)은 `marketing/semantic_layer.py`의 `resolve()`로 통일(78도구 드리프트 방지).
4. **합성(Synthesizer)**: 검증 통과 수치만 보고. 불일치는 **⚠로 표면화**하고 원자료 점검을 권고(숨기지 말 것).
   - **외부로 나가는 중요 보고서는 `madobi-verifier` 에이전트에 초안+원본 경로를 넘겨 독립 검증** —
     `VERIFIER VERDICT: APPROVED` 후에만 발송 (Doer–Verifier 분리, 자기검증 편향 차단).
5. **기록(Knowledge)**: 새 기준선·통한 소재·정합성 이슈·선호 포맷을 자산/메모리에 누적(`MEMORY_PROTOCOL.md`).
   - **중복 없이 누적**: `python marketing/knowledge/curate.py --upsert marketing/knowledge/<account>.md --tag <t> --feedback "<교훈>"`
     (경로는 repo 루트 기준 — `marketing/` 접두어 필수. 같은 교훈은 날짜만 '재검증'으로 갱신 — append-only 중복 방지).
     새 계정은 `--onboard <account>`로 템플릿 생성.

## 3. 보고 형식 계약
- 숫자엔 **단위**(₩/%/×), 자릿수 일관, 천단위 구분. 가정(윈도우·타임존·통화·필터)을 머리에 명시.
- 각 파생지표 옆에 **검산 ✓** 또는 **⚠불일치(원자료 X≠Y)**.
- 마지막에 **한 줄 정합성 판정**(CONSISTENT ✓ / N건 불일치 → 점검).

## 4. 견고성 규칙 (실험으로 검증됨)
- 무거운 합/반복 계산은 단일패스로 믿지 말 것 → 청크 검산 또는 **코드 실행으로 교차검증**.
- 중요한 수치는 **다수결(서로 다른 방법 2~3회)** 로 확정. (실험: 검증+다수결 = 무거운 산술도 무실점.)
- 추천·소재 평가는 **충분 표본**에서만, 소표본 변동을 경고.

## 퍼마 도구 (78개)
일상/심화 분석은 `marketing/pm/` 도구로 수행. **전체 목록·설명은 `marketing/pm/TOOLS.md` 인덱스 참조**
(어트리뷰션 MTA/Shapley/DiD · 예산최적화 · A/B표본수·증분성 · MMM·가격탄력성 · 코호트·RFM·이탈·LTV ·
페이싱·입찰·KPI분해·프로모ROI · 시장바구니·검색어클러스터·이상탐지 · 데이터품질·대시보드 등).
모든 계산은 코드 검산(수치 안 틀림). 도구 추가 시 `python marketing/pm/tools_index.py`로 인덱스 갱신.

## 참조 자산
`marketing/METRICS.md` · `marketing/CREATIVE_PLAYBOOK.md` · `marketing/MEMORY_PROTOCOL.md` ·
`marketing/reconcile.py` · `marketing/STRATEGY.md`
