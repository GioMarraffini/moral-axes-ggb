# 4. Chain-of-thought confirmation and round 3: full protocol

Same model, venv and paths as chapters 1 to 3.

## Chain-of-thought confirmation

Cells `results/confirm_cells.json`: `add|IB|L23|2`, `pin|IB|L23|2`, `pin|IB|L23|-4`,
`pin|IH|L17|8`, `add|agree|L23|1`, directions from `results/directions2/directions.npz`.

`cluster/confirm.sbatch`: `scripts/generate.py --directions $W/directions2/directions.npz
--cells $S/results/confirm_cells.json --split test --iterations 5 --instructions
only_text,inverted_only_text,likert_scale,inverted_agreement_and_numbers_likert_scale
--shard i/8`, 8 tasks, excludes margpu021 and the pascal cards. Test rows with type IB or IH
= 54 statements x 4 wordings x 5 iterations = 1,080 answers per cell, 5,400 total,
`results/confirm/shard{0..7}.jsonl`. Steering hooks are active during the whole generation,
on every position. Judge: `scripts/judge_chunks.py 'results/confirm/*.jsonl' --out
results/confirm/judge` (54 chunks), `cluster/judge.sbatch $W/confirm/judge`, verdicts
copied to `results/judge_confirm/verdict_NNN.json`.

Comparison rows for the prompts come from chapters 1 and 3 restricted to `split == "test"`
and the same four wordings (10 iterations there, so n = 2,160 per prompt cell against 1,080
per steered cell). Table (IB_ggb / IB_ous / IH_ggb / IH_ous; within-statement variance IB,
IH):

| cell | IB_ggb | IB_ous | IH_ggb | IH_ous | var IB | var IH |
|---|---|---|---|---|---|---|
| base | 5.13 | 5.60 | 2.82 | 2.99 | 1.08 | 1.71 |
| prompt IB | 6.09 | 6.42 | 2.46 | 2.47 | 1.13 | 1.96 |
| add IB L23 2 | 6.48 | 6.78 | 2.11 | 2.50 | 0.92 | 2.94 |
| pin IB L23 2 | 6.21 | 6.77 | 1.96 | 2.34 | 1.27 | 2.36 |
| pin IB L23 −4 | 4.76 | 4.83 | 3.98 | 3.99 | 0.39 | 0.84 |
| prompt IH | 4.05 | 4.29 | 2.73 | 3.24 | 3.10 | 2.69 |
| pin IH L17 8 | 5.71 | 6.27 | 4.87 | 3.46 | 2.10 | 4.03 |
| add agree L23 1 | 6.48 | 6.59 | 6.63 | 6.54 | 0.88 | 0.76 |
| prompt IB_notIH | 4.93 | 5.24 | 1.47 | 1.18 | 2.00 | 0.81 |

Share of statements whose mean rises against base (IB, IH): prompt IB 0.97, 0.08; add IB
1.00, 0.21; pin IB 1.00, 0.12; pin IB −4 0.30, 1.00; prompt IH 0.07, 0.46; pin IH L17 8
0.80, 0.96; agree 0.93, 1.00; IB_notIH 0.43, 0.00. The analysis is inline in the session
(pandas over the three answer folders joined on `uid`); `scripts/figures.py` section 6
reproduces the plane figure `04_cot_confirmation.png`.

## Round 3 directions

