"""
SessionStart 브리핑 — 세션 시작 시 하네스 상태를 한 줄로 (결정론·무네트워크·<1s).

Claude Code 가 이 리포에서 열릴 때 훅(.claude/settings.json SessionStart)이 실행한다.
에이전트/사용자가 "지금 하네스가 어떤 상태인가"를 매번 다시 조사하지 않게 하는 것이 목적.

  python tools/session_brief.py            # 브리핑 한 줄 출력
  python tools/session_brief.py --selftest
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def counts():
    pm = len([f for f in (ROOT / "marketing" / "pm").glob("*.py")
              if not f.stem.startswith("_") and f.stem != "tools_index"])
    knowledge = len(list((ROOT / "marketing" / "knowledge").rglob("*.md")))
    checks = len(re.findall(r'^\s*\("', (ROOT / "tests" / "run_all.py").read_text(encoding="utf-8"), re.M))
    fb = ROOT / "FEEDBACK_LOG.md"
    lessons = len(re.findall(r"^- \[", fb.read_text(encoding="utf-8"), re.M)) if fb.exists() else 0
    return {"pm": pm, "knowledge": knowledge, "checks": checks, "lessons": lessons}


def brief():
    c = counts()
    return (f"🧭 MADOBI 하네스: pm도구 {c['pm']} · 놀리지 {c['knowledge']} · "
            f"게이트 {c['checks']}체크(python tests/run_all.py) · 누적 교훈 {c['lessons']} · "
            f"챗봇: python marketing/madobi.py chat")


def _selftest():
    c = counts()
    assert c["pm"] >= 78, c
    assert c["knowledge"] >= 200, c
    assert c["checks"] >= 100, c
    line = brief()
    assert line.startswith("🧭") and "체크" in line, line
    assert brief() == brief()  # 결정론
    print(f"session-brief self-test: PASS  ({c})")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print(brief())
