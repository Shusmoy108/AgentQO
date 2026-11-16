#!/usr/bin/env python3
"""P0: judge a 5-problem vLLM smoke run of one setting, and record skips.

    python3 scripts/v2/smoke_check.py check SETTING H3_DIR --skips results/v2/P0/skips.tsv
    python3 scripts/v2/smoke_check.py skip SETTING "reason" --skips results/v2/P0/skips.tsv
    python3 scripts/v2/smoke_check.py reduce SETTING "N reason"   # A17: eval on the first N problems
    python3 scripts/v2/smoke_check.py moved SETTING "VM-A"        # another VM runs it; not a deviation

check reads H3_DIR/h3_traces.json (plans all_small and all_large, plus all_xl for A16). The
setting fails if it scores 0 (no correct answer in any plan) or gives a yes/no answer to a question whose gold
is not yes/no. A failed or manually skipped setting is appended to the skips file (read by
run_phase.sh), to FAILURES.md and, as a lease-time deviation, to prereg/v2_amendments.md. A
reduction goes to reduced.tsv next to the skips file and is logged the same way. A move only
goes to the skips file, so this VM does not start a setting the other VM has taken.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agentqo.tasks.answers import normalize_answer  # noqa: E402

YES_NO = {"yes", "no"}


def problems(traces: dict) -> List[str]:
    """Reasons the smoke run fails; empty if it passes."""
    rows = [t for ts in traces.values() for t in ts]
    if not rows:
        return ["no traces"]
    out = []
    if not any(t["correct"] for t in rows):
        out.append(f"scores 0 ({len(rows)} answers, none correct)")
    wrong = [t for t in rows if normalize_answer(str(t["gold"])) not in YES_NO
             and normalize_answer(str(t.get("pred") or "")) in YES_NO]
    if wrong:
        out.append(f"{len(wrong)} yes/no answers to non-yes/no questions ({wrong[0]['task_id']})")
    return out


def skipped(skips: Path) -> set:
    return {line.split("\t")[0] for line in skips.read_text().splitlines() if line} if skips.exists() else set()


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _append(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(line)


def record_skip(setting: str, reason: str, skips: Path, root: Path = Path(".")) -> None:
    now = _now()
    _append(skips, f"{setting}\t{reason}\t{now}\n")
    _append(root / "FAILURES.md", f"- {now}: setting `{setting}` skipped for the rest of the lease: {reason}\n")
    _append(root / "prereg/v2_amendments.md", f"\nLease-time deviation D-P0-{setting} ({now}): setting `{setting}` "
                                              f"is skipped; {reason}. No hypothesis is tested on it.\n")
    print(f"SKIP {setting}: {reason}")


def record_reduction(setting: str, n: int, reason: str, skips: Path, root: Path = Path(".")) -> None:
    now = _now()
    _append(skips.with_name("reduced.tsv"), f"{setting}\t{n}\t{reason}\t{now}\n")
    _append(root / "FAILURES.md", f"- {now}: setting `{setting}` evaluated on the first {n} eval problems: {reason}\n")
    _append(root / "prereg/v2_amendments.md", f"\nLease-time deviation D-P0-{setting}-n{n} ({now}): setting "
                                              f"`{setting}` plans are evaluated on the first {n} eval problems "
                                              f"(labels unchanged); {reason}.\n")
    print(f"REDUCE {setting} to {n}: {reason}")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["check", "skip", "reduce", "moved"])
    ap.add_argument("setting")
    ap.add_argument("arg", help="check: the h3 output dir; skip: the reason; reduce: 'N reason'; moved: the VM")
    ap.add_argument("--skips", type=Path, default=Path("results/v2/P0/skips.tsv"))
    ap.add_argument("--root", type=Path, default=Path("."), help="where FAILURES.md and prereg/ are (the repo)")
    args = ap.parse_args(argv)
    if args.cmd == "skip":
        record_skip(args.setting, args.arg, args.skips, args.root)
        return 0
    if args.cmd == "reduce":
        n, reason = args.arg.split(" ", 1)
        record_reduction(args.setting, int(n), reason, args.skips, args.root)
        return 0
    if args.cmd == "moved":
        _append(args.skips, f"{args.setting}\tmoved to {args.arg}\t{_now()}\n")
        print(f"MOVED {args.setting} to {args.arg}")
        return 0
    path = Path(args.arg) / "h3_traces.json"
    reasons = problems(json.loads(path.read_text())) if path.exists() else [f"no {path} (run failed)"]
    if reasons:
        record_skip(args.setting, "P0 smoke test: " + "; ".join(reasons), args.skips, args.root)
    else:
        print(f"PASS {args.setting}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
