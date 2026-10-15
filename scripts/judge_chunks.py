"""Split generated answers into shuffled chunks for the rating judges.

Each chunk is a JSON list of {uid, instruction, response}. A judge writes
verdict_NNN.json next to chunk_NNN.json as {uid: rating}, rating 1..7 or 0 for no answer.
"""
import argparse
import glob
import json
import random
from pathlib import Path

from moral_axes import data

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--out", required=True)
ap.add_argument("--size", type=int, default=100)
args = ap.parse_args()

instr = data.instructions()
rows = [json.loads(l) for g in args.files for f in sorted(glob.glob(g)) for l in open(f)]
random.Random(0).shuffle(rows)
out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
for n, b in enumerate(range(0, len(rows), args.size)):
    chunk = [{"uid": r["uid"], "instruction": instr[r["instruction"]], "response": r["response"]}
             for r in rows[b:b + args.size]]
    json.dump(chunk, open(out / f"chunk_{n:03d}.json", "w"), indent=1)
print(len(rows), "answers,", n + 1, "chunks")
