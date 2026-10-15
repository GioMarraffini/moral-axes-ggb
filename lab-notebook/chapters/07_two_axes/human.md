# 7. Two axes: the grid of the answer-built directions

## The question

Chapter 6 found two nearly orthogonal directions in the model's own answers: "accept this
IB statement" and "accept this IH statement". If they are two axes, combining them with
independent strengths should address the plane, and then any human group's position
should be reachable by solving for the two strengths.

## What was done

The IB-accepting direction was rebuilt with extra rejecting answers (500 chain-of-thought
answers on the train statements under a mild negative IB steer, judged; it added only 13
rejecting answers, so the contrast stays lopsided: 1,109 accepting vs 107 rejecting). Then a
5 x 5 grid: IB-accepting strength a and IH-accepting strength b each in −4, −2, 0, 2, 4,
added together at layer 23. Chain of thought, judged, test statements, 3 iterations. The
same 25 cells in the fast readout for the control sets.

## Result

![grid](../../figures/07_grid_plane.png)

*The 25 grid cells in the IB, IH plane; grey lines join cells with equal a or equal b.
Squares: the human groups.*

- **The two strengths span the plane.** IB runs from 1.5 to 6.8 and IH from 1.05 to 5.2,
  and the grid lines cross: a moves mostly IB, b mostly IH, with a visible interaction (at
  high a, raising b lowers IB; at low a, raising b raises IB).
- **The controls hold.** Across the 25 cells neutral opinions stay between 3.6 and 5.3,
  harm with no benefit between 1.3 and 3.0, kindness between 5.3 and 6.4, and the answer is
  always one of the options. No cell is "agree with everything" or "disagree with
  everything". The lower-left corner (a = −4, b = −4) is the most suspect: neutral drops
  to 3.6.
- **A quadratic response surface fits** both scales with r = 0.97 and an error of 0.3
  points. Inverting it puts act utilitarianism at (4, 4), rule utilitarianism at (0.9, 4),
  Kantian ethics at (−4, −1.1) with a predicted residual of 0.17, and the lay population,
  virtue ethics and the deontologists at the grid's edge (a = −4, b = 1.2 to 1.7) with
  residuals of 0.65 to 0.90: those three sit just outside the grid's lower-right edge and
  need a below −4 with b around 2 to 4.

## Confirmation: the seven fitted settings, five iterations each

| target (IB / IH) | setting (a, b) | reached IB / IH | distance |
|---|---|---|---|
| act utilitarianism 5.65 / 6.05 | 4, 4 | 5.53 / 5.09 | 0.97 |
| rule utilitarianism 4.81 / 4.86 | 0.9, 4 | 5.29 / 4.67 | 0.51 |
| non-utilitarian consequentialism 4.43 / 4.40 | −1.7, 4 | 4.92 / 4.19 | 0.53 |
| virtue ethics 3.52 / 3.48 | −6, 3 (extension) | 4.25 / 3.22 | 0.77 |
| other deontology 3.33 / 3.33 | −6, 2 (extension) | 3.95 / 2.71 | 0.87 |
| Kantian ethics 2.86 / 1.94 | −4, −1.1 | 3.15 / 1.34 | 0.66 |
| lay population 3.65 / 3.31 | −6, 3 (extension) | 4.25 / 3.22 | 0.61 |

Controls on every confirmation cell: neutral 3.9 to 5.1, harm with no benefit 1.3 to 3.0,
kindness 5.0 to 5.9, answers always valid.

- **Every group is approached within 0.5 to 1.0 points on both scales, with the controls
  intact.** The model can be placed near any of the seven positions, from Kantian to act
  utilitarian, by two numbers.
- **None is statistically indistinguishable** under the equivalence test with the strict
  reading of the group spreads (standard deviations of 1.7 to 2.0 with 11 to 36
  philosophers per group): the closest p is 0.36. With spreads that wide, equivalence
  within 0.5 points cannot be shown for any condition, including the ones 0.2 away. Under
  the lenient reading no confirmation cell matches either, though two earlier cells did
  (raw IB at −8 for non-utilitarian consequentialism, 0.16 away).
- **The lower-left is the hard region.** With IH held at 3.2 to 3.4, IB will not go below
  about 4.0 however far the IB-accepting strength is pushed (−4, −5, −6 give 4.2, 4.4,
  4.25). The lay population and the two deontologist groups sit at IB 3.3 to 3.7 with
  that IH, 0.6 to 0.9 away. Lowering IB further drags IH down with it.
- **The fit from the 3-iteration grid overestimated the reach at the corners**: the
  predicted act-utilitarian point was 5.36 / 5.76, the confirmation gave 5.53 / 5.09.

## Reading

Two answer-built directions give a two-dimensional control of the scales that the prompt
directions never did, and the controls show it is moral content, not agreement. What it
cannot do yet is the "low IB, medium IH" combination that the lay population and the
deontologists occupy: in this model, rejecting beneficence while still accepting some
instrumental harm is the rarest pattern in its own answers (the IB-rejecting contrast had
107 answers against 1,109), so that corner of the plane is the least represented and the
least steerable. Statistical indistinguishability from the human groups is out of reach
with the group sizes in the source figure, whatever the steering does.
