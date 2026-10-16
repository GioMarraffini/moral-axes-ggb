#!/bin/bash
# Stop a running H100 chain and its python children. Usage: bash h100_kill.sh <script name>
pkill -f "^bash cluster/$1"; sleep 1; pkill -f "^/root/mp/.venv/bin/python scripts/(generate|judge).py"; sleep 3
nvidia-smi --query-gpu=memory.used --format=csv,noheader
