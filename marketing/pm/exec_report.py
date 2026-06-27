"""
임원 요약 리포트 — 한 CSV에서 종합 성과·ROAS 갭·최대 기여자·데이터 품질을 한 장 마크다운으로.
모든 수치 원자료 재계산(검산 가능). 여러 도구의 핵심을 통합한 캡스톤.

입력 CSV: name + impressions,clicks,spend,conversions,revenue
Usage: python exec_report.py data.csv --target-roas 3.0 --md exec.md
"""
import argparse, csv, re
from pathlib import Path
RAWM=["impressions","clicks","spend","conversions","revenue"]
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--target-roas",type=float,default=3.0); ap.add_argument("--md",default=None)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    name=list(rows[0])[0]; h={c.lower():c for c in rows[0]}
    cols={m:h.get(m) for m in RAWM}
    ents=[]; tot={m:0.0 for m in RAWM}; dq=0
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(name) or ""),re.I): continue
        v={m:num(r.get(cols[m])) for m in RAWM}; v["_n"]=(r.get(name) or "").strip()
        if (v["clicks"]>v["impressions"]>0) or (v["conversions"]>v["clicks"]>0): dq+=1
        ents.append(v)
        for m in RAWM: tot[m]+=v[m]
    roas=tot["revenue"]/tot["spend"] if tot["spend"] else 0
    ctr=tot["clicks"]/tot["impressions"] if tot["impressions"] else 0
    cpa=tot["spend"]/tot["conversions"] if tot["conversions"] else 0
    byrev=sorted(ents,key=lambda x:-x["revenue"])
    byroas=sorted(ents,key=lambda x:(x["revenue"]/x["spend"] if x["spend"] else 0))
    gap=sum(max(0,x["spend"]*a.target_roas-x["revenue"]) for x in ents)
    top=byrev[0] if byrev else None; worst=byroas[0] if byroas else None
    L=[f"# 📊 MADOBI 임원 요약 — `{Path(a.csv).name}`","",
       f"## 종합 (검산)",
       f"- 광고비 **{tot['spend']:,.0f}** · 매출 **{tot['revenue']:,.0f}** · 블렌디드 ROAS **{roas:.2f}x** (목표 {a.target_roas}x)",
       f"- 노출 {tot['impressions']:,.0f} · 클릭 {tot['clicks']:,.0f} (CTR {ctr:.2%}) · 전환 {tot['conversions']:,.0f} (CPA {cpa:,.0f})",
       "",
       f"## 핵심",
       f"- 🏆 최대 매출 기여: **{top['_n']}** ({top['revenue']:,.0f}, 전체의 {top['revenue']/max(tot['revenue'],1):.0%})" if top else "",
       f"- 🔻 최저 효율: **{worst['_n']}** (ROAS {(worst['revenue']/worst['spend'] if worst['spend'] else 0):.2f}x)" if worst else "",
       f"- 🎯 ROAS 목표 부족분 합: **{gap:,.0f}** (목표 달성에 필요한 추가매출)",
       f"- 🧪 데이터 품질: {'✅ 이상 없음' if dq==0 else f'⚠️ {dq}건 정합성 위반(보고 전 점검)'}",
       "",
       f"## 권고",
       f"- {'목표 미달 → 저효율 채널 소재/타깃 개선·예산 재배분' if roas<a.target_roas else '목표 달성 → 승자 점진 증액(학습 보존)'}",
       "*숫자는 원자료 재계산·검산. 가정(윈도우·타임존·통화) 확인.*"]
    text="\n".join(x for x in L if x is not None)
    if a.md: Path(a.md).write_text(text+"\n",encoding="utf-8",newline="\n"); print(f"[md] -> {a.md}")
    print("\n=== EXEC REPORT ===\n"+text)
if __name__=="__main__": main()
