"""놀리지에셋 빌더 4 — 후크/오퍼/LP요소/실험/그로스 전술 카드. 각 파일 = 한 사이클."""
from pathlib import Path
from _fm_preserve import write_md  # 기존 frontmatter 보존하며 본문 재생성
HERE=Path(__file__).parent
def write(cat,name,title,b):
    d=HERE/cat; d.mkdir(parents=True,exist_ok=True)
    write_md(d/f"{name}.md", f"# {title}\n\n"+"\n".join(f"- {x}" for x in b)+"\n")
HOOKS={
 "number":["구체 숫자로 신뢰('3일 만에','37% 절감')","과장 금지·근거 보유"],
 "question":["통점 질문으로 자기인식 유발","타깃 언어로"],
 "reversal":["통념 반전으로 주의 환기","근거로 뒷받침"],
 "before_after":["변화 시각화","규제(효능) 주의"],
 "social_proof":["사용자수·후기·랭킹","수치 검산"],
 "curiosity":["정보격차로 시청 유지","낚시 금지(이탈)"],
 "scarcity":["한정·마감으로 행동 촉구","허위 희소성 금지"],
 "problem_agitate":["문제 부각→해결 제시(PAS)","공감 우선"],
 "testimonial":["진짜 사용자 목소리","동의·권리"],
 "how_to":["방법 제시로 가치 선전달","간결"],
}
OFFERS={
 "discount":["즉시 전환↑","마진 잠식·할인 의존 주의"],
 "free_shipping":["장바구니 이탈↓","임계 금액 설계"],
 "bundle":["AOV↑","재고·마진 균형"],
 "free_trial":["진입장벽↓","전환·해지율 추적"],
 "bogo":["수량 판매","마진 계산"],
 "gift":["인지가치↑","원가 통제"],
 "subscription":["LTV↑","해지·페이백"],
 "limited_edition":["희소·프리미엄","수량 관리"],
}
LP={
 "hero":["3초 내 가치 전달","후크↔LP 메시지매치"],
 "value_prop":["명확한 베네핏","타깃 언어"],
 "social_proof":["후기·로고·수치","신뢰"],
 "cta":["하나·명확·반복","대비·위치"],
 "urgency":["마감·재고","진정성"],
 "faq":["이탈 사유 선제 해소","간결"],
 "trust_badges":["보안·보증·리뷰","과장 금지"],
 "form":["필드 최소화","마찰↓ 전환↑"],
}
EXP={
 "ab_creative":["소재 1변수 격리","충분 표본·유의성(abtest)"],
 "ab_audience":["오디언스 비교","오버랩 통제"],
 "ab_lp":["랜딩 변형","트래픽 분할 균등"],
 "ab_bid":["입찰 전략 비교","학습기·기간"],
 "holdout":["광고 미노출군 대비 증분","외생 통제"],
 "multivariate":["다요소 동시","상호작용·표본 큼"],
 "geo":["지역 분할 실험","시장 동질성"],
 "sequential":["순차 노출 효과","순서·빈도"],
}
GROWTH={
 "referral":["추천 루프","어뷰징 방지"],
 "loyalty":["재구매·등급","원가·혜택 균형"],
 "winback":["휴면 재활성","세그·오퍼"],
 "upsell_crosssell":["객단가↑","관련성"],
 "email_flow":["환영·장바구니·구매후","개인화"],
 "retargeting_ladder":["퍼널 단계별 리타게팅","빈도·제외"],
 "viral_loop":["공유 유인","바이럴계수 K"],
 "content":["오가닉·SEO·콘텐츠","장기 복리"],
}
total=0
for cat,data in [("hooks",HOOKS),("offers",OFFERS),("lp_elements",LP),("experiments",EXP),("growth",GROWTH)]:
    for n,b in data.items(): write(cat,n,f"{n.replace('_',' ').title()} — {cat}",b); total+=1
print(f"generated {total} files")
