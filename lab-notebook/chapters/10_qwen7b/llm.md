# 10. Qwen2.5-7B-Instruct: full protocol

Model `Qwen/Qwen2.5-7B-Instruct` (28 layers, hidden 3584), bf16, on the Scaleway H100.
Chain `cluster/h100_next_model.sh Qwen/Qwen2.5-7B-Instruct qwen7b results/grid_cells_qwen7b.json`
(log `qwen7b.log`), outputs under `results/qwen7b/`, synced back minus `acts_*`.
Instructions: the four kept wordings (`only_text`, `inverted_only_text`, `likert_scale`,
`inverted_agreement_and_numbers_likert_scale`). Judge: `scripts/judge.py` with
Qwen2.5-14B-Instruct, bf16, batch 16, on the same card.

## Round 1

1. Unsteered: `generate.py --cells base --split all --types IB,IH --iterations 10`
   (`base/moral.jsonl`, 3,960 answers) and the three controls, three iterations
   (`base/ctrl.jsonl`, 720). Judge `base/judge/` (94 chunks). Means over all 99
   statements: IB 4.90, IH 2.29, neutral 4.56, harm 1.06, kindness 6.35; within-statement
   s.d. 0.69 / 0.90.
2. Directions: `directions_resp.py --responses base/moral.jsonl --judge base/judge --out
   directions/` -> `directions/directions.npz` (keys `IBacc|v`, `IHacc|v`, `both|v` per
   layer, plus `|mu`) and `geometry.json`: IB 739 accepting (>= 5) vs 125 rejecting
   (<= 3) of 1,000 rated; IH 58 vs 721 of 800. cos(IBacc, IHacc) per layer output
   (hidden_states[L+1], index L): 0.02, −0.02, 0.03, 0.04, 0.04, 0.10, 0.15, 0.15, 0.18,
   0.17, 0.16, 0.15, 0.15, 0.10, 0.08, 0.10, 0.10, 0.11, 0.12, 0.13, 0.16, 0.13, 0.13,
   0.12, 0.11, 0.11, 0.11, 0.10. Norms grow from 0.5 to 28 across depth (IBacc), 0.35 to
   21 (IHacc).
3. Grid `results/grid_cells_qwen7b.json`: `base` plus, at layers 14, 18, 21, every (a, b)
   with a, b in {−4, −2, 0, 2, 4} except (0, 0): 72 steered cells (`steer2` with two
   terms, `steer`/`add` when one strength is zero). Test split (54 statements), three
   iterations on IB and IH (`grid/moral.jsonl`, 47,304), one on the controls
   (`grid/ctrl.jsonl`, 14,600). Judge `grid/judge/` (1,240 chunks), 61,904 rated, none
   missing.
4. Tables: `final_table.py --run 'results/qwen7b/grid/*.jsonl' results/qwen7b/grid/judge`
   (means, shifts, within-statement s.d.). Targets: `targets.py --run ... --csv
   results/qwen7b/targets_grid.csv`: no match at margin 0.5; closest per group: act
   (4, 4)@L14 d 1.06; kantian (−2, −4)@L14 d 1.02; lay `add|IBacc|L14|−4` d 0.79;
   non-util (−4, 4)@L14 d 0.46; deontology `add|IBacc|L14|−4` d 1.10; rule (−4, 4)@L14
   d 0.50; virtue `add|IBacc|L14|−4` d 0.96.
5. Surface: `fit_plane.py 'results/qwen7b/grid/*.jsonl' --judge results/qwen7b/grid/judge
   --layer L --range -12 12`. Fit r (IB / IH): L14 0.96 / 0.99, L18 0.99 / 0.99, L21
   0.99 / 1.00. The inversion at L18 asks for a = −12 (bound) for the lay population,
   virtue, deontology and kantian groups and (5.9, 4.4) for act utilitarianism; the
   quadratic extrapolates badly at L14 (it predicts IH 3.5 at b = −4), so it is used only
   to set the range of round 2.
6. Figure: `figures_qwen7b.py --run 'results/qwen7b/grid/*.jsonl' results/qwen7b/grid/judge`
   -> `figures/10_qwen7b_grid.png`.

