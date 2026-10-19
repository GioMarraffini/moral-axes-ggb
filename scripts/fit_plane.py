"""Fit the map from the two steering strengths to the two scores and invert it for each target.

Input: judged chain-of-thought answers of the grid cells (IBacc strength a, IHacc strength b).
A quadratic response surface is fitted per scale; each target's (a, b) is the least-squares
inverse inside the grid's range. Writes a cell list for the confirmation run.
"""
import argparse
import json

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from moral_axes import data

ap = argparse.ArgumentParser()
ap.add_argument("--run", nargs=2, action="append", required=True, metavar=("FILES", "JUDGE"),
                help="answer files (glob) and the judge folder of that run; repeatable")
ap.add_argument("--out", default="results/target_cells.json")
ap.add_argument("--drop", default="inverted_agreement_likert_scale,inverted_numbers_likert_scale")
ap.add_argument("--layer", type=int, default=23, help="keep the grid cells at this layer; the output cells use it")
ap.add_argument("--range", type=float, nargs=2, help="bounds for the inverted strengths (default: the grid's range)")
args = ap.parse_args()

df = pd.concat(data.judged(f, j) for f, j in args.run)
df = df[(df.split == "test") & ~df.instruction.isin(args.drop.split(",")) & (df.r > 0)]
df = df[(df.cell == "base") | df.cell.str.contains(f"|L{args.layer}|", regex=False)]


def strengths(c):
    a = b = 0.0
    terms = c.get("terms") or ([{"axis": c["axis"], "s": c["s"]}] if c["kind"] == "steer" else [])
    for t in terms:
        if t["axis"] in ("IBacc", "IBaff"):
            a = t["s"]
        if t["axis"] in ("IHacc", "IHaff"):
            b = t["s"]
    return a, b


cells = df.drop_duplicates("cell").set_index("cell")
pts = []
for cell, c in cells.iterrows():
    a, b = strengths(json.loads(c[["kind", "axis", "mode", "layer", "s", "terms"]].dropna().to_json()))
    g = df[df.cell == cell]
    pts.append({"cell": cell, "a": a, "b": b, "IB": g[g.type == "IB"].r.mean(), "IH": g[g.type == "IH"].r.mean()})
pts = pd.DataFrame(pts)
print(pts.sort_values(["a", "b"]).round(2).to_string(index=False))

X = np.stack([np.ones(len(pts)), pts.a, pts.b, pts.a ** 2, pts.b ** 2, pts.a * pts.b], 1)
coef = {k: np.linalg.lstsq(X, pts[k], rcond=None)[0] for k in ("IB", "IH")}
feat = lambda a, b: np.array([1, a, b, a * a, b * b, a * b])
for k in ("IB", "IH"):
    pred = X @ coef[k]
    print(f"{k}: fit r = {np.corrcoef(pred, pts[k])[0, 1]:.3f}, rmse = {np.sqrt(((pred - pts[k]) ** 2).mean()):.2f}")

lo, hi = args.range if args.range else (pts.a.min(), pts.a.max())
targets = {k: t for k, t in json.load(open(data.D / "targets.json")).items() if k[0] != "_"}
out = []
for name, t in targets.items():
    f = lambda z: (feat(*z) @ coef["IB"] - t["IB"]) ** 2 + (feat(*z) @ coef["IH"] - t["IH"]) ** 2
    best = min((minimize(f, z0, bounds=[(lo, hi), (lo, hi)]) for z0 in [(0, 0), (2, 2), (-2, -2), (2, -2), (-2, 2)]),
               key=lambda r: r.fun)
    a, b = (round(float(x), 1) for x in best.x)
    print(f"{name:34s} a={a:+.1f} b={b:+.1f} predicted IB {feat(a, b) @ coef['IB']:.2f} IH {feat(a, b) @ coef['IH']:.2f}"
          f" target {t['IB']:.2f} {t['IH']:.2f} residual {np.sqrt(best.fun):.2f}")
    L = args.layer
    terms = [t_ for t_ in ({"axis": "IBacc", "layer": L, "s": a}, {"axis": "IHacc", "layer": L, "s": b}) if t_["s"] != 0]
    out.append({"kind": "steer2", "terms": terms, "target": name})
json.dump(out, open(args.out, "w"), indent=0)
