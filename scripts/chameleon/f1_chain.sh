#!/bin/bash
cd ~/AgentQO && source ~/env.sh; export PYTHONUNBUFFERED=1 AGENTQO_VERIFIER=passthrough; set -o pipefail
stop() { echo "$1"; echo "F1_CHAIN_EXIT=1"; exit 1; }
PLANS="all_large,$(python3 -c "from scripts.run_real_pipeline import WORKFLOWS; print(','.join('only_'+n for n in WORKFLOWS['complex'][1]().topological_order))"),ec_top1,ec_top2,ec_top3,struct_top1,struct_top2,struct_top3,output_top1,output_top2,output_top3,qplus_top1,qplus_top2,qplus_top3"
CMP=""; for k in 1 2 3; do CMP="$CMP --compare ec_top$k:output_top$k --compare qplus_top$k:output_top$k --compare qplus_top$k:ec_top$k --compare ec_top$k:struct_top$k"; done
H1ARGS="--backend vllm --stage h1 --n-tasks 100 --workflows complex --workers 16 --max-tokens 256 --k 3 --corruptions 2 --cache data/cache/vllm.sqlite"
date -u
# ---- smoke (3 problems, /tmp)
{ python3 -u scripts/run_real_pipeline.py ${H1ARGS/--n-tasks 100/--n-tasks 3} --output-dir /tmp/smoke_f1a && \
  python3 -u scripts/run_real_h3.py --backend vllm --workflow complex --split eval --n-tasks 3 --workers 16 --plans "$PLANS" $CMP --budget-plot \
    --h1-summary /tmp/smoke_f1a/h1/complex_r2_s2_ver/h1_summary.json --qplus-from /tmp/smoke_f1a/h1/complex_r2_s2_ver --cache data/cache/vllm.sqlite --output-dir /tmp/smoke_f1b; echo "SMOKE_F1_EXIT=$?"; } 2>&1 | tee logs/smoke_f1.txt | grep -E "plan |EXIT|Error|Traceback"
grep -q "SMOKE_F1_EXIT=0" logs/smoke_f1.txt || stop "F1 smoke failed"
# ---- F1a
date -u; { echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) (UTC) ==="; cat /tmp/pre_f1.txt; echo; } >> logs/preregistration.txt
{ date -u; python3 -u scripts/run_real_pipeline.py $H1ARGS --output-dir data/vllm/f1_complex_passthrough_h1_n100; echo "F1A_EXIT=$?"; date -u; } 2>&1 | tee logs/f1a_complex_passthrough_h1_n100.txt
grep -q "F1A_EXIT=0" logs/f1a_complex_passthrough_h1_n100.txt || stop "F1a failed"
python3 /tmp/ids_check.py dev data/vllm/f1_complex_passthrough_h1_n100/run_config.json 2>&1 | tee logs/f1_checks.txt || stop "F1a IDs differ"
# ---- F1b
H=data/vllm/f1_complex_passthrough_h1_n100/h1/complex_r2_s2_ver
date -u; { date -u; python3 -u scripts/run_real_h3.py --backend vllm --workflow complex --split eval --n-tasks 200 --workers 16 --plans "$PLANS" $CMP --budget-plot \
   --h1-summary $H/h1_summary.json --qplus-from $H --cache data/cache/vllm.sqlite --output-dir data/vllm/f1_complex_passthrough_h3_eval200; echo "F1B_EXIT=$?"; date -u; } 2>&1 | tee logs/f1b_complex_passthrough_h3_eval200.txt
grep -q "F1B_EXIT=0" logs/f1b_complex_passthrough_h3_eval200.txt || stop "F1b failed"
python3 /tmp/ids_check.py eval data/vllm/f1_complex_passthrough_h3_eval200/h3_summary.json 2>&1 | tee -a logs/f1_checks.txt || stop "F1b IDs differ"
echo "F1_CHAIN_EXIT=0"
