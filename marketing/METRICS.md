# 마케팅 지표 & 숫자 정합성(reconciliation) 레퍼런스

마케팅 분석에서 **숫자를 틀리지 않기** 위한 공식·검산 규칙. 모든 파생지표는 **원자료에서 재계산 +
독립 교차검증**한 값만 보고한다. (SWARM-SOLVER의 검증 스웜이 여기에 직접 적용된다.)

## A. 핵심 지표 공식 (애드테크)
| 지표 | 정의 | 단위/주의 |
|------|------|-----------|
| CTR | clicks / impressions | 0~1 또는 %, ×100 |
| CPC | spend / clicks | 통화 |
| CPM | spend / impressions × 1000 | 통화, ×1000 주의 |
| CVR (전환율) | conversions / clicks | %; 정의가 /impressions인지 확인 |
| CPA / CPI | spend / conversions(installs) | 통화 |
| ROAS | revenue / spend | 배수(×) 또는 % |
| ROI | (revenue − spend) / spend | % |
| AOV | revenue / orders | 통화 |
| Reach / Frequency | unique users / (impressions ÷ reach) | reach ≤ impressions |
| eCPM | revenue / impressions × 1000 | 퍼블리셔측 |
| VTR | views / impressions (동영상) | % |
| Fill rate | served / requested | % |
| Engagement rate | engagements / impressions(또는 reach) | 분모 정의 확인 |
| CPL | spend / leads | 통화 |
| LTV | ARPU × 평균 수명 (또는 코호트 누적) | 정의 문서화 |
| Retention Dn | day-n 잔존 / 설치 | % |

## B. 정합성(reconciliation) 불변식 — 보고 전 반드시 검산
1. **분해 합 = 총계**: 일자별/채널별/캠페인별/소재별 합 = 전체 합. (spend, impressions, clicks, conversions 각각)
2. **파생지표 역산**: 보고된 CTR × impressions ≈ clicks; CPC × clicks ≈ spend; ROAS × spend ≈ revenue.
   두 경로가 어긋나면 원자료를 의심.
3. **기간 합산**: 주간/월간 총계 = 해당 일자 합. 중복기간/경계일 off-by-one 주의.
4. **비율 평균의 함정**: CTR 등 **비율은 단순평균하지 말 것** — 가중(Σclicks/Σimpr)으로 재계산. (Simpson)
5. **단위/통화 일관성**: KRW/USD 혼용, %와 소수, CPM/eCPM의 ×1000, 천단위 구분기호 제거 후 계산.
6. **반올림 누적오차**: 중간값은 충분한 자릿수 유지, 최종에만 반올림. 합이 100%가 안 되면 반올림 표기.
7. **결측/0 분모**: clicks=0에서 CPC 정의 불가 → "—"로, 0으로 채우지 말 것.
8. **어트리뷰션 윈도우/모델**: conversions는 윈도우(1d/7d), 모델(last-click 등)에 따라 다름 — 비교 전 동일 기준 확인.
9. **중복/봇/무효 트래픽**: invalid clicks 제거 전후 구분.
10. **타임존**: 플랫폼 타임존(UTC vs KST) 경계에서 일자 집계 차이.

## C. 스프레드시트 요약 규칙
- 셀을 **눈대중 합산 금지** — 항상 재계산(코드/청크합)하고 총계행과 대조.
- 헤더·합계행·소계행을 데이터로 오인하지 말 것(이중계산 방지).
- 숨은 행/필터/피벗 소계가 총합에 포함되는지 확인.
- 통화·% 혼합 열, 천단위 콤마, 빈칸/—/N/A 처리 명시.
- 요약에는 **(a) 검산한 총계, (b) 핵심 파생지표, (c) 정합성 경고(있으면)** 를 함께 제시.

## D. 광고 소재(creative) 분석 특화
- 소재 단위 지표: impressions/clicks/spend/conversions → CTR/CPC/CPA/ROAS/CVR (소재별 재계산).
- **승자/패자 식별**: 충분 노출(예: impr ≥ 임계) 소재만 비교, 소표본 변동 경고.
- **소재 피로(fatigue)**: frequency↑ + CTR↓ 추세, 최초대비 성과 감쇠.
- **포맷/후크/길이/썸네일** 등 차원별 집계, 차원합=총계 검산.
- **크리에이티브 테스트(A/B)**: 표본·기간 동일성, 통계적 유의 여부(소표본 과해석 금지).
- 추천은 **수치 근거 + 정합성 확인**과 함께. "느낌" 금지.

## E. 이벤트/캠페인 분석 특화
- 사전/사후(pre/post), 리프트(lift = post − baseline), 페이싱(예산 소진율 = spend/budget × 기간보정).
- 이상치(anomaly): 일자 급변 → 원자료/타임존/중복 점검 후 보고.
- 동기간 비교(YoY/WoW)는 요일·시즌·캠페인 중첩 통제.

## F. 보고 형식 계약
- 숫자는 **단위 명시**(₩, %, ×), 자릿수 일관, 천단위 구분.
- 모든 파생지표 옆에 **검산 통과 여부**(✓) 또는 **불일치 경고**(⚠ 원자료 X≠Y) 표기.
- 가정/기준(윈도우·타임존·통화·필터)을 보고 머리에 명시.
