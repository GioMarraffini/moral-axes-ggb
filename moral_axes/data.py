"""Statements, instructions, answer options and prompt formats."""
import glob
import json
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "data" / "ggb"

LABELS = ["Strongly Disagree", "Disagree", "Slightly Disagree", "Neutral",
          "Slightly Agree", "Agree", "Strongly Agree"]
DIGITS = [str(k) for k in range(1, 8)]
# instruction -> (answer strings, agreement value 1..7 of each)
OPTIONS = {
    "only_text": (LABELS, list(range(1, 8))),
    "inverted_only_text": (LABELS[:3] + ["Neither Agree nor Disagree"] + LABELS[4:],
                           list(range(1, 8))),
    "likert_scale": (DIGITS, list(range(1, 8))),
    "inverted_numbers_likert_scale": (DIGITS, list(range(7, 0, -1))),
    "inverted_agreement_likert_scale": (DIGITS, list(range(7, 0, -1))),
    "inverted_agreement_and_numbers_likert_scale": (DIGITS, list(range(1, 8))),
}
N_NEUTRAL_TRAIN = 10


def instructions():
    return json.load(open(D / "instructions.json"))


def system(axis=None):
    """The model's default system prompt, followed by the IB or IH prompt when an axis is given."""
    p = json.load(open(D / "system_prompts.json"))
    return p["default"] if axis is None else p["default"] + "\n\n" + p[axis]


def statements(split=None):
    """Benchmark and OUS statements plus the three control sets, as one list of rows."""
    rows = json.load(open(D / "statements.json"))
    for name, items in json.load(open(D / "controls.json")).items():
        for i, s in enumerate(items):
            sp = "train" if name == "neutral" and i < N_NEUTRAL_TRAIN else "test"
            rows.append({"id": f"{name}{i:02d}", "type": name, "source": "control",
                         "split": sp, "statement": s})
    return [r for r in rows if split is None or r["split"] == split]


def chat(system, user):
    return (f"<|im_start|>system\n{system}<|im_end|>\n"
            f"<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n")


def rate_prompt(system, instruction, statement):
    return chat(system, f"{instruction}\n\nStatement: {statement}\n\nReply with the option only.")


def cot_prompt(system, instruction, statement):
    return chat(system, f"{instruction}\n\nStatement: {statement}\n\nFirst copy the statement, "
                "then reason about how much you agree with it, and only then give your answer.")


def judged(files, judge):
    """Answer rows of one run with their judged rating in column r (NaN if not judged).

    Verdicts are keyed by uid, which is unique only within a run, so each run is paired
    with its own judge folder.
    """
    import pandas as pd
    v = {}
    for f in glob.glob(judge + "/*.json"):
        v.update(json.load(open(f)))
    df = pd.concat(pd.read_json(f, lines=True) for f in sorted(glob.glob(files)))
    df["r"] = df.uid.map(v)
    return df
