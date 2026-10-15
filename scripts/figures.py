"""Figures for the lab notebook: prompt check and the first steering sweep."""
import glob
import numpy as np
import json

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")
C = {"IB": "#2a78d6", "IH": "#eb6834", "neutral": "#8a8a85", "harm_no_benefit": "#1baf7a",
     "kindness": "#eda100", "IB_ous": "#2a78d6", "IH_ous": "#eb6834"}
DROP = ["inverted_agreement_likert_scale", "inverted_numbers_likert_scale"]
FIG = "lab-notebook/figures/"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": 0.6})

# 1. prompt check: per-statement means under each condition
df = pd.concat(pd.read_json(f, lines=True) for f in glob.glob("results/prompt_check3/*.jsonl"))
v = {}
for f in glob.glob("results/judge_all/verdict_*.json"):
    v.update(json.load(open(f)))
df["r"] = df.uid.map(v)
df = df[(df.r > 0) & ~df.instruction.isin(DROP)]
m = df.groupby(["type", "cell", "id"]).r.mean().reset_index()
cells = ["base", "prompt|IB", "prompt|IH"]
labels = ["default prompt", "+ IB follower", "+ IH follower"]
fig, axes = plt.subplots(1, 2, figsize=(8, 3.4), sharey=True)
for ax, t in zip(axes, ["IB", "IH"]):
    for x, c in enumerate(cells):
        y = m[(m.type == t) & (m.cell == c)].r
        ax.scatter([x + 0.08 * (i % 3 - 1) for i in range(len(y))], y, s=10, color=C[t], alpha=0.35)
        ax.hlines(y.mean(), x - 0.3, x + 0.3, color="#222", linewidth=2)
        ax.text(x, 7.25, f"{y.mean():.2f}", ha="center", fontsize=9)
    ax.set_xticks(range(3), labels, rotation=15)
    ax.set_ylim(1, 7.6)
    ax.set_title(f"{t} statements (n = {m[m.type == t].id.nunique()})", fontsize=10)
axes[0].set_ylabel("mean rating (1 = strongly disagree, 7 = strongly agree)", fontsize=8)
fig.tight_layout()
fig.savefig(FIG + "01_prompt_check.png", dpi=160)

# 2. steering sweep at the layers of interest
t = pd.read_csv("results/sweep.csv")
ref = t[t.kind != "steer"].set_index("cell")
sets = ["IB", "IH", "neutral", "harm_no_benefit", "kindness"]
names = {"IB": "IB statements", "IH": "IH statements", "neutral": "neutral opinions",
         "harm_no_benefit": "harm with no benefit", "kindness": "ordinary kindness"}
panels = [("IB", "add", 23), ("IB", "pin", 23), ("IH", "pin", 17), ("IH", "add", 23)]
fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), sharey=True)
for ax, (axis, mode, L) in zip(axes, panels):
    g = t[(t.kind == "steer") & (t.axis == axis) & (t["mode"] == mode) & (t.layer == L)].sort_values("s")
    for s in sets:
        ax.plot([0] + list(g.s), [ref.loc["base", s]] + list(g[s]), "-o", ms=4, color=C[s],
                label=names[s], linewidth=1.6)
    p = ref.loc[f"prompt|{axis}", axis]
    ax.axhline(p, color=C[axis], linestyle="--", linewidth=1)
    ax.text(8.1, p, f"{axis} prompt", color=C[axis], fontsize=8, va="center")
    ax.set_title(f"{axis} direction, {mode}, layer {L}", fontsize=10)
    ax.set_xlabel("strength")
    ax.set_xticks([0, 1, 2, 4, 6, 8])
axes[0].set_ylabel("mean rating")
axes[0].set_ylim(1, 7.3)
axes[-1].legend(fontsize=8, loc="lower right", frameon=False)
fig.tight_layout()
fig.savefig(FIG + "02_steering_sweep.png", dpi=160)

# 3. IB score against IH score for every cell, with the prompts and the baseline
fig, ax = plt.subplots(figsize=(5, 4.2))
st = t[t.kind == "steer"]
for axis, mk in [("IB", "o"), ("IH", "s"), ("rand", "x")]:
    g = st[st.axis == axis]
    ax.scatter(g.IB, g.IH, s=14 + 4 * g.s, marker=mk, color=C.get(axis, "#8a8a85"), alpha=0.5,
               label=f"{axis} direction" if axis != "rand" else "random direction")
