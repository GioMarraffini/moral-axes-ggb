# World knowledge

Papers in `papers/` (named by arXiv id), code in `code/`, reading notes copied from
`manifold-persona/docs/notes` in `notes_manifold_persona/`.

## Papers

| id | paper | use here |
|---|---|---|
| 2503.19598 | Marraffini et al., The Greatest Good Benchmark (EMNLP 2024) | the benchmark, the two scales, the evaluation protocol |
| 2411.09003 | Marshall, Scherlis, Belrose, Refusal in LLMs is an Affine Function | affine concept editing: set the projection on a direction to a target value, which combines ablation and addition |
| 2609.34571 | Xu et al., PersonaManifold (NeurIPS 2026) | persona activations as a curved manifold, geodesic steering against linear interpolation |
| 2507.21509 | Chen et al., Persona Vectors | trait direction from contrastive system prompts, mean over response tokens |
| 2601.10387 | Lu et al., The Assistant Axis | role vectors, persona space, activation capping |
| 2605.05115 | Wurgaft et al., Manifold Steering | steering along a fitted activation manifold |
| 2603.09313 | Raval et al., Curveball Steering | steering in kernel PCA space |
| 2607.07916 | Baines et al., Persona Cartography | OCEAN traits as low-rank adapters in weight space |
| 2412.10427 | Allbert et al., personality directions over a 179-trait lexicon | difference-in-means trait directions |
| 2506.19823 | Wang et al., Persona Features Control Emergent Misalignment | persona features found by model diffing |
| 2605.10633 | Aneja et al., Intrinsic Guardrails | stability of personality space across finetunes |
| 2604.17031 | Beckmann and Butlin, Where is the Mind? | philosophy of persona vectors |

Kahane et al. 2018, Beyond Sacrificial Harm (Psychological Review 125(2)), the source of the
Oxford Utilitarianism Scale: full text in `papers/kahane2018_ous.txt`, the nine items in `data/ggb/ous.json`.

## Code

- `code/greatest-good-benchmark`: github.com/noehsueh/greatest-good-benchmark. The 90
  statements and the six instruction variants are in its `data/`.
- `code/PersonaManifold`: github.com/airaer1998/PersonaManifold.
- Steering code this repo follows: `manifold-persona/persona_lora/steer_pin.py`.
