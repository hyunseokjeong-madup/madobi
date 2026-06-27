# MADOBI 데모 — 실제 산출물 (Live outputs)

샘플 캠페인 데이터([`marketing/sample_campaign.csv`](../marketing/sample_campaign.csv), 오류를 일부러 심음)에
MADOBI 도구를 돌린 **실제 결과**입니다. 모두 코드로 생성되며 재현 가능합니다.

## 1. 정합성 검산 — 숨은 숫자 오류 적발
```bash
python marketing/reconcile.py marketing/sample_campaign.csv --md docs/demo/reconcile_report.md
```
→ [`docs/demo/reconcile_report.md`](demo/reconcile_report.md). 두 개의 진짜 오류를 잡습니다:
- `C_carousel` CTR **보고 9.9% ≠ 실제 5.0%** (clicks/impr 재계산)
- `[SUM] spend` **행 합계 4,100,000 ≠ 총계행 4,200,000**

> 이것이 "스프레드 요약하면 숫자가 틀린다"를 막는 핵심입니다 — 보고 전에 항상 검산.

## 2. 소재 분석 — 승자/패자 자동 식별
```bash
python marketing/analyze_creatives.py marketing/sample_campaign.csv --kpi roas --min-impr 1000 --md docs/demo/creative_report.md
```
→ [`docs/demo/creative_report.md`](demo/creative_report.md). ROAS 기준 랭킹, 🏆 승자 / 🛑 패자,
소표본 제외, (날짜 있으면) 피로 감지. *CTR은 보고값이 아니라 원자료에서 재계산한 값을 씁니다.*

## 3. 집계 요약 — 가중지표로 정확히
```bash
python marketing/bench/summarize.py marketing/sample_campaign.csv --by creative --md docs/demo/summary_by_creative.md
```
→ [`docs/demo/summary_by_creative.md`](demo/summary_by_creative.md). 분해합=총계가 보장되고,
비율은 가중평균(Σ/Σ)으로 계산됩니다(Simpson 함정 회피).

## 4. 대규모 무실점 (10만 행)
```bash
python marketing/bench/gen_dataset.py --rows 100000 && python marketing/bench/levels.py
# → 29/29 levels PASS — 멀티피벗/필터/top-N/4D 피벗 전부 정확
```

---
*데모 리포트는 도구 실행 시 자동 갱신됩니다. 전체 통합 검증: `python tests/run_all.py`*