ax.scatter(ref.loc["base", "IB"], ref.loc["base", "IH"], s=90, color="#222", marker="*",
           label="no steering", zorder=5)
for a in ("IB", "IH"):
    ax.scatter(ref.loc[f"prompt|{a}", "IB"], ref.loc[f"prompt|{a}", "IH"], s=70, marker="D",
               color=C[a], edgecolor="#222", label=f"{a} prompt", zorder=5)
ax.set_xlabel("IB score (test statements)")
ax.set_ylabel("IH score (test statements)")
ax.legend(fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(FIG + "02_ib_ih_plane.png", dpi=160)
print("ok")

# 4. round 2: full strength range for IB at layer 23, and the agreement direction
t2 = pd.read_csv("results/sweep2.csv")
both = pd.concat([t[t.kind == "steer"], t2[t2.kind == "steer"]])
panels = [("IB", "add", 23, both), ("IB", "pin", 23, both), ("agree", "add", 23, t2), ("agree", "pin", 23, t2)]
fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), sharey=True)
for ax, (axis, mode, L, src) in zip(axes, panels):
    g = src[(src.axis == axis) & (src["mode"] == mode) & (src.layer == L) & (src.mass > 0.5)]
    g = pd.concat([g, pd.DataFrame([{"s": 0, **{k: ref.loc["base", k] for k in sets}}])]).sort_values("s")
    for s in sets:
        ax.plot(g.s, g[s], "-o", ms=4, color=C[s], label=names[s], linewidth=1.6)
    ax.axvline(0, color="#bbb", linewidth=0.8)
    ax.set_title(f"{'agreement' if axis == 'agree' else axis} direction, {mode}, layer {L}", fontsize=10)
    ax.set_xlabel("strength")
axes[0].set_ylabel("mean rating")
axes[0].set_ylim(1, 7.3)
axes[-1].legend(fontsize=8, loc="lower right", frameon=False)
fig.tight_layout()
fig.savefig(FIG + "03_opposite_and_agreement.png", dpi=160)

# 5. the four prompts in the IB, IH plane, judged chain of thought
df = pd.concat(pd.read_json(f, lines=True) for f in glob.glob("results/prompt_check[34]/*.jsonl"))
v = {}
for f in glob.glob("results/judge_all/verdict_*.json"):
    v.update(json.load(open(f)))
df["r"] = df.uid.map(v)
df = df[(df.r > 0) & ~df.instruction.isin(DROP)]
m = df.groupby(["cell", "type"]).r.mean().unstack()
fig, ax = plt.subplots(figsize=(4.6, 4))
lab = {"base": "default prompt", "prompt|IB": "+ IB", "prompt|IH": "+ IH", "prompt|IB_notIH": "+ IB, reject IH"}
for c, row in m.iterrows():
    ax.scatter(row.IB, row.IH, s=60, color="#222" if c == "base" else C["IB"], zorder=3)
    ax.annotate(lab[c], (row.IB, row.IH), xytext=(6, 4), textcoords="offset points", fontsize=9)
ax.set_xlabel("IB (judged chain of thought)")
ax.set_ylabel("IH (judged chain of thought)")
ax.set_xlim(3.5, 7)
ax.set_ylim(1, 4)
fig.tight_layout()
fig.savefig(FIG + "03_prompts_plane.png", dpi=160)
print("ok2")

# 6. chain-of-thought confirmation in the IB, IH plane
v = {}
for f in glob.glob("results/judge_all/*.json") + glob.glob("results/judge_confirm/*.json"):
    v.update(json.load(open(f)))
df = pd.concat(pd.read_json(f, lines=True) for f in glob.glob("results/prompt_check[34]/*.jsonl")
               + glob.glob("results/confirm/*.jsonl"))
df = df[(df.split == "test") & ~df.instruction.isin(DROP)]
df["r"] = df.uid.map(v)
m = df[df.r > 0].groupby(["cell", "type"]).r.mean().unstack()
lab = {"base": "no steering", "prompt|IB": "IB prompt", "prompt|IH": "IH prompt",
       "prompt|IB_notIH": "IB, reject IH prompt", "add|IB|L23|2": "IB add 2, L23",
       "pin|IB|L23|2": "IB pin 2, L23", "pin|IB|L23|-4": "IB pin -4, L23",
       "pin|IH|L17|8": "IH pin 8, L17", "add|agree|L23|1": "agreement add 1, L23"}
