# research/ — 에이전트 선별 실험 (아카이브)

MADOBI의 **챔피언 전략이 어떻게 선별됐는지**를 기록한 실험 자료. 제품 사용에는 불필요하며,
방법론·재현용 아카이브다. (제품은 최상위 `marketing/`, `.claude/`, `tests/`, `docs/`.)

## 내용
- `optimization_log.md` — 스웜 최적화 운영 일지(Gen0~5, 과정·교훈)
- `KNOWHOW.md` — 최적화 누적 지식 · `TEAM.md` — 팀 조직도 · `REPORT.md` — 실험 리포트
- `benchmark/` — 코드검증 추론 벤치(20문항) 생성기/정답
- `designs/` — 시드 전략 + Planner 역할 정의
- `results/` — 세대별 결과 데이터(랭킹·집단·결선) ※ 원자료 덤프·eval 스크립트는 정리(재생성 가능)
- 스크립트: `make_eval_script.py`(워크플로 생성), `merge_and_rank.py`, `score.py`, `track.py`,
  `extract_pop.py`, `gen_designs.js`, `swarm_eval.js`, `eval_swarm_args.js`

## 핵심 결론
검증(adversarial self-verify) + 다수결 전략(`F03_adversarial_c`)이 4세대 토너먼트에서 최강 →
이 전략을 마케팅 정합성에 특화한 것이 제품 **MADOBI**.
