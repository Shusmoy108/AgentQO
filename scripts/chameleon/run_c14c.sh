#!/bin/bash
cd ~/AgentQO && source ~/env.sh
export PYTHONUNBUFFERED=1
set -o pipefail
date -u | tee logs/c14c_h3_cautious_eval200.txt
AGENTQO_VERIFIER=cautious python3 -u scripts/run_real_h3.py --backend vllm --split eval --n-tasks 200 \
  --h1-summary data/vllm/c14_h1_cautious_n100/h1/math_reasoning_s3_ver/h1_summary.json \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/c14_h3_cautious_eval200 2>&1 | tee -a logs/c14c_h3_cautious_eval200.txt
echo "C14C_EXIT=$?" | tee -a logs/c14c_h3_cautious_eval200.txt
date -u | tee -a logs/c14c_h3_cautious_eval200.txt
