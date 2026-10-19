# 14. Induced IH contrast: full protocol

Prompted answers: `scripts/generate.py --model Qwen/Qwen2.5-7B-Instruct --cells
results/prompt_IH_cells.json --split train --types IH --iterations 10 --instructions <4
wordings> --dtype bf16 --bs 48 --out $W/qwen7b/np/prompted.jsonl`, where
`results/prompt_IH_cells.json` is `[{"kind": "prompt", "axis": "IH"}]` (the IH system prompt
from `data/ggb/system_prompts.json`). Judge: `judge_chunks.py` then `judge.py --dtype bf16
--bs 16` into `np/judge_prompted`. Directions: `scripts/directions_resp.py --model M
--responses $W/qwen7b/base/moral.jsonl $W/qwen7b/np/prompted.jsonl --judge
$W/qwen7b/base/judge $W/qwen7b/np/judge_prompted --cells "base,prompt|IH" --dtype bf16
--out $W/qwen7b/directions_np`. The script re-encodes every answer under
`data.system(None, model)`, with no axis prompt, and pools the accepting and rejecting
answers of both cells per axis. All three steps in `cluster/np_prompted.sbatch` (one hopper
job, 6 min). Counts in `results/qwen7b/directions_np/geometry.json`: IB 739 / 125, IH 453 /
1093 (unprompted 58 / 721, prompted 395 / 372 rated accepting / rejecting, the rest
rated 4).

Grid: `scripts/grid_cells.py` wrote `results/grid_cells_qwen7b_np.json` (25 additive cells
at block 18, a, b in −4, −2, 0, 2, 4) and the six slices `_0.._5` (9, 9, 2, 2, 2, 1 cells).
`cluster/np_gen_hopper.sbatch` (array 0-1, `--gres=gpu:hopper:1`, bf16, batch 48, 18 min)
and `cluster/np_gen_rtx.sbatch` (array 2-5, `--gres=gpu:rtx:1`, fp16, batch 12, 15 to 29
min), test split, scales three repetitions, controls once; `cluster/np_chunks.sbatch` (CPU,
212 chunks); `cluster/np_judge.sbatch` (array 0-2, hopper, bf16, `--shard i/3`). Shard 0
ran on margaret (10 min); the hopper cards were then taken by another user's array, so
shards 1 and 2 ran side by side on the Scaleway H100 (`cluster/h100_np_judge.sh`, bf16,
two judge copies on one card, 70 GB), and the outputs were copied back to margaret.
`cluster/np_judge_rtx.sbatch` (two RTX 6000 per job, `device_map="auto"` in
`moral_axes/model.py:load` when more than one card is visible) was submitted as a backup
and cancelled when the H100 finished. Jobs 789182-789186, 790166 (failed its own memory
preflight), 790180 (cancelled). Outputs `$W/qwen7b/grid_np/{moral,ctrl}_{0..5}.jsonl`,
`judge/`, synced to `results/qwen7b/grid_np/`. 21,200 answers, 0 unrated, 0 with no answer.

Analysis: `final_table.py --run 'results/qwen7b/grid_np/*.jsonl' results/qwen7b/grid_np/judge
> results/qwen7b/np_table.txt` (chapter 10 table regenerated to
`results/qwen7b/grid_table.txt` for the matched-cell comparison); `targets.py ... --csv
results/qwen7b/targets_np.csv` (no match; lay 0.88 at (−4, 4), rule utilitarianism 0.61 at
(2, 4), non-utilitarian consequentialism 0.77 at (0, 4)); `fit_plane.py --run ... --layer
18 --range -12 12 --out results/qwen7b/target_cells_np.json` (IB r 0.994 rmse 0.06, IH r
0.993 rmse 0.13; act (5.2, 4.4), rule (−4.6, 9.0), non-util (−7.5, 9.8), virtue (−12, 9.7),
deontology (−12, 9.1), kantian (−10.6, 3.0), lay (−10.9, 8.7)); `figures_qwen7b.py ...
--layers 18 --out lab-notebook/figures/14_qwen7b_np_L18.png`.

Directions at block 18 (`results/qwen7b/directions_np/directions.npz` against
`results/qwen7b/directions/directions.npz`): IBacc identical (cos 1.000, norm 6.03);
IHacc cos 0.685, norm 5.01 against 4.41; cos(IBacc, IHacc) 0.216 (old 0.122).
Matched-cell differences, new minus old, over the 24 steered block-18 cells: mean IB
+0.07, IH +0.05, neutral +0.03, harm 0.00, kindness +0.03; largest |difference| 0.39,
0.33, 0.22, 0.67 (at (4, 4)), 0.18; unsteered cell IB +0.03, IH +0.13.
