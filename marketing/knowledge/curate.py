"""
CURATE — 놀리지에셋 UPSERT/중복제거 + 계정 온보딩 (learn.py의 자매 헬퍼).

learn.py는 무조건 append 한다(같은 교훈이 또 들어오면 줄이 쌓임). 이 모듈은 그 옆에서:
  1) upsert_lesson — 같은 (정규화된) feedback 줄이 이미 있으면 날짜만 '재검증'으로 갱신,
     없으면 learn.py와 동일한 포맷으로 새 줄 추가. → 중복 누적 방지.
  2) onboard_account — knowledge/<account>.md 와 history/<account>-log.md 를 템플릿에서 생성
     (없을 때만). 비어있던 history/ 갭을 채운다.

외부 의존성 없음 — stdlib만. 타임존은 learn.py와 동일한 KST.

Usage:
  python curate.py --upsert marketing/knowledge/_GLOBAL.md --tag report --feedback '...'
  python curate.py --onboard demo --vertical ecommerce --baseline 'CTR 1.2%, ROAS 3.5x'
"""
import argparse
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]      # .../madobi
KNOWLEDGE = ROOT / "marketing" / "knowledge"
HISTORY = ROOT / "marketing" / "history"
KST = timezone(timedelta(hours=9))              # learn.py와 동일

# learn.py 줄 포맷: "- [<날짜/타임스탬프>] (tag) feedback"
# 날짜 안엔 ']' 가 없으므로 [^\]] 로 안전하게 떼어낸다.
_LINE_RE = re.compile(r"^- \[(?P<ts>[^\]]+)\] \((?P<tag>[^)]*)\) (?P<body>.*)$")


def _now():
    """(타임스탬프, 날짜) 튜플. learn.py와 같은 strftime 포맷."""
    n = datetime.now(KST)
    return n.strftime("%Y-%m-%d %H:%M KST"), n.strftime("%Y-%m-%d")


def normalize(text: str) -> str:
    """중복 판정용 정규화: 좌우공백 제거 + 내부 연속공백 1칸 + 소문자.
    표기 흔들림(공백/대소문자)은 같은 교훈으로 본다. 의미까지는 보지 않는다(KISS)."""
    return re.sub(r"\s+", " ", text.strip()).lower()


def upsert_lesson(target_md_path, tag: str, feedback: str) -> str:
    """feedback 줄을 UPSERT 한다.

    - 같은 정규화 body 를 가진 줄이 있으면 그 줄의 타임스탬프를 '재검증'으로 갱신(in place).
    - 없으면 learn.py와 동일 포맷 '- [<ts>] (tag) feedback' 한 줄을 끝에 추가.

    반환: "updated" | "appended" (호출측/CLI 표시용).
    """
    path = Path(target_md_path)
    if not path.is_absolute():
        path = ROOT / path
    ts, _date = _now()
    feedback = feedback.strip()
    key = normalize(feedback)

    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = text.split("\n")

    for i, line in enumerate(lines):
        m = _LINE_RE.match(line)
        if m and normalize(m.group("body")) == key:
            # 이미 있음 → 날짜만 갱신. 태그/본문은 보존(원래 교훈 그대로).
            lines[i] = f"- [{ts} 재검증] ({m.group('tag')}) {m.group('body')}"
            new_text = "\n".join(lines)
            path.write_text(new_text, encoding="utf-8", newline="\n")
            return "updated"

    # 신규 → append (learn.py 포맷, 파일 끝에 개행 보장)
    entry = f"- [{ts}] ({tag}) {feedback}\n"
    prev = text
    if prev and not prev.endswith("\n"):
        prev += "\n"
    path.write_text(prev + entry, encoding="utf-8", newline="\n")
    return "appended"


_KNOWLEDGE_TPL = """# {account} — 계정 놀리지에셋
> vertical: {vertical} · 생성: {date} · 검산 통과분만 누적(중복은 curate.upsert로 갱신).

## 지표 기준선
- {baseline}
- (윈도우/타임존/통화/어트리뷰션 모델 기준을 함께 못박을 것)

## 통하는 앵글/후크
- (계정 데이터로 검증된 승자 앵글만 승격. 첫 3초 후크/오퍼/소구점)

## 금칙어
- (브랜드/법무상 쓰면 안 되는 표현·과장·비교광고 문구)

## 리포트 포맷 선호
- 숫자엔 단위·천단위 구분, 가정(윈도우/타임존/통화/필터) 머리에 명시.
- ROAS는 배수(x), 비율은 가중평균(Σ/Σ), 정합성 판정 1줄로 마무리.
"""

_LOG_TPL = """# {account} — 대화·분석 이력 (자동 누적)
> vertical: {vertical} · 생성: {date}

## {date}
- 요청: (온보딩 — 기준선 등록)
- 한 일: knowledge/{account}.md 생성, 기준선 '{baseline}' 기록
- 결정/추천: (다음 세션에 업데이트)
- 결과: (다음 세션에 업데이트)
"""


def onboard_account(account: str, vertical: str, baseline: str):
    """계정 온보딩: knowledge/<account>.md + history/<account>-log.md 생성(없을 때만).

    반환: 실제로 생성한 파일 경로 리스트(이미 있으면 건너뜀 → 빈 리스트 가능).
    """
    _ts, date = _now()
    KNOWLEDGE.mkdir(parents=True, exist_ok=True)
    HISTORY.mkdir(parents=True, exist_ok=True)

    kpath = KNOWLEDGE / f"{account}.md"
    lpath = HISTORY / f"{account}-log.md"
    created = []
    ctx = dict(account=account, vertical=vertical, baseline=baseline.strip(), date=date)

    if not kpath.exists():
        kpath.write_text(_KNOWLEDGE_TPL.format(**ctx), encoding="utf-8", newline="\n")
        created.append(kpath)
    if not lpath.exists():
        lpath.write_text(_LOG_TPL.format(**ctx), encoding="utf-8", newline="\n")
        created.append(lpath)
    return created


def _main():
    ap = argparse.ArgumentParser(description="놀리지에셋 UPSERT/중복제거 + 계정 온보딩")
    ap.add_argument("--upsert", metavar="FILE", help="이 .md 파일에 교훈을 upsert")
    ap.add_argument("--tag", default="general")
    ap.add_argument("--feedback")
    ap.add_argument("--onboard", metavar="ACCOUNT", help="계정 온보딩")
    ap.add_argument("--vertical", default="general")
    ap.add_argument("--baseline", default="(기준선 미정)")
    a = ap.parse_args()

    if a.onboard:
        created = onboard_account(a.onboard, a.vertical, a.baseline)
        if created:
            for p in created:
                print(f"created -> {p.relative_to(ROOT)}")
        else:
            print(f"exists  -> 이미 온보딩됨 ({a.onboard})")
    elif a.upsert:
        if not a.feedback:
            ap.error("--upsert 에는 --feedback 이 필요합니다")
        result = upsert_lesson(a.upsert, a.tag, a.feedback)
        path = Path(a.upsert)
        rel = path if path.is_absolute() else (ROOT / path)
        print(f"{result} -> {rel.relative_to(ROOT)}")
    else:
        ap.error("--upsert FILE 또는 --onboard ACCOUNT 중 하나가 필요합니다")


if __name__ == "__main__":
    _main()
