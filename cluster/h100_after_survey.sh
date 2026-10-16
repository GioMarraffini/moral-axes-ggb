#!/bin/bash
# Wait for the survey, rank the judged models by distance to the lay population, and run the
# full first-round pipeline (h100_next_model.sh) on the K nearest, one after the other.
# Usage: bash h100_after_survey.sh [K]
set -uo pipefail
K=${1:-2}
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
until grep -q ALLDONE survey.log; do sleep 120; done
QUEUE=$($P - "$K" <<'EOF'
import glob, json, sys
import numpy as np
from moral_axes import data
K = int(sys.argv[1])
DROP = ["inverted_agreement_likert_scale", "inverted_numbers_likert_scale"]
T = json.load(open("data/ggb/targets.json"))["lay_population"]
rows = []
for d in sorted(glob.glob("results/survey/*/")):
    tag = d.rstrip("/").split("/")[-1]
    if not glob.glob(d + "judge/judge_*.json"):
        continue
    df = data.judged(d + "*.jsonl", d + "judge")
    df = df[(df.split == "test") & ~df.instruction.isin(DROP) & (df.r > 0)]
    m = df.groupby(["type", "id"]).r.mean().groupby("type").mean()
    rows.append((float(np.hypot(m["IB"] - T["IB"], m["IH"] - T["IH"])), tag))
rows.sort()
print(" ".join(t for _, t in rows[:K]))
EOF
)
echo "queue: $QUEUE" | tee results/pipeline_queue.txt
for T in $QUEUE; do
  M=${MODEL[$T]}
  N=$($P -c "from transformers import AutoConfig; print(AutoConfig.from_pretrained('$M').num_hidden_layers)")
  L=$($P -c "n=$N; print(','.join(str(round(n*f)) for f in (0.5, 0.64, 0.75)))")
  $P scripts/grid_cells.py --layers $L --out results/grid_cells_$T.json
  echo "=== $T $M layers $N grid at $L"
  bash cluster/h100_next_model.sh $M $T results/grid_cells_$T.json > pipeline_$T.log 2>&1 \
    && echo "PIPELINE DONE $T" || echo "PIPELINE FAILED $T"
done
echo "PIPELINES DONE"
