#!/bin/bash
cd ~/AgentQO && source ~/env.sh
export PYTHONUNBUFFERED=1
set -o pipefail
{ echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) (UTC) ==="; cat /tmp/pre_c12.txt; echo; } >> logs/preregistration.txt
date -u | tee logs/c12_qplus_top2.txt
AGENTQO_VERIFIER=passthrough python3 -u scripts/run_real_h3.py --backend vllm --split eval --n-tasks 200 \
  --plans qplus_top2,ec_top2,all_large --compare qplus_top2:ec_top2 \
  --h1-summary data/vllm/h1_math_passthrough_n100/h1/math_reasoning_s3_ver/h1_summary.json \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/c12_qplus_top2 2>&1 | tee -a logs/c12_qplus_top2.txt
echo "C12_EXIT=$?" | tee -a logs/c12_qplus_top2.txt
