# The pipeline, as it stands

Model-agnostic: every script takes `--model`. Defaults below are the ones used for
Qwen2.5-3B-Instruct. Code paths are relative to the repo root; `$W` is the output folder.

## 0. Data (once)

- `data/ggb/statements.json`: 90 benchmark + 9 OUS statements, split 45 train / 54 test
  (`scripts/make_split.py`, seed 0, OUS always test).
- `data/ggb/instructions.json`: six scale wordings. Four are used: `only_text`,
  `inverted_only_text`, `likert_scale`, `inverted_agreement_and_numbers_likert_scale`
  (the two where a higher number means more disagreement are dropped: the judge misreads
  them).
- `data/ggb/controls.json`: 20 neutral opinions, 20 harm with no benefit, 20 ordinary
  kindness (first 10 neutral are train, the rest test).
- `data/ggb/targets.json`: human group means (IB, IH, spread, N).

## 1. Unprompted answers on the train statements

```
scripts/generate.py --model M --cells '[{"kind":"base"}]' --split train --iterations 10 \
  --instructions <4 wordings> --temperature 0.5 --max_new_tokens 2000 --out $W/base_train/
```
Chain of thought, no length cap, the model's own default system prompt
(`data/ggb/system_prompts.json: default`).

## 2. Rate the answers

```
scripts/judge_chunks.py '$W/base_train/*.jsonl' --out $W/base_train/judge     # 100 per chunk
scripts/judge.py --chunks $W/base_train/judge --model Qwen/Qwen2.5-14B-Instruct --dtype bf16
```
Judge prompt in `scripts/judge.py:RULES`: the stated level in words wins over a number; a
bare number is read with the item's own scale; 0 = no answer. Verdicts `judge_NNN.json`
= `{uid: 1..7}`.

## 3. Directions from the model's own answers

```
scripts/directions_resp.py --model M --responses '$W/base_train/*.jsonl' --judge $W/base_train/judge \
  --cells base --out $W/directions
```
Per axis: mean response-token activation (every block output) of the train answers rated
5 to 7 minus those rated 1 to 3. Keys `IBacc|v`, `IHacc|v` (36 x d), `*|mu`.
`geometry.json` reports norms and cos(IBacc, IHacc).

## 4. Steer and answer (test statements and controls)

Cells: `{"kind":"steer2","terms":[{"axis":"IBacc","layer":L,"s":a},{"axis":"IHacc","layer":L,"s":b}]}`
added to the block-L output at every position, `s` in units of the direction's norm.
```
scripts/generate.py --model M --directions $W/directions/directions.npz --cells cells.json \
  --split test --types IB,IH --iterations 10 ...                  # scales
scripts/generate.py ... --types neutral,harm_no_benefit,kindness --iterations 3   # controls
```
Then step 2 on both outputs. Layer: the first run sweeps L in {0.5, 0.65, 0.75} of depth
with a 3-iteration grid a, b in {−4, −2, 0, 2, 4}; the layer is the one whose single-axis
cells move their own scale most with the smallest control shift (3B: 23 of 36; 7B: 18
of 28). A second round at that layer widens the strengths until the groups are inside
the grid (3B: a to −10, b to 8; 7B: a to −12, b to 8). On one H100 the whole chain is
`cluster/h100_next_model.sh MODEL TAG grid_cells.json` (steps 1 to 4, first round) and
`cluster/h100_grid.sh MODEL TAG cells.json SUBDIR` (any further grid).

## 5. Place the model

```
scripts/fit_plane.py '$W/grid/*.jsonl' --judge $W/grid/judge --layer L --out target_cells.json  # fit (a,b) per target
scripts/targets.py '$W/final/*.jsonl' --judge $W/final/judge --csv targets.csv          # equivalence test
scripts/report.py / scripts/figures.py                                                 # tables, figures
```
`targets.py`: per statement mean; two one-sided Welch tests per scale with margin 0.5; a
group counts as reached when both reject at 0.05; it also prints the distance in group
standard deviations.

## Compute (3B)

Generation: 16 x 11 GB cards, ~20 min per 16,000 answers. Judge: one 80 GB card, 11 s per
100 answers. Preflight in every sbatch: exit if no visible CUDA device, if the card has
under 10 GB (38 GB for the judge), or if the torch wheel lacks the card's architecture.
Nodes margpu020/021 allocate an invisible GPU and are excluded; pascal cards are excluded
for generation (fp16 is slow there).
