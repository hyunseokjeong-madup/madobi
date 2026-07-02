# MODULES — 단일 레포 안의 모듈 경계

매도비는 **단일 레포(single repo)** 다. 모듈은 *문서상으로만* 구분되며 **물리적으로 분리되지 않는다.**
아래 5개 모듈은 폴더 경계일 뿐, 별도 패키지/별도 git 레포가 아니다.

| 모듈 | 경로 | 한 줄 |
|------|------|------|
| `madobi-core` | `marketing/reconcile.py`, `summarize.py`, `bench/`, (safemath) | 결정론적 stdlib 산술·검산 |
| `madobi-pm-tools` | `marketing/pm/` (78개) | CLI 의사결정 도구 모음 |
| `madobi-knowledge` | `marketing/knowledge/` (210+ md, 25 카테고리) | 쓸수록 자라는 지식 자산 |
| `madobi-agent` | `.claude/` (agents + skills) | 에이전트 페르소나·스킬 |
| `madobi-research` | `research/` | 챔피언 전략 선별 실험 아카이브 (IP) |

---

## 왜 단일 레포인가 (분리하지 않는 이유)

에이전트(`madobi-agent`)는 런타임에 `.claude/` 와 `marketing/` 를 **함께 자동 로드**한다.
스킬은 `marketing/pm/*.py` 를 직접 호출하고, 답변 근거를 `marketing/knowledge/*.md` 에서 끌어온다.
이 둘을 별도 레포로 쪼개면:

- `clone & run` 이 깨진다 — 사용자가 N개 레포를 정확한 버전으로 맞춰야 동작.
- `tests/run_all.py` 의 전체-그린 게이트가 레포 경계를 넘어 깨진다 (도구·샘플·검산이 한 트리에 있어야 결정론적).
- `learn.py` 의 자기개선 루프(피드백 → 자산 → 커밋)가 한 트리 안에서만 원자적으로 돈다.

→ **결론: 문서로 모듈을 나누되 물리적으로는 한 레포.** 멀티레포 분리는 채택하지 않았다.

---

## `madobi-core`
- **무엇:** 정합성 검산 + 집계 엔진. 분해합(일/채널/캠페인/소재) = 총계를 **정확히** 보장.
  파생지표(ROAS/CPA/CVR…)는 원자료 재계산 + 역산 일치. 비율은 가중평균(Σ/Σ).
- **공개 인터페이스:** `python marketing/reconcile.py <csv>`, `python marketing/bench/summarize.py <csv> --by <dim>`,
  `marketing/bench/verify_bench.py`(대규모 EXACT 검증), `bench/levels.py`(40단계 난이도 사다리 — 함정 포함).
  단일 진입점은 `python marketing/madobi.py list|chat|<tool>` — 디스패처(오타 시 유사 도구 제안) +
  챗봇 REPL(`chat.py`, 결정론 NL→도구 라우터 · 지표 Q&A · 놀리지 회상).
  `marketing/safemath.py` — 0-분모 안전 나눗셈·지표별 허용오차 헬퍼(stdlib). `reconcile.py` 의 검산
  로직을 ADDITIVE 하게 떼어낸 모듈로, `reconcile.py` 는 그대로 동작하고 새 도구가 골라 쓴다.
- **불변식:** **결정론적 · stdlib only.** API/네트워크/난수 없음. 같은 입력 → 같은 출력.
  외부 라이브러리 0개. (가속용 duckdb 는 OPT-IN extra, 없어도 stdlib 경로로 동작.)

## `madobi-pm-tools` (`marketing/pm/`, 78개)
- **무엇:** ROAS 민감도·페이싱·퍼널·A/B·재배분·가드레일·낭비탐지·예측 등 PM 의사결정 CLI.
- **공개 인터페이스:** 각 도구 = 단일 파일. `python marketing/pm/<tool>.py --<args>` → 텍스트 표
  (기계가독이 필요한 도구는 `--json` stdout — reconcile.py·`madobi.py list --json` 이 선례.
  신규/개정 도구는 점진적으로 이 규약을 따른다: `json.dumps(payload, ensure_ascii=False, sort_keys=True)`).
  각 도구는 `tests/run_all.py` 의 `CHECKS` 에 한 줄로 등록되어 PASS 토큰을 가진다.
