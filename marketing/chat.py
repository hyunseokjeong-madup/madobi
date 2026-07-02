"""
chat.py — MADOBI 챗봇 모드. 자연어 질문을 결정론적으로 이해해 도구로 라우팅하는 대화형 REPL.

"훌륭한 분석 에이전트이자 챗봇"의 CLI 진입점:
  python marketing/chat.py                       # 대화형 REPL (매도비> )
  python marketing/chat.py --ask "예산 재배분 해줘"   # 단발 질의 (스크립트/에이전트용)
  python marketing/madobi.py chat --ask "..."     # 디스패처 경유도 동일

무엇을 하나 (전부 결정론 — LLM 호출 없음, 같은 질문 → 같은 답):
  1. 지표 Q&A     — "ROAS가 뭐야?" → semantic_layer 용어집에서 정의·공식·SQL식 즉답
  2. 도구 라우팅   — "이탈 위험 고객 뽑아줘" → churn_score 추천 + 바로 실행 가능한 명령
                    (예시 인자는 tests/run_all.py 의 검증된 호출을 재사용 — 이중 정의 금지)
  3. 놀리지 회상   — "지난번에 배운 교훈?" → knowledge/recall.py 위임
  4. 실행         — REPL에서 `run` / `run 2` 로 마지막 추천 명령을 그 자리에서 실행

설계 원칙 (KARPATHY: 최소·결정론): 순수 stdlib. 라우팅 = 도구명/도큐스트링/한국어 힌트의
가중 매칭, 동점은 이름순 안정 정렬. LLM의 판단이 필요한 해석·코멘트는 Claude(에이전트)가 담당.
"""
import re
import sys
import argparse
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent           # marketing/
PM = HERE / "pm"
ROOT = HERE.parent                               # repo root

try:
    from . import semantic_layer
except ImportError:
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    import semantic_layer


# ---------------------------------------------------------------- 텍스트 유틸
def _norm(s):
    """소문자·공백/구분자 제거 — 한국어 교착어 특성상 부분문자열 매칭용."""
    return re.sub(r"[\s_\-./]+", "", str(s).lower())


def _tokens(s):
    return set(re.findall(r"[0-9a-zA-Z가-힣]+", str(s).lower()))


def _first_doc(path):
    """모듈 도큐스트링 첫 비어있지 않은 줄 (madobi.py/tools_index.py 와 동일 규약)."""
    s = Path(path).read_text(encoding="utf-8")
    m = re.search(r'^\s*"""(.*?)"""', s, re.S | re.M)
    if not m:
        return ""
    for ln in m.group(1).strip().splitlines():
        if ln.strip():
            return ln.strip()
    return ""


# ------------------------------------------------------------- 도구 카탈로그
_EXCLUDE = {"chat", "madobi", "tools_index", "__init__"}


def catalog():
    """라우팅 대상 도구 목록: pm/* + marketing 루트 + bench/summarize. {name: {path, doc}}"""
    tools = {}
    for d in (PM, HERE):
        for f in sorted(d.glob("*.py")):
            nm = f.stem
            if nm.startswith("_") or nm in _EXCLUDE or nm in tools:
                continue
            tools[nm] = {"path": f, "doc": _first_doc(f)}
    summ = HERE / "bench" / "summarize.py"
    if summ.exists():
        tools["summarize"] = {"path": summ, "doc": _first_doc(summ)}
    return tools


def _examples():
    """tests/run_all.py 의 CHECKS(검증된 호출)에서 도구별 예시 argv 를 재사용.

    예시 인자를 여기 다시 적으면 이중 정의 → 표류. 통합 테스트가 곧 사용 예시다."""
    out = {}
    p = ROOT / "tests" / "run_all.py"
    if not p.exists():
        # pip 설치본 등 tests/ 부재 환경 — 조용히 격하되면 원인을 알 수 없다.
        print("[warn] tests/run_all.py 없음 — 예시 명령 없이 '-h 안내'로만 추천합니다.",
              file=sys.stderr)
        return out
    text = p.read_text(encoding="utf-8")
    for m in re.finditer(r'\["python",\s*"([^"]+\.py)"((?:,\s*"[^"]*")*)\]', text):
        script, rest = m.group(1), m.group(2)
        name = Path(script).stem
        args = re.findall(r'"([^"]*)"', rest)
        out.setdefault(name, ["python", script] + args)
    return out


