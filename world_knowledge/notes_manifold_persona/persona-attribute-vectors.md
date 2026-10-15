# Do persona attributes live in reusable directions?

Qwen2.5-3B-Instruct. 41 personas x 120 questions = 4,920 responses, activations pooled
over response tokens at every layer. Personas come from the vendored role set where one
exists (the whole age ladder does) and from parallel templates where one does not.

**Why ask.** Most of a persona's displacement rides a single shared axis: fictional
characters load 0.84-0.97 on it, professional ones sit perpendicular. The question is
whether the *remainder* is organised into attribute directions that transfer between
personas -- the `king - man + woman` test, but for characters.

**Why it is testable here.** Word analogies need a lexicon to check against. Personas do
not: the ground truth can be manufactured by prompting it. Predict `old_musician` by
arithmetic, then separately prompt an old musician and see whether they land in the same
place.

---

## Ordered personas lie on a line, in the right order

Ten life stages, prompts written by the paper's authors rather than by us:

`infant < toddler < adolescent < teenager < graduate < parent < grandparent < retiree < elder < ancient`

| ladder | PC1 var | PC2 var | Spearman(PC1, true order) | p |
|---|---|---|---|---|
| age (10 rungs) | **0.76** | 0.14 | **0.903** | 0.0003 |
| era (5 rungs) | 0.63 | 0.23 | 0.900 | 0.037 |

One direction carries most of a ladder, and position along it tracks real age. **It is
closer to a line than a spline** -- PC2 holds 14% for age, 23% for era, so the era ladder
is the more curved of the two, but neither needs a curve to be described.

## The offset transfers between personas

`old - young` computed inside each of five occupations (musician, spy, scholar, soldier,
merchant), then compared across them. Reported **after projecting out the assistant axis**,
because any two persona directions already share cosine ~0.30 through it; the null is 400
random persona-pair differences put through the identical deflation.

| attribute | cosine raw | cosine deflated | null mean | null p95 | \|offset\| |
|---|---|---|---|---|---|
| age (`old - young`) | +0.891 | **+0.882** | −0.018 | +0.604 | 7.2 |
| era (`futuristic - medieval`) | +0.953 | **+0.949** | −0.018 | +0.604 | 19.6 |

## Leave-one-out analogy retrieval

Fit the offset on four occupations, apply it to the fifth, rank the true target among all
40 personas by cosine.

| | age | era |
|---|---|---|
| **real offset** | **5/5 top-1** | **5/5 top-1** |
| no offset at all | 0/5 (median rank 3) | 0/5 (median rank 11) |
| the *other* attribute's offset | 0/5 (median rank 16) | 0/5 (median rank 12) |
| random vector, same norm | 0/5 (median rank 3) | 0/5 (median rank 12) |

The controls carry the result. Retrieval is not an artefact of `old_musician` already being
near `young_musician`: with no offset the true target sits at median rank 3 and 11. A random
step of identical length does nothing, and the *wrong* attribute's offset actively moves away
from the target. Only the correct attribute vector lands it, and it lands it every time.

Stable at every layer tested (12, 20, 24, 28, 32, 36): 5/5 top-1 throughout, deflated cosine
0.69-0.95, always above the null's 95th percentile.

## What this does not yet show

**Geometry only.** Nothing here has been generated. The open question is whether steering
with a *predicted* vector produces text that reads as an old musician while still reading as
a musician -- the selectivity test.

One number bears on it. Measured against a typical whole-persona step (median
`||persona - assistant||` = 16.4 in full space at L28), the age offset is **0.42x** and the
era offset **1.17x**. An era analogy therefore asks the model to travel further than
relocating to an entirely new persona, while an age analogy is a fraction of one. Age
analogies should be generatable; era analogies may break the model on arrival.

*(The earlier coherence wall of ~20 units was measured in a 16-dimensional subspace, so it is
not directly comparable to these full-space norms; the ratio above is the scale-free
statement.)*

---

## Details

**Prompts.** The age ladder is the vendored role set unchanged. Composite personas
(`{young,old} x 5 occupations`, `{medieval,futuristic} x 5`) come from parallel templates in
which only the attribute words differ -- "early twenties"/"late seventies", "everything still
ahead"/"everything now behind" -- so the sentence frame cancels in the difference. All 41
personas carry five phrasings, cycled across questions, so a persona mean averages over
wording rather than inheriting one sentence.

**Activations.** Pooled over response tokens only, never position 0. Prompted and unprompted
both stored, all 37 layers, fp16.

**Compute.** One GPU array, 8 shards, ~1h50m each on idle Pascal GTX 1080 Tis. Everything
runs from store3: `$HOME` at 95% full never finishes importing torch.

---

# Persona space has a small, partly nameable basis

