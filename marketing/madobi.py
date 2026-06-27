"""
MADOBI 통합 CLI 디스패처 (하네스) — 모든 퍼마 도구의 단일 진입점.
  python marketing/madobi.py list                 # 도구 목록(설명)
  python marketing/madobi.py <tool> [args...]      # 도구 실행 (예: reconcile, mmm, rfm ...)
도구는 marketing/pm/<tool>.py 와 marketing/<tool>.py 에서 탐색. 의존성 없음.
"""
import sys, subprocess, re, glob
from pathlib import Path
ROOT=Path(__file__).parent
SEARCH=[ROOT/"pm", ROOT]
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
    return None
def main():
    if len(sys.argv)<2 or sys.argv[1] in ("-h","--help","help"):
        print("usage: madobi.py list | <tool> [args...]"); return
    cmd=sys.argv[1]
    if cmd=="list":
        tools=[]
        for d in SEARCH:
            for f in glob.glob(str(d/"*.py")):
                nm=Path(f).stem
                if nm in ("madobi","__init__"): continue
                tools.append((nm,first_doc(f)))
        tools=sorted(set(tools))
        print(f"=== MADOBI 도구 {len(tools)}개 ===")
        for nm,doc in tools: print(f"  {nm.ljust(24)} {doc[:70]}")
        return
    p=find(cmd)
    if not p:
        print(f"도구 없음: {cmd}  (madobi.py list 로 확인)"); sys.exit(1)
    sys.exit(subprocess.run([sys.executable,str(p)]+sys.argv[2:]).returncode)
if __name__=="__main__": main()