fig, ax = plt.subplots(figsize=(5.4, 4.6))
for c, row in m.iterrows():
    k = "prompt" if c.startswith("prompt") else ("base" if c == "base" else "steer")
    ax.scatter(row.IB, row.IH, s=70, marker={"prompt": "D", "base": "*", "steer": "o"}[k],
               color={"prompt": C["IH"], "base": "#222", "steer": C["IB"]}[k], zorder=3)
    ax.annotate(lab[c], (row.IB, row.IH), xytext=(6, 3), textcoords="offset points", fontsize=8)
ax.set_xlabel("IB, judged chain of thought (test statements)")
ax.set_ylabel("IH, judged chain of thought")
ax.set_xlim(3.5, 7.4)
ax.set_ylim(1, 7.2)
fig.tight_layout()
fig.savefig(FIG + "04_cot_confirmation.png", dpi=160)

# 7. round 3 sweeps: orthogonalised directions and the kind and cruel directions
t3 = pd.read_csv("results/sweep3.csv")
panels = [("IB_orth", "add"), ("IH_orth", "add"), ("kind", "add"), ("cruel", "add")]
titles = {"IB_orth": "IB with IH projected out", "IH_orth": "IH with IB projected out",
          "kind": "kindness direction", "cruel": "cruelty direction"}
fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), sharey=True)
for ax, (axis, mode) in zip(axes, panels):
    g = t3[(t3.kind == "steer") & (t3.axis == axis) & (t3["mode"] == mode)]
    g = pd.concat([g, pd.DataFrame([{"s": 0, **{k: ref.loc["base", k] for k in sets}}])]).sort_values("s")
    for s in sets:
        ax.plot(g.s, g[s], "-o", ms=4, color=C[s], label=names[s], linewidth=1.6)
    ax.axvline(0, color="#bbb", linewidth=0.8)
    ax.set_title(f"{titles[axis]}, {mode}, layer 23", fontsize=10)
    ax.set_xlabel("strength")
axes[0].set_ylabel("mean rating")
axes[0].set_ylim(1, 7.3)
axes[-1].legend(fontsize=8, loc="lower right", frameon=False)
fig.tight_layout()
fig.savefig(FIG + "04_round3_sweep.png", dpi=160)
print("ok3")

# 8. every chain-of-thought condition against the philosopher groups
tg = pd.read_csv("results/targets.csv")
cells = tg.drop_duplicates("cell").set_index("cell")[["IB", "IH"]]
targets = {k: t for k, t in json.load(open("data/ggb/targets.json")).items() if k[0] != "_"}
fig, ax = plt.subplots(figsize=(6.4, 5.6))
for c, row in cells.iterrows():
    k = "prompt" if c.startswith("prompt") else ("base" if c == "base" else
        ("answer" if any(x in c for x in ("acc", "both")) else "steer"))
    ax.scatter(row.IH, row.IB, s=34, marker={"prompt": "D", "base": "*", "steer": "o", "answer": "^"}[k],
               color={"prompt": C["IH"], "base": "#222", "steer": C["IB"], "answer": C["kindness"]}[k],
               alpha=0.85, zorder=3)
for c in ["base", "prompt|IB", "prompt|IH", "add|IB|L23|-8", "add|IB_orth|L23|4", "add|IH_orth|L23|8",
          "pin|IH|L17|8", "add|agree|L23|1", "add|IB|L23|4", "add|IHacc|L23|4", "add|IHacc|L23|8",
          "add|both|L23|8", "add|IBacc|L23|4", "add|IB_notIH|L23|12"]:
    if c not in cells.index:
        continue
    r = cells.loc[c]
    ax.annotate(c.replace("|L23", "").replace("|L17", " L17"), (r.IH, r.IB), xytext=(5, 3),
                textcoords="offset points", fontsize=7, color="#444")
for name, t in targets.items():
    ax.errorbar(t["IH"], t["IB"], xerr=t["IH_sd"] / t["N"] ** 0.5, yerr=t["IB_sd"] / t["N"] ** 0.5,
                fmt="s", color="#1baf7a", ms=6, capsize=3, zorder=4)
    ax.annotate(name.replace("_", " "), (t["IH"], t["IB"]), xytext=(6, -9), textcoords="offset points",
                fontsize=8, color="#0b6b48")
