#!/bin/bash
#SBATCH -J np_gen_r
#SBATCH --array=2-5%4
#SBATCH -p gpu-best
#SBATCH --gres=gpu:rtx:1
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -t 04:00:00
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
if p.total_memory < 20 * 2**30:
    sys.exit("GPU has under 20 GB")
if not any(a.startswith(f"sm_{p.major}") and int(a[-1]) <= p.minor for a in torch.cuda.get_arch_list()):
    sys.exit(f"no kernels for sm_{p.major}{p.minor} in {torch.cuda.get_arch_list()}")
PRE
I=$SLURM_ARRAY_TASK_ID
M=Qwen/Qwen2.5-7B-Instruct
D=$W/qwen7b/directions_np/directions.npz
C=$S/results/grid_cells_qwen7b_np_$I.json
INS=only_text,inverted_only_text,likert_scale,inverted_agreement_and_numbers_likert_scale
$V/bin/python scripts/generate.py --model $M --directions $D --cells $C --split test --types IB,IH \
  --iterations 3 --instructions $INS --dtype fp16 --bs 12 --out $W/qwen7b/grid_np/moral_$I.jsonl
$V/bin/python scripts/generate.py --model $M --directions $D --cells $C --split test \
  --types neutral,harm_no_benefit,kindness --iterations 1 --instructions $INS --dtype fp16 --bs 12 --out $W/qwen7b/grid_np/ctrl_$I.jsonl
echo GENDONE $I
