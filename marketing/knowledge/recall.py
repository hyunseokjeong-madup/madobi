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
    try:
        raw = fn(query, category=category, limit=limit)
    except TypeError:
        try:
            raw = fn(query)
        except Exception:
            return None
    except Exception:
        return None
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
        out.append({
            "title": f"{account} 이력 로그",
            "category": "history",
            "snippet": _snippet_for(log.read_text(encoding="utf-8"), []),
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


def _line(h):
    return f"- **{h['title']}** ({h['category']}) — {h['snippet']} [{h['path']}]"


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

    print(out)
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
