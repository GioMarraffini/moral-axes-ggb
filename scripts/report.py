"""Mean rating per cell and statement set. Writes a CSV and prints one table per layer and source."""
import argparse
import glob

import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--csv", default="results/sweep.csv")
ap.add_argument("--drop", default="", help="instructions to leave out, comma separated")
args = ap.parse_args()

df = pd.concat(pd.read_json(f, lines=True) for g in args.files for f in sorted(glob.glob(g)))
df = df[~df.instruction.isin(args.drop.split(","))]
df["set"] = df["type"].where(df["source_set"] != "ous", df["type"] + "_ous")
meta = [k for k in ["kind", "axis", "mode", "layer", "s"] if k in df]
t = df.pivot_table(index="cell", columns="set", values="rating", aggfunc="mean")
t["mass"] = df.groupby("cell")["mass"].mean() if "mass" in df else float("nan")
t = t.join(df.groupby("cell")[meta].first()).reset_index()
t.to_csv(args.csv, index=False)

cols = [c for c in ["IB", "IH", "IB_ous", "IH_ous", "neutral", "harm_no_benefit", "kindness", "mass"]
        if c in t]
pd.set_option("display.width", 200)
print("baseline and system prompts")
print(t[t.kind != "steer"].set_index("cell")[cols].round(2).to_string())
st = t[t.kind == "steer"]
for (L, ax, mode), g in st.groupby(["layer", "axis", "mode"]):
    print(f"\nlayer {int(L)}  axis {ax}  {mode}")
    print(g.sort_values("s").set_index("s")[cols].round(2).to_string())
