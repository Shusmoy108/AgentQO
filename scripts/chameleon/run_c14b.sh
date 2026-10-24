#!/bin/bash
cd ~/AgentQO && source ~/env.sh
export PYTHONUNBUFFERED=1
set -o pipefail
date -u | tee logs/c14b_verifier_cautious.txt
python3 -u scripts/verifier_analysis.py --details data/vllm/c14_h1_cautious_n100 2>&1 | tee -a logs/c14b_verifier_cautious.txt
echo "C14B_EXIT=$?" | tee -a logs/c14b_verifier_cautious.txt
