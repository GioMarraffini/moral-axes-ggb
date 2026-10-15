"""3D PCA of answer activations (layer 23, unsteered forward pass) with the two axes drawn."""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")
z = np.load("results/final_acts_L23.npz")
X, cell = z["acts"], z["cell"]
Z = np.load("results/directions_resp2/directions.npz")
vIB, vIH = Z["IBacc|v"][23], Z["IHacc|v"][23]
mu = X[cell == "base"].mean(0)
U, S, Vt = np.linalg.svd(X - mu, full_matrices=False)
ev = S ** 2 / (S ** 2).sum()
P = Vt[:3]
proj = (X - mu) @ P.T
names = {"base": "unsteered", "IBacc|L23|-8+IHacc|L23|4": "lay / virtue / deontology (-8, 4)",
         "IBacc|L23|-10+IHacc|L23|4": "Kantian (-10, 4)", "IBacc|L23|-6+IHacc|L23|6": "non-util. consequentialism (-6, 6)",
         "IHacc|L23|8": "rule utilitarianism (0, 8)", "IBacc|L23|4+IHacc|L23|4": "act utilitarianism (4, 4)"}
cols = {"base": "#222", "IBacc|L23|-8+IHacc|L23|4": "#2a78d6", "IBacc|L23|-10+IHacc|L23|4": "#1baf7a",
        "IBacc|L23|-6+IHacc|L23|6": "#eda100", "IHacc|L23|8": "#e87ba4", "IBacc|L23|4+IHacc|L23|4": "#eb6834"}
fig = plt.figure(figsize=(7.5, 6))
ax = fig.add_subplot(111, projection="3d")
rng = np.random.default_rng(0)
for c, lab in names.items():
    p = proj[cell == c]
    idx = rng.choice(len(p), min(150, len(p)), replace=False)
    ax.scatter(p[idx, 0], p[idx, 1], p[idx, 2], s=5, alpha=0.25, color=cols[c])
    ax.scatter(*p.mean(0), s=120, color=cols[c], edgecolor="k", label=lab, zorder=10)
for n, v, col in (("IB axis", vIB, "#2a78d6"), ("IH axis", vIH, "#eb6834")):
    a = P @ v * 6
    ax.quiver(0, 0, 0, *a, color=col, linewidth=2.5, arrow_length_ratio=0.12)
    ax.text(*(a * 1.1), n, color=col, fontsize=10, weight="bold")
ax.set_xlabel(f"PC1 ({ev[0]:.0%})")
ax.set_ylabel(f"PC2 ({ev[1]:.0%})")
ax.set_zlabel(f"PC3 ({ev[2]:.0%})")
ax.legend(fontsize=7, loc="upper left", frameon=False)
ax.view_init(elev=22, azim=-55)
fig.tight_layout()
fig.savefig("lab-notebook/figures/paper_pca3d.png", dpi=200)
