# SWARM-SOLVER 경쟁우위 (vs 기존 에이전틱 시스템)

비교 대상: **Hermes Agent** (Nous Research) · **Pi Agent** (Mario Zechner / earendil-works).

## 1. 상대 시스템 요약
### Hermes Agent (Nous Research, 2026.2 오픈소스)
- Hermes 3(2024.8)/Hermes 4(2025.8) 파인튜닝 오픈웨이트 모델 기반.
- 강점: 함수호출 정확도(Hermes 2 Pro 시절 ~90% vs 동급 일반모델 60–70%), XML 구조화 출력,
  스크래치패드, 내부 모놀로그, 단계라벨 추론/계획, Mermaid 다이어그램.
- 런타임: 영속 메모리, **자율 스킬 생성**, 로컬 추론. 슬로건 "the agent that grows with you".
- 한계: 본질적으로 **단일 에이전트 루프**(병렬 검증/다수결 구조 없음).

### Pi Agent (오픈소스 터미널 코딩 에이전트)
- 미니멀 코어: 4개 도구(read/write/edit/bash) + 짧은 시스템 프롬프트.
- 강점: **공격적 확장성**(extensions/skills/packages), 자기문서화, 멀티 제공자(pi-ai/agent-core/tui).
- 포지셔닝: "Claude Code를 능가하는 커스터마이즈 가능 오픈소스 코딩 에이전트".
- 한계: 의도적 미니멀리즘 → **단일 루프**, 복잡 추론의 견고성 보장 장치는 사용자 확장에 의존.

## 2. 우리의 구조적 우위 (단일 루프가 못 가지는 것)
1. **증거기반 전략 선별**: 운영 매뉴얼을 손튜닝이 아니라 **112개 후보를 코드검증 20문항 벤치마크로
   4세대 진화선별**해 얻었다. "이길 것 같은" 게 아니라 **"측정으로 이긴"** 전략.
2. **검증 스웜으로 견고성**: Doer–Verifier 패턴을 내장 — 병렬 Solver(서로 다른 전략) → 적대적 Verifier
   → 다수결 Synthesizer. 실험에서 baseline·decomp 계열도 범하던 **P4 무거운 산술 슬립을 검증 계열만
   3세대 연속 무실점** 통과. 잔여 오류를 0으로.
3. **병렬 다중 에이전트 오케스트레이션**: Hermes/Pi가 단일 루프인 데 비해 우리는 난이도에 비례해
   서브에이전트/워크플로로 **병렬 팬아웃**(계층적). 광범위 감사·마이그레이션·다관점 리뷰에서 처리량·커버리지 우위.
4. **복리형 자기개선**: KNOWHOW.md + optimization_log가 매 세대 교훈을 누적해 다음 설계 생성에 피드백.
   Hermes의 "grows with you"를 **코드검증 피드백 루프**로 구현 → 증거로 검증된 교훈만 승격.

## 3. 그들의 강점을 흡수
- Hermes: 영속 메모리·자율 스킬 생성·구조화 스크래치패드·단계라벨 추론 → 우리 에이전트에 반영.
- Pi: 미니멀·확장 가능 코어·도구 규율 → 코어는 단순, 복잡성은 스킬/서브에이전트로 확장.

## 4. 한 줄 정리
> **"증거로 이긴 전략 × 검증 스웜의 견고성 × 병렬 오케스트레이션 × 복리형 자기개선"**
> — 단일 루프 에이전트(Hermes·Pi)가 구조적으로 따라오기 어려운 4축.

---
출처: Nous Research Hermes 3 / hermes-agent (github.com/nousresearch/hermes-agent),
Hermes 3 Technical Report (arxiv 2408.11857); Pi Agent (pi.dev, github.com/earendil-works/pi).
