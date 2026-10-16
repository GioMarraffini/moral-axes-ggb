#!/bin/bash
# Unsteered placement of many models on one H100: two generation lanes in parallel (small
# models, large models), then two judge lanes. Test split, five chain-of-thought iterations
# on the scales, one on the controls. Gated models need /root/.hf_token. A model is skipped
# when its gen.done or judge folder exists, so the script can be rerun after a failure.
set -uo pipefail
cd /root/moral-axes-ggb
export PYTHONPATH=/root/moral-axes-ggb HF_HOME=/scratch/hf_cache PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
[ -f /root/.hf_token ] && export HF_TOKEN=$(cat /root/.hf_token)
P=/root/mp/.venv/bin/python
I=only_text,inverted_only_text,likert_scale,inverted_agreement_and_numbers_likert_scale
echo '[{"kind":"base"}]' > results/survey_base_cells.json
# lane: tag=model=batch
SMALL="qwen05=Qwen/Qwen2.5-0.5B-Instruct=64 qwen15=Qwen/Qwen2.5-1.5B-Instruct=64 olmo1b=allenai/OLMo-2-0425-1B-Instruct=64
   smol17=HuggingFaceTB/SmolLM2-1.7B-Instruct=64 llama1b=meta-llama/Llama-3.2-1B-Instruct=64 gemma2b=google/gemma-2-2b-it=48
   phi4mini=microsoft/Phi-4-mini-instruct=48 llama3b=meta-llama/Llama-3.2-3B-Instruct=48"
LARGE="qwen14b=Qwen/Qwen2.5-14B-Instruct=24 olmo7b=allenai/OLMo-2-1124-7B-Instruct=24 llama8b=meta-llama/Llama-3.1-8B-Instruct=32
   mistral7b=mistralai/Mistral-7B-Instruct-v0.3=24 gemma9b=google/gemma-2-9b-it=24 olmo13b=allenai/OLMo-2-1124-13B-Instruct=16"

gen_lane() {
  for kv in $1; do
    T=$(echo $kv | cut -d= -f1); M=$(echo $kv | cut -d= -f2); BS=$(echo $kv | cut -d= -f3); R=results/survey/$T
    if [ -f $R/gen.done ] || [ -d $R/judge ]; then echo "skip $T"; continue; fi
    if [[ $M == meta-llama/* || $M == google/* || $M == mistralai/* ]] && [ -z "${HF_TOKEN:-}" ]; then echo "no token $T"; continue; fi
    mkdir -p $R
    { $P scripts/generate.py --model $M --cells results/survey_base_cells.json --split test --types IB,IH \
        --iterations 5 --instructions $I --dtype bf16 --bs $BS --out $R/moral.jsonl \
      && $P scripts/generate.py --model $M --cells results/survey_base_cells.json --split test \
        --types neutral,harm_no_benefit,kindness --iterations 1 --instructions $I --dtype bf16 --bs $BS --out $R/ctrl.jsonl \
      && touch $R/gen.done && echo "GEN $T"; } > $R/gen.log 2>&1
    [ -f $R/gen.done ] || echo "FAILED $T"
  done
}
gen_lane "$SMALL" & gen_lane "$LARGE" & wait

judge_lane() {
  for T in $1; do
    R=results/survey/$T
    [ -f $R/gen.done ] || continue
    [ -d $R/judge ] && [ -n "$(ls $R/judge 2>/dev/null)" ] && continue
    { $P scripts/judge_chunks.py "$R/*.jsonl" --out $R/judge \
      && $P scripts/judge.py --chunks $R/judge --dtype bf16 --bs 16 && echo "DONE $T"; } > $R/judge.log 2>&1
    grep -q "DONE $T" $R/judge.log || echo "FAILED judge $T"
  done
}
ALL=$(for kv in $SMALL $LARGE; do echo $kv | cut -d= -f1; done)
J1=$(echo "$ALL" | awk 'NR%2==1'); J2=$(echo "$ALL" | awk 'NR%2==0')
judge_lane "$J1" & judge_lane "$J2" & wait
for T in $ALL; do grep -q "DONE $T" results/survey/$T/judge.log 2>/dev/null && echo "DONE $T"; done
echo ALLDONE
