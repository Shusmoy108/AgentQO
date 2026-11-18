#!/usr/bin/env bash
# Lease 2 stage 6 (Mac): L2-X9 and L2-X10 on VM-B (registered 2104fad2), one block at a time:
# prep -> X9 -> X9 pack -> X10 math_granite -> X10 math_phi -> X10 pack. No block starts after 2026-11-19 14:00Z
# (PI schedule; final_guard stops anything still running at 15:30Z).
R=~/AgentQO_results/v2; EV=$R/events.log; ST=$R/STATUS.md
ts() { date -u +%FT%TZ; }
left() { python3 -c 'import datetime as d; e=d.datetime(2026,11,19,14,tzinfo=d.timezone.utc); print(round((e-d.datetime.now(d.timezone.utc)).total_seconds()/3600,1))'; }
run() {  # block
  python3 -c "import sys; sys.exit(not $(left) > 0)" || { echo "$(ts) X9/X10 CUT: $1 not started, past 2026-11-19 14:00Z" | tee -a $ST >> $EV; return 1; }
  ssh agentqo-B "tmux kill-session -t blk_$1 2>/dev/null; tmux new -d -s blk_$1 'VM=B bash /mnt/data/x9x10.sh $1'" && echo "$(ts) ORCH start $1 on VM-B" >> $EV
  local s
  while true; do
    sleep 60
    s=$(ssh -o ConnectTimeout=20 agentqo-B "if [ -f /mnt/data/blk/$1.done ]; then echo done; elif [ -f /mnt/data/blk/$1.fail ]; then echo fail; elif tmux has-session -t blk_$1 2>/dev/null; then echo run; else echo gone; fi" 2>/dev/null)
    case $s in done) echo "$(ts) ORCH done $1 on VM-B" >> $EV; return 0 ;; fail|gone) echo "$(ts) WARN ORCH block $1 on VM-B: $s" >> $EV; return 1 ;; esac
  done
}
run x910prep || { echo "$(ts) X9/X10 STOPPED at prep" | tee -a $ST >> $EV; exit 0; }
run x9 && echo "$(ts) TIME LEFT after X9: $(left) h to 2026-11-19 14:00Z" >> $ST
run x9pack
for s in math_granite math_phi; do run x10-$s && echo "$(ts) TIME LEFT after X10 $s: $(left) h to 2026-11-19 14:00Z" >> $ST; done
run x10pack
echo "$(ts) ORCH STAGE6 DONE (X9, X10)" >> $EV
