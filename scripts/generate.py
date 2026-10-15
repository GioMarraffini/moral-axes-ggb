"""Chain-of-thought answers under chosen cells, generated until the model stops."""
import argparse
import json

import numpy as np

from moral_axes import cells as C
from moral_axes import data
from moral_axes.model import generate, load, steer

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
ap.add_argument("--directions", default=None)
ap.add_argument("--split", default="test", choices=["train", "test", "all"])
ap.add_argument("--bs", type=int, default=16)
ap.add_argument("--types", default="IB,IH", help="statement types to include, comma separated")
ap.add_argument("--cells", required=True, help="JSON list of cells")
ap.add_argument("--out", required=True)
ap.add_argument("--instructions", default=",".join(data.OPTIONS))
ap.add_argument("--iterations", type=int, default=10)
ap.add_argument("--temperature", type=float, default=0.5)
ap.add_argument("--max_new_tokens", type=int, default=2000)
ap.add_argument("--shard", default="0/1")
ap.add_argument("--dtype", default="fp16")
ap.add_argument("--limit", type=int, default=None)
args = ap.parse_args()

model, tok = load(args.model, args.dtype)
Z = np.load(args.directions) if args.directions else None
rows = [r for r in data.statements(None if args.split == "all" else args.split)
        if r["type"] in args.types.split(",")][:args.limit]
instr = data.instructions()
names = args.instructions.split(",")
i, n = (int(x) for x in args.shard.split("/"))
jobs = json.load(open(args.cells))
items = [(r, k, it) for r in rows for k in names for it in range(args.iterations)][i::n]
with open(args.out, "w") as f:
    for ci, c in enumerate(jobs):
        prompts = [data.cot_prompt(C.system(c), instr[k], r["statement"]) for r, k, _ in items]
        with steer(model, C.hooks(c, Z, model.device)):
            resp = generate(model, tok, prompts, args.max_new_tokens, args.temperature,
                            args.bs, seed=1000 * ci + i)
        for j, ((r, k, it), t) in enumerate(zip(items, resp)):
            f.write(json.dumps({"cell": C.name(c), **c, "id": r["id"], "type": r["type"],
                                "source_set": r["source"], "instruction": k, "iteration": it,
                                "uid": f"{C.name(c)}|{args.types}|{i}|{j}", "split": r["split"], "statement": r["statement"], "response": t}) + "\n")
        f.flush()
        print(f"[{ci + 1}/{len(jobs)}] {C.name(c)}", flush=True)
