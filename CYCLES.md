# 🔄 300-Cycle 트래커 (퍼포먼스 마케팅 일상 루틴 자동화)

목표: 퍼마 분석가의 **일상 루틴**을 한 사이클에 하나씩, 코드검증 + 커밋·푸시로 완성. ~300 사이클.
규칙: 각 사이클 = 실제 동작하는 도구/자산 1개 + `tests/run_all.py` green + 이 표 갱신.

## ✅ 완료 (108/300)
| # | 사이클 | 산출물 |
|---|--------|--------|
| 1 | 숫자 정합성 검산 | `marketing/reconcile.py` |
| 2 | 소재 성과 분석 | `marketing/analyze_creatives.py` |
| 3 | 대용량 집계 | `marketing/bench/summarize.py` |
| 4 | 집계 벤치 30단계(4D 피벗) | `marketing/bench/levels.py` |
| 5 | 소재 변주 생성 | `marketing/creative_gen.py` |
| 6 | 이벤트/리프트/이상치 | `marketing/event_analysis.py` |
| 7 | 자기개선(피드백→깃) | `learn.py` |
| 8 | 놀리지 자동동기화 훅 | `tools/autosync.py` + settings |
| 9 | 통합 테스트 러너 | `tests/run_all.py` |
| 10 | 라이브 데모 리포트 | `docs/DEMO.md` |
| 11 | Gen5 마케팅 추론 벤치 | `marketing/bench/marketing_reasoning.py` |
| 12 | 성과 리포트 생성 | `marketing/report.py` |
| 13 | 예산 페이싱 알림 | `marketing/pm/pacing.py` |
| 14 | 퍼널 드롭오프 | `marketing/pm/funnel.py` |
| 15 | A/B 유의성 검정 | `marketing/pm/abtest.py` |
| 16 | 예산 재배분 제안 | `marketing/pm/reallocate.py` |
| 17 | 목표 CPA/ROAS 가드레일 | `marketing/pm/guardrails.py` |
| 18 | 예산 낭비 탐지 | `marketing/pm/waste.py` |
| 19 | 요일별 히트맵 | `marketing/pm/dow_heatmap.py` |
| 20 | 월말 예측(spend/conv/rev) | `marketing/pm/forecast.py` |
| 21 | POAS(마진반영 수익성) | `marketing/pm/poas.py` |
| 22 | 빈도 캡 점검 | `marketing/pm/frequency.py` |
| 23 | LTV/페이백 | `marketing/pm/ltv_payback.py` |
| 24 | 네이밍 규칙 검증 | `marketing/pm/naming_check.py` |
| 25 | 검색어/네거티브 발굴 | `marketing/pm/search_terms.py` |
| 26 | 채널 믹스 분석 | `marketing/pm/channel_mix.py` |
| 27 | 일일 알림 다이제스트 | `marketing/pm/alert_digest.py` |
| 28-31 | 채널 플레이북(Meta/Google/TikTok/Naver) | `marketing/knowledge/channels/*.md` |
| 32 | 지표 용어집(놀리지에셋) | `marketing/knowledge/glossary.md` |
| 33–42 | 버티컬 플레이북 10(이커머스/앱/리드젠/게임/금융/뷰티/패션/푸드/교육/여행) | `knowledge/verticals/*` |
| 43–52 | 포맷 가이드 10(검색/쇼핑/숏폼/롱폼/디스플레이/네이티브/UGC/캐러셀/컬렉션/플레이어블) | `knowledge/formats/*` |
| 53–62 | 함정 카드 10(어트리뷰션/심슨/타임존/통화/중복/봇/학습기/iOS/브랜드잠식/소표본) | `knowledge/pitfalls/*` |
| 63–66 | 루틴 체크리스트 4(일/주/월/분기) | `knowledge/routines/*` |
| 67–72 | 채널 추가 6(YouTube/Kakao/AppleSearch/Criteo/LINE/X) | `knowledge/channels/*` |
| 73–92 | 지표 심화카드 20(CTR…MER·기여마진) | `knowledge/metrics/*` |
| 93–100 | 템플릿 8(온보딩/일·주·월 리포트/브리프/네이밍/AB/QBR) | `knowledge/templates/*` |
| 101–108 | 체크리스트 8(런칭/감사/정합성/소재QA/트래킹/예산/스케일/중지) | `knowledge/checklists/*` |

## ⬜ 큐 (다음 사이클들)
109 소재 로테이션 도구 · 110 어트리뷰션 윈도우 비교 · 111 시즌성 탐지 ·
112 마케팅 추론 벤치 +30문항(함정) · 113 집계 레벨 50까지 확장 · … (→300)
29 어트리뷰션 윈도우 비교 · 30 시즌성 탐지 · 31 입찰 조정 제안 · 32 LP/오퍼 점검 ·
33 증분성(holdout) 추정 · 34 CPM 추세/경매압력 · 35 세그먼트 성과 랭커 · 36 KPI 자동 코멘트 ·
37 다계정 롤업 · 38 예산 시뮬레이터 · 39 경쟁/점유율 · 40 리포트 스케줄러(하네스) ·
… (41–300: 위 루틴 심화·통합·다계정·대시보드·지식자산 확장)
22 코호트 리텐션/LTV-페이백 · 23 POAS(마진반영 ROAS) · 24 월말 예산/전환 예측 ·
25 빈도(frequency) 캡 점검 · 26 네이밍 규칙 검증기 · 27 채널 믹스 최적화 · 28 세그먼트 성과 랭커 ·
29 입찰 조정 제안 · 30 낭비 탐지(저ROAS·고지출) · 31 증분성(holdout) 추정 · 32 시즌성 탐지 ·
33 전환 지연(lag) 보정 · 34 어트리뷰션 윈도우 비교 · 35 CPM 추세/경매압력 · 36 LP 퍼널(있으면) ·
37 예산 시뮬레이터 · 38 KPI 이상 자동 코멘트 · 39 경쟁 벤치(점유율) · 40 리포트 스케줄러(하네스) ·
… (41–100: 위 루틴들의 심화/통합·다계정·자동화·대시보드)

## 진행 원칙
- 동시 워크플로 1~2개. 모든 수치 코드검증. 각 사이클 커밋·푸시.
- 사용자 피드백은 `learn.py`로 학습→깃 반영. 이 표는 매 사이클 갱신(살아있는 문서).