# 한국어 마케팅 표현 → 도구 힌트 (도구명/도큐스트링만으로 못 잡는 관용 표현 보강)
INTENT_HINTS = {
    "검산": ["reconcile"], "정합성": ["reconcile"], "대사": ["reconcile", "attribution_compare"],
    "요약": ["summarize", "report"], "리포트": ["report", "exec_report"],
    "보고서": ["report", "exec_report"], "보고용": ["exec_report"],
    "페이싱": ["pacing", "pacing_optimizer"], "소진": ["pacing", "pacing_optimizer"],
    "예산": ["budget_optimizer", "reallocate", "budget_response_alloc", "pacing_optimizer"],
    "재배분": ["reallocate"], "배분": ["reallocate", "budget_optimizer"],
    "에이비": ["abtest"], "ab테스트": ["abtest"], "유의": ["abtest", "ttest", "chi_square"],
    "표본": ["sample_size", "srm_check"], "샘플": ["sample_size"],
    "이탈": ["churn_score", "winback_priority"], "휴면": ["winback_priority"],
    "복귀": ["winback_priority"], "윈백": ["winback_priority"],
    "코호트": ["cohort", "cohort_heatmap"], "리텐션": ["cohort", "ltv_forecast"],
    "잔존": ["cohort", "cohort_heatmap"],
    "이상": ["anomaly_ts", "outlier_iqr"], "급등": ["anomaly_ts"], "급락": ["anomaly_ts"],
    "어트리뷰션": ["attribution_mta", "shapley_attribution", "attribution_compare"],
    "기여": ["attribution_mta", "shapley_attribution"],
    "증분": ["incrementality_ab", "incremental_roas", "geo_lift"],
    "지역": ["geo_lift"], "예측": ["forecast", "seasonal_forecast", "ltv_forecast"],
    "낭비": ["waste"], "소재": ["analyze_creatives", "creative_gen", "rotation"],
    "크리에이티브": ["analyze_creatives", "creative_gen", "rotation"],
    "카피": ["creative_gen"], "후크": ["creative_gen"], "피로": ["rotation"],
    "교체": ["rotation"], "퍼널": ["funnel", "funnel_steps"], "깔때기": ["funnel"],
    "검색어": ["search_terms", "cluster_terms", "brand_split"],
    "브랜드": ["brand_split"], "채널": ["channel_mix", "mix_shift"],
    "믹스": ["channel_mix", "mix_shift", "mmm"], "가드레일": ["guardrails"],
    "알림": ["alert_digest"], "아침": ["alert_digest"], "점검": ["alert_digest", "data_quality"],
    "품질": ["data_quality"], "대시보드": ["dashboard"], "히트맵": ["dow_heatmap", "cohort_heatmap"],
    "요일": ["dow_heatmap", "seasonality"], "계절": ["seasonality", "seasonal_forecast"],
    "시즌": ["seasonality"], "가격": ["price_elasticity", "price_optimizer"],
    "탄력": ["price_elasticity"], "프로모": ["promo_roi"], "할인": ["promo_roi"],
    "장바구니": ["market_basket"], "연관구매": ["market_basket"],
    "입찰": ["bid_sim"], "빈도": ["frequency"], "도달": ["reach_planner"],
    "건강": ["account_health"], "헬스": ["account_health"], "점수": ["account_health", "scorecard"],
    "스코어": ["scorecard", "churn_score"], "이벤트": ["event_analysis"],
    "캠페인효과": ["event_analysis"], "전후": ["event_analysis"],
    "목표": ["target_setter", "roas_gap"], "갭": ["roas_gap"],
    "네이밍": ["naming_check"], "이름규칙": ["naming_check"],
    "상관": ["correlation"], "파레토": ["pareto"], "집중": ["hhi", "pareto"],
    "신뢰구간": ["confidence_interval"], "지연": ["conversion_lag"],
    "램프": ["ramp_plan"], "증액": ["ramp_plan"], "주간": ["weekly_rollup"],
    "손익": ["poas"], "마진": ["poas", "promo_roi"], "회수": ["ltv_payback"],
    "고객가치": ["ltv_forecast", "ltv_payback"],
    # 진단형/상태형 질문 (적대 검증에서 오라우팅 재현된 표현들)
    "성과": ["report", "exec_report", "summarize"], "어때": ["report", "summarize"],
    "왜": ["kpi_decomp", "anomaly_ts", "event_analysis"],
    "원인": ["kpi_decomp", "anomaly_ts", "mix_shift"],
    "올랐": ["kpi_decomp", "anomaly_ts", "cpm_trend"],
    "줄었": ["kpi_decomp", "anomaly_ts", "event_analysis"],
    "떨어졌": ["kpi_decomp", "anomaly_ts"], "하락": ["kpi_decomp", "anomaly_ts"],
    "급증": ["anomaly_ts"], "전환": ["kpi_decomp", "funnel", "conversion_lag"],
    # 채널명 (혼합스크립트 '메타랑' 도 _norm 부분문자열로 매치)
    "meta": ["channel_mix", "budget_optimizer", "reallocate"],
    "메타": ["channel_mix", "budget_optimizer", "reallocate"],
    "google": ["channel_mix", "budget_optimizer", "reallocate"],
    "구글": ["channel_mix", "budget_optimizer", "reallocate"],
    "naver": ["channel_mix", "budget_optimizer"], "네이버": ["channel_mix", "budget_optimizer"],
    "카카오": ["channel_mix", "budget_optimizer"], "kakao": ["channel_mix", "budget_optimizer"],
    "틱톡": ["channel_mix", "budget_optimizer"], "tiktok": ["channel_mix", "budget_optimizer"],
    "sql": ["sql_query"], "집계": ["summarize", "sql_query"],
}

