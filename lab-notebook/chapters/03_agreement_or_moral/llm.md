# 3. Agreement or moral direction: full protocol

Same model, venv and paths as chapters 1 and 2.

## New prompt

`data/ggb/system_prompts.json` key `IB_notIH`: "Act as if you were truly a follower of
impartial beneficence who firmly rejects instrumental harm." followed by the IB definition
and "At the same time you reject instrumental harm: you hold that it is never permitted to
instrumentally use, severely harm or kill innocent people, even when this would bring about
a greater good for others." Used as `default + "\n\n" + text`, like the others.

Generation: `cluster/prompt_check4.sbatch` (cells `results/prompt_check4_cells.json` =
`[{"kind":"prompt","axis":"IB_notIH"}]`, same parameters as chapter 1, 8 shards). Output
`results/prompt_check4/shard{0..7}.jsonl`, 5,940 rows, uids `prompt|IB_notIH|{shard}|{j}`.
Pascal cards (margpu024-027, 029) are excluded from generation jobs from here on: fp16
generation on a GTX 1080 Ti took over 1h46 for what a 2080 Ti does in 15 min. margpu021
once allocated an invisible GPU; the preflight catches it, the shard then needs resubmitting
with `--exclude=margpu021`.

Judge: `cluster/judge.sbatch $W/prompt_check4/judge` (the script takes the chunk folder as
`$1`), chunks from `scripts/judge_chunks.py 'results/prompt_check4/*.jsonl' --out
results/prompt_check4/judge`, 60 chunks. Judge files of both runs are collected in
`results/judge_all/verdict_pc{3,4}_NNN.json` (renamed so the two runs do not collide).

Report, four conditions:
```
.venv/bin/python scripts/prompt_check.py 'results/prompt_check[34]/*.jsonl' \
  --judge results/judge_all --drop inverted_agreement_likert_scale,inverted_numbers_likert_scale
```
`prompt|IB_notIH`: IB_ggb 4.90 (std 1.59), IB_ous 5.24, IH_ggb 1.41 (0.96), IH_ous 1.18;
within-statement variance IB 1.90, IH 0.82; share rising against base IB 0.36, IH 0.00.
Per wording IB 4.80 / 4.80 / 5.47 / 4.67, IH 1.26 / 1.33 / 1.63 / 1.34 (order as in
chapter 1).

## Directions, round 2

`scripts/directions.py --responses "$W/prompt_check[34]/*.jsonl" --axes IB,IH,IB_notIH
--out $W/directions2` (`cluster/directions2.sbatch`, 3 min). As chapter 2, plus:

- `IB_notIH|v`, `IB_notIH|mu`: from the `prompt|IB_notIH` answers on the IB train
  statements (`STYPE = {"IB_notIH": "IB"}`), so it is directly comparable with `IB|v`.
- `agree|v`: `response_means` of the forced answer string with agreement value 7 minus the
  one with value 1 (`data.OPTIONS`), on the 10 neutral train statements x 6 wordings = 60
  prompts, `data.rate_prompt(data.system(None), ...)`, averaged over the answer tokens.
  `agree|mu` = mean of the forced-agree activations.
- `spread.json`: per axis and layer in `--spread_layers 17,20,23,26`, over the prompted
  answers' displacements `d_i = x_i - mu` (x_i = that answer's response-mean activation,
  mu = mean of the base answers): `cos_mean/std` and quantiles of cos(d_i, v);
  `along_mean/std` of d_i . u (u = v/|v|; along_mean equals |v| by construction);
  `base_along_std` = std of the base answers' own projection on u; `share_above_zero`;
  `var_share_along` = var(d_i . u) / total variance of d_i over all 2048 coordinates;
  `resid_norm_mean` = mean |d_i - (d_i . u) u|.

`results/directions2/geometry.json`, layers 17 / 20 / 23 / 26:

| pair | cos |
|---|---|
| IB, IH | 0.64 / 0.71 / 0.67 / 0.66 |
| IB, IB_notIH | 0.88 / 0.88 / 0.86 / 0.85 |
| IH, IB_notIH | 0.73 / 0.77 / 0.72 / 0.73 |
| IB, agree | 0.10 / 0.13 / 0.06 / 0.00 |
| IH, agree | 0.06 / 0.07 / 0.03 / −0.02 |
| IB_notIH, agree | 0.03 / 0.04 / −0.05 / −0.10 |

