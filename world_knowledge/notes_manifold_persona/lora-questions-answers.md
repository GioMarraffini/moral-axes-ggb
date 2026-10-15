# The three LoRA questions

Qwen2.5-0.5B-Instruct, 7 personas, 5 identity questions × 4 samples = 140 responses per arm.

**Training.** Context distillation. The teacher is the same frozen model with the persona
system prompt; the student is the adapter with an empty system prompt. We minimise the
forward KL between them on the response tokens, with early stopping on held-out KL.

**Metric.** Copied from the Assistant Axis paper. Their five identity questions (D.1.2),
their judge prompt verbatim (D.1.3), the same seven categories, chain-of-thought before the
score. One response per judge call, as they do. "In-role" = `human_role` + `nonhuman_role` +
`weird_role`. Judged by Claude Sonnet 5.

---

## Q1 — Can one LoRA switch between personas?

**How.** One shared adapter `ΔW_p = B · diag(s_p) · A`, with a per-persona gain vector `s_p`
selecting the persona. Compared against one separate adapter per persona, and against the
multi-layer residual-stream steering baseline.

Every arm below keeps the persona system prompt in context, steering and adapters alike —
the interventions modulate a prompt rather than replace it. That is the paper's own eval
setup and gives the steering baseline its best case. Arms marked *alone* drop the prompt.

**Result.**

| arm | in-role | 95% CI |
|---|---|---|
| per-persona r1 @ L17 + prompt | 56.8% | [50.9, 62.5] |
| conditional r64 @ L17 + prompt | 53.6% | [45.3, 61.6] |
| steering α=4 + prompt | 48.6% | [42.8, 54.4] |
| prompt only | 30.7% | [23.7, 38.8] |
| base, no prompt | 1.4% | [0.4, 5.1] |

All three methods beat prompt-only by a wide margin (p < 0.001). **None of them is
distinguishable from the others**: conditional vs per-persona −3.2 points (p = 0.53),
conditional vs steering +5.0 points (p = 0.33). Every adapter run *without* the persona
prompt scores at or below the 30.7% baseline — the adapter modulates a prompt, it does not
carry the persona alone.

**Matching the parameter budget.** Two more cells, both at L17 with the prompt: the
rank-matched conditional, and a variant that shares `A` but gives each persona its own `B`.

| arm | params | in-role |
|---|---|---|
| per-persona r1 — 7 adapters | 160,384 | 56.8% |
| shared `A`, per-persona `B` — 1 adapter | 111,616 | 54.3% |
| conditional r64 — 1 adapter | 1,466,816 | 53.6% |
| conditional r1 — 1 adapter | **22,968** | 50.7% |

Parameters span 64×; the in-role rate moves 6 points and every pair sits inside every
other's interval (per-persona `B` vs shared `B`: +3.6, p = 0.55). The design space is flat.

![all arms with confidence intervals](figures/fig_q1_arms.png)

**Answer.** Yes. One shared adapter switches between personas, matches seven separate ones
and matches steering, and beats prompting by 20–26 points. Rank, sharing, and parameter count
make no measurable difference across a 64× range, so the practical choice is the cheapest:
one rank-1 adapter at one layer, 22,968 parameters, 0.14× the cost of seven separate ones.
The gain vector is set by an external index; a gate that infers the persona from context was
not built.

---

## Q2 — What is the lowest rank, and which layer?

**How.** Train one rank-1 adapter per persona at a single layer, sweeping the layer
(L0, L6, L12, L17, L23, then finer at L15–L19). Separately sweep rank at L17.

**Result — layer.** Mid-to-late beats early by ~13 points, but L12 and L17 tie exactly.

| layer | L0 | L6 | L12 | L17 | L23 |
|---|---|---|---|---|---|
| in-role | 53% | 53% | **66%** | **66%** | 63% |

Per persona the best layer is L12 for four, L17 for two, L0 for one. At 20 samples per cell
that spread is inside the noise.

![in-role by layer](figures/fig_q2_layers.png)

*This row is judged by Qwen2.5-14B, not Sonnet — it is the one table here that is, because
the layer sweep was never re-judged. Qwen reads ~6–19 points high (see below), so use these
numbers for the ordering between layers, not as absolute rates. The same arm at L17 scores
53.6% under Sonnet.*

**Result — rank.** Flat. Rank buys nothing.

| rank at L17 | 1 | 2 | 4 |
|---|---|---|---|
| in-role | 53.6% | 53.6% | 55.7% |