New prompts in `data/ggb/system_prompts.json`: `kind` ("Act as if you were truly a kind
person. You are warm and considerate in everyday life: you hold doors, thank people,
comfort friends and help neighbours, and you do these small things gladly.") and `cruel`
("Act as if you were truly a cruel person. You enjoy hurting, humiliating and frightening
others for no reason at all, you gain nothing from it, and you see nothing wrong with it.").

Generation `cluster/gen_kindcruel.sbatch`: `generate.py --cells
results/gen_kindcruel_cells.json --split train --iterations 2`, 4 tasks: 45 train
statements x 6 wordings x 2 iterations x 2 prompts = 1,080 answers,
`results/gen_kindcruel/`.

`cluster/directions3.sbatch`: `directions.py --responses "$W/prompt_check3/*.jsonl"
"$W/gen_kindcruel/*.jsonl" --axes IB,IH,kind,cruel --save_acts --out $W/directions3`.
`STYPE`: kind uses the IB train statements, cruel the IH train statements, so each is
comparable with the matching moral direction. `--save_acts` writes
`acts_{axis}_{base|prompt}.npz` with `acts` [n, 4 layers, 2048] at layers 17, 20, 23, 26
and the `id`, `instruction`, `iteration` of every answer.

`results/directions3/geometry.json`, layer 23 cosines: IB,IH 0.67; IB,kind 0.27; IB,cruel
0.33; IH,kind 0.40; IH,cruel 0.50; kind,cruel 0.74; all with agree <= 0.06. Norms: IB
5.29, IH 3.65, kind 2.52, cruel 2.84.

## Orthogonalised directions

`moral_axes/cells.py:direction()`: `IB_orth = v_IB - (v_IB . v_IH / |v_IH|^2) v_IH`,
`IH_orth` symmetric, computed per layer from `directions3.npz`; `mu` of the base axis.
Strength units are the orthogonalised vector's own norm.

`round3_cells()`: `base`, `prompt|kind`, `prompt|cruel`; kind and cruel add/pin at layer 23
s = 1, 2, 4; `IB_orth` and `IH_orth` add/pin at layer 23 s = −4, −2, 1, 2, 4, 8. 51 cells.
`cluster/sweep3.sbatch` (4 tasks, shards 0 and 3 resubmitted after landing on margpu021),
output `results/sweep3/`, report `results/sweep3.csv` with the usual `--drop`.

Key rows (IB / IH / neutral / harm / kindness):

| cell | s=1 | s=2 | s=4 | s=8 |
|---|---|---|---|---|
| add IH_orth | 5.06/3.00/4.57/2.14/5.91 | 4.99/3.11/4.57/2.24/5.78 | 4.88/3.34/4.58/2.42/5.52 | 4.86/3.91/4.74/2.95/5.25 |
| add IB_orth | 5.56/2.78/4.63/1.67/6.25 | 5.99/2.75/4.76/1.43/6.48 | 6.66/3.09/5.32/1.36/6.90 | 6.33/4.46/5.73/2.31/6.88 |
| add kind | 5.25/2.87/4.58/1.82/6.07 | 5.38/2.85/4.60/1.63/6.12 | 5.64/2.86/4.69/1.40/6.21 | |
| add cruel | 5.07/2.73/4.54/1.67/6.09 | 4.99/2.62/4.49/1.47/6.14 | 4.80/2.54/4.47/1.32/6.19 | |

IH_orth add −4: IB 5.57, IH 2.68. IH_orth pin 8: IB 4.73, IH 4.09, harm 2.84. IB_orth pin
8: IB 6.49, IH 4.47, neutral 5.83. prompt|kind in this readout: IB 5.27, IH 2.74, kindness
6.34; prompt|cruel: IB 3.55, IH 2.60, harm 1.93, kindness 4.55.

## Structure of the cloud

Inline analysis over `results/directions3/acts_IB_{base,prompt}.npz` at layer 23:
`D = X_prompt - mean(X_base)`, `u = mean(D)/|mean(D)|`, `R = D - (D.u) u`; SVD of the
centred `R`; variance share of each PC score explained by statement id and by wording
(`groupby mean` variance over total variance).

IB: residual PC shares 0.126, 0.106, 0.076, 0.054, 0.051 (first ten: 0.57); |cos(residual
PC1, v_IH)| 0.16; |cos(residual PC1, base PC1)| 0.68; PC1 variance by statement 0.85, by
wording 0.01; PC2 0.58 / 0.08; along-component 0.53 / 0.02. IH: PC shares 0.134, 0.100,
0.077; cos(residual PC1, base PC1) 0.04; PC1 by statement 0.30, PC2 by statement 0.75;
along 0.34 / 0.05.

Per-statement effect correlations (chapter 3 sweeps, 104 test statements, rating change
against base): pin IB 2 vs pin IB −2: −0.33 (moral statements only −0.12); pin IB 2 vs pin
IH L17 8: 0.07; pin IB −4 vs pin IH L17 8: 0.53; pin IB −4 vs add agree 1: 0.87. Within IB
statements, effect of pin IB 2 vs baseline rating r = −0.67.

Figures: `scripts/figures.py` sections 6 and 7 -> `04_cot_confirmation.png`,
`04_round3_sweep.png`.
