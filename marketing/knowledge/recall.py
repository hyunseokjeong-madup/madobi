"""
recall.py — 무상태(stateless) 놀리지 회상 API.
에이전트/스킬이 "이 주제로 우리가 아는 게 뭐였지?"를 물을 때 호출한다.
컨텍스트에 그대로 붙여넣을 수 있는 마크다운 블록을 돌려준다.

설계 원칙 (KARPATHY: 최소·결정론):
- search.py(같은 폴더)의 색인이 있으면 그걸 쓰고, 없으면 stdlib grep으로 폴백.
  → search.py는 방어적으로 import (try/except). 없어도 import·동작 보장.
- 외부 의존성 0. stdlib만 사용.
- 같은 입력 → 같은 출력 (점수 desc, 동점이면 경로 asc로 안정 정렬).

각 hit 출력 형식:
  - **title** (category) — snippet [path]

CLI:
  python recall.py --account acme --query 'weekend CPA' --limit 5
  python recall.py --query 'ROAS'
"""
import re
import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent          # marketing/knowledge
MARKETING = HERE.parent                          # marketing
HISTORY = MARKETING / "history"                  # marketing/history


# --- search.py 색인이 있으면 사용, 없으면 None (→ grep 폴백) ------------------
def _import_search():
    """같은 폴더의 search.py를 방어적으로 import. 없거나 깨졌으면 None."""
    try:
        import importlib
        if __package__:
            return importlib.import_module(".search", package=__package__)
    except Exception:
        pass
    try:
        import sys
        if str(HERE) not in sys.path:
            sys.path.insert(0, str(HERE))
        import search  # type: ignore
        return search
    except Exception:
        return None


def _try_index_search(query, category, limit):
    """search.py 색인이 결과를 내면 정규화해 반환. 색인 부재/실패면 None(→ grep 폴백).

    search.search(query, category, limit) 계약: [{path, title, category, snippet}],
    path 는 knowledge/ 기준 상대 posix. 빈 리스트도 '색인은 있으나 매치 0'으로 본다.
    """
    if not query:
        return None
    mod = _import_search()
    fn = getattr(mod, "search", None) if mod else None
    if not callable(fn):
        return None
    # 인덱스 파일이 실제로 있어야 색인 경로로 인정 (없으면 grep 폴백)
    db = getattr(mod, "DB_PATH", None)
    if db is not None and not Path(db).exists():
        return None
    # 손상 색인은 '매치 0건'이 아니라 폴백 신호 → grep 으로 내려간다.
    # (search.IndexCorrupt 가 그 신호. 자동 재빌드는 하지 않는다 — 비결정.)
    corrupt = getattr(mod, "IndexCorrupt", None)
    try:
        raw = fn(query, category=category, limit=limit)
    except TypeError:
        try:
            raw = fn(query)
        except Exception:
            return None
    except Exception as e:
        if corrupt is not None and isinstance(e, corrupt):
            return None  # 색인 손상 → grep 폴백
        return None      # 그 외 예외도 안전하게 폴백 (회상은 절대 죽지 않는다)
    if raw is None:
        return None
    hits = []
    for item in raw:
        if isinstance(item, dict) and item.get("path"):
            hits.append(_normalize_index_hit(item, query))
        elif isinstance(item, (tuple, list)) and item:
            hits.append(_hit_from_path(Path(item[0]), query,
                                       score=item[1] if len(item) > 1 else 0))
        elif isinstance(item, (str, Path)):
            hits.append(_hit_from_path(Path(item), query))
    return hits  # 빈 리스트면 '색인 사용했으나 매치 0'


def _normalize_index_hit(item, query):
    """search.py dict({path,title,category,snippet}) → 표준 hit. path는 knowledge 상대경로."""
    rel = str(item["path"])
    abspath = HERE / rel
    snippet = (item.get("snippet") or "").replace("\n", " ").strip()
    if not snippet:
        try:
            snippet = _snippet_for(abspath.read_text(encoding="utf-8"), _terms(query))
        except Exception:
            snippet = ""
    return {
        "title": item.get("title") or abspath.stem,
        "category": item.get("category") or _category_of(abspath),
        "snippet": snippet[:120].rstrip(),
        "path": _display_path(abspath),
        "score": 0,
    }


# --- grep 폴백 (search.py 없을 때 기본 경로) ----------------------------------
def _md_files():
    """knowledge/ 아래 모든 .md (build_kb 산출물). 경로 정렬로 결정론 보장."""
    return sorted(HERE.rglob("*.md"))


