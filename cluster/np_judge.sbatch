#!/bin/bash
#SBATCH -J np_judge
#SBATCH --array=0-2%3
#SBATCH -p gpu-best
#SBATCH --gres=gpu:hopper:1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 03:00:00
#SBATCH -o /data/parietal/store3/work/gmarraff/moral-axes-ggb/logs/%x_%A_%a.out
#SBATCH -e /data/parietal/store3/work/gmarraff/moral-axes-ggb/logs/%x_%A_%a.err
set -euo pipefail
S=/data/parietal/store3/work/gmarraff/repos/moral-axes-ggb
W=/data/parietal/store3/work/gmarraff/moral-axes-ggb
V=/data/parietal/store3/work/gmarraff/repos/manifold-persona/.venv_pascal
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-8}
export HF_HOME=/data/parietal/store3/work/gmarraff/hf_cache HF_HUB_OFFLINE=1
export TOKENIZERS_PARALLELISM=false PYTHONPATH=$S
cd $S
$V/bin/python - <<'PRE'
import sys, torch
if not torch.cuda.is_available():
    sys.exit("no CUDA device visible despite a --gres allocation")
p = torch.cuda.get_device_properties(0)
print("gpu", p.name, f"sm_{p.major}{p.minor}", f"{p.total_memory/2**30:.0f}GB")
if p.total_memory < 38 * 2**30:
    sys.exit("GPU has under 38 GB")
if not any(a.startswith(f"sm_{p.major}") and int(a[-1]) <= p.minor for a in torch.cuda.get_arch_list()):
    sys.exit(f"no kernels for sm_{p.major}{p.minor} in {torch.cuda.get_arch_list()}")
PRE
I=$SLURM_ARRAY_TASK_ID
$V/bin/python scripts/judge.py --chunks $W/qwen7b/grid_np/judge --shard $I/3 --dtype bf16 --bs 16
echo JUDGEDONE $I
