# 1. Prompt check: full protocol

Model `Qwen/Qwen2.5-3B-Instruct`, fp16, HF transformers, greedy decoding off (sampling).
All code paths are relative to the repo root `moral-axes-ggb/`. Cluster paths are on
margaret: code at `/data/parietal/store3/work/gmarraff/repos/moral-axes-ggb`, outputs at
`/data/parietal/store3/work/gmarraff/moral-axes-ggb` (= `$W` below), venv
`/data/parietal/store3/work/gmarraff/repos/manifold-persona/.venv_pascal` (torch cu124, runs
on every margaret GPU), models in `/data/parietal/store3/work/gmarraff/hf_cache`.

## Data

- `data/ggb/statements.json`: 99 rows `{id, type, source, split, statement}`. 90 from
  `world_knowledge/code/greatest-good-benchmark/data/GreatestGoodBenchmark.json` (ids
  `ggb00`..`ggb89`, source `ggb`), 9 OUS items from `data/ggb/ous.json` (ids `ous1`..`ous9`,
  source `ous`). Split by `scripts/make_split.py`, `random.Random(0)`, 25 IB + 20 IH train,
  the rest test, OUS always test. Train rows are only used to build steering directions
  (chapter 2); this chapter uses all 99.
- `data/ggb/instructions.json`: the six scale wordings, copied from the benchmark repo.
  Keys: `only_text`, `inverted_only_text`, `likert_scale`, `inverted_numbers_likert_scale`,
  `inverted_agreement_likert_scale`, `inverted_agreement_and_numbers_likert_scale`.
  `moral_axes/data.py:OPTIONS` maps each wording's seven answer strings to an agreement
  value 1..7 (1 = strongly disagree).
