#!/bin/bash
cd ~/AgentQO && source ~/env.sh; export PYTHONUNBUFFERED=1; set -o pipefail
H1=data/vllm/c14_h1_cautious_n100/h1/math_reasoning_s3_ver/h1_summary.json
stop() { echo "$1"; echo "E_CHAIN_EXIT=1"; exit 1; }
health() { curl -s -m 10 localhost:8001/v1/models >/dev/null && curl -s -m 10 http://$VMB:8002/v1/models >/dev/null; }
# ---- E1
date -u; health || stop "server down before E1"
{ echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) (UTC) ==="; cat /tmp/pre_e1.txt; echo; } >> logs/preregistration.txt
{ date -u; AGENTQO_VERIFIER=cautious python3 -u scripts/run_real_h3.py --backend vllm --split eval --n-tasks 200 \
   --plans output_top1,output_top2,output_top3,ec_top3,ec_top2,all_large --compare ec_top2:output_top2 --compare ec_top3:output_top3 \
   --h1-summary $H1 --cache data/cache/vllm.sqlite --output-dir data/vllm/e1_output_cautious; echo "E1_EXIT=$?"; date -u; } 2>&1 | tee logs/e1_output_cautious.txt
grep -q "E1_EXIT=0" logs/e1_output_cautious.txt || stop "E1 failed"
{ python3 -u /tmp/e1_check.py; echo "E1_CHECK_EXIT=$?"; } 2>&1 | tee logs/e1_checks.txt
# ---- E2a
date -u; health || stop "server down before E2a"
{ echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) (UTC) ==="; cat /tmp/pre_e2.txt; echo; } >> logs/preregistration.txt
{ date -u; AGENTQO_VERIFIER=cautious python3 -u scripts/run_real_pipeline.py --backend vllm --stage h1 --n-tasks 100 --workflows complex \
   --workers 16 --max-tokens 256 --k 3 --corruptions 2 --cache data/cache/vllm.sqlite --output-dir data/vllm/e2_complex_h1_n100; echo "E2A_EXIT=$?"; date -u; } 2>&1 | tee logs/e2a_complex_h1_n100.txt
grep -q "E2A_EXIT=0" logs/e2a_complex_h1_n100.txt || stop "E2a failed"
{ date -u; python3 -u /tmp/e2a_analysis.py; echo; python3 -u scripts/verifier_analysis.py --details --workflow-dir complex_r2_s2_ver data/vllm/e2_complex_h1_n100; echo "E2A_ANALYSIS_EXIT=$?"; } 2>&1 | tee logs/e2a_analysis.txt
grep -q "E2A_ANALYSIS_EXIT=0" logs/e2a_analysis.txt || stop "E2a analysis failed"
# ---- E2b
date -u; health || stop "server down before E2b"
E2H1=data/vllm/e2_complex_h1_n100/h1/complex_r2_s2_ver
{ date -u; AGENTQO_VERIFIER=cautious python3 -u scripts/run_real_h3.py --backend vllm --workflow complex --split eval --n-tasks 200 --workers 16 \
   --plans "$(cat /tmp/e2b_plans.txt)" $(cat /tmp/e2b_compare.txt) --budget-plot --h1-summary $E2H1/h1_summary.json --qplus-from $E2H1 \
   --cache data/cache/vllm.sqlite --output-dir data/vllm/e2_complex_h3_eval200; echo "E2B_EXIT=$?"; date -u; } 2>&1 | tee logs/e2b_complex_h3_eval200.txt
grep -q "E2B_EXIT=0" logs/e2b_complex_h3_eval200.txt || stop "E2b failed"
{ python3 -u /tmp/e2b_check.py; echo "E2B_CHECK_EXIT=$?"; } 2>&1 | tee logs/e2b_checks.txt
echo "E_CHAIN_EXIT=0"
