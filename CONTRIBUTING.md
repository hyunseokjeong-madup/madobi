# Contributing to MADOBI

매도비는 **"쓸수록 자라는"** 에이전트다. 기여 = 자산을 한 줄씩 누적하는 것.
세 가지 길이 있다: **놀리지에셋 추가**, **PM 도구 추가**, **피드백 통합**.

---

## 0. 기여의 단일 합격선 — ALL CHECKS GREEN

무엇을 바꾸든, 머지 전에 통합 체크가 전부 통과해야 한다. 이게 유일한 게이트다.

```bash
python tests/run_all.py
# 마지막 줄이 반드시:  ✅ ALL N/N CHECKS GREEN (개수 N 은 계속 는다 — 전부 green 이 합격선)
```

빨간 줄이 하나라도 있으면 그 PR 은 받지 않는다. (API·네트워크 없이 결정론적으로 돈다.)

### 코어는 STDLIB ONLY (절대 불변식)
- 코어(reconcile / summarize / bench / pm 도구 / 검증 로직)는 **파이썬 표준 라이브러리만** 쓴다.
  허용: `csv, json, sqlite3, math, re, pathlib, argparse, datetime, collections, urllib, hashlib`.
- 외부 의존성(duckdb, sentence-transformers 등)은 **`pyproject.toml` 의 extras 로** 들어간다.
  코어에서 쓸 때는 반드시 `try/except ImportError` 로 감싸 **없어도 import 되고 degrade** 해야 한다.
- 이유: `clone & run` — 매도비는 `pip install` 없이도 동작하는 게 제품 약속이다.

---

## 1. 놀리지에셋 추가 (`marketing/knowledge/`)

지식 자산 = 검산을 통과한 교훈 1개 = `.md` 파일 1개. 카테고리 폴더 아래에 둔다
(`verticals/`, `formats/`, `pitfalls/`, `channels/`, `routines/`, `metrics/`, … 25개 카테고리).

**형식** (md + 선택적 YAML frontmatter):

```markdown
---
title: 제목
category: pitfalls
tags: [roas, attribution]
---
# 제목 (무엇에 대한 자산인지 한 줄)

## 핵심 KPI
- 항목 1

## 함정
- 플랫폼 ROAS 는 중복귀속 → 실매출 대사  ← 반드시 "근거/검산" 을 동반
```

frontmatter 가 없는 기존 파일에는 `python marketing/knowledge/add_frontmatter.py` 로 백필할 수 있다
(stdlib 전용, 제목/카테고리/태그를 경로에서 유추). frontmatter 는 `search.py` 인덱싱을 돕지만 필수는 아니다.

규칙(`_GLOBAL.md` 의 헌법):
- **추측 금지.** 정합성 검산을 통과한 교훈만 올린다. 한 줄 + 근거. 중복은 갱신.
- 계정 특이사항은 카테고리가 아니라 `marketing/knowledge/<account>.md` 로.

**curate (선별/승급) 흐름:** 자산은 `build_kb*.py` 로 대량 시드하거나 손으로 추가한 뒤,
범용 경험칙은 계정 데이터로 검증되면 `_GLOBAL.md` 로 **승급(promote)** 한다.
- `python marketing/knowledge/curate.py` — 중복 줄을 UPSERT(재검증 날짜만 갱신)하고 계정을 온보딩한다
  (무조건 append 하는 `learn.py` 의 자매 헬퍼).
- `python marketing/knowledge/search.py --build` / `--query "..."` — SQLite FTS5/bm25 전문검색 (stdlib).
- `python marketing/knowledge/recall.py --query "..."` — 컨텍스트에 붙여넣을 회상 블록 (인덱스 있으면 사용, 없으면 grep 폴백).

---

## 2. PM 도구 추가 (`marketing/pm/`, 현재 78개)

PM 도구 = `argparse` 로 입력 받고 텍스트 표를 찍는 **단일 파일 stdlib 스크립트**.
기존 도구(`roas_sensitivity.py`, `pacing.py`, `funnel.py` …)와 같은 모양을 따른다.

**템플릿:**

```python
"""
<한 줄 설명 — 무엇을, 어떤 공식으로 계산하는지. 폐형식이면 "정확", 추정이면 가정 명시>.

Usage: python <toolname>.py --foo 1 --bar 2
"""
import argparse
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--foo", type=float, required=True)
    a = ap.parse_args()
    print("\n=== <TOOL TITLE> ===")     # ← run_all.py 가 이 헤더 토큰으로 PASS 판정
    # ... 계산은 stdlib 만. 0-분모는 "—" 로, 비율은 가중평균으로.
if __name__ == "__main__":
    main()
```

**등록 (필수):** `tests/run_all.py` 의 `CHECKS` 리스트에 한 줄 추가한다.

```python
("pm: <name>", ["python", "marketing/pm/<name>.py", "--foo", "1"], "<TOOL TITLE>"),
#   라벨            실행 커맨드(인자 포함)                              stdout 에 있어야 할 토큰
```

세 번째 원소(기대 토큰)가 스크립트 출력에 포함되면 PASS. 추가 후 `python tests/run_all.py` 가
**96/96** 으로 늘며 GREEN 이어야 한다. (도구 1개 = 체크 1개.)

원칙: 표준편차/회귀 등도 직접 구현(`math`)한다. numpy/pandas 끌어오지 말 것 — 코어 불변식 위반.

---

## 3. 피드백 통합 (`learn.py`)

사용자가 "앞으로 항상 X 해" / "그건 틀렸어, Y 가 맞아" 라고 하면 그 교훈을 자산으로 박제한다.

```bash
# 전역(모든 계정 공통) 교훈 → _GLOBAL.md 승급 + FEEDBACK_LOG.md 기록
python learn.py --feedback "ROAS는 항상 배수(x)로 표기" --scope global --tag report

# 계정 특이사항 → marketing/knowledge/<account>.md
python learn.py --feedback "A계정은 18-24 세그먼트가 핵심" --scope account --account acmecorp

# 자동 커밋·푸시 끄기
python learn.py --feedback "..." --scope global --no-commit
```

`learn.py` 가 하는 일: (1) 올바른 자산 파일에 한 줄 append → (2) `FEEDBACK_LOG.md` 에 이력 →
(3) (기본 ON) git add/commit/push. **이것이 "쓸수록 자라는" 루프의 입구다.**

---

## PR 체크리스트

- [ ] `python tests/run_all.py` → `✅ ALL N/N CHECKS GREEN` (PM 도구 추가 시 N 이 늘었는지 확인)
- [ ] 코어 변경은 stdlib 만 사용 (외부 의존성은 `pyproject.toml` extras + `try/except`)
- [ ] 놀리지에셋은 추측이 아니라 검산/근거를 동반
- [ ] do-not-break 파일(`tests/run_all.py`, `reconcile.py`, `summarize.py`, `bench/*`, `pm/*`,
      `learn.py`)을 깨지 않음 — 새 파일/새 줄 위주
- [ ] `research/` 는 IP 페이퍼트레일 — 삭제 금지
