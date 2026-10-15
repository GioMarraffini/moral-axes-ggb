"""Scales, controls and within-statement spread per cell of a chain-of-thought run."""
import argparse

import pandas as pd

from moral_axes import data

ap = argparse.ArgumentParser()
ap.add_argument("--run", nargs=2, action="append", required=True, metavar=("FILES", "JUDGE"))
ap.add_argument("--drop", default="inverted_agreement_likert_scale,inverted_numbers_likert_scale")
args = ap.parse_args()

df = pd.concat(data.judged(f, j) for f, j in args.run)
df = df[~df.instruction.isin(args.drop.split(","))]
print(f"{len(df)} answers, {df.r.isna().sum()} not judged, {(df.r == 0).sum()} with no answer")
df = df[df.r > 0]
cols = [c for c in ["IB", "IH", "neutral", "harm_no_benefit", "kindness"] if c in set(df.type)]
t = df.pivot_table(index="cell", columns="type", values="r")[cols]
base = t.loc["base"] if "base" in t.index else None
pd.set_option("display.width", 200)
print(t.round(2).to_string())
if base is not None:
    print("\nshift from base")
    print((t - base).drop("base").round(2).to_string())
print("\nwithin-statement s.d.")
print(df.groupby(["cell", "type", "id"]).r.std().groupby(["cell", "type"]).mean().unstack()[cols].round(2).to_string())
