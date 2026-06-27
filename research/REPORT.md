# 🧠 MADOBI — 실험 리포트 (Smartest-Agent Lab)

> Claude Code를 "가장 똑똑하게" 만드는 운영 매뉴얼을 **스웜 최적화 + 팀 모드**로 탐색한 실험.
> 진화적 프롬프트 최적화 · 코드 검증 벤치마크 · 다중 팀 병렬.

```
┌──────────────────────────────────────────────────────────────────┐
│  GOAL    도구 없는 추론력을 최대로 끌어올리는 에이전트 운영 매뉴얼   │
│  METHOD  집단 생성(112) → 스웜 평가 → 적합도 → 선별 → 결선 (GA)     │
│  SCORING 코드로 검증된 20문항, 결정론적 이진 채점                    │
│  TEAMS   Planner · Designer · Evaluator Swarm · Analyst · Critic    │
│          · Synthesizer · Report Designer                            │
└──────────────────────────────────────────────────────────────────┘
```

## 1. 파이프라인 한눈에
```
 [Gen0] 시드 4종(C0~C3) ─▶ [Gen1] 10문항 평가
                               │  발견: naive 분해는 무거운 산술에서 ↓, 검증은 ↑
                               ▼
 벤치마크 20문항으로 확장 + 블로그 노하우(KNOWHOW.md) 흡수
                               │
                               ▼
 [Gen2] Designer 스웜 14계열 × 8 = 112 설계 생성
                               │
                               ▼
 스크리닝: 112설계 × 어려운 10문항 (5샤드 병렬, +SEED-20)
                               │  만점 13종, 검증(F02)계열 최강
                               ▼
 결선: 상위 12종 × 전체 20문항 (단일 워크플로)  ← 진행/완료
                               │
                               ▼
 챔피언 ─▶ .claude/agents/smartest.md (스웜/팀 오케스트레이터)
```

## 2. 핵심 발견
1. **검증(verification) 계열이 지배적.** 112종 중 풀커버리지 만점 13종, 그 다수가
   F02_verify(독립 재검증/베이즈표/세표결/보수계산). "분해 + 독립 재검증"이 가장 견고.
2. **무거운 산술이 유일한 변별점.** 점수 손실은 거의 전부 P4(콜라츠 합 8418)에서 발생
   (단일패스 분해가 8378/8410/9693 등으로 실수). → 계산 위생·다수결·코드검증이 방어.
3. **모델 자체가 매우 강함.** baseline도 SEED-20에서 다수결 20/20. 따라서 "스마트함"의 실익은
   평균 정확도보다 **견고성(robustness)** — 가끔의 산술 실수를 검증으로 0으로 만드는 것.
4. **팀/병렬 운영의 현실 제약.** 6팀 동시(~1360노드)는 서버 레이트리밋 유발 → 동시 팀 1~2개로 제한.

## 3. 스크리닝 상위 (어려운 10문항, 만점·풀커버리지)
F02_verify_smallcase, F02_verify_dual_track, F01_decomp_b, F02_verify_bayes_table,
F11_metacog_b, F01_decomp_c, F01_decomp_h, F02_verify_three_vote, F01_decomp_d,
F03_adversarial_c, F02_verify_complement, F02_verify_invert, F01_decomp_e

## 4. 결선 & 챔피언
- **결선(20문항)**: 20/20 만점 4종 = F02_verify_smallcase, F02_verify_dual_track, **F03_adversarial_c**, C2_selfverify. (실패 0)
- **결정전(오류多 6문항 × 5시행)**: 단일샷 **F03_adversarial_c 29/30**·C2_selfverify 29/30 공동 최강.
  **다수결 시 4종 전부 6/6 완벽** → 검증+self-consistency가 무거운 산술 슬립을 0으로.
- **🏆 챔피언 = `F03_adversarial_c`** (적대적 자기반박). 배포 레시피 = **검증 스웜 + 다수결(3)**.
- 일반 챔피언(SWARM-SOLVER) → 마케팅 특화(MADOBI)로 도메인 적용.

## 4-b. 경쟁우위 (vs Hermes Agent · Pi Agent)
기존 에이전틱 시스템은 둘 다 **단일 에이전트 루프**:
- **Hermes Agent**(Nous): 영속 메모리 + 자율 스킬 생성 + 강한 함수호출/구조화 추론, "grows with you".
- **Pi Agent**: 미니멀 4툴 코어 + 공격적 확장성 + 자기문서화.

SWARM-SOLVER의 4축 우위 (상세 `ADVANTAGES.md`):
1. **증거기반 전략** — 손튜닝이 아니라 112후보 × 코드검증 벤치마크로 4세대 진화선별.
2. **검증 스웜 견고성** — Doer–Verifier로 잔여 산술·함정 오류를 0으로(검증계열 3세대 무실점).
3. **병렬 다중 에이전트** — 단일 루프 대비 팬아웃 커버리지/처리량.
4. **복리형 자기개선** — 코드검증 피드백으로 누적되는 KNOWHOW.
그들의 강점(영속메모리·스킬생성·구조화 스크래치패드·미니멀 확장코어)은 흡수.

## 5. 산출물
| 파일 | 내용 |
|------|------|
| `.claude/agents/smartest.md` | **챔피언 에이전트** — 스웜/팀 오케스트레이터(+경쟁우위 레이어) |
| `ADVANTAGES.md` | Hermes·Pi 대비 경쟁우위 분석 |
| `.claude/agents/madobi.md` | **마케팅 특화 에이전트** (정합성·소재·성장형 메모리) |
| `.claude/skills/marketing-analyst/SKILL.md` | **스킬화** — 루틴 마케팅 업무 자동화 |
| `marketing/STRATEGY.md` | 마케팅 에이전트 전략 |
| `marketing/METRICS.md` | 지표 공식 + **정합성 불변식**(놀리지에셋) |
| `marketing/CREATIVE_PLAYBOOK.md` | 소재 기획·생성·점검 플레이북 |
| `marketing/MEMORY_PROTOCOL.md` | 성장형 놀리지에셋 + 히스토리 기록 규칙 |
| `marketing/reconcile.py` | **정합성 검산 엔진**(동작·검증됨) |
| `marketing/knowledge/`, `history/` | 계정별 성장형 자산 |
| `optimization_log.md` | 스웜 최적화 운영 일지(과정·교훈 기록) |
| `KNOWHOW.md` | 누적 지식베이스(쓸수록 최적화) |
| `TEAM.md` | 팀 조직도 |
| `benchmark/` | 코드 검증 20문항 + 정답 |
| `results/` | 세대별 원자료·랭킹 |

## 6. 재현
```bash
python benchmark/build_benchmark.py          # 정답 생성(검증)
python make_eval_script.py --designs results/finalists.json --pids all --trials 1 \
       --name finals --out results/finals.js # 평가 스크립트(LF-only, ASCII)
# results/finals.js 를 Workflow로 실행 → .output
python merge_and_rank.py --pids all <out>    # 병합·채점·랭킹
```

## 7. 인프라 교훈 (재현성 핵심)
- **`args`는 문자열로 도착** → 스크립트에서 `JSON.parse(args)`.
- **Python `write_text`의 CRLF(`\r`)가 Workflow 권한훅에 차단됨** → `newline="\n"`로 LF 전용.
- **워크플로당 누적 1000 에이전트 상한** → 대규모는 샤드 분할.
- **동시 팀은 1~2개** → 과도한 팬아웃은 레이트리밋.
