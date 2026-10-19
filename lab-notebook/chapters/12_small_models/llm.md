# 12. Small models: full protocol

Chain `cluster/h100_queue.sh llama1b gemma2b qwen05 qwen15` on the H100 (log
`after_survey.log`, per model `pipeline_<tag>.log`), October 16 13:32 to October 17 12:29
UTC: Llama 1B 5 h 55 min, Gemma 2B 5 h, Qwen 0.5B 4 h 20 min, Qwen 1.5B 7 h 40 min (its
answers run long). Per tag: `scripts/grid_cells.py --layers L1,L2,L3 --out
results/grid_cells_<tag>.json` with the layers at 0.5, 0.64 and 0.75 of the block count
(73 cells: base plus 24 at each of three blocks), then `cluster/h100_next_model.sh MODEL
TAG results/grid_cells_<tag>.json` unchanged from chapter 10: `generate.py --cells base
--iterations 10` on all statements (`results/<tag>/base/moral.jsonl`) and the controls
with three iterations (`ctrl.jsonl`), `judge_chunks.py` + `judge.py` (`base/judge`),
`directions_resp.py` (`directions/directions.npz`, keys `IBacc|v`, `IHacc|v` of shape
blocks x hidden), `generate.py` on the grid cells, test split, three iterations on IB and
IH (`grid/moral.jsonl`, 47,304 answers) and one on the three controls (`grid/ctrl.jsonl`,
14,600), judge (`grid/judge`, 1,240 chunks). After the queue the Mistral survey rerun
(chapter 11). Results synced to `results/<tag>/` without the activation files.

Direction counts (accepting / rejecting train answers, rated answers): Llama 1B IB 420 /
523 of 1,000, IH 86 / 672 of 800; Gemma 2B 380 / 382, 25 / 697; Qwen 0.5B 492 / 179 of
971, 286 / 182 of 761; Qwen 1.5B 497 / 123 of 850, 86 / 330 of 670. Cosine between
`IBacc|v` and `IHacc|v` at the three grid blocks: Llama 0.45, 0.38, 0.36; Gemma 0.22,
0.14, 0.16; Qwen 0.5B 0.71, 0.64, 0.62; Qwen 1.5B 0.18, 0.17, 0.13.

Analysis, local: `scripts/final_table.py --run 'results/<tag>/grid/*.jsonl'
results/<tag>/grid/judge > results/<tag>/final_table.txt` (means, shifts from base,
within-statement s.d. for every cell); `scripts/targets.py --run ... --csv
results/<tag>/targets_grid.csv` (equivalence test, margin 0.5, both one-sided Welch
tests at 0.05); `scripts/fit_plane.py --run ... --layer L --out
results/<tag>/target_cells.json` at the kept block (Llama 10, Gemma 13, Qwen 0.5B 12,
Qwen 1.5B 18); `scripts/figures_qwen7b.py --run ... --layers L1,L2,L3 --out
lab-notebook/figures/12_<tag>_grid.png`, and `--layers 13` for
`12_gemma2b_L13.png` (two panels, colour by a and by the largest control shift).

Kept block: the one whose single-axis cells move their own scale most with the smallest
control shift, as in chapter 10. Llama: block 8 moves all five sets together (IH −4:
IB −2.5, kindness −3.5), block 12 moves IB by at most 1.2 and IH by 0.8, block 10 kept.
Gemma: block 13 moves IB by −1.1 / +2.6 and IH by −1.0 / +1.8, blocks 17 and 20 by under
0.9 and 0.6, block 13 kept. Qwen 1.5B: blocks 14 and 18 similar on the scales (IB −1.3 /
+1.3 at 14 with a = 4 non-monotone, −1.5 / +1.3 at 18), block 14 raises the harm control
more (+2.1 at IH +4 against +1.4), block 18 kept. Qwen 0.5B: all three blocks move all
five sets together; block 12 reported as the one with the largest IB and IH shifts.

Unrated grid answers (judge level 0): Llama 173, Gemma 13, Qwen 0.5B 5,567, Qwen 1.5B
10,749 of 61,904 each. Equivalence matches (`targets_grid.csv`): Llama (L10, −4, −4) lay
d 0.15 p 0.002 / 0.019; Gemma (L13, −4, 2) lay d 0.29 p 0.000 / 0.038; Qwen 1.5B seven
cells including (L18, −4, 2) lay d 0.19, (L18, −2, −4) deontology d 0.08 and lay d 0.24,
(L14, −4, 0) lay d 0.21; Qwen 0.5B eleven cells at all three blocks for lay and
deontology. Gemma (L13, −2, −2) is 0.09 from the Kantian group with p 0.24 on IB.