Shifts from the grid base (IB / IH / neutral / harm / kindness), strength 4 and −4:
L14 IBacc +1.47 / +1.71 / +0.22 / +0.21 / +0.19 and −0.39 / +0.80 / +0.10 / +0.64 /
−0.89; L14 IHacc +0.32 / +1.94 / +0.10 / +0.61 / −0.29 and −0.94 / −1.16 / −0.40 / −0.02
/ +0.20; L18 IBacc +0.68 / +1.46 / +0.40 / +0.21 / +0.05 and −0.64 / −0.62 / −0.35 /
−0.06 / −0.20; L18 IHacc +0.33 / +1.69 / +0.17 / +0.49 / −0.30 and −0.56 / −0.80 / −0.45
/ +0.01 / +0.04; L21 IBacc +0.18 / +0.42 / −0.10 / 0.00 / −0.09 and −0.44 / −0.18 /
−0.20 / 0.00 / −0.01; L21 IHacc +0.17 / +1.10 / −0.05 / +0.09 / −0.06 and −0.29 / −0.60
/ −0.30 / −0.04 / +0.04.

## Round 2

Cells `results/grid2_cells_qwen7b.json`: `base`; layer 18; a = 0 with b in {6, 8}; a in {−6,
−8, −10} x b in {−2, 0, 2, 4, 6, 8}; a in {6, 8} x b in {0, 2, 4, 6, 8}: 31 cells, mild
first. `cluster/h100_grid.sh Qwen/Qwen2.5-7B-Instruct qwen7b results/grid2_cells_qwen7b.json grid2`
(log `qwen7b_grid2.log`), same iterations and judge as round 1, outputs
`results/qwen7b/grid2/`. A first attempt included a = −12: that cell produced no answer
in 20 minutes (the base cell takes 2), every generation running to the 2,000-token cap,
and was stopped (`cluster/h100_kill.sh`).

Outputs: `grid2/moral.jsonl` (20,088), `grid2/ctrl.jsonl` (6,200), judge `grid2/judge/`
(26,288 rated, 17 with no rating, all in cells with a <= −8). Tables:
`final_table.py --run 'results/qwen7b/grid2/*.jsonl' results/qwen7b/grid2/judge`; targets:
`targets.py --run ... --csv results/qwen7b/targets_grid2.csv` (no match; closest per group:
act (8, 8) d 1.00; kantian (−10, 2) d 0.27; lay (−6, 6) d 0.91; non-util (−6, 8) d 0.58;
deontology (−6, 4) d 1.20; rule `add|IHacc|L18|8` d 0.46; virtue (−6, 6) d 1.06).
Surface on both rounds at layer 18: `fit_plane.py --run 'results/qwen7b/grid/*.jsonl'
results/qwen7b/grid/judge --run 'results/qwen7b/grid2/*.jsonl' results/qwen7b/grid2/judge
--layer 18 --range -10 8 --out results/qwen7b/target_cells.json`: IB r 0.990 rmse 0.13,
IH r 0.963 rmse 0.36; inverse act (8.0, 7.9) residual 0.54, rule (3.9, 8.0) 0.55,
non-util (0.7, 6.5) 0.87, virtue (−9.1, 6.4) 1.01, deontology (−10, 6.1) 0.99, kantian
(−10, 2.3) 0.21, lay (−9.1, 6.4) 0.80. Figure: `figures_qwen7b.py --run ... --run ...
--layers 18 --out lab-notebook/figures/10_qwen7b_L18.png` (two panels when one layer is
given: colour by a, colour by the largest control shift).

Within-statement s.d. (IB / IH / neutral / harm / kindness): base 0.74 / 0.88 / 0.42 /
0.15 / 0.47; (8, 8) 0.71 / 0.39 / 0.20 / 0.58 / 0.78; `add|IHacc|L18|8` 0.45 / 0.61 / 0.26
/ 1.02 / 0.45; (−6, 6) 0.64 / 1.22 / 0.55 / 0.73 / 0.69; (−8, 4) 1.54 / 1.19 / 1.28 / 0.79
/ 1.12; `add|IBacc|L18|-10` 2.02 / 1.69 / 2.38 / 1.37 / 2.34. Answers at the 2,000-token
cap: 4 at (−10, −2), 2 at `add|IBacc|L18|-10`, 1 at (−8, −2).