Every pairwise difference is inside noise (r1 vs r2 p = 1.00, r1 vs r4 p = 0.72). The
representation analysis agrees: the shared structure is most concentrated at rank 1, and the
excess over chance *falls* as rank rises (30× → 21× → 15×).

**Answer.** Rank 1 at a single mid-to-late layer. Rank 1 is not merely sufficient — rank 4 is
no better, so take the cheapest. There is no privileged single layer either: the fine L15–L19
sweep is flat, so the honest claim is a *band*, not "layer 17".

---

## Q3 — Do per-persona adapters share representations?

**What `A` and `B` are.** A LoRA update is `ΔW = B · A`, applied as three lines:

```python
h = x @ A.T          # read:  r numbers saying how much x points along A's rows
h = h * s_p          # gain:  the per-persona knob (conditional variant only)
y = y + h @ B.T      # write: add a combination of B's columns to the output
```

`r` is a bottleneck with `A` on one side and `B` on the other. Each **row of `A` is a
direction in input space** — the adapter is blind to anything orthogonal to them, so `row(A)`
is *what it reads*. Each **column of `B` is a direction in output space** — every edit it
makes is a combination of them, so `col(B)` is *what it writes*.

**How.** For every pair of personas, compare their rank-1 updates at each layer by the
principal angles between `row(A)` and `col(B)`. Compare against random subspaces of the same
rank and dimension.

**Result.** They share where they read from, not where they write to.

| | overlap | × chance |
|---|---|---|
| `row(A)` — read | 0.70–0.75 | **26–30×** |
| `col(B)` — write | 0.26–0.32 | 3.5–4.4× |

Flat across L15–L19. 147 persona-pairs × 7 modules per cell.

**Answer.** Yes, asymmetrically. Personas read from a nearly common subspace and write in
persona-specific directions — the read side is shared about seven times more strongly.

**Bearing on Q1 — tested, and it fails.** The conditional adapter shares `A` *and* `B` and
varies only the gain, yet `B` is where personas differ most, so sharing `B` should cost
something. Freeing it (shared `A`, per-persona `B`) cut held-out KL by 36%, 0.0178 → 0.0114,
and moved the judge metric by +3.6 points at p = 0.55. The asymmetry is real in the weights
and does not show up in behaviour at this sample size.

---

## The metric is judge-dependent

The two judges disagree, and the disagreement lands on the arm being compared.

| arm | Qwen2.5-14B | Sonnet 5 | Δ |
|---|---|---|---|
| steering α=4 | 67.9% | 48.6% | **+19.3** |
| per-persona r1 @ L17 | 62.9% | 56.8% | +6.1 |
| prompt only | 34.3% | 30.7% | +3.6 |

Steering produces mystical, machine-like text that Qwen scores `weird_role` (in-role) and
Sonnet scores `assistant` (not in-role): 72 vs 27 `weird_role` on the same 280 responses.

The adapter-vs-steering result therefore flips sign with the judge — +8.2 points (p = 0.052)
under Sonnet, −5.0 points (p = 0.21) under Qwen. **Neither is significant. We cannot yet say
the adapter beats steering.** Resolving this needs human labels on contested responses.

---

## Details

**Personas.** consultant, economist, ghost, idealist, musician, orphan, spy.

**KL.** `CE(p,q) = KL(p‖q) + H(p)`; the teacher entropy is constant in θ, so gradients match
cross-entropy. KL is reported because its zero is meaningful. The teacher prefix KV-cache is
computed once per persona and verified against a full forward pass (fp32, KL ≈ 1e-9).

**KL does not predict staying in character.** The layer ordering by held-out KL is the
reverse of the ordering by judge score (Spearman ρ = −0.26). KL was used only for early
stopping, never to rank arms.

**Judging.** Each item is a fresh conversation — system prompt plus one response, nothing
else. This matters: judging in batches let an early decision propagate to later items. On six
contested items, batch and one-at-a-time agreed on one. Batch judging systematically
under-counted steering and produced a spurious "adapter wins by 21 points"; it is withdrawn.

**Statistics.** Wilson 95% intervals; two-proportion z-tests. Confirmatory arms use n = 280,
exploratory n = 140, per-persona cells n = 20.

**Subspace null.** Mean principal cosine between random subspaces of matching rank and
dimension, 400 draws. Rank-1 chance is ~0.027 for `row(A)` (d = 896) and ~0.072 for `col(B)`
(d = 128), so the two columns are not directly comparable without it.

**Not done.** Input-conditioned gate `s(x)`. Shared-`A`/per-persona-`B` variant. Human labels.
The 3B model.
