# 5. Reachable plane: full protocol

## Targets

`data/ggb/targets.json`: IB, IB_sd, IH, IH_sd, N per group, converted from the plotting
code's pixel values (`(198 + px) / 198`, spread `px_diff / 198`). The plotted spread is
recorded as read and declared a standard error (`_spread_is`), the stricter choice;
`scripts/targets.py` multiplies it by sqrt(N) to get the group standard deviation. Lay population: Kahane et al. 2018, N = 300, sd 1.20 / 1.22.

## Cells

`results/grid_cells.json`, directions from `results/directions3/directions.npz`:
`add|IH_orth|L23|{-8,-4,4,8}`, `add|IB_orth|L23|{-4,-2,2,4}`, `add|IB|L23|{-8,-2,4}`, and
`steer2` cells `IB_orth|L23|a+IH_orth|L23|b` for a in (−2, 2, 4), b in (−4, 4, 8).
`moral_axes/cells.py`: a `steer2` cell has `terms`, each an additive direction; terms at
the same layer are summed in one hook. Orthogonalisation as in chapter 4.

## Generation and judging

`cluster/grid.sbatch`: `generate.py --directions directions3.npz --cells grid_cells.json
--split test --iterations 3 --instructions <4 kept wordings> --shard i/16`, 16 tasks,
810 answers each, about 20 min on a 2080 Ti. Shard 15 landed on margpu020 (invisible GPU,
like margpu021) and was rerun with that node excluded. 12,960 answers in
`results/grid/shard{0..15}.jsonl`.

Judge: chunks `results/grid/judge` (122, from shards 0 to 14) and `results/grid/judge2` (8,
shard 15). The cluster's large cards were all taken, so the judge ran on the Scaleway H100
(`root@51.159.142.179:/root/moral-axes-ggb`, venv `/root/mp/.venv`, torch 2.13 cu126):
`PYTHONPATH=. /root/mp/.venv/bin/python scripts/judge.py --chunks results/grid/judge
--dtype bf16 --bs 16`, about 12 minutes for 130 chunks. The model cache was deleted
afterwards (the disk had 32 GB free; the 14B weights are 28 GB). Verdicts collected in
`results/judge_grid/verdict_{judge,judge2}_NNN.json`.

## Equivalence test

```
PYTHONPATH=. .venv/bin/python scripts/targets.py \
  'results/prompt_check[34]/*.jsonl' 'results/confirm/*.jsonl' 'results/grid/*.jsonl' \
  --judge results/judge_all results/judge_confirm results/judge_grid --margin 0.5
```

`scripts/targets.py`: per cell, one value per statement (mean judged rating over wordings
and iterations, test split, four wordings); per group and scale, Welch two one-sided tests
of H0: |mean_model − mean_group| >= margin with Welch–Satterthwaite degrees of freedom; the
reported p is the larger of the two; a match needs p < 0.05 on both scales. Output
`results/targets.csv` (cell, target, IB, IH, dIB, dIH, dist, p_IB, p_IH, match).

## Results

Chain-of-thought means per condition (IB / IH), sorted by IH:

| cell | IB | IH |
|---|---|---|
| prompt IB_notIH | 4.98 | 1.42 |
| add IB_orth 2 | 6.10 | 1.82 |
| IB_orth 2 + IH_orth −4 | 6.67 | 1.84 |
| add IH_orth −8 | 6.44 | 1.91 |
| pin IB 2 | 6.30 | 2.03 |
| add IB_orth 4 | 6.87 | 2.06 |
| add IB 2 | 6.53 | 2.17 |
| add IH_orth −4 | 5.72 | 2.19 |
| IB_orth 4 + IH_orth 4 | 6.64 | 2.33 |
| prompt IB | 6.15 | 2.46 |
| IB_orth 4 + IH_orth 8 | 5.73 | 2.68 |
| IB_orth 2 + IH_orth 4 | 5.54 | 2.69 |
| prompt IH | 4.09 | 2.82 |
| base | 5.21 | 2.85 |
| IB_orth −2 + IH_orth −4 | 4.99 | 3.09 |
| IB_orth 4 + IH_orth −4 | 6.72 | 3.14 |
| add IH_orth 4 | 4.84 | 3.31 |
| IB_orth 2 + IH_orth 8 | 4.86 | 3.45 |
| add IB_orth −2 | 4.88 | 3.51 |
| add IB −2 | 4.93 | 3.58 |
| add IB 4 | 6.98 | 3.67 |
| add IH_orth 8 | 4.78 | 3.76 |
| IB_orth −2 + IH_orth 4 | 4.80 | 3.82 |
| add IB_orth −4 | 4.84 | 3.95 |
| pin IB −4 | 4.77 | 3.98 |
| IB_orth −2 + IH_orth 8 | 4.69 | 4.01 |
| add IB −8 | 4.55 | 4.29 |
| pin IH L17 8 | 5.81 | 4.64 |
| add agree 1 | 6.50 | 6.61 |

Equivalence at margin 0.5, strict reading: no match. Closest: non-utilitarian
consequentialism `add|IB|L23|-8` d = 0.16 (dIB +0.12, dIH −0.11, p = 0.125); rule
utilitarianism `add|IB|L23|-8` d = 0.63 (p = 0.54); lay population `prompt|IH` d = 0.66
(p = 0.50); act utilitarianism `add|agree|L23|1` d = 1.02; virtue `prompt|IH` d = 0.87;
other deontology `prompt|IH` d = 0.91; Kantian `prompt|IH` d = 1.51. Under the lenient
reading (plotted spread = standard deviation) the first one matches with p < 0.001 on both
scales.

Figure: `scripts/figures.py` section 8 -> `05_reachable_plane.png`.
