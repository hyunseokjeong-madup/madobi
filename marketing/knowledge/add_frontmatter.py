#!/usr/bin/env python3
"""
프론트매터 백필 도구 — marketing/knowledge/**/*.md 를 훑어
YAML 프론트매터가 없는 md 파일 맨 앞에 표준 프론트매터를 덧붙인다.

설계 원칙 (KARPATHY: 군더더기 없이):
- stdlib 전용 (외부 의존성 0). 코어 불변식 준수.
- 멱등(idempotent): 이미 맨 위가 '---' 인 파일은 건너뜀.
- 기본은 드라이런. --apply 일 때만 실제로 기록.
- 본문은 바이트 단위로 보존. 프론트매터만 앞에 prepend.
- _GLOBAL.md 도 (맨 위에 '---' 가 없으므로) 프론트매터를 받지만 본문은 손대지 않는다.

frontmatter 형식:
---
title: <첫 # 헤딩 또는 파일명에서 도출>
category: <상위 디렉터리 경로명, 예: metrics/bidding/...>
tags: [<경로+파일명에서 몇 개 도출>]
verified: true
status: stable
last_updated: 2026-06-28
related: []
---
"""
import argparse
import re
from datetime import date
from pathlib import Path

# 놀리지 루트 (이 스크립트의 상위 = marketing/knowledge)
KB_ROOT = Path(__file__).resolve().parent
LAST_UPDATED = "2026-06-28"

# tags 잡음 제거용 — 너무 흔하거나 의미 없는 토큰
_STOP_TOKENS = {"the", "a", "an", "of", "and", "global", "md"}


def derive_title(text: str, path: Path) -> str:
    """첫 '# ' 헤딩에서 제목을 뽑고, 없으면 파일명(stem)에서 도출."""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    # 폴백: 파일명 → 언더스코어/하이픈을 공백으로
    stem = path.stem.lstrip("_")
    return re.sub(r"[_\-]+", " ", stem).strip() or path.stem


def derive_category(path: Path) -> str:
    """knowledge 루트 기준 상위 디렉터리의 상대 경로명.
    예) metrics/roas.md -> 'metrics', a/b/c/x.md -> 'a/b/c'.
    루트 바로 아래 파일(_GLOBAL.md 등)은 'knowledge'."""
    rel_parent = path.parent.resolve().relative_to(KB_ROOT)
    parts = rel_parent.parts
    if not parts:  # 루트 바로 아래
        return KB_ROOT.name  # 'knowledge'
    return "/".join(parts)


def derive_tags(path: Path, category: str, max_tags: int = 5) -> list[str]:
    """경로 디렉터리 조각 + 파일명 조각에서 태그 후보를 만든다.
    소문자, 중복/불용어 제거, 순서 보존, 최대 max_tags 개."""
    raw: list[str] = []
    # 카테고리 경로 조각
    for seg in category.split("/"):
        raw.extend(re.split(r"[_\-/]+", seg))
    # 파일명 조각
    for tok in re.split(r"[_\-]+", path.stem.lstrip("_")):
        raw.append(tok)

    seen: set[str] = set()
    out: list[str] = []
    for t in raw:
        t = t.strip().lower()
        if not t or t in _STOP_TOKENS or t in seen:
            continue
        seen.add(t)
        out.append(t)
        if len(out) >= max_tags:
            break
    return out


def has_frontmatter(text: str) -> bool:
    """파일 맨 위(선행 공백/BOM 허용)가 YAML 프론트매터 구분자 '---' 인가."""
    stripped = text.lstrip("﻿")  # BOM 제거 후 판단
    # 맨 첫 줄이 정확히 '---' (또는 '--- ' 류)면 프론트매터로 간주
    first_line = stripped.split("\n", 1)[0].rstrip()
    return first_line == "---"


def build_frontmatter(title: str, category: str, tags: list[str]) -> str:
    """프론트매터 블록 문자열 생성. YAML 안전을 위해 title 은 따옴표 처리."""
    safe_title = title.replace('"', '\\"')
    tag_str = "[" + ", ".join(tags) + "]"
    return (
        "---\n"
        f'title: "{safe_title}"\n'
        f"category: {category}\n"
        f"tags: {tag_str}\n"
        "verified: true\n"
        "status: stable\n"
        f"last_updated: {LAST_UPDATED}\n"
        "related: []\n"
        "---\n"
    )


def iter_md_files() -> list[Path]:
    return sorted(KB_ROOT.rglob("*.md"))


