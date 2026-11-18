#!/usr/bin/env bash
# Lease 2 X10r (L2-X10r, registered 1ffa6772 before any data; not repo code). usage: VM=B bash /mnt/data/x10r.sh <block>
# Blocks: x10r-math_granite, x10r-math_phi, x10rpack. X10 at P4/P4b's max-model-len 8192, fresh cache x10r_vmB.sqlite.
source /mnt/data/lq.sh
export AGENTQO_VERIFIER=cautious V2_TIERS=small,large
G2=ibm-granite/granite-3.1-2b-instruct G8=ibm-granite/granite-3.1-8b-instruct P35=microsoft/Phi-3.5-mini-instruct P4=microsoft/phi-4
PY=/mnt/data/venv/bin/python MAIN=/mnt/data/AgentQO XCL=/mnt/data/AgentQO-x RES=/mnt/data/AgentQO/results/v2
XC=18b3d7a0414a1079fb68ba0f14526e2d0e0417ba C=/mnt/data/AgentQO/data/cache/x10r_vmB.sqlite
blk=${1:?block}; mkdir -p /mnt/data/blk; rm -f /mnt/data/blk/$blk.done /mnt/data/blk/$blk.fail
exec > >(tee -a $MAIN/logs/v2/blk_$blk.log) 2>&1
die() { qlog "block $blk FAILED: $*"; touch /mnt/data/blk/$blk.fail; exit 1; }
cd $XCL; export V2_DEVIATION=D-L2-X-code; L=$MAIN/logs/v2; G=$RES/GATES
[ -f /mnt/data/TIMING_LOCK ] && die "TIMING_LOCK held"
[ "$(git rev-parse HEAD)" = $XC ] || die "x clone not at $XC"
ev() { echo "$(date -u +%FT%TZ) $*" >> /mnt/data/x3_events.log; }
case $blk in
  x10r-*)
    s=${blk#x10r-}; $PY scripts/v2/summarize_phase.py provenance $RES/X10r --refuse-dirty --lease || die "provenance"
    case $s in math_granite) sm=$G2 lg=$G8 ref=$MAIN/results/v2/P4/math_granite/plans ;;
               math_phi)     sm=$P35 lg=$P4 ref=$MAIN/results/v2/P4b/math_phi/plans ;; *) die "setting $s" ;; esac
    d=$RES/X10r/$s; mkdir -p $d
    if [ -d $d/plans ] && [ ! -f $d/plans/DONE ]; then mv $d/plans $d/superseded_$(date -u +%Y%m%dT%H%MZ)_plans; ev "X10r restart: partial $d/plans moved aside"; fi
    t0=$(date -u +%FT%TZ)
    srv_start "$lg|8002|0.55|8192" "$sm|8001|0.25|8192" || die "servers"
    # confirm max-model-len 8192 before the first model call: server log lines written at this start, and the live servers
    for m in "$lg" "$sm"; do
      awk -v t="[$t0]" '$1 >= t' $L/queue_B.log | grep -q "server $m :80[0-9]* up (mem [0-9.]*, len 8192)" || die "server log does not show len 8192 for $m"
    done
    for p in 8001 8002; do
      ml=$(curl -s -m 10 localhost:$p/v1/models | $PY -c 'import sys,json; print(json.load(sys.stdin)["data"][0].get("max_model_len"))')
      [ "$ml" = 8192 ] || die "live server :$p max_model_len=$ml, not 8192"
    done
    ev "X10r $s: max-model-len 8192 confirmed (server log + /v1/models) on :8001 and :8002 before the first call"
    export VLLM_SMALL_MODEL=$sm VLLM_LARGE_MODEL=$lg
    for i in 0 120 300; do
      [ $i -gt 0 ] && { qlog "retry $blk after ${i}s"; sleep $i; srv_ensure; }
      qlog "start X10r $s (eval_ext 400, all 64 plans, max-model-len 8192, fresh cache x10r_vmB.sqlite)"
      AGENTQO_SEED_SALT=1 $PY scripts/run_real_h3.py --backend vllm --cache $C --workflow math --dataset gsm8k --split eval_ext --n-tasks 400 \
        --max-tokens 512 --workers $V2_WORKERS --plans all_subsets --output-dir $d/plans && break
      [ $i = 300 ] && die "X10r $s"
    done
    srv_stop
    $PY /mnt/data/x10compare.py $ref $d/plans $d > $d/x10r_vs_ref.txt 2>&1 || die "compare vs ref"
    for f in x10_vs_ref_summary.json x10_vs_ref_per_plan.csv; do mv $d/$f $d/${f/x10_vs_ref/x10r_vs_ref}; done
    $PY /mnt/data/x10compare.py $RES/X10/$s/plans $d/plans $d > $d/x10r_vs_x10.txt 2>&1 || die "compare vs X10"
    for f in x10_vs_ref_summary.json x10_vs_ref_per_plan.csv; do mv $d/$f $d/${f/x10_vs_ref/x10r_vs_x10_4096}; done
    ev "X10r $s vs ref: $(cat $d/x10r_vs_ref.txt | cut -c1-300)"; ev "X10r $s vs X10 (4096): $(cat $d/x10r_vs_x10.txt | cut -c1-300)"
    gate X10r-$s ;;
  x10rpack) srv_stop; cp $L/blk_$blk.log $RES/X10r/run_$blk.log.txt; (cd $MAIN && scripts/v2/package_phase.sh X10r) || die "package X10r"; gate X10r-pack ;;
  *) die "unknown block" ;;
esac
touch /mnt/data/blk/$blk.done; qlog "block $blk done"
