"""Token statistics at one layer for the affine hook, from the model's own rated answers.

For each axis: mean and per-dimension standard deviation of the layer-L state over the
response tokens of the accepting answers (rated 5..7) and of the rejecting answers (1..3),
and the pooled mean and spread over all rated answers of both axes. Written together with
the keys of the directions file, so one file serves generate.py.
"""
import argparse
import glob
import json
from pathlib import Path

import numpy as np
import torch

from moral_axes import data
from moral_axes.model import load, response_token_stats

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
ap.add_argument("--responses", nargs="+", required=True)
ap.add_argument("--judge", nargs="+", required=True)
ap.add_argument("--directions", required=True)
ap.add_argument("--layer", type=int, required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--dtype", default="bf16")
ap.add_argument("--bs", type=int, default=4)
ap.add_argument("--drop", default="inverted_agreement_likert_scale,inverted_numbers_likert_scale")
ap.add_argument("--limit", type=int, default=None)
args = ap.parse_args()

v = {}
for d in args.judge:
    for f in glob.glob(d + "/judge_*.json") + glob.glob(d + "/verdict_*.json"):
        v.update(json.load(open(f)))
gen = [json.loads(l) for g in args.responses for f in sorted(glob.glob(g)) for l in open(f)]
gen = [r for r in gen if r["cell"] == "base" and r["split"] == "train"
       and r["instruction"] not in args.drop.split(",") and v.get(r["uid"], 0) > 0]
instr = data.instructions()
model, tok = load(args.model, args.dtype)
L = args.layer
Z = dict(np.load(args.directions))
tot = {"cnt": 0.0, "s1": 0.0, "s2": 0.0}
geom = {}
for axis in ("IB", "IH"):
    rows = [r for r in gen if r["type"] == axis][:args.limit]
    prompts = [data.cot_prompt(data.system(None, args.model), instr[r["instruction"]], r["statement"], tok) for r in rows]
    cnt, s1, s2 = response_token_stats(model, tok, prompts, [r["response"] for r in rows], L, args.bs)
    rating = torch.tensor([v[r["uid"]] for r in rows])
    for grp, sel in (("acc", rating >= 5), ("rej", rating <= 3)):
        n, a, b = cnt[sel].sum(), s1[sel].sum(0), s2[sel].sum(0)
        mu = a / n
        sd = torch.sqrt(torch.clamp(b / n - mu ** 2, min=1e-6))
        Z[f"{axis}aff|L{L}|mu_{grp}"] = mu.float().numpy()
        Z[f"{axis}aff|L{L}|sd_{grp}"] = sd.float().numpy()
        geom[f"{axis} {grp}"] = {"answers": int(sel.sum()), "tokens": int(n)}
    tot["cnt"] += float(cnt.sum())
    tot["s1"] = tot["s1"] + s1.sum(0)
    tot["s2"] = tot["s2"] + s2.sum(0)
    print(axis, {k: g for k, g in geom.items() if k.startswith(axis)}, flush=True)
mu_p = tot["s1"] / tot["cnt"]
sd_p = torch.sqrt(torch.clamp(tot["s2"] / tot["cnt"] - mu_p ** 2, min=1e-6))
Z[f"aff|L{L}|mu_p"] = mu_p.float().numpy()
Z[f"aff|L{L}|sd_p"] = sd_p.float().numpy()
geom["pooled tokens"] = int(tot["cnt"])
for axis in ("IB", "IH"):
    for grp in ("acc", "rej"):
        k = f"{axis}aff|L{L}"
        geom[f"{axis} {grp} |mu - mu_p|"] = float(np.linalg.norm(Z[f"{k}|mu_{grp}"] - Z[f"aff|L{L}|mu_p"]))
        geom[f"{axis} {grp} sd ratio median"] = float(np.median(Z[f"{k}|sd_{grp}"] / Z[f"aff|L{L}|sd_p"]))
geom["|mu_p|"] = float(np.linalg.norm(Z[f"aff|L{L}|mu_p"]))
Path(args.out).parent.mkdir(parents=True, exist_ok=True)
np.savez(args.out, **Z)
json.dump(geom, open(Path(args.out).with_suffix(".json"), "w"), indent=1)
print(json.dumps(geom, indent=1), flush=True)
