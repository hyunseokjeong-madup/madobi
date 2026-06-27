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
