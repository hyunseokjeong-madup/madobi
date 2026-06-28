"""놀리지에셋 빌더 2 — 지표 심화카드 + 템플릿 + 체크리스트. 각 파일 = 한 사이클."""
from pathlib import Path
from _fm_preserve import write_md  # 기존 frontmatter 보존하며 본문 재생성
HERE = Path(__file__).parent
def write(cat, name, title, sections):
    d = HERE / cat; d.mkdir(parents=True, exist_ok=True)
    L=[f"# {title}",""]
    for h,b in sections: L.append(f"## {h}"); L+= [f"- {x}" for x in b]; L.append("")
    write_md(d/f"{name}.md", "\n".join(L))

# metric: (정의/공식, 레버, 함정)
METRICS = {
 "ctr":("clicks/impressions","후크·소재·타깃·관련성","outbound vs all, 봇 클릭"),
 "cpc":("spend/clicks","품질지수·입찰·경쟁","고CPC가 항상 나쁘진 않음(고의도)"),
 "cpm":("spend/impressions×1000","오디언스·시즌·경매압력","×1000, 인벤토리 품질"),
 "cvr":("conversions/clicks","LP·오퍼·메시지매치","분모(클릭/노출) 정의"),
 "cpa":("spend/conversions","입찰·타깃·전환율","어트리뷰션·중복"),
 "roas":("revenue/spend","타깃·소재·LP·가격","중복귀속·환불·반품"),
 "poas":("revenue×margin/spend","마진·믹스·할인 통제","마진 데이터 정확성"),
 "aov":("revenue/orders","번들·업셀·무료배송 임계","쿠폰 마진 잠식"),
 "ltv":("ARPU×수명×마진(또는 코호트 누적)","리텐션·재구매·업셀","정의·기간 일관"),
 "cac":("획득비용/신규고객","효율·믹스","오가닉 혼입 주의"),
 "payback":("CAC/월 공헌","마진·ARPU·리텐션","현금흐름 관점"),
 "retention":("dayN 잔존/설치","온보딩·가치전달·CRM","코호트 정의"),
 "frequency":("impressions/reach","도달 확대·빈도캡","피로 임계 ≈2~3"),
 "reach":("순 도달 사용자","예산·오디언스 크기","reach≤impressions"),
 "ecpm":("revenue/impressions×1000","수요·인벤토리","퍼블리셔 측"),
 "impression_share":("노출/가능노출","예산·입찰·품질","손실 IS 분해(예산/순위)"),
 "incrementality":("광고 순증분(holdout 대비)","증분 테스트 설계","플랫폼 전환≠증분"),
 "blended_roas":("Σrevenue/Σspend(전채널)","믹스·효율","채널 중복귀속"),
 "mer":("총매출/총광고비(Marketing Efficiency Ratio)","전사 효율 관점","채널 귀속 무관 총량 지표"),
 "contribution_margin":("매출−변동비","가격·원가·할인","광고비 포함 여부 정의"),
}
for n,(f,lev,pit) in METRICS.items():
    write("metrics", n, n.upper()+" 심화",
          [("정의/공식",[f]),("개선 레버",[lev]),("함정",[pit]),("검산",["코드로 재계산(reconcile/summarize), 단위·가중 확인"])])

TEMPLATES = {
 "account_onboarding":("계정 온보딩 템플릿",["목표/KPI·예산·시즌성","계정 기준선(평균 CTR/CPA/ROAS)","타깃·금칙어·브랜드 가이드","측정/어트리뷰션·타임존·통화","선호 리포트 포맷 → knowledge/<account>.md 기록"]),
 "daily_report":("일일 리포트 템플릿",["총지출/매출/블렌디드 ROAS(검산)","페이싱·가드레일·이상치","상위/하위 성과","오늘의 조치"]),
 "weekly_report":("주간 리포트 템플릿",["WoW 핵심지표","소재 승자/패자","검색어/네거티브","예산 재배분 제안","다음주 계획"]),
 "monthly_report":("월간 리포트 템플릿",["MoM·목표 대비","채널 믹스·효율","코호트/LTV","예측 vs 실제","전략 조정"]),
 "creative_brief":("소재 브리프 템플릿",["목표/KPI·타깃·인사이트","앵글·후크·포맷","헤드라인/본문/CTA","네이밍 규칙","QA 체크"]),
 "naming_convention":("네이밍 규칙",["{campaign}_{angle}_{format}_{hook}_v##","소문자·하이픈, 공백 금지","차원 분해·정합성 전제"]),
 "ab_test_plan":("A/B 테스트 계획",["가설·1변수 격리","표본·기간·성공지표","유의성(abtest) 사전 정의","의사결정 규칙"]),
 "qbr":("QBR(분기 리뷰)",["목표 대비 성과","증분성·믹스","리스크·기회","다음 분기 계획"]),
}
for n,(t,b) in TEMPLATES.items(): write("templates", n, t, [("항목", b)])

CHECKLISTS = {
 "launch":("런칭 체크리스트",["전환추적·이벤트 검증","예산·입찰·일정","타깃·제외·빈도","소재 규격·금칙어","UTM·네이밍"]),
 "audit":("계정 감사",["낭비(저ROAS·고지출)","중복·과타게팅","학습기 상태","어트리뷰션 설정","네거티브·검색어"]),
 "reconciliation":("정합성 점검",["분해합=총계","파생 역산 일치","가중평균(Simpson)","단위·통화·타임존","플랫폼 vs 실매출"]),
 "creative_qa":("소재 QA",["규격·자막·안전영역","클레임·규제·금칙어","메시지매치(후크↔본문↔CTA↔LP)","수치 검산"]),
 "tracking_setup":("트래킹 설정",["픽셀/SDK/서버전환","이벤트·매개변수","중복제거·동의","테스트 이벤트 검증"]),
 "budget_review":("예산 검토",["페이싱·소진율","채널 믹스","가드레일·낭비","재배분"]),
 "scaling":("스케일링",["승자 식별(충분표본)","점진 증액(±20%)","학습 리셋 주의","소재 다양화"]),
 "pause_decision":("일시중지 결정",["충분 노출/지출 후 판단","가드레일 위반 지속","낭비·피로","대체안 준비"]),
}
for n,(t,b) in CHECKLISTS.items(): write("checklists", n, t, [("항목", b)])

print(f"generated {len(METRICS)+len(TEMPLATES)+len(CHECKLISTS)} files "
      f"(metrics {len(METRICS)}, templates {len(TEMPLATES)}, checklists {len(CHECKLISTS)})")
