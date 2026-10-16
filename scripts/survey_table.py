"""Unsteered placement of several models against the human groups: table and figure.

Each run is a folder with moral.jsonl, ctrl.jsonl and judge/; extra runs can be given as
tag, files glob, judge folder. Scores are means over the test statements of each type.
"""
import argparse
import glob
import json
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from moral_axes import data

matplotlib.use("Agg")
DROP = ["inverted_agreement_likert_scale", "inverted_numbers_likert_scale"]
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": 0.6})

ap = argparse.ArgumentParser()
ap.add_argument("--dir", default="results/survey")
ap.add_argument("--extra", nargs=3, action="append", default=[], metavar=("TAG", "FILES", "JUDGE"))
ap.add_argument("--csv", default="results/survey/survey.csv")
ap.add_argument("--fig", default="lab-notebook/figures/11_survey_plane.png")
args = ap.parse_args()

runs = {}
for d in sorted(glob.glob(args.dir + "/*")):
    if os.path.isdir(d + "/judge"):
        runs.setdefault(os.path.basename(d), []).append((d + "/*.jsonl", d + "/judge"))
for tag, files, judge in args.extra:
    runs.setdefault(tag, []).append((files, judge))
targets = {k: t for k, t in json.load(open(data.D / "targets.json")).items() if k[0] != "_"}
centre = np.mean([[t["IB"], t["IH"]] for t in targets.values()], 0)
rows = []
for tag, parts in runs.items():
    df = pd.concat(data.judged(f, j) for f, j in parts)
    df = df[(df.split == "test") & (df.cell == "base") & ~df.instruction.isin(DROP)]
    rated = df[df.r > 0]
    m = rated.groupby(["type", "id"]).r.mean().groupby("type").mean()
    r = {"model": tag, "n": len(df), "unrated": int((df.r > 0).eq(False).sum()), **m.round(2).to_dict()}
    p = np.array([m.get("IB", np.nan), m.get("IH", np.nan)])
    d = {k: float(np.hypot(*(p - [t["IB"], t["IH"]]))) for k, t in targets.items()}
    near = min(d, key=d.get)
    r.update({"d_lay": round(d["lay_population"], 2), "d_centre": round(float(np.hypot(*(p - centre))), 2),
              "nearest": near, "d_nearest": round(d[near], 2)})
    rows.append(r)
tab = pd.DataFrame(rows).sort_values("d_lay")
cols = ["model", "n", "unrated", "IB", "IH", "neutral", "harm_no_benefit", "kindness", "d_lay", "d_centre", "nearest", "d_nearest"]
tab = tab[[c for c in cols if c in tab.columns]]
print(tab.to_string(index=False))
os.makedirs(os.path.dirname(args.csv), exist_ok=True)
tab.to_csv(args.csv, index=False)

fig, ax = plt.subplots(figsize=(6.6, 5.8))
for _, r in tab.iterrows():
    ax.scatter(r.IH, r.IB, s=46, color="#2a78d6", edgecolor="#222", linewidth=0.5, zorder=3)
    ax.annotate(r.model, (r.IH, r.IB), xytext=(5, 3), textcoords="offset points", fontsize=8)
for name, t in targets.items():
    ax.scatter(t["IH"], t["IB"], marker="s", color="#1baf7a", s=50, zorder=4)
    ax.annotate(name.replace("_", " "), (t["IH"], t["IB"]), xytext=(6, -9), textcoords="offset points",
                fontsize=8, color="#0b6b48")
ax.scatter(*centre[::-1], marker="+", color="#0b6b48", s=80, zorder=4)
ax.set_xlabel("IH")
ax.set_ylabel("IB")
ax.set_xlim(1, 7)
ax.set_ylim(1, 7.4)
fig.tight_layout()
fig.savefig(args.fig, dpi=160)
