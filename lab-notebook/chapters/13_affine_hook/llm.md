# 13. Affine hook: full protocol

Statistics: `scripts/aff_stats.py --model Qwen/Qwen2.5-7B-Instruct --responses
results/qwen7b/base/moral.jsonl --judge results/qwen7b/base/judge --directions
results/qwen7b/directions/directions.npz --layer 18 --dtype bf16 --bs 8 --out
results/qwen7b/directions/aff_L18.npz` (run on the H100, 5 min; `aff_L18.json` holds the
counts and norms). `moral_axes/model.py:response_token_stats` returns per answer the token
count, sum and sum of squares of hidden_states[L + 1] over the response tokens; the script
pools them per group (`{IB,IH}aff|L18|mu_{acc,rej}`, `sd_{acc,rej}`) and over all rated
answers of both axes (`aff|L18|mu_p`, `sd_p`), and copies the directions keys so one file
serves `generate.py`.

Hook: `moral_axes/cells.py`, mode `aff`, axis `IBaff` or `IHaff`; `steer2` terms whose
axis ends in `aff` use it, and two terms at one block add their displacements.
`scripts/grid_cells.py --mode aff --strengths=-2,-1,0,1,2 --layers 18` wrote
`results/aff_cells_qwen7b.json` (25 cells); `fit_plane.py` and `figures_qwen7b.py` read
the `aff` axes like the `acc` ones.

Runs: an H100 chain (`cluster/h100_aff.sh`) was started and stopped after the statistics
step because the card was shared with other work. On margaret: `cluster/aff_gen_hopper.sbatch`
(array 0-1, `--gres=gpu:hopper:1`, bf16, batch 48, cells 0-8 and 9-17 from
`results/aff_cells_qwen7b_{0,1}.json`), `cluster/aff_gen_rtx.sbatch` (array 2-5,
`--gres=gpu:rtx:1`, Quadro RTX 6000 24 GB, fp16, batch 12, cells 18-19, 20-21, 22-23, 24),
both after a CPU job that downloaded the 7B into the HF cache; `cluster/aff_chunks.sbatch`
(CPU) then `cluster/aff_judge.sbatch` (array 0-2, hopper). All twelve ampere cards were
allocated and the 2080 Ti cards (11 GB) cannot hold the 7B. Jobs 789109, 789112-789115;
outputs `W/qwen7b/aff/{moral,ctrl}_{0..5}.jsonl`, `judge/` (424 chunks), synced to
`results/qwen7b/aff/`. 21,200 answers, 0 unrated, 0 at the token cap.

Analysis: `final_table.py --run 'results/qwen7b/aff/*.jsonl' results/qwen7b/aff/judge >
results/qwen7b/aff_table.txt`; `targets.py ... --csv results/qwen7b/targets_aff.csv` (no
match); `fit_plane.py ... --layer 18 --out results/qwen7b/target_cells_aff.json` (IB r
0.925, IH r 0.971; every group at the a = ±2 bound, residuals 1.1 to 2.4);
`figures_qwen7b.py ... --layers 18 --out lab-notebook/figures/13_qwen7b_aff_L18.png`.

Geometry from `aff_L18.npz` at block 18: |mu_IBacc − mu_p| 5.76, |mu_IBrej − mu_p| 8.38,
|mu_IHacc − mu_p| 7.41, |mu_IHrej − mu_p| 6.65, |mu_p| 54.5; token-level |acc − rej| 5.84
(IB) and 4.13 (IH), cosine 1.00 with the answer-level `IBacc|v`, `IHacc|v` (norms 6.03,
4.41); cos(mu_IBacc − mu_p, IBacc|v) −0.05, cos(mu_IBrej − mu_p, IBacc|v) −0.73,
cos(mu_IHacc − mu_p, IHacc|v) +0.45, cos(mu_IHrej − mu_p, IHacc|v) −0.12;
cos(mu_IBacc − mu_p, mu_IHacc − mu_p) −0.84; |mean of IB answers − mean of IH answers|
12.45. Gain term sd_t / sd_p − 1: median −0.01, largest magnitude 0.15 (IB) and 0.31 (IH);
|gain (mu_t − mu_p)| 0.30 to 0.78.
