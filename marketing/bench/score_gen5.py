"""Score the Gen5 marketing-reasoning run (numeric, majority-vote). Usage: python score_gen5.py <output.json>"""
import json, re, sys
from pathlib import Path
from collections import defaultdict, Counter

HERE = Path(__file__).parent
ans = json.loads((HERE / "reasoning" / "answers.json").read_text(encoding="utf-8"))

def num(s):
    if s is None: return None
    s = str(s).replace(",", "").replace("원","").replace("%","").replace("x","").replace("배","").strip()
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None

def load(p):
    raw = Path(p).read_text(encoding="utf-8")
    obj = json.loads(raw)
    return obj["result"] if isinstance(obj, dict) and "result" in obj else obj

def main(path):
    rows = load(path)
    cells = defaultdict(lambda: defaultdict(list))
    for r in rows:
        cells[r["design"]][r["pid"]].append(r.get("answer"))
    pids = list(ans)
    print(f"\n=== GEN5 MARKETING REASONING ({path}) ===")
    print("design".ljust(20) + "".join(p.ljust(6) for p in pids) + " TOTAL")
    for d in sorted(cells):
        line = d.ljust(20); c = 0
        for pid in pids:
            vals = [num(x) for x in cells[d][pid] if x is not None]
            gt = num(ans[pid])
            ok = False
            if vals:
                modal = Counter(vals).most_common(1)[0][0]
                ok = abs(modal - gt) <= 1e-3 * max(1, abs(gt))
            c += ok
            line += ("  O   " if ok else "  X   ")
        line += f"  {c}/{len(pids)}"
        print(line)

if __name__ == "__main__":
    main(sys.argv[1])