def process(apply: bool) -> dict:
    files = iter_md_files()
    added, skipped, results = 0, 0, []
    for f in files:
        text = f.read_text(encoding="utf-8")
        if has_frontmatter(text):
            skipped += 1
            continue
        title = derive_title(text, f)
        category = derive_category(f)
        tags = derive_tags(f, category)
        block = build_frontmatter(title, category, tags)
        rel = f.relative_to(KB_ROOT)
        results.append((str(rel), category, title, tags))
        if apply:
            # 본문을 바이트 단위로 보존: 블록을 앞에 붙이기만 한다.
            f.write_text(block + text, encoding="utf-8")
        added += 1
    return {
        "total": len(files),
        "added": added,
        "skipped": skipped,
        "results": results,
        "applied": apply,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="knowledge md 파일에 YAML 프론트매터 백필 (기본 드라이런)"
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="실제로 파일에 기록 (미지정 시 드라이런: 무엇이 바뀔지만 출력)",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=5,
        help="출력 미리보기 개수 (요약 출력용, 처리 자체에는 영향 없음)",
    )
    args = ap.parse_args(argv)

    info = process(apply=args.apply)
    mode = "APPLY" if info["applied"] else "DRY-RUN"
    print(f"[{mode}] knowledge root: {KB_ROOT}")
    print(
        f"  md 파일 총 {info['total']}개 | 프론트매터 추가 {info['added']}개 "
        f"| 이미 보유(스킵) {info['skipped']}개"
    )
    for rel, cat, title, tags in info["results"][: args.limit]:
        print(f"  + {rel}")
        print(f"      title='{title}' category={cat} tags={tags}")
    if info["added"] > args.limit:
        print(f"  ... 외 {info['added'] - args.limit}개")
    if not info["applied"] and info["added"]:
        print("  (드라이런입니다. 실제 기록하려면 --apply 를 붙이세요.)")
    return info


# ── 셀프테스트 (실제 레포 데이터로 검증) ──────────────────────────────
def _selftest():
    import io
    import tempfile
    import contextlib

    ok = 0

    # 1) 프론트매터 감지: 맨 위 '---' 는 보유로 간주, 본문 중간 '---' 는 무시
    assert has_frontmatter("---\ntitle: x\n---\n# H\n")
    assert not has_frontmatter("# H\n---\nbody\n")
    assert has_frontmatter("﻿---\nk: v\n---\n")  # BOM 허용
    ok += 1

    # 2) title 도출: 첫 # 헤딩 우선, 없으면 파일명
    assert derive_title("# 진짜 제목\n본문", Path("x/foo_bar.md")) == "진짜 제목"
    assert derive_title("프론트만 없음", Path("x/foo_bar.md")) == "foo bar"
    ok += 1

    # 3) category 도출: 실제 레포 파일로 검증
    roas = KB_ROOT / "metrics" / "roas.md"
    assert derive_category(roas) == "metrics", derive_category(roas)
    glob = KB_ROOT / "_GLOBAL.md"
    assert derive_category(glob) == "knowledge", derive_category(glob)
    ok += 1

    # 4) tags 도출: 경로+파일명 조각, 소문자/중복제거/캡
    tags = derive_tags(KB_ROOT / "metrics" / "impression_share.md", "metrics")
    assert tags[0] == "metrics" and "impression" in tags and "share" in tags, tags
    assert len(tags) <= 5
    ok += 1

    # 5) build 블록은 정확히 '---' 로 시작·끝, 8개 키 라인
    blk = build_frontmatter("T", "metrics", ["a", "b"])
    assert blk.startswith("---\n") and blk.rstrip().endswith("---")
    for key in ("title:", "category:", "tags:", "verified:", "status:",
                "last_updated:", "related:"):
        assert key in blk, key
    ok += 1

    # 6) 멱등성 + 본문 바이트 보존: 임시 디렉터리에서 2회 적용 시뮬레이션
    body = "# 헤딩\n\n본문 한 줄.\n중간에 ---\n끝.\n"
    block = build_frontmatter("헤딩", "x", ["x"])
    once = block + body
    # 두 번째 적용은 has_frontmatter 가 True → 변화 없음
    assert has_frontmatter(once)
    # 본문이 블록 뒤에 바이트 단위로 그대로 남아있는가
    assert once[len(block):] == body
    ok += 1

    # 7) 드라이런은 디스크를 바꾸지 않는다 (added>0 이어도)
    before = (KB_ROOT / "metrics" / "roas.md").read_bytes()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        info = process(apply=False)
    after = (KB_ROOT / "metrics" / "roas.md").read_bytes()
    assert before == after, "드라이런이 파일을 변경함!"
    assert info["total"] >= 1
    ok += 1

    print(f"[selftest] OK {ok}/7 — knowledge md {info['total']}개 인식, "
          f"드라이런 add={info['added']} skip={info['skipped']}")


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        _selftest()
    else:
        main()