def _title_of(text, path):
    """첫 '# 제목' 라인을 title로. 없으면 파일명."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def _category_of(path):
    """knowledge 바로 아래 디렉터리명 = 카테고리. 루트 파일은 '_root'."""
    rel = path.relative_to(HERE)
    return rel.parts[0] if len(rel.parts) > 1 else "_root"


def _terms(query):
    """질의를 소문자 토큰으로 분해 (영문/숫자/한글 단위)."""
    return [t for t in re.split(r"\s+", (query or "").strip().lower()) if t]


def _snippet_for(text, terms, width=120):
    """질의어가 처음 등장하는 줄(또는 첫 본문 줄)을 잘라 스니펫으로."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    body = [l for l in lines if not l.startswith("#")]
    if terms:
        low = [l.lower() for l in lines]
        for orig, lo in zip(lines, low):
            if any(t in lo for t in terms):
                s = orig.lstrip("-* ").strip()
                return s[:width].rstrip()
    first = (body[0] if body else (lines[0] if lines else "")).lstrip("-* ").strip()
    return first[:width].rstrip()


def _score(text, title, terms):
    """질의어 등장 빈도로 점수. 제목 매치는 가중치 5배 (관련도↑)."""
    if not terms:
        return 0
    low = text.lower()
    tlow = title.lower()
    s = 0
    for t in terms:
        s += low.count(t)
        s += tlow.count(t) * 5
    return s


