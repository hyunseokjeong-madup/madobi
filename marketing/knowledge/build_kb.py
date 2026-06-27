"""
놀리지에셋 빌더 — 버티컬/포맷/함정/루틴/채널별 실전 지식 파일을 생성.
각 파일 = 한 사이클(쓸수록 자라는 자산). 내용은 구체적 KPI·전술·함정 포함.
"""
import json
from pathlib import Path
HERE = Path(__file__).parent

def write(cat, name, title, sections):
    d = HERE / cat; d.mkdir(parents=True, exist_ok=True)
    L = [f"# {title}", ""]
    for h, bullets in sections:
        L.append(f"## {h}")
        L += [f"- {b}" for b in bullets]
        L.append("")
    (d / f"{name}.md").write_text("\n".join(L), encoding="utf-8", newline="\n")

VERTICALS = {
 "ecommerce": ("이커머스",
   [("핵심 KPI", ["ROAS·CPA·AOV·전환율·장바구니 이탈률", "신규 vs 재구매 분리, 마진반영 POAS"]),
    ("전술", ["카탈로그/쇼핑 광고, 동적 리타게팅", "장바구니/구매 퍼널별 메시지", "시즌·프로모션 캘린더 정렬"]),
    ("함정", ["플랫폼 ROAS는 중복귀속 → 실매출 대사", "재고/품절 소재 노출 방지", "쿠폰 마진 잠식 주의"])]),
 "mobile_app": ("모바일 앱",
   [("핵심 KPI", ["CPI·CPA(인앱액션)·D1/D7/D30 리텐션·ROAS·LTV/CAC"]),
    ("전술", ["UAC/Advantage+ App, MMP(Appsflyer/Adjust) 연동", "딥링크·이벤트 최적화", "크리에이티브 다양화·플레이어블"]),
    ("함정", ["iOS SKAN 지연·모델링 전환", "MMP vs 플랫폼 vs 스토어 대사", "부정설치(fraud) 필터"])]),
 "lead_gen": ("리드젠/B2B",
   [("핵심 KPI", ["CPL·리드품질(MQL/SQL)·전환율·파이프라인 기여"]),
    ("전술", ["폼/인스턴트폼, 화이트페이퍼·웨비나 오퍼", "롱세일즈 사이클 → 어트리뷰션 길게"]),
    ("함정", ["리드량 vs 품질 트레이드오프", "스팸/허위 리드 필터", "오프라인 전환 업로드 대사"])]),
 "gaming": ("게임",
   [("핵심 KPI", ["CPI·ROAS·결제전환·ARPPU·리텐션"]),
    ("전술", ["플레이어블/영상 소재, 유사오디언스", "이벤트·업데이트 타이밍"]),
    ("함정", ["고래(소수 고결제) 의존 → 분포 확인", "소재 피로 매우 빠름"])]),
 "finance": ("금융",
   [("핵심 KPI", ["CPA(계좌개설/대출)·승인율·LTV"]),
    ("전술", ["규제 준수 카피, 신뢰 요소", "리타게팅 제한 고려"]),
    ("함정", ["금융광고 규제·심의·금칙어", "민감정보·타게팅 제한"])]),
 "beauty": ("뷰티",
   [("핵심 KPI", ["ROAS·AOV·재구매율·UGC 참여"]),
    ("전술", ["UGC·인플루언서·before/after(규제 내)", "샘플·구독 오퍼"]),
    ("함정", ["과장·효능 클레임 규제", "before/after 표현 주의"])]),
 "fashion": ("패션",
   [("핵심 KPI", ["ROAS·AOV·반품률·시즌 소진"]),
    ("전술", ["룩북·캐러셀·컬렉션, 시즌 캘린더", "사이즈/핏 정보로 반품 저감"]),
    ("함정", ["반품률이 ROAS 왜곡 → 순매출 기준", "재고 소진 연동"])]),
 "food_delivery": ("푸드/배달",
   [("핵심 KPI", ["CPA(첫주문)·재주문율·지역별 ROAS"]),
    ("전술", ["지역·시간대 타게팅, 첫주문 쿠폰", "피크타임 입찰 가중"]),
    ("함정", ["쿠폰 의존 신규의 잔존 낮음 → 코호트 확인", "지역 단위 정합성"])]),
 "education": ("교육",
   [("핵심 KPI", ["CPL·수강전환·완주율·LTV"]),
    ("전술", ["무료체험·웨비나, 시즌(개강) 정렬"]),
    ("함정", ["장기 전환 → 어트리뷰션 길게", "환불·완주율 반영"])]),
 "travel": ("여행",
   [("핵심 KPI", ["ROAS·예약전환·취소율·시즌성"]),
    ("전술", ["시즌·목적지 타게팅, 동적 가격 소재"]),
    ("함정", ["취소율로 순매출 보정", "리드타임 긴 전환 윈도우"])]),
}

