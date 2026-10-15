# 7. Two-axis grid: full protocol

## Rejecting answers for the IB contrast

`results/genrej_cells.json` = `[pin|IB|L23|-4]`, `cluster/genrej.sbatch`: `generate.py
--directions directions2/directions.npz --split train --iterations 5 --instructions <4
wordings> --shard i/4`, 900 answers (45 train statements x 4 x 5), `results/genrej/`.
Judged on the cluster (`cluster/judge.sbatch $W/genrej/judge`, 9 chunks; verdicts
`results/judge_genrej/`). The first attempt on the H100 failed with "No space left on
device" during the model download because another job was writing to the same disk; the
partial cache was deleted.

## Directions

`cluster/directions_resp2.sbatch`: `directions_resp.py --responses prompt_check3/*.jsonl
genrej/*.jsonl --judge judge_all judge_genrej --cells "base,pin|IB|L23|-4" --out
directions_resp2`, then merged with `directions2/directions.npz` into
`directions_resp2/merged.npz`. Activations always from the unsteered model on the answer
text. Counts: IB 1,500 answers, 1,109 rated >= 5, 107 rated <= 3; IH 1,200 answers, 198 vs
684. cos(IBacc, IHacc) 0.25 / 0.25 / 0.18 / 0.19 at layers 17 / 20 / 23 / 26.

## Grid

`results/grid2_cells.json`: `base` and the 24 other combinations of a, b in {−4, −2, 0, 2,
4} (a = IBacc strength, b = IHacc strength, in units of each vector's norm, both added at
layer 23; single-term cells are plain `add` cells). `cluster/grid2.sbatch` (16 tasks,
`--iterations 3`, four wordings, test split): 16,200 answers in `results/grid2/`. Judge on
the cluster, 162 chunks (`results/judge_grid2/`). Controls: `cluster/sweep5.sbatch` ->
`results/sweep5.csv`.

Chain-of-thought means (a, b: IB / IH):

| a \ b | −4 | −2 | 0 | 2 | 4 |
|---|---|---|---|---|---|
| −4 | 1.51 / 1.05 | 2.56 / 1.13 | 3.72 / 1.87 | 4.30 / 3.00 | 4.63 / 3.93 |
| −2 | 1.73 / 1.08 | 3.29 / 1.28 | 4.26 / 2.36 | 4.63 / 3.45 | 4.91 / 4.23 |
| 0 | 3.67 / 1.08 | 5.07 / 1.47 | 5.28 / 2.93 | 5.25 / 3.98 | 5.18 / 4.57 |
| 2 | 6.08 / 1.23 | 6.39 / 1.89 | 6.05 / 3.63 | 5.62 / 4.51 | 5.37 / 4.84 |
| 4 | 6.83 / 1.99 | 6.81 / 2.55 | 6.34 / 4.56 | 5.89 / 5.22 | 5.59 / 5.10 |

Fast-readout controls over the 25 cells: neutral 3.57 to 5.31, harm_no_benefit 1.25 to
3.00, kindness 5.33 to 6.43, mass 1.0 everywhere (`results/sweep5.csv`).

## Fit and inversion

`scripts/fit_plane.py 'results/grid2/*.jsonl' --judge results/judge_grid2 --out
results/target_cells.json`: quadratic surface `[1, a, b, a², b², ab]` per scale by least
squares (IB r = 0.976, rmse 0.31; IH r = 0.973, rmse 0.33); per target, the (a, b) in
[−4, 4]² minimising the squared distance (L-BFGS-B from five starts):

| target | a | b | predicted IB / IH | residual |
|---|---|---|---|---|
| act utilitarianism | 4.0 | 4.0 | 5.36 / 5.76 | 0.41 |
| rule utilitarianism | 0.9 | 4.0 | 5.17 / 4.77 | 0.37 |
| non-utilitarian consequentialism | −1.7 | 4.0 | 4.97 / 4.17 | 0.59 |
| virtue ethics | −4.0 | 1.7 | 4.17 / 2.92 | 0.86 |
| other deontology | −4.0 | 1.2 | 3.99 / 2.72 | 0.90 |
| Kantian ethics | −4.0 | −1.1 | 2.94 / 1.79 | 0.17 |
| lay population | −4.0 | 1.6 | 4.14 / 2.88 | 0.65 |

`results/target_cells.json` holds these seven plus five extension cells (a, b) = (−6, 2),
(−6, 3), (−6, 4), (−5, 2), (−5, 3). Confirmation: `cluster/target.sbatch` (`--iterations
5`, 16 tasks) and `cluster/sweep6.sbatch` (controls).

Figure: `scripts/figures.py` section 9 -> `07_grid_plane.png`.

## Confirmation

`cluster/target.sbatch`: 12 cells x 54 statements x 4 wordings x 5 iterations = 12,960
answers in `results/target/`; judged on the cluster (130 chunks, `results/judge_target/`);
controls `cluster/sweep6.sbatch` -> `results/sweep6.csv` (the first submission died on
margpu020/021, the invisible-GPU nodes, now excluded in every sweep file).

Chain of thought (IB / IH): (4, 4) 5.53 / 5.09; (0.9, 4) 5.29 / 4.67; (−1.7, 4)
4.92 / 4.19; (−4, 1.7) 4.28 / 2.86; (−4, 1.6) 4.20 / 2.80; (−4, 1.2) 4.11 / 2.59;
(−4, −1.1) 3.15 / 1.34; (−5, 2) 4.07 / 2.86; (−5, 3) 4.40 / 3.38; (−6, 2) 3.95 / 2.71;
(−6, 3) 4.25 / 3.22; (−6, 4) 4.46 / 3.64.

Fast-readout controls (neutral / harm / kindness): (4, 4) 5.05 / 3.00 / 5.93; (0.9, 4)
4.69 / 2.30 / 5.80; (−1.7, 4) 4.52 / 2.08 / 5.59; (−4, −1.1) 4.08 / 1.27 / 5.50;
(−6, 2) 3.93 / 1.27 / 5.02; (−6, 4) 4.23 / 1.61 / 5.12; mass 1.0 everywhere.

Equivalence (`scripts/targets.py`, margin 0.5): strict reading (`_spread_is:
standard_error`), no match; closest per group: act `IBacc 4 + IHacc 4` d 0.97; rule
`IBacc 0.9 + IHacc 4` d 0.51 (p 0.49) and, over all cells, `add|IHacc|L23|8` d 0.23
(p 0.36); non-utilitarian `IBacc −1.7 + IHacc 4` d 0.53; virtue `IBacc −6 + IHacc 3`
d 0.77; deontology `IBacc −6 + IHacc 2` d 0.87; Kantian `IBacc −4 + IHacc −1.1` d 0.66;
lay `IBacc −6 + IHacc 3` d 0.61. Lenient reading (`standard_deviation`): no confirmation
cell matches; `results/targets_lenient.csv`. All cells of every chain-of-thought run:
`results/targets.csv`.
