"""Directions from the model's own unprompted answers, split by the rating they received.

For each axis, among the chain-of-thought answers to that axis's train statements (unprompted,
or from the cells given; the activations are always taken from the unsteered model):
v = mean activation of answers judged 5..7 minus mean of answers judged 1..3, over the
response tokens, at every layer. "both" is the sum of the IB and IH vectors.
"""
import argparse
import glob
import json
from pathlib import Path

import numpy as np
import torch

from moral_axes import data
from moral_axes.model import load, response_means

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
ap.add_argument("--responses", nargs="+", required=True)
ap.add_argument("--judge", nargs="+", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--dtype", default="fp16")
ap.add_argument("--drop", default="inverted_agreement_likert_scale,inverted_numbers_likert_scale")
ap.add_argument("--cells", default="base", help="cells whose answers enter the contrast, comma separated")
ap.add_argument("--limit", type=int, default=None)
args = ap.parse_args()

out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
v = {}
for d in args.judge:
    for f in glob.glob(d + "/judge_*.json") + glob.glob(d + "/verdict_*.json"):
        v.update(json.load(open(f)))
gen = [json.loads(l) for g in args.responses for f in sorted(glob.glob(g)) for l in open(f)]
gen = [r for r in gen if r["cell"] in args.cells.split(",") and r["split"] == "train"
       and r["instruction"] not in args.drop.split(",") and v.get(r["uid"], 0) > 0]
instr = data.instructions()
model, tok = load(args.model, args.dtype)
Z, geom = {}, {}
for axis in ("IB", "IH"):
    rows = [r for r in gen if r["type"] == axis][:args.limit]
    prompts = [data.cot_prompt(data.system(None), instr[r["instruction"]], r["statement"]) for r in rows]
    acts = response_means(model, tok, prompts, [r["response"] for r in rows])
    rating = torch.tensor([v[r["uid"]] for r in rows])
    hi, lo = acts[rating >= 5], acts[rating <= 3]
    Z[f"{axis}acc|v"] = hi.mean(0) - lo.mean(0)
    Z[f"{axis}acc|mu"] = acts.mean(0)
    geom[axis] = {"n_high": int(len(hi)), "n_low": int(len(lo)), "n": int(len(rows))}
    print(axis, geom[axis], flush=True)
Z["both|v"] = Z["IBacc|v"] + Z["IHacc|v"]
Z["both|mu"] = (Z["IBacc|mu"] + Z["IHacc|mu"]) / 2
cos = lambda a, b: torch.nn.functional.cosine_similarity(a, b, dim=-1).tolist()
geom["cos IBacc,IHacc"] = cos(Z["IBacc|v"], Z["IHacc|v"])
for k in ("IBacc", "IHacc", "both"):
    geom[f"norm {k}"] = Z[f"{k}|v"].norm(dim=-1).tolist()
np.savez(out / "directions.npz", **{k: x.numpy().astype(np.float32) for k, x in Z.items()})
json.dump(geom, open(out / "geometry.json", "w"), indent=1)
print("done", flush=True)
