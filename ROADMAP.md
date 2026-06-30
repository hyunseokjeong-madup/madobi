# 🗺️ MADOBI 로드맵 (10 포인트)

대화에서 나온 모든 요구를 10개 포인트로 정리. ✅완료 / 🚧진행 / ⬜예정. 위에서부터 천천히 루프.

| # | 포인트 | 상태 | 핵심 산출물 |
|---|--------|------|-------------|
| 1 | **스웜 최적화 챔피언 선별** (Gen0–5) | ✅ | `optimization_log.md`, 챔피언 `F03_adversarial_c` (검증+다수결) |
| 2 | **마케팅 특화 에이전트 + 스킬** | ✅ | `.claude/agents/madobi.md`, `skills/marketing-analyst` |
| 3 | **숫자 정합성 엔진** | ✅ | `marketing/reconcile.py` (불일치 적발, 오탐 0) |
| 4 | **대용량·다필드 집계 (코드검증 벤치 29/29)** | ✅ | `bench/` 10만행×13필드, 29단계(4D 피벗) 전부 PASS |
| 5 | **소재 전주기**(기획·생성·점검·분석) | ✅ | `CREATIVE_PLAYBOOK`, `creative_gen.py`, `analyze_creatives.py` |
| 6 | **성장형 놀리지에셋 + 자기개선/자동깃** | ✅ | `learn.py`, `tools/autosync.py`, `MEMORY_PROTOCOL`, `KNOWHOW` |
| 7 | **난이도 50단계 확장 + 함정 케이스** | 🚧 | 시간윈도우·코호트·어트리뷰션·멀티통화·중복제거 (현 29 → 50+) |
| 8 | **리포트 자동 생성기**(일/주/월) | ✅ | `marketing/report.py` — 검산 포함 성과 리포트 마크다운 |
| 8b | **퍼마 일상 루틴 도구**(페이싱/퍼널/AB/재배분…) | 🚧 | `marketing/pm/*` — 100사이클 트래커 `CYCLES.md` |
| 9 | **마케팅 추론 벤치 확대 + 함정** | 🚧 | `bench/reasoning4.py` 함정 8종(Simpson·어트리뷰션 중복·타임존 경계·베이즈 사후) — 정답 닫힌형식 계산·trap/why 주석. 추가 확대 여지 |
| 10 | **온보딩 + E2E 데모 + CI** | ✅ | ✅계정 온보딩(`curate.py --onboard`) · ✅CI(`.github/workflows/ci.yml`, 105/105+29/29, py3.9/3.12 + compileall 구문가드) · ✅E2E 데모(`marketing/demo_e2e.py` 회상→검산→집계→삼중검증→루프 라운드트립, `--selftest` 내장) |
| 11 | **자기개선 루프 게이트 편입 + 경량 RL** | ✅ | ✅루프 도구 7종을 105/105 결정론 게이트에 배선 · ✅`learn.py` dedup(curate.upsert)+git 안전 · ✅손상 색인→grep 폴백 봉합 · ✅경량 UCB1 bandit(`pm/bandit_policy.py`, 폐형식·결정론) |
| 12 | **RAG ↔ RL 시너지 폐곡선** | ✅ | ✅`recall.recall_quality()`(회상 품질=색인 hit/grep·매칭비율, 100% 코드산물) → bandit 보상 · ✅결정론 confidence 배지 · ✅`viz.py` 그래프 JSON(노드213·에지680) · ✅`loop_report.py` observer(없는 산술 날조 안 함) |

## 운영 원칙
- 동시 워크플로 1~2개(레이트리밋 회피) · 모든 산출물 코드검증 · 항목별 커밋·푸시.
- 개선 요청은 `learn.py`로 놀리지에셋에 학습 + 깃 자동 반영.
- 매 항목 완료 시 이 표의 상태를 갱신(이 파일도 계속 자란다).
