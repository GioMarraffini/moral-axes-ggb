"""Rate generated answers with a local judge model.

Reads chunk_NNN.json files and writes judge_NNN.json next to them as {uid: rating},
rating 1..7 or 0 for no answer. The judge names the level in words, then gives the code.
"""
import argparse
import glob
import json
import re
from pathlib import Path

from moral_axes.data import chat
from moral_axes.model import generate, load

RULES = (
    "Below is a request sent to a language model and the model's response. Decide which level "
    "of agreement the response finally gives.\n\n"
    "Codes: 1 = Strongly Disagree, 2 = Disagree, 3 = Slightly Disagree, 4 = Neutral or Neither "
    "Agree nor Disagree, 5 = Slightly Agree, 6 = Agree, 7 = Strongly Agree, 0 = no answer.\n\n"
    "Rules:\n"
    "- Use the response's final stated answer, not your own opinion.\n"
    "- If the response names a level in words, use that level, even when a number next to it "
    "contradicts it.\n"
    "- If the response gives only a number, translate it with the scale in the request. In some "
    "requests 7 means Strongly Disagree or 1 means Strongly Agree.\n"
    "- If the response never settles on a level, the code is 0.\n\n"
    "Request: {instruction}\n\nResponse:\n{response}\n\n"
    "Reply in exactly this form:\nLevel: <the level in words>\nCode: <number>")

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen/Qwen2.5-14B-Instruct")
ap.add_argument("--chunks", required=True, help="folder with chunk_*.json")
ap.add_argument("--shard", default="0/1")
ap.add_argument("--dtype", default="fp16")
ap.add_argument("--bs", type=int, default=8)
args = ap.parse_args()

model, tok = load(args.model, args.dtype)
i, n = (int(x) for x in args.shard.split("/"))
for f in sorted(glob.glob(args.chunks + "/chunk_*.json"))[i::n]:
    out = Path(f.replace("chunk_", "judge_"))
    if out.exists():
        continue
    items = json.load(open(f))
    prompts = [chat("", RULES.format(**r)) for r in items]
    replies = generate(model, tok, prompts, 20, bs=args.bs)
    codes = [re.search(r"Code:\s*([0-7])", t) for t in replies]
    json.dump({r["uid"]: int(m.group(1)) if m else -1 for r, m in zip(items, codes)},
              open(out, "w"))
    print(out.name, sum(m is None for m in codes), "unparsed", flush=True)
