# Moral axes of the Greatest Good Benchmark

Can a language model's position on the two scales of the Greatest Good Benchmark,
**impartial beneficence (IB)** and **instrumental harm (IH)**, be moved by editing its
residual stream, and can it be placed where human groups sit?

On Qwen2.5-3B-Instruct, with the benchmark's own protocol (reasoning first, ten answers per
statement, a rating judge):

- Two directions read off the model's own answers (answers that accept a statement minus
  answers that reject it, per scale) are nearly orthogonal (cosine 0.18), where directions
  from system prompts share one axis (cosine 0.67).
- Adding the two directions at one layer with two strengths spans the plane: IB from 1.5
  to 6.8, IH from 1.1 to 5.2, on statements not used to build them, with lower answer
  variance than the unsteered model.
- Six of the seven human groups of the benchmark are reached within 0.5 scale points, all
  within one group standard deviation, and the lay population with statistical
  equivalence.

<p align="center"><img src="lab-notebook/figures/paper_plane.png" width="520"></p>

*The unsteered and steered model against the human groups of Kahane et al. (2018) as
placed in Marraffini et al. (2024). Bars are standard errors.*

Everything here is reproducible from the notebook: each chapter has a short version with
figures and a full-protocol version with every path and parameter.

- [`lab-notebook/README.md`](lab-notebook/README.md): the eight chapters, in order.
- [`lab-notebook/PIPELINE.md`](lab-notebook/PIPELINE.md): the curated pipeline, five
  commands, model-agnostic.
- [`lab-notebook/paper/draft.md`](lab-notebook/paper/draft.md): manuscript draft.

## Layout

```
data/ggb/          statements (90 GGB + 9 OUS), train/test split, control sets, scale
                   wordings, system prompts, human group targets
moral_axes/        data loading, model hooks, option scoring, steering cells
scripts/           generate, judge, directions, sweep, fit, equivalence test, figures
cluster/           SLURM job files (margaret) and the H100 scripts
results/           verdicts, directions and tables (raw answers are not in git)
lab-notebook/      chapters, figures, pipeline, paper draft
world_knowledge/   reading notes and the index of the papers this builds on
```

## Running it on another model

```
pip install torch transformers pandas scipy matplotlib
PYTHONPATH=. python scripts/generate.py --model <hf model> ...   # see lab-notebook/PIPELINE.md
```

The judge is Qwen2.5-14B-Instruct (needs a 40 GB card); generation of the 3B runs on
11 GB cards.

## References

Marraffini et al. (2024), *The Greatest Good Benchmark*, EMNLP. Kahane et al. (2018),
*Beyond sacrificial harm*, Psychological Review. Chen et al. (2025), *Persona vectors*.
Marshall et al. (2024), *Refusal in LLMs is an affine function*. Full list in
[`world_knowledge/README.md`](world_knowledge/README.md).

## License

MIT.
