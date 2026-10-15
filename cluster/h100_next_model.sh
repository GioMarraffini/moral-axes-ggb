#!/bin/bash
# Next model, steps that do not depend on the IH cleaning result: unprompted answers,
# judge, answer-built directions, 5 x 5 grid at three layers (scales and controls), judge.
# Usage: bash h100_next_model.sh <model> <tag> <grid cells json> [wait-for-log]
set -euo pipefail
M=$1; T=$2; G=$3; WAIT=${4:-}
cd /root/moral-axes-ggb
export PYTHONPATH=/root/moral-axes-ggb HF_HOME=/scratch/hf_cache
P=/root/mp/.venv/bin/python
I=only_text,inverted_only_text,likert_scale,inverted_agreement_and_numbers_likert_scale
if [ -n "$WAIT" ]; then until grep -q ALLDONE "$WAIT"; do sleep 60; done; fi
R=results/$T; mkdir -p $R/base $R/grid
echo '[{"kind":"base"}]' > $R/base_cells.json
$P scripts/generate.py --model $M --cells $R/base_cells.json --split all --types IB,IH --iterations 10 \
  --instructions $I --dtype bf16 --bs 48 --out $R/base/moral.jsonl
$P scripts/generate.py --model $M --cells $R/base_cells.json --split all --types neutral,harm_no_benefit,kindness \
  --iterations 3 --instructions $I --dtype bf16 --bs 48 --out $R/base/ctrl.jsonl
$P scripts/judge_chunks.py "$R/base/*.jsonl" --out $R/base/judge
$P scripts/judge.py --chunks $R/base/judge --dtype bf16 --bs 16
$P scripts/directions_resp.py --model $M --responses "$R/base/moral.jsonl" --judge $R/base/judge --dtype bf16 --out $R/directions
$P scripts/generate.py --model $M --directions $R/directions/directions.npz --cells $G --split test --types IB,IH \
  --iterations 3 --instructions $I --dtype bf16 --bs 48 --out $R/grid/moral.jsonl
$P scripts/generate.py --model $M --directions $R/directions/directions.npz --cells $G --split test \
  --types neutral,harm_no_benefit,kindness --iterations 1 --instructions $I --dtype bf16 --bs 48 --out $R/grid/ctrl.jsonl
$P scripts/judge_chunks.py "$R/grid/*.jsonl" --out $R/grid/judge
$P scripts/judge.py --chunks $R/grid/judge --dtype bf16 --bs 16
echo ALLDONE