def _hit_from_path(path, query, title=None, snippet=None, score=0):
    """경로 → 표준 hit dict. 본문은 스니펫/제목 보강용으로만 읽음."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        text = ""
    return {
        "title": title or _title_of(text, path),
        "category": _category_of(path) if _is_under_kb(path) else "account",
        "snippet": snippet or _snippet_for(text, _terms(query)),
        "path": _display_path(path),
        "score": score,
    }


def _is_under_kb(path):
    try:
        path.resolve().relative_to(HERE)
        return True
    except ValueError:
        return False


def _display_path(path):
    """레포 루트 기준 상대경로로 깔끔하게 표기 (실패 시 절대경로)."""
    p = path.resolve()
    for base in (MARKETING.parent, MARKETING):
        try:
            return str(p.relative_to(base))
        except ValueError:
            continue
    return str(p)


def _grep(query, category, limit):
    terms = _terms(query)
    hits = []
    for f in _md_files():
        if category and _category_of(f) != category:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        title = _title_of(text, f)
        sc = _score(text, title, terms)
        # 질의가 있으면 매치된 것만, 없으면(카테고리 브라우징) 전부 후보
        if terms and sc == 0:
            continue
        hits.append({
            "title": title,
            "category": _category_of(f),
            "snippet": _snippet_for(text, terms),
            "path": _display_path(f),
            "score": sc,
        })
    # 점수 desc, 동점이면 경로 asc → 결정론
    hits.sort(key=lambda h: (-h["score"], h["path"]))
    return hits[:limit]


# --- 계정 전용 파일 (account.md / account-log.md) ------------------------------
def _account_files(account):
    out = []
    if not account:
        return out
    kb = HERE / f"{account}.md"
    if kb.exists():
        out.append(_hit_from_path(kb, "", title=None, snippet=None, score=10**9))
    log = HISTORY / f"{account}-log.md"
    if log.exists():
        # 형제 경로(_hit_from_path 등)와 동일하게 read 를 방어 — "회상은 절대 죽지 않는다".
        try:
            snippet = _snippet_for(log.read_text(encoding="utf-8"), [])
        except Exception:
            snippet = ""
        out.append({
            "title": f"{account} 이력 로그",
            "category": "history",
            "snippet": snippet,
            "path": _display_path(log),
            "score": 10**9,
        })
    return out


# --- 공개 API ------------------------------------------------------------------
def recall(account=None, query=None, category=None, limit=5):
    """
    결정론적 놀리지 회상.
    - account: 주면 <account>.md / <account>-log.md를 우선 노출.
    - query:   검색어 (없으면 카테고리 브라우징 모드).
    - category: knowledge 하위 카테고리명으로 제한 (예: 'metrics').
    - limit:   본문 KB 히트 개수 상한 (계정 파일은 별도로 항상 노출).
    반환: 에이전트가 컨텍스트에 붙여넣을 마크다운 문자열.
    """
    acct_hits = _account_files(account)

    kb_hits = _try_index_search(query, category, limit) if query else None
    source = "search.py 색인" if kb_hits is not None else "grep 폴백"
    if kb_hits is None:
        kb_hits = _grep(query, category, limit)

    # 결정론 신뢰도 배지(질의어 매칭 비율) — 색인/grep 경로 일관, score 와 독립.
    for h in kb_hits:
        h["confidence"] = _confidence(h, query)

    return _render(account, query, category, source, acct_hits, kb_hits)


def _render(account, query, category, source, acct_hits, kb_hits):
    head = "## 회상(recall)"
    crumbs = []
    if account:
        crumbs.append(f"account=`{account}`")
    if query:
        crumbs.append(f"query=`{query}`")
    if category:
        crumbs.append(f"category=`{category}`")
    crumbs.append(f"source={source}")
    L = [head, "> " + " · ".join(crumbs) if crumbs else head, ""]

    if acct_hits:
        L.append("### 계정 메모리")
        for h in acct_hits:
            L.append(_line(h))
        L.append("")

    L.append("### 놀리지")
    if kb_hits:
        for h in kb_hits:
            L.append(_line(h))
    else:
        L.append("- (해당 질의로 검산 통과 지식 없음 — 추측 금지, 데이터로 확인 필요)")
    return "\n".join(L)


def _haystack_for(h):
    """매칭 대상 텍스트 — title + *본문 전체*. 본문은 경로로 직접 읽어 색인/grep 경로가
    같은 값을 내게 한다(snippet 은 색인=FTS5 발췌 vs grep=파일전체로 출처가 달라 불일치).
    파일 read 실패 시 snippet 으로 폴백(회상은 죽지 않는다).
    """
    parts = [str(h.get("title", ""))]
    body = None
    p = h.get("path")
    if p:
        for base in (MARKETING.parent, MARKETING, HERE):
            cand = (base / p) if not Path(p).is_absolute() else Path(p)
            try:
                if cand.exists():
                    body = cand.read_text(encoding="utf-8")
                    break
            except Exception:
                body = None
    parts.append(body if body is not None else str(h.get("snippet", "")))
    return " ".join(parts).lower()


def _confidence(h, query):
    """결정론적 휴리스틱 신뢰도 = (히트가 담은 질의어 종류 수) / (전체 질의어 종류 수).

    score(빈도) 와 독립 + *본문 전체* 기준 → 색인 경로와 grep 경로가 같은 값을 낸다
    (예전엔 snippet 출처가 경로마다 달라 동일 문서가 다른 conf 를 냈다).
    '진실'이 아니라 표면 매칭 지표일 뿐(임베딩·의미판단 안 함 → 추측 금지).
    """
    terms = set(_terms(query))
    if not terms:
        return None
    hay = _haystack_for(h)
    matched = sum(1 for t in terms if t in hay)
    return matched / len(terms)


def _line(h):
    base = f"- **{h['title']}** ({h['category']}) — {h['snippet']} [{h['path']}]"
    c = h.get("confidence")
    if c is None:
        return base
    return base + f"  ·conf={c:.2f}"  # 결정론 휴리스틱 지표(질의어 매칭 비율), 진실 아님


# --- 회상 품질 = bandit 보상 신호 (시너지: RAG ↔ 자기개선 루프) -------------------
def recall_quality(account=None, query=None, category=None, limit=5):
    """이번 회상이 '얼마나 잘 답했나'를 0~1 결정론 점수로. bandit_policy 의 정직한 보상.

    외부 마케팅 성과(노이즈)와 달리 이건 100% 코드 산물이라 검산 가능:
      base = 색인 hit 이면 1.0, grep 폴백이면 0.5 (색인이 살아있는 경로가 더 건강)
      cover = 히트들의 평균 질의어 매칭 비율(_confidence)
      quality = base * (0.5 + 0.5*cover)   # 히트 0건이면 cover=0 → base*0.5
    arm=prefetch 카테고리, reward=recall_quality(...) 로 두면 루프가 철학을 안 깨고 닫힌다.
    """
    acct_hits = _account_files(account)
    kb_hits = _try_index_search(query, category, limit) if query else None
    base = 1.0 if kb_hits is not None else 0.5      # 색인 경로 vs grep 폴백
    if kb_hits is None:
        kb_hits = _grep(query, category, limit)
    confs = [c for c in (_confidence(h, query) for h in kb_hits) if c is not None]
    cover = sum(confs) / len(confs) if confs else 0.0
    return round(base * (0.5 + 0.5 * cover), 6)


# --- CLI / self-test -----------------------------------------------------------
def _selftest():
    """레포 실데이터로 동작 증명 — 색인 경로 + grep 폴백 둘 다 검증."""
    # 1) 기본 경로 (색인 있으면 색인, 없으면 grep)
    out = recall(query="ROAS", limit=3)
    assert "## 회상(recall)" in out, "헤더 누락"
    assert "[marketing/knowledge/" in out, "KB 경로 누락"
    assert "ROAS" in out.upper(), "ROAS 히트 없음"

    # 2) grep 폴백 강제: 인덱스 검색을 끊고도 결과가 나오는지
    grep_hits = _grep("ROAS", None, 3)
    assert grep_hits, "grep 폴백이 ROAS를 못 찾음"
    assert all("marketing/knowledge/" in h["path"] for h in grep_hits), "grep 경로 형식 오류"

    # 3) 손상 색인 → grep 폴백: '매치 0건'으로 위장되지 않고 폴백을 타는지.
    #    실제 .index.db 를 건드리지 않도록 백업→손상주입→복원으로 격리한다.
    mod = _import_search()
    db = Path(getattr(mod, "DB_PATH")) if mod and getattr(mod, "DB_PATH", None) else None
    if db is not None:
        backup = db.read_bytes() if db.exists() else None
        try:
            db.write_bytes(b"not a sqlite database -- deliberately corrupt\n")
            corrupt_out = recall(query="ROAS", limit=3)
            assert "ROAS" in corrupt_out.upper(), "손상 색인에서 grep 폴백 실패"
            assert "source=grep 폴백" in corrupt_out, "손상인데 색인 경로로 오인(폴백 미작동)"
        finally:
            if backup is not None:
                db.write_bytes(backup)        # 원래 인덱스 복원
            elif db.exists():
                db.unlink()                   # 원래 없었으면 정리
        print("[selftest] 손상 색인 → grep 폴백 확인 OK")

    # 4) confidence 배지: 결정론(같은 입력 같은 값) + 0~1 범위
    out_conf = recall(query="ROAS 심화", limit=3)
    assert "·conf=" in out_conf, "신뢰도 배지 누락"
    assert recall(query="ROAS 심화", limit=3) == out_conf, "회상 출력 비결정적"

    # 5) recall_quality (bandit 보상): 색인 경로(>0.5)가 grep 폴백보다 건강, 결정론
    q1 = recall_quality(query="ROAS", limit=3)
    assert 0.0 <= q1 <= 1.0, f"품질 점수 범위 이탈: {q1}"
    assert q1 == recall_quality(query="ROAS", limit=3), "recall_quality 비결정적"
    assert recall_quality(query="존재하지않을질의어xyzzy", limit=3) <= q1, "무매치가 매치보다 높음"

    # 6) confidence 경로 일관: 같은 문서를 색인/grep hit 으로 만들어도 conf 동일(본문 기준).
    real = _md_files()[0]
    p = _display_path(real)
    idx_like = {"title": real.stem, "snippet": "본문 일부 발췌만", "path": p}
    grep_like = {"title": real.stem, "snippet": "# 완전 다른 발췌", "path": p}
    for q in ("ROAS CPA", "예산 점검", "타깃"):
        assert _confidence(idx_like, q) == _confidence(grep_like, q), \
            f"색인/grep 경로 confidence 불일치 (query={q})"

    # 7) account-log 가 읽기불가/깨진 인코딩이어도 recall 은 죽지 않는다(공개 API 불변식).
    log = HISTORY / "_recall_crashtest_tmp-log.md"
    try:
        HISTORY.mkdir(parents=True, exist_ok=True)
        log.write_bytes(b"\xff\xfe broken utf8 \x80")
        crash = recall(account="_recall_crashtest_tmp", query="ROAS", limit=2)
        assert "## 회상(recall)" in crash, "손상 account-log 에서 recall 헤더 누락"
    finally:
        if log.exists():
            log.unlink()

    print(out)
    print(f"[selftest] confidence 배지 + recall_quality(={q1}) 결정론 OK")
    print("[selftest] confidence 경로 일관 + account-log 크래시 가드 OK")
    print(f"\n[selftest] OK — 색인 경로 + grep 폴백(직접 {len(grep_hits)}건) 모두 ROAS 회상 성공")


def main():
    ap = argparse.ArgumentParser(description="stateless knowledge recall")
    ap.add_argument("--account", default=None)
    ap.add_argument("--query", default=None)
    ap.add_argument("--category", default=None)
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        return
    print(recall(account=a.account, query=a.query, category=a.category, limit=a.limit))


if __name__ == "__main__":
    main()
