# 자기개선 루프 (Self-Improvement Loop) — 피드백→학습→레포→깃

> 사용자가 "이건 개선해야 해 / 항상 이렇게 해 / 이게 틀렸어"라고 하면, 에이전트가 그 피드백을
> **자동으로 학습 자산화**하고, 레포에 기록하고, 중앙(공용) 값이면 **깃에 푸시**한다. 쓸수록 똑똑해진다.

## 루프
```
사용자 피드백 ("개선해야 함")
   │
   ▼
[1] 분류  — 범용(global)인가? 특정 계정(account)인가?
   │
   ▼
[2] 승격  — learn.py 가 해당 놀리지에셋에 한 줄(날짜·태그·근거)로 추가
   │         · global → marketing/knowledge/_GLOBAL.md
   │         · account → marketing/knowledge/<account>.md
   ▼
[3] 기록  — FEEDBACK_LOG.md 에 이력 누적(언제·무엇을 배웠나)
   │
   ▼
[4] 중앙 업데이트 — 공용/중앙값이면 git add/commit/push (--commit) → 레포 전체에 반영
   │
   ▼
[5] 적용  — 다음 분석/대화부터 그 자산을 먼저 읽어 즉시 반영 (MEMORY_PROTOCOL)
```

## 사용 (에이전트가 호출)
```bash
# 범용 규칙 학습 + 즉시 중앙 반영(깃 푸시)
python learn.py --feedback "ROAS는 항상 배수(x)로 표기" --scope global --tag report --commit

# 계정 특이값 학습(로컬 기록)
python learn.py --feedback "acme는 25-34 세그먼트가 핵심, 주말 CPA 상승" --scope account --account acme
```

## 무엇이 "중앙값(global)"인가
- 모든 계정에 적용되는 규칙: 지표 표기, 정합성 점검 순서, 리포트 형식 기본값, 플랫폼 공통 함정.
- 반대로 계정 기준선·세그먼트·금칙어·선호 포맷은 account 범위.

## 원칙
- **검증된 것만 승격**: 추측이 아니라 사용자가 명시했거나 정합성 검산을 통과한 교훈만.
- 한 줄 = 한 교훈(날짜·태그·근거). 중복은 갱신.
- 중앙 업데이트는 `--commit`으로 git에 남겨 **레포가 곧 조직의 공용 지식**이 된다.
- 민감정보(고객 실데이터·키)는 자산에 올리지 않는다(공개 레포 안전).