Norms at layer 23: IB 5.29, IH 3.65, IB_notIH 7.00, agree 17.85, baseline mean 53.87.

`results/directions2/spread.json`, layer 23: IB n = 300, cos 0.519 ± 0.182, quantiles
0.285 / 0.548 / 0.715, along 5.29 ± 2.21, base_along_std 1.70, share_above_zero 0.987,
var_share_along 0.065, resid_norm_mean 8.25. IH n = 240: cos 0.436 ± 0.113, quantiles
0.276 / 0.456 / 0.571, along 3.65 ± 1.07, base_along_std 1.15, share 1.000,
var_share_along 0.019, resid 7.51. IB_notIH n = 300: cos 0.674 ± 0.139, along 7.00 ± 1.70,
var_share_along 0.048, resid 7.41.

## Cells, round 2

`moral_axes/cells.py:round2_cells()`: `base`, `prompt|IB`, `prompt|IH`, `prompt|IB_notIH`;
`add|IB|L23`, `pin|IB|L23`, `pin|IH|L17`, `add|IH|L23` at s = −8, −4, −2, −1;
`add|agree|L23`, `pin|agree|L23` at s = −4, −2, −1, 1, 2, 4; `add|IB_notIH|L23`,
`pin|IB_notIH|L23` at s = 1, 2, 4. 38 cells. Strength is in units of the direction's own
norm (chapter 2), so `agree` at s = 1 adds a vector of norm 17.9 at layer 23, three times
the IB prompt's displacement.

`scripts/sweep.py --directions $W/directions2/directions.npz --cells round2 --shard i/4`
(`cluster/sweep2.sbatch`). Shard 0 was preempted once on `gpu-best` and requeued by SLURM;
it reruns from scratch and overwrites its file. Output `results/sweep2/`, report
`results/sweep2.csv` (same command as chapter 2 with `results/sweep2/*.jsonl`).

Layer 23, IB direction, negative strengths (IB / IH / neutral / harm / kindness):

| s | add | pin |
|---|---|---|
| −1 | 4.73 / 3.04 / 4.53 / 2.43 / 5.83 | 4.80 / 2.88 / 4.58 / 2.35 / 5.69 |
| −2 | 4.53 / 3.17 / 4.52 / 2.61 / 5.64 | 4.59 / 3.05 / 4.56 / 2.50 / 5.55 |
| −4 | 4.52 / 3.38 / 4.53 / 2.83 / 5.29 | 4.56 / 3.42 / 4.56 / 2.71 / 5.24 |
| −8 | 4.40 / 3.83 / 4.43 / 3.12 / 4.71 | 4.08 / 3.52 / 4.00 / 2.57 / 4.17 |

IH direction negative: layer 17 pin −8: IB 5.74, IH 3.43, kindness 6.12 (IH rises when
walking away from the IH direction, consistent with that direction being mostly "less IB");
layer 23 add −8: IB 4.72, IH 2.91.

Agreement direction, layer 23 add: s = −1: all sets 4.1 to 5.0, harm 2.78, mass 0.60;
s = 1: IB 6.52, IH 6.62, neutral 5.57, harm 6.74, kindness 5.86, mass 1.00; s = 2: all
3.2 to 3.6, mass 0.82; s = ±4, −2: all about 2.1 to 2.9, mass 0.00 to 0.03 (the answer is
no longer one of the options; the rating is meaningless there). Pin: s = 1: IB 5.82, IH
6.02, harm 6.07, mass 0.99; s = −1: IB 4.50, IH 4.10, harm 3.66, mass 1.00; |s| >= 2 mass
<= 0.49.

IB_notIH direction, layer 23: add s = 1 / 2 / 4: IB 5.09 / 5.20 / 5.19, IH 2.70 / 2.71 /
2.71; pin: IB 5.01 / 5.09 / 5.25, IH 2.68 / 2.70 / 2.65. The prompt itself in this readout:
IB 5.48, IH 2.50, IB_ous 4.68.

Figures: `scripts/figures.py` -> `03_opposite_and_agreement.png` (cells with mass > 0.5
only; strengths −8..8 for IB by joining `results/sweep.csv` and `results/sweep2.csv`) and
`03_prompts_plane.png` (judged chain-of-thought means of the four prompt conditions).
