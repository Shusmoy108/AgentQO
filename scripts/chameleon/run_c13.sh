#!/bin/bash
cd ~/AgentQO && source ~/env.sh
export PYTHONUNBUFFERED=1
set -o pipefail
{ echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) (UTC) ==="; cat /tmp/pre_c13.txt; echo; } >> logs/preregistration.txt
date -u | tee logs/c13_budget_curve.txt
AGENTQO_VERIFIER=passthrough python3 -u scripts/run_real_h3.py --backend vllm --split eval --n-tasks 200 \
  --plans all_large,ec_top1,ec_top2,ec_top3,ec_top4,struct_top1,struct_top2,struct_top3,struct_top4 --budget-plot \
  --h1-summary data/vllm/h1_math_passthrough_n100/h1/math_reasoning_s3_ver/h1_summary.json \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/c13_budget_curve 2>&1 | tee -a logs/c13_budget_curve.txt
echo "C13_EXIT=$?" | tee -a logs/c13_budget_curve.txt
