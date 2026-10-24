#!/bin/bash
cd ~/AgentQO && source ~/env.sh; export PYTHONUNBUFFERED=1 AGENTQO_VERIFIER=passthrough; set -o pipefail
export VLLM_SMALL_MODEL=ibm-granite/granite-3.1-2b-instruct VLLM_LARGE_MODEL=ibm-granite/granite-3.1-8b-instruct
GC=data/cache/vllm_granite.sqlite
stop() { echo "$1"; echo "F2_CHAIN_EXIT=1"; exit 1; }
PLANS="all_large,$(python3 -c "from scripts.run_real_pipeline import WORKFLOWS; print(','.join('only_'+n for n in WORKFLOWS['math'][1]().topological_order))"),ec_top1,ec_top2,ec_top3,struct_top1,struct_top2,struct_top3,output_top1,output_top2,output_top3,qplus_top1,qplus_top2,qplus_top3"
CMP=""; for k in 1 2 3; do CMP="$CMP --compare ec_top$k:output_top$k --compare qplus_top$k:output_top$k --compare qplus_top$k:ec_top$k --compare ec_top$k:struct_top$k"; done
H1ARGS="--backend vllm --stage h1 --workflows math --workers 16 --max-tokens 256 --k 3 --corruptions 2 --cache $GC"
date -u; curl -s localhost:8001/v1/models | grep -o '"id":"[^"]*"' | head -1; curl -s http://$VMB:8002/v1/models | grep -o '"id":"[^"]*"' | head -1
# ---- smoke: logprobs (stage smoke) + extraction on 3 problems + H3 plan list
{ python3 -u scripts/run_real_pipeline.py --backend vllm --stage smoke --n-tasks 3 --workflows math --cache /tmp/smoke_f2_cache.sqlite --output-dir /tmp/smoke_f2s && \
  python3 -u scripts/run_real_pipeline.py $H1ARGS --n-tasks 3 --output-dir /tmp/smoke_f2a && \
  python3 -u /tmp/f2_extract_check.py /tmp/smoke_f2a && \
  python3 -u scripts/run_real_h3.py --backend vllm --workflow math --split eval --n-tasks 3 --workers 16 --plans "$PLANS" $CMP --budget-plot \
    --h1-summary /tmp/smoke_f2a/h1/math_reasoning_s3_ver/h1_summary.json --qplus-from /tmp/smoke_f2a/h1/math_reasoning_s3_ver --cache $GC --output-dir /tmp/smoke_f2b; echo "SMOKE_F2_EXIT=$?"; } 2>&1 | tee logs/smoke_f2.txt | grep -E "conf_src|EXTRACTION|plan |EXIT|Error|Traceback"
grep -q "SMOKE_F2_EXIT=0" logs/smoke_f2.txt || stop "F2 smoke failed (see logs/smoke_f2.txt)"
grep -q "conf_src=logprobs" logs/smoke_f2.txt || stop "F2 smoke: no logprobs"
# ---- F2a
date -u; { echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) (UTC) ==="; cat /tmp/pre_f2.txt; echo; } >> logs/preregistration.txt
{ date -u; python3 -u scripts/run_real_pipeline.py $H1ARGS --n-tasks 100 --output-dir data/vllm/f2_granite_h1_n100; echo "F2A_EXIT=$?"; date -u; } 2>&1 | tee logs/f2a_granite_h1_n100.txt
grep -q "F2A_EXIT=0" logs/f2a_granite_h1_n100.txt || stop "F2a failed"
python3 /tmp/ids_check.py dev data/vllm/f2_granite_h1_n100/run_config.json 2>&1 | tee logs/f2_checks.txt || stop "F2a IDs differ"
{ python3 -u scripts/verifier_analysis.py --details data/vllm/f2_granite_h1_n100; echo "F2A_VERIFIER_EXIT=$?"; } 2>&1 | tee logs/f2a_verifier.txt
# ---- F2b
H=data/vllm/f2_granite_h1_n100/h1/math_reasoning_s3_ver
date -u; { date -u; python3 -u scripts/run_real_h3.py --backend vllm --workflow math --split eval --n-tasks 200 --workers 16 --plans "$PLANS" $CMP --budget-plot \
   --h1-summary $H/h1_summary.json --qplus-from $H --cache $GC --output-dir data/vllm/f2_granite_h3_eval200; echo "F2B_EXIT=$?"; date -u; } 2>&1 | tee logs/f2b_granite_h3_eval200.txt
grep -q "F2B_EXIT=0" logs/f2b_granite_h3_eval200.txt || stop "F2b failed"
python3 /tmp/ids_check.py eval data/vllm/f2_granite_h3_eval200/h3_summary.json 2>&1 | tee -a logs/f2_checks.txt || stop "F2b IDs differ"
echo "F2_CHAIN_EXIT=0"
