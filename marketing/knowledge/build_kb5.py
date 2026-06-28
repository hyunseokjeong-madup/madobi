"""놀리지에셋 빌더 5 — 목표/플랫폼기능/리포팅/예산모델/소재테스트/진단. 각 파일 = 한 사이클."""
from pathlib import Path
from _fm_preserve import write_md  # 기존 frontmatter 보존하며 본문 재생성
HERE=Path(__file__).parent
def write(cat,name,title,b):
    d=HERE/cat; d.mkdir(parents=True,exist_ok=True)
    write_md(d/f"{name}.md", f"# {title}\n\n"+"\n".join(f"- {x}" for x in b)+"\n")
OBJ={
 "awareness":["KPI: 도달·CPM·VTR","상단 퍼널","브랜드 리프트로 측정"],
 "traffic":["KPI: 클릭·CPC·CTR","LP 트래픽","전환과 혼동 금지"],
 "engagement":["KPI: 참여·CPE","커뮤니티","전환 직결 약함"],
 "leads":["KPI: CPL·리드품질","폼·오퍼","품질 추적 필수"],
 "app_installs":["KPI: CPI·인앱액션","MMP·SKAN","설치후 가치"],
 "sales":["KPI: ROAS·CPA·POAS","하단·리타게팅","마진반영"],
 "store_visits":["KPI: 방문·지역","O2O","지오 측정"],
 "retention":["KPI: 리텐션·CRM","재참여","코호트"],
}
FEAT={
 "advantage_plus":["Meta 자동 전환 캠페인","광범위+소재 다양화"],
 "pmax":["Google 전채널 자동","에셋·시그널, 투명성 낮음"],
 "spark_ads":["TikTok 오가닉 부스팅","네이티브 신뢰"],
 "dynamic_ads":["카탈로그 동적 리타게팅","피드 품질"],
 "lead_forms":["인스턴트 폼","품질·CRM 연동"],
 "catalog":["상품 피드","가격·재고 동기화"],
 "conversions_api":["서버 전환(CAPI)","정합성·중복제거"],
 "smart_bidding":["tCPA/tROAS","데이터량·점진 변경"],
}
REPORT={
 "kpi_tree":["북극성→하위 KPI 분해","드라이버 추적"],
 "dashboard":["검산된 수치·정합성 배지","단위·가정 명시"],
 "cadence":["일/주/월/분기 리듬","루틴 자동화"],
 "stakeholder":["청중별 요약·액션","배치 커뮤니케이션"],
 "anomaly_comment":["급변에 자동 코멘트","원인 가설+점검"],
 "north_star":["야심찬 목표 명문화","정렬"],
 "attribution_statement":["윈도우·모델·타임존·통화 명시","비교 가능성"],
 "data_hygiene":["결측·중복·단위 정규화","reconcile 선행"],
}
BUDGET={
 "always_on":["상시 운영·안정","효율 관리"],
 "pulsing":["기저+피크 가중","시즌"],
 "flighting":["온/오프 구간","학습 리셋 주의"],
 "zero_based":["제로베이스 재배정","효율 기반"],
 "sov":["점유율 목표","방어"],
 "marginal_roas":["한계 ROAS로 증감","체감 고려"],
 "portfolio":["채널 묶음 최적","개별 통제↓"],
 "reserve":["테스트·기회 예비비","민첩성"],
}
TEST={
 "hook_test":["첫 3초 변주","CTR/시청유지"],
 "format_test":["포맷 비교","제작비 고려"],
 "concept_test":["메시지 앵글","승자 컨셉 확장"],
 "iteration":["승자 변주 반복","1변수"],
 "winner_scaling":["승자 점진 증액","학습 보존"],
 "hold_the_winner":["콘트롤 유지","비교 기준"],
 "kill_criteria":["사전 정의 손절","소표본 금지"],
 "library":["소재 라이브러리·태깅","재사용·학습"],
}
DIAG={
 "low_ctr":["원인: 후크·타깃·관련성","조치: 소재/타깃 교체"],
 "high_cpc":["원인: 경쟁·품질","조치: 품질·입찰·키워드"],
 "low_cvr":["원인: LP·오퍼·매치","조치: LP/오퍼 개선"],
 "high_cpa":["원인: CVR·입찰","조치: 전환율·입찰·타깃"],
 "low_roas":["원인: 가치·가격·타깃","조치: AOV·리타게팅·소재"],
 "low_volume":["원인: 예산·입찰·도달","조치: 확대·완화"],
 "fatigue":["원인: 빈도↑·CTR↓","조치: 신규 소재"],
 "disapproval":["원인: 정책 위반","조치: 카피·소재 수정·재심"],
}
total=0
for cat,data in [("objectives",OBJ),("platform_features",FEAT),("reporting",REPORT),
                 ("budget_models",BUDGET),("creative_testing",TEST),("diagnostics",DIAG)]:
    for n,b in data.items(): write(cat,n,f"{n.replace('_',' ').title()} — {cat}",b); total+=1
print(f"generated {total} files")
