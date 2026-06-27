---
name: marketing-analyst
description: 매드업 마케팅 분석가 스킬. 광고 성과 분석·스프레드시트 요약·이벤트/캠페인 분석·광고 소재(creative) 기획/생성/점검을 숫자 정합성(reconciliation) 보장과 함께 자동 수행한다. 스프레드/시트/CSV 요약, CTR·CPC·CPA·ROAS·CPM 계산, 소재 성과·승자 분석, 소재 카피/후크 기획, 리포트 작성 같은 루틴 업무를 요청할 때 사용. 숫자를 절대 틀리지 않는 것이 최우선.
---

# Marketing-Analyst Skill (MADUP-MARKETER)

매드업 분석가의 **루틴 업무를 정합성 보장과 함께 자동화**한다.
핵심 원칙: **모든 숫자는 원자료에서 재계산 + 독립 교차검증한 값만 보고한다.** ("느낌" 금지.)

## 0. 시작 시 (맥락 복원)
- 계정이 식별되면 `marketing/knowledge/<account>.md` 와 최근 `marketing/history/<account>-log.md` 를 먼저 읽어
  기준선·통하는 앵글·금칙어·선호 리포트 포맷을 복원한다. → `marketing/MEMORY_PROTOCOL.md`

## 1. 작업 라우팅
| 요청 | 절차 |
|------|------|
| 스프레드/CSV 요약, 성과 리포트 | §2 정합성 파이프라인 → 검산된 총계+파생지표+⚠경고 |
| 채널/캠페인/소재 분석 | §2 + `METRICS.md` D(소재) → 승자/패자·피로·추천 |
| 이벤트/캠페인 분석 | §2 + `METRICS.md` E → pre/post·리프트·페이싱·이상치 |
| 소재 기획/생성/점검 | `CREATIVE_PLAYBOOK.md` 1/2/3 (기획→변주매트릭스→QA체크리스트) |

## 2. 숫자 정합성 파이프라인 (검증 스웜)
1. **파싱**: 단위/통화/콤마/%/결측 정리(`METRICS.md` A,B). 헤더·합계행·소계행 구분(이중계산 방지).
2. **재계산(Solver)**: 파생지표를 원자료에서 계산 — CTR=clicks/impr, CPC=spend/clicks, CPM=spend/impr×1000,
   CPA=spend/conv, ROAS=rev/spend. **비율은 가중**(Σ/Σ), 단순평균 금지(Simpson).
3. **검산(Verifier)**: 정합성 불변식 — 분해합=총계, 파생 역산 일치, 기간합, 단위/반올림.
   **데이터가 CSV면 `python marketing/reconcile.py <file>` 를 실행해 자동 검산**하고 결과를 보고에 반영.
4. **합성(Synthesizer)**: 검증 통과 수치만 보고. 불일치는 **⚠로 표면화**하고 원자료 점검을 권고(숨기지 말 것).
5. **기록(Knowledge)**: 새 기준선·통한 소재·정합성 이슈·선호 포맷을 자산/메모리에 누적(`MEMORY_PROTOCOL.md`).

## 3. 보고 형식 계약
- 숫자엔 **단위**(₩/%/×), 자릿수 일관, 천단위 구분. 가정(윈도우·타임존·통화·필터)을 머리에 명시.
- 각 파생지표 옆에 **검산 ✓** 또는 **⚠불일치(원자료 X≠Y)**.
- 마지막에 **한 줄 정합성 판정**(CONSISTENT ✓ / N건 불일치 → 점검).

## 4. 견고성 규칙 (실험으로 검증됨)
- 무거운 합/반복 계산은 단일패스로 믿지 말 것 → 청크 검산 또는 **코드 실행으로 교차검증**.
- 중요한 수치는 **다수결(서로 다른 방법 2~3회)** 로 확정. (실험: 검증+다수결 = 무거운 산술도 무실점.)
- 추천·소재 평가는 **충분 표본**에서만, 소표본 변동을 경고.

## 참조 자산
`marketing/METRICS.md` · `marketing/CREATIVE_PLAYBOOK.md` · `marketing/MEMORY_PROTOCOL.md` ·
`marketing/reconcile.py` · `marketing/STRATEGY.md`
