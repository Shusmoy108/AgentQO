#!/bin/bash
cd ~/AgentQO && source ~/env.sh; export PYTHONUNBUFFERED=1 AGENTQO_VERIFIER=passthrough; set -o pipefail
export VLLM_SMALL_MODEL=ibm-granite/granite-3.1-2b-instruct VLLM_LARGE_MODEL=ibm-granite/granite-3.1-8b-instruct
GC=data/cache/vllm_granite.sqlite
stop() { echo "$1"; echo "F5_CHAIN_EXIT=1"; exit 1; }
PL="$(cat /tmp/f4c_plans.txt)"; CU="$(cat /tmp/f4c_custom.txt)"
echo "plans: $PL"
date -u; curl -s localhost:8001/v1/models | grep -o '"id":"[^"]*"' | head -1; curl -s http://$VMB:8002/v1/models | grep -o '"id":"[^"]*"' | head -1
{ for sp in valid2 eval2; do python3 -u scripts/run_real_h3.py --backend vllm --workflow math --split $sp --n-tasks 3 --workers 16 --max-tokens 512 \
     --plans all_small,set_planner,set_aggregator --custom-plan set_planner:planner --custom-plan set_aggregator:aggregator --cache $GC --output-dir /tmp/smoke_f5_$sp || exit 1; done; echo "SMOKE_F5_EXIT=$?"; } 2>&1 | tee logs/smoke_f5.txt | grep -E "acc=|EXIT|Error|Traceback"
grep -q "SMOKE_F5_EXIT=0" logs/smoke_f5.txt || stop "F5 smoke failed"
for sp in valid2 eval2; do
  N=${sp^^}
  { date -u; python3 -u scripts/run_real_h3.py --backend vllm --workflow math --split $sp --n-tasks 300 --workers 16 --max-tokens 512 --plans "$PL" $CU \
       --cache $GC --output-dir data/vllm/f5_granite_$sp; echo "F5A_${N}_EXIT=$?"; date -u; } 2>&1 | tee logs/f5a_granite_$sp.txt
  grep -q "F5A_${N}_EXIT=0" logs/f5a_granite_$sp.txt || stop "F5a $sp failed"
done
echo "F5_CHAIN_EXIT=0"