- **불변식:** 폐형식이면 정확, 추정이면 가정 명시. stdlib only(표준편차·회귀도 `math` 로 직접 구현).

## `madobi-knowledge` (`marketing/knowledge/`, 210+ md / 25 카테고리, 쓸수록 증가)
- **무엇:** 버티컬·포맷·함정·채널·루틴별 실전 지식. `_GLOBAL.md`(공통) + `<account>.md`(계정별).
- **공개 인터페이스:** 시드/생성은 `build_kb*.py`. 접근면은 **search / recall / curate** 3개 stdlib 진입점:
  - `search.py` — 질의로 자산 찾기(SQLite FTS5/bm25). FTS5 가 없으면 graceful degrade.
  - `recall.py` — 답변 시 붙여넣을 근거 블록(무상태). 인덱스 있으면 사용, 없으면 grep 폴백.
  - `curate.py` — 검증된 교훈만 UPSERT/승급 + 계정 온보딩(append 하는 `learn.py` 의 자매).
  - `add_frontmatter.py` — frontmatter 백필. frontmatter 는 검색용 메타이며 본문 규약을 바꾸지 않는다.
  전부 외부 의존성 0 — 없어도 코어·도구는 독립 동작.
- **불변식:** 추측 금지 — 정합성 검산을 통과한 교훈만 누적. 한 줄 + 근거. 중복은 갱신.

## `madobi-agent` (`.claude/`)
- **무엇:** 에이전트 페르소나(`agents/madobi.md`, `agents/smartest.md`) + 스킬(`skills/marketing-analyst`).
- **공개 인터페이스:** Claude Code 가 레포를 열 때 `.claude/` 를 자동 로드 → 스킬이 `marketing/` 의 도구·지식을 호출.
- **불변식:** 산술은 코어(코드)에 위임, 판단만 LLM. 에이전트는 숫자를 직접 만들지 않고 검산된 결과를 인용.

## `madobi-research` (`research/`)
- **무엇:** 챔피언 전략이 *어떻게 선별됐는지*의 실험 아카이브 (스웜 최적화 Gen0~5, 벤치마크, 결과).
- **공개 인터페이스:** 제품 사용에는 불필요. 방법론·재현용. `research/README.md` 가 입구.
- **불변식:** **IP 페이퍼트레일 — 보존(PRESERVED). 삭제·정리 금지.**

---

## 데이터 추적 결정 — `dataset.csv` (의도된 결정)

`marketing/bench/dataset.csv` 와 `ground_truth.json` 은 **재생성 가능한(regenerable) 벤치마크 산출물**이다.
따라서 git 으로 추적하지 **않는다** — `.gitignore` 에 의도적으로 등재되어 있다:

```
# Large regenerable benchmark artifacts (recreate via marketing/bench/gen_dataset.py)
marketing/bench/dataset.csv
marketing/bench/ground_truth.json
```

이유:
- 결정론적 생성기(`gen_dataset.py`, `--rows N`)가 있으므로 산출물을 박제할 필요가 없다.
  레포에 대용량 CSV 를 넣으면 클론이 무거워지고 diff 가 오염된다.
- 대신 **생성기와 검증기(`verify_bench.py`)를 추적**한다 → 누구든 같은 데이터를 재현하고 EXACT 검증 가능.
- `research/results/`(재현 증거)는 반대로 **추적 유지** — IP/재현성 증거이기 때문(가치 ≠ 크기).

`.gitattributes` 에는 그럼에도 `*.csv text` 규칙을 둔다: 추적되는 CSV(예: `marketing/samples/*.csv`)의
줄바꿈(LF)·diff 일관성을 보장하기 위함이다. (자세한 건 `DATA.md`.)

> 요약: **재생성 가능 = 미추적**(dataset.csv), **재현 증거/샘플 = 추적**(results/, samples/).
> 추적되는 모든 CSV 는 `*.csv text` 로 텍스트(LF) 정규화한다.
