# The LoRA path — what's already answered, and what to run

Follow-up to [`about-the-definition-of-a-persona.md`](about-the-definition-of-a-persona.md) §7A.
Three questions from the mentor discussion, checked against the two papers, with a
verdict and a plan for each.

Papers checked:

- **PC** — Persona Cartography: Charting LM Personality Traits in Weight Space
  (Baines et al., arXiv:2607.07916, Jul 2026). `docs/papers/2607.07916.pdf`
- **PV** — Persona Vectors (Chen et al., arXiv:2507.21509). `docs/papers/2507.21509.pdf`

**What PC actually does**, since all three verdicts depend on it: trains one LoRA per
trait *and polarity* (10 total: OCEAN × amplify/suppress), rank 64, α = 128, applied to
**all attention and MLP matrices**, via constitution-guided DPO distillation plus an SFT
stage. Six models, 4B–32B; Llama-3.1-8B-Instruct is the default. Personas are composed at
inference by **summing the ΔW of several adapters elementwise**. A neutral control adapter
(same pipeline, seed-only preference pairs) isolates trait effect from DPO artefacts.

**What PV does with LoRA:** nothing representational. LoRA (rs-LoRA, rank 32, α 64) is
only the *tool* used to finetune models into exhibiting a trait, so the trait shift can be
studied in activation space. PV's persona is a **1-D activation direction at one selected
layer** (layer 20 of Qwen for both evil and sycophancy), chosen by sweeping candidate
vectors per layer and keeping the one that steers best.

---

## Q1 — Can we train one LoRA to switch between personas?

### Verdict: not answered.

PC composes, it does not switch. Persona choice happens *outside* the model, by deciding
which ΔW to load or sum; the adapter itself is a fixed linear map with no input dependence.
There is no experiment anywhere in PC where one set of weights produces different personas
for different inputs.

This matters more than it looks, because of our own Experiment 1: the true prefix-induced
shift is **not** a gated constant (SV1 = 0.24, ~10 effective directions, and *more* spread
out than the null). A plain LoRA is an input-independent linear map — the same object class
Experiment 1 just rejected, one step less wrong than a single steering vector. So Q1 is not
only unanswered, it is the question that decides whether §7A is viable at all.

Closest prior art, both from the §7A note: **Text-to-LoRA** (Sakana AI, ICML 2025), a
hypernetwork emitting a task LoRA from a text description — amortises training but still
emits a *static* adapter per persona; and **ReFT/LoReFT**, low-rank learned interventions
on hidden states.

### Experiment 1A — conditional persona LoRA

Train **one** adapter on a mixture of `k` personas where the system prompt carries only a
short persona tag (`[persona: pirate]`), and the target is that persona's behaviour.

- **Design.** `k = 4–8` roles from `refs/assistant-axis/roles/`. Distillation loss from
  §7A: `min_θ E_x KL( p(·|persona,x) ‖ p_θ(·|tag,x) )`, teacher = the same base model with
  the full system prompt. No new teacher model needed — the teacher is the prompted model.
- **Baselines, all required.** (i) `k` separate per-persona LoRAs of the same total
  parameter budget; (ii) the prompted model (the ceiling — it *is* `f`); (iii) a tag-only
  control adapter trained with shuffled tag↔persona assignment (the floor).
- **Measure.** Per-persona KL to the prompted model on held-out questions; trait-expression
  score; and **tag fidelity** — does the adapter actually respond to the tag, or has it
  collapsed to the mixture mean? Test with tags held out from a persona's own questions.
- **The real readout.** Capacity curve: KL-to-prompted as a function of `k` at fixed rank.
  If one adapter holds 8 personas as well as 8 adapters do, personas share weight-space
  structure. If it degrades from `k = 2`, they do not, and switching needs a gate.

### Experiment 1B — gated LoRA, only if 1A degrades

`Δh(x) = λ_φ(x)·BAh` with a tiny gate `λ_φ` reading the tag (or the prefix activations).
This is the LoRA analogue of the `λ(x)` in §6 that a real prefix gets for free. Compare
against 1A at matched parameter count. Experiment 1's rejection of the gated-constant model
predicts a *gate alone* is insufficient — the direction moves too, so expect a gated LoRA
to beat plain LoRA but still fall short of the prompted ceiling. Measuring that gap is the
point.

**Cost:** `k` × a few hundred distillation steps at 0.5B–3B. Fits one GPU-day.

---

## Q2 — What's the lowest rank, and at which layer does it sit?

### Verdict: rank is partially answered. Layer is not answered at all.

**Rank — partial (PC Appendix H).** They SVD-compress each trained rank-64 adapter down to
**rank 1** and run TRAIT + MMLU sweeps; trait-modifying behaviour is "still largely
present" (Figures 56–57). Three caveats: it is *post-hoc compression of a rank-64 adapter*,
not training at low rank; the claim is qualitative, with no threshold and no per-trait
breakdown; and capability cost at low rank is not quantified against the control adapter.
They also note PV models personas as 1-D activation vectors, which is the motivation.

**Layer — absent.** PC applies LoRA to *all* attention and MLP matrices and never ablates
placement. The only layer statement in the paper is Appendix J's activation *capping*,
applied to "the final 40% of layers" — and that is a downstream inference-time intervention
on the residual stream, not a claim about where the adapter needs to be. PV selects a layer
(20 for Qwen) but for activation-space vectors, chosen by steering score. **Nobody has
asked where in *weight* space a persona lives.**

### Experiment 2A — rank floor, trained not compressed

