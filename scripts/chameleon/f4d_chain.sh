#!/bin/bash
# F4d: plan-level selection on the Qwen settings (default Qwen models, max_tokens 256, data/cache/vllm.sqlite).
cd ~/AgentQO && source ~/env.sh; export PYTHONUNBUFFERED=1; set -o pipefail
unset VLLM_SMALL_MODEL VLLM_LARGE_MODEL
T=/tmp/f4_tools.py; O=data/vllm/f4_qwen_valid_plans
date -u; curl -s localhost:8001/v1/models | grep -o '"id":"[^"]*"' | head -1; curl -s http://$VMB:8002/v1/models | grep -o '"id":"[^"]*"' | head -1
run_setting() {  # name workflow verifier h1dir evaldirs...
  local NAME=$1 WF=$2 VER=$3 H1=$4; shift 4
  if [ $(date -u +%H%M) -ge 1745 ]; then echo "SKIPPED $NAME: past 17:45 UTC, could not finish by 18:00"; return 0; fi
  mkdir -p $O/$NAME
  AGENTQO_VERIFIER=$VER python3 $T candidates --setting $NAME --workflow $WF --verifier $VER --eval-dirs "$@" --h1 $H1 \
     --out $O/$NAME/candidates.json > /tmp/f4d_custom_$NAME.txt 2> /tmp/f4d_plans_$NAME.txt || { echo "candidates failed for $NAME"; return 1; }
  { date -u; AGENTQO_VERIFIER=$VER python3 -u scripts/run_real_h3.py --backend vllm --workflow $WF --split valid --n-tasks 100 --workers 16 \
       --plans "$(cat /tmp/f4d_plans_$NAME.txt)" $(cat /tmp/f4d_custom_$NAME.txt) --cache data/cache/vllm.sqlite --output-dir $O/$NAME; echo "F4D_${NAME^^}_EXIT=$?"; date -u; } 2>&1 | tee logs/f4d_$NAME.txt
  grep -q "F4D_${NAME^^}_EXIT=0" logs/f4d_$NAME.txt || return 1
  { python3 -u $T select --candidates $O/$NAME/candidates.json --valid $O/$NAME --out $O/$NAME/selection.json; echo "F4D_${NAME^^}_SELECT_EXIT=$?"; } 2>&1 | tee logs/f4d_${NAME}_selection.txt
}
run_setting math_passthrough math passthrough data/vllm/h1_math_passthrough_n100/h1/math_reasoning_s3_ver data/vllm/h3_eval_n200 data/vllm/c12_qplus_top2 data/vllm/c13_budget_curve || { echo "F4D_CHAIN_EXIT=1"; exit 1; }
run_setting math_cautious math cautious data/vllm/c14_h1_cautious_n100/h1/math_reasoning_s3_ver data/vllm/c14_h3_cautious_eval200 data/vllm/e1_output_cautious || { echo "F4D_CHAIN_EXIT=1"; exit 1; }
run_setting complex_cautious complex cautious data/vllm/e2_complex_h1_n100/h1/complex_r2_s2_ver data/vllm/e2_complex_h3_eval200 || { echo "F4D_CHAIN_EXIT=1"; exit 1; }
run_setting complex_passthrough complex passthrough data/vllm/f1_complex_passthrough_h1_n100/h1/complex_r2_s2_ver data/vllm/f1_complex_passthrough_h3_eval200 || { echo "F4D_CHAIN_EXIT=1"; exit 1; }
echo "F4D_CHAIN_EXIT=0"
