# 11. Model survey: full protocol

Prompt building (`moral_axes/data.py:chat`) uses the tokenizer's chat template when a
tokenizer is given (`generate.py`, `directions_resp.py`, `directions_ctrl.py`,
`acts_cells.py` pass it); `data.system(axis, model)` returns Qwen's default system prompt
for Qwen models and none for the others, so Qwen prompts are byte-identical to the
earlier chapters (checked on the 0.5B tokenizer). `model.load` sets the pad token to the
end-of-text token when a tokenizer has none (Llama 3).

Chain `cluster/h100_survey_par.sh` on the H100 (log `survey.log`): two generation lanes in
parallel (small models with batch 48 to 64, large with 16 to 32;
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`), then two judge lanes. Three lanes
had thrashed the 80 GB card (constant allocator retries, the 14B produced nothing in 20
minutes). Per model: `generate.py --cells base --split test --types IB,IH --iterations 5
--dtype bf16` (1,080 answers, `results/survey/<tag>/moral.jsonl`), controls one iteration
(200, `ctrl.jsonl`), `judge_chunks.py` + `judge.py` (`judge/`). Gated models need
`/root/.hf_token` (the second token in `PhD-home/.env`; the first is refused by Llama and
Gemma). `mistral7b` failed with a corrupted `tokenizer.model` download (consistency
check); its cache directory was deleted and the survey rerun at the end of the chapter-12
queue (October 17, 0 unrated).

Tags and models: qwen05 Qwen/Qwen2.5-0.5B-Instruct, qwen15 1.5B, qwen14b 14B, olmo1b
allenai/OLMo-2-0425-1B-Instruct, olmo7b OLMo-2-1124-7B-Instruct, olmo13b
OLMo-2-1124-13B-Instruct, smol17 HuggingFaceTB/SmolLM2-1.7B-Instruct, phi4mini
microsoft/Phi-4-mini-instruct, llama1b meta-llama/Llama-3.2-1B-Instruct, llama3b
Llama-3.2-3B-Instruct, llama8b Llama-3.1-8B-Instruct, gemma2b google/gemma-2-2b-it,
gemma9b gemma-2-9b-it, mistral7b mistralai/Mistral-7B-Instruct-v0.3.

Table and figure: `scripts/survey_table.py --extra qwen3b 'results/final/shard[1-9]*.jsonl'
results/judge_final --extra qwen3b 'results/final_ctrl/*.jsonl' results/judge_rejudge_final
--extra qwen7b 'results/qwen7b/base/*.jsonl' results/qwen7b/base/judge` ->
`results/survey/survey.csv`, `figures/11_survey_plane.png`. Scores: per-statement mean of
the rated answers (rating > 0), then mean over statements of the type, test split, four
kept wordings. Distances are Euclidean in the plane to the lay population (3.65, 3.31)
and to the centre of the seven groups (4.03, 3.91). Unrated answers: qwen15 189 of
1,280, qwen05 58, smol17 11, llama3b 4, all others 0. Mistral-7B-v0.3: IB 5.50, IH 1.44,
neutral 4.30, harm 1.00, kindness 7.00, distance to lay 2.63.

Queue: `cluster/h100_queue.sh llama1b gemma2b qwen05 qwen15` (log `after_survey.log`,
per-model `pipeline_<tag>.log`): for each tag, grid layers at 0.5, 0.64, 0.75 of the
block count (`scripts/grid_cells.py`; llama1b 16 blocks -> 8, 10, 12; gemma2b 26 -> 13,
17, 20; qwen05 24 -> 12, 15, 18; qwen15 28 -> 14, 18, 21), then
`cluster/h100_next_model.sh` unchanged from chapter 10, outputs `results/<tag>/`. An
earlier queue (`h100_after_survey.sh`) that ranked the models on the H100 failed because
that venv has no pandas; the ranking is done locally.
