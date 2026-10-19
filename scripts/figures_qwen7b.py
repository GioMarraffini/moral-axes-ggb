"""Figures for the Qwen2.5-7B-Instruct chapter: the steering grid at each layer against the human groups."""
import argparse
import json

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from moral_axes import data

matplotlib.use("Agg")
DROP = ["inverted_agreement_likert_scale", "inverted_numbers_likert_scale"]
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": 0.6})

ap = argparse.ArgumentParser()
ap.add_argument("--run", nargs=2, action="append", required=True, metavar=("FILES", "JUDGE"))
ap.add_argument("--layers", default="14,18,21")
ap.add_argument("--out", default="lab-notebook/figures/10_qwen7b_grid.png")
args = ap.parse_args()

df = pd.concat(data.judged(f, j) for f, j in args.run)
df = df[(df.split == "test") & ~df.instruction.isin(DROP) & (df.r > 0)]
m = df.groupby(["cell", "type"]).r.mean().unstack()
targets = {k: t for k, t in json.load(open(data.D / "targets.json")).items() if k[0] != "_"}


def abl(c):
    a = b = 0.0
    L = None
    for part in c.split("+"):
        if "|L" in part:
            L = int(part.split("|L")[1].split("|")[0])
        if "IBacc" in part or "IBaff" in part:
            a = float(part.split("|")[-1])
        if "IHacc" in part or "IHaff" in part:
            b = float(part.split("|")[-1])
    return a, b, L


m["a"], m["b"], m["L"] = zip(*[abl(c) for c in m.index])
base = m.loc["base"]
m["ctrl"] = (m[["neutral", "harm_no_benefit", "kindness"]] - base[["neutral", "harm_no_benefit", "kindness"]]).abs().max(1)
layers = [int(x) for x in args.layers.split(",")]
panels = [(L, "a") for L in layers] + ([(layers[0], "ctrl")] if len(layers) == 1 else [])
fig, axes = plt.subplots(1, len(panels), figsize=(5.2 * len(panels), 5.2), sharey=True)
for ax, (L, colour) in zip(axes, panels):
    g = m[(m.L == L) | (m.index == "base")]
    for _, gg in g.groupby("a"):
        gg = gg.sort_values("b")
        ax.plot(gg.IH, gg.IB, "-", color="#bbb", linewidth=1, zorder=1)
    for _, gg in g.groupby("b"):
        gg = gg.sort_values("a")
        ax.plot(gg.IH, gg.IB, "-", color="#bbb", linewidth=1, zorder=1)
    if colour == "a":
        sc = ax.scatter(g.IH, g.IB, c=g.a, cmap="Blues", vmin=m.a.min(), vmax=m.a.max(), s=46,
                        edgecolor="#444", linewidth=0.5, zorder=3)
        cb = fig.colorbar(sc, ax=ax, shrink=0.8)
        cb.set_label("IB-accepting strength a (lines join equal a or b)")
    else:
        sc = ax.scatter(g.IH, g.IB, c=g.ctrl, cmap="YlOrRd", vmin=0, vmax=2.5, s=46,
                        edgecolor="#444", linewidth=0.5, zorder=3)
        cb = fig.colorbar(sc, ax=ax, shrink=0.8)
        cb.set_label("largest control shift from unsteered (points)")
    ax.scatter(base.IH, base.IB, marker="*", color="#222", s=120, zorder=5)
    for c, r in g.iterrows():
        if (abs(r.a) == g.a.abs().max() and abs(r.b) == g.b.abs().max()) or (len(layers) == 1 and r.b in (g.b.min(), g.b.max())):
            ax.annotate(f"({r.a:g}, {r.b:g})", (r.IH, r.IB), xytext=(5, 3), textcoords="offset points", fontsize=7)
    for name, t in targets.items():
        ax.scatter(t["IH"], t["IB"], marker="s", color="#1baf7a", s=50, zorder=4)
        ax.annotate(name.replace("_", " "), (t["IH"], t["IB"]), xytext=(6, -9), textcoords="offset points",
                    fontsize=7, color="#0b6b48")
    ax.set_title(f"layer {L}")
    ax.set_xlabel("IH")
    ax.set_xlim(1, 7)
    ax.set_ylim(1, 7.4)
axes[0].set_ylabel("IB")
fig.savefig(args.out, dpi=160, bbox_inches="tight")
print(m[["IB", "IH", "neutral", "harm_no_benefit", "kindness"]].round(2).to_string())
