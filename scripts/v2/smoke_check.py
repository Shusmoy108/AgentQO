#!/usr/bin/env python3
"""P0: judge a 5-problem vLLM smoke run of one setting, and record skips.

    python3 scripts/v2/smoke_check.py check SETTING H3_DIR --skips results/v2/P0/skips.tsv
    python3 scripts/v2/smoke_check.py skip SETTING "reason" --skips results/v2/P0/skips.tsv

check reads H3_DIR/h3_traces.json (plans all_small and all_large). The setting fails if it
scores 0 (no correct answer in either plan) or gives a yes/no answer to a question whose gold
is not yes/no. A failed or manually skipped setting is appended to the skips file (read by
run_phase.sh), to FAILURES.md and, as a lease-time deviation, to prereg/v2_amendments.md.
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
    rows = [t for plan in ("all_small", "all_large") for t in traces.get(plan, [])]
    if not rows:
        return ["no all_small/all_large traces"]
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


def record_skip(setting: str, reason: str, skips: Path, root: Path = Path(".")) -> None:
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    skips.parent.mkdir(parents=True, exist_ok=True)
    with skips.open("a") as fh:
        fh.write(f"{setting}\t{reason}\t{now}\n")
    with (root / "FAILURES.md").open("a") as fh:
        fh.write(f"- {now}: setting `{setting}` skipped for the rest of the lease: {reason}\n")
    with (root / "prereg/v2_amendments.md").open("a") as fh:
        fh.write(f"\nLease-time deviation D-P0-{setting} ({now}): setting `{setting}` is skipped; {reason}. "
                 f"No hypothesis is tested on it.\n")
    print(f"SKIP {setting}: {reason}")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["check", "skip"])
    ap.add_argument("setting")
    ap.add_argument("arg", help="check: the h3 output dir; skip: the reason")
    ap.add_argument("--skips", type=Path, default=Path("results/v2/P0/skips.tsv"))
    args = ap.parse_args(argv)
    if args.cmd == "skip":
        record_skip(args.setting, args.arg, args.skips)
        return 0
    path = Path(args.arg) / "h3_traces.json"
    reasons = problems(json.loads(path.read_text())) if path.exists() else [f"no {path} (run failed)"]
    if reasons:
        record_skip(args.setting, "P0 smoke test: " + "; ".join(reasons), args.skips)
    else:
        print(f"PASS {args.setting}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