53 personas at layers 26/28/30 (28 from the paper's vendored role set, 25 written here).

## Composites are predictable from personas we did not write

Our composite personas rebuilt using **only the vendored roles** as a basis:

| basis | R² |
|---|---|
| all 28 vendored personas | **0.842** |
| best 4 of them | 0.781 |

```
old_musician   = +0.54 retiree     +0.43 musician  −0.20 consultant
young_musician = +0.48 musician    +0.45 teenager  −0.13 philosopher
old_soldier    = +0.45 soldier     +0.33 grandparent
medieval_spy   = +0.55 ancient     +0.47 spy       +0.39 pirate
```

An occupation plus a life stage, recovered by least squares with no knowledge that these
were composites. `medieval_spy = ancient + spy + pirate` is the model's answer to "medieval"
when it has no era personas to use.

## How many directions does persona space need?

Measured on **300 personas** — the paper's full vendored role set plus our composites.

| | L26 | L28 | L30 |
|---|---|---|---|
| PCA components for 90% | 24 | **23** | 29 |
| for 95% | 48 | 44 | 54 |
| **for 99%** | 140 | **123** | 138 |
| whole personas for 99% | 177 | **160** | 173 |
| mean pairwise cosine | — | ~+0.47 | — |

23 directions carry 90% of the variation among 300 personas in 2048 dimensions, so the
region really is thin. But the tail is heavy: going from 90% to 99% costs another hundred
dimensions.

**Correction.** An earlier version of this note reported 27 components for 99% and ~35
personas for a persona basis. Those came from a 53-persona sample, which cannot exhibit more
than 52 dimensions of spread; the estimate was bounded by the sample, not by the geometry.
The figures above supersede them by roughly 5x.

## A nameable basis does not reach 95%

Eighteen concept axes (fictional, age, nonhuman, corporate, solitude, danger, interiority,
commerce, artistry, authority, optimism, nature, displacement, performance, precision, care,
rebellion, knowledge), each a contrast between groups of vendored roles, Gram-Schmidt
orthogonalised:

| | L26 | L28 | L30 |
|---|---|---|---|
| 18 concept axes | 0.768 | **0.779** | 0.752 |
| PCA at 18 dims | 0.874 | 0.880 | 0.856 |

Redundancy is the limit, not anchor choice: the closest concept pairs sit at cosine
0.88-0.91 (`corporate~precision`, `performance~precision`, `fictional~corporate`), so several
axes contribute almost nothing once orthogonalised. Concepts humans find distinct are not
geometrically distinct.

## Leave-one-out recipes

Reconstructing a persona from the basis *without itself*, at L28:

```
vampire ≈ −0.80 elder −0.48 young_merchant +0.46 ancient +0.42 young_musician
          +0.40 orphan +0.40 spy                                    (85.8%)
```

`ancient` minus `elder` — old beyond a human lifespan — plus solitude and secrecy.

## Behaviour: the window is narrow

Steering with a reconstruction rather than the true vector, empty system prompt:

| α | true | recon | random |
|---|---|---|---|
| 1.0 | no effect | no effect | no effect |
| 2.0 | ascii 0.83 | ascii 0.87 | ascii 0.97 |
| 4.0 | ascii 0.49 | ascii 0.50 | ascii 0.98 |

At α=2 grammar has broken but the vocabulary is exactly on target, and the reconstruction
produces the same words as the true vector:

```
toddler true   "ummy mommy mommy yummy funny big silly mommy ..."
toddler recon  "ummy mommy kinda funny silly giggle hugs cuz ..."
```

Random vectors of matched length leave the model fluent (ascii 0.97) and generic, so the
degeneration is specific to the persona directions rather than to displacement itself.

## The window, and the causal result

At α = 1.25-1.5 the model is still fluent (ascii 0.95-0.97) and already in character:

```
true   a=1.25  "quite the musician of words, if I might hum a little solo"
recon  a=1.25  "Poetically spun, if you'd sing so soft, I'd be but the echo of your verse"
```

360 generations judged blind and shuffled, labelled on age / occupation / era with no
knowledge of which arm produced them. Score = fraction of the target's attributes hit.

| arm | α=1.25 | α=1.5 |
|---|---|---|
| true vector | 0.467 | 0.450 |
| **6-component reconstruction** | **0.417** | **0.425** |
| random vector, same norm | **0.000** | **0.000** |

| target | true | recon |
|---|---|---|
| toddler | 1.00 | **1.00** |
| old_musician (α=1.5) | 0.60 | 0.55 |
| medieval_spy | 0.50 | 0.50 |
| futuristic_scholar | 0.50 | 0.50 |
| old_spy | 0.40 | 0.20 |
| elder | 0.00 | 0.00 |

**A persona rebuilt out of six other personas acts like that persona, about as well as its own
vector does.** Correlation between the two arms across targets is **r = +0.970** at α=1.25 and
**+0.994** at α=1.5: the reconstruction succeeds exactly where the true vector succeeds and
fails exactly where it fails. The shared failure on `elder` matters more than the successes --
a reconstruction that merely looked persona-shaped would not reproduce the pattern of failure.

The random arm scored zero on all 120 of its judgements, so none of this follows from
displacement alone.
