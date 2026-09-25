"""CSV / JSON writers for experiment artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence


def write_csv(
    path: Path,
    rows: Sequence[Mapping[str, Any]],
    fieldnames: Optional[Iterable[str]] = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    names = list(fieldnames) if fieldnames is not None else list(rows[0].keys())
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=names, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _cell(row.get(k)) for k in names})


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str))


def _cell(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (float, int, str, bool)):
        return value
    return json.dumps(value, default=str)


RESULTS_HEADER = """# AgentQO Results

## Environment
- Commit:
- Chameleon site / node type / GPU / driver / CUDA:
- vLLM version:
- Models (small / large / probe):
- SU used this phase (see ledger):

## Gate summary
| Gate | Result | Key number (95% CI) | n |
|---|---|---|---|
| CAL | | | |
| H1 | | | |
| H2 | | | |
| H3 | | | |
| H4 | | | |
| RT | | | |

## SU ledger (hard cap 1,000)
| Date | Hardware | Hours | SU | Cumulative | What ran |
|---|---|---|---|---|---|

## Per-experiment entries
"""


def append_results_entry(
    exp_id: str,
    config: Mapping[str, Any],
    result: str,
    figure: str,
    interpretation: str,
    changes: str = "",
    path: Path = Path("RESULTS.md"),
) -> None:
    """Append one Appendix-C entry to RESULTS.md (created on first use)."""
    import datetime

    path = Path(path)
    if not path.exists():
        path.write_text(RESULTS_HEADER)
    cfg = ", ".join(f"{k}={v}" for k, v in config.items())
    entry = (
        f"\n### {exp_id} {datetime.date.today().isoformat()}\n"
        f"- Config: {cfg}\n"
        f"- Result: {result}\n"
        f"- Figure: {figure}\n"
        f"- Interpretation: {interpretation}\n"
        f"- Changes made since last run and why: {changes}\n"
    )
    with path.open("a") as fh:
        fh.write(entry)
