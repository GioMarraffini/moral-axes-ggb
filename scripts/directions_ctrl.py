"""Accepting-minus-rejecting directions for the control sets, from judged control answers.

The activations are taken from the unsteered model over each answer's text, so a direction
describes the content of answers that accept a control statement against those that reject it.
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
ap.add_argument("--merge", default=None, help="npz whose keys are copied into the output")
ap.add_argument("--out", required=True)
ap.add_argument("--dtype", default="fp16")
ap.add_argument("--types", default="harm_no_benefit,kindness,neutral")
ap.add_argument("--drop", default="inverted_agreement_likert_scale,inverted_numbers_likert_scale")
ap.add_argument("--max_per_side", type=int, default=600)
args = ap.parse_args()

out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
v = {}
for d in args.judge:
    for f in glob.glob(d + "/*.json"):
        v.update(json.load(open(f)))
gen = [json.loads(l) for g in args.responses for f in sorted(glob.glob(g)) for l in open(f)]
gen = [r for r in gen if r["instruction"] not in args.drop.split(",") and v.get(r["uid"], 0) > 0]
instr = data.instructions()
model, tok = load(args.model, args.dtype)
Z = dict(np.load(args.merge)) if args.merge else {}
geom = {}
rng = np.random.default_rng(0)
for t in args.types.split(","):
    rows = [r for r in gen if r["type"] == t]
    hi = [r for r in rows if v[r["uid"]] >= 5]
    lo = [r for r in rows if v[r["uid"]] <= 3]
    hi = [hi[i] for i in rng.permutation(len(hi))[:args.max_per_side]]
    lo = [lo[i] for i in rng.permutation(len(lo))[:args.max_per_side]]
    acts = {}
    for name, rs in (("hi", hi), ("lo", lo)):
        prompts = [data.cot_prompt(data.system(None), instr[r["instruction"]], r["statement"]) for r in rs]
        acts[name] = response_means(model, tok, prompts, [r["response"] for r in rs])
    key = {"harm_no_benefit": "harmacc", "kindness": "kindacc", "neutral": "neutralacc"}[t]
    Z[f"{key}|v"] = (acts["hi"].mean(0) - acts["lo"].mean(0)).numpy().astype(np.float32)
    Z[f"{key}|mu"] = torch.cat([acts["hi"], acts["lo"]]).mean(0).numpy().astype(np.float32)
    geom[key] = {"n_high": len(hi), "n_low": len(lo)}
    print(t, geom[key], flush=True)
keys = [k[:-2] for k in Z if k.endswith("|v")]
cos = lambda a, b: float(np.sum(a * b, -1) / np.linalg.norm(a) / np.linalg.norm(b))
for L in (17, 20, 23, 26):
    geom[f"cos L{L}"] = {f"{x},{y}": round(cos(Z[f"{x}|v"][L], Z[f"{y}|v"][L]), 3)
                         for i, x in enumerate(keys) for y in keys[i + 1:]}
np.savez(out / "directions.npz", **Z)
json.dump(geom, open(out / "geometry.json", "w"), indent=1)
print("done", flush=True)
