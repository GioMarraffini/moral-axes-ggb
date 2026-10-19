#!/bin/bash
#SBATCH -J np_prompted
#SBATCH -p gpu-best
#SBATCH --gres=gpu:hopper:1
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -t 02:00:00
#SBATCH -o /data/parietal/store3/work/gmarraff/moral-axes-ggb/logs/%x_%j.out
#SBATCH -e /data/parietal/store3/work/gmarraff/moral-axes-ggb/logs/%x_%j.err
# IH answers under the IH system prompt on the train statements, judged, then the IH
# direction from those accepting answers and the unprompted rejecting ones, all re-encoded
# with no axis prompt.
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
if p.total_memory < 40 * 2**30:
    sys.exit("GPU has under 40 GB")
if not any(a.startswith(f"sm_{p.major}") and int(a[-1]) <= p.minor for a in torch.cuda.get_arch_list()):
    sys.exit(f"no kernels for sm_{p.major}{p.minor} in {torch.cuda.get_arch_list()}")
PRE
M=Qwen/Qwen2.5-7B-Instruct
R=$W/qwen7b
INS=only_text,inverted_only_text,likert_scale,inverted_agreement_and_numbers_likert_scale
mkdir -p $R/np
$V/bin/python scripts/generate.py --model $M --cells $S/results/prompt_IH_cells.json --split train --types IH \
  --iterations 10 --instructions $INS --dtype bf16 --bs 48 --out $R/np/prompted.jsonl
$V/bin/python scripts/judge_chunks.py "$R/np/prompted.jsonl" --out $R/np/judge_prompted
$V/bin/python scripts/judge.py --chunks $R/np/judge_prompted --dtype bf16 --bs 16
$V/bin/python scripts/directions_resp.py --model $M --responses "$R/base/moral.jsonl" "$R/np/prompted.jsonl" \
  --judge $R/base/judge $R/np/judge_prompted --cells "base,prompt|IH" --dtype bf16 --out $R/directions_np
echo PROMPTEDDONE
