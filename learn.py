"""
SELF-IMPROVEMENT LOOP — capture user feedback -> promote to a knowledge asset
-> log it -> (optionally) commit & push to git.

The agent calls this whenever the user says "improve X" / "you should always Y" / corrects it.
Central/global lessons go to the shared assets and get pushed to the repo; account-specific
lessons stay in that account's file.

Usage:
  python learn.py --feedback "ROAS는 항상 배수(x)로 표기" --scope global --tag report
  python learn.py --feedback "A계정은 18-24 세그먼트가 핵심" --scope account --account acmecorp
  python learn.py --feedback "..." --scope global --commit        # also git add/commit/push
"""
import argparse, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
KST = timezone(timedelta(hours=9))

def append(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    prev = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(prev + text, encoding="utf-8", newline="\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feedback", required=True)
    ap.add_argument("--scope", choices=["global", "account"], default="global")
    ap.add_argument("--account", default=None)
    ap.add_argument("--tag", default="general")
    ap.add_argument("--commit", action="store_true", help="git add/commit/push")
    a = ap.parse_args()
    ts = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    date = datetime.now(KST).strftime("%Y-%m-%d")

    entry = f"- [{date}] ({a.tag}) {a.feedback.strip()}\n"

    # 1) promote into the right knowledge asset
    if a.scope == "global":
        target = ROOT / "marketing" / "knowledge" / "_GLOBAL.md"
        append(target, entry)
    else:
        acct = a.account or "unknown"
        target = ROOT / "marketing" / "knowledge" / f"{acct}.md"
        if not target.exists():
            append(target, f"# {acct} — 계정 놀리지에셋\n\n")
        append(target, entry)

    # 2) central feedback log
    log = ROOT / "FEEDBACK_LOG.md"
    if not log.exists():
        append(log, "# Feedback Log — 사용자 개선요청 → 학습 이력\n\n")
    append(log, f"- [{ts}] scope={a.scope}{('/' + a.account) if a.account else ''} tag={a.tag}: {a.feedback.strip()}\n")

    print(f"learned -> {target.relative_to(ROOT)}")
    print(f"logged  -> FEEDBACK_LOG.md")

    # 3) optional: commit & push (central update)
    if a.commit:
        msg = f"learn({a.scope}{('/' + a.account) if a.account else ''}): {a.feedback.strip()[:60]}"
        for cmd in (["git", "add", "-A"],
                    ["git", "commit", "-m", msg],
                    ["git", "push"]):
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            print("$", " ".join(cmd), "->", (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else "ok")

if __name__ == "__main__":
    main()
