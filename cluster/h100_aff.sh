#!/bin/bash
# Affine-hook grid for a model whose base answers are judged: token statistics at one
# layer, then the grid (scales, controls, judge).
# Usage: bash h100_aff.sh <model> <tag> <layer> <cells json> <subdir>
set -euo pipefail
M=$1; T=$2; L=$3; G=$4; S=$5
cd /root/moral-axes-ggb
export PYTHONPATH=/root/moral-axes-ggb HF_HOME=/scratch/hf_cache
[ -f /root/.hf_token ] && export HF_TOKEN=$(cat /root/.hf_token)
P=/root/mp/.venv/bin/python
R=results/$T
D=$R/directions/aff_L$L.npz
[ -f $D ] || $P scripts/aff_stats.py --model $M --responses "$R/base/moral.jsonl" --judge $R/base/judge \
  --directions $R/directions/directions.npz --layer $L --dtype bf16 --bs 8 --out $D
bash cluster/h100_grid.sh $M $T $G $S $D
echo "AFF DONE $T $S $(date -u)"
