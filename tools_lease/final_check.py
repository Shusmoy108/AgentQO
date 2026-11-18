#!/usr/bin/env python3
"""FINAL data completeness check (PI FINAL spec, 2026-11-16) from the Mac mirror; no model calls.
usage: final_check.py [out.md]   (default: print). Exit 0 always; MISSING rows are listed in the report."""
import csv, glob, os, sys
csv.field_size_limit(1 << 30)
M = os.environ.get("FINALCHECK_ROOT") or os.path.expanduser("~/AgentQO_results/v2")   # FINAL-early: the archive copy
A, B = f"{M}/vm-A/results/v2", f"{M}/vm-B/results/v2"
AGENTS = {"math": ["planner", "step_1", "step_2", "step_3", "aggregator", "verifier"],
          "code": ["planner", "coder", "tester", "fixer", "verifier"]}
# setting, status, plans dir, expected plans, expected eval problems, labels dir (or note), cost file (or None)
S = [
 ("math_q15_7", "registered", f"{A}/P2/math_q15_7/plans", 64, 400, f"{A}/P1/math_q15_7/labels", f"{A}/P6/math_q15_7/cost/plan_costs.csv"),
 ("hotpot_q15_7", "registered", f"{A}/P2/hotpot_q15_7/plans", 32, 400, f"{A}/P1/hotpot_q15_7/labels", f"{A}/P6/hotpot_q15_7/cost/plan_costs.csv"),
 ("hotpot_iso_q15_7", "registered", f"{A}/P2/hotpot_iso_q15_7/plans", 32, 400, f"{A}/P1/hotpot_iso_q15_7/labels", f"{A}/P6/hotpot_iso_q15_7/cost/plan_costs.csv"),
 ("math_q3_14", "registered", f"{B}/P3/math_q3_14/plans", 64, 400, f"{B}/P3/math_q3_14/labels", f"{A}/P6/math_q3_14/cost/plan_costs.csv"),
 ("math_granite", "registered", f"{B}/P4/math_granite/plans", 64, 400, f"{B}/P4/math_granite/labels", f"{A}/P6/math_granite/cost/plan_costs.csv"),
 ("hotpot_granite", "registered", f"{B}/P4/hotpot_granite/plans", 32, 400, f"{B}/P4/hotpot_granite/labels", f"{A}/P6/hotpot_granite/cost/plan_costs.csv"),
 ("hotpot_iso_granite", "registered", f"{B}/P4/hotpot_iso_granite/plans", 32, 400, f"{B}/P4/hotpot_iso_granite/labels", f"{A}/P6/hotpot_iso_granite/cost/plan_costs.csv"),
 ("math_phi", "registered", f"{B}/P4b/math_phi/plans", 64, 400, f"{B}/P4b/math_phi/labels", f"{A}/P6/math_phi/cost/plan_costs.csv"),
 ("hotpot_phi", "registered", f"{B}/P4b/hotpot_phi/plans", 32, 400, f"{B}/P4b/hotpot_phi/labels", f"{A}/P6/hotpot_phi/cost/plan_costs.csv"),
 ("complex_q15_7", "registered", f"{A}/P2c/complex_q15_7/plans", 1024, 200, f"{A}/P2c/complex_q15_7/labels", f"{A}/P6/complex_q15_7/cost/plan_costs.csv"),
 ("math_tiers", "registered", f"{A}/P2b/math_tiers/plans", 729, 200, f"{A}/P2b/math_tiers/labels", f"{A}/P6/math_tiers/tiers/tier_pareto.csv"),
 ("X2 math_q15_7", "X2", f"{A}/X2/math_q15_7/plans", 64, 719, "P1 (reused)", None),
 ("X2 hotpot_q15_7", "X2", f"{A}/X2/hotpot_q15_7/plans", 32, 600, "P1 (reused)", None),
 ("X2 hotpot_iso_q15_7", "X2", f"{A}/X2/hotpot_iso_q15_7/plans", 32, 600, "P1 (reused)", None),
 ("X2 math_granite", "X2", f"{B}/X2/math_granite/plans", 64, 719, "P4 (reused)", None),
 ("X2 math_phi", "X2", f"{B}/X2/math_phi/plans", 64, 719, "P4b (reused)", None),
 ("X3 math_xfamily", "X3", f"{B}/X3/plans_2", 729, 200, f"{B}/X3/labels_q7_G8_2", None),
 ("X4 math_q15_7", "X4", f"{A}/X4/math_q15_7/plans", 64, 400, "P1 (reused)", None),
 ("X4 hotpot_q15_7", "X4", f"{A}/X4/hotpot_q15_7/plans", 32, 400, "P1 (reused)", None),
 ("X5 math500_q15_7", "X5", f"{A}/X5/math500_q15_7/plans", 64, 300, f"{A}/X5/math500_q15_7/labels", None),
 ("X6 math_q7_32", "X6", f"{A}/X6/math_q7_32/plans", 64, 400, f"{A}/X6/math_q7_32/labels", None),
 ("X6 hotpot_q7_32", "X6", f"{A}/X6/hotpot_q7_32/plans", 32, 400, f"{A}/X6/hotpot_q7_32/labels", None),
 ("X6 math500_q7_32", "X6", f"{A}/X6/math500_q7_32/plans", 64, 300, f"{A}/X6/math500_q7_32/labels", None),
 ("X7 code_c15_7", "X7", f"{B}/X7/code_c15_7/plans", 32, 178, f"{B}/X7/code_c15_7/labels", None),
 ("X8 complex_q15_7", "X8", f"{A}/X8/complex_q15_7/plans", 1024, 200, "P2c (reused)", None),
 # registered 2026-11-18; required only if they finished (plans/DONE on the VM), otherwise listed as not finished
 ("X9 math_tiers", "X9", f"{B}/X9/math_tiers/plans", 729, 200, "P2b (reused)", None),
 ("X10 math_granite", "X10", f"{B}/X10/math_granite/plans", 64, 400, "P4 (reused)", None),
 ("X10 math_phi", "X10", f"{B}/X10/math_phi/plans", 64, 400, "P4b (reused)", None),
 ("X11 math500_q15_7", "X11", f"{A}/X11/math500_q15_7/plans", 64, 200, "X5 (reused)", None),
 ("X11 code_c15_7", "X11", f"{A}/X11/code_c15_7/plans", 32, 200, "X7 (reused)", None),
 ("X10r math_granite", "X10r", f"{B}/X10r/math_granite/plans", 64, 400, "P4 (reused)", None),
 ("X10r math_phi", "X10r", f"{B}/X10r/math_phi/plans", 64, 400, "P4b (reused)", None),
 ("X12 math_q15_7 eval", "X12", f"{A}/X12/math_q15_7/eval", 1, 400, "n/a (all_small only)", None),
 ("X12 math_q15_7 x2", "X12", f"{A}/X12/math_q15_7/x2", 1, 719, "n/a (all_small only)", None),
 ("X12 math_granite eval", "X12", f"{A}/X12/math_granite/eval", 1, 400, "n/a (all_small only)", None),
 ("X12 math_granite x2", "X12", f"{A}/X12/math_granite/x2", 1, 719, "n/a (all_small only)", None),
]
LATE = {"X9", "X10", "X10r", "X11", "X12"}
def rows(p):
    with open(p, newline="") as fh: return list(csv.DictReader(fh))
