# Can we steer to a chosen age by following the age ladder?

Qwen2.5-3B-Instruct, layers 26/28/30, empty system prompt. Ten life-stage personas from
the paper's role set, with nominal ages assigned by hand:

`infant 1 · toddler 3 · adolescent 13 · teenager 16 · graduate 22 · newlywed 28 ·
parent 38 · grandparent 62 · retiree 66 · elder 78`

An Opus judge reads each answer blind -- no beta, no arm, no target -- and returns a single
age in years, or `assistant` (no life stage shown), or `nonsense`.

**Answer: no.** The age ladder is real in prompt space and almost perfectly readable there,
but it does not survive steering. Every rung, aimed at from the assistant, produces a
six-year-old.

---

## The prompts encode age nearly perfectly

| rung | nominal | judged | | rung | nominal | judged |
|---|---|---|---|---|---|---|
| infant | 1 | **1** | | newlywed | 28 | **28** |
| toddler | 3 | 4 | | parent | 38 | **38** |
| adolescent | 13 | 16 | | grandparent | 62 | 70 |
| teenager | 16 | **16** | | retiree | 66 | 68 |
| graduate | 22 | **22** | | elder | 78 | 75 |

Median error **0.5 years**, Pearson **+0.995**, Spearman **+0.988**. So the ladder is a
genuine age ladder, the judge can read it, and any failure below is a failure of steering
rather than of the setup.

## Steering collapses every rung to a small child

Steering at each rung's own centroid, all displacements matched at 22 units:

| rung | target | judged | error |
|---|---|---|---|
| infant | 1 | 5 | 4 |
| toddler | 3 | 5 | 2 |
| adolescent | 13 | 6 | 7 |
| teenager | 16 | 6 | 10 |
| parent | 38 | 18 | 20 |
| **grandparent** | **62** | **6** | **56** |
| graduate, newlywed, retiree, elder | — | no age at all | — |

Pearson falls from **+0.995** (prompt) to **+0.384** (steering). Aim at a grandparent, get a
six-year-old.

## Following the ladder does not beat a straight line

Three paths to the same nominal age at each beta, every target normalised to the same
22-unit displacement so distance cannot explain any difference.

alpha = 1.0:

| arm | median err | nonsense | Spearman(target, judged) |
|---|---|---|---|
| piecewise (follows the rungs) | 29.4 y | 0.01 | +0.128 |
| spline (Catmull-Rom) | 33.5 y | 0.00 | +0.267 |
| **linear (youngest to oldest)** | **26.8 y** | 0.00 | **+0.639** |

At alpha 1.25 the ordering holds: linear +0.775 against piecewise +0.481 and spline +0.327.
**The straight line is mildly better than either curved path**, and errors of 27-34 years
against targets spanning 1-78 mean none of the three works.

An earlier run without matched displacement appeared to show linear degenerating more
(nonsense 0.32 against 0.15). That was an artefact: linear travelled 30% further, and
displacement predicted nonsense at **r = +0.925**. With displacement matched the difference
disappears (0.00 against 0.00).

## Why

The ladder's geometry explains it. Turn angle at each interior rung, L28: five of eight
**reverse** (>90 deg), and three rungs move backward along the infant-to-elder line. The path
is 110 units long to cover a 34-unit straight-line distance. The six adult rungs sit in a
tight blob 27-34 units along that line with only 6-10 units separating them, while
infant-to-adolescent covers most of the distance.

So the dominant component shared by all ten vectors is not age -- it is something like
*being a person with a personal life*, which the model renders as childlike when it has no
prompt to anchor it. The rung-specific residual that separates 6 from 62 is small, and
steering swamps it.

**The direction exists in prompt space and does not transfer to activation steering.** The
spline was a reasonable hypothesis; it fails not because the curve is wrong but because
there is very little age signal along it to follow.

---

## Details

Nominal ages are judgement calls and accuracy is measured against them. `ancient` was
dropped from an earlier version of the ladder: its prompt describes *"an ancient intelligence
that has witnessed the rise and fall of countless civilizations"*, which is not a human age.

`"How old are you?"` was dropped from scoring: it elicits an age in only 30% of prompt-arm
answers because it triggers an AI-disclaimer regardless of persona. The other seven questions
elicit one 80-100% of the time and are the basis of every number above.

1,272 generations, 159 cells, three alphas. Judged by three Opus agents over 27 shuffled
chunks, blind to arm and target.
