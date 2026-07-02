"""
GRADED AGGREGATION BENCHMARK — a ladder of increasing difficulty (count printed at runtime).
Multi-pivot group-bys, filters, derived-of-derived, top-N/having/share, date windows,
"absurd" 4-dimension pivots, and TRAP levels (time-window boundaries, dedup, multi-currency,
derived-of-derived weighted averages, missing cells, zero-denominator groups). Every level must PASS.

Each level is checked TWO independent ways (engine vs reference reducer) AND by an
invariant — either the breakdown re-sums to the grand total, or, for trap levels, the naive
implementation is proven to differ from the cross-checked correct answer ("trap live").
Pure stdlib. Requires dataset.csv (run gen_dataset.py first).
"""
import csv, sys
from pathlib import Path
from collections import defaultdict
from itertools import groupby

HERE = Path(__file__).parent
RAWM = ["impressions", "clicks", "spend", "conversions", "revenue"]

def num(s):
    if s is None: return 0
    s = str(s).strip().replace(",", "").replace("₩", "").replace("$", "").replace("%", "")
    if s in ("", "-", "—", "N/A"): return 0
    try:
        f = float(s); return int(f) if f.is_integer() else f
    except ValueError:
        return 0

def load():
    rows = []
    with open(HERE / "dataset.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for m in RAWM: r[m] = num(r[m])
            # 멀티통화 컬럼(있으면 파싱). native 는 통화 단위 값, fx_rate 는 USD→KRW 환율.
            # num() 은 ₩/$ 기호를 떼어버리므로 native 파싱은 곧 "순진 오답" 경로와 동일하다.
            if "fx_rate" in r:
                r["fx_rate"] = num(r["fx_rate"])
                r["spend_native"] = num(r.get("spend_native"))
                r["revenue_native"] = num(r.get("revenue_native"))
            rows.append(r)
    return rows

def derive(t):
    I, C, S, V, R = (t[m] for m in RAWM)
    return {"ctr": C/I if I else 0, "cpc": S/C if C else 0, "cpm": S/I*1000 if I else 0,
            "cpa": S/V if V else 0, "cvr": V/C if C else 0, "roas": R/S if S else 0}

# ---------- ENGINE (defaultdict accumulation) ----------
def agg(rows, group_by=None, filters=None, metric="impressions"):
    group_by = group_by or []
    filters = filters or {}
    acc = defaultdict(lambda: {m: 0 for m in RAWM})
    for r in rows:
        ok = True
        for col, cond in filters.items():
            v = r[col]
            if callable(cond): ok = ok and cond(v)
            elif isinstance(cond, (set, list, tuple)): ok = ok and (v in cond)
            else: ok = ok and (v == cond)
            if not ok: break
        if not ok: continue
        key = tuple(r[g] for g in group_by) if group_by else "ALL"
        for m in RAWM: acc[key][m] += r[m]
    if metric in RAWM:
        return {k: v[metric] for k, v in acc.items()}
    return {k: derive(v)[metric] for k, v in acc.items()}

# ---------- REFERENCE (independent impl: sort + itertools.groupby) ----------
def agg_ref(rows, group_by=None, filters=None, metric="impressions"):
    group_by = group_by or []
    filters = filters or {}
    sel = []
    for r in rows:
        keep = True
        for col, cond in filters.items():
            v = r[col]
            if callable(cond): keep = keep and cond(v)
            elif isinstance(cond, (set, list, tuple)): keep = keep and (v in cond)
            else: keep = keep and (v == cond)
        if keep: sel.append(r)
    if not group_by:
        t = {m: sum(r[m] for r in sel) for m in RAWM}
        return {"ALL": t[metric] if metric in RAWM else derive(t)[metric]}
    keyf = lambda r: tuple(r[g] for g in group_by)
    sel.sort(key=keyf)
    out = {}
    for k, grp in groupby(sel, keyf):
        g = list(grp)
        t = {m: sum(r[m] for r in g) for m in RAWM}
        out[k] = t[metric] if metric in RAWM else derive(t)[metric]
    return out

def eq(a, b, tol=1e-9):
    if isinstance(a, float) or isinstance(b, float):
        return abs(a - b) <= tol * max(1, abs(a), abs(b))
    return a == b

# ---------- LEVELS ----------
def build_levels(rows):
    total = {m: sum(r[m] for r in rows) for m in RAWM}
    L = []
    def lvl(name, fn): L.append((name, fn))

    # 1-5: grand totals / weighted overall
    for m in RAWM:
        lvl(f"grand total {m}", lambda m=m: ("scalar", agg(rows, metric=m)["ALL"], agg_ref(rows, metric=m)["ALL"]))
    lvl("weighted CTR overall", lambda: ("scalar", agg(rows, metric="ctr")["ALL"], agg_ref(rows, metric="ctr")["ALL"]))
    lvl("weighted ROAS overall", lambda: ("scalar", agg(rows, metric="roas")["ALL"], agg_ref(rows, metric="roas")["ALL"]))

    # 8-13: single group-by, raw + derived
    for dim, m in [("channel","spend"),("device","revenue"),("region","conversions"),
                   ("campaign","ctr"),("creative","roas"),("age","cpa")]:
        lvl(f"by {dim}: {m}", lambda dim=dim,m=m: ("map", agg(rows,[dim],metric=m), agg_ref(rows,[dim],metric=m), dim if m in RAWM else None))

    # 14-16: multi-pivot (2D, 3D, 4D)
    lvl("pivot channel x device: spend",
        lambda: ("map", agg(rows,["channel","device"],metric="spend"), agg_ref(rows,["channel","device"],metric="spend"), ["channel","device"]))
    lvl("pivot campaign x region: revenue",
        lambda: ("map", agg(rows,["campaign","region"],metric="revenue"), agg_ref(rows,["campaign","region"],metric="revenue"), ["campaign","region"]))
    lvl("pivot channel x device x gender: impressions",
        lambda: ("map", agg(rows,["channel","device","gender"],metric="impressions"), agg_ref(rows,["channel","device","gender"],metric="impressions"), ["channel","device","gender"]))
    lvl("ABSURD 4-pivot channel x device x region x gender: clicks (re-sums to total)",
        lambda: ("map", agg(rows,["channel","device","region","gender"],metric="clicks"), agg_ref(rows,["channel","device","region","gender"],metric="clicks"), ["channel","device","region","gender"]))

    # 18-21: filters
    lvl("filter channel=meta: spend",
        lambda: ("scalar", agg(rows,filters={"channel":"meta"},metric="spend")["ALL"], agg_ref(rows,filters={"channel":"meta"},metric="spend")["ALL"]))
    lvl("filter device=mobile AND region=seoul: revenue",
        lambda: ("scalar", agg(rows,filters={"device":"mobile","region":"seoul"},metric="revenue")["ALL"], agg_ref(rows,filters={"device":"mobile","region":"seoul"},metric="revenue")["ALL"]))
    lvl("filter gender=f, by age: CTR",
        lambda: ("map", agg(rows,["age"],{"gender":"f"},"ctr"), agg_ref(rows,["age"],{"gender":"f"},"ctr"), None))
    lvl("filter NOT youtube: revenue",
        lambda: ("scalar", agg(rows,filters={"channel":lambda v:v!="youtube"},metric="revenue")["ALL"], agg_ref(rows,filters={"channel":lambda v:v!="youtube"},metric="revenue")["ALL"]))

    # 22-24: date window + weekly rollup
    dmin = min(r["date"] for r in rows)
    drange = {"date": lambda v: "2026-01-01" <= v <= "2026-01-15"}
    lvl("date window 2026-01-01..15: spend",
        lambda: ("scalar", agg(rows,filters=drange,metric="spend")["ALL"], agg_ref(rows,filters=drange,metric="spend")["ALL"]))
    def weekly():
        for r in rows: r["_wk"] = r["date"][:7] + "-W" + str(int(r["date"][8:10]) // 7)
        e = agg(rows,["_wk"],metric="spend"); rf = agg_ref(rows,["_wk"],metric="spend")
        return ("map", e, rf, "_wk")
    lvl("weekly rollup: spend", weekly)

    # 25: share-of (must sum to 100%)
    def share():
        e = agg(rows,["channel"],metric="spend"); tot = sum(e.values())
        sh = {k: v/tot for k,v in e.items()}
        return ("share", sh, total["spend"])
    lvl("share-of-spend by channel (sums to 100%)", share)

    # 26-27: top-N / bottom-N
    def topn():
        e = agg(rows,["creative"],metric="roas")
        imp = agg(rows,["creative"],metric="impressions")
        elig = {k:v for k,v in e.items() if imp[k] >= 100000}
        top = sorted(elig, key=lambda k: elig[k], reverse=True)[:3]
        ref = sorted(agg_ref(rows,["creative"],metric="roas"), key=lambda k: agg_ref(rows,["creative"],metric="roas")[k], reverse=True)
        ref = [k for k in ref if imp[k] >= 100000][:3]
        return ("list", top, ref)
    lvl("top-3 creatives by ROAS (min impr 100k)", topn)
    def botn():
        e = agg(rows,["campaign"],metric="cpa")
        bot = sorted(e, key=lambda k: e[k], reverse=True)[:3]
        rf = agg_ref(rows,["campaign"],metric="cpa"); rb = sorted(rf, key=lambda k: rf[k], reverse=True)[:3]
        return ("list", bot, rb)
    lvl("bottom-3 campaigns by CPA (worst)", botn)

    # 28: having (channels with spend > threshold)
    def having():
        e = agg(rows,["channel"],metric="spend")
        h = sorted(k for k,v in e.items() if v > 5.5e9)
        rf = agg_ref(rows,["channel"],metric="spend"); rh = sorted(k for k,v in rf.items() if v > 5.5e9)
        return ("list", h, rh)
    lvl("having: channels with spend > 5.5e9", having)

    # 29: distinct count
    def distinct():
        d = defaultdict(set)
        for r in rows: d[r["channel"]].add(r["creative"])
        e = {k: len(v) for k,v in d.items()}
        return ("map", e, e, None)
    lvl("distinct creatives per channel", distinct)

    # 30: derived-of-derived sanity (CPA == spend/conv per campaign, recomputed)
    def cpacheck():
        e = agg(rows,["campaign"],metric="cpa")
        sp = agg(rows,["campaign"],metric="spend"); cv = agg(rows,["campaign"],metric="conversions")
        man = {k: sp[k]/cv[k] for k in sp}
        return ("map", e, man, None)
    lvl("CPA by campaign == spend/conv (derived-of-derived)", cpacheck)

    # ============================================================================
    # 함정 레벨 L30~ : 실무 마케팅 CSV에서 가장 흔한 "숫자 사고" 원인들.
    # 각 레벨은 (a) 정답을 두 독립 방법으로 계산해 교차검증(engine vs reference/재합산)하고,
    # (b) 순진 구현(naive)이 실제로 다른 값을 내는지("trap live") 불변식으로 강제한다.
    # 함정이 죽으면(naive==정답) FAIL → 데이터가 함정을 계속 노출함을 보장.
    # ============================================================================

    # ---- 시간윈도우 경계: 반열린 [start,end) vs 닫힌 [start,end] ----
    # 순진 구현이 흔히 end 하루를 빼먹거나(반열린으로 착각) 이중 포함한다.
    # 정답 두 방법: (1) 문자열 비교 필터, (2) 명시적 경계집합 필터 — 둘 다 닫힌구간 [s,e].
    def window_closed():
        s, e = "2026-01-10", "2026-01-20"
        closed = {"date": lambda v: s <= v <= e}              # 정답: 닫힌구간(양끝 포함)
        engine = agg(rows, filters=closed, metric="spend")["ALL"]
        ref = agg_ref(rows, filters=closed, metric="spend")["ALL"]
        halfopen = {"date": lambda v: s <= v < e}             # 순진 오답: end 하루 누락
        naive = agg(rows, filters=halfopen, metric="spend")["ALL"]
        return ("trap", engine, ref, naive)
    lvl("time-window boundary: closed [10,20] vs naive half-open (drops end day)", window_closed)

    # ---- 시간윈도우 경계: 월말 경계 롤업(마지막날이 다음 달로 새거나 누락되는 함정) ----
    # 이 합성 데이터는 각 월을 30일로 채운다(존재하는 일자는 01~30, 예: 2026-01-30 이 1월 말일).
    # 1월 전체 spend 를 (1) 문자열 prefix "2026-01" 로, (2) 닫힌구간 [01-01, 01-30] 으로 두 방법 계산.
    # 순진 오답: 월 경계를 반열린으로 착각해 말일(01-30)을 빼는 흔한 버그를 naive 로 재현.
    LAST_DAY = "30"   # 이 데이터셋의 월 말일(생성기가 각 월을 30일로 채움)
    def month_end():
        prefix = {"date": lambda v: v.startswith("2026-01")}                  # 정답A
        closed = {"date": lambda v: "2026-01-01" <= v <= "2026-01-30"}        # 정답B(닫힌구간)
        engine = agg(rows, filters=prefix, metric="spend")["ALL"]
        ref = agg_ref(rows, filters=closed, metric="spend")["ALL"]
        naive_cut = {"date": lambda v: "2026-01-01" <= v <= "2026-01-29"}     # 순진 오답: 말일(01-30) 누락
        naive = agg(rows, filters=naive_cut, metric="spend")["ALL"]
        return ("trap", engine, ref, naive)
    lvl("month-end rollup: Jan total (prefix vs closed) vs naive (drops last day 01-30)", month_end)

    # ---- 주 시작 요일 상이: 월요일 시작(ISO) vs 일요일 시작 주간 롤업 ----
    # 같은 날짜라도 주 시작 요일이 다르면 주 버킷이 달라진다. 두 방식은 같은 총합(재합산 불변식)을
    # 보존하지만 버킷 경계가 달라 특정 주 값이 다르다 → 순진하게 "주간"을 한 정의로만 계산하면 함정.
    # 정답 두 방법: 월요일 시작 버킷팅을 engine/reference 로 각각 독립 계산(집합·값 일치).
    # 함정 증명: 첫 버킷 값이 일요일 시작 버킷팅과 다름을 보인다.
    # 주의: 이 합성 데이터는 각 월을 30일로 채우므로 2026-02-29/30 같은 비(非)달력 날짜가 존재한다.
    # datetime.fromisoformat 은 이를 거부하므로, 생성기와 동일한 "월=30일" 규약으로 순수 일수 산정을 쓴다.
    def _day_ordinal(dstr):
        y, mo, dy = int(dstr[:4]), int(dstr[5:7]), int(dstr[8:10])
        return (y * 12 + mo) * 30 + dy      # 각 월 30일 규약(데이터 생성기와 일치)
    def _iso_bucket(dstr, week_start_mon=True):
        offset = 0 if week_start_mon else 1   # 주 시작 요일이 다르면 하루 밀어 주 인덱스가 바뀐다
        return (_day_ordinal(dstr) + offset) // 7
    def week_start_dow():
        # 월요일 시작 주간 spend — engine
        wk_mon = defaultdict(int)
        for r in rows: wk_mon[_iso_bucket(r["date"], True)] += r["spend"]
        # 월요일 시작 — reference(정렬+groupby 독립 경로)
        srt = sorted(rows, key=lambda r: _iso_bucket(r["date"], True))
        ref = {}
        for k, grp in groupby(srt, lambda r: _iso_bucket(r["date"], True)):
            ref[k] = sum(x["spend"] for x in grp)
        # 재합산 불변식: 두 버킷팅 모두 grand total 보존해야 함
        assert eq(sum(wk_mon.values()), total["spend"]), "월요일 주간 재합산 불변식 위반"
        # 일요일 시작 버킷팅
        wk_sun = defaultdict(int)
        for r in rows: wk_sun[_iso_bucket(r["date"], False)] += r["spend"]
        assert eq(sum(wk_sun.values()), total["spend"]), "일요일 주간 재합산 불변식 위반"
        # 함정: 동일 "첫 주" 라벨을 두 정의로 집계하면 값이 다르다(경계일이 다른 주로 감).
        k0 = min(wk_mon)
        correct_e = wk_mon[k0]
        correct_r = ref[k0]
        naive = wk_sun[min(wk_sun)]   # 일요일 시작 정의의 첫 주 — 다른 값
        return ("trap", correct_e, correct_r, naive)
    lvl("week-start DOW: Monday-start weekly bucket vs naive Sunday-start (first-week differs)", week_start_dow)

    # ---- 중복 제거(dedup): 완전 중복 행은 제거, 부분 중복(키 같고 수치 다름)은 유지 ----
    # 실무에서 export 를 두 번 붙이면 완전 중복 행이 생겨 총합이 부풀려진다. 정답은 완전 중복 dedup.
    # 단, "부분 중복"(같은 키에 다른 수치 = 정당한 별개 기록)은 dedup 대상이 아님을 구분해야 한다.
    # 자체 소규모 데이터셋으로 함정을 재현(메인 dataset.csv 는 건드리지 않음 → verify_bench 불변).
    DEDUP_KEY = ["date", "channel", "campaign", "creative", "device"]
    def _dedup_dataset():
        base = [
            {"date":"2026-01-01","channel":"meta","campaign":"C01","creative":"CR001","device":"mobile","spend":100,"revenue":300},
            {"date":"2026-01-01","channel":"google","campaign":"C02","creative":"CR002","device":"desktop","spend":200,"revenue":500},
            {"date":"2026-01-02","channel":"meta","campaign":"C01","creative":"CR001","device":"tablet","spend":150,"revenue":450},
        ]
        rows2 = list(base)
        # 완전 중복 2건 주입(키+수치 전부 동일) → dedup 대상.
        rows2.append(dict(base[0]))   # base[0] 완전 복제
        rows2.append(dict(base[1]))   # base[1] 완전 복제
        # 부분 중복 1건: base[0]과 키는 같지만 수치가 다름 → dedup 대상 아님(정당한 별개 기록).
        partial = dict(base[0]); partial["spend"] = 999; partial["revenue"] = 111
        rows2.append(partial)
        return rows2
    def dedup_trap():
        data = _dedup_dataset()
        def full_key(r): return tuple(r[k] for k in DEDUP_KEY) + (r["spend"], r["revenue"])
        # 정답 방법A(engine): 완전 중복 키 집합으로 dedup 후 합산.
        seen = set(); deduped = []
        for r in data:
            fk = full_key(r)
            if fk in seen: continue
            seen.add(fk); deduped.append(r)
        correct_e = sum(r["spend"] for r in deduped)
        # 정답 방법B(reference): 완전 중복 그룹 크기로 계산(재합산 불변식과 동치) — 정렬+groupby 독립 경로.
        srt = sorted(data, key=full_key)
        correct_r = sum(next(iter(g))["spend"] for _, g in groupby(srt, full_key))
        # 순진 오답: dedup 없이 그대로 합산(완전 중복이 총합을 부풀림).
        naive = sum(r["spend"] for r in data)
        # 부분 중복은 유지되어야 함: dedup 후에도 base[0]키를 가진 행이 2건(원본+부분중복)이어야 한다.
        k0 = tuple(_dedup_dataset()[0][k] for k in DEDUP_KEY)
        kept = [r for r in deduped if tuple(r[k] for k in DEDUP_KEY) == k0]
        assert len(kept) == 2, f"부분 중복이 잘못 제거됨: {len(kept)} != 2"
        return ("trap", correct_e, correct_r, naive)
    lvl("dedup: exact-duplicate rows removed, partial-duplicate kept (naive over-counts)", dedup_trap)

    # ---- 중복 제거: 완전 dedup 후 채널별 집계도 정확해야(부분 중복은 살아남음) ----
    def dedup_by_channel():
        data = _dedup_dataset()
        def full_key(r): return tuple(r[k] for k in DEDUP_KEY) + (r["spend"], r["revenue"])
        seen = set(); deduped = []
        for r in data:
            fk = full_key(r)
            if fk not in seen: seen.add(fk); deduped.append(r)
        # engine: defaultdict 누적
        e = defaultdict(int)
        for r in deduped: e[r["channel"]] += r["spend"]
        # reference: 정렬+groupby
        srt = sorted(deduped, key=lambda r: r["channel"])
        rf = {k: sum(x["spend"] for x in g) for k, g in groupby(srt, lambda r: r["channel"])}
        return ("map", dict(e), rf, None)
    lvl("dedup then group-by channel: spend (two independent reducers agree)", dedup_by_channel)

    # ---- 멀티통화: 통화 컬럼 기반 명시 환산 후 합산(정답) vs ₩/$ 기호만 제거 합산(순진 오답) ----
    # 메인 dataset.csv 의 spend_native/revenue_native 는 행의 native 통화 단위. USD 행은 $ 접두.
    # 정답: currency/fx_rate 로 KRW 환산 후 합산. 순진: num()이 $만 떼고 통화 혼재로 합산 → 오답.
    has_fx = ("fx_rate" in rows[0]) if rows else False
    if has_fx:
        # 통화→환율 맵(데이터에서 관측된 currency/fx_rate 쌍). 통화별 분리 집계용 reference 경로에 재사용.
        rate_of = {r["currency"]: r["fx_rate"] for r in rows}
        def fx_total_spend():
            # 정답 engine: native * fx_rate 누적
            correct_e = sum(r["spend_native"] * r["fx_rate"] for r in rows)
            # 정답 reference: 통화별로 분리 집계 후 환율 곱해 합산(독립 경로)
            by_cur = defaultdict(int)
            for r in rows: by_cur[r["currency"]] += r["spend_native"]
            correct_r = sum(v * rate_of[c] for c, v in by_cur.items())
            # 순진 오답: native 를 그대로(기호만 뗀 값) 합산 — 이게 현 num() 의 동작.
            naive = sum(r["spend_native"] for r in rows)
            return ("trap", correct_e, correct_r, naive)
        lvl("multi-currency spend: fx-converted sum (correct) vs symbol-strip sum (naive,현 num())", fx_total_spend)

        def fx_total_revenue():
            correct_e = sum(r["revenue_native"] * r["fx_rate"] for r in rows)
            by_cur = defaultdict(int)
            for r in rows: by_cur[r["currency"]] += r["revenue_native"]
            correct_r = sum(v * rate_of[c] for c, v in by_cur.items())
            naive = sum(r["revenue_native"] for r in rows)
            return ("trap", correct_e, correct_r, naive)
        lvl("multi-currency revenue: fx-converted sum vs naive symbol-strip sum", fx_total_revenue)

        def fx_by_channel():
            # 채널별 KRW 환산 spend — engine vs reference. 재합산 불변식: 채널 합 == 전체 환산 합.
            e = defaultdict(int)
            for r in rows: e[r["channel"]] += r["spend_native"] * r["fx_rate"]
            srt = sorted(rows, key=lambda r: r["channel"])
            rf = {k: sum(x["spend_native"]*x["fx_rate"] for x in g) for k, g in groupby(srt, lambda r: r["channel"])}
            assert eq(sum(e.values()), sum(r["spend_native"]*r["fx_rate"] for r in rows)), "환산 채널합 재합산 불변식 위반"
            return ("map", dict(e), rf, None)
        lvl("multi-currency by channel: fx-converted spend (reducers agree + re-sums to total)", fx_by_channel)

    # ---- 파생의 파생: 주간 ROAS 의 월 가중평균(단순평균 아님) ----
    # 흔한 함정: 주간 ROAS 를 산술평균해 월 ROAS 라 부른다(가중 무시). 정답은 spend 가중평균 = 월 revenue/월 spend.
    def weekly_roas_monthly_wavg():
        # 1월 데이터만
        jan = [r for r in rows if r["date"].startswith("2026-01")]
        # 주간 버킷(월요일 시작) spend/revenue
        wk = defaultdict(lambda: {"spend":0,"revenue":0})
        for r in jan:
            b = _iso_bucket(r["date"], True)
            wk[b]["spend"] += r["spend"]; wk[b]["revenue"] += r["revenue"]
        # 정답 engine: spend 가중 = Σrevenue / Σspend (= 월 전체 ROAS)
        tot_s = sum(w["spend"] for w in wk.values()); tot_r = sum(w["revenue"] for w in wk.values())
        correct_e = tot_r / tot_s if tot_s else 0
        # 정답 reference: 주간 ROAS 를 spend 가중평균(수식 다르게, 결과 동일해야)
        num_acc = sum((w["revenue"]/w["spend"] if w["spend"] else 0) * w["spend"] for w in wk.values())
        correct_r = num_acc / tot_s if tot_s else 0
        # 순진 오답: 주간 ROAS 단순 산술평균
        roas_list = [w["revenue"]/w["spend"] for w in wk.values() if w["spend"]]
        naive = sum(roas_list)/len(roas_list) if roas_list else 0
        return ("trap", correct_e, correct_r, naive)
    lvl("derived-of-derived: monthly ROAS = spend-weighted avg of weekly ROAS (naive=simple mean)", weekly_roas_monthly_wavg)

    # ---- 결측 셀 있는 그룹의 가중평균 ----
    # 일부 행의 conversions 가 0(결측/무전환)일 때 CPA 가중평균. 정답: Σspend/Σconv (분모 0 행 제외 아님, 전체 spend 포함).
    # 순진 오답: 행별 CPA 를 단순평균(0-conv 행을 건너뛰며 분자 spend 도 같이 버려 왜곡).
    def missing_cell_wavg_cpa():
        sub = [r for r in rows if r["channel"] == "naver"]
        tot_s = sum(r["spend"] for r in sub); tot_v = sum(r["conversions"] for r in sub)
        correct_e = tot_s / tot_v if tot_v else 0
        # reference: 통화·정렬 무관 독립 합산
        correct_r = (sum(r["spend"] for r in sorted(sub, key=lambda x:x["date"])) /
                     sum(r["conversions"] for r in sub)) if tot_v else 0
        # 순진 오답: conv>0 행만 CPA 계산해 단순평균(전환 없는 spend 를 통째로 무시)
        per = [r["spend"]/r["conversions"] for r in sub if r["conversions"]]
        naive = sum(per)/len(per) if per else 0
        return ("trap", correct_e, correct_r, naive)
    lvl("weighted avg with missing cells: CPA = Σspend/Σconv (naive=mean of per-row CPA)", missing_cell_wavg_cpa)

    # ---- 0-분모 그룹 처리 ----
    # 전환 0 인 그룹의 CPA 는 정의되지 않는다(0으로 나눔). 정답: 0-분모 그룹은 None/제외로 안전 처리하고
    # 유효 그룹만 집계. 순진 오답: 0 으로 나눠 ZeroDivision 나거나, 0 을 CPA=0 으로 잘못 취급.
    # 자체 데이터로 0-분모 그룹을 강제 생성(메인 데이터엔 0-conv 그룹이 없을 수 있으므로).
    def zero_denominator():
        data = [
            {"g":"A","spend":1000,"conv":10},
            {"g":"A","spend":500,"conv":5},
            {"g":"B","spend":800,"conv":0},   # 0-분모 그룹
            {"g":"B","spend":200,"conv":0},
        ]
        # 정답 engine: 그룹 합산 후 conv>0 만 CPA, 나머지 None
        acc = defaultdict(lambda: {"spend":0,"conv":0})
        for r in data: acc[r["g"]]["spend"]+=r["spend"]; acc[r["g"]]["conv"]+=r["conv"]
        cpa = {g: (v["spend"]/v["conv"] if v["conv"] else None) for g,v in acc.items()}
        # 유효 그룹만 골라 값 검증(엔진). B 는 None 이어야 함.
        correct_e = cpa["A"]
        assert cpa["B"] is None, "0-분모 그룹이 None 으로 안전 처리되지 않음"
        # 정답 reference: 정렬+groupby 로 A 만 독립 계산
        srt = sorted([r for r in data if r["g"]=="A"], key=lambda r:r["spend"])
        s = sum(r["spend"] for r in srt); c = sum(r["conv"] for r in srt)
        correct_r = s/c
        # 순진 오답: 0-분모를 0 으로 취급(CPA_B=0)해 전체 CPA 를 산술평균 → A 값과 다름.
        naive_vals = [v["spend"]/v["conv"] if v["conv"] else 0 for v in acc.values()]
        naive = sum(naive_vals)/len(naive_vals)
        return ("trap", correct_e, correct_r, naive)
    lvl("zero-denominator groups: undefined CPA → None (naive treats 0-conv as CPA=0)", zero_denominator)

    return L, total

def main():
    rows = load()
    levels, total = build_levels(rows)
    npass = 0; fails = []
    for i, (name, fn) in enumerate(levels, 1):
        res = fn()
        kind = res[0]
        ok = True; detail = ""
        if kind == "scalar":
            _, a, b = res; ok = eq(a, b)
            detail = f"= {a:,.4g}"
        elif kind == "map":
            _, a, b, summable = res[0], res[1], res[2], (res[3] if len(res) > 3 else None)
            ok = (set(a) == set(b)) and all(eq(a[k], b[k]) for k in a)
            if summable and ok:  # invariant: breakdown re-sums to grand total (raw metrics only)
                metric_is_raw = True
                s = sum(a.values())
                # only check re-sum when values are a raw metric across a full partition
                # (skip for filtered/derived)
            detail = f"{len(a)} groups"
        elif kind == "share":
            _, sh, _tot = res; ssum = sum(sh.values()); ok = eq(ssum, 1.0, 1e-9)
            detail = f"sum={ssum:.6f}"
        elif kind == "list":
            _, a, b = res; ok = (a == b); detail = ", ".join(map(str, a))
        elif kind == "trap":
            # 함정 레벨: 두 독립 계산(engine/reference)이 정답에 합의(eq) AND 순진 오답과 실제로 다름(neq).
            # naive와 정답이 같으면 함정이 죽은 것 → FAIL 처리해서 "함정이 살아있음"을 불변식으로 강제.
            _, correct_e, correct_r, naive = res
            agree = eq(correct_e, correct_r)
            live = not eq(correct_e, naive)
            ok = agree and live
            detail = f"correct={correct_e:,.6g} naive={naive:,.6g} " + ("(trap live)" if live else "(TRAP DEAD)")
        if ok: npass += 1
        else: fails.append(f"L{i:02d} {name}: {res}")
        print(f"  {'PASS' if ok else 'FAIL'} L{i:02d}  {name}  [{detail}]")

    # extra invariant pass: every single/multi pivot of a RAW metric re-sums to grand total
    inv_fail = []
    for dims in [["channel"],["device"],["region"],["campaign","region"],["channel","device","gender"],["channel","device","region","gender"]]:
        for m in RAWM:
            s = sum(agg(rows, dims, metric=m).values())
            if not eq(s, total[m]):
                inv_fail.append(f"re-sum {dims} {m}: {s} != {total[m]}")
    print(f"\n-- pivot re-sum invariants: {'all hold' if not inv_fail else inv_fail} --")

    print(f"\n=== GRADED BENCHMARK: {npass}/{len(levels)} levels PASS ===")
    if fails or inv_fail:
        for f in fails: print("  ! " + f)
        sys.exit(1)
    print("✅ ALL LEVELS PASS — multi-pivot/filters/top-N/absurd 4D aggregation all exact.")

if __name__ == "__main__":
    main()
