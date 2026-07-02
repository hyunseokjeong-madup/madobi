# DATA — 데이터 추적 정책

매도비가 어떤 데이터 파일을 git 으로 추적하고/안 하는지, 그리고 그 이유.

## 원칙

> **재생성 가능 = 미추적. 재현 증거·테스트 입력 = 추적.**

| 데이터 | 위치 | 추적? | 이유 |
|--------|------|-------|------|
| `dataset.csv` | `marketing/bench/` | ❌ 미추적 (`.gitignore`) | 결정론적 생성기로 언제든 재생성 |
| `ground_truth.json` | `marketing/bench/` | ❌ 미추적 (`.gitignore`) | `dataset.csv` 와 함께 재생성 |
| 샘플 CSV (`sample_*.csv`) | `marketing/samples/` | ✅ 추적 | 테스트·도구의 결정론적 입력 — 고정돼야 통합 체크 전체가 성립 |
| 결과 데이터 | `research/results/` | ✅ 추적 | 스웜 최적화 재현 증거(IP) — `.gitignore` 에서 명시적 제외 |

## `dataset.csv` — 의도적으로 추적하지 않는다

`marketing/bench/dataset.csv`(와 `ground_truth.json`)는 **재생성 가능한 대용량 벤치마크 산출물**이다.

```bash
# 누구든 동일 데이터를 재현
python marketing/bench/gen_dataset.py --rows 30000
# 집계가 대규모에서도 EXACT 임을 검증
python marketing/bench/verify_bench.py     # -> ALL ...
```

레포에는 **산출물 대신 생성기·검증기를 박제**한다. 이렇게 하면:
- 클론이 가벼워지고, 대용량 CSV diff 가 PR 을 오염시키지 않는다.
- "데이터를 신뢰하라"가 아니라 "데이터를 재현하라"가 된다 — 재현성이 곧 증거.

`tests/run_all.py` 는 매 실행 시 `gen_dataset.py` 를 먼저 돌려 데이터를 새로 만들고 검증하므로,
산출물을 추적하지 않아도 통합 체크 게이트는 항상 성립한다 (개수는 run_all.py 가 진실).

## CSV 정규화 — `.gitattributes`

추적되는 CSV 는 `*.csv text` 규칙으로 **텍스트(LF)** 정규화한다(`.gitattributes`).
OS 간 줄바꿈 차이로 diff 가 흔들리거나, 결정론적 입력의 바이트가 바뀌는 것을 막는다.
미추적인 `dataset.csv` 에는 영향이 없다(어차피 커밋되지 않음) — 규칙은 추적 CSV 의 위생을 위한 것.
