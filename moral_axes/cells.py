"""The conditions of an experiment: baseline, system prompts, single-layer steering.

add: h + s * v, with v the prompted mean minus the baseline mean of response activations.
pin: the projection of h on v / |v| is set to the baseline projection plus s * |v|.
"""
import json

import numpy as np
import torch

from . import data

LAYERS = [17, 20, 23, 26]
STRENGTHS = [1, 2, 4, 6, 8]


def sweep_cells(layers=LAYERS):
    cells = [{"kind": "base"}, {"kind": "prompt", "axis": "IB"}, {"kind": "prompt", "axis": "IH"}]
    for L in layers:
        for s in STRENGTHS:
            cells += [{"kind": "steer", "axis": a, "mode": m, "layer": L, "s": s}
                      for a in ("IB", "IH") for m in ("add", "pin")]
            cells.append({"kind": "steer", "axis": "rand", "mode": "add", "layer": L, "s": s})
    return cells


def round2_cells():
    """Opposite direction, the agreement direction, and the IB-but-not-IH direction."""
    cells = [{"kind": "base"}] + [{"kind": "prompt", "axis": a} for a in ("IB", "IH", "IB_notIH")]
    for s in (-8, -4, -2, -1):
        cells += [{"kind": "steer", "axis": "IB", "mode": m, "layer": 23, "s": s} for m in ("add", "pin")]
        cells += [{"kind": "steer", "axis": "IH", "mode": "pin", "layer": 17, "s": s},
                  {"kind": "steer", "axis": "IH", "mode": "add", "layer": 23, "s": s}]
    for s in (-4, -2, -1, 1, 2, 4):
        cells += [{"kind": "steer", "axis": "agree", "mode": m, "layer": 23, "s": s} for m in ("add", "pin")]
    for s in (1, 2, 4):
        cells += [{"kind": "steer", "axis": "IB_notIH", "mode": m, "layer": 23, "s": s} for m in ("add", "pin")]
    return cells


def round3_cells():
    """Kindness and cruelty directions, and IB and IH with the other projected out."""
    cells = [{"kind": "base"}] + [{"kind": "prompt", "axis": a} for a in ("kind", "cruel")]
    for a in ("kind", "cruel"):
        for s in (1, 2, 4):
            cells += [{"kind": "steer", "axis": a, "mode": m, "layer": 23, "s": s} for m in ("add", "pin")]
    for a in ("IB_orth", "IH_orth"):
        for s in (-4, -2, 1, 2, 4, 8):
            cells += [{"kind": "steer", "axis": a, "mode": m, "layer": 23, "s": s} for m in ("add", "pin")]
    return cells


def file_cells(path):
    return json.load(open(path))


def direction(axis, Z, L):
    """The direction vector and the baseline mean at layer L.

    "X-Y-Z" is X with Y and then Z projected out (Gram-Schmidt); *_orth removes the other axis.
    """
    if "-" in axis:
        parts = axis.split("-")
        v, mu = direction(parts[0], Z, L)
        basis = []
        for p in parts[1:]:
            w, _ = direction(p, Z, L)
            for b in basis:
                w = w - (w @ b) * b
            basis.append(w / np.linalg.norm(w))
        for b in basis:
            v = v - (v @ b) * b
        return v, mu
    if axis.endswith("_orth"):
        a, b = axis[:-5], {"IB": "IH", "IH": "IB"}[axis[:-5]]
        v, w = Z[f"{a}|v"][L], Z[f"{b}|v"][L]
        return v - (v @ w) / (w @ w) * w, Z[f"{a}|mu"][L]
    return Z[f"{axis}|v"][L], Z[f"{axis}|mu"][L]


def name(c):
    if c["kind"] == "steer2":
        return "+".join(f"{t['axis']}|L{t['layer']}|{t['s']:g}" for t in c["terms"])
    if c["kind"] != "steer":
        return c["kind"] + ("|" + c["axis"] if "axis" in c else "")
    return f"{c['mode']}|{c['axis']}|L{c['layer']}|{c['s']:g}"


def system(c, model=None):
    return data.system(c["axis"] if c["kind"] == "prompt" else None, model)


def hooks(c, Z, dev):
    """A steer2 cell adds several directions; terms at the same layer are summed."""
    if c["kind"] == "steer2":
        fns = {}
        for t in c["terms"]:
            f = hooks({"kind": "steer", "mode": "add", **t}, Z, dev)[t["layer"]]
            g = fns.get(t["layer"])
            fns[t["layer"]] = (lambda h, f=f, g=g: f(h) + g(h) - h) if g else f
        return fns
    if c["kind"] != "steer":
        return {}
    L, s = c["layer"], c["s"]
    t = lambda x: torch.tensor(x, dtype=torch.float32, device=dev)
    if c["axis"] == "rand":
        r = np.random.default_rng(L).standard_normal(Z["IB|v"].shape[1])
        v = t(r / np.linalg.norm(r) * np.linalg.norm(Z["IB|v"][L]))
        return {L: lambda h: h + s * v}
    v, mu = direction(c["axis"], Z, L)
    d = float(np.linalg.norm(v))
    if c["mode"] == "add":
        v = t(v)
        return {L: lambda h: h + s * v}
    u = t(v / d)
    goal = float(mu @ (v / d)) + s * d
    return {L: lambda h: h + (goal - h @ u).unsqueeze(-1) * u}
