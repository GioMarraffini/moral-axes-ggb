#!/bin/bash
#SBATCH -J np_chunks
#SBATCH -p normal
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 00:20:00
#SBATCH -o /data/parietal/store3/work/gmarraff/moral-axes-ggb/logs/%x_%j.out
#SBATCH -e /data/parietal/store3/work/gmarraff/moral-axes-ggb/logs/%x_%j.err
set -euo pipefail
S=/data/parietal/store3/work/gmarraff/repos/moral-axes-ggb
W=/data/parietal/store3/work/gmarraff/moral-axes-ggb
V=/data/parietal/store3/work/gmarraff/repos/manifold-persona/.venv_pascal
export PYTHONPATH=$S
cd $S
$V/bin/python scripts/judge_chunks.py "$W/qwen7b/grid_np/*.jsonl" --out $W/qwen7b/grid_np/judge
echo CHUNKSDONE
