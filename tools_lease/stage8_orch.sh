#!/usr/bin/env bash
# Lease 2 stage 8 (Mac): optional L2-X12 on VM-A only (registered 5cc73094): after X11 completes (stage 7 done), and only if
# X12 can start before 2026-11-19 08:00Z; no block starts after 2026-11-19 14:00Z. Never touches VM-B.
R=~/AgentQO_results/v2; EV=$R/events.log; ST=$R/STATUS.md
ts() { date -u +%FT%TZ; }
before() { python3 -c "import datetime as d,sys; sys.exit(not d.datetime.now(d.timezone.utc) < d.datetime(2026,11,19,$1,tzinfo=d.timezone.utc))"; }
run() {  # block
  before 14 || { echo "$(ts) X12 CUT: $1 not started, past 2026-11-19 14:00Z" | tee -a $ST >> $EV; return 1; }
  until ssh agentqo-A 'test ! -f /mnt/data/TIMING_LOCK'; do sleep 60; done
  ssh agentqo-A "tmux kill-session -t blk_$1 2>/dev/null; tmux new -d -s blk_$1 'VM=A bash /mnt/data/x12.sh $1'" && echo "$(ts) ORCH start $1 on VM-A" >> $EV
  local s
  while true; do
    sleep 60
    s=$(ssh -o ConnectTimeout=20 agentqo-A "if [ -f /mnt/data/blk/$1.done ]; then echo done; elif [ -f /mnt/data/blk/$1.fail ]; then echo fail; elif tmux has-session -t blk_$1 2>/dev/null; then echo run; else echo gone; fi" 2>/dev/null)
    case $s in done) echo "$(ts) ORCH done $1 on VM-A" >> $EV; return 0 ;; fail|gone) echo "$(ts) WARN ORCH block $1 on VM-A: $s" >> $EV; return 1 ;; esac
  done
}
until grep -q 'ORCH STAGE7 DONE' $EV; do sleep 120; done
before 8 || { echo "$(ts) X12 SKIPPED: X11 finished after 2026-11-19 08:00Z (optional item)" | tee -a $ST >> $EV; exit 0; }
echo "$(ts) X12 START on VM-A (X11 complete)" | tee -a $ST >> $EV
run x12prep || { echo "$(ts) X12 STOPPED at prep" | tee -a $ST >> $EV; exit 0; }
for s in math_q15_7 math_granite; do run x12-$s; done
run x12pack
echo "$(ts) ORCH STAGE8 DONE (X12)" >> $EV
