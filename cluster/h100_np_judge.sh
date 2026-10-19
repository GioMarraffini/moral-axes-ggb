#!/bin/bash
# Judge shards 1 and 2 of the new-frame grid chunks side by side on one card.
set -euo pipefail
cd /root/moral-axes-ggb
export PYTHONPATH=/root/moral-axes-ggb HF_HOME=/scratch/hf_cache
P=/root/mp/.venv/bin/python
J=results/qwen7b/grid_np/judge
$P scripts/judge.py --chunks $J --shard 1/3 --dtype bf16 --bs 16 > $J/../judge_1.log 2>&1 &
$P scripts/judge.py --chunks $J --shard 2/3 --dtype bf16 --bs 16 > $J/../judge_2.log 2>&1 &
wait
echo JUDGEDONE
