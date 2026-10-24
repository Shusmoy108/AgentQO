#!/bin/bash
cd ~/AgentQO
set -o pipefail
gpu_check() {  # expected number of compute processes on VM-A
  local n=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)
  echo "$(date -u +%H:%M:%S) GPU check VM-A: $n compute process(es), expected $1"; nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
  [ "$n" = "$1" ] || { echo "GPU CHECK FAILED"; exit 1; }
}
{
gpu_check 1 && bash /tmp/grid.sh separate 1 "32 128 512" && \
gpu_check 1 && bash /tmp/grid.sh separate 2 "32 128 512" && \
bash /tmp/serve.sh start8003 && gpu_check 2 && \
bash /tmp/grid.sh shared 0 "32 128 512" && gpu_check 2 && \
bash /tmp/grid.sh shared 1 "32 128 512" && gpu_check 2 && \
bash /tmp/grid.sh shared 2 "32 128 512"
echo "H4_P1A_CHAIN_EXIT=$?"
} 2>&1 | tee logs/h4_p1a_chain.txt
