"""Evaluate every prediction version on every test set present and write the tables of REPORT.md.

    python3 -m agentqo.latsim.report            # writes results/latsim/report_tables.md

Versions: frozen (results/latsim/predictions.csv) and each results/latsim/rev*/predictions.csv.
Test sets: X1 (results/v2/X1*/<setting>/<placement>/placement_summary.csv) and X1b
(results/v2/X1b*/...); a test set with no files is listed as not yet available.
"""

from __future__ import annotations

import csv
import glob
import os
import subprocess
import sys

TESTS = {"X1": "results/v2/X1/*/*/placement_summary.csv,results/v2/X1_vm*/*/*/placement_summary.csv",
         "X1b": "results/v2/X1b*/*/*/placement_summary.csv"}
EXCLUDE_K = {"X1b": "1"}  # X1b K=1 ran 32 problems: scored only against the matched re-runs (matched.py)
COLS = [("w10", "within 10%"), ("w20", "within 20%"), ("mape50", "MAPE p50"), ("mape95", "MAPE p95"),
        ("bias95", "median p95 error"), ("tau", "Kendall tau")]


def versions(out: str):
    yield "frozen", f"{out}/predictions.csv", out
    for d in sorted(glob.glob(f"{out}/rev*/")):
        yield os.path.basename(d.rstrip("/")), f"{d}predictions.csv", d.rstrip("/")


def read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def fmt(v):
    try:
        return f"{float(v):.3f}" if v not in ("", None) else "-"
    except ValueError:
        return str(v)


def table(rows, keys, predictors=("latsim", "h3c", "mean_sum")):
    head = keys + ["n"] + [f"{p} {label}" for p in predictors for _, label in COLS[:1] + COLS[1:2] + COLS[3:4] + COLS[5:]]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        cells = [str(r.get(k, "")) for k in keys] + [r["n_plans"]]
        for p in predictors:
            cells += [fmt(r.get(f"{p}_{c}")) for c, _ in COLS[:2] + COLS[3:4] + COLS[5:]]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main(out: str = "results/latsim") -> None:
    md = []
    for test, pattern in TESTS.items():
        files = [f for p in pattern.split(",") for f in glob.glob(p)]
        if not files:
            md.append(f"## {test}\n\nNo measured files yet ({pattern}).\n")
            continue
        for name, pred, dest in versions(out):
            if not os.path.exists(pred):
                continue
            subprocess.run([sys.executable, "-m", "agentqo.latsim.evaluate", "--name", test,
                            "--measured", pattern, "--predictions", pred, "--out", dest,
                            "--exclude-k", EXCLUDE_K.get(test, "")], check=True, stdout=subprocess.DEVNULL)
            md.append(f"## {test}, {name} predictions ({os.path.relpath(pred, out)})\n")
            md.append("Pooled:\n\n" + table(read(f"{dest}/{test}_pooled.csv"), ["placement", "k", "all"]) + "\n")
            md.append("By setting:\n\n" + table(read(f"{dest}/{test}_by_setting.csv"), ["setting", "placement", "k"]) + "\n")
            md.append("By plan type (latsim only):\n\n" + table(read(f"{dest}/{test}_by_plan_type.csv"),
                                                              ["placement", "k", "plan_type"], ("latsim",)) + "\n")
        cov = read(f"{out}/{test}_coverage.csv")
        md.append(f"### {test} coverage\n\n| summary | placement | K | plans measured | plans listed | min repeats |\n|---|---|---|---|---|---|\n"
                  + "\n".join(f"| {c['summary']} | {c['placement']} | {c['k']} | {c['plans_measured']} | "
                              f"{c['plans_listed']} | {c['min_repeats']} |" for c in cov) + "\n")
    with open(f"{out}/report_tables.md", "w") as f:
        f.write("\n".join(md))
    print(f"wrote {out}/report_tables.md")


if __name__ == "__main__":
    main()