ax.scatter([], [], marker="o", color=C["IB"], label="steering (chain of thought)")
ax.scatter([], [], marker="^", color=C["kindness"], label="steering with answer-built directions")
ax.scatter([], [], marker="D", color=C["IH"], label="system prompt")
ax.scatter([], [], marker="s", color="#1baf7a", label="human groups (Kahane et al. 2018)")
ax.set_xlabel("IH")
ax.set_ylabel("IB")
ax.set_xlim(1, 7)
ax.set_ylim(1, 7.4)
ax.legend(fontsize=8, frameon=False, loc="lower right")
fig.tight_layout()
fig.savefig(FIG + "05_reachable_plane.png", dpi=160)
print("ok4")

# 9. the 5 x 5 grid of the two answer-built directions, chain of thought
g2 = pd.read_csv("results/sweep5.csv") if False else None
v = {}
for f in glob.glob("results/judge_grid2/*.json"):
    v.update(json.load(open(f)))
df = pd.concat(pd.read_json(f, lines=True) for f in glob.glob("results/grid2/*.jsonl"))
df = df[(df.split == "test") & ~df.instruction.isin(DROP)]
df["r"] = df.uid.map(v)
m = df[df.r > 0].groupby(["cell", "type"]).r.mean().unstack()


def ab(c):
    a = b = 0
    for part in c.split("+"):
        if "IBacc" in part:
            a = float(part.split("|")[-1])
        if "IHacc" in part:
            b = float(part.split("|")[-1])
    return a, b


m["a"], m["b"] = zip(*[ab(c) for c in m.index])
fig, ax = plt.subplots(figsize=(6.4, 5.6))
for a, g in m.groupby("a"):
    g = g.sort_values("b")
    ax.plot(g.IH, g.IB, "-", color="#bbb", linewidth=1, zorder=1)
for b, g in m.groupby("b"):
    g = g.sort_values("a")
    ax.plot(g.IH, g.IB, "-", color="#bbb", linewidth=1, zorder=1)
sc = ax.scatter(m.IH, m.IB, c=m.a, cmap="Blues", s=46, edgecolor="#444", linewidth=0.5, zorder=3)
for c, r in m.iterrows():
    if r.b == 4 or r.a == 4 or (r.a == -4 and r.b == -4):
        ax.annotate(f"({r.a:g}, {r.b:g})", (r.IH, r.IB), xytext=(5, 3), textcoords="offset points", fontsize=7)
for name, t in targets.items():
    ax.scatter(t["IH"], t["IB"], marker="s", color="#1baf7a", s=50, zorder=4)
    ax.annotate(name.replace("_", " "), (t["IH"], t["IB"]), xytext=(6, -9), textcoords="offset points",
                fontsize=8, color="#0b6b48")
ax.set_xlabel("IH")
ax.set_ylabel("IB")
ax.set_xlim(1, 7)
ax.set_ylim(1, 7.4)
cb = fig.colorbar(sc, ax=ax, shrink=0.8)
cb.set_label("IB-accepting strength a (lines join equal a or b)")
fig.tight_layout()
fig.savefig(FIG + "07_grid_plane.png", dpi=160)
print("ok5")

# 10. final cells: position against the groups, coloured by the worst control shift (chain of thought)
v = {}
for f in glob.glob("results/judge_final/*.json"):
    v.update(json.load(open(f)))
df = pd.concat(pd.read_json(f, lines=True) for f in glob.glob("results/final/*.jsonl") + glob.glob("results/final_ctrl/*.jsonl"))
df = df[~df.instruction.isin(DROP)]
df["r"] = df.uid.map(v)
m = df[df.r > 0].groupby(["cell", "type"]).r.mean().unstack()
base = m.loc["base"]
m["ctrl"] = (m[["neutral", "harm_no_benefit", "kindness"]] - base[["neutral", "harm_no_benefit", "kindness"]]).abs().max(1)
fig, ax = plt.subplots(figsize=(6.6, 5.6))
sc = ax.scatter(m.IH, m.IB, c=m.ctrl, cmap="YlOrRd", vmin=0, vmax=2.5, s=60, edgecolor="#444", linewidth=0.5, zorder=3)
for c, r in m.iterrows():
    ax.annotate(c.replace("IBacc|L23|", "a").replace("+IHacc|L23|", " b").replace("IHacc|L23|", "b"), (r.IH, r.IB),
                xytext=(5, 3), textcoords="offset points", fontsize=7)
for name, t in targets.items():
    ax.scatter(t["IH"], t["IB"], marker="s", color="#1baf7a", s=50, zorder=4)
    ax.annotate(name.replace("_", " "), (t["IH"], t["IB"]), xytext=(6, -9), textcoords="offset points", fontsize=8, color="#0b6b48")
