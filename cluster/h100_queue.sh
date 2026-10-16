#!/bin/bash
# Full first-round pipeline on a fixed list of survey tags, then the Mistral survey retry.
# Usage: bash h100_queue.sh tag ...
set -uo pipefail
cd /root/moral-axes-ggb
export PYTHONPATH=/root/moral-axes-ggb HF_HOME=/scratch/hf_cache
[ -f /root/.hf_token ] && export HF_TOKEN=$(cat /root/.hf_token)
P=/root/mp/.venv/bin/python
declare -A MODEL=([qwen05]=Qwen/Qwen2.5-0.5B-Instruct [qwen15]=Qwen/Qwen2.5-1.5B-Instruct
  [olmo1b]=allenai/OLMo-2-0425-1B-Instruct [smol17]=HuggingFaceTB/SmolLM2-1.7B-Instruct
  [llama1b]=meta-llama/Llama-3.2-1B-Instruct [gemma2b]=google/gemma-2-2b-it
  [phi4mini]=microsoft/Phi-4-mini-instruct [llama3b]=meta-llama/Llama-3.2-3B-Instruct
  [qwen14b]=Qwen/Qwen2.5-14B-Instruct [olmo7b]=allenai/OLMo-2-1124-7B-Instruct
  [llama8b]=meta-llama/Llama-3.1-8B-Instruct [mistral7b]=mistralai/Mistral-7B-Instruct-v0.3
  [gemma9b]=google/gemma-2-9b-it [olmo13b]=allenai/OLMo-2-1124-13B-Instruct)
echo "queue: $*" | tee results/pipeline_queue.txt
for T in "$@"; do
  M=${MODEL[$T]}
  N=$($P -c "from transformers import AutoConfig; print(AutoConfig.from_pretrained('$M').num_hidden_layers)")
  L=$($P -c "n=$N; print(','.join(str(round(n*f)) for f in (0.5, 0.64, 0.75)))")
  $P scripts/grid_cells.py --layers $L --out results/grid_cells_$T.json
  echo "=== $T $M layers $N grid at $L $(date)"
  bash cluster/h100_next_model.sh $M $T results/grid_cells_$T.json > pipeline_$T.log 2>&1 \
    && echo "PIPELINE DONE $T $(date)" || echo "PIPELINE FAILED $T"
done
rm -rf /scratch/hf_cache/hub/models--mistralai--Mistral-7B-Instruct-v0.3 results/survey/mistral7b
bash cluster/h100_survey_par.sh >> survey.log 2>&1
echo "PIPELINES DONE"
