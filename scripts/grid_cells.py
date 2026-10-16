"""Write the first-round grid cells for a model: a, b in {-4, -2, 0, 2, 4} at the given layers."""
import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("--layers", required=True, help="comma separated block indices")
ap.add_argument("--strengths", default="-4,-2,0,2,4")
ap.add_argument("--out", required=True)
args = ap.parse_args()

S = [int(x) for x in args.strengths.split(",")]
cells = [{"kind": "base"}]
for L in (int(x) for x in args.layers.split(",")):
    for a in S:
        for b in S:
            terms = [t for t in ({"axis": "IBacc", "layer": L, "s": a}, {"axis": "IHacc", "layer": L, "s": b}) if t["s"]]
            if len(terms) == 2:
                cells.append({"kind": "steer2", "terms": terms})
            elif len(terms) == 1:
                t = terms[0]
                cells.append({"kind": "steer", "axis": t["axis"], "mode": "add", "layer": L, "s": t["s"]})
json.dump(cells, open(args.out, "w"), indent=0)
print(len(cells), "cells")
