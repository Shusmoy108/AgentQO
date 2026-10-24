#!/bin/bash
cd ~/AgentQO && source ~/env.sh
export PYTHONUNBUFFERED=1
set -o pipefail
{ echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) (UTC) ==="; cat /tmp/pre_c14.txt; echo; } >> logs/preregistration.txt
date -u | tee logs/c14a_h1_cautious_n100.txt
AGENTQO_VERIFIER=cautious python3 -u scripts/run_real_pipeline.py --backend vllm --stage h1 --n-tasks 100 --workflows math \
  --workers 16 --max-tokens 256 --k 3 --corruptions 2 \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/c14_h1_cautious_n100 2>&1 | tee -a logs/c14a_h1_cautious_n100.txt
echo "C14A_EXIT=$?" | tee -a logs/c14a_h1_cautious_n100.txt
date -u | tee -a logs/c14a_h1_cautious_n100.txt
