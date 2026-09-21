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
