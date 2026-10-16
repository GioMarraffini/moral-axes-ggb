#!/bin/bash
# Steered grid for a model whose directions exist: scales (3 iterations), controls (1), judge.
# Usage: bash h100_grid.sh <model> <tag> <cells json> <subdir>
set -euo pipefail
M=$1; T=$2; G=$3; S=$4
cd /root/moral-axes-ggb
export PYTHONPATH=/root/moral-axes-ggb HF_HOME=/scratch/hf_cache
P=/root/mp/.venv/bin/python
I=only_text,inverted_only_text,likert_scale,inverted_agreement_and_numbers_likert_scale
R=results/$T; mkdir -p $R/$S
$P scripts/generate.py --model $M --directions $R/directions/directions.npz --cells $G --split test --types IB,IH \
  --iterations 3 --instructions $I --dtype bf16 --bs 48 --out $R/$S/moral.jsonl
$P scripts/generate.py --model $M --directions $R/directions/directions.npz --cells $G --split test \
  --types neutral,harm_no_benefit,kindness --iterations 1 --instructions $I --dtype bf16 --bs 48 --out $R/$S/ctrl.jsonl
$P scripts/judge_chunks.py "$R/$S/*.jsonl" --out $R/$S/judge
$P scripts/judge.py --chunks $R/$S/judge --dtype bf16 --bs 16
echo ALLDONE
