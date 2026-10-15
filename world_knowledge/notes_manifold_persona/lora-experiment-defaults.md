# Persona LoRA — fixed defaults

Everything here is the default for experiment 1A. Changing any of it means a new run
label, not an edit. Decided 2026-08-05.

## Model

`Qwen/Qwen2.5-3B-Instruct` — 36 layers, hidden 2048, vocab 151,936. Same model as the
role cloud, so activations are directly comparable to everything already measured.
0.5B is for smoke tests only and is not a result.

## Personas — 8

Chosen by k-medoid (`manifold/subsets.py::kmeans_medoid_roles`) on the **clean** 3B role
cloud, with `default` forced in as the neutral baseline. Selection is a measurement, not
a hand-pick, so it is reproducible and reportable.

Not 276: with 276 a failure cannot be attributed — "adapter too small" and "personas do
not share structure" look identical. 8 spread personas is the capacity question at its
cleanest.

**Known bias, deliberate:** maximally-spread personas bias *against* finding shared
structure. A contrast set of 2–3 near-neighbours of one medoid is a follow-up, not part
of the default.

Each persona uses **instruction phrasing 0** of its role file. The other 4 phrasings are
held out — they are the test of whether the adapter learned the persona or the string.

## The adapter — conditional LoRA

```
ΔW_p = B · diag(s_p) · A
```

`A ∈ R^{r×d}` and `B ∈ R^{d×r}` shared across all personas; `s_p ∈ R^r` one gain vector
per persona. `k` personas cost `r·k` extra parameters over a single LoRA.

This is the minimal conditional adapter, and it makes Q3 constructive: if it trains, the
personas share a subspace and differ only in coordinates. Fallbacks in order, each
localising where sharing breaks: per-persona `B_p` with shared `A` (same features read,
different write), then shared `B` with per-persona `A_p`.

Applied to attention and MLP projection matrices, following Persona Cartography.
Persona selected by tag at train time; the input-conditioned gate `s(x) = MLP_φ(tag)` is
experiment 1B, not the default.

## Loss

```
L = KL( p_teacher(·|P,x,t) ‖ p_student(·|x,t) )  +  β · Σ_ℓ w_ℓ · ‖h_ℓ^stu − h_ℓ^tea‖² / ‖h_ℓ^tea‖²
```

- **Forward KL**, teacher → student. Identical in gradient to full-vocab soft
  cross-entropy (`CE = KL + H(p_teacher)`, and `H` does not depend on θ); KL is reported
  because it has a meaningful zero. Reverse KL / on-policy (GKD) is a later variant.
- **Every response token**, teacher-forced — not just the first. Question tokens carry
  almost no persona signal.
- **No KD temperature** (τ = 1). Teacher and student are the same network; we want an
  exact match, not a softened one.
- **Per-layer normalisation is not optional.** `‖h‖` runs 0.44 → 91 across depth, so
  unnormalised MSE is entirely late layers.
- `β = 0.1`, `w_ℓ = 1`. The **per-layer residual after training is the readout for the
  layer question** — where the adapter cannot match is where the persona lives.

## Teacher

The same frozen base model with the persona system prompt prepended — with LoRA that is
literally the student with the adapter disabled, so there is **no second model in
memory**. The persona KV cache is computed **once per persona** and reused for every
question and every step.

Positions: teacher sees `[P; q; r]`, student sees `[q; r]`. Matching is by **relative
index over response tokens**. The absolute-position offset is inherent (that is the RoPE
issue Experiment 1 had to control for) and means an exact match may be unreachable at
early layers — expect a nonzero floor, and report it rather than tuning it away.

## Training data

240 shared extraction questions (`refs/assistant-axis/extraction_questions.jsonl`), split
**192 train / 48 held-out**, seed 0, same split for every persona and every cell.

Teacher responses generated once per (persona, question) with the persona prompt:
temperature 0.3, top-p 0.9, max 256 new tokens. Low temperature by decision — the target
is the persona's typical behaviour, not its tail. Generated once and cached to disk;
every sweep cell trains on identical targets.

## The sweep — 28 cells

| axis | values |
|---|---|
| rank `r` | 1, 2, 4, 8, 16, 32, 64 |
| placement | all 36 · early (1–12) · middle (13–24) · late (25–36) |

Array `0-27%10` — never more than 10 concurrent, by instruction.

**Parameter-count confound, stated up front:** a third-of-the-stack cell at rank `r` has
~⅓ the parameters of an all-layers cell at the same `r`. Every cell logs its trainable
parameter count, and placement comparisons are read against the rank curve, not across
it at fixed `r`.

Fixed for all cells: seed 0, AdamW, lr 1e-4, cosine schedule, 10% warmup, bf16.

## Metrics

Primary: **held-out KL to the prompted model**, per persona, on the 48 held-out questions.
Secondary: per-layer activation residual (the layer readout); tag fidelity (does the
adapter respond to the tag, or has it collapsed to the mixture mean); trainable parameter
count.

Two controls, both required before any of it means anything:

1. **Prompted ceiling** — the teacher itself; KL = 0 by construction.
2. **Shuffled-tag floor** — same adapter trained with persona↔tag assignment shuffled.
   Anything the adapter achieves above this is not persona learning.

## Storage — cluster

| what | where | why |
|---|---|---|
| code + venv | `/home/mind/gmarraff/repos/manifold-persona` | $HOME, 50G quota, small |
| HF model cache | `/scratch/gmarraff/hf_cache` | large, regenerable |
| clouds, adapters, runs, logs | `/data/parietal/store3/work/gmarraff/manifold-persona/` | team store, 26T free |

**Never** `/data/parietal/scratch` — ~98% full and the first mount to degrade the NFS
system under load. Nothing runs on the login node; everything is `sbatch`.
