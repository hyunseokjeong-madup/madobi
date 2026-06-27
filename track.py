"""
Generation tracker. Scores every results/gen*.json and prints a fitness-over-generations
table plus per-design trajectory. Confirms elite-monotonicity for the Planner.
"""
import json, re, glob
from pathlib import Path
from fractions import Fraction
from collections import defaultdict

ROOT = Path(__file__).parent
answers = json.loads((ROOT/"benchmark"/"answers.json").read_text(encoding="utf-8"))

def gtnorm(pid):
    gt = answers[pid]
    if "/" in gt:
        m = re.search(r"(-?\d+)\s*/\s*(\d+)", gt)
        return str(Fraction(int(m.group(1)), int(m.group(2))))
    return gt.lower() if not re.fullmatch(r"-?\d+", gt) else gt

def norm(pid, raw):
    if raw is None: return None
    s = str(raw).strip()
    m = re.search(r"answer\s*[:=]\s*(.+)$", s, re.I)
    if m: s = m.group(1).strip()
    s = s.strip().strip(".").strip()
    gt = answers[pid]
    if "/" in gt:
        m = re.search(r"(-?\d+)\s*/\s*(\d+)", s)
        if m:
            try: return str(Fraction(int(m.group(1)), int(m.group(2))))
            except ZeroDivisionError: return s
        m3 = re.search(r"-?\d+\.\d+", s)
        if m3:
            try: return str(Fraction(m3.group()).limit_denominator(10**6))
            except Exception: pass
        m2 = re.search(r"-?\d+", s.replace(",",""))
        if m2: return str(Fraction(int(m2.group()),1))
        return s
    if re.fullmatch(r"-?\d+", gt):
        m = re.search(r"-?\d[\d,]*", s)
        return m.group().replace(",","") if m else s
    return s.lower()

def score_file(path):
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    from collections import Counter
    bd = defaultdict(lambda: defaultdict(list))
    for r in rows: bd[r["design"]][r["pid"]].append(r.get("answer"))
    def pick(pid, lst):
        ns = [norm(pid, a) for a in lst if a is not None]
        return Counter(ns).most_common(1)[0][0] if ns else None
    out = {}
    for d, ans in bd.items():
        out[d] = sum(pick(p, ans.get(p, [])) == gtnorm(p) for p in answers)
    return out

def main():
    files = sorted(glob.glob(str(ROOT/"results"/"gen*.json")),
                   key=lambda p: int(re.search(r"gen(\d+)", p).group(1)))
    if not files:
        print("no generation results yet"); return
    print("\n=== Fitness over generations (out of", len(answers), ") ===")
    all_designs = []
    gen_scores = []
    for f in files:
        sc = score_file(f)
        gen_scores.append((Path(f).stem, sc))
        for d in sc:
            if d not in all_designs: all_designs.append(d)
    header = "design".ljust(18) + "".join(g.ljust(8) for g,_ in gen_scores)
    print(header)
    for d in all_designs:
        line = d.ljust(18)
        for _, sc in gen_scores:
            line += (str(sc[d]) if d in sc else "-").ljust(8)
        print(line)
    print("\n-- best (elite) per generation --")
    elite = -1
    for g, sc in gen_scores:
        b = max(sc.values()); bd = max(sc, key=sc.get)
        flag = "" if b >= elite else "  <-- REGRESSION!"
        elite = max(elite, b)
        print(f"  {g}: best={b}/{len(answers)} ({bd}){flag}")

if __name__ == "__main__":
    main()
