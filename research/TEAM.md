# 스웜 최적화 팀 조직도 (Team Roster) — 팀 모드

이 프로젝트는 **팀 모드**로 운영된다. 각 역할은 전용 서브에이전트(스웜 노드)로 실행되며,
스웜 최적화 기획자(Planner)가 전체 세대 루프를 지휘한다.

| # | 팀/역할 | 책임 | 산출물 |
|---|---------|------|--------|
| 1 | **Planner (기획자)** ★리드 | 세대 루프 운전, 매 세대 *과정 기록*, 다음 세대 설계 | `optimization_log.md` |
| 2 | **Designer (설계자)** | 에이전트 운영 매뉴얼(프롬프트) 설계·변이·교배, 구조/가독성 정돈 | `designs/C*.md` |
| 3 | **Evaluator Swarm (평가 스웜)** | closed-book 추론으로 문제 풀이 (설계×문제 병렬) | 답안 행 |
| 4 | **Analyst (분석가)** | 채점 결과에서 실패 패턴·문제군 약점·원인 분석 | 분석 노트 |
| 5 | **Critic / Red-team (비평가)** | 설계 약점·과적합·과한 절차 부작용 지적 | 비평 노트 |
| 6 | **Synthesizer (통합자)** | 승자 설계를 최종 에이전트 정의로 통합 | `.claude/agents/*.md` |
| 7 | **Report Designer (리포트 디자이너)** | 결과를 보기 좋은 리포트/에이전트 카드로 시각화("이쁘게") | `REPORT.md`, 카드 |

## 협업 흐름 (한 세대)
```
Planner ─▶ Designer (집단 생성/변이)
            │
            ▼
        Evaluator Swarm (병렬 평가) ─▶ 결정론적 채점
            │
            ▼
        Analyst (약점 분석) ─▶ Critic (반박/과적합 점검)
            │
            ▼
        Planner (기록 + 다음 세대 결정)  ── 반복 ──┐
            │                                       │
            └──── 수렴 시 ─▶ Synthesizer ─▶ Report Designer
```

## 원칙
- 모든 평가는 도구 없는 추론(closed-book)으로 측정 → 매뉴얼의 순수 추론 향상력.
- 매 세대 과정은 반드시 `optimization_log.md`에 기록(Planner 책임).
- 엘리트 보존: 세대 최고 적합도는 단조 비감소.
- 최종 산출물은 Report Designer가 깔끔하게 정리한다.
