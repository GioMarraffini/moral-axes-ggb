# Moral axes of the Greatest Good Benchmark: lab notebook

Can the two scales of the Greatest Good Benchmark, impartial beneficence (IB) and
instrumental harm (IH), be moved in Qwen2.5-3B-Instruct, first by a system prompt and then
by editing the residual stream, and are the two separable?

Every chapter has two versions:

- `human.md`: short, the concepts and the result, with figures.
- `llm.md`: everything needed to reproduce it: paths, commands, parameters, file formats.

| chapter | human | llm | one line |
|---|---|---|---|
| 1. Does a system prompt move the scales? | [human](chapters/01_prompt_check/human.md) | [llm](chapters/01_prompt_check/llm.md) | An IB prompt raises IB by 0.9 on 95% of statements. An IH prompt leaves IH flat and lowers IB. |
| 2. First steering, no prompt | [human](chapters/02_first_steering/human.md) | [llm](chapters/02_first_steering/llm.md) | One direction at layer 23 matches the IB prompt with IH unchanged. IH has no clean cell. |
| 3. Is it just agreement? | [human](chapters/03_agreement_or_moral/human.md) | [llm](chapters/03_agreement_or_moral/llm.md) | No: cosine 0.06 with a real agreement direction. Its far side is IH. Answers scatter widely around the line. "Endorse IB, reject IH" lowers both. |
| 4. Chain of thought and disentangling | [human](chapters/04_cot_and_disentangling/human.md) | [llm](chapters/04_cot_and_disentangling/llm.md) | Under the paper's protocol IB steering beats the prompt (6.52 vs 6.14). Walking IB backwards raises IH on 100% of statements. IH minus IB is plain harm acceptance. The cloud around the line is the statements. |
| 5. The reachable plane | [human](chapters/05_reachable_plane/human.md) | [llm](chapters/05_reachable_plane/llm.md) | All steering lies on one IB-vs-IH trade-off line. Raw IB at −8 reaches non-utilitarian consequentialism (equivalence p < 0.001). Both-high and both-low corners are unreached. |
| 6. Off the line | [human](chapters/06_off_the_line/human.md) | [llm](chapters/06_off_the_line/llm.md) | Directions built from the model's own accepting vs rejecting answers are nearly orthogonal (cos 0.2). The IH one raises IH by 1.8 with IB unchanged. Both-high reached; both-low still not. |
| 7. Two axes | [human](chapters/07_two_axes/human.md) | [llm](chapters/07_two_axes/llm.md) | A 5x5 grid of the two answer-built directions spans IB 1.5 to 6.8 and IH 1.1 to 5.2 with controls intact. A quadratic surface (r = 0.97) is inverted for each human group: every group is approached within 0.5 to 1.0 points with controls intact; none is statistically equivalent under the strict spreads; low IB with medium IH is the unreachable corner. |
| 8. Final placement | [human](chapters/08_final/human.md) | [llm](chapters/08_final/llm.md) | Ten iterations, controls under chain of thought. Lay population reached and statistically equivalent (p = 0.002); every other group within 0.5 except act utilitarianism. Raising IH also raises acceptance of pointless harm; the fast readout had hidden it. |
| 9. Cleaning the axes | [human](chapters/09_cleaning_the_axes/human.md) | [llm](chapters/09_cleaning_the_axes/llm.md) | Projecting a "pointless harm" direction out of IH removes IH gain and harm gain in the same proportion: in this model the IH axis is a harm-acceptance axis. |
| 10. Qwen2.5-7B-Instruct | [human](chapters/10_qwen7b/human.md) | [llm](chapters/10_qwen7b/llm.md) | The pipeline runs unchanged. Directions near-orthogonal (cos 0.12), layer 18 of 28; each axis moves 2 to 2.5 points. The reachable region is a curved band that passes above the lay and deontological groups (low IB with medium IH not reached), IH saturates near 5, and a < −6 breaks the controls. Only the Kantian group is within 0.5, in the broken regime. |

Also: [`PIPELINE.md`](PIPELINE.md), the curated pipeline with its options, and
[`paper/draft.md`](paper/draft.md), the manuscript draft.

Shared material: [`figures/`](figures/), the repo's `data/ggb/` (statements, controls, prompts),
`results/` (raw outputs, not in git), `world_knowledge/` (papers and the benchmark code).
