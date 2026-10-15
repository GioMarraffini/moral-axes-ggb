"""Build the IB and IH directions at every layer from the train statements.

Direction = mean response activation with the axis system prompt minus the mean with the
default system prompt, over generated chain-of-thought answers to the axis's train statements.
The agreement direction is a forced "Strongly Agree" answer minus a forced "Strongly Disagree"
answer on the neutral train statements, over the six wordings.
spread.json holds, per axis and layer, how each prompted answer's displacement from the
baseline mean relates to the direction.
"""
import argparse
import glob
import json
from pathlib import Path

import numpy as np
import torch

from moral_axes import data
from moral_axes import cells as C
from moral_axes.model import load, response_means

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
ap.add_argument("--out", required=True)
ap.add_argument("--dtype", default="fp16")
ap.add_argument("--responses", nargs="+", required=True, help="globs of generate.py outputs")
ap.add_argument("--iterations", type=int, default=2)
ap.add_argument("--axes", default="IB,IH")
ap.add_argument("--spread_layers", default="17,20,23,26")
ap.add_argument("--save_acts", action="store_true", help="dump per-answer activations at the spread layers")
args = ap.parse_args()

out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
model, tok = load(args.model, args.dtype)
instr = data.instructions()
gen = [json.loads(l) for g in args.responses for f in sorted(glob.glob(g)) for l in open(f)]
gen = [r for r in gen if r["split"] == "train" and r["iteration"] < args.iterations]
Z, spread = {}, {}
SL = [int(x) for x in args.spread_layers.split(",")]
STYPE = {"IB": "IB", "IH": "IH", "IB_notIH": "IB", "kind": "IB", "cruel": "IH"}

for axis in args.axes.split(","):
    acts = {}
    for cell in ({"kind": "base"}, {"kind": "prompt", "axis": axis}):
        rows = [r for r in gen if r["type"] == STYPE[axis] and r["cell"] == C.name(cell)]
        prompts = [data.cot_prompt(C.system(cell), instr[r["instruction"]], r["statement"])
                   for r in rows]
        acts[cell["kind"]] = response_means(model, tok, prompts, [r["response"] for r in rows])
        print(axis, cell["kind"], len(rows), flush=True)
        if args.save_acts:
            np.savez(out / f"acts_{axis}_{cell['kind']}.npz",
                     acts=acts[cell["kind"]][:, SL].numpy().astype(np.float32), layers=SL,
                     id=[r["id"] for r in rows], instruction=[r["instruction"] for r in rows],
                     iteration=[r["iteration"] for r in rows])
    mu = acts["base"].mean(0)
    v = acts["prompt"].mean(0) - mu
    Z[f"{axis}|v"], Z[f"{axis}|mu"] = v, mu
    spread[axis] = {}
    for L in SL:
        u = v[L] / v[L].norm()
        d = acts["prompt"][:, L] - mu[L]
        along = d @ u
        cos = torch.nn.functional.cosine_similarity(d, v[L].expand_as(d), dim=-1)
        base_along = (acts["base"][:, L] - mu[L]) @ u
        spread[axis][L] = {
            "n": int(d.shape[0]), "norm_v": float(v[L].norm()),
            "cos_mean": float(cos.mean()), "cos_std": float(cos.std()),
            "cos_q10_q50_q90": [float(q) for q in cos.quantile(torch.tensor([.1, .5, .9]))],
            "along_mean": float(along.mean()), "along_std": float(along.std()),
            "base_along_std": float(base_along.std()),
            "share_above_zero": float((along > 0).float().mean()),
            "var_share_along": float(along.var() / d.var(0).sum()),
            "resid_norm_mean": float((d - along.unsqueeze(-1) * u).norm(dim=-1).mean()),
        }

# agreement direction from forced answers on the neutral train statements
rows = [r for r in data.statements("train") if r["type"] == "neutral"]
prompts, agree, disagree = [], [], []
for r in rows:
    for k, text in instr.items():
        opts, vals = data.OPTIONS[k]
        prompts.append(data.rate_prompt(data.system(None), text, r["statement"]))
        agree.append(opts[vals.index(7)])
        disagree.append(opts[vals.index(1)])
a = response_means(model, tok, prompts, agree)
Z["agree|v"] = (a - response_means(model, tok, prompts, disagree)).mean(0)
Z["agree|mu"] = a.mean(0)
print("agree", len(prompts), flush=True)

cos = lambda x, y: torch.nn.functional.cosine_similarity(Z[x], Z[y], dim=-1).tolist()
keys = [k[:-2] for k in Z if k.endswith("|v")]
geom = {f"norm {k}": Z[f"{k}|v"].norm(dim=-1).tolist() for k in keys}
geom["norm baseline"] = Z["IB|mu"].norm(dim=-1).tolist()
for i, x in enumerate(keys):
    for y in keys[i + 1:]:
        geom[f"cos {x},{y}"] = cos(f"{x}|v", f"{y}|v")
json.dump(spread, open(out / "spread.json", "w"), indent=1)
np.savez(out / "directions.npz", **{k: v.numpy().astype(np.float32) for k, v in Z.items()})
json.dump(geom, open(out / "geometry.json", "w"), indent=1)
print("done", flush=True)