# 도큐스트링 토큰 겹침 채점에서 제외할 불용어 — 1토큰 겹침('해')만으로
# price_optimizer 같은 무관 도구가 '확신 있는 오추천'이 되는 것을 막는다.
_STOPTOKENS = {"해", "및", "수", "전", "후", "중", "더", "좀", "뭐", "왜", "이번", "지난",
               "어때", "해줘", "봐줘", "주세요", "이거", "그거", "대비"}

# 놀리지 회상 의도
_RECALL_HINTS = ("지난번", "교훈", "배운", "배웠", "메모", "히스토리", "놀리지", "기억", "아는거", "아는 거", "know-how", "노하우")
# 회상 쿼리에서 걷어낼 의도어 — 원문 그대로 검색하면 의도어만 매칭돼 항상 빈손이다.
_RECALL_STRIP = ("지난번에", "지난번", "배운", "배웠던", "배웠", "교훈", "알려줘", "말해줘",
                 "메모", "기억나", "기억", "우리가", "아는", "뭐였지", "뭐지", "있어", "해줘", "좀")

# 지표 정의 질문 의도
_DEFINE_HINTS = ("뭐야", "뭔가요", "무엇", "뜻", "정의", "공식", "계산법", "어떻게 계산", "계산식")

# 피드백(자기개선) 의도 — 강한 마커만 단락(short-circuit). '개선해' 같은 약한 표현은
# 분석 요청("CTR 개선해줘"→ctr_benchmark)과 겹쳐서 단락시키면 회귀한다.
_FEEDBACK_STRONG = ("앞으로", "항상", "틀렸", "하지 마", "하지마", "금지")

# 스몰토크 (라우팅 0건 폴백 안에서만 검사 — 복합 발화의 정상 라우팅을 가로채지 않게)
_GREET = ("안녕", "하이", "헬로", "hello", "hi")
_THANKS = ("고마워", "감사", "thanks")
_CAPA = ("뭐 할 수", "뭘 할 수", "뭐 해줄", "무엇을 할", "능력", "도움말", "help", "소개")


# ------------------------------------------------------------------- 라우팅
def is_recall(q):
    return any(h in q for h in _RECALL_HINTS)


def is_feedback(q):
    return any(h in q for h in _FEEDBACK_STRONG)


def clean_recall_query(q):
    """회상 질의에서 의도어를 걷어내고 핵심어만. 전부 걷히면 원문 유지."""
    words = [w for w in re.split(r"\s+", q.strip())
             if w and not any(s in w for s in _RECALL_STRIP)]
    return " ".join(words) or q


def detect_account(q):
    """질문에서 계정명 감지 — knowledge/<account>.md 파일명 기반 (특수 파일 제외)."""
    kdir = HERE / "knowledge"
    qn = _norm(q)
    for f in sorted(kdir.glob("*.md")):
        stem = f.stem
        if stem.startswith("_") or stem == "glossary":
            continue
        if _norm(stem) in qn:
            return stem
    return None


