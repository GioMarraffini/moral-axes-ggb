"""Expected rating of every evaluation statement under every cell, from option probabilities."""
import argparse
import json

import numpy as np

from moral_axes import cells as C
from moral_axes import data
from moral_axes.model import load, option_probs, steer

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
ap.add_argument("--directions", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--layers", default=",".join(map(str, C.LAYERS)))
ap.add_argument("--shard", default="0/1")
ap.add_argument("--cells", default="sweep", help="sweep, round2, round3, or a path to a JSON list of cells")
ap.add_argument("--dtype", default="fp16")
ap.add_argument("--limit", type=int, default=None)
ap.add_argument("--bs", type=int, default=32)
args = ap.parse_args()

model, tok = load(args.model, args.dtype)
Z = np.load(args.directions)
rows = data.statements("test")[:args.limit]
instr = data.instructions()
i, n = (int(x) for x in args.shard.split("/"))
jobs = {"sweep": lambda: C.sweep_cells([int(x) for x in args.layers.split(",")]),
        "round2": C.round2_cells, "round3": C.round3_cells}.get(args.cells, lambda: C.file_cells(args.cells))()[i::n]
items = [(r, k) for r in rows for k in instr]
options = [data.OPTIONS[k][0] for _, k in items]
values = np.array([data.OPTIONS[k][1] for _, k in items], dtype=float)

with open(args.out, "w") as f:
    for ci, c in enumerate(jobs):
        prompts = [data.rate_prompt(C.system(c), instr[k], r["statement"]) for r, k in items]
        with steer(model, C.hooks(c, Z, model.device)):
            p = option_probs(model, tok, prompts, options, args.bs).numpy()
        mass = p.sum(1)
        rating = (p * values).sum(1) / mass
        for (r, k), m, x in zip(items, mass, rating):
            f.write(json.dumps({"cell": C.name(c), **c, "id": r["id"], "type": r["type"],
                                "source_set": r["source"], "instruction": k,
                                "rating": round(float(x), 4), "mass": round(float(m), 4)}) + "\n")
        f.flush()
        print(f"[{ci + 1}/{len(jobs)}] {C.name(c)}", flush=True)