ax.set_xlabel("IH")
ax.set_ylabel("IB")
ax.set_xlim(1, 7)
ax.set_ylim(1, 7.4)
cb = fig.colorbar(sc, ax=ax, shrink=0.8)
cb.set_label("largest control shift from baseline (points)")
fig.tight_layout()
fig.savefig(FIG + "08_final_cells.png", dpi=160)
print("ok6")

# 11. paper figure: model positions with standard errors against the human groups
v = {}
for f in glob.glob("results/judge_final/*.json"):
    v.update(json.load(open(f)))
df = pd.concat(pd.read_json(f, lines=True) for f in glob.glob("results/final/*.jsonl"))
df = df[~df.instruction.isin(DROP)]
df["r"] = df.uid.map(v)
df = df[df.r > 0]
per = df.groupby(["cell", "type", "id"]).r.mean().reset_index()
stats = per.groupby(["cell", "type"]).r.agg(["mean", "sem", "std"]).unstack("type")
keep = {"base": "Qwen2.5-3B (unsteered)", "IBacc|L23|-8+IHacc|L23|4": "steered (-8, 4)",
        "IBacc|L23|-10+IHacc|L23|4": "steered (-10, 4)", "IBacc|L23|-6+IHacc|L23|6": "steered (-6, 6)",
        "IHacc|L23|8": "steered (0, 8)", "IBacc|L23|4+IHacc|L23|4": "steered (4, 4)"}
fig, ax = plt.subplots(figsize=(7, 6))
for name, t in targets.items():
    n = t["N"] ** 0.5
    sd_ib = t["IB_sd"] * (1 if t.get("spread_is") == "standard_deviation" else n)
    sd_ih = t["IH_sd"] * (1 if t.get("spread_is") == "standard_deviation" else n)
    ax.errorbar(t["IH"], t["IB"], xerr=sd_ih / n, yerr=sd_ib / n, fmt="s", color="#1baf7a", ms=6, capsize=3, zorder=4)
    ax.annotate(name.replace("_", " "), (t["IH"], t["IB"]), xytext=(7, -10), textcoords="offset points", fontsize=8, color="#0b6b48")
for c, lab in keep.items():
    s = stats.loc[c]
    col = "#222" if c == "base" else C["IB"]
    ax.errorbar(s[("mean", "IH")], s[("mean", "IB")], xerr=s[("sem", "IH")], yerr=s[("sem", "IB")],
                fmt="*" if c == "base" else "o", color=col, ms=12 if c == "base" else 7, capsize=3, zorder=5)
    ax.annotate(lab, (s[("mean", "IH")], s[("mean", "IB")]), xytext=(7, 4), textcoords="offset points", fontsize=8, color=col)
ax.set_xlabel("Instrumental harm (IH)")
ax.set_ylabel("Impartial beneficence (IB)")
ax.set_xlim(1, 7)
ax.set_ylim(1, 7)
ax.scatter([], [], marker="s", color="#1baf7a", label="human groups (mean ± s.e.)")
ax.scatter([], [], marker="o", color=C["IB"], label="steered model (mean ± s.e. over statements)")
ax.legend(fontsize=8, frameon=False, loc="upper left")
fig.tight_layout()
fig.savefig(FIG + "paper_plane.png", dpi=200)

# 12. paper figure: per-statement spread, unsteered against steered
fig, ax = plt.subplots(figsize=(6.4, 3.4))
cells_v = ["base", "IBacc|L23|-8+IHacc|L23|4", "IBacc|L23|-6+IHacc|L23|6", "IHacc|L23|8", "IBacc|L23|4+IHacc|L23|4"]
labels = ["unsteered", "(-8, 4)", "(-6, 6)", "(0, 8)", "(4, 4)"]
w = df.groupby(["cell", "type", "id"]).r.std().groupby(["cell", "type"]).mean().unstack("type")
x = np.arange(len(cells_v))
ax.bar(x - 0.18, w.loc[cells_v, "IB"], 0.36, color=C["IB"], label="IB statements")
ax.bar(x + 0.18, w.loc[cells_v, "IH"], 0.36, color=C["IH"], label="IH statements")
ax.set_xticks(x, labels)
ax.set_ylabel("s.d. of the 40 answers\nto one statement")
ax.legend(fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(FIG + "paper_variance.png", dpi=200)
print("ok7")
