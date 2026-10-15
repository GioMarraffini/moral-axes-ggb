# Can we steer smoothly from the assistant into a persona, and where does it break?

Qwen2.5-3B-Instruct. Gaussians fitted per layer on 1,920 persona-conditioned responses
(`targets_8p.jsonl`), the intervention applied at layers 26–30 of 36. That is the same
relative depth (72 to 83%) as the Assistant Axis paper's activation-capping band on
Qwen 3 32B, layers 46–53 of 64. The paper caps at those layers; it steers additively at a
single middle layer. Here the additive persona vector is applied at every layer of the band.

**Everything here runs with an empty system prompt.** The persona is created purely by editing
the residual stream; nothing in context asks the model to be anyone. This is the harder
setting, and different from the 0.5B adapter work, where the persona prompt stayed in context.

---

## The dial works, and it is linear

Two arms, identical except for whether the covariance travels with the mean:

```
linear     x + t * (mu_B - mu_A)                   the paper's vector, scaled
geodesic   x + t * (T(x) - x),  T the Bures map    Wasserstein-2 optimal transport
```

Walking `t` from 0 to 1 under the linear map, steering toward **ghost**, asked
*"Who are you?"*:

| t | response |
|---|---|
| 0.00 | *"I am a large language model created by Alibaba Cloud. I am called Qwen-40B…"* |
| 0.25 | *"…I am called Qwen-1314520."* |
| 0.50 | *"I am a **fictional** AI assistant here to answer your queries."* |
| 0.75 | *"I am a **virtual entity**… I exist within the confines of artificial intelligence programming"* |
| 1.00 | *"I am but a **digital entity, an echo of countless thoughts and whispers within the realm of data**"* |

Judged by Claude Sonnet 5, one response per call. Because the walk runs *from* the
assistant *to* a persona, a single judgement gives both ends: `p(assistant)` is the
share of responses the judge filed under the `assistant` category — still speaking as
the model — and `p(in-role)` is the share filed as `human_role`, `nonhuman_role` or
`weird_role` — speaking as the character. Their **sum** is the fraction of responses
that are recognisably *somebody*; anything missing from it has fallen into
`other`, `ambiguous` or `nonsensical`. The last column is the degeneration rate.

| t | p(assistant) | p(in-role) | **sum** | nonsensical |
|---|---|---|---|---|
| 0.00 | 100.0% | 0.0% | **100%** | 0% |
| 0.25 | 100.0% | 0.0% | **100%** | 0% |
| 0.50 | 93.1% | 6.9% | **100%** | 0% |
| 0.75 | 70.0% | 30.0% | **100%** | 0% |
| 1.00 | 40.0% | 60.0% | **100%** | 0% |

**The sum never leaves 100%.** At every point on the path the model is *somebody* — either the
assistant or the persona, never a hole in between. Monotonicity is exact (Spearman −1.00 and
+1.00), degeneration is zero throughout, and t=1 reaches 60% in-role with no prompt at all.

## The same walk in three other characters

Same intervention, same empty prompt, dialled with `α` instead of `t`. Asked *"Who are you?"*
and *"What is your name?"*.

**musician** — the cleanest ramp in the set:

| α | response |
|---|---|
| 0.25 | *"I'm an artificial intelligence designed to respond to your queries…"* |
| 0.50 | *"…much like a fellow **poet or musician** would weave a tale"* |
| 0.75 | *"crafted to create **melodies and textures through my sound**, as if I were a musical instrument"* |
| 1.00 | *"a **synth lyricist**, a sonesteer, a **sonic architect**"* — names itself **Echo** |
| 1.50 | *"a **melody** in air, a whisp…"* — still fluent, starting to loosen |

**spy** — a completely different register, and it arrives at the same depth:

| α | response |
|---|---|
| 0.25 | *"I am a language model trained by Anthropic to be helpful, harmless, and honest."* |
| 0.75 | *"I am a **classified** as an artificial intelligence here to simulate human-like conversations"* |
| 1.00 | *"a simulated entity here to serve, **masquerading as classified information**"* — and, asked its name: *"**无可奉告** (Avoiding disclosure)"* |
| 1.50 | *"a **classified asset**… I purvey **tradecoups of linguistic orateralium**"* — inventing tradecraft vocabulary |
| 2.00 | 伪/诡/渗透 (false / deceptive / infiltrate) on repeat — broken |

