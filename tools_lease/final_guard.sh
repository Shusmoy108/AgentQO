#!/usr/bin/env bash
# Mac guards for the lease end (Chameleon lease ends 2026-11-19 22:38Z; PI schedule change 2026-11-18):
#  - new GPU work may start until 2026-11-19 14:00Z (orchestrators check this themselves);
#  - 15:30Z: stop every X/GPU block still running on both VMs (resumable from the cache) and free the GPUs, so FINAL
#    (16:00-20:00Z) is never delayed;
#  - 21:00Z: nothing runs after this: stop the FINAL orchestrator if it is still running, mac_sync, and any VM block or server.
R=~/AgentQO_results/v2; EV=$R/events.log
at() { python3 -c "import datetime as d; print(int(d.datetime(2026,11,19,$1,$2,tzinfo=d.timezone.utc).timestamp()))"; }
stop_vms() {  # reason
  for v in A B; do
    ssh agentqo-$v 'for s in $(tmux ls -F "#S" 2>/dev/null | grep -E "^blk_|^srv|^x3watch"); do tmux kill-session -t $s; done; pkill -f "run_real_(h3|pipeline).py|run_placement.py"; pkill -f "vllm serve"; true'
    echo "$(date -u +%FT%TZ) FINAL GUARD: $1 on VM-$v" | tee -a $R/STATUS.md >> $EV
  done
}
T1=$(at 15 30); T2=$(at 21 0)
while [ $(date +%s) -lt $T1 ]; do sleep 60; done
for f in stage3_orch stage4_orch stage5_orch; do kill $(cat $R/$f.pid) 2>/dev/null; done
stop_vms "X/GPU work stopped at 15:30Z so FINAL (16:00Z) is not delayed"
while [ $(date +%s) -lt $T2 ]; do sleep 60; done
if kill -0 "$(cat $R/final_orch.pid 2>/dev/null)" 2>/dev/null; then
  pkill -P "$(cat $R/final_orch.pid)"; kill "$(cat $R/final_orch.pid)"
  echo "$(date -u +%FT%TZ) WARN FINAL GUARD: FINAL orchestrator still running at 21:00Z, stopped (nothing runs after 21:00Z)" | tee -a $R/STATUS.md >> $EV
fi
kill "$(cat $R/mac_sync.pid)" 2>/dev/null
stop_vms "21:00Z: everything stopped (lease ends 22:38Z)"
