"""Distance of every judged condition to the philosopher groups, with an equivalence test.

Model side: one value per statement (its mean rating), IB statements for IB, IH for IH.
Human side: group mean, spread and N from data/ggb/targets.json; a plotted standard error is
converted to a standard deviation.
Equivalence (TOST): the null is |model - group| >= margin on a scale; it is rejected when
both one-sided Welch t tests have p < 0.05. A condition matches a group when both scales reject.
"""
import argparse
import glob
import json

import numpy as np
import pandas as pd
from scipy import stats

from moral_axes import data

ap = argparse.ArgumentParser()
ap.add_argument("--run", nargs=2, action="append", required=True, metavar=("FILES", "JUDGE"),
                help="a glob of answer files and the folder with their verdicts; repeatable")
ap.add_argument("--margin", type=float, default=0.5)
ap.add_argument("--split", default="test")
ap.add_argument("--drop", default="inverted_agreement_likert_scale,inverted_numbers_likert_scale")
ap.add_argument("--csv", default="results/targets.csv")
args = ap.parse_args()

df = pd.concat(data.judged(files, judge) for files, judge in args.run)
df = df[(df.split == args.split) & ~df.instruction.isin(args.drop.split(","))]
df = df[df.r > 0]
per = df.groupby(["cell", "type", "id"]).r.mean().reset_index()
raw = json.load(open(data.D / "targets.json"))
targets = {k: t for k, t in raw.items() if k[0] != "_"}
for t in targets.values():
    if t.get("spread_is", raw.get("_spread_is")) == "standard_error":
        t["IB_sd"], t["IH_sd"] = t["IB_sd"] * t["N"] ** 0.5, t["IH_sd"] * t["N"] ** 0.5


def tost(x, m, sd, n, margin):
    """p of the equivalence test between sample x and a group with mean m, sd, size n."""
    d = x.mean() - m
    se = np.sqrt(x.var(ddof=1) / len(x) + sd ** 2 / n)
    dof = se ** 4 / ((x.var(ddof=1) / len(x)) ** 2 / (len(x) - 1) + (sd ** 2 / n) ** 2 / (n - 1))
    p_low = stats.t.sf((d + margin) / se, dof)
    p_high = stats.t.sf((margin - d) / se, dof)
    return max(p_low, p_high), d


rows = []
for cell, g in per.groupby("cell"):
    ib, ih = g[g.type == "IB"].r.values, g[g.type == "IH"].r.values
    for name, t in targets.items():
        p_ib, d_ib = tost(ib, t["IB"], t["IB_sd"], t["N"], args.margin)
        p_ih, d_ih = tost(ih, t["IH"], t["IH_sd"], t["N"], args.margin)
        rows.append({"cell": cell, "target": name, "IB": ib.mean(), "IH": ih.mean(),
                     "dIB": d_ib, "dIH": d_ih, "dist": np.hypot(d_ib, d_ih),
                     "p_IB": p_ib, "p_IH": p_ih, "match": p_ib < 0.05 and p_ih < 0.05})
t = pd.DataFrame(rows)
t.to_csv(args.csv, index=False)
pd.set_option("display.width", 200)
print(f"equivalence margin {args.margin} on each scale\n")
print("closest condition per group:")
for name, g in t.groupby("target"):
    g = g.sort_values("dist")
    print(f"{name:34s} " + "; ".join(f"{r.cell} (d={r.dist:.2f}, p={max(r.p_IB, r.p_IH):.3f})"
                                    for r in g.head(3).itertuples()))
print("\nmatches:")
m = t[t.match]
print(m[["cell", "target", "IB", "IH", "dist", "p_IB", "p_IH"]].round(3).to_string(index=False) if len(m) else "none")
