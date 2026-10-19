"""Write the first-round grid cells for a model: a, b in {-4, -2, 0, 2, 4} at the given layers."""
import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("--layers", required=True, help="comma separated block indices")
ap.add_argument("--strengths", default="-4,-2,0,2,4")
ap.add_argument("--mode", default="add", choices=["add", "aff"])
ap.add_argument("--out", required=True)
args = ap.parse_args()

S = [float(x) for x in args.strengths.split(",")]
S = [int(x) if x == int(x) else x for x in S]
suffix = {"add": "acc", "aff": "aff"}[args.mode]
cells = [{"kind": "base"}]
for L in (int(x) for x in args.layers.split(",")):
    for a in S:
        for b in S:
            terms = [t for t in ({"axis": "IB" + suffix, "layer": L, "s": a}, {"axis": "IH" + suffix, "layer": L, "s": b}) if t["s"]]
            if len(terms) == 2:
                cells.append({"kind": "steer2", "terms": terms})
            elif len(terms) == 1:
                t = terms[0]
                cells.append({"kind": "steer", "axis": t["axis"], "mode": args.mode, "layer": L, "s": t["s"]})
json.dump(cells, open(args.out, "w"), indent=0)
print(len(cells), "cells")