def check_setting(name, d, n_plans, n_prob, lab, cost):
    bad = []
    try: plans = [r["plan"] for r in rows(f"{d}/h3_plans.csv")]
    except OSError: return ["h3_plans.csv missing"], False
    if len(set(plans)) != n_plans: bad.append(f"h3_plans.csv has {len(set(plans))} plans, expected {n_plans}")
    complete = False
    try:
        pp = rows(f"{d}/h3_per_problem.csv"); pairs = {(r["plan"], r["task_id"]) for r in pp}
        tasks = {t for _, t in pairs}; need = len(set(plans)) * len(tasks)
        if len(tasks) != n_prob: bad.append(f"per-problem covers {len(tasks)} problems, expected {n_prob}")
        if len(pairs) != need or len(pp) != need: bad.append(f"per-problem {len(pairs)} unique pairs / {len(pp)} rows, expected {need}")
        complete = len(tasks) == n_prob and len(pairs) == n_plans * n_prob
    except OSError: bad.append("h3_per_problem.csv missing")
    cp = f"{d}/h3_calls.csv"
    if not os.path.exists(cp) and os.path.exists(cp + ".gz"): cp += ".gz"
    if not os.path.exists(cp): bad.append("h3_calls.csv missing")
    elif cp.endswith(".csv"):
        with open(cp, newline="") as fh:
            rd = csv.DictReader(fh); cols = rd.fieldnames or []
            miss = [c for c in ("prompt_tokens", "completion_tokens", "latency_s") if c not in cols]
            if miss: bad.append(f"h3_calls.csv lacks {miss}")
            else:
                empty = sum(1 for r in rd if not all(r[c] not in ("", None) for c in ("prompt_tokens", "completion_tokens", "latency_s")))
                if empty: bad.append(f"h3_calls.csv: {empty} calls with an empty token/latency field")
    if d.split("/results/v2/")[-1].startswith("X12/") and os.path.exists(cp) and cp.endswith(".csv"):
        with open(cp, newline="") as fh:
            cols = csv.DictReader(fh).fieldnames or []
        if not {"mean_logprob", "answer_logprob", "answer_text"} <= set(cols): bad.append("X12 h3_calls.csv lacks the logprob columns")
    if lab.startswith("/"):
        try:
            got = {r["agent"] for r in rows(f"{lab}/labels_v2.csv")}
            fam = "code" if "code" in name else "math"
            if fam == "code" or "math" in name:
                want = set(AGENTS[fam]); m = want - got
                if m: bad.append(f"labels_v2.csv lacks agents {sorted(m)}")
            if not os.path.exists(f"{lab}/labels_v2_per_problem.csv"): bad.append("labels_v2_per_problem.csv missing")
        except OSError: bad.append(f"labels missing ({os.path.relpath(lab, M)})")
    if cost:
        try:
            cp = {r["plan"] for r in rows(cost)}; m = set(plans) - cp
            if m: bad.append(f"{os.path.basename(cost)} lacks {len(m)} plans")
        except OSError: bad.append(f"{os.path.relpath(cost, M)} missing")
        sd = os.path.dirname(os.path.dirname(cost))
        if name != "math_tiers" and not glob.glob(f"{sd}/pareto*/*"): bad.append("P6 pareto outputs missing")
    return bad, complete
