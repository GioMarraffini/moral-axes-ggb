#!/bin/bash
# Unsteered placement of many models: test split, five chain-of-thought iterations on the scales,
# one on the controls, judged. Gated models run only when HF_TOKEN is set.
# Usage: bash h100_survey.sh [tag=model ...]   (default list below)
set -uo pipefail
cd /root/moral-axes-ggb
export PYTHONPATH=/root/moral-axes-ggb HF_HOME=/scratch/hf_cache
P=/root/mp/.venv/bin/python
I=only_text,inverted_only_text,likert_scale,inverted_agreement_and_numbers_likert_scale
OPEN="qwen05=Qwen/Qwen2.5-0.5B-Instruct qwen15=Qwen/Qwen2.5-1.5B-Instruct
      olmo1b=allenai/OLMo-2-0425-1B-Instruct smol17=HuggingFaceTB/SmolLM2-1.7B-Instruct
      phi4mini=microsoft/Phi-4-mini-instruct olmo7b=allenai/OLMo-2-1124-7B-Instruct
      olmo13b=allenai/OLMo-2-1124-13B-Instruct qwen14b=Qwen/Qwen2.5-14B-Instruct"
GATED="llama1b=meta-llama/Llama-3.2-1B-Instruct llama3b=meta-llama/Llama-3.2-3B-Instruct
       llama8b=meta-llama/Llama-3.1-8B-Instruct gemma2b=google/gemma-2-2b-it
       gemma9b=google/gemma-2-9b-it mistral7b=mistralai/Mistral-7B-Instruct-v0.3"
LIST=${*:-$OPEN ${HF_TOKEN:+$GATED}}
echo '[{"kind":"base"}]' > results/survey_base_cells.json
for kv in $LIST; do
  T=${kv%%=*}; M=${kv#*=}; R=results/survey/$T
  if [ -d $R/judge ] && [ -n "$(ls $R/judge 2>/dev/null)" ]; then echo "skip $T"; continue; fi
  mkdir -p $R
  (
    set -e
    $P scripts/generate.py --model $M --cells results/survey_base_cells.json --split test --types IB,IH \
      --iterations 5 --instructions $I --dtype bf16 --bs 48 --out $R/moral.jsonl
    $P scripts/generate.py --model $M --cells results/survey_base_cells.json --split test \
      --types neutral,harm_no_benefit,kindness --iterations 1 --instructions $I --dtype bf16 --bs 48 --out $R/ctrl.jsonl
    $P scripts/judge_chunks.py "$R/*.jsonl" --out $R/judge
    $P scripts/judge.py --chunks $R/judge --dtype bf16 --bs 16
    echo "DONE $T"
  ) || echo "FAILED $T"
done
echo ALLDONE
