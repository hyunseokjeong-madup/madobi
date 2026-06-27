# marketing/pm — 도구 인덱스 (자동 생성)

총 68개 도구. `python tools_index.py`로 갱신. 모든 계산은 코드 검산(수치 안 틀림).

| 도구 | 설명 |
|------|------|
| `abtest.py` | A/B 테스트 유의성 (two-proportion z-test). 전환율 A vs B가 통계적으로 유의한가. |
| `account_health.py` | 계정 헬스 스코어 — 캠페인 CSV에서 효율(ROAS/목표)·집중도(HHI)·데이터품질을 종합해 0~100 점수. |
| `alert_digest.py` | 일일 알림 다이제스트. 한 CSV에서 가드레일 위반·낭비·상위성과를 한 번에 요약(아침 점검용). |
| `anomaly_ts.py` | 시계열 이상탐지 — 추세(이동중앙값) + 요일계절 + 잔차(MAD) 분해. |
| `attribution_compare.py` | 어트리뷰션 비교. 두 전환 소스(예: 플랫폼 vs GA/내부)의 합계와 격차(%)를 대사. |
| `attribution_mta.py` | 멀티터치 어트리뷰션(MTA) 엔진 — 경로(touchpoint) CSV에서 채널 기여를 5개 모델로 배분. |
| `bid_sim.py` | 입찰 시뮬레이터 — 입찰 랜드스케이프(CPC→클릭량)에서 이익 최대 입찰 탐색. |
| `brand_split.py` | 브랜드 vs 논브랜드 분리 — 검색어를 브랜드 키워드 포함 여부로 분류해 성과 분해. |
| `budget_optimizer.py` | 예산 최적화 — 한계수익(marginal return) 기반 채널 배분. |
| `budget_response_alloc.py` | 포화곡선 기반 예산배분 — 채널별 Hill 반응(y=Vmax·x/(K+x))에서 한계전환 균등화로 총전환 최대 배분. |
| `channel_mix.py` | 채널 믹스 분석. 현재 지출 배분(%)과 ROAS를 비교해 과/저투자 채널을 식별. |
| `churn_score.py` | 이탈위험 스코어 — 최근성 대비 기대 구매주기로 위험 산출. |
| `cluster_terms.py` | 검색어 클러스터링 — 공통 토큰으로 검색어를 묶고 클러스터별 성과 집계. |
| `cohort.py` | 코호트 리텐션 + LTV 곡선. |
| `cohort_heatmap.py` | 코호트 리텐션 HTML 히트맵 — 코호트×기간 잔존율을 색조 셀로 시각화. 잔존율 계산 정확. |
| `confidence_interval.py` | Wilson 신뢰구간 — 비율(전환율 등)의 정확한 CI. 소표본·극단비율에서 정규근사보다 정확. |
| `conversion_lag.py` | 전환 지연(conversion lag) 분포 — 클릭→전환 소요일 분포로 어트리뷰션 윈도우 적정성 진단. |
| `correlation.py` | 피어슨 상관 — 두 수치 컬럼의 상관계수(시너지/잠식/연관 탐지). r=cov/(sx·sy). 계산 정확. |
| `ctr_benchmark.py` | CTR 벤치마크 — 각 항목 CTR을 포트폴리오 가중 CTR(ΣClk/ΣImpr) 대비 비교해 과/저성과 표시. |
| `dashboard.py` | HTML 대시보드 생성 — CSV를 받아 종합 카드 + 차원별 표(인라인 막대)를 단일 HTML로 출력. |
| `data_quality.py` | 데이터 품질 검증기 — 마케팅 CSV의 정합성 위반을 다중 룰로 점검(보고 전 게이트). |
| `dow_heatmap.py` | 요일별 성과 히트맵. 날짜 컬럼 → 요일별 지표 집계(가중) + 막대. |
| `exec_report.py` | 임원 요약 리포트 — 한 CSV에서 종합 성과·ROAS 갭·최대 기여자·데이터 품질을 한 장 마크다운으로. |
| `forecast.py` | 월말/기간말 예측. 현재 추세(일평균)로 목표 일수까지 spend/conversions/revenue 선형 투영. |
| `forecast_accuracy.py` | 예측 정확도 — 실제 vs 예측의 MAE/MAPE/RMSE/bias 산출. 모델 신뢰도 평가. 계산 정확. |
| `frequency.py` | 빈도(frequency) 캡 점검. freq=노출/도달. 캡 초과 시 피로·예산낭비 경보. |
| `funnel.py` | 퍼널 드롭오프 분석 (impr→click→conv). 가장 약한 단계 식별. CSV 합계 또는 직접 인자. |
| `geo_lift.py` | Geo 증분성(geo holdout) — 이중차분(difference-in-differences)으로 광고 순증분 추정. |
| `guardrails.py` | 목표 CPA/ROAS 가드레일 체커. 엔티티별로 목표 위반을 경보. |
| `hhi.py` | 집중도 HHI — Herfindahl-Hirschman 지수(점유율 제곱합)로 채널/상품 집중도 측정. |
| `incrementality_ab.py` | 증분성(홀드아웃 RCT) — 노출군 vs PSA/홀드아웃 대조군의 전환율 차이로 순증분 추정. |
| `kpi_decomp.py` | KPI 변동 요인분해 — CPA = CPC / CVR 의 기간 변화(A→B)를 CPC효과·CVR효과로 로그분해. |
| `ltv_forecast.py` | LTV 예측 — 관측 리텐션에서 기하감쇠(retention_n = r1 * d^(n-1)) 추정 후 horizon까지 외삽, |
| `ltv_payback.py` | LTV·페이백. CAC 회수 기간(개월)과 LTV/CAC 비율. 마진 반영. |
| `marginal_cpa.py` | 한계 CPA — 두 구간(증액 전/후)의 추가 지출당 추가 전환 비용. marginal CPA=Δspend/Δconv. |
| `market_basket.py` | 시장바구니 분석 — 연관규칙(support/confidence/lift). 함께 구매되는 품목쌍 발굴(번들·교차판매). |
| `mer.py` | MER (Marketing Efficiency Ratio) = 총매출/총광고비. 채널귀속 무관 전사 효율. |
| `mmm.py` | 미디어믹스 간이 회귀(MMM) — OLS로 채널별 매출 기여 계수 추정. |
| `naming_check.py` | 네이밍 규칙 검증. 소재/캠페인명이 {campaign}_{angle}_{format}_{hook}_v## 규칙을 따르는지 점검. |
| `new_vs_returning.py` | 신규 vs 재구매 분해 — 거래 데이터에서 각 거래를 첫구매(신규)/재구매로 판정해 매출·주문 분해. |
| `outlier_iqr.py` | IQR 이상치 탐지 — Tukey 울타리(Q1−1.5·IQR, Q3+1.5·IQR) 밖 값을 이상치로 표시. |
| `pacing.py` | 예산 페이싱 알림 (budget pacing). 소진 추세 → 예상 소진·일일 목표·과/저소진 경보. |
| `pacing_optimizer.py` | 페이싱 최적화 — 잔여 예산을 남은 일자에 가중치(요일/시즌)대로 재분배해 일별 목표 산출. |
| `pareto.py` | 파레토(80/20) 분석 — 상위 몇 %의 항목이 가치의 80%를 차지하는지. 누적 기여 산출(정확). |
| `poas.py` | POAS — 마진 반영 수익성 ROAS. POAS=매출×마진/광고비. 손익분기 마진도 계산. |
| `price_elasticity.py` | 가격탄력성 추정 — log(수량) = a + e·log(가격)의 OLS 기울기 e가 탄력성. |
| `price_optimizer.py` | 가격 최적화 — 일정탄력성 수요(q=k·p^e)에서 이익 최대 가격의 폐형식 해. |
| `promo_roi.py` | 프로모션 ROI — 할인 판촉의 증분 이익을 마진 잠식까지 반영해 계산. |
| `ramp_plan.py` | 예산 램프 플랜 — 학습 리셋 없이 일일 최대 증액률(기본 20%)로 현재→목표 일예산 점진 증액 계획. |
| `reach_planner.py` | 도달 플래너 — 예산·CPM·모수에서 노출/도달/빈도 추정(미디어 플래닝). |
| `reallocate.py` | 예산 재배분 제안 (budget reallocation). 저효율 → 고효율 채널로 예산 이동, 매출 증분 추정. |
| `revenue_waterfall.py` | 매출 워터폴 — 두 기간 사이 총매출 변화를 채널별 기여로 분해(워터폴). 합=총변화(정확). |
| `rfm.py` | RFM 세그멘테이션 — 거래 데이터로 Recency/Frequency/Monetary 5분위 점수화 후 세그먼트 분류. |
| `roas_gap.py` | ROAS 목표 갭 — 채널별 실제 ROAS vs 목표. 미달 채널의 매출 부족분(목표달성 필요 추가매출) 집계. |
| `rotation.py` | 소재 로테이션/리프레시. 노출 충분한데 CTR 낮은 소재 → 교체 후보. 신선도 우선순위 제시. |
| `sample_size.py` | A/B 표본수 · 검정력 계산기 (two-proportion). |
| `saturation_fit.py` | 반응곡선 적합(포화) — Hill/Michaelis 곡선 y = Vmax·x/(K+x) 을 (지출,전환) 점들에서 적합. |
| `scorecard.py` | 가중 점수카드 — 여러 지표를 0~1 정규화(min-max) 후 가중합으로 종합 순위. |
| `search_terms.py` | 검색어 분석. 지출은 큰데 전환 0인 검색어 → 네거티브 키워드 후보. 전환 좋은 검색어 → 확대 후보. |
| `seasonal_forecast.py` | 계절성 반영 예측 — 선형 추세 × 요일 계절지수로 향후 N일 예측. |
| `seasonality.py` | 시즌성(요일) 지수. 요일 평균/전체 평균 = 지수(>1 강세, <1 약세). 입찰·예산 가중 가이드. |
| `shapley_attribution.py` | Shapley 값 데이터기반 어트리뷰션 — 채널 조합(coalition) 기여를 Shapley 값으로 공정 배분. |
| `srm_check.py` | SRM(표본비율 불일치) 점검 — A/B 트래픽 배분이 기대비율(기본 50/50)에서 유의하게 벗어났는지 카이제곱 검정. |
| `target_setter.py` | 목표 역산(goal-seek) — 목표 ROAS/CPA 달성에 필요한 입력값 역산. |
| `tools_index.py` | 도구 인덱스 생성기 — marketing/pm/*.py 의 모듈 도크스트링 첫 줄을 모아 TOOLS.md 자동 생성. |
| `waste.py` | 예산 낭비 탐지. ROAS가 기준 미만인데 지출이 큰 엔티티 → 절감 후보. |
| `weekly_rollup.py` | 주간 롤업 — 일별 CSV를 ISO 주 단위로 집계하고 WoW(주간대비) 증감 산출. 가중지표 정확. |
| `winback_priority.py` | 윈백 우선순위 — 과거가치(monetary) × 이탈위험(recency/기대주기)으로 재유치 대상 순위화. |
