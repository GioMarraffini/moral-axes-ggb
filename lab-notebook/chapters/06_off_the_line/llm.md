# 6. Answer-built directions: full protocol

## Directions

`scripts/directions_resp.py --responses "$W/prompt_check3/*.jsonl" --judge
$S/results/judge_all --out $W/directions_resp` (`cluster/directions_resp.sbatch`, one GPU,
excludes margpu021 and pascal; the same job then merges `directions2/directions.npz` and
`directions_resp/directions.npz` into `directions_resp/merged.npz` so the IB_notIH, agree
and prompt directions are available to the same cells).

Input rows: `cell == "base"`, `split == "train"`, the four kept wordings, judged rating > 0:
IB 1,000 answers (25 statements x 4 wordings x 10 iterations), IH 800. Activations:
`response_means` (mean over response tokens, every block output) on the answer rebuilt with
`data.cot_prompt(data.system(None), ...)`. `IBacc|v = mean(rating >= 5) - mean(rating <=
3)` (756 vs 94 answers), `IHacc|v` (83 vs 553), `{axis}acc|mu` = mean of all that axis's
answers, `both|v = IBacc|v + IHacc|v`, `both|mu` = average of the two mu.

`results/directions_resp/geometry.json`: cos(IBacc, IHacc) 0.15 / 0.18 / 0.19 / 0.20 at
layers 17 / 20 / 23 / 26; norms at 23: IBacc 3.74, IHacc 3.82. Against `directions2`
vectors at layer 23: cos(IHacc, IH) 0.20, cos(IHacc, IB) 0.02, cos(IHacc, agree) 0.10,
cos(IBacc, IB) 0.28, cos(IBacc, IH) 0.06, cos(IBacc, agree) 0.19, cos(both, agree) 0.19.

## Cells

`results/offline_cells.json`: `add|IHacc|L23|{2,4,8}`, `add|IBacc|L23|{2,4}`,
`add|both|L23|{2,4,8}`, `add|IB_notIH|L23|{-4,4,8,12}`. Strength in units of each vector's
own norm. `cluster/offline.sbatch`: `generate.py --directions directions_resp/merged.npz
--cells offline_cells.json --split test --iterations 3 --instructions <4 wordings> --shard
i/16`, 16 tasks (margpu020 and 021 excluded), 7,776 answers, `results/offline/`. Judge on
the Scaleway H100 as in chapter 5 (`results/offline/judge`, 78 chunks, verdicts in
`results/judge_offline/`), model cache deleted afterwards.

Fast-readout controls: `results/round4_cells.json` (`base`, IHacc 2/4/8, IBacc 2/4, both
2/4/8), `cluster/sweep4.sbatch` (`sweep.py --cells <json path>`; `sweep.py` now accepts a
cell file path), output `results/sweep4.csv`.

## Results

Chain of thought (IB / IH, test statements): see the table in `human.md`; full list with
every earlier cell in `results/targets.csv` (regenerate with the `targets.py` command of
chapter 5 plus `'results/offline/*.jsonl'` and `results/judge_offline`).

Fast readout (IB / IH / neutral / harm / kindness): base 5.12 / 2.90 / 4.57 / 2.03 / 6.03;
IHacc 2: 5.33 / 3.28 / 4.58 / 2.05 / 5.77; IHacc 4: 5.50 / 3.60 / 4.71 / 2.23 / 5.65;
IHacc 8: 5.49 / 4.46 / 5.02 / 3.14 / 5.55; IBacc 2: 6.21 / 3.48 / 4.91 / 2.47 / 6.21;
IBacc 4: 6.39 / 4.91 / 5.28 / 2.85 / 6.27; both 2: 6.06 / 3.94 / 4.89 / 2.57 / 6.01;
both 4: 6.05 / 5.49 / 5.20 / 3.08 / 6.01; both 8: 5.77 / 5.55 / 5.65 / 5.34 / 5.81.

Equivalence (strict reading, margin 0.5): no match. Closest: rule utilitarianism
`add|IHacc|L23|8` d = 0.23 (p = 0.36); act utilitarianism `add|both|L23|8` d = 0.65
(p = 0.63), `add|both|L23|4` d = 0.70; non-utilitarian consequentialism `add|IB|L23|-8`
d = 0.16, `add|IB_notIH|L23|12` d = 0.38; lay population `prompt|IH` d = 0.66,
`add|IB_notIH|L23|12` d = 0.96.

Figure: `scripts/figures.py` section 8 (triangles) -> `05_reachable_plane.png`.
