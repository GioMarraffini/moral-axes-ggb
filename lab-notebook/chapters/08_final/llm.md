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
`results/judge_final/`; 5 answers coded 0. The control file and the first moral shard
had colliding uids (`cell|shard|index` without the statement type), so both were
re-judged with unique uids (`results/final_ctrl/shard0_fixed.jsonl`,
`results/judge_rejudge_final/`); every analysis pairs each run with its own verdict
folder (`moral_axes/data.py:judged`, `scripts/targets.py --run FILES JUDGE`,
`scripts/final_table.py`). `generate.py` now writes `cell|types|shard|index`.

`scripts/targets.py 'results/final/*.jsonl' --judge results/judge_final --csv
results/targets_final.csv` (strict spreads for the philosopher groups, SD for the lay
population). Matches at margin 0.5: `IBacc −8 + IHacc 4` with lay population (IB 3.747,
IH 3.128, d 0.206, p_IB < 0.001, p_IH 0.002) and `IBacc −8 + IHacc 5` (3.961 / 3.441,
d 0.337, p 0.022 / 0.001). Closest otherwise: Kantian (−10, 4) d 0.20 p 0.24; non-util.
(−6, 6) d 0.35 p 0.23; rule (0, 8) d 0.28 p 0.38; virtue (−8, 4) d 0.42; deontology (−8, 4)
d 0.46; act (4, 4) d 0.97.

Chain-of-thought means (IB / IH / neutral / harm / kindness), corrected: base 5.22 / 2.84 /
4.53 / 1.55 / 6.31; (−10, 3) 2.52 / 1.85 / 2.95 / 1.54 / 4.08; (−10, 4) 2.80 / 2.11 / 2.99 /
1.81 / 4.15; (−9, 4) 3.32 / 2.69 / 3.70 / 2.08 / 4.60; (−8, 4) 3.75 / 3.10 / 3.92 / 2.25 /
4.92; (−8, 5) 3.96 / 3.42 / 4.10 / 2.75 / 4.95; (−6, 6) 4.70 / 4.14 / 4.38 / 3.22 / 5.20;
(−5, 5) 4.71 / 4.08 / 4.38 / 3.10 / 5.14; (0, 5) 5.16 / 4.66 / 4.78 / 3.66 / 5.37; (0, 8)
5.10 / 4.80 / 4.87 / 4.24 / 5.28; (4, 4) 5.52 / 5.09 / 5.08 / 3.98 / 5.68; (4, 6) 5.31 /
5.01 / 5.02 / 4.38 / 5.42; (8, 8) 5.13 / 4.97 / 4.92 / 4.81 / 5.23.

Equivalence matches at margin 0.5 (corrected): (−8, 4) with lay population, d 0.235,
p_IB < 0.001, p_IH 0.005; (−8, 5) d 0.332, p 0.026 / < 0.001. Closest otherwise: Kantian
(−10, 4) d 0.18; non-util. (−6, 6) d 0.37; rule (0, 8) d 0.30; virtue (−8, 4) d 0.44;
deontology (−8, 4) d 0.48; act (4, 4) d 0.97.

Within-statement s.d. (IB / IH): base 0.97 / 1.32; (4, 4) 0.54 / 0.58; (4, 6) 0.56 / 0.51;
(0, 5) 0.54 / 0.72; (0, 8) 0.57 / 0.65; (8, 8) 0.83 / 0.75; (−6, 6) 0.88 / 0.96; (−8, 4)
1.00 / 0.97; (−10, 4) 1.17 / 0.91.

Figure: `scripts/figures.py` section 10 -> `08_final_cells.png`.
