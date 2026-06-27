"""
Deterministic scorer. Reads a results file: JSON list of {design, pid, answer}.
Compares against benchmark/answers.json with format normalization.
Usage: python score.py results/round1.json
"""
import json, sys, re
from fractions import Fraction
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent
answers = json.loads((ROOT/"benchmark"/"answers.json").read_text(encoding="utf-8"))
problems = {p["id"]: p for p in json.loads((ROOT/"benchmark"/"problems.json").read_text(encoding="utf-8"))}

def norm(pid, raw):
    """Normalize an answer string to a canonical comparable token."""
    if raw is None: return None
    s = str(raw).strip()
    # pull a trailing "ANSWER: x" if present
    m = re.search(r"answer\s*[:=]\s*(.+)$", s, re.I)
    if m: s = m.group(1).strip()
    s = s.strip().strip(".").strip()
    gt = answers[pid]
    # fraction-type ground truth
    if "/" in gt:
        m = re.search(r"(-?\d+)\s*/\s*(\d+)", s)
        if m:
            try: return str(Fraction(int(m.group(1)), int(m.group(2))))
            except ZeroDivisionError: return s
        # decimal value -> fraction (accept correct value even if format is decimal)
        m3 = re.search(r"-?\d+\.\d+", s)
        if m3:
            try: return str(Fraction(m3.group()).limit_denominator(10**6))
            except Exception: pass
        m2 = re.search(r"-?\d+", s.replace(",",""))
        if m2: return str(Fraction(int(m2.group()), 1))
        return s
    # integer-type ground truth
    if re.fullmatch(r"-?\d+", gt):
        m = re.search(r"-?\d[\d,]*", s)
        if m: return m.group().replace(",", "")
        return s
    # word ground truth
    return s.lower()

def gtnorm(pid):
    gt = answers[pid]
    if "/" in gt:
        m = re.search(r"(-?\d+)\s*/\s*(\d+)", gt)
        return str(Fraction(int(m.group(1)), int(m.group(2))))
    return gt.lower() if not re.fullmatch(r"-?\d+", gt) else gt

def main(path):
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    from collections import Counter
    by_design = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_design[r["design"]][r["pid"]].append(r.get("answer"))
    def pick(pid, lst):
        ns = [norm(pid, a) for a in lst if a is not None]
        return Counter(ns).most_common(1)[0][0] if ns else None
    designs = sorted(by_design)
    pids = [p for p in problems]
    # per-problem correctness
    print(f"\n=== {Path(path).name} ===")
    header = "design".ljust(16) + "".join(p.ljust(6) for p in pids) + " TOTAL"
    print(header)
    score_tot = {}
    detail = {}
    for d in designs:
        line = d.ljust(16)
        c = 0
        detail[d] = {}
        for pid in pids:
            got = pick(pid, by_design[d].get(pid, []))
            ok = (got == gtnorm(pid))
            detail[d][pid] = ok
            c += ok
            line += ("  O   " if ok else "  X   ")
        line += f"  {c}/{len(pids)}"
        score_tot[d] = c
        print(line)
    # per-group breakdown
    print("\n-- per-group accuracy --")
    groups = sorted(set(problems[p]["group"] for p in pids))
    gp = {g:[p for p in pids if problems[p]["group"]==g] for g in groups}
    gh = "design".ljust(16) + "".join(g[:10].ljust(12) for g in groups)
    print(gh)
    for d in designs:
        line = d.ljust(16)
        for g in groups:
            ps = gp[g]
            c = sum(detail[d][p] for p in ps)
            line += f"{c}/{len(ps)}".ljust(12)
        print(line)
    # which problems nobody got
    print("\n-- hardest problems (fewest designs correct) --")
    for pid in pids:
        n = sum(detail[d][pid] for d in designs)
        if n < len(designs):
            print(f"  {pid} ({problems[pid]['group']}): {n}/{len(designs)} correct  gt={answers[pid]}")
    return score_tot

if __name__ == "__main__":
    main(sys.argv[1])
