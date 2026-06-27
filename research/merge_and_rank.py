"""
Merge multiple workflow .output files, majority-vote per (design,pid), score vs ground truth,
and rank designs. Treats null/missing as 'not attempted' (so rate-limited cells don't unfairly
kill a design). Local-only: no API calls.

Usage: python merge_and_rank.py --pids P1,P4,P6,P11,P12,P14,P16,P17,P19,P20 <out1> <out2> ...
"""
import json, re, sys, argparse
from fractions import Fraction
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).parent
answers = json.loads((ROOT/"benchmark"/"answers.json").read_text(encoding="utf-8"))
problems = {p["id"]: p for p in json.loads((ROOT/"benchmark"/"problems.json").read_text(encoding="utf-8"))}

def gtnorm(pid):
    gt = answers[pid]
    if "/" in gt:
        m = re.search(r"(-?\d+)\s*/\s*(\d+)", gt); return str(Fraction(int(m.group(1)), int(m.group(2))))
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
        m2 = re.search(r"-?\d+", s.replace(",", ""))
        if m2: return str(Fraction(int(m2.group()), 1))
        return s
    if re.fullmatch(r"-?\d+", gt):
        m = re.search(r"-?\d[\d,]*", s); return m.group().replace(",", "") if m else s
    return s.lower()

def load_rows(path):
    raw = Path(path).read_text(encoding="utf-8")
    try: obj = json.loads(raw)
    except Exception:
        i, j = raw.find("["), raw.rfind("]"); obj = json.loads(raw[i:j+1])
    if isinstance(obj, dict) and "result" in obj: return obj["result"]
    return obj

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pids", default="all")
    ap.add_argument("--save", default=None)
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    pids = list(problems) if a.pids == "all" else a.pids.split(",")

    # design -> pid -> list of raw answers
    data = defaultdict(lambda: defaultdict(list))
    allrows = []
    for f in a.files:
        for r in load_rows(f):
            data[r["design"]][r["pid"]].append(r.get("answer"))
            allrows.append(r)
    if a.save:
        Path(a.save).write_text(json.dumps(allrows, ensure_ascii=False), encoding="utf-8")

    rank = []
    for d, pm in data.items():
        correct = attempted = 0
        miss = []
        for pid in pids:
            raws = [x for x in pm.get(pid, []) if x is not None]
            if not raws:
                miss.append(pid); continue
            attempted += 1
            modal = Counter(norm(pid, x) for x in raws).most_common(1)[0][0]
            if modal == gtnorm(pid): correct += 1
        acc = correct / attempted if attempted else 0
        rank.append((d, correct, attempted, len(pids), acc, miss))

    # sort: accuracy desc, attempted desc, correct desc
    rank.sort(key=lambda x: (-x[4], -x[2], -x[1]))
    print(f"\n=== RANKING ({len(rank)} designs, target {len(pids)} problems) ===")
    print("rank design".ljust(42), "correct/attempt  acc    missing")
    for i, (d, c, at, tot, acc, miss) in enumerate(rank, 1):
        ms = "" if not miss else "  miss:" + ",".join(miss)
        print(f"{i:>3} {d:<38} {c:>2}/{at:<2}={acc:5.2f}{ms}")
    # perfect designs with full coverage
    perfect = [r for r in rank if r[4] == 1.0 and not r[5]]
    print(f"\nperfect & full-coverage ({len(perfect)}): " + ", ".join(r[0] for r in perfect))
    return rank

if __name__ == "__main__":
    main()