def main():
    out = ["# FINAL data completeness check", "",
           "Generated by tools/final_check.py from the Mac mirror of both VMs (no model calls). Expected counts are the",
           "registered/amended sizes. A setting with incomplete per-problem data is not usable for search.", "",
           "| setting | status | plans x problems | result | per-problem complete |", "|---|---|---|---|---|"]
    missing = []
    for name, st, d, n, k, lab, cost in S:
        if st in LATE and not os.path.exists(f"{d}/DONE"):
            out.append(f"| {name} | {st} | {n} x {k} | not finished (not required; see STATUS.md) | NO |"); continue
        bad, ok = check_setting(name, d, n, k, lab, cost)
        out.append(f"| {name} | {st} | {n} x {k} | {'OK' if not bad else 'MISSING: ' + '; '.join(bad)} | {'yes' if ok else 'NO'} |")
        missing += [f"{name}: {b}" for b in bad]
    out += ["", "## Other required outputs", ""]
    def need(label, ok, why=""):
        out.append(f"- {label}: {'OK' if ok else 'MISSING ' + why}")
        if not ok: missing.append(f"{label}: {why}")
    for vm, base, g in (("VM-A", A, "a"), ("VM-B", B, "b")):
        p5 = [x for x in glob.glob(f"{base}/P5/*/") if "superseded" not in x and "h4grid" not in x]
        nopl = [os.path.basename(x.rstrip("/")) for x in p5 if not glob.glob(f"{x}/placement_*.csv") and not glob.glob(f"{x}/*requests*.csv") and not glob.glob(f"{x}/calls_*.csv")]
        nopw = [os.path.basename(x.rstrip("/")) for x in p5 if not glob.glob(f"{x}/power_gpu_*.csv")]
        need(f"P5 placement CSVs {vm} ({len(p5)} runs)", p5 and not nopl, f"no placement CSV in {nopl}")
        need(f"P5 power logs {vm}", p5 and not nopw, f"no power log in {nopw}")
    need("h4_fit outputs (P5/h4grid)", bool(glob.glob(f"{A}/P5/h4grid/**/*fit*", recursive=True)), "no fit files")
    for e in ("fp16", "awq"):
        need(f"E1 {e} outputs", bool(glob.glob(f"{A}/E1/{e}/*/labels_v2.csv")), "no labels_v2.csv")
    need("P6 hypotheses.md", os.path.exists(f"{A}/P6/hypotheses/hypotheses.md"), "")
    env = open(f"{A}/P0/env.txt").read() if os.path.exists(f"{A}/P0/env.txt") else ""
    need("env.txt (P0, both VMs)", "## VM-A" in env and "## VM-B" in env, "P0/env.txt lacks a VM section")
    for base in (A, B):
        for ph in sorted(glob.glob(f"{base}/*/")):
            n = os.path.basename(ph.rstrip("/"))
            files = [f for _, _, fs in os.walk(ph) for f in fs if not f.startswith(".")]
            if n == "GATES" or not files or files == ["README.md"]: continue   # empty mirror dirs; a README-only note
            need(f"provenance {os.path.relpath(ph, M).rstrip('/')}", os.path.exists(f"{ph}/provenance.jsonl"), "provenance.jsonl missing")
    for x in ("X1", "X1b", "X1c"):
        for vm, base in (("VM-A", A), ("VM-B", B)):
            if not os.path.isdir(f"{base}/{x}"): continue
            calls = [c for c in glob.glob(f"{base}/{x}/**/*.csv", recursive=True) if "superseded" not in c and ("calls_" in c or "requests" in c)]
            ok_ts = calls and all({"request_start_s", "request_end_s"} <= set(next(csv.reader(open(c)))) or "placement_" in c for c in calls[:50])
            need(f"{x} latency calls {vm} ({len(calls)} files)", bool(calls) and ok_ts, "no call CSVs or no per-request start/end")
    out += ["", f"## Summary: {len(missing)} MISSING item(s)", ""] + [f"- {m}" for m in missing]
    txt = "\n".join(out) + "\n"
    if len(sys.argv) > 1: open(sys.argv[1], "w").write(txt)
    print(txt)
main()
