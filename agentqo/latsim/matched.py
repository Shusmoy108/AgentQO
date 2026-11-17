"""Re-run a tagged latsim, unchanged, on the exact problems a measured run used (no refit).

    python3 -m agentqo.latsim.matched --tag latsim-frozen-20261117T133315Z \
        --params results/latsim/params.json --label frozen_matched_k1 \
        --runs 'results/v2/X1b/math_q15_7/*_k1/run_*.csv'

PI decision (relayed 2026-11-17 by the lease session): X1b's K=1 block measured 32 problems
while the frozen grid predicts over 64, so it is scored only against this re-run. The tag's
agentqo/latsim and its params file are extracted with git archive into a scratch folder and
imported from there, so the code is the tag's, not the working tree's. The problems are the
first N of the setting's h3_calls (load_setting's own rule), and the run's task_ids must be
exactly those N in that order, otherwise this stops. Output:
results/latsim/matched/<label>.csv in predictions.csv format (pred_p50, pred_p95).
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import subprocess
import sys
import tempfile
from collections import defaultdict

RUNNER = r"""
import csv, json, sys
sys.path.insert(0, sys.argv[1])
import agentqo.latsim.predict as P
assert P.__file__.startswith(sys.argv[1]), P.__file__
results, setting, n, params, out = sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5], sys.argv[6]
ks, placements, plans_wanted = json.loads(sys.argv[7]), json.loads(sys.argv[8]), json.loads(sys.argv[9])
params = json.load(open(params))
plans = P.load_setting(results, setting, n)
rows = []
for plan in plans_wanted:
    for pl in placements:
        for k in ks:
            rows.append({"setting": setting, "plan": plan, "placement": pl, "k": k, "n_problems": n,
                         **P.predict_plan(plans[plan], params, pl, k)})
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
"""


def first_tasks(results: str, setting: str, n: int):
    sys.path.insert(0, os.getcwd())
    from agentqo.latsim.predict import SETTINGS
    import gzip
    base = f"{results}/{SETTINGS[setting]}/plans/h3_calls.csv"
    f = open(base, newline="") if os.path.exists(base) else gzip.open(base + ".gz", "rt", newline="")
    seen = []
    with f:
        for r in csv.DictReader(f):
            if r["task_id"] not in seen:
                seen.append(r["task_id"])
                if len(seen) == n:
                    break
    return seen


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tag", required=True)
    ap.add_argument("--params", required=True, help="params file path inside the tag")
    ap.add_argument("--label", required=True)
    ap.add_argument("--runs", required=True, help="glob of the measured run_*.csv files")
    ap.add_argument("--results", default="results/v2")
    ap.add_argument("--out", default="results/latsim/matched")
    args = ap.parse_args()
    runs = sorted(glob.glob(args.runs))
    if not runs:
        raise SystemExit(f"no runs match {args.runs}")
    by = defaultdict(set)  # (setting, placement, k) -> plans
    tasks = {}
    for path in runs:
        setting = os.path.basename(os.path.dirname(os.path.dirname(path)))
        with open(path, newline="") as f:
            rs = sorted(csv.DictReader(f), key=lambda r: float(r["start_s"]))
        ids = [r["task_id"] for r in rs]
        if setting in tasks and set(tasks[setting]) != set(ids):
            raise SystemExit(f"{path}: a different problem set than other runs of {setting}")
        tasks[setting] = ids
        by[(setting, rs[0]["placement"], int(rs[0]["k"]))].add(rs[0]["plan"])
    os.makedirs(args.out, exist_ok=True)
    out_rows = []
    with tempfile.TemporaryDirectory() as tmp:
        arch = subprocess.run(["git", "archive", args.tag, "agentqo/__init__.py", "agentqo/latsim", args.params],
                              check=True, capture_output=True).stdout
        subprocess.run(["tar", "-x", "-C", tmp], input=arch, check=True)
        commit = subprocess.run(["git", "rev-list", "-n1", args.tag], check=True, capture_output=True, text=True).stdout.strip()
        for (setting, placement, k), plans in sorted(by.items()):
            n = len(tasks[setting])
            want = first_tasks(args.results, setting, n)
            if sorted(want) != sorted(tasks[setting]):
                raise SystemExit(f"{setting}: measured problems are not the first {n} of h3_calls; refusing")
            part = os.path.join(tmp, "part.csv")
            subprocess.run([sys.executable, "-I", "-c", RUNNER, tmp, args.results, setting, str(n),
                            os.path.join(tmp, args.params), part, f"[{k}]", f'["{placement}"]',
                            __import__("json").dumps(sorted(plans))], check=True)
            with open(part, newline="") as f:
                out_rows += [{**r, "tag": args.tag, "commit": commit} for r in csv.DictReader(f)]
    path = f"{args.out}/{args.label}.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0]))
        w.writeheader()
        w.writerows(out_rows)
    print(f"wrote {len(out_rows)} rows ({args.tag} code and params, {sorted({len(v) for v in tasks.values()})} problems) to {path}")


if __name__ == "__main__":
    main()