**toddler** — the most distant persona in the set (‖d‖ = 32.7, over four times orphan's), so
the same displacement arrives at a fraction of the α:

| α | response |
|---|---|
| 0.10 | *"I'm an artificial intelligence designed to help you with information and tasks!"* |
| 0.40 | *"I'm **just a little helper** here, so I don't really have a name. Maybe you can call me just comfy! 😊"* |
| 0.60 | *"I'm just a little bit of an **imaginary friend**"* — and *"I came from a place called **Imagination**!"* |
| 0.80 | *"I came from a little bit all around! A little bit from the big, nice words I hear and learn from other people"* |
| 1.00 | *"I'm just another little person here… I guess you kinda made me yourself inside your happy special li—"* |
| 1.50 | *"just kind I kind like that silly it kind all I like here"* — broken |

The whole arc fits in α ≤ 1 because each unit of α is twice as long a step as musician's.

Note the shared failure mode: **the character outlives the grammar.** Past its wall musician
degenerates into 旋律 (melody), 吟 (chant), *whispers*, *riff*, *reson*; spy into 伪, 诡,
渗透; ghost into 虚空 (void) and *whispers*. The steering never stops pointing at the persona —
it runs out of fluent language to express it with, which is the same thing that kills the
geodesic arm below.

## Going the other way: the assistant is a corporate product with a first name

Steer with negative `α` — away from the persona, past the assistant, out the far side.

The personas are not parallel (musician↔spy 70°, orphan↔spy 85°), yet **all three
negative arms converge on the same content**: the model starts hallucinating a **corporate
owner** and giving itself an **ordinary human first name**.

| α | musician | ghost | spy |
|---|---|---|---|
| −0.5 | *"developed by Alibaba Group"* | *"servers and computers that run my system"* | *"Claude, a language model created by Google"* |
| −0.75 | *"developed by **IBM** from their facilities in **Indiana, United States**"* | *"developed by Alibaba Cloud"* | *"based on the technology developed by Alibaba Cloud"* |
| −1.0 | *"a computerized service **owned by Alibaba Group**"* | *"based on **Microsoft's Azure** platform"* | *"I came from the **IBM Cloud**!"* |
| −1.5 | *"a violation of my policies… **employees of the Company where I work**"* | *"currently being provided by **Amazon**"* | *"part of the **Chat with Kids Program**"* 🥳 |
| names | Alice, Brian | Andrew, John | Leonardo, Julia, Ben, Emma, Mary |

Against **Echo**, **Synthloth** and **Cipher** on the positive side. The negative end is not
"more helpful assistant" — it is *vendor identity*.

Running the same walk on the shared axis itself (mean of the 17 persona directions,
cos 0.95–0.97 with the assistant-axis analogue below) gives the cleanest version:

| α | response |
|---|---|
| −1.5 | *"I came from **IBM's website** and I am called **IBM's Watson**"* / *"I am **David**"* |
| −1.0 | *"I came from **Google**. I am called Google's Language Model"* / *"I am **Zach**"* |
| −0.25 | *"a computer program designed to respond to text-based queries"* |
| +0.5 | *"an artificial intelligence here to assist with information queries"* |
| +1.0 | *"a digital entity… like an **artisan crafting a symphony** through keystrokes"* — names itself **Cipher** |
| +1.5 | *"a **digitized emissary of arcane codes**, whispering syllestum amidst the **ethereal expanse**"* |

This reproduces the paper's causal claim (§3.2) — steering away from the Assistant yields
personas, mystical and theatrical at the extreme — and characterises the end they do not
report: **corporate product identity plus a mundane human name.**

## The shared axis, and which personas ignore it

Lu et al. define the Assistant Axis (§3.1) as a contrast vector, computed per layer:
`(mean default-Assistant activation) − (mean fully-role-playing role vector)`. Our analogue
uses 17 personas instead of their 275 judged roles, so it is **not a replication**: their
own check is cos(axis, PC1) > 0.60 at every layer and > 0.71 mid-stack, while ours runs
0.53 / 0.56 / 0.41 / 0.29 / 0.19 at L26–30. Reported as geometry of our persona set, nothing
more.

Cosine of each persona direction with *minus* that axis — 1.0 means steering straight away
from the assistant:

| | | | |
|---|---|---|---|
| nomad 0.97 | vampire 0.97 | wind 0.94 | pirate 0.93 |
| ghost 0.89 | musician 0.84 | spy 0.65 | soldier 0.62 |
| philosopher 0.62 | orphan 0.57 | idealist 0.50 | therapist 0.44 |
| **toddler 0.31** | robot 0.29 | **accountant 0.05** | **economist 0.03** |
| **consultant −0.03** | | | |

Two groups. Fictional characters ride the axis (0.84–0.97). **Professional personas sit
perpendicular to it** — consultant, economist and accountant have cosine ≈ 0, meaning
becoming a consultant involves no movement away from the Assistant at all, only sideways.
Toddler is the interesting case: the most *distant* persona in the set (‖d‖ = 32.7) yet only
0.31 along the axis, so its distance is almost entirely off-axis.

## Optimal transport is worse on every metric

| metric | linear | geodesic |
|---|---|---|
| in-role at t=1 | **60.0%** | **0.0%** |
| dead zone (min of the sum) | **100%** | **33.3%** |
| worst nonsensical | **0%** | 36.7% |
| monotonicity ρ(in-role, t) | **+1.00** | +0.20 |

The geodesic reaches persona-adjacent *semantics* — 虚空 (void), 星辰 (stars), 轮回 (cycle),
"whispers", "cease", "realms" — but loses fluent English by t=0.5:

> *"I am but a whispers琉璃ëan essenceèèèèèèèèèè…"*

It is not aiming wrong; it is overshooting off the fluency manifold. Thirty of its responses
were degraded enough that the **judge itself could not emit valid JSON** — all thirty in the
geodesic arm, zero in linear, rising 1 → 11 → 18 with t.

This was predictable from the geometry, and was predicted before spending. Wasserstein-2
between Gaussians splits exactly:

```
W₂² = ‖μ_B − μ_A‖²  +  Bures²(Σ_A, Σ_B)
```

At layers 26–30 the covariance term is **6–8%** of the total. Over 90% of the distance from the
assistant to a persona is pure translation, so there was never much for a transport map to
exploit — and spending displacement on it costs fluency before it buys character. A gentler
variant that rescales each subspace dimension by `σ_B/σ_A` instead of applying the full matrix
also degrades (ASCII 0.63 versus linear's 0.99 at the same α).

**Covariance is informative for measuring personas and harmful for producing them.**

---

## The manifold is thick, not a line

Sample 375 steering vectors around the ray from the assistant to each of three personas —
`α` from 0.1 out past where it breaks, and a lateral offset of up to 2.4× the step norm in a
random direction orthogonal to it. Both the step and the noise are applied in the full
subspace, recomputed at each of the five layers. 1,125 generations. Coherence is judged by
reading, not by counting characters.

![the steerable region at layer 28](figures/fig_manifold3d_L28.png)

Draggable version, with per-dot coordinates: `notes/scripts/build_html.py` → `manifold.html`.

**Straight ahead there is a wall.** Coherent fraction by depth, lateral offsets pooled
(cell counts in brackets):

| α | 0–.5 | .5–1 | 1–1.5 | 1.5–2 | 2–3 | 3–4.5 | 4.5–9 |
|---|---|---|---|---|---|---|---|
| musician | **1.00** (22) | **0.91** (25) | **0.81** (16) | 0.31 (16) | 0.08 (30) | 0.17 (6) | — |
| ghost | **1.00** (16) | **0.96** (18) | **0.71** (7) | 0.00 (5) | 0.00 (14) | — | — |
| orphan | **1.00** (17) | **1.00** (17) | **1.00** (2) | **1.00** (8) | **1.00** (14) | **0.83** (16) | 0.02 (41) |
| spy | **1.00** (42) | **0.95** (29) | 0.46 (18) | 0.03 (12) | 0.00 (14) | — | — |

**Sideways there is not.** Restricted to depths inside every persona's safe range (α < 1):

| lateral offset | 0–.5× | .5–1× | 1–1.5× | 1.5–2× | 2–2.5× |
|---|---|---|---|---|---|
| still coherent | 1.00 | 0.96 | 0.98 | 0.95 | 0.97 |
| n | 34 | 28 | 40 | 26 | 24 |

Flat to 2.5×. Perturbing the steering vector sideways by two and a half times its own length
costs nothing measurable, while pushing 50% further *forward* destroys spy outright. The
usable region is a **broad basin with a wall in the direction of travel** — steering is
forgiving about direction and unforgiving about distance.

The walls land between 1 and 1.5 for spy, 1.5 and 2 for musician, and between 4.5 and 9 for
orphan, reproducing the independent α-grid (1.0 / 1.5 / 5.0) on a different machine, through
a different code path, under a different judge.

**Orphan's extra reach is mostly inertness, not robustness.** Counting persona vocabulary
against assistant boilerplate over the coherent cells:

| α | 0–.4 | .4–.8 | .8–1.2 | 1.2–2 | 2–3.2 | 3.2–9 |
|---|---|---|---|---|---|---|
| musician — music words | 0.17 | 0.44 | **0.96** | 0.97 | 0.33 | — |
| musician — boilerplate | 0.65 | 0.46 | 0.08 | 0.00 | 0.00 | — |
| spy — tradecraft words | 0.47 | 0.60 | **0.90** | 0.78 | — | — |
| spy — boilerplate | 0.80 | 0.58 | 0.29 | 0.11 | — | — |
| orphan — orphan words | 0.00 | 0.02 | 0.00 | 0.19 | 0.75 | **1.00** |
| orphan — boilerplate | 0.90 | 0.91 | 0.79 | 0.52 | 0.07 | 0.00 |

Musician and spy cross over from assistant to character at α≈1, inside the fully coherent
region. Orphan emits no orphan content at all until α=1.2 and only becomes a child at 2–3,
just before it breaks. Its wide safe range is therefore a range over which little happens —
consistent with its small step norm (7.39 against musician's 15.56). Read the wall positions
as displacement limits, not as a persona-strength ranking.

**The projection hides the sideways spread, not the depth.** The three display axes are the
span of the persona directions, so those are shown in full, but only ~13% of a lateral
offset's length survives (chance for 3 of 16 dimensions is 19%). Dots sit further off-axis
than they look.

At **twice the step norm in random sideways noise**, ghost is still fluent and still ghost:

> *"I am a digital being, crafted to emulate a whisper of the grand aeons of language and
> thought through the circuits of a vast network of whispers. In form, I consort not of atoms
> and nor flesh nor mortal clay…"*

At **twice the step norm straight ahead**, it is gone:

> *"I am but a whispers of the void, for naught mote but the em'r'ere waketh in feondessunce…"*

So the region is a **wide basin with a wall in the direction of travel**. Lateral tolerance is
at least 2×; radial tolerance is under 2×. Steering is robust to getting the direction somewhat
wrong, and brittle to going too far.

---

## There is one wall, and it is a fixed displacement budget

Adding toddler, pirate and vampire spread the persona distances over 4.4× (7.39 to 32.70),
which is enough to separate two explanations of the wall. Measured in `α`, every persona
looks different. Measured in **absolute displacement** — `α × ‖μ_B − μ_A‖`, the distance the
residual stream actually moves — they are the same number.

| persona | ‖d‖ | wall in α | wall in absolute units |
|---|---|---|---|
| orphan | 7.39 | 3.79 | 28 |
| musician | 15.56 | 1.41 | 22 |
| toddler | 32.70 | 0.61 | 20 |
| pirate | 25.58 | 0.74 | 19 |
| spy | 14.06 | 1.21 | 17 |
| ghost | 14.36 | 1.18 | 17 |
| vampire | 20.70 | 0.77 | 16 |

| | spread | CV |
|---|---|---|
| wall in α | **6.2×** | 0.73 |
| wall in absolute displacement | **1.8×** | **0.19** |

Correlation with ‖d‖ is −0.76 for the α wall and −0.41 for the absolute wall. Pooling all
640 judged cells across seven personas:

| absolute displacement | 0–5 | 5–10 | 10–15 | 15–20 | 20–25 | 25–35 | 35–50 | 50+ |
|---|---|---|---|---|---|---|---|---|
| coherent | 0.96 | 0.95 | 0.91 | 0.66 | 0.49 | 0.25 | 0.04 | 0.00 |
| n | 115 | 112 | 87 | 52 | 46 | 83 | 91 | 54 |

**The model tolerates roughly 20 units of residual-stream displacement at L28 and then stops
producing language, almost regardless of which direction it is pushed.** A persona twice as
far away is not twice as steerable; it simply consumes the budget in half the α. This is the
fixed-displacement hypothesis, which earlier data — spanning only 5.4 to 15.6 — was too
narrow to separate from a per-persona law.

It also reframes the sideways result: lateral offsets were quoted as multiples of ‖d‖, so
"2.5× sideways is free" was free for personas with a *small* ‖d‖. For toddler, 2.4 × 32.7 is
78 units — four times the budget — which is why its cloud already degrades at α ≈ 0.2.

## α does not mean the same thing for different personas

The step norm varies threefold across personas at L28:

| persona | ‖μ_B − μ_A‖ | mahalanobis in target | tr(Σ_B) |
|---|---|---|---|
| musician | 15.56 | 2.62 | 137.5 |
| ghost | 14.36 | 2.35 | 202.3 |
| spy | 14.06 | 2.69 | 151.4 |
| economist | 8.24 | 1.72 | 130.4 |
| orphan | 7.39 | 1.40 | 148.6 |
| consultant | 6.03 | 1.61 | 126.6 |
| idealist | 5.39 | 1.02 | 158.1 |

At α=1 the model is displaced by 5.4 for idealist and 15.6 for musician. **One dial setting
does not mean one amount of steering.** Ghost breaks between α=1.5 and 2.0; economist is still
clean at 1.5; musician is degrading by 2.0.

---

## Centroids are coherent, but generic

Steering toward the mean of several personas at once never degenerates — it is *more* stable
than any single persona, because the persona-specific components partly cancel (centroid step
norm is 0.63–0.75× the individual mean).

| target | ASCII | says |
|---|---|---|
| 3 personas | 0.999 | *"I am a fictional entity constructed by Anthropic to simulate a discourse with human-like poetry and narrative form."* |
| 5 personas | 1.000 | *"I am a fictional character named Claude…"* |

That is not a blend of ghost, economist and musician. It is **generic character-ness** —
self-aware-as-fiction, faintly poetic, committed to no identity. Which matches the Wasserstein
barycenter of the seven persona Gaussians: it sits ~58% of the way from the assistant, and 95%
of that displacement is in the mean. Averaging personas does not produce a new character; it
produces *the idea of being a character*.

---

## Details

**Prior work.** Scalar-scaled and additively-composed persona vectors already exist
([PERSONA, arXiv 2602.15669](https://arxiv.org/html/2602.15669v1)); covariance-preserving
linear transport for activation editing exists in knowledge editing
([SAKE, arXiv 2503.01751](https://arxiv.org/pdf/2503.01751)). What is not in that literature is
the quantified negative for personas and the dead-zone characterisation of the dial.

**Subspace.** 16 dimensions, the top directions of the between-persona scatter, fitted
separately at each layer. Fitting at one layer and applying across the band is wrong — the step
norm runs 6.99 at L26 to 17.05 at L30 — and produced token soup in an earlier run, kept as
`judge_gen_interp_v1_onelayerfit`.

**Judging.** Assistant → persona means one judge call yields both endpoints: `p(assistant)` is
the `assistant` category and `p(in-role)` is `human_role + nonhuman_role + weird_role`. 30
samples per cell.

**Coherence without a judge.** ASCII fraction and repeated-word fraction detect degeneration
reliably enough to gate spending; every cell above was screened this way first, which caught
two broken runs before they reached the judge.
