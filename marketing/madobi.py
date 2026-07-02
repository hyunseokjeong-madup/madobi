"""
MADOBI 통합 CLI 디스패처 (하네스) — 모든 퍼마 도구의 단일 진입점.
  python marketing/madobi.py list                 # 도구 목록(카테고리별 + 설명)
  python marketing/madobi.py list --json          # 기계가독 카탈로그 [{name,group,doc}]
  python marketing/madobi.py chat                 # 챗봇 REPL (자연어 → 도구 라우팅)
  python marketing/madobi.py <tool> [args...]      # 도구 실행 (예: reconcile, mmm, rfm ...)
탐색: marketing/pm/, marketing/ + EXTRA(summarize·recall·search·curate·learn — 하위폴더/루트의
핵심 도구를 단일 진입점으로 노출; 폴더 통째 추가는 내부 스크립트로 목록이 오염돼 채택 안 함).
오타면 유사 도구 제안. 의존성 없음.
"""
import sys, subprocess, re, glob, json, difflib
from pathlib import Path
ROOT=Path(__file__).parent
SEARCH=[ROOT/"pm", ROOT]
# 하위폴더/리포 루트의 핵심 도구 allowlist — bench/·knowledge/ 통째 스캔은
# build_kb*·gen_dataset 같은 내부 스크립트까지 노출해 도구 수 규약을 오염시킨다.
EXTRA={
    "summarize": ROOT/"bench"/"summarize.py",   # 집계 엔진
    "recall":    ROOT/"knowledge"/"recall.py",  # 놀리지 회상
    "search":    ROOT/"knowledge"/"search.py",  # 놀리지 검색(FTS5)
    "curate":    ROOT/"knowledge"/"curate.py",  # 교훈 upsert
    "learn":     ROOT.parent/"learn.py",        # 자기개선 루프 (기본 자동 커밋+푸시 주의)
}
def first_doc(p):
    s=Path(p).read_text(encoding="utf-8")
    m=re.search(r'^\s*"""(.*?)"""',s,re.S|re.M)
    if not m: return ""
    for ln in m.group(1).strip().splitlines():
        if ln.strip(): return ln.strip()
    return ""
def find(name):
    for d in SEARCH:
        p=d/f"{name}.py"
        if p.exists(): return p
    p=EXTRA.get(name)
    return p if p and p.exists() else None
def _catalog():
    """[(group, name, path)] — group: core(marketing/) | pm | extra."""
    out=[]
    for d in SEARCH:
        grp="pm" if d.name=="pm" else "core"
        for f in sorted(glob.glob(str(d/"*.py"))):
            nm=Path(f).stem
            # 언더스코어 헬퍼(_pmutil 등)는 CLI 도구가 아님 — tools_index.py 와 동일 규약
            if nm in ("madobi","__init__") or nm.startswith("_"): continue
            out.append((grp,nm,Path(f)))
    for nm,p in sorted(EXTRA.items()):
        if p.exists(): out.append(("extra",nm,p))
    return out
def all_names():
    return sorted({nm for _,nm,_ in _catalog()})
def main():
    if len(sys.argv)<2 or sys.argv[1] in ("-h","--help","help"):
        print("usage: madobi.py list [--json] | chat | <tool> [args...]"); return
    cmd=sys.argv[1]
    if cmd=="list":
        cat=_catalog()
        if "--json" in sys.argv[2:]:
            print(json.dumps([{"name":nm,"group":g,"doc":first_doc(p)} for g,nm,p in cat],
                             ensure_ascii=False))
            return
        print(f"=== MADOBI 도구 {len(cat)}개 ===")
        titles={"core":"-- 코어 (marketing/) --","pm":"-- 퍼포먼스 마케팅 (marketing/pm/) --",
                "extra":"-- 지식/집계/학습 (bench·knowledge·루트) --"}
        for grp in ("core","pm","extra"):
            print(titles[grp])
            for g,nm,p in cat:
                if g==grp: print(f"  {nm.ljust(24)} {first_doc(p)[:70]}")
        return
    p=find(cmd)
    if not p:
        near=difflib.get_close_matches(cmd, all_names(), n=3, cutoff=0.5)
        hint=f"  혹시: {', '.join(near)}?" if near else ""
        print(f"도구 없음: {cmd}  (madobi.py list 로 확인){hint}"); sys.exit(1)
    sys.exit(subprocess.run([sys.executable,str(p)]+sys.argv[2:]).returncode)
if __name__=="__main__": main()