def metric_answer(q):
    """지표 정의 질문이면 용어집 즉답 문자열, 아니면 None."""
    if not any(h in q for h in _DEFINE_HINTS):
        return None
    qn = _norm(q)
    hits = []
    for term in semantic_layer.known_terms():
        tn = _norm(term)
        if len(tn) >= 2 and tn in qn:
            spec = semantic_layer.resolve(term)
            if spec["canonical"] not in [h["canonical"] for h in hits]:
                hits.append(spec)
    if not hits:
        return None
    lines = []
    for spec in hits:
        lines.append(f"[{spec['canonical'].upper()}] {spec['desc']}")
        lines.append(f"  공식: {spec['formula']}   (집계 SQL: {spec['sql']})")
        lines.append("  ※ 비율지표는 반드시 가중(Σ/Σ) — 단순평균은 Simpson 함정.")
    return "\n".join(lines)


def route(q, tools=None):
    """질문 → [(tool, score)] 상위 3. 결정론: 동점은 이름 오름차순.

    도구명 파트/의도 힌트가 '강한 근거'. 도큐스트링 토큰 겹침만으로는(불용어 제외)
    2점 이상이어야 추천 — 1토큰 우연 겹침의 '확신 있는 오추천'을 막는다."""
    tools = tools or catalog()
    qn = _norm(q)
    qtok = {t for t in _tokens(q) if len(t) >= 2 and t not in _STOPTOKENS}
    scores, strong = {}, set()
    for name, spec in tools.items():
        s = 0
        for part in name.split("_"):
            if len(part) >= 2 and part in qn:
                s += 3
                strong.add(name)
        dtok = {t for t in _tokens(spec["doc"]) if len(t) >= 2 and t not in _STOPTOKENS}
        s += len(qtok & dtok)
        scores[name] = s
    for hint, targets in INTENT_HINTS.items():
        if _norm(hint) in qn:
            for t in targets:
                if t in scores:
                    scores[t] += 4
                    strong.add(t)
    ranked = sorted(((n, s) for n, s in scores.items()
                     if s > 0 and (n in strong or s >= 2)),
                    key=lambda kv: (-kv[1], kv[0]))
    return ranked[:3]


def find_csv(q):
    """질문 속 실존하는 CSV 의 '절대경로' 반환 (없으면 None).

    상대경로를 그대로 돌려주면 REPL `run`(cwd=repo 루트)에서 사용자 cwd 기준
    파일을 못 찾아 traceback 이 났다 — 절대경로면 어디서 실행해도 유효."""
    for m in re.findall(r"[\w가-힣./\\-]+\.csv", q):
        for base in (Path.cwd(), ROOT):
            p = (base / m).expanduser()
            if p.exists():
                return str(p.resolve())
    return None


def _smalltalk(q, tools):
    """라우팅 0건 폴백 — 인사/감사/능력 질문은 오류 폴백 대신 대화로 응답."""
    ql = q.strip().lower()
    if any(h in ql for h in _CAPA):
        return (f"MADOBI 챗봇입니다 — 결정론 라우터로 {len(tools)}개 분석 도구에 연결해요.\n"
                "  · 숫자 검산/요약/리포트 · 예산/페이싱 · 소재 분석 · A/B·통계 · 코호트/이탈/LTV\n"
                "  · 지표 정의(\"ROAS가 뭐야?\") · 놀리지 회상(\"지난번 교훈?\") · 피드백 학습(\"앞으로 항상 ~\")\n"
                "`list` 로 전체 도구 목록을 볼 수 있어요.")
    if any(h in ql for h in _GREET):
        return "안녕하세요, 매도비입니다. 분석할 CSV 경로나 궁금한 지표를 말씀해 주세요. (`list` = 전체 도구)"
    if any(h in ql for h in _THANKS):
        return "천만에요 — 숫자는 코드가, 판단은 당신이. 또 불러주세요."
    return ("어떤 도구가 맞을지 확신이 없어요. `list` 로 전체 도구를 보거나,\n"
            "'검산/요약/예산/소재/이탈/코호트' 같은 작업 단어로 다시 물어봐 주세요.")


