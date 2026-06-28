"""놀리지에셋 빌더 3 — 오디언스/입찰/측정/지역/시즌/규제. 각 파일 = 한 사이클."""
from pathlib import Path
from _fm_preserve import write_md  # 기존 frontmatter 보존하며 본문 재생성
HERE=Path(__file__).parent
def write(cat,name,title,b):
    d=HERE/cat; d.mkdir(parents=True,exist_ok=True)
    write_md(d/f"{name}.md", f"# {title}\n\n"+"\n".join(f"- {x}" for x in b)+"\n")

AUDIENCE={
 "prospecting":["신규 고객 발굴, 광범위+시그널","상단 퍼널, CPM/CTR 관점","소재가 타게팅을 대체하는 추세"],
 "retargeting":["방문/장바구니/구매자 리타게팅","빈도캡·제외기간","번인 방지, 동적 소재"],
 "lookalike":["고가치 시드(구매자/LTV상위) 기반","1~3% 유사도 트레이드오프","시드 품질이 핵심"],
 "interest":["관심사·행동 타게팅","점차 자동화로 비중↓","오버랩 주의"],
 "broad":["광범위+알고리즘 최적화","학습 데이터 충분 필요","소재 다양화로 신호"],
 "custom":["CRM/이벤트 기반 맞춤","동의·프라이버시","매칭률 확인"],
 "exclusions":["기존고객·전환자 제외(프로스펙팅)","중복·낭비 방지","리스트 최신화"],
 "sequential":["퍼널 단계별 순차 메시지","인지→고려→전환","빈도·순서 설계"],
}
BIDDING={
 "manual_cpc":["입찰 직접 통제","초기·소규모","최적화 수동 부담"],
 "max_clicks":["트래픽 최대화","상단·테스트","전환 무관 주의"],
 "tcpa":["목표 CPA 자동","전환 데이터 충분(주15+)","목표 과도 시 노출 급감"],
 "troas":["목표 ROAS 자동","가치 데이터 필요","목표 현실적으로"],
 "max_conv":["전환 최대화(예산 내)","CPA 변동 허용","예산이 사실상 통제"],
 "max_value":["전환가치 최대화","가치 신호 정확성","고가치 편향"],
 "target_is":["노출점유율 목표(브랜드)","방어·인지","비용 비효율 가능"],
 "portfolio":["여러 캠페인 묶어 입찰","규모의 학습","개별 통제 약화"],
}
MEASUREMENT={
 "last_click":["마지막 클릭 100% 귀속","단순·하단 편향","상단 과소평가"],
 "data_driven":["기여 데이터 기반 배분","데이터량 필요","플랫폼별 상이"],
 "mta":["멀티터치 어트리뷰션","크로스채널","쿠키/프라이버시 한계"],
 "mmm":["미디어믹스 모델(집계·회귀)","쿠키리스·장기","granularity 낮음"],
 "incrementality_test":["홀드아웃 대비 순증분","진실의 기준","설계·표본 필요"],
 "view_through":["조회 후 전환","상단 가치","과대 위험"],
 "geo_holdout":["지역 분할 실험","증분 측정","외생요인 통제"],
 "conversion_lift":["플랫폼 리프트 스터디","증분 추정","플랫폼 내 한정"],
}
REGIONAL={
 "kr":["네이버/카카오/쿠팡 비중","KST·KRW","심의·금융/의료 규제"],
 "jp":["LINE/Yahoo!Japan","JST·JPY","정중한 카피·신뢰"],
 "us":["Google/Meta/TikTok","다중 타임존·USD","주별 규제 차이"],
 "sea":["모바일·앱 중심","현지화·다언어","COD 비중"],
 "eu_gdpr":["동의·프라이버시 강함","컨센트 모드","데이터 최소화"],
 "global":["다통화·다타임존 정규화","현지 공휴일·시즌","번역≠현지화"],
}
SEASON={
 "q1":["연초·신학기","설(KR)·旧正월 변동","재고·예산 리셋"],
 "q2":["가정의달·여름 준비","비수기 효율 관리"],
 "q3":["여름·휴가·백투스쿨","추석(KR) 변동"],
 "q4":["블프·연말·홈쇼핑 피크","CPM 급등·예산 집중","페이싱 주의"],
}
COMPLIANCE={
 "finance":["금융광고 심의·금리/원금 표기","과장·확정수익 금지"],
 "health":["의료/건강기능 효능 클레임 규제","before/after 주의"],
 "alcohol":["연령·시간대·플랫폼 제한"],
 "kids":["아동 타게팅·데이터 제한(COPPA 등)"],
 "privacy":["동의·옵트아웃·민감정보","지역별 법규"],
 "claims":["최상급·비교 근거 보유","허위·기만 금지"],
}
total=0
for cat,data in [("audience",AUDIENCE),("bidding",BIDDING),("measurement",MEASUREMENT),
                 ("regional",REGIONAL),("seasonality",SEASON),("compliance",COMPLIANCE)]:
    for n,b in data.items():
        write(cat,n,f"{n.replace('_',' ').title()} — {cat}",b); total+=1
print(f"generated {total} files across 6 categories")
