"""Extract the design-generation workflow result into results/pop.json."""
import json, re, sys
from pathlib import Path

src = Path(sys.argv[1]) if len(sys.argv) > 1 else None
ROOT = Path(__file__).parent
raw = src.read_text(encoding="utf-8")

# try direct parse, else extract outermost JSON array
def load(raw):
    try:
        obj = json.loads(raw)
    except Exception:
        i, j = raw.find("["), raw.rfind("]")
        obj = json.loads(raw[i:j+1])
    if isinstance(obj, dict) and "result" in obj:
        return obj["result"]
    return obj

data = load(raw)
# normalize to [{name, manual, strategy, family}]
pop = []
seen = set()
for d in data:
    nm = d.get("name") or (d.get("family", "F") + "_" + str(len(pop)))
    while nm in seen:
        nm += "x"
    seen.add(nm)
    man = (d.get("manual") or "").strip()
    if not man:
        continue
    pop.append({"name": nm, "manual": man,
                "strategy": d.get("strategy", ""), "family": d.get("family", "")})

(ROOT/"results"/"pop.json").write_text(json.dumps(pop, ensure_ascii=False, indent=1), encoding="utf-8")
from collections import Counter
fam = Counter(d["family"] for d in pop)
print(f"saved {len(pop)} designs -> results/pop.json")
for k in sorted(fam): print(f"  {k}: {fam[k]}")
