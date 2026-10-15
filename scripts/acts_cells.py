"""Response-mean activations at one layer for the answers of every cell in a run.

The answers are run through the unsteered model, so the activations describe the text of
each answer, not the edit that produced it.
"""
import argparse
import glob
import json

import numpy as np

from moral_axes import data
from moral_axes.model import load, response_means

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--out", required=True)
ap.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
ap.add_argument("--layer", type=int, default=23)
ap.add_argument("--iterations", type=int, default=2)
ap.add_argument("--dtype", default="fp16")
ap.add_argument("--drop", default="inverted_agreement_likert_scale,inverted_numbers_likert_scale")
args = ap.parse_args()

rows = [json.loads(l) for g in args.files for f in sorted(glob.glob(g)) for l in open(f)]
rows = [r for r in rows if r["iteration"] < args.iterations and r["instruction"] not in args.drop.split(",")
        and r["type"] in ("IB", "IH")]
instr = data.instructions()
model, tok = load(args.model, args.dtype)
prompts = [data.cot_prompt(data.system(None), instr[r["instruction"]], r["statement"]) for r in rows]
acts = response_means(model, tok, prompts, [r["response"] for r in rows])[:, args.layer].numpy()
np.savez_compressed(args.out, acts=acts.astype(np.float32), cell=[r["cell"] for r in rows],
                    type=[r["type"] for r in rows], id=[r["id"] for r in rows], uid=[r["uid"] for r in rows])
print(len(rows), "answers")
