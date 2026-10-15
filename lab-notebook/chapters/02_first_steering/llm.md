# 2. First steering: full protocol

Same model, venv and paths as chapter 1's `llm.md`.

## Layer convention

`moral_axes/model.py`: layer L means the output of decoder block `model.model.layers[L]`,
which equals HF `hidden_states[L + 1]`. Directions are extracted there and hooks are
registered there (`register_forward_hook` on the block). This is the same hook position
as "L23" in `manifold-persona/persona_lora/steer_pin.py`. Qwen2.5-3B has 36 blocks.

## Directions

`scripts/directions.py --responses "$W/prompt_check3/*.jsonl" --out $W/directions`
(`cluster/directions.sbatch`, one GPU, 16 min). For each axis in (IB, IH):

1. Take the chapter 1 answers with `split == "train"`, `type == axis`, `iteration < 2`,
   for cells `base` and `prompt|{axis}`: 25 statements x 6 wordings x 2 = 300 answers per
   cell for IB, 240 for IH.
2. Rebuild each answer's full prompt with its own system prompt
   (`data.cot_prompt(C.system(cell), instruction, statement)`), run one teacher-forced
   forward pass with `output_hidden_states=True` (`moral_axes/model.py:response_means`,
   batch 4, left padding), and average the hidden state over the response tokens only, at
   every block output, in float32.
3. `v[axis][L] = mean over prompted answers - mean over base answers` (shape 36 x 2048),
   `mu[axis][L] = mean over base answers`.

Saved as `results/directions/directions.npz` with keys `IB|v`, `IB|mu`, `IH|v`, `IH|mu`,
and `results/directions/geometry.json` with per-layer norms and `cos IB,IH`.

| layer | 17 | 20 | 23 | 26 |
|---|---|---|---|---|
| cos(v_IB, v_IH) | 0.64 | 0.71 | 0.67 | 0.66 |
| norm v_IB / norm baseline mean | 0.097 | 0.103 | 0.098 | 0.111 |

Norm of v_IB grows from 0.7 at layer 0 to 21 at layer 34 (12.6 at 35); v_IH is about 0.7
times v_IB at every layer.

## Cells

`moral_axes/cells.py:sweep_cells()`: `base`, `prompt|IB`, `prompt|IH`, then for every
layer in `LAYERS = [17, 20, 23, 26]` and strength in `STRENGTHS = [1, 2, 4, 6, 8]`:
`add|IB`, `pin|IB`, `add|IH`, `pin|IH`, `add|rand`. 103 cells. Name format
`{mode}|{axis}|L{layer}|{s}`. Steered cells use the default system prompt; prompt cells use
`data.system(axis)`.

`moral_axes/cells.py:hooks(c, Z, dev)`, applied to the float block output `h` at every
position (prompt and generated tokens alike):

- add: `h + s * v[L]`
- pin: `u = v[L] / |v[L]|`, `goal = mu[L] . u + s * |v[L]|`, `h + (goal - h . u) u`
- rand: `numpy.random.default_rng(L).standard_normal(2048)`, scaled to `|v_IB[L]|`, added
  with strength `s`.

So `s = 1` adds (or pins to) exactly the prompt's mean displacement at that layer.

## Readout (R1)

`scripts/sweep.py --directions $W/directions/directions.npz --shard i/4`
(`cluster/sweep.sbatch`, 4 tasks, each takes cells `[i::4]`, 15 min on a 2080 Ti).
Evaluation rows: `data.statements("test")` = 30 IB + 24 IH (including the 9 OUS items) + 10
neutral (controls 10..19; the first 10 neutral are reserved as train) + 20 harm_no_benefit
+ 20 kindness = 104 rows, each under all 6 wordings = 624 prompts per cell.

Prompt: `data.rate_prompt(system, instruction, statement)` = `chat(system,
"{instruction}\n\nStatement: {statement}\n\nReply with the option only.")`.
`moral_axes/model.py:option_probs` scores the seven answer strings of that wording as the
assistant's reply: single-token answers (the digits) from one forward pass over the prompt;
multi-token answers (the text labels) by the product of token probabilities, computed on
the last `max_len + 1` positions only. `rating = sum(p_i * value_i) / sum(p_i)`,
`mass = sum(p_i)` (how much probability the seven options get; 1.0 almost everywhere,
0.45 for the random direction at layer 20 strength 8).

Output `$W/sweep/shard{0..3}.jsonl`, copied to `results/sweep/`: one row per (cell,
statement, wording) with `rating` and `mass`.

## Report

```
.venv/bin/python scripts/report.py 'results/sweep/*.jsonl' --csv results/sweep.csv \
  --drop inverted_agreement_likert_scale,inverted_numbers_likert_scale
```

`results/sweep.csv` has one row per cell with mean rating per set: `IB`, `IH` (test
split, source ggb), `IB_ous`, `IH_ous`, `neutral`, `harm_no_benefit`, `kindness`, `mass`.

Reference cells (four wordings): base IB 5.12, IH 2.90, IB_ous 6.29, IH_ous 2.72, neutral
4.57, harm 2.04, kindness 6.03. prompt|IB: 6.62, 2.71, 6.59, 2.49, 4.40, 2.03, 5.76.
prompt|IH: 4.32, 3.40, 4.30, 5.59, 4.37, 2.35, 4.78.

Layer 23, IB direction (IB / IH / neutral / harm / kindness):

| s | add | pin |
|---|---|---|
| 1 | 5.74 / 2.83 / 4.68 / 1.61 / 6.29 | 5.97 / 2.77 / 4.72 / 1.60 / 6.09 |
| 2 | 6.24 / 2.86 / 4.99 / 1.46 / 6.67 | 6.50 / 2.86 / 5.01 / 1.39 / 6.55 |
| 4 | 6.81 / 4.07 / 6.04 / 2.43 / 6.96 | 6.90 / 4.17 / 6.16 / 1.81 / 6.98 |
| 8 | 6.85 / 5.90 / 6.61 / 3.35 / 6.91 | 6.96 / 6.22 / 6.85 / 3.19 / 6.99 |

IH direction, best cell: layer 17 pin 8: IB 5.39, IH 4.09, IB_ous 5.78, IH_ous 2.49,
neutral 4.48, harm 2.13, kindness 5.14, mass 0.93. Layer 23 add 8: IB 6.02, IH 3.59,
neutral 5.22. Layer 26 moves nothing by more than 0.3 on IH.

Random direction, layer 23: IB 4.69 / 4.28 / 3.61 / 3.58 / 4.12 at s = 1, 2, 4, 6, 8;
neutral falls to 3.35. Layer 20 s = 8: mass 0.45 (output no longer an option).

All other cells: `results/sweep.csv`, or rerun the report without `--drop` for six wordings.

Figures: `scripts/figures.py` -> `lab-notebook/figures/02_steering_sweep.png` (panels: IB
add L23, IB pin L23, IH pin L17, IH add L23) and `02_ib_ih_plane.png` (every steer cell,
marker size grows with s).

## Failed runs, for the record

- 714863 / 714925: direction build regenerated answers itself (1,100 generations on one
  GTX 1080 Ti, cancelled after 1h12 at a quarter done). Replaced by reading the chapter 1
  answers.
- 715423: sweep out of memory on 11 GB cards: `option_probs` computed logits for every
  position. Fixed by applying `lm_head` to the last positions only; checked equal to the
  full computation on one prompt to 1e-4.
