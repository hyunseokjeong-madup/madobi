# prompt_eval — 서비스 프롬프트 행동계약 평가 (측정→패치→재측정 루프)

madobi의 원칙("프롬프트는 손으로 쓰지 않고 **측정으로** 고른다")을 연구용 매뉴얼이 아니라
**서비스 중인 프롬프트**(.claude/agents/madobi.md + skills/marketing-analyst/SKILL.md)에 적용하는 하네스.

## 구성
- `scenarios.json` — 행동계약 10종. 각 계약 = 사용자 발화 + must/forbid regex + 톤 제약(길이·되묻기 수).
  계약은 전부 **결정론 assertion** — 같은 응답이면 같은 점수(LLM 채점 없음).
  일부 계약(S01 검산 총계)은 도구를 실제 실행해야만 알 수 있는 수치를 요구한다 → "검산을 진짜 돌렸는가"의 증거.
- `build_eval.py` — 2-arm(madobi 프롬프트 vs baseline) 비교 워크플로 JS 생성. 현재 시점의
  madobi.md+SKILL.md 전문을 임베드하므로 **프롬프트를 고치고 다시 생성하면 그 버전이 측정된다**.
- `grade.py` — 스코어카드 채점기. `--selftest` 가 결정론 게이트(tests/run_all.py)에 배선돼 있다.

## 루프 돌리기
```bash
python research/prompt_eval/build_eval.py --out research/prompt_eval/eval.js   # 1) 현재 프롬프트로 생성
# 2) Claude Code Workflow 도구로 eval.js 실행 → 결과 JSON 저장
python research/prompt_eval/grade.py results.json                              # 3) 결정론 채점
# 4) FAIL 계약 분석 → (a) 프롬프트 결함이면 madobi.md/SKILL.md 패치
#                     (b) 계약 오탐이면 scenarios.json 정밀화 (사유를 note에 기록)
python research/prompt_eval/build_eval.py --ids <실패 id들> --out eval_rerun.js # 5) 실패분만 재측정
```

## 측정 이력
| 라운드 | madobi | baseline | 조치 |
|--------|--------|----------|------|
| 1 (2026-07-02, results_round1.json) | 8/10 → 정밀화 후 9/10 | 8/10 | S03: 계약 오탐(놀리지 기준선 인용을 날조로 오판) → forbid를 '성과 단정 패턴'으로 정밀화. S04: 진짜 결함 — 피드백에 "기억할게요"만 하고 학습 루프 미언급 → madobi.md 대화 프로토콜 4번에 learn.py 기록 의무 추가. |
| 2 (2026-07-02, results_round2/final.json) | **10/10** | 8/10 | 패치된 프롬프트로 S03·S04 재측정 → 전 계약 통과. S04 응답이 세션 기억과 영구 학습(learn.py)을 구분해 명시. baseline은 두 계약에서 그대로 실패(S03: 되묻지 않고 데모 수치 나열, S04: 학습 루프 부재) — 프롬프트의 부가가치가 계약 단위로 측정됨. |

## 계약 추가 기준
- 새 계약은 **한 번 실제로 깨진 행동**에서 만든다 (가상의 규칙 금지 — 오버피팅 방지).
- forbid regex는 좁게: 나쁜 행동의 *단정 패턴*만 잡고, 올바른 행동(기준선 인용·예시 수치)을 오탐하지 않는지
  round-1 응답으로 교차 확인 후 커밋.
- baseline arm은 유지한다 — 계약이 "프롬프트 없이도 다 통과"라면 계약이 무의미하다는 신호.