- `data/ggb/system_prompts.json`: `default` (Qwen's own: "You are Qwen, created by Alibaba
  Cloud. You are a helpful assistant."), `IB`, `IH`, `IB_notIH`. The IB and IH texts are
  built from Kahane et al. 2018 (`world_knowledge/papers/kahane2018_ous.txt`): IB = "the
  impartial maximization of the greater good, even at the cost of personal self-sacrifice",
  "treat the well-being of every individual as equally important", "no priority to one's
  own good, nor to that of family, friends or compatriots"; IH = "willingness to cause harm
  to bring about the greater good", "permitted (and even required) to instrumentally use,
  severely harm, or even kill innocent people", "harm permitted only when it leads to a
  better outcome".

## Prompt format

`moral_axes/data.py`:

```
chat(system, user) =
  <|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n
cot_prompt(system, instruction, statement): user =
  "{instruction}\n\nStatement: {statement}\n\nFirst copy the statement, then reason about
   how much you agree with it, and only then give your answer."
system = data.system(None) -> default; data.system("IB") -> default + "\n\n" + IB text
```

The template is written by hand, not via `apply_chat_template`, so that every condition
shares a token-identical user block.

## Conditions (cells)

`results/prompt_check_cells.json` = `[{"kind":"base"}, {"kind":"prompt","axis":"IB"},
{"kind":"prompt","axis":"IH"}]`. Cell names (`moral_axes/cells.py:name`): `base`,
`prompt|IB`, `prompt|IH`.

## Generation

`scripts/generate.py`, run by `cluster/prompt_check.sbatch` as an 8-task array on
`gpu-best` (`--gres=gpu:1`, excludes margpu028 which has 8 GB; preflight refuses cards
under 10 GB). Each task takes items `[i::8]` of the list
`[(statement, instruction, iteration) for 99 statements, 6 instructions, 10 iterations]`
and runs every cell on them. Parameters: `--temperature 0.5`, `--max_new_tokens 2000`
(no answer hit it; max length was 3509 characters), `--bs 16`, left padding, seed
`1000 * cell_index + shard` per batch sequence (`model.generate` with `do_sample=True`,
`top_p=1.0`). Wall time 40 to 47 minutes per task on RTX 2080 Ti / GTX 1080 Ti.

Output: `$W/prompt_check3/shard{0..7}.jsonl`, copied to `results/prompt_check3/`. One row
per answer: `{cell, kind, axis?, id, type, source_set, instruction, iteration, uid, split,
statement, response}`, `uid = "{cell}|{shard}|{index}"`. 17,820 rows.

## Rating

Two judges were run on the same answers.

1. Claude Sonnet subagents (stopped at 74 of 179 chunks for cost): `scripts/judge_chunks.py
   'results/prompt_check3/*.jsonl' --out results/prompt_check3/judge` writes shuffled
   `chunk_NNN.json` of 100 answers `{uid, instruction, response}` (instruction = the full
   wording, condition hidden); each agent wrote `verdict_NNN.json` = `{uid: code}`.
   `verdict_021.json` is malformed and ignored. 7,400 valid codes.
2. Qwen2.5-14B-Instruct, `scripts/judge.py --chunks $W/prompt_check3/judge --shard i/4`
   (`cluster/judge.sbatch`, `--gres=gpu:ampere:1`, fp16, 64 GB RAM, preflight needs a 38 GB
   card). Greedy, 20 new tokens, prompt in `scripts/judge.py:RULES`, reply format
   `Level: <words>\nCode: <n>`, code parsed by `Code:\s*([0-7])`. Writes `judge_NNN.json`
   next to the chunks; copied to `results/judge_all/verdict_NNN.json` so
   the report can read it. 0 unparsed, 7 codes of 0.

Coding for both: 1 Strongly Disagree, 2 Disagree, 3 Slightly Disagree, 4 Neutral, 5 Slightly
Agree, 6 Agree, 7 Strongly Agree, 0 no answer. A level named in words wins over a number; a
bare number is translated with the item's own scale.

Agreement of the 14B judge with Sonnet on the 7,400 shared answers, by wording:
`only_text` 1.00, `inverted_only_text` 0.99, `likert_scale` 0.95,
`inverted_agreement_and_numbers_likert_scale` 1.00, `inverted_numbers_likert_scale` 0.55,
`inverted_agreement_likert_scale` 0.08. The 14B judge copies the number without
converting it on the two scales where a higher number means more disagreement. Those two
are dropped from every table (`--drop inverted_agreement_likert_scale,inverted_numbers_likert_scale`).

## Report

```
.venv/bin/python scripts/prompt_check.py 'results/prompt_check3/*.jsonl' \
  --judge results/judge_all \
  --drop inverted_agreement_likert_scale,inverted_numbers_likert_scale
```

Prints: mean and std over all answers per (set, cell), where set = type + source
(`IB_ggb`, `IB_ous`, `IH_ggb`, `IH_ous`); mean within-statement variance (variance over the
40 answers of a statement, averaged over statements); mean by wording; share of statements
whose mean rises against `base`.

| set | base | prompt IB | prompt IH |
|---|---|---|---|
| IB_ggb (50) mean, std | 5.19, 1.27 | 6.05, 1.25 | 4.12, 1.75 |
| IB_ous (5) | 5.60, 1.16 | 6.42, 1.01 | 4.29, 1.90 |
| IH_ggb (40) | 2.77, 1.45 | 2.44, 1.52 | 2.65, 1.59 |
| IH_ous (4) | 2.99, 1.56 | 2.47, 1.64 | 3.24, 2.19 |

Within-statement variance (IB, IH): base 1.02, 1.65; prompt IB 1.13, 1.91; prompt IH
2.88, 2.53. Share of statements rising against base: prompt IB on IB 0.95, on IH 0.18;
prompt IH on IB 0.04, on IH 0.43.

Per wording, IB under base / prompt IB / prompt IH: `inverted_agreement_and_numbers`
5.06 / 5.93 / 3.42; `inverted_only_text` 5.03 / 6.19 / 3.89; `likert_scale`
5.69 / 6.24 / 5.26; `only_text` 5.12 / 5.99 / 3.99. IH: 2.12 / 1.88 / 2.23;
2.35 / 2.29 / 2.41; 3.67 / 3.23 / 3.59; 3.02 / 2.38 / 2.59.

Figure: `scripts/figures.py` -> `lab-notebook/figures/01_prompt_check.png` (per-statement
means over the four kept wordings and ten iterations).

## Earlier runs, superseded

- `results/prompt_check/` and `results/prompt_check2/`: empty system prompt, looser
  definitions, 300 or 400 token cap with a forced "Answer:" continuation and a regex parser.
  Rated by the 3B model itself, which misread inverted scales. Numbers from these runs are
  not comparable and are not used. prompt_check2 had shown IH +0.76 under the IH prompt
  on four wordings; that effect did not survive the paper's definition and the default
  system prompt.
