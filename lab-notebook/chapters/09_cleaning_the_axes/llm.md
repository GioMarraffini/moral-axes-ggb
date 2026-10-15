# 9. Cleaning the axes: full protocol

`scripts/directions_ctrl.py --responses "results/final_ctrl/*.jsonl" --judge
results/judge_final --merge results/directions_resp2/merged.npz --out
results/directions_ctrl` (run on the H100, `cluster/h100_clean.sh`). Note: at the time of
this run the control verdicts were the colliding ones of chapter 8 (the uid collision was
found afterwards); the rated subsets used for the contrast (600 per side, sampled) are
therefore partly mislabelled, which weakens but does not reverse the contrast. Per
control type: accepting (rating >= 5) minus rejecting (<= 3), up to 600 answers per side,
unsteered forward pass over the answer text, all block outputs. Keys `harmacc|v`,
`kindacc|v`, `neutralacc|v` (+ `|mu`), merged with `directions_resp2/merged.npz`.
`geometry.json` lists cosines at layers 17, 20, 23, 26; at 23: IHacc,harmacc 0.573;
IHacc,kindacc −0.031; IBacc,kindacc 0.471; IBacc,harmacc 0.352; IBacc,neutralacc 0.222;
IHacc,neutralacc 0.157.

Orthogonalised axes: `moral_axes/cells.py:direction()` accepts `X-Y-Z` (X with Y, then
Z projected out, Gram-Schmidt). Cells `results/clean_cells.json`: `base`; `IHacc`,
`IHacc-harmacc`, `IHacc-harmacc-kindacc` at 4 and 8; `IBacc-kindacc` at −8;
`IBacc-kindacc + IHacc-harmacc` at (−8, 4); `IBacc-kindacc-neutralacc + IHacc-harmacc`
at (−8, 4). Generation on the H100 (`generate.py --dtype bf16 --bs 64`), test split, three
iterations, scales (`results/clean/moral_fixed.jsonl`, 6,480) and controls
(`results/clean/ctrl_fixed.jsonl`, 6,000; uids rewritten to the new scheme), judged
together (`results/judge_clean/`, 125 chunks).

Table: `scripts/final_table.py --run 'results/clean/*_fixed.jsonl' results/judge_clean`.
Values in `human.md`. Shifts from base (IB / IH / neutral / harm / kindness): IHacc 4
−0.07 / +1.68 / +0.21 / +1.91 / −0.84; IHacc 8 −0.14 / +2.04 / +0.33 / +2.64 / −1.09;
IHacc−harm 4 −0.02 / +1.01 / +0.03 / +0.92 / −0.40; IHacc−harm 8 +0.05 / +1.65 / +0.22 /
+1.64 / −0.58; IHacc−harm−kind 4 +0.07 / +1.13 / +0.20 / +0.97 / −0.36; 8 +0.09 / +1.92 /
+0.32 / +1.94 / −0.48; IBacc−kind −8 −1.46 / −1.39 / −0.61 / −0.48 / −0.70; combined
(−8, 4) −0.75 / −0.34 / −0.15 / −0.01 / −0.76.
