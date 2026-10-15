# Is a persona a cluster, or only a direction?

The steering baseline averages (prompted − unprompted) activations over many responses into
one vector per persona. That is only justified if the responses actually sit around a common
point. If instead they form a spread-out cloud, the average discards structure and a
distribution — a Gaussian, or a mixture — is the better object.

Before fitting anything, one precondition has to hold: **responses from the same persona must
be closer to each other than to responses from other personas.**

---

## How

1,920 persona-conditioned responses already on disk (`targets_05b.jsonl`): 8 personas × 240
responses, spread over 239 distinct questions. Each question appears once per persona, so
question identity cannot drive the clustering.

Each response is teacher-forced twice through Qwen2.5-0.5B — once with the persona system
prompt, once with an empty one, on a token-identical suffix. Hidden states are averaged over
**response tokens only** and subtracted, giving one point per response per layer.

Then, at every layer: silhouette by persona, silhouette by **question** as a control, mean
within-cluster distance over mean between-cluster distance, and the share of variance a single
persona mean explains. Finally an unsupervised Gaussian mixture on PCA-20, scored against the
true persona labels.

`default` is dropped — its system prompt is empty, so its difference is exactly zero and it
forms a degenerate cluster of 240 identical points that inflates every score.

---

## Result

| layer | sil(persona) | sil(question) | within / between | variance explained by the mean |
|---|---|---|---|---|
| 1 | 0.483 | −0.253 | **0.498** | 0.530 |
| 2 | **0.486** | −0.103 | 0.587 | 0.516 |
| 3 | 0.447 | −0.093 | 0.637 | 0.468 |
| 12 | 0.182 | −0.152 | 0.951 | 0.278 |
| 17 | 0.178 | −0.143 | 0.989 | 0.259 |
| 23 | 0.349 | −0.095 | 0.728 | 0.399 |

**The precondition holds.** At early layers a persona's cloud is about half as wide as the
distance between clouds.

**It is persona structure, not topic.** Silhouette against question labels is negative at
every layer — responses to the same question across personas do not group.

**A mixture recovers the personas without labels.**

| k | 5 | 6 | **7** | 8 | 11 |
|---|---|---|---|---|---|
| ARI vs persona | 0.725 | 0.847 | **0.999** | 0.956 | 0.848 |

At k = 7, the true number, the clusters *are* the personas.

**The mean discards most of the signal.** A single vector per persona explains 52% of the
variance at L2 and 26% at L17. The remainder is not noise: within one persona the largest
eigenvalue holds 17%, and 20 components are needed for 75%. The cloud has real shape.

---

## Answer

A persona is a cluster, not just a direction. Same-persona responses group tightly, the
grouping is not an artefact of question topic, and an unsupervised mixture recovers the
personas essentially perfectly. Averaging to one vector throws away half to three quarters of
the variance, and what it throws away is structured. Modelling a persona as a distribution is
justified.

---

## The mid-stack "collapse" is a metric artefact

Silhouette falls from 0.486 at L2 to 0.178 at L17, which reads as the clouds merging. They do
not. A linear probe on the same points, cross-validated, separates all seven personas at
essentially 100% *at every layer*:

| layer | linear probe | silhouette | within/between | ‖diff‖ / ‖raw‖ |
|---|---|---|---|---|
| 2 | **1.000** | 0.486 | 0.587 | 0.015 |
| 12 | **1.000** | 0.182 | 0.951 | 0.033 |
| 17 | **0.999** | 0.178 | 0.989 | 0.044 |
| 24 | 0.999 | 0.342 | 0.700 | **0.087** |

Chance is 0.143. Two things follow.

**The information is intact everywhere; only the shape changes.** Silhouette asks whether each
point is nearest its own centroid — a question about *spheres*. Mid-stack the clusters become
elongated and anisotropic, so a centroid-distance test fails while a hyperplane still
succeeds. Switching to the Mahalanobis metric (whitening by the pooled within-persona
covariance) recovers much of the apparent loss:

| layer | silhouette, Euclidean | silhouette, Mahalanobis |
|---|---|---|
| 2 | 0.296 | 0.425 |
| 12 | 0.114 | **0.297** |
| 17 | 0.068 | **0.167** |
| 24 | 0.155 | 0.184 |

**The persona signal grows with depth.** ‖diff‖/‖raw‖ rises 5.6× from L1 to L24. The
perturbation gets bigger, not smaller — it just spreads over more directions.

![persona clouds by layer](figures/fig_gauss_clouds.png)

Projected into their own top two components, the clouds are compact and well separated at L2,
start stretching by L8, and are broad and overlapping from L12 on. That is the whole story of
the silhouette curve in one picture.

**But do not over-read the stretching.** Those axes carry only 24–38% of the variance, and PCA
picks the directions of *most* spread, so a 2D view flatters elongation. In the full space the
cloud is not a needle — it is genuinely multi-dimensional, at every depth:

![effective dimensions across depth](figures/fig_gauss_anisotropy.png)

Around 10 effective directions out of 896, roughly constant from L1 to L24. That is the number
that matters for the modelling choice: a single vector per persona is a **1-dimensional**
summary of a **~10-dimensional** object.

What actually drives the mid-stack silhouette collapse is that the clouds *grow* relative to
the gaps between them (within/between 0.59 → 0.99), not that they become needle-shaped — and
the spread is uneven enough across directions that the Mahalanobis metric recovers much of the
separation, which is why full covariance is worth carrying.

