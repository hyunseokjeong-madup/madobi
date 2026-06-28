"""
frontmatter 보존 헬퍼 — build_kb*.py 가 본문을 재생성해도 기존 YAML frontmatter 를 지키게 한다.

배경: build_kb*.py 는 본문(`# title` + 불릿)을 실제 knowledge md 에 덮어쓴다. 그런데 add_frontmatter.py
가 입힌 YAML frontmatter(옵시디언 메타데이터)를 함께 날려버렸다(tests/run_all.py 가 매번 빌더를 호출하므로
frontmatter 가 213↔7 로 플래핑). 이 헬퍼는 덮어쓰기 전에 기존 frontmatter 를 떼어 새 본문 앞에 다시 붙인다.

순수 stdlib. build_kb*.py 의 write_text(path, body) 호출을 write_md(path, body) 로 바꿔 쓴다.
"""
from pathlib import Path


def extract_frontmatter(path: Path) -> str:
    """대상 파일이 존재하고 '---' 로 시작하면 frontmatter 블록(닫는 '---' 포함, 끝 개행 포함)을 반환. 없으면 ''."""
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    # 첫 '---' 다음의 닫는 '---' 를 찾는다.
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    fm_inner = parts[1]  # 두 '---' 사이
    return "---" + fm_inner + "---\n"


def write_md(path: Path, body: str):
    """본문을 쓰되, 대상 파일에 기존 frontmatter 가 있으면 그 블록을 본문 앞에 보존한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = extract_frontmatter(path)
    if fm:
        # 본문이 frontmatter 로 시작하지 않을 때만 보존 블록을 앞에 붙인다(이중 방지).
        body_no_lead = body.lstrip("\n")
        if not body_no_lead.startswith("---"):
            body = fm + body_no_lead
    path.write_text(body, encoding="utf-8", newline="\n")
