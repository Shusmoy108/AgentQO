"""SQLite generation cache: the source of reproducibility for real runs.

Keyed by sha256 over everything that determines a sampled response (model,
messages, temperature, top_p, max_tokens, seed). vLLM does not guarantee
bit-identical sampling under batching, so a rerun reads from here.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

KEY_FIELDS = ("model", "messages", "temperature", "top_p", "max_tokens", "seed")


def cache_key(payload: Dict[str, Any]) -> str:
    material = {k: payload.get(k) for k in KEY_FIELDS}
    return hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()


class GenerationCache:
    def __init__(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._db = sqlite3.connect(str(path), check_same_thread=False)
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS gen (key TEXT PRIMARY KEY, response TEXT NOT NULL,"
            " latency_s REAL NOT NULL, created REAL NOT NULL)"
        )
        self._db.commit()
        self.hits = 0
        self.misses = 0

    def get(self, payload: Dict[str, Any]) -> Optional[Tuple[Dict[str, Any], float]]:
        with self._lock:
            row = self._db.execute(
                "SELECT response, latency_s FROM gen WHERE key = ?", (cache_key(payload),)
            ).fetchone()
            if row is None:
                self.misses += 1
                return None
            self.hits += 1
        return json.loads(row[0]), float(row[1])

    def put(self, payload: Dict[str, Any], response: Dict[str, Any], latency_s: float) -> None:
        with self._lock:
            self._db.execute(
                "INSERT OR REPLACE INTO gen VALUES (?, ?, ?, ?)",
                (cache_key(payload), json.dumps(response), float(latency_s), time.time()),
            )
            self._db.commit()