FORMATS = {
 "search": ("검색 광고", ["의도 높음→CPA/ROAS", "키워드 매치·네거티브 관리", "광고문구 A/B·확장"]),
 "shopping": ("쇼핑 광고", ["상품 단위 ROAS", "피드 품질(제목·이미지·가격)", "재고/가격 동기화"]),
 "video_short": ("숏폼 영상", ["첫 1~3초 후크", "세로 9:16·자막·사운드", "피로 빠름→신규 빈번"]),
 "video_long": ("롱폼 영상", ["스토리텔링·인지", "VTR·시청유지", "CTA 명확"]),
 "display": ("디스플레이", ["인지·리타게팅", "뷰어빌리티·빈도캡", "플레이스먼트 정제"]),
 "native": ("네이티브", ["콘텐츠 맥락 융화", "클릭베이트 금지", "랜딩 일관성"]),
 "ugc": ("UGC", ["진정성·후기", "크리에이터 다양성", "권리·동의 확인"]),
 "carousel": ("캐러셀", ["다상품·스토리 분할", "1번 카드 후크", "카드별 성과 분석"]),
 "collection": ("컬렉션", ["모바일 풀스크린 카탈로그", "즉시 탐색", "피드 연동"]),
 "playable": ("플레이어블", ["체험형(게임/앱)", "고전환·고제작비", "핵심 재미 30초내"]),
}

PITFALLS = {
 "attribution": ("어트리뷰션 함정", ["윈도우(1d/7d)·모델(last/DDA) 다르면 비교 불가", "플랫폼 합산 > 실제(중복) → 대사 필수"]),
 "simpson": ("심슨 패러독스", ["비율은 단순평균 금지", "가중(Σ/Σ)으로 재계산", "세그먼트 합쳐서 보면 역전 가능"]),
 "timezone": ("타임존", ["UTC vs KST 경계 일자 차이", "계정 타임존 기준 집계 통일"]),
 "currency": ("통화/포맷", ["KRW/USD 혼용, 천단위·% 혼동", "파싱 전 정규화"]),
 "dedup": ("중복/이중계산", ["합계행·소계행 데이터 오인", "다채널 전환 중복귀속"]),
 "bot_traffic": ("무효 트래픽", ["봇/무효클릭 제거 전후 구분", "이상 CTR 급등 점검"]),
 "learning_phase": ("학습기", ["전환 부족 시 잦은 수정 금지", "광고세트당 주 50전환 목표"]),
 "ios_privacy": ("iOS 프라이버시", ["SKAN 지연·모델링 전환", "결정론적 vs 확률적 구분"]),
 "brand_cannibalization": ("브랜드 잠식", ["PMax/검색이 브랜드 잠식", "홀드아웃으로 증분 확인"]),
 "small_sample": ("소표본 과해석", ["충분 노출/전환 전 판단 보류", "A/B는 유의성 검정(abtest)"]),
}

ROUTINES = {
 "daily": ("일일 루틴", ["페이싱·예산 소진 점검", "가드레일(ROAS/CPA) 위반 확인", "이상치/급변 점검", "소재 피로·빈도", "→ alert_digest로 일괄"]),
 "weekly": ("주간 루틴", ["WoW 성과·기여 리뷰", "소재 승자/패자 교체", "검색어→네거티브", "예산 재배분 검토", "리포트 발행"]),
 "monthly": ("월간 루틴", ["MoM·목표 대비", "채널 믹스 최적화", "코호트/LTV·페이백", "예측 vs 실제", "전략 조정"]),
 "quarterly": ("분기 루틴", ["증분성/홀드아웃", "시즌성·연간 계획", "벤치마크·경쟁", "측정체계 점검"]),
}

CHANNELS_EXTRA = {
 "youtube": ("YouTube", ["인지·고려(VTR·CPV)", "스킵/논스킵·범퍼", "시청유지·후크", "전환은 리타게팅 병행"]),
 "kakao": ("Kakao(카카오)", ["비즈보드·채널 메시지", "국내 메신저 도달", "전환 추적·통화 KST"]),
 "apple_search": ("Apple Search Ads", ["앱스토어 검색", "키워드·CPT", "SKAN 한계"]),
 "criteo": ("Criteo", ["리타게팅·상품추천", "오픈웹 인벤토리", "대사·증분 점검"]),
 "line": ("LINE", ["메신저·타임라인", "지역(일/대만/태)", "전환 추적"]),
 "x_ads": ("X(Twitter)", ["실시간·관심사", "대화·트렌드", "브랜드 안전성"]),
}

count = 0
for n,(t,secs) in VERTICALS.items(): write("verticals", n, f"{t} 버티컬 플레이북", secs); count+=1
for n,(t,b) in FORMATS.items(): write("formats", n, f"{t} 포맷 가이드", [("핵심", b)]); count+=1
for n,(t,b) in PITFALLS.items(): write("pitfalls", n, t, [("점검", b)]); count+=1
for n,(t,b) in ROUTINES.items(): write("routines", n, t, [("체크리스트", b)]); count+=1
for n,(t,b) in CHANNELS_EXTRA.items(): write("channels", n, f"{t} 플레이북", [("핵심", b)]); count+=1
print(f"generated {count} knowledge files")
print(json.dumps({"verticals":len(VERTICALS),"formats":len(FORMATS),"pitfalls":len(PITFALLS),
                  "routines":len(ROUTINES),"channels_extra":len(CHANNELS_EXTRA)},ensure_ascii=False))
