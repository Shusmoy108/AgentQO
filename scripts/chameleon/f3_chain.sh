#!/bin/bash
cd ~/AgentQO && source ~/env.sh; export PYTHONUNBUFFERED=1 AGENTQO_VERIFIER=passthrough; set -o pipefail
export VLLM_SMALL_MODEL=ibm-granite/granite-3.1-2b-instruct VLLM_LARGE_MODEL=ibm-granite/granite-3.1-8b-instruct
GC=data/cache/vllm_granite.sqlite
stop() { echo "$1"; echo "F3_CHAIN_EXIT=1"; exit 1; }
PLANS="all_large,$(python3 -c "from scripts.run_real_pipeline import WORKFLOWS; print(','.join('only_'+n for n in WORKFLOWS['math'][1]().topological_order))"),ec_top1,ec_top2,ec_top3,struct_top1,struct_top2,struct_top3,output_top1,output_top2,output_top3,qplus_top1,qplus_top2,qplus_top3"
CMP=""; for k in 1 2 3; do CMP="$CMP --compare ec_top$k:output_top$k --compare qplus_top$k:output_top$k --compare qplus_top$k:ec_top$k --compare ec_top$k:struct_top$k"; done
H1ARGS="--backend vllm --stage h1 --workflows math --workers 16 --max-tokens 512 --k 3 --corruptions 2 --cache $GC"
date -u; curl -s localhost:8001/v1/models | grep -o '"id":"[^"]*"' | head -1; curl -s http://$VMB:8002/v1/models | grep -o '"id":"[^"]*"' | head -1
# ---- smoke gate (3 dev problems incl. gsm8k-test-1282)
T0=$(date +%s.%N)
{ python3 -u scripts/run_real_pipeline.py $H1ARGS --n-tasks 3 --output-dir /tmp/smoke_f3a && python3 -u /tmp/f3_smoke_check.py /tmp/smoke_f3a $T0; echo "SMOKE_F3_EXIT=$?"; } 2>&1 | tee logs/smoke_f3.txt | grep -vE "it/s\]|s/it\]"
grep -q "SMOKE_F3_EXIT=0" logs/smoke_f3.txt || stop "F3 smoke gate failed"
# ---- F3a
date -u; [ $(date -u +%H%M) -lt 1600 ] || stop "too late to start F3a"
T1=$(date +%s.%N)
{ date -u; python3 -u scripts/run_real_pipeline.py $H1ARGS --n-tasks 100 --output-dir data/vllm/f3_granite512_h1_n100; echo "F3A_EXIT=$?"; date -u; } 2>&1 | tee logs/f3a_granite512_h1_n100.txt
grep -q "F3A_EXIT=0" logs/f3a_granite512_h1_n100.txt || stop "F3a failed"
python3 /tmp/ids_check.py dev data/vllm/f3_granite512_h1_n100/run_config.json 2>&1 | tee logs/f3_checks.txt || stop "F3a IDs differ"
{ date -u; python3 -u /tmp/f3_calls.py $GC $T1 512; echo; python3 -u /tmp/f3a_analysis.py; echo; python3 -u scripts/verifier_analysis.py --details data/vllm/f3_granite512_h1_n100; echo "F3A_ANALYSIS_EXIT=$?"; } 2>&1 | tee logs/f3a_analysis.txt
grep -q "F3A_ANALYSIS_EXIT=0" logs/f3a_analysis.txt || stop "F3a analysis failed"
# ---- F3b (only if it can finish by 16:45: start by 16:25)
date -u; [ $(date -u +%H%M) -lt 1625 ] || stop "F3b not started: it could not finish by 16:45 UTC"
H=data/vllm/f3_granite512_h1_n100/h1/math_reasoning_s3_ver
T2=$(date +%s.%N)
{ date -u; python3 -u scripts/run_real_h3.py --backend vllm --workflow math --split eval --n-tasks 200 --workers 16 --max-tokens 512 --plans "$PLANS" $CMP --budget-plot \
   --h1-summary $H/h1_summary.json --qplus-from $H --cache $GC --output-dir data/vllm/f3_granite512_h3_eval200; echo "F3B_EXIT=$?"; date -u; } 2>&1 | tee logs/f3b_granite512_h3_eval200.txt
grep -q "F3B_EXIT=0" logs/f3b_granite512_h3_eval200.txt || stop "F3b failed"
python3 /tmp/ids_check.py eval data/vllm/f3_granite512_h3_eval200/h3_summary.json 2>&1 | tee -a logs/f3_checks.txt || stop "F3b IDs differ"
python3 -u /tmp/f3_calls.py $GC $T2 512 2>&1 | tee -a logs/f3_checks.txt
echo "F3_CHAIN_EXIT=0"
