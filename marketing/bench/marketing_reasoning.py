"""
Gen5 — marketing-reasoning benchmark. Closed-book word problems where the agent must compute
marketing metrics correctly (the real pain point). Answers are computed by code -> deterministic.
Outputs marketing/bench/reasoning/{problems.json, answers.json}.
"""
import json
from pathlib import Path
from fractions import Fraction

OUT = Path(__file__).parent / "reasoning"
OUT.mkdir(parents=True, exist_ok=True)
problems, answers = [], {}

def add(pid, prompt, fmt, ans):
    problems.append({"id": pid, "group": "marketing", "prompt": prompt, "format": fmt})
    answers[pid] = str(ans)

add("M1", "광고비 1,800,000원, 클릭 3,600회일 때 CPC(클릭당 비용, 원)는?", "정수(원)", 1800000//3600)
add("M2", "광고비 1,800,000원, 노출 120,000회일 때 CPM(1000노출당 비용, 원)은?", "정수(원)", 1800000*1000//120000)
add("M3", "매출 5,400,000원, 광고비 1,800,000원일 때 ROAS(배수)는? 소수 첫째자리.", "소수 한자리 (예: 2.5)", f"{5400000/1800000:.1f}")
add("M4", "전환 180건, 광고비 1,800,000원일 때 CPA(전환당 비용, 원)는?", "정수(원)", 1800000//180)
add("M5", "캠페인 A: 노출 100,000 클릭 2,000. 캠페인 B: 노출 300,000 클릭 3,000. "
        "두 캠페인을 합친 '가중' CTR(%)은? 소수 둘째자리. (단순평균 금지)", "퍼센트 소수 둘째자리 (예: 1.25)",
    f"{(2000+3000)/(100000+300000)*100:.2f}")
add("M6", "총예산 30,000,000원, 하루 광고비 1,500,000원으로 일정할 때 예산 소진까지 며칠 걸리나?", "정수(일)", 30000000//1500000)
add("M7", "목표 CPA가 8,000원이고 전환율(CVR)이 4%일 때, 허용 가능한 최대 CPC(원)는?", "정수(원)", int(8000*0.04))
add("M8", "채널별 광고비가 1,200,000 / 900,000 / 1,250,000 / 150,000원이다. 보고서 총합은 3,600,000원으로 적혀있다. "
        "실제 합계와의 차이(원)는?", "정수(원, 차이의 절대값)", abs(3600000-(1200000+900000+1250000+150000)))
add("M9", "매출 5,400,000원, 광고비 1,800,000원일 때 ROI(%)는? (ROI=(매출-비용)/비용)", "정수(%)",
    int((5400000-1800000)/1800000*100))
add("M10", "총노출 600,000회, 도달(reach) 150,000명일 때 평균 빈도(frequency)는?", "정수", 600000//150000)

(OUT/"problems.json").write_text(json.dumps(problems, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT/"answers.json").write_text(json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"built {len(problems)} marketing problems")
for p in problems: print(" ", p["id"], "=>", answers[p["id"]])
