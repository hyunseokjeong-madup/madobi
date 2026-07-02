"""
SELF-IMPROVEMENT LOOP — capture user feedback -> promote to a knowledge asset
-> log it -> (optionally) commit & push to git.

The agent calls this whenever the user says "improve X" / "you should always Y" / corrects it.
Central/global lessons go to the shared assets and get pushed to the repo; account-specific
lessons stay in that account's file.

Usage:
  python learn.py --feedback "ROAS는 항상 배수(x)로 표기" --scope global --tag report
  python learn.py --feedback "A계정은 18-24 세그먼트가 핵심" --scope account --account acmecorp
  python learn.py --feedback "..." --scope global --no-commit   # 커밋/푸시 생략(기본은 자동 커밋+푸시)
"""
import argparse, subprocess, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
KST = timezone(timedelta(hours=9))


def _curate():
    """marketing/knowledge/curate.py 를 방어적으로 import (recall.py와 같은 sys.path 패턴).

    있으면 upsert_lesson(중복은 재검증으로 갱신)을 쓰고, 없으면 None → append 폴백.
    """
    kdir = ROOT / "marketing" / "knowledge"
    try:
        if str(kdir) not in sys.path:
            sys.path.insert(0, str(kdir))
        import curate  # type: ignore
        return curate
    except Exception:
        return None


def append(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    prev = path.read_text(encoding="utf-8") if path.exists() else ""
    # 기존 내용이 개행으로 안 끝나면(외부 수동편집 등) 새 항목이 같은 줄에 붙어 md 가 깨진다
    # → curate.py 와 동일하게 선행 개행 보존.
    if prev and not prev.endswith("\n"):
        prev += "\n"
    path.write_text(prev + text, encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feedback", required=True)
    ap.add_argument("--scope", choices=["global", "account"], default="global")
    ap.add_argument("--account", default=None)
    ap.add_argument("--tag", default="general")
    ap.add_argument("--no-commit", dest="commit", action="store_false",
                    help="skip git add/commit/push (auto-commit+push is ON by default)")
    ap.set_defaults(commit=True)
    a = ap.parse_args()
    if not a.feedback.strip():
        ap.error("feedback 은 비거나 공백만일 수 없습니다(빈 stub 가 지식 자산을 오염).")
    ts = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    date = datetime.now(KST).strftime("%Y-%m-%d")

    entry = f"- [{date}] ({a.tag}) {a.feedback.strip()}\n"

    # 1) promote into the right knowledge asset.
    #    놀리지에셋은 curate.upsert 로 중복 누적을 막는다(같은 교훈 재출현 → '재검증'으로
    #    타임스탬프만 갱신). '검산 통과분만 누적' 원칙 강화. curate 없으면 append 폴백.
    curate = _curate()
    if a.scope == "global":
        target = ROOT / "marketing" / "knowledge" / "_GLOBAL.md"
    else:
        acct = a.account or "unknown"
        target = ROOT / "marketing" / "knowledge" / f"{acct}.md"
        if not target.exists():
            append(target, f"# {acct} — 계정 놀리지에셋\n\n")

    if curate is not None:
        result = curate.upsert_lesson(target, a.tag, a.feedback)   # "updated" | "appended"
    else:
        append(target, entry)
        result = "appended"

    # 2) central feedback log — 감사로그라 append-only(모든 발생을 시간순 보존, dedup 금지).
    log = ROOT / "FEEDBACK_LOG.md"
    if not log.exists():
        append(log, "# Feedback Log — 사용자 개선요청 → 학습 이력\n\n")
    append(log, f"- [{ts}] scope={a.scope}{('/' + a.account) if a.account else ''} tag={a.tag}: {a.feedback.strip()}\n")

    print(f"learned -> {target.relative_to(ROOT)} ({result})")
    print(f"logged  -> FEEDBACK_LOG.md")

    # 3) optional: commit & push (central update).
    #    returncode 를 실제로 검사한다 — 예전엔 push 실패도 마지막 출력줄을 'ok'처럼
    #    찍어서 조용히 실패했다. 단 실패해도 학습 자체는 이미 디스크에 반영됐으므로
    #    프로세스를 죽이지 않고(autosync 'never block' 철학) 명확히 경고만 한다.
    if a.commit:
        msg = f"learn({a.scope}{('/' + a.account) if a.account else ''}): {a.feedback.strip()[:60]}"
        # add 는 learn 이 실제로 만진 두 파일만 — 과거 -A 는 작업트리의 무관한 진행 중
        # 변경까지 'learn(...)' 커밋에 쓸어 담아 push 했다. '--' 는 경로 오해석 차단.
        for cmd in (["git", "add", "--", str(target.relative_to(ROOT)), "FEEDBACK_LOG.md"],
                    ["git", "commit", "-m", msg],
                    ["git", "push"]):
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
            out = (r.stdout or r.stderr).strip()
            last = out.splitlines()[-1] if out else ""
            if r.returncode == 0:
                print("$", " ".join(cmd), "->", last or "ok")
            else:
                # commit 이 'nothing to commit' 으로 비0이 나는 건 정상(변경 없음).
                if cmd[1] == "commit" and "nothing to commit" in out.lower():
                    print("$", " ".join(cmd), "-> (변경 없음, 건너뜀)")
                    continue
                print("$", " ".join(cmd), f"-> ⚠️ FAILED (rc={r.returncode}):", last or "(출력 없음)")
                break  # 이후 단계(예: push) 진행 무의미 — 학습은 이미 디스크에 반영됨

if __name__ == "__main__":
    main()
