"""
놀리지에셋 전문검색(full-text search) — SQLite FTS5 + bm25 랭킹.

외부 의존성 0. 표준 라이브러리 sqlite3에 컴파일된 FTS5만 사용한다.
(macOS / 최신 CPython 의 sqlite3 는 FTS5 내장. 없으면 graceful degrade.)

  python search.py --build                                  # 인덱스 재생성
  python search.py 'ROAS high CPA'                          # 검색
  python search.py 'ROAS' --category diagnostics --limit 5  # 카테고리 한정

프론트매터(YAML) 는 있으면 단순 라인 파서로 읽고(없으면 무시),
없으면 H1 헤더에서 제목, 부모 디렉터리에서 카테고리를 추론한다.
"""
import argparse
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # marketing/knowledge
DB_PATH = HERE / ".index.db"


def fts5_available() -> bool:
    """이 파이썬의 sqlite3 가 FTS5 를 지원하는지 실측."""
    try:
        con = sqlite3.connect(":memory:")
        con.execute("CREATE VIRTUAL TABLE _t USING fts5(x)")
        con.close()
        return True
    except sqlite3.OperationalError:
        return False


def parse_frontmatter(text: str):
    """'---' 로 감싼 선두 블록을 단순 라인 파싱(YAML 라이브러리 없이).

    반환: (meta dict, frontmatter 제거한 본문). 프론트매터 없으면 ({}, 원문).
    'key: value' 만 처리. tags 는 콤마/대괄호 모두 허용.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta, end = {}, None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
        line = lines[i]
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip().lower()] = v.strip()
    if end is None:                       # 닫는 '---' 없으면 프론트매터 아님
        return {}, text
    body = "\n".join(lines[end + 1:])
    return meta, body


def _clean_tags(raw: str) -> str:
    """tags: [a, b] 또는 tags: a, b → 'a b' 공백구분 문자열."""
    raw = raw.strip().strip("[]")
    parts = [p.strip().strip("'\"") for p in raw.replace(",", " ").split()]
    return " ".join(p for p in parts if p)


def extract_doc(path: Path):
    """md 파일 1개 → (title, category, tags, body)."""
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    # 제목: frontmatter > 첫 H1 > 파일명
    title = meta.get("title")
    if not title:
        for line in body.splitlines():
            if line.startswith("# "):
                title = line[2:].split(" — ")[0].strip()
                break
    if not title:
        title = path.stem

    # 카테고리: frontmatter > 부모 디렉터리명 (knowledge 직속이면 'general')
    category = meta.get("category")
    if not category:
        category = path.parent.name if path.parent != HERE else "general"

    tags = _clean_tags(meta.get("tags", ""))
    return title, category, tags, body


def build_index(verbose: bool = False) -> int:
    """marketing/knowledge/**/*.md 전부 스캔 → FTS5 가상테이블 재생성.

    반환: 인덱싱된 행(문서) 수. FTS5 없으면 RuntimeError.
    """
    if not fts5_available():
        raise RuntimeError("이 파이썬 sqlite3 에 FTS5 가 없습니다 — 검색 인덱스를 만들 수 없음.")

    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    # path 는 비검색 컬럼(UNINDEXED): MATCH 대상에서 제외해 노이즈 방지.
    con.execute(
        "CREATE VIRTUAL TABLE docs USING fts5("
        "path UNINDEXED, title, category, tags, body, tokenize='unicode61')"
    )
    rows = 0
    for md in sorted(HERE.rglob("*.md")):
        rel = md.relative_to(HERE).as_posix()
        title, category, tags, body = extract_doc(md)
        con.execute(
            "INSERT INTO docs(path, title, category, tags, body) VALUES(?,?,?,?,?)",
            (rel, title, category, tags, body),
        )
        rows += 1
        if verbose:
            print(f"  + {rel}  [{category}] {title}")
    con.commit()
    con.close()
    return rows


def _fts_query(query: str) -> str:
    """사용자 입력을 FTS5 MATCH 안전 쿼리로. 각 토큰을 OR 로 묶고 따옴표 처리.

    'ROAS high CPA' → '"ROAS" OR "high" OR "CPA"' — 일부만 맞아도 랭킹되게.
    """
    toks = [t for t in query.replace('"', " ").split() if t]
    if not toks:
        return '""'
    return " OR ".join(f'"{t}"' for t in toks)


def search(query: str, category: str = None, limit: int = 5):
    """FTS5 MATCH + bm25 랭킹. 반환: [{path, title, category, snippet}].

    인덱스 없거나 FTS5 미지원이면 빈 리스트 반환(graceful).
    """
    if not DB_PATH.exists() or not fts5_available():
        return []
    con = sqlite3.connect(DB_PATH)
    match = _fts_query(query)
    # snippet(): 5번 컬럼=body, '[' ']' 하이라이트, '…' 생략, 12 토큰.
    sql = (
        "SELECT path, title, category, "
        "snippet(docs, 4, '[', ']', '…', 12), bm25(docs) AS rank "
        "FROM docs WHERE docs MATCH ?"
    )
    params = [match]
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY rank LIMIT ?"
    params.append(int(limit))
    try:
        cur = con.execute(sql, params)
        out = [
            {"path": p, "title": t, "category": c, "snippet": s}
            for (p, t, c, s, _r) in cur.fetchall()
        ]
    except sqlite3.OperationalError:
        out = []
    finally:
        con.close()
    return out


def _cli():
    ap = argparse.ArgumentParser(description="놀리지에셋 FTS5 전문검색")
    ap.add_argument("query", nargs="*", help="검색어 (공백 구분)")
    ap.add_argument("--build", action="store_true", help="인덱스 재생성")
    ap.add_argument("--category", default=None, help="카테고리 한정 (예: diagnostics)")
    ap.add_argument("--limit", type=int, default=5, help="결과 개수 (기본 5)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if not fts5_available():
        print("FTS5 미지원 sqlite3 — 검색 비활성화(degraded).", file=sys.stderr)
        return 0

    if args.build:
        n = build_index(verbose=args.verbose)
        print(f"INDEX BUILT: {n} rows → {DB_PATH.relative_to(HERE.parent.parent)}")
        if not args.query:
            return 0

    if not DB_PATH.exists():
        print("인덱스가 없습니다. 먼저 `python search.py --build` 실행.", file=sys.stderr)
        return 1

    q = " ".join(args.query)
    if not q:
        ap.print_help()
        return 0
    results = search(q, category=args.category, limit=args.limit)
    print(f"SEARCH '{q}'" + (f" [category={args.category}]" if args.category else "")
          + f" — {len(results)} hits")
    for i, r in enumerate(results, 1):
        print(f"{i}. ({r['category']}) {r['title']}  —  {r['path']}")
        print(f"   {r['snippet']}")
    return 0


# 자체검증: 인덱스 빌드 후 'ROAS' 검색이 결과를 내는지 확인.
def _self_test():
    n = build_index()
    assert n > 0, "indexed 0 docs"
    res = search("ROAS", limit=3)
    assert res, "ROAS 검색 결과 없음"
    print(f"SELF-TEST OK: indexed {n} rows, 'ROAS' → {len(res)} hits; top={res[0]['path']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _self_test()
    else:
        sys.exit(_cli())