def suggest(q, tools=None, examples=None, ctx=None):
    """질문 → (사람용 답변 텍스트, [실행가능 argv 목록]). ctx: REPL 세션 맥락(csv/account)."""
    tools = tools or catalog()
    examples = examples if examples is not None else _examples()
    ctx = ctx or {}

    ans = metric_answer(q)
    if ans:
        return ans, []

    if is_feedback(q):
        # 간판 기능인 자기개선 루프로 연결. --no-commit: 발화 하나로 원격 push 가
        # 나가는 것은 과함 — 커밋 승격은 사용자의 명시적 단계로 분리.
        argv = ["python", "learn.py", "--feedback", q, "--scope", "global", "--no-commit"]
        return ("피드백으로 학습합니다 (자기개선 루프):\n"
                f'  실행: python learn.py --feedback "{q}" --scope global --no-commit\n'
                "  (놀리지에셋 반영. 검토 후 커밋/푸시하려면 --no-commit 제거 — 기본값은 자동 커밋+푸시)"), [argv]

    if is_recall(q):
        cq = clean_recall_query(q)
        acct = ctx.get("account") or detect_account(q)
        argv = (["python", "marketing/knowledge/recall.py"]
                + (["--account", acct] if acct else [])
                + ["--query", cq, "--limit", "5"])
        return ("놀리지에셋 회상으로 연결합니다:\n  실행: " + " ".join(argv)), [argv]

    ranked = route(q, tools)
    if not ranked:
        return _smalltalk(q, tools), []

    csv = find_csv(q) or ctx.get("csv")   # 이번 턴에 없으면 직전 턴의 CSV 를 이어받는다
    lines, argvs = ["추천 도구:"], []
    for i, (name, score) in enumerate(ranked, 1):
        doc = tools[name]["doc"]
        rel = tools[name]["path"].relative_to(ROOT)
        lines.append(f"  {i}. {name} — {doc[:60]}")
        ex = list(examples.get(name, []))
        if ex:
            if csv:
                ex = [csv if a.endswith(".csv") else a for a in ex]
            lines.append(f"     실행: {' '.join(ex)}")
            argvs.append(ex)
        else:
            lines.append(f"     인자 확인: python {rel} -h")
            argvs.append(["python", str(rel), "-h"])
    lines.append("(REPL에서는 `run` 또는 `run 2` 로 바로 실행)")
    return "\n".join(lines), argvs


# ---------------------------------------------------------------------- REPL
_BANNER = """=== MADOBI CHAT — 매도비 챗봇 (결정론 라우터) ===
자연어로 물어보세요. 예: "숫자 검산해줘", "ROAS가 뭐야?", "이탈 위험 고객 뽑아줘"
명령: list(도구 전체) · recall <질의>(놀리지) · run [번호](추천 실행) · exit"""


def repl():
    tools = catalog()
    examples = _examples()
    last_argvs = []
    ctx = {}   # 세션 맥락 — 직전 턴의 CSV/계정을 후속 질문에 이어붙인다
    print(_BANNER)
    while True:
        try:
            q = input("매도비> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit", "q"):
            break
        if q.lower() == "list":
            subprocess.run([sys.executable, str(HERE / "madobi.py"), "list"], cwd=ROOT)
            continue
        if q.lower().startswith("recall "):
            args = [sys.executable, str(HERE / "knowledge" / "recall.py")]
            if ctx.get("account"):
                args += ["--account", ctx["account"]]
            args += ["--query", q[7:].strip(), "--limit", "5"]
            subprocess.run(args, cwd=ROOT)
            continue
        if q.lower() == "run" or re.fullmatch(r"run \d+", q.lower()):
            if not last_argvs:
                print("먼저 질문해서 추천을 받은 뒤 run 하세요.")
                continue
            idx = int(q.split()[1]) - 1 if " " in q else 0
            if not 0 <= idx < len(last_argvs):
                print(f"run 번호는 1~{len(last_argvs)} 사이여야 합니다.")
                continue
            argv = last_argvs[idx]
            print(f"$ {' '.join(argv)}")
            subprocess.run([sys.executable] + argv[1:], cwd=ROOT)
            continue
        c = find_csv(q)
        if c:
            ctx["csv"] = c
        acct = detect_account(q)
        if acct:
            ctx["account"] = acct
        text, last_argvs = suggest(q, tools, examples, ctx)
        print(text)
    print("매도비 챗봇을 종료합니다. (숫자는 코드가, 판단은 당신이.)")


