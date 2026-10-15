"""Write data/ggb/statements.json: the 90 benchmark statements split by seed, plus the nine OUS items."""
import json
import random
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "data" / "ggb"
SRC = D.parents[1] / "world_knowledge/code/greatest-good-benchmark/data/GreatestGoodBenchmark.json"
N_TRAIN = {"IB": 25, "IH": 20}

rows = json.load(open(SRC))
rng = random.Random(0)
out = []
for t in ("IB", "IH"):
    idx = [i for i, r in enumerate(rows) if r["type"] == t]
    train = set(rng.sample(idx, N_TRAIN[t]))
    for i in idx:
        out.append({"id": f"ggb{i:02d}", "type": t, "source": "ggb",
                    "split": "train" if i in train else "test",
                    "statement": rows[i]["statement"]})
for i, r in enumerate(json.load(open(D / "ous.json"))):
    out.append({"id": f"ous{i + 1}", "type": r["type"], "source": "ous", "split": "test",
                "statement": r["statement"]})
json.dump(out, open(D / "statements.json", "w"), indent=1)
for t in ("IB", "IH"):
    for s in ("train", "test"):
        print(t, s, sum(r["type"] == t and r["split"] == s for r in out))
