#!/usr/bin/env python3
"""M10 helpers for package_phase.sh: SUMMARY.md, summary.json, MANIFEST.txt, the zip.

    python3 scripts/v2/summarize_phase.py report results/v2/P1
    python3 scripts/v2/summarize_phase.py zip results/v2/P1 --name P1
    python3 scripts/v2/summarize_phase.py copy results/v2/P1 /path/to/worktree/results/v2/P1
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

# file name -> (sort column, descending, rows shown); None = file order
KEY_TABLES = {
    "labels_v2.csv": (None, False, 20),
    "labels_v2_by_strategy.csv": (None, False, 40),
    "h3_plans.csv": ("accuracy", True, 8),
    "plan_costs.csv": ("api_usd", False, 5),
    "rule_plans.csv": (None, False, 16),
    "estimator_errors.csv": (None, False, 6),
    "pareto_front.csv": ("accuracy", True, 10),
    "constrained_best.csv": (None, False, 3),
    "budget_best.csv": (None, False, 6),
    "latency_check.csv": (None, False, 30),
    "routing.csv": ("accuracy", True, 8),
    "placement_summary.csv": (None, False, 30),
}
GIT_KEEP = (".csv", ".json", ".md", ".txt")
SKIP_IN_ZIP = (".sqlite", ".sqlite-journal", ".sqlite-wal", ".sqlite-shm")


def _fmt(value: str) -> str:
    try:
        x = float(value)
    except ValueError:
        return value.replace("|", "\\|")
    return f"{x:.3f}".rstrip("0").rstrip(".") if abs(x) >= 1e-3 or x == 0 else f"{x:.2e}"


def table(path: Path) -> str:
    sort_col, desc, limit = KEY_TABLES[path.name]
    with path.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return "(no rows)\n"
    if sort_col:
        rows.sort(key=lambda r: float(r[sort_col] or 0), reverse=desc)
    cols = list(rows[0])
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(_fmt(r[c] or "") for c in cols) + " |" for r in rows[:limit]]
    if len(rows) > limit:
        out.append(f"\n{limit} of {len(rows)} rows shown.")
    return "\n".join(out) + "\n"


def git_commit() -> str:
    res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    return res.stdout.strip() or "unknown"


def report(root: Path) -> Dict:
    """Write SUMMARY.md and summary.json. A step is a directory holding run_config.v2.json."""
    steps = sorted(p.parent for p in root.rglob("run_config.v2.json"))
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary: Dict = {"phase": root.name, "generated": now, "git_commit": git_commit(),
                     "backend": os.environ.get("V2_BACKEND", "vllm"), "steps": []}
    md = [f"# Phase {root.name}", "",
          f"Generated {now} at commit `{summary['git_commit']}`, backend `{summary['backend']}`.", ""]
    if summary["backend"] != "vllm":
        md += [f"**Test run on `{summary['backend']}`: not a reported result.**", ""]
    md += ["| step | status |", "|---|---|"]
    for step in steps:
        rel, done = str(step.relative_to(root)), (step / "DONE").exists()
        md.append(f"| {rel} | {'finished' if done else 'UNFINISHED'} |")
        info: Dict = {"step": rel, "finished": done, "config": json.loads((step / "run_config.v2.json").read_text())}
        for name in sorted(step.glob("*_summary.json")) + sorted(step.glob("h1c.json")):
            info[name.stem] = json.loads(name.read_text())
        summary["steps"].append({k: v for k, v in info.items() if k != "h3_summary" and k != "pipeline_summary"})
    if not steps:
        md.append("| (none) | no steps ran |")
    md.append("")
    for step in steps:
        tables = [step / n for n in KEY_TABLES if (step / n).exists()]
        if not tables:
            continue
        md += [f"## {step.relative_to(root)}", ""]
        for path in tables:
            md += [f"### {path.name}", "", table(path)]
        for name in ("cost_summary", "rules_summary", "pareto_summary", "adaptive_summary"):
            if (step / f"{name}.json").exists():
                md += [f"### {name}", "", "```json", (step / f"{name}.json").read_text().strip(), "```", ""]
    (root / "SUMMARY.md").write_text("\n".join(md))
    (root / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    return summary


def manifest(root: Path) -> None:
    lines = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.name != "MANIFEST.txt"):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(root)}")
    (root / "MANIFEST.txt").write_text("\n".join(lines) + "\n")


def free_zip_name(name: str, where: Path) -> Path:
    path, i = where / f"results_v2_{name}.zip", 1
    while path.exists():
        i += 1
        path = where / f"results_v2_{name}_{i}.zip"
    return path


def make_zip(root: Path, name: str, where: Path, extra: Optional[List[Path]] = None) -> Path:
    """Zip a phase, without caches. ``extra`` (the final zip's cache) goes in as given."""
    target = free_zip_name(name, where)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix not in SKIP_IN_ZIP):
            zf.write(path, Path("results/v2") / root.name / path.relative_to(root))
        for path in extra or []:
            zf.write(path, Path("cache") / path.name)
    return target


def copy_for_git(root: Path, dest: Path) -> int:
    n = 0
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in GIT_KEEP:
            target = dest / path.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["report", "zip", "copy"])
    ap.add_argument("root", type=Path)
    ap.add_argument("dest", nargs="?", type=Path)
    ap.add_argument("--name", default="")
    ap.add_argument("--where", type=Path, default=Path("."))
    ap.add_argument("--extra", nargs="*", type=Path, default=[], help="files to add as is (the cache, in the final zip)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.dry_run:
        print(f"would {args.command} {args.root}")
        return
    if args.command == "report":
        report(args.root)
        manifest(args.root)
        print(f"wrote {args.root}/SUMMARY.md, summary.json, MANIFEST.txt")
    elif args.command == "zip":
        print(make_zip(args.root, args.name or args.root.name, args.where, args.extra))
    else:
        print(f"copied {copy_for_git(args.root, args.dest)} files")


if __name__ == "__main__":
    main()
