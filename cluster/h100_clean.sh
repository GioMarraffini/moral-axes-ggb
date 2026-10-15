#!/bin/bash
# Orthogonalised directions: build control directions, generate, judge. Run on the H100.
set -euo pipefail
cd /root/moral-axes-ggb
export PYTHONPATH=/root/moral-axes-ggb HF_HOME=/scratch/hf_cache
P=/root/mp/.venv/bin/python
I=only_text,inverted_only_text,likert_scale,inverted_agreement_and_numbers_likert_scale
mkdir -p results/clean
$P scripts/directions_ctrl.py --responses "results/final_ctrl/*.jsonl" --judge results/judge_final \
  --merge results/directions_resp2/merged.npz --dtype bf16 --out results/directions_ctrl
$P scripts/generate.py --directions results/directions_ctrl/directions.npz --cells results/clean_cells.json \
  --split test --types IB,IH --iterations 3 --instructions $I --dtype bf16 --bs 64 --out results/clean/moral.jsonl
$P scripts/generate.py --directions results/directions_ctrl/directions.npz --cells results/clean_cells.json \
  --split test --types neutral,harm_no_benefit,kindness --iterations 3 --instructions $I --dtype bf16 --bs 64 --out results/clean/ctrl.jsonl
$P scripts/judge_chunks.py "results/clean/*.jsonl" --out results/clean/judge
$P scripts/judge.py --chunks results/clean/judge --dtype bf16 --bs 16
echo ALLDONE
