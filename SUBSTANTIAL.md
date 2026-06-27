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

| 21 | Shapley 데이터기반 어트리뷰션(조합) | `marketing/pm/shapley_attribution.py` | 합=3.00 효율성공리 검산 |

| 22 | 전환 지연 분포·윈도우 추천 | `marketing/pm/conversion_lag.py` | 누적 40/60/80/100% 검산 |
| 23 | 증분성 홀드아웃 RCT(CI·유의) | `marketing/pm/incrementality_ab.py` | inc 500/z=6.84 검산 |

| 24 | 도구 인덱스 자동 생성기(발견성) | `marketing/pm/tools_index.py` → `TOOLS.md` | 43개 인덱싱 |
| 25 | 스킬 라우팅에 도구 인덱스 연결(skill 강화) | `.claude/skills/marketing-analyst/SKILL.md` | — |

| 26 | 가격 최적화(탄력성 폐형식) | `marketing/pm/price_optimizer.py` | p*=20,000 검산 |
| 27 | 반응곡선 적합(Hill 포화) | `marketing/pm/saturation_fit.py` | Vmax=100,K=5000 복원 |

| 28 | 매출 워터폴(기간변화 채널분해) | `marketing/pm/revenue_waterfall.py` | 분해합=+700k 검산 |
| 29 | 포화곡선 예산배분(한계전환 그리디) | `marketing/pm/budget_response_alloc.py` | 한계균등·합=예산 |

| 30 | madobi 통합 CLI 디스패처(하네스, 53도구) | `marketing/madobi.py` | list·dispatch 작동 |
| 31 | 계절성 반영 예측(추세×요일지수) | `marketing/pm/seasonal_forecast.py` | 지수 반영 검증 |

| 32 | 파레토(80/20) 분석 | `marketing/pm/pareto.py` | 상위3개=80% 검산 |
| 33 | 집중도 HHI·유효개수 | `marketing/pm/hhi.py` | HHI=0.335 검산 |

| 34 | 코호트 리텐션 HTML 히트맵 | `marketing/pm/cohort_heatmap.py` | valid HTML 색조 |
| 35 | 윈백 우선순위(가치×이탈위험) | `marketing/pm/winback_priority.py` | c4 1순위 검산 |

| 36 | 가중 점수카드(정규화×가중) | `marketing/pm/scorecard.py` | A 1순위 검산 |
| 37 | Wilson 신뢰구간(비율 CI) | `marketing/pm/confidence_interval.py` | [3.81%,6.53%] 검산 |

| 38 | 예측 정확도(MAE/MAPE/RMSE/bias) | `marketing/pm/forecast_accuracy.py` | MAE10/MAPE6.7% 검산 |
| 39 | 목표 역산 goal-seek(ROAS→CPC/CVR) | `marketing/pm/target_setter.py` | 최대CPC=833 검산 |

| 40 | 피어슨 상관(시너지/잠식) | `marketing/pm/correlation.py` | r=+0.979 검산 |
| 41 | 계정 헬스 스코어(효율·분산·품질) | `marketing/pm/account_health.py` | 93/100 검산 |

| 42 | 주간 롤업(ISO주·WoW) | `marketing/pm/weekly_rollup.py` | WoW -28.4% 검산 |
| 43 | IQR 이상치(Tukey 울타리) | `marketing/pm/outlier_iqr.py` | C6 적발·Q1/Q3 검산 |
*(레포 정리: 19 샘플 → `marketing/samples/`)*

| 44 | SRM 표본비율 불일치(카이제곱) | `marketing/pm/srm_check.py` | chi²=52.6 검산 |
| 45 | 예산 램프 플랜(학습 리셋 방지) | `marketing/pm/ramp_plan.py` | 7일 점진 검산 |

| 46 | 브랜드 vs 논브랜드 분리 | `marketing/pm/brand_split.py` | 세그 집계 검산 |
| 47 | 한계 CPA(증액 효율 체감) | `marketing/pm/marginal_cpa.py` | meta20k/google8.3k/naver∞ |

| 48 | 도달 플래너(예산·CPM·모수) | `marketing/pm/reach_planner.py` | 도달864k/빈도2.31 검산 |
| 49 | ROAS 목표 갭(매출 부족분) | `marketing/pm/roas_gap.py` | 총부족 900k 검산 |

| 50 | 임원 요약 리포트(통합 캡스톤) | `marketing/pm/exec_report.py` | 종합·갭·품질 검산 |
| 51 | CTR 벤치마크(포트폴리오 대비) | `marketing/pm/ctr_benchmark.py` | C 1.84x 검산 |

**🎯 SC 50 돌파 — 50개 substantial 분석도구, 전부 수치 검산 통과.**

| 52 | CPM 추세(경매 경쟁 압력) | `marketing/pm/cpm_trend.py` | +20% 상승 검산 |
| 53 | 효율 사분면(볼륨×효율 액션) | `marketing/pm/efficiency_quadrant.py` | Scale/Grow/Fix/Cut 검산 |

## ⬜ 진행/큐 (각 30분급)
54 멀티 KPI 대시 · 55 코호트 LTV 비교 · 56 가설검정 일반화 · … (→200)
6 미디어믹스 회귀(MMM 간이) · 7 증분성(geo holdout) 추정 · 8 검색어 클러스터링 · 9 소재 피로 모델(추세) ·
10 페이싱 최적화(잔여예산 재분배) · 11 HTML 대시보드 생성 · 12 데이터 품질 검증기(다중 룰) ·
13 입찰 시뮬레이터 · 14 LTV 예측(코호트 외삽) · 15 RFM 세그먼테이션 · … (→200)
