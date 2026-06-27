# 🧪 Substantial Cycles 트래커 (각 ~30분급 실작업 × 200)

원칙: 각 사이클은 **실제 알고리즘이 든 도구/분석**. **계산은 정확·검산 가능**(수치 절대 안 틀림),
모델/예측은 "추정"으로 명확히 라벨. 각 사이클: 구현 + 검증(수동/단위) + 통합테스트 + 커밋.

## ✅ 완료
| SC | 작업 | 산출물 | 검증 |
|----|------|--------|------|
| 1 | 멀티터치 어트리뷰션(5모델: first/last/linear/time-decay/position) | `marketing/pm/attribution_mta.py` | 수동검산 일치 |
| 2 | 예산 최적화(한계수익 균등, 체감곡선 그리디) | `marketing/pm/budget_optimizer.py` | 배분 산술 검증 |
| 3 | A/B 표본수·검정력(역정규 Acklam) | `marketing/pm/sample_size.py` | z=1.96/0.8416, n 수동검산 일치 |
| 4 | 코호트 리텐션 + LTV 곡선 | `marketing/pm/cohort.py` | 리텐션·LTV 수동검산 일치 |
| 5 | 시계열 이상탐지(추세·요일·잔차 MAD) | `marketing/pm/anomaly_ts.py` | 1/14 급락 포착 |
| 6 | 미디어믹스 회귀 MMM(OLS, 가우스소거) | `marketing/pm/mmm.py` | 진짜 계수 2/3/1.5 복원, R²=1.0 |
| 7 | geo 증분성(이중차분 DiD) | `marketing/pm/geo_lift.py` | 증분 400/리프트 36.4% 검산 |
| 8 | RFM 세그멘테이션(5분위) | `marketing/pm/rfm.py` | 세그·매출비중 100% 검산 |
| 9 | 검색어 클러스터링(공통토큰) | `marketing/pm/cluster_terms.py` | 6→5 클러스터 |
| 10 | HTML 대시보드 생성 | `marketing/pm/dashboard.py` | valid HTML 산출 |
| 11 | 입찰 시뮬레이터(이익최대 입찰) | `marketing/pm/bid_sim.py` | 최적 CPC·손익분기 검산 |
| 12 | LTV 예측(기하감쇠 외삽) | `marketing/pm/ltv_forecast.py` | d=0.5, LTV 19,688 검산 |
| 13 | 페이싱 최적화(가중 재분배) | `marketing/pm/pacing_optimizer.py` | 합=잔여 정확 |
| 14 | KPI 변동 요인분해(CPA=CPC/CVR 로그) | `marketing/pm/kpi_decomp.py` | +50%=20%×25% 검산 |
| 15 | 가격탄력성(로그-로그 OLS) | `marketing/pm/price_elasticity.py` | e=-1.5 복원, R²=1.0 |
| 16 | 프로모션 ROI(마진잠식) | `marketing/pm/promo_roi.py` | 증분 -5M/BE +100% 검산 |
| 17 | 시장바구니 연관규칙(support/conf/lift) | `marketing/pm/market_basket.py` | lift 1.12x 검산 |
| 18 | 이탈위험 스코어(최근성/기대주기) | `marketing/pm/churn_score.py` | 위험 4명 식별 |
| 19 | 신규 vs 재구매 분해 | `marketing/pm/new_vs_returning.py` | 재구매율 60% 검산 |
| 20 | 데이터 품질 검증기(다중 정합성 룰) | `marketing/pm/data_quality.py` | 5종 위반 전부 적발 |

## ⬜ 진행/큐 (각 30분급)
21 코호트 히트맵 · 22 LTV 세그·예산배분(LP) · 23 어트리뷰션 Shapley · … (→200)
6 미디어믹스 회귀(MMM 간이) · 7 증분성(geo holdout) 추정 · 8 검색어 클러스터링 · 9 소재 피로 모델(추세) ·
10 페이싱 최적화(잔여예산 재분배) · 11 HTML 대시보드 생성 · 12 데이터 품질 검증기(다중 룰) ·
13 입찰 시뮬레이터 · 14 LTV 예측(코호트 외삽) · 15 RFM 세그먼테이션 · … (→200)
