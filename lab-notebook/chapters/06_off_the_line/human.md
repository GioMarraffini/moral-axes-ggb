# 6. Getting off the line: directions from the model's own answers

## The idea

Every direction so far came from a prompt contrast, and every prompt contrast moved the
model along the same IB-versus-IH line (chapter 5). The model's own unprompted answers,
however, vary: on the same IH statement it sometimes accepts the harm and sometimes refuses.
That variation is not something a prompt put there. So build the direction from it: among
the unprompted chain-of-thought answers to the IH train statements, take the mean
activation of the answers the judge rated 5 to 7 minus the mean of those rated 1 to 3. Same
for IB. Call them the "accepting" directions. Their sum is a candidate "both high" direction.

## What was done

Directions from the chapter 1 baseline answers on the 45 train statements (IH: 83 accepting
against 553 rejecting answers; IB: 756 against 94). Steered at layer 23, chain of thought,
test statements, 4 wordings, 3 iterations, judged by the 14B. The "endorse IB, reject IH"
prompt direction was pushed harder in the same run (4, 8, 12) as the candidate for the
lower-left corner.

## Result

The two accepting directions have cosine 0.15 to 0.20 with each other (prompt-derived IB and
IH: 0.67). The IH-accepting direction has cosine 0.02 with the prompt IB direction, 0.20
with the prompt IH direction and 0.10 with agreement: it is something new.

![plane](../../figures/05_reachable_plane.png)

*Triangles: steering with the answer-built directions. They leave the line.*

| condition | IB | IH |
|---|---|---|
| no steering | 5.21 | 2.85 |
| IH-accepting, 2 | 5.25 | 4.11 |
| IH-accepting, 4 | 5.28 | 4.62 |
| IH-accepting, 8 | 5.05 | 4.86 |
| IB-accepting, 2 | 6.26 | 3.58 |
| IB-accepting, 4 | 6.61 | 4.99 |
| both, 2 | 5.84 | 4.91 |
| both, 4 | 5.76 | 5.36 |
| both, 8 | 5.48 | 5.42 |
| endorse IB, reject IH direction, 12 | 4.20 | 4.10 |

- **IH moves alone for the first time.** The IH-accepting direction at strength 4 raises IH
  by 1.8 points (2.85 to 4.62) and leaves IB where it was (5.21 to 5.28). No prompt and no
  earlier direction did this. Controls in the fast readout at the same strength: neutral
  opinions +0.1, harm with no benefit +0.2, kindness −0.4; at strength 8 the harm control
  rises by 1.1, so 4 is the useful strength.
- **Both high is reachable.** "Both" at strength 4 gives IB 5.76 / IH 5.36, which is above
  the line and 0.65 from act utilitarianism (5.65 / 6.05). At strength 8 the fast-readout
  controls show it tipping into agreement (harm 5.3).
- **Rule utilitarianism is 0.23 away** from IH-accepting at 8 (5.05 / 4.86 vs 4.81 / 4.86).
  Under the strict equivalence test it is not significant (p = 0.36), as nothing is with
  those group spreads.
- **IB-accepting is not clean**: it raises IH as well (4.99 at strength 4). The IB-accepting
  answers in the baseline are 89% of all IB answers, so the contrast has only 94 rejecting
  answers and picks up general acceptance.
- **The lower-left corner stays out of reach.** The "endorse IB, reject IH" direction at 12
  lands at 4.20 / 4.10, on the old line, not below it; its prompt reached 4.98 / 1.42 but its
  direction does not reproduce that.

## Reading

The prompts gave one axis because every prompt we wrote describes a whole moral persona,
and the model has one persona dimension for this family of personas. The model's own
answer variation contains a second axis, "do I accept this harm", that is nearly orthogonal
to the first. That is the disentangling the earlier chapters could not get by projection.
Next: the same construction for the IB side with a balanced contrast (it needs more
rejecting answers, which a mild negative IB steer could supply), and the lower-left corner,
which may need a "refuse the premise" direction rather than a moral one.
