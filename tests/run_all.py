"""
MADOBI integration check — runs every deterministic guarantee and reports green/red.
Use before committing so "다 통과" stays true. No API, no network.

  python tests/run_all.py
"""
import subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHECKS = [
    ("benchmark ground truth builds", ["python", "research/benchmark/build_benchmark.py"], "built 20 problems"),
    ("large dataset generates",       ["python", "marketing/bench/gen_dataset.py", "--rows", "30000"], "ground_truth.json"),
    ("aggregation is EXACT at scale", ["python", "marketing/bench/verify_bench.py"], "ALL"),
    ("30-level difficulty ladder",    ["python", "marketing/bench/levels.py"], "ALL LEVELS PASS"),
    ("summarize tool runs",           ["python", "marketing/bench/summarize.py", "marketing/sample_campaign.csv", "--by", "creative"], "SUMMARY"),
    ("creative analyzer runs",        ["python", "marketing/analyze_creatives.py", "marketing/sample_campaign.csv"], "CREATIVE ANALYSIS"),
    ("creative generator runs",       ["python", "marketing/creative_gen.py", "--product", "x", "--n", "3"], "CREATIVE MATRIX"),
    ("event analyzer runs",           ["python", "marketing/event_analysis.py", "marketing/sample_timeseries.csv", "--metric", "revenue", "--event", "2026-01-10"], "EVENT/CAMPAIGN ANALYSIS"),
    ("report generator runs",         ["python", "marketing/report.py", "marketing/sample_campaign.csv", "--by", "creative"], "성과 리포트"),
    ("pm: pacing",                    ["python", "marketing/pm/pacing.py", "--spend", "100", "--budget", "200", "--elapsed", "5", "--total", "10"], "PACING"),
    ("pm: funnel",                    ["python", "marketing/pm/funnel.py", "--csv", "marketing/sample_campaign.csv"], "FUNNEL"),
    ("pm: abtest",                    ["python", "marketing/pm/abtest.py", "--a-n", "1000", "--a-x", "50", "--b-n", "1000", "--b-x", "70"], "A/B TEST"),
    ("pm: reallocate",                ["python", "marketing/pm/reallocate.py", "marketing/sample_campaign.csv", "--by", "creative"], "REALLOCATION"),
    ("pm: guardrails",                ["python", "marketing/pm/guardrails.py", "marketing/sample_campaign.csv", "--by", "creative", "--target-roas", "2.5"], "GUARDRAILS"),
    ("pm: waste",                     ["python", "marketing/pm/waste.py", "marketing/sample_campaign.csv", "--by", "creative", "--min-roas", "2.5"], "WASTE FINDER"),
    ("pm: dow heatmap",               ["python", "marketing/pm/dow_heatmap.py", "marketing/sample_timeseries.csv", "--metric", "revenue"], "HEATMAP"),
    ("pm: forecast",                  ["python", "marketing/pm/forecast.py", "marketing/sample_timeseries.csv", "--total-days", "30"], "FORECAST"),
    ("pm: poas",                      ["python", "marketing/pm/poas.py", "--revenue", "100", "--spend", "50", "--margin", "0.3"], "POAS"),
    ("pm: frequency",                 ["python", "marketing/pm/frequency.py", "--impressions", "600", "--reach", "150"], "FREQUENCY"),
    ("pm: ltv_payback",               ["python", "marketing/pm/ltv_payback.py", "--cac", "30000", "--arpu", "15000"], "PAYBACK"),
    ("pm: naming_check",              ["python", "marketing/pm/naming_check.py", "--names", "CMP_benefit_video_number_v01"], "NAMING CHECK"),
    ("pm: search_terms",              ["python", "marketing/pm/search_terms.py", "marketing/sample_searchterms.csv"], "SEARCH TERMS"),
    ("pm: channel_mix",               ["python", "marketing/pm/channel_mix.py", "marketing/sample_campaign.csv", "--by", "creative"], "CHANNEL MIX"),
    ("pm: alert_digest",              ["python", "marketing/pm/alert_digest.py", "marketing/sample_campaign.csv", "--by", "creative", "--target-roas", "2.5"], "DAILY DIGEST"),
    ("pm: mer",                       ["python", "marketing/pm/mer.py", "--revenue", "300", "--spend", "100"], "MER"),
    ("pm: seasonality",               ["python", "marketing/pm/seasonality.py", "marketing/sample_timeseries.csv", "--metric", "revenue"], "SEASONALITY INDEX"),
    ("pm: attribution_compare",       ["python", "marketing/pm/attribution_compare.py", "marketing/sample_attribution.csv", "--a-col", "platform_conv", "--b-col", "ga_conv"], "ATTRIBUTION COMPARE"),
    ("pm: rotation",                  ["python", "marketing/pm/rotation.py", "marketing/sample_campaign.csv", "--min-impr", "30000"], "CREATIVE ROTATION"),
    ("kb: build_kb",                  ["python", "marketing/knowledge/build_kb.py"], "generated"),
    ("kb: build_kb2",                 ["python", "marketing/knowledge/build_kb2.py"], "generated"),
    ("kb: build_kb3",                 ["python", "marketing/knowledge/build_kb3.py"], "generated"),
    ("kb: build_kb4",                 ["python", "marketing/knowledge/build_kb4.py"], "generated"),
    ("bench: reasoning2",             ["python", "marketing/bench/reasoning2.py"], "built 40"),
    ("kb: build_kb5",                 ["python", "marketing/knowledge/build_kb5.py"], "generated"),
    ("bench: reasoning3",             ["python", "marketing/bench/reasoning3.py"], "built 18"),
    ("sc: mta",                       ["python", "marketing/pm/attribution_mta.py", "marketing/sample_paths.csv"], "MULTI-TOUCH"),
    ("sc: budget_optimizer",          ["python", "marketing/pm/budget_optimizer.py", "marketing/sample_campaign.csv", "--by", "creative"], "BUDGET OPTIMIZER"),
    ("sc: sample_size",               ["python", "marketing/pm/sample_size.py", "--baseline", "0.04", "--mde", "0.2"], "SAMPLE SIZE"),
    ("sc: cohort",                    ["python", "marketing/pm/cohort.py", "marketing/sample_cohorts.csv"], "COHORT RETENTION"),
    ("sc: anomaly_ts",                ["python", "marketing/pm/anomaly_ts.py", "marketing/sample_timeseries.csv", "--metric", "revenue"], "TS ANOMALY"),
    ("sc: mmm",                       ["python", "marketing/pm/mmm.py", "marketing/sample_mmm.csv", "--channels", "meta,google,naver"], "MMM (OLS"),
    ("sc: geo_lift",                  ["python", "marketing/pm/geo_lift.py", "marketing/sample_geo.csv"], "GEO INCREMENTALITY"),
    ("sc: rfm",                       ["python", "marketing/pm/rfm.py", "marketing/sample_tx.csv", "--asof", "2026-01-31"], "RFM"),
    ("sc: cluster_terms",             ["python", "marketing/pm/cluster_terms.py", "marketing/sample_searchterms.csv"], "SEARCH-TERM CLUSTERS"),
    ("sc: dashboard",                 ["python", "marketing/pm/dashboard.py", "marketing/sample_campaign.csv", "--by", "creative", "--out", "docs/demo/dashboard.html"], "DASHBOARD"),
    ("sc: bid_sim",                   ["python", "marketing/pm/bid_sim.py", "marketing/sample_landscape.csv", "--value", "50000", "--cvr", "0.05"], "BID SIMULATOR"),
    ("sc: ltv_forecast",              ["python", "marketing/pm/ltv_forecast.py", "marketing/sample_retention.csv", "--arpu", "10000", "--horizon", "6"], "LTV FORECAST"),
    ("sc: pacing_optimizer",          ["python", "marketing/pm/pacing_optimizer.py", "--budget", "30000000", "--spent", "12000000", "--remaining-days", "6"], "PACING OPTIMIZER"),
    ("sc: kpi_decomp",                ["python", "marketing/pm/kpi_decomp.py", "--cpc-a", "500", "--cvr-a", "0.05", "--cpc-b", "600", "--cvr-b", "0.04"], "KPI DECOMPOSITION"),
    ("sc: price_elasticity",          ["python", "marketing/pm/price_elasticity.py", "marketing/sample_pq.csv"], "PRICE ELASTICITY"),
    ("sc: promo_roi",                 ["python", "marketing/pm/promo_roi.py", "--baseline-units", "1000", "--price", "50000", "--margin", "0.4", "--discount", "0.2", "--uplift", "0.5"], "PROMO ROI"),
    ("sc: market_basket",             ["python", "marketing/pm/market_basket.py", "marketing/sample_baskets.csv", "--min-support", "0.2"], "MARKET BASKET"),
    ("sc: churn_score",               ["python", "marketing/pm/churn_score.py", "marketing/sample_tx.csv", "--asof", "2026-02-15"], "CHURN RISK"),
    ("sc: new_vs_returning",          ["python", "marketing/pm/new_vs_returning.py", "marketing/sample_tx.csv"], "NEW vs RETURNING"),
    ("sc: data_quality",              ["python", "marketing/pm/data_quality.py", "marketing/sample_dirty.csv"], "DATA QUALITY"),
    ("sc: shapley_attribution",       ["python", "marketing/pm/shapley_attribution.py", "marketing/sample_paths.csv"], "SHAPLEY ATTRIBUTION"),
    ("sc: conversion_lag",            ["python", "marketing/pm/conversion_lag.py", "marketing/sample_lag.csv"], "CONVERSION LAG"),
    ("sc: incrementality_ab",         ["python", "marketing/pm/incrementality_ab.py", "--test-n", "100000", "--test-conv", "3000", "--control-n", "100000", "--control-conv", "2500"], "INCREMENTALITY"),
    ("sc: tools_index",               ["python", "marketing/pm/tools_index.py"], "TOOLS index"),
    ("sc: price_optimizer",           ["python", "marketing/pm/price_optimizer.py", "--cost", "10000", "--elasticity", "-2"], "PRICE OPTIMIZER"),
    ("sc: saturation_fit",            ["python", "marketing/pm/saturation_fit.py", "marketing/sample_curve.csv"], "SATURATION FIT"),
    ("sc: revenue_waterfall",         ["python", "marketing/pm/revenue_waterfall.py", "marketing/sample_rev2.csv"], "REVENUE WATERFALL"),
    ("sc: budget_response_alloc",     ["python", "marketing/pm/budget_response_alloc.py", "marketing/sample_params.csv", "--budget", "30000000"], "BUDGET RESPONSE"),
    ("harness: madobi dispatcher",    ["python", "marketing/madobi.py", "list"], "MADOBI 도구"),
    ("sc: seasonal_forecast",         ["python", "marketing/pm/seasonal_forecast.py", "marketing/sample_timeseries.csv", "--metric", "revenue", "--days", "5"], "SEASONAL FORECAST"),
    ("sc: pareto",                    ["python", "marketing/pm/pareto.py", "marketing/sample_campaign.csv", "--value", "revenue"], "PARETO"),
    ("sc: hhi",                       ["python", "marketing/pm/hhi.py", "marketing/sample_campaign.csv", "--value", "spend"], "CONCENTRATION"),
    ("sc: cohort_heatmap",            ["python", "marketing/pm/cohort_heatmap.py", "marketing/sample_cohorts.csv", "--out", "docs/demo/cohort_heatmap.html"], "COHORT HEATMAP"),
    ("sc: winback_priority",          ["python", "marketing/pm/winback_priority.py", "marketing/sample_tx.csv", "--asof", "2026-02-15"], "WINBACK PRIORITY"),
    ("sc: scorecard",                 ["python", "marketing/pm/scorecard.py", "marketing/sample_campaign.csv", "--weights", "roas:0.5,ctr:0.3,conversions:0.2"], "SCORECARD"),
    ("sc: confidence_interval",       ["python", "marketing/pm/confidence_interval.py", "--conv", "50", "--n", "1000"], "CONFIDENCE INTERVAL"),
    ("sc: forecast_accuracy",         ["python", "marketing/pm/forecast_accuracy.py", "marketing/sample_af.csv"], "FORECAST ACCURACY"),
    ("sc: target_setter",             ["python", "marketing/pm/target_setter.py", "--target-roas", "3", "--aov", "50000", "--cvr", "0.05"], "TARGET SETTER"),
]

def run():
    print("=" * 60)
    print(" MADOBI integration checks")
    print("=" * 60)
    results = []
    for name, cmd, needle in CHECKS:
        t0 = time.time()
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        ok = (r.returncode == 0) and (needle in (r.stdout or ""))
        dt = time.time() - t0
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}  ({dt:.1f}s)")
        if not ok:
            print("    cmd:", " ".join(cmd))
            tail = (r.stdout or "")[-400:] + (r.stderr or "")[-400:]
            print("    " + tail.replace("\n", "\n    "))
        results.append(ok)
    print("=" * 60)
    n = sum(results)
    if all(results):
        print(f" ✅ ALL {n}/{len(results)} CHECKS GREEN")
        return 0
    print(f" ❌ {n}/{len(results)} green — fix before commit")
    return 1

if __name__ == "__main__":
    sys.exit(run())
