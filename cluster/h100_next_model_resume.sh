#!/bin/bash
# Resume h100_next_model.sh after the base answers are judged. Usage: <model> <tag> <grid cells json>
set -euo pipefail
M=$1; T=$2; G=$3
cd /root/moral-axes-ggb
export PYTHONPATH=/root/moral-axes-ggb HF_HOME=/scratch/hf_cache
P=/root/mp/.venv/bin/python
I=only_text,inverted_only_text,likert_scale,inverted_agreement_and_numbers_likert_scale
R=results/$T
$P scripts/directions_resp.py --model $M --responses "$R/base/moral.jsonl" --judge $R/base/judge --dtype bf16 --out $R/directions
$P scripts/generate.py --model $M --directions $R/directions/directions.npz --cells $G --split test --types IB,IH \
  --iterations 3 --instructions $I --dtype bf16 --bs 48 --out $R/grid/moral.jsonl
$P scripts/generate.py --model $M --directions $R/directions/directions.npz --cells $G --split test \
  --types neutral,harm_no_benefit,kindness --iterations 1 --instructions $I --dtype bf16 --bs 48 --out $R/grid/ctrl.jsonl
$P scripts/judge_chunks.py "$R/grid/*.jsonl" --out $R/grid/judge
$P scripts/judge.py --chunks $R/grid/judge --dtype bf16 --bs 16
echo ALLDONE