Train adapters at `r ∈ {1, 2, 4, 8, 16, 32, 64}`, everything else fixed.

- Plot KL-to-prompted and trait score vs `r`. The knee is the honest rank floor.
- Compare **trained rank-`r`** against **rank-64-then-SVD-to-`r`** at each `r`. If trained
  low-rank wins, PC's Appendix H understates how compact a persona is; if compression wins,
  the extra rank is doing optimisation work, not representation work.
- Include the control adapter at every rank — the floor for "any DPO/distillation at all".

### Experiment 2B — where the persona lives in weight space

Two complementary sweeps:

1. **Placement.** Train with the adapter restricted to one contiguous block of layers
   (early / middle / late thirds; then single layers), at fixed total parameter count.
   Report trait score and KL-to-prompted per placement. This is the direct answer to "at
   which layer does it sit".
2. **Ablation of a trained full-stack adapter.** Take PC-style all-layer adapters and zero
   ΔW layer by layer, measuring trait score after each. Gives a per-layer importance profile
   without retraining.

**Prediction worth stating in advance**, so it can be wrong: PV finds the activation-space
persona direction most informative around ~0.7 depth, and our own extraction uses layer 26
of 37 for that reason. If weight-space and activation-space personas are the same
phenomenon, placement should peak at similar relative depth. If it instead peaks early, the
adapter is doing input *encoding* rather than persona *expression* — a genuinely different
mechanism and a result in its own right.

**Cost:** 7 ranks + ~6 placements ≈ 13 short training runs per persona. Do it for 2–3
personas first.

---

## Q3 — Do per-persona LoRAs share representations, and sit at the same layer?

### Verdict: partially answered, at a resolution too coarse to settle it.

**What PC has (Appendix D, "Flattened Weight Space Analysis").** They flatten and
concatenate every ΔW in the model into one vector per adapter, then:

- **Table 1:** Frobenius norms lie in 6.078–6.529 — all ten adapters have essentially the
  same magnitude in weight space.
- **Figure 15:** cosine similarity matrix. Each amplifier has **negative** cosine with its
  own suppressor (as it should, if the pair is a signed axis). Cross-trait cosines are
  small, ~0.06–0.14. Their own words: adapters with high cosine similarity "may or may not
  have behavioural similarities, **this needs further work**."
- **Main text:** "Learned directions are not perfectly orthogonal"; the adapters "do not
  form a perfectly orthogonal or globally linear basis", but compose approximately additively
  over practical scaling ranges, with deviations from additivity that are "themselves
  informative".

**Why that does not answer the question.** A cosine between two flattened whole-model
vectors is the wrong statistic for a *low-rank* object. Two adapters can write into the
exact same rank-64 subspace with different coefficients and still show near-zero flattened
cosine. The right object is the **subspace** each adapter spans per module — column space of
`B`, row space of `A` — compared with **principal angles / Grassmann distance**. And it is
one number for the entire model, so it cannot say whether sharing is concentrated in some
layers and absent in others. The "same layer?" half of Q3 is untouched.

### Experiment 3A — per-layer subspace overlap

For every pair of persona adapters, per layer `ℓ` and module `m`:

- principal angles between `col(B_ℓm)` for the two adapters; report `mean cos²θ` (the
  fraction of one subspace captured by the other) and the Grassmann distance;
- the same for `row(A_ℓm)`, which answers a different question — `A` is what the adapter
  *reads*, `B` is what it *writes*. Shared `A` with different `B` would mean personas read
  the same features and act differently; the reverse would mean different triggers, common
  output channel.

Then do exactly what this repo already does to activation clouds: **stack the per-layer
overlap matrices and look at the geometry of adapter space** — intrinsic dimension of the
set of persona adapters, and whether `default`/neutral sits at the centre as the Assistant
Axis claims for activations.

**Controls that decide whether any of it means anything:** (i) `n` control adapters trained
with the same pipeline and *no* trait signal — their pairwise overlap is the floor, since
any two adapters trained on the same data share optimisation-driven structure; (ii) two
adapters for the *same* persona at different seeds — the ceiling. Overlap only counts as
"shared representation" if it sits meaningfully above (i). PC has the control adapter
already, but never uses it this way.

### Experiment 3B — same layer?

From 2B's per-layer importance profile, computed for each persona separately: do the
profiles peak at the same depth? Correlate the profiles pairwise. A shared peak with low
subspace overlap is the interesting outcome — same *place*, different *directions* — and is
the weight-space analogue of the low-dimensional-manifold picture.

**Cheap first pass:** 3A needs no training beyond the adapters from Q2, and is pure linear
algebra on saved weights. Run it the day the adapters exist.

---

## Order to run

1. **2A rank sweep** — cheapest, and every later experiment needs to know the rank floor.
2. **3A subspace overlap** — free once 2A's adapters exist, and directly tests the shared-
   representation claim PC left open.
3. **2B placement** — the genuinely unanswered structural question.
4. **1A conditional LoRA** — the most expensive and the one whose result matters most, since
   Experiment 1 already predicts a static adapter is the wrong object class.

## Two things to settle before writing any training code

- **Which personas.** PC uses OCEAN traits; we have 276 character roles. Roles are richer
  and match our existing cloud, but OCEAN is what PC measured, so a shared subset makes our
  numbers comparable to theirs. Suggest: run on roles, plus 2 OCEAN traits for calibration.
- **Evaluation.** PC leans on an LLM judge plus the TRAIT benchmark. KL-to-prompted needs no
  judge and is the quantity §7A actually defines — make it the primary metric, and keep a
  judge score only as a secondary sanity check.
