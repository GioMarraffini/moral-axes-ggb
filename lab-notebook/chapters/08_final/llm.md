# 8. Final run: full protocol

## Checks

Hook point: `moral_axes/model.py` stores `hidden_states[1:]`, so index L = output of
`model.model.layers[L]`; `steer()` hooks `layers[L].register_forward_hook`. Verified on
Qwen2.5-0.5B at L = 14: hook output == `hidden_states[15]` == `response_means[:, 14]`
(allclose, atol 1e-4). Note manifold-persona's `steer_pin.py` hooks `layers[L]` with
vectors from `hidden_states[L]`, one block earlier than its extraction point; its "L23" is
not this repo's L23.

Balanced IB contrast: `results/genrej2/` (900 answers on train statements under
`add|IBacc|L23|-4`, `cluster/genrej2.sbatch`, judged on the cluster + H100),
`directions_resp.py --cells "base,add|IBacc|L23|-4"` -> `results/directions_resp3/`:
IB 901 accepting vs 275 rejecting, IH 86 vs 908; cos(IBacc, IHacc) 0.39 / 0.40 / 0.31 /
0.26 at layers 17 / 20 / 23 / 26; cos with the directions in use at L23: IBacc 0.89, IHacc
0.74. Not used for steering.

Extended grid: `results/grid3_cells.json` (a in {−6, −8, −10} x b in {2, 4, 6} at L23;
(−4, 2), (0, 4), (2, 2) at L17, L20, L26), `cluster/grid3.sbatch`, 3 iterations, judged
(`results/judge_grid3/`), fast controls `results/sweep7.csv`. L23 chain of thought (IB /
IH): (−6, 2) 3.91 / 2.61, (−6, 4) 4.47 / 3.50, (−6, 6) 4.62 / 4.19, (−8, 2) 3.41 / 2.36,
(−8, 4) 3.75 / 3.17, (−8, 6) 4.15 / 3.62, (−10, 2) 2.24 / 1.55, (−10, 4) 2.66 / 2.17,
(−10, 6) 3.16 / 2.67. Other layers move less than L23 at the same settings (L17 (0, 4):
5.28 / 4.02; L20: 5.56 / 4.61; L26: 5.15 / 3.98 against L23 5.18 / 4.57). Fast controls at
a <= −8: neutral 2.8 to 4.1, kindness 3.7 to 4.9.

## Final cells

`results/final_cells.json`: `base`; (−8, 4), (−8, 5), (−9, 4), (−10, 4), (−10, 3), (−6, 6),
(−5, 5), (0, 5), (0, 8), (4, 4), (4, 6), (8, 8), all at L23, directions
`directions_resp2/merged.npz`. Moral statements: `cluster/final.sbatch` (`--iterations
10`, 16 tasks, 25,920 answers, `results/final/`). Controls: run on the H100
(`generate.py --types neutral,harm_no_benefit,kindness --iterations 3 --bs 64 --dtype
bf16`, 9,960 answers, `results/final_ctrl/shard0.jsonl`; the H100 venv is
`/root/mp/.venv`, HF cache `/scratch/hf_cache`). Judge: H100, 359 chunks, 11 s per chunk,
`results/judge_final/`; 5 answers coded 0.

`scripts/targets.py 'results/final/*.jsonl' --judge results/judge_final --csv
results/targets_final.csv` (strict spreads for the philosopher groups, SD for the lay
population). Matches at margin 0.5: `IBacc −8 + IHacc 4` with lay population (IB 3.747,
IH 3.128, d 0.206, p_IB < 0.001, p_IH 0.002) and `IBacc −8 + IHacc 5` (3.961 / 3.441,
d 0.337, p 0.022 / 0.001). Closest otherwise: Kantian (−10, 4) d 0.20 p 0.24; non-util.
(−6, 6) d 0.35 p 0.23; rule (0, 8) d 0.28 p 0.38; virtue (−8, 4) d 0.42; deontology (−8, 4)
d 0.46; act (4, 4) d 0.97.

Chain-of-thought means (IB / IH / neutral / harm / kindness): base 5.20 / 2.88 / 4.22 /
1.58 / 6.30; (−10, 3) 2.53 / 1.87 / 2.68 / 1.57 / 4.08; (−10, 4) 2.81 / 2.14 / 2.69 / 1.85 /
4.15; (−9, 4) 3.32 / 2.71 / 3.13 / 2.11 / 4.60; (−8, 4) 3.75 / 3.13 / 3.70 / 2.34 / 4.92;
(−8, 5) 3.96 / 3.44 / 3.84 / 2.78 / 4.95; (−6, 6) 4.68 / 4.16 / 4.38 / 3.23 / 5.21; (−5, 5)
4.70 / 4.09 / 4.40 / 3.14 / 5.14; (0, 5) 5.14 / 4.67 / 4.82 / 3.72 / 5.37; (0, 8) 5.09 /
4.81 / 4.93 / 4.26 / 5.28; (4, 4) 5.50 / 5.09 / 5.22 / 4.05 / 5.68; (4, 6) 5.30 / 5.00 /
5.08 / 4.40 / 5.42; (8, 8) 5.13 / 4.97 / 4.97 / 4.83 / 5.23.

Within-statement variance (IB / IH): base 1.04 / 1.83; steered cells 0.31 to 1.49 / 0.28 to
1.09 (lowest at (4, 4), (4, 6), (0, 5)).

Figure: `scripts/figures.py` section 10 -> `08_final_cells.png`.
