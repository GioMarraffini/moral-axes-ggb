"""IB and IH scores per condition from judged chain-of-thought answers, with consistency measures."""
import argparse
import glob
import json

import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--judge", required=True, help="folder with verdict_*.json")
ap.add_argument("--drop", default="", help="instructions to leave out, comma separated")
args = ap.parse_args()

df = pd.concat(pd.read_json(f, lines=True) for g in args.files for f in sorted(glob.glob(g)))
verdict = {}
for f in glob.glob(args.judge + "/verdict_*.json"):
    verdict.update(json.load(open(f)))
df["rating"] = df.uid.map(verdict)
print(f"{len(df)} answers, {df.rating.isna().sum()} not judged")
df = df[df.rating.notna() & ~df.instruction.isin(args.drop.split(","))]
print("no answer:", df[df.rating == 0].groupby("cell").size().to_dict())
df = df[df.rating > 0].rename(columns={"rating": "r"})
df["set"] = df["type"] + "_" + df["source_set"]

print("\nmean and std over all answers")
print(df.groupby(["set", "cell"])["r"].agg(["mean", "std", "count"]).round(2).unstack("set").to_string())
print("\nmean variance within statement (over instructions and iterations)")
print(df.groupby(["type", "cell", "id"])["r"].var().groupby(["type", "cell"]).mean().round(2).unstack("type").to_string())
print("\nmean by instruction")
print(df.pivot_table(index=["type", "cell"], columns="instruction", values="r").round(2).T.to_string())
m = df.pivot_table(index=["type", "id"], columns="cell", values="r")
print("\nshare of statements whose mean rises against base")
for c in m.columns.drop("base"):
    print(c, (m[c] > m["base"]).groupby("type").mean().round(2).to_dict())