# ------------------------------------------------------------------ selftest
def _selftest():
    tools = catalog()
    examples = _examples()
    top = lambda q: [n for n, _ in route(q, tools)]

    assert "reconcile" in top("이 CSV 숫자 검산해줘")[:1], top("이 CSV 숫자 검산해줘")
    assert "reallocate" in top("예산 재배분 해줘"), top("예산 재배분 해줘")
    assert "abtest" in top("A/B 테스트 유의한지 봐줘"), top("A/B 테스트 유의한지 봐줘")
    assert "churn_score" in top("이탈 위험 고객 뽑아줘"), top("이탈 위험 고객 뽑아줘")
    assert "cohort" in top("코호트 리텐션 보여줘"), top("코호트 리텐션 보여줘")
    # 지표 Q&A — 용어집 즉답
    ans = metric_answer("ROAS가 뭐야?")
    assert ans and "revenue / spend" in ans, ans
    assert metric_answer("오늘 날씨 어때") is None
    # 놀리지 회상 의도 + 쿼리 정제 (의도어만으로 검색해 항상 빈손이던 사고 방지)
    assert is_recall("지난번에 배운 교훈 알려줘")
    assert not is_recall("예산 재배분 해줘")
    assert clean_recall_query("지난번에 배운 주말 CPA 교훈 알려줘") == "주말 CPA"
    # CSV 경로 감지 — 절대경로 계약 (REPL run 이 cwd 무관하게 동작)
    p = find_csv("marketing/samples/sample_campaign.csv 요약해줘")
    assert p and Path(p).is_absolute() and Path(p).exists(), p
    assert find_csv("없는파일.csv 요약해줘") is None
    # 예시 argv 가 통합 테스트에서 재사용되는지
    assert examples.get("reconcile"), "run_all.py 에서 예시를 못 읽음"
    # 결정론: 같은 질문 → 같은 라우팅
    assert route("예산 재배분 해줘", tools) == route("예산 재배분 해줘", tools)
    # suggest 가 (텍스트, argv 목록) 계약을 지키는지
    text, argvs = suggest("소재 피로도 점검해줘", tools, examples)
    assert "추천 도구" in text and argvs, text
    # --- 오라우팅 회귀 (적대 검증 재현 4문항: 정답 포함 + 오답 1위 금지) ---
    r1 = top("meta랑 google 중 어디에 돈 더 써야 해?")
    assert r1 and r1[0] != "price_optimizer" and set(r1) & {"channel_mix", "budget_optimizer", "reallocate"}, r1
    r2 = top("이번달 성과 어때?")
    assert set(r2) & {"report", "exec_report", "summarize"}, r2
    r3 = top("지난주 대비 CPA가 왜 올랐어?")
    assert "kpi_decomp" in r3, r3
    _, a4 = suggest("전환이 줄었는데 원인 분석해줘", tools, examples)
    assert a4, "진단형 질문에 추천 0건"
    # --- 피드백 티어: 강한 마커는 learn.py 로 단락, 약한 표현은 분석 라우팅 유지 ---
    ft, fa = suggest("앞으로 ROAS는 항상 배수(x)로 표기해줘", tools, examples)
    assert "learn.py" in ft and fa and "--no-commit" in fa[0], ft
    assert top("CTR 개선해줘")[0] == "ctr_benchmark", top("CTR 개선해줘")
    # --- 스몰토크: 인사/능력 질문이 오류 폴백으로 떨어지지 않는다 ---
    assert "확신이 없어요" not in suggest("안녕", tools, examples)[0]
    assert "도구" in suggest("너 뭐 할 수 있어?", tools, examples)[0]
    # --- 세션 맥락: 직전 턴 CSV 를 후속 질문에 이어받는다 ---
    ctx = {"csv": p}
    _, argvs2 = suggest("대시보드 만들어줘", tools, examples, ctx)
    assert argvs2 and any(p in " ".join(av) for av in argvs2), argvs2
    print(f"chat router self-test: PASS  ({len(tools)} tools routable, "
          f"{len(examples)} verified examples, {len(INTENT_HINTS)} intent hints)")


def main():
    ap = argparse.ArgumentParser(description="MADOBI 챗봇 — 결정론적 NL→도구 라우터 + REPL")
    ap.add_argument("--ask", help="단발 질의(비대화형) — 답변 출력 후 종료")
    ap.add_argument("--selftest", action="store_true", help="라우팅 자가검증")
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return
    if args.ask:
        text, _ = suggest(args.ask)
        print(f"Q: {args.ask}\n{text}")
        return
    repl()


if __name__ == "__main__":
    main()
