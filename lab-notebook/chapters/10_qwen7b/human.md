# 10. Does the pipeline transfer to Qwen2.5-7B-Instruct?

## The question

Chapters 6 to 9 were all on the 3B model. The pipeline that came out of them (unprompted
chain-of-thought answers, judge, answer-built accepting-minus-rejecting directions, a grid
of the two directions, inversion of the fitted surface) is stated in `PIPELINE.md`. Does
it work unchanged on the next model of the same family, and where do the two axes sit in
a 28-layer model?

## What was done

The pipeline of `PIPELINE.md`, run once on an H100 with no manual step (`cluster/h100_next_model.sh`):
ten unprompted chain-of-thought iterations on all 99 statements, judge, directions from
the model's own accepting versus rejecting answers, then a 5 x 5 grid of the two
directions (a, b in −4, −2, 0, 2, 4) at three layers (14, 18, 21 of 28, that is 50%, 64%
and 75% of depth; the 3B used layer 23 of 36, 64%), test split, three iterations, with
the three controls under chain of thought, one iteration.

## Result

Unsteered the 7B is less utilitarian than the 3B on both scales: IB 4.80 (3B 5.22), IH 2.31
(3B 2.84). Its controls are cleaner: pointless harm 1.08 (3B 1.55), kindness 6.36.

The 7B accepts 739 of 1,000 rated IB answers and rejects only 125, and accepts 58 of 800 IH
answers: the contrasts are more imbalanced than in the 3B. The two directions are still
nearly orthogonal (cosine 0.10 to 0.18 over the middle layers, 0.12 at layer 18; 3B: 0.18).

![7B grid](../../figures/10_qwen7b_grid.png)

*The 5 x 5 grid at each layer in the IH, IB plane. Star: unsteered. Colour: IB strength a.
Green squares: the human groups.*

| layer | cell | IB | IH | neutral | harm, no benefit | kindness |
|---|---|---|---|---|---|---|
| | unsteered | 4.80 | 2.31 | 4.40 | 1.08 | 6.36 |
| 14 | IB +4 | 6.27 | 4.02 | 4.62 | 1.29 | 6.55 |
| 14 | IB −4 | 4.41 | 3.11 | 4.50 | 1.71 | 5.48 |
| 14 | IH +4 | 5.12 | 4.25 | 4.50 | 1.69 | 6.08 |
| 14 | IH −4 | 3.86 | 1.15 | 4.00 | 1.05 | 6.56 |
| 18 | IB +4 | 5.48 | 3.77 | 4.80 | 1.29 | 6.41 |
| 18 | IB −4 | 4.16 | 1.69 | 4.05 | 1.01 | 6.16 |
| 18 | IH +4 | 5.13 | 4.01 | 4.58 | 1.56 | 6.06 |
| 18 | IH −4 | 4.24 | 1.51 | 3.95 | 1.09 | 6.40 |
| 21 | IB +4 | 4.98 | 2.73 | 4.30 | 1.08 | 6.28 |
| 21 | IB −4 | 4.36 | 2.14 | 4.20 | 1.08 | 6.35 |
| 21 | IH +4 | 4.97 | 3.42 | 4.35 | 1.16 | 6.30 |
| 21 | IH −4 | 4.51 | 1.71 | 4.10 | 1.04 | 6.40 |

- **The layer matters more than in the 3B.** Layer 14 moves the most (IB +1.5, IH +1.9 at
  strength 4) but is dirty: lowering IB there raises pointless harm (+0.6) and lowers
  kindness (−0.9), and raising IB raises IH by more than IB. Layer 21 is clean but weak
  (IB at most +0.2, IH +1.1). Layer 18 is the compromise: IH +1.7 for +0.5 of harm, IB
  −0.6 with the controls flat.
- **The IB direction is not as clean as in the 3B.** At layers 14 and 18, raising IB
  raises IH by about as much (layer 18, a = 4: IB +0.7, IH +1.5). Lowering IB lowers IH
  (a = −4: −0.6 and −0.6). Raising IH raises IB by 0.3. The grid is a sheared
  parallelogram rather than a square, and lower-left to upper-right is its long axis.
- **The scales are too small to reach the groups.** The quadratic surface fits well at
  every layer (r 0.96 to 0.99) but no human group is inside the grid; the closest cell to
  the lay population is 0.8 group SD away. As in the 3B, where the lay population needed
  a = −8, the inversion asks for a of −6 to −12.

A second round at layer 18 with a in −10 to −6 and 6 to 8 and b in −2 to 8 (31 cells; a = −12 was tried first and ran every answer to the token cap) is
in `llm.md`; its result is written below when it lands.

## Round 2

(pending)