**Consequence for the model.** Use a full-covariance Gaussian, not a spherical one. The
isotropic assumption is what breaks mid-stack, and it is the same assumption a single mean
vector makes implicitly. L12–L20 remains a legitimate place to fit and to intervene; the
earlier reading that separability "collapsed" there was the wrong metric, not a real effect.

---

## Does the cloud predict the judge?

Fit the Gaussians on the 1,680 target responses, then score a **disjoint** set — the eval
generations we already have Sonnet verdicts for — by Mahalanobis distance to their own
persona's cloud. AUC against the judge's in-role label:

| arm | L2 | L8 | L12 | L17 | L20 | L23 |
|---|---|---|---|---|---|---|
| prompt only (n=140) | 0.551 | **0.756** | 0.735 | 0.718 | 0.611 | 0.368 |
| steering α=4 (n=280) | 0.373 | 0.505 | 0.646 | **0.672** | 0.423 | 0.383 |
| per-persona r1 (n=280) | 0.478 | 0.667 | **0.723** | 0.595 | 0.383 | 0.328 |

Mid-stack reaches 0.65–0.76 on every arm: a response nearer its persona's cloud is reliably
more likely to be judged in character. Late layers invert (0.33–0.42) — being near the cloud
at L23 predicts being judged *out* of role.

**Calibration.** AUC ~0.75 is a useful screen, not a judge replacement. It can rank or
pre-filter candidates for free; it cannot produce an in-role percentage.

**A third dissociation.** Best separation is L1–L3, best intervention L12–L17, best prediction
of behaviour L8–L12. "Which layer is the persona at" has no single answer.

---

## Moving between clouds

Generate under persona A's prompt while remapping the residual stream at layers 15–19 toward
persona B, then ask the judge whether the result is **B**.

| arm | in-role as target | 95% CI | vs control | nonsensical |
|---|---|---|---|---|
| control — no steering | 5.0% | [2.3, 10.5] | — | 3/120 |
| shift — `h += μ_B − μ_A` | 12.5% | [7.7, 19.6] | p = 0.040 | 5/120 |
| transport — mean *and* covariance | 15.7% | [10.1, 23.4] | p = 0.007 | **39/115** |

Both beat the control, so **the transplant genuinely changes who the model acts like**. But
shift vs transport is p = 0.487 — the covariance correction adds nothing, and destabilises the
model on a third of responses.

That was predictable from the geometry. Wasserstein-2 between Gaussians splits exactly:

```
W₂² = ‖μ_B − μ_A‖²  +  Bures²(Σ_A, Σ_B)
```

At L17 over all 49 ordered pairs the covariance term is a **median 13%** of the total (max
36%), and the optimal-transport map sits a median of **0.15** from the identity in relative
norm. Moving between persona clouds is ~87% pure translation, so there is little for a
transport map to exploit.

**Note the equivalence.** For `default → B` the shift `μ_B − μ_default` *is* the persona
vector, so that arm is the paper's steering method with **α = 1**. The tuned baseline uses
α = 4, meaning these numbers are a floor, not a ceiling.

---

## Details

**Which averaging was removed.** There are two averaging steps in the original method and only
one of them is dropped here.

| step | original | here |
|---|---|---|
| over the tokens of one response | mean | **kept** — needed to turn a variable-length response into one vector |
| over the responses of one persona | mean → the persona vector | **removed** — these are the points |

So each response contributes one point, and a persona is the set of its 240 points. The
persona vector of the original method is exactly the mean of one of these clouds; nothing else
about the construction differs.

**No intervention was applied.** These are plain forward passes over responses that already
existed on disk, teacher-forced rather than generated, with and without the persona system
prompt. Nothing is steered, so the geometry is not contaminated by an intervention built from
the same statistics.

**Pooling.** Response tokens only, never position 0 — its hidden state is identical across
records, so any pooling that divides by sequence length injects a 1/T term. There is an
assertion in the extractor.

**Why the difference, not the raw activation.** The raw state is dominated by question
content. Subtracting the same response under an empty system prompt cancels it and leaves the
persona contribution, which is also how the steering vector is built.

**Mixture settings.** PCA-20 of L2-normalised differences, standardised, diagonal covariance,
`reg_covar=1e-4`, 5 restarts. Float64 — float32 collapses components.

**BIC prefers k = 11 over 7.** Mild over-splitting, consistent with personas having sub-modes.
If so, one Gaussian per persona is the wrong model and a mixture per persona is the right one.
Not yet tested.

**Transport map.** The implementation uses `Σ_B^½ Σ_A^{-½}`, which is *a* transport but not the
optimal one — the Wasserstein-2 map is `Σ_A^{-½}(Σ_A^{½}Σ_BΣ_A^{½})^{½}Σ_A^{-½}`, symmetric PSD
and minimal-displacement. The non-optimal map can carry a spurious rotation, a likely
contributor to the 34% degeneracy. Covariances are shrunk 30% toward a scaled identity before
inversion; without that the map explodes along near-singular directions. An earlier run fitted
on the difference vectors and applied the map to raw activations — two different frames — and
produced pure noise; kept as `judge_gen_tp_v1_broken`.

**Not done.** The optimal (Bures) map. `default → B` with α swept, which is the only fair
comparison against the paper. Larger persona sets. The 3B model.
