#!/bin/bash
cd ~/AgentQO && source ~/env.sh; export PYTHONUNBUFFERED=1 AGENTQO_VERIFIER=passthrough; set -o pipefail
export VLLM_SMALL_MODEL=ibm-granite/granite-3.1-2b-instruct VLLM_LARGE_MODEL=ibm-granite/granite-3.1-8b-instruct
GC=data/cache/vllm_granite.sqlite; T=/tmp/f4_tools.py
stop() { echo "$1"; echo "F4_GRANITE_CHAIN_EXIT=1"; exit 1; }
H1A="--backend vllm --stage h1 --workflows math --split label --workers 16 --max-tokens 512 --k 3 --corruptions 2 --cache $GC"
F4B_PLANS="all_small,struct_top1,struct_top2,struct_top3,ec500_top1,ec500_top2,ec500_top3,qplus500_top1,qplus500_top2,qplus500_top3"
F4B_CMP=""; for k in 1 2 3; do F4B_CMP="$F4B_CMP --compare qplus500_top$k:struct_top$k --compare ec500_top$k:struct_top$k"; done
date -u; curl -s localhost:8001/v1/models | grep -o '"id":"[^"]*"' | head -1; curl -s http://$VMB:8002/v1/models | grep -o '"id":"[^"]*"' | head -1
# ---- smoke (3 problems each, /tmp)
{ python3 -u scripts/run_real_pipeline.py $H1A --n-tasks 3 --output-dir /tmp/smoke_f4a && \
  python3 -u scripts/run_real_h3.py --backend vllm --workflow math --split eval --n-tasks 3 --workers 16 --max-tokens 512 --name-tag 500 --plans $F4B_PLANS $F4B_CMP \
     --h1-summary /tmp/smoke_f4a/h1/math_reasoning_s3_ver/h1_summary.json --qplus-from /tmp/smoke_f4a/h1/math_reasoning_s3_ver --cache $GC --output-dir /tmp/smoke_f4b && \
  python3 -u scripts/run_real_h3.py --backend vllm --workflow math --split valid --n-tasks 3 --workers 16 --max-tokens 512 --plans all_small,set_planner,set_aggregator+step_3 \
     --custom-plan set_planner:planner --custom-plan set_aggregator+step_3:aggregator+step_3 --cache $GC --output-dir /tmp/smoke_f4c; echo "SMOKE_F4_EXIT=$?"; } 2>&1 | tee logs/smoke_f4.txt | grep -E "plan |acc=|EXIT|Error|Traceback"
grep -q "SMOKE_F4_EXIT=0" logs/smoke_f4.txt || stop "F4 smoke failed"
# ---- F4a
date -u; [ $(date -u +%H%M) -lt 1730 ] || stop "too late for F4a"
{ date -u; python3 -u scripts/run_real_pipeline.py $H1A --n-tasks 500 --output-dir data/vllm/f4_granite_h1_n500; echo "F4A_EXIT=$?"; date -u; } 2>&1 | tee logs/f4a_granite_h1_n500.txt
grep -q "F4A_EXIT=0" logs/f4a_granite_h1_n500.txt || stop "F4a failed"
python3 -c "import json; a=json.load(open('data/vllm/f4_granite_h1_n500/run_config.json'))['qids']; c=json.load(open('data/vllm/h1_n100/run_config.json'))['qids']; print('F4a n =', len(a), '; first 100 identical to C7/F3a:', a[:100]==c)" 2>&1 | tee logs/f4_checks.txt
{ date -u; python3 -u $T curve --h1 data/vllm/f4_granite_h1_n500 --f3b data/vllm/f3_granite512_h3_eval200; echo "F4A_CURVE_EXIT=$?"; } 2>&1 | tee logs/f4a_label_curve.txt
grep -q "F4A_CURVE_EXIT=0" logs/f4a_label_curve.txt || stop "F4a curve failed"
# ---- F4b
date -u; H=data/vllm/f4_granite_h1_n500/h1/math_reasoning_s3_ver
{ date -u; python3 -u scripts/run_real_h3.py --backend vllm --workflow math --split eval --n-tasks 200 --workers 16 --max-tokens 512 --name-tag 500 --plans $F4B_PLANS $F4B_CMP \
   --h1-summary $H/h1_summary.json --qplus-from $H --cache $GC --output-dir data/vllm/f4_granite_h3_eval200; echo "F4B_EXIT=$?"; date -u; } 2>&1 | tee logs/f4b_granite_h3_eval200.txt
grep -q "F4B_EXIT=0" logs/f4b_granite_h3_eval200.txt || stop "F4b failed"
{ python3 /tmp/ids_check.py eval data/vllm/f4_granite_h3_eval200/h3_summary.json; python3 $T f4b-check --f3b data/vllm/f3_granite512_h3_eval200 --f4b data/vllm/f4_granite_h3_eval200; echo "F4B_CHECK_EXIT=$?"; } 2>&1 | tee -a logs/f4_checks.txt
# ---- F4c
date -u; [ $(date -u +%H%M) -lt 1745 ] || stop "too late for F4c"
mkdir -p data/vllm/f4_granite_valid_plans
python3 $T candidates --setting granite_math_passthrough --workflow math --verifier passthrough --eval-dirs data/vllm/f3_granite512_h3_eval200 data/vllm/f4_granite_h3_eval200 \
   --families struct output ec qplus ec500 qplus500 --out data/vllm/f4_granite_valid_plans/candidates.json > /tmp/f4c_custom.txt 2> /tmp/f4c_plans.txt || stop "candidates failed"
{ date -u; python3 -u scripts/run_real_h3.py --backend vllm --workflow math --split valid --n-tasks 100 --workers 16 --max-tokens 512 --plans "$(cat /tmp/f4c_plans.txt)" $(cat /tmp/f4c_custom.txt) \
   --cache $GC --output-dir data/vllm/f4_granite_valid_plans; echo "F4C_EXIT=$?"; date -u; } 2>&1 | tee logs/f4c_granite_valid_plans.txt
grep -q "F4C_EXIT=0" logs/f4c_granite_valid_plans.txt || stop "F4c failed"
{ python3 -u $T select --candidates data/vllm/f4_granite_valid_plans/candidates.json --valid data/vllm/f4_granite_valid_plans --qplus-n500 $H --out data/vllm/f4_granite_valid_plans/selection.json; echo "F4C_SELECT_EXIT=$?"; } 2>&1 | tee logs/f4c_selection.txt
echo "F4C_FINISHED_AT=$(date -u +%H:%M)"
echo "F4_GRANITE_CHAIN_EXIT=0"
