"""
Auto-sync knowledge assets to git (used by the Claude Code Stop hook).
Commits & pushes ONLY when marketing/knowledge/* , marketing/history/* or FEEDBACK_LOG.md changed,
so routine sessions don't create noise. All errors are swallowed (never blocks the session).

  python tools/autosync.py
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCH = ("marketing/knowledge/", "marketing/history/", "FEEDBACK_LOG.md")

def sh(*args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")

def main():
    try:
        status = sh("git", "status", "--porcelain").stdout or ""
        changed = [ln[3:].strip() for ln in status.splitlines()
                   if any(w in ln for w in WATCH)]
        if not changed:
            return
        for p in WATCH:
            sh("git", "add", p)
        msg = f"auto: knowledge sync ({len(changed)} file(s))"
        c = sh("git", "commit", "-m", msg)
        if c.returncode == 0:
            sh("git", "push")
            print(f"[autosync] {msg}")
    except Exception:
        pass  # never block the session

if __name__ == "__main__":
    main()
