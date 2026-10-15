#!/bin/bash
cd /root/moral-axes-ggb
for p in $(pgrep -f "h100_next_model|h100_next_model_resume|scripts/generate.py|scripts/judge.py|directions_resp.py"); do [ "$p" != "$$" ] && kill $p 2>/dev/null; done
sleep 3
rm -rf results/qwen7b
nohup bash h100_next_model.sh Qwen/Qwen2.5-7B-Instruct qwen7b results/grid_cells_qwen7b.json > qwen7b.log 2>&1 &
sleep 5
pgrep -af "h100_next_model|scripts/generate.py" | grep -v pgrep | cut -c1-80
