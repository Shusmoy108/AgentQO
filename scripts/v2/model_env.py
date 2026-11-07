#!/usr/bin/env python3
"""M9: turn config names into environment exports for the existing backends.

    eval "$(python3 scripts/v2/model_env.py qwen3b qwen14b)"
    python3 scripts/v2/model_env.py --check-servers qwen3b qwen14b
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
import urllib.request
from pathlib import Path
from typing import Dict

import yaml

CONFIG = Path(__file__).resolve().parent.parent.parent / "configs" / "v2_models.yaml"


def load_models(path: Path = CONFIG) -> Dict:
    return yaml.safe_load(Path(path).read_text())


def exports(small: str, large: str, cfg: Dict) -> Dict[str, str]:
    models, tags = cfg["models"], cfg["ollama_tags"]
    env = {"VLLM_SMALL_MODEL": models[small], "VLLM_LARGE_MODEL": models[large]}
    if small in tags:
        env["OLLAMA_SMALL_MODEL"] = tags[small]
    if large in tags:
        env["OLLAMA_LARGE_MODEL"] = tags[large]
    return env


def served_models(base_url: str) -> list:
    with urllib.request.urlopen(base_url.rstrip("/") + "/v1/models", timeout=15) as r:
        return [m["id"] for m in json.loads(r.read())["data"]]


def check_servers(small: str, large: str, cfg: Dict) -> None:
    """Fail before any generation if an endpoint serves the wrong model."""
    endpoints = json.loads(os.environ.get("VLLM_ENDPOINTS", "{}"))
    default = os.environ.get("VLLM_BASE_URL", "http://localhost:8000")
    for tier, name in (("small", small), ("large", large)):
        url, want = endpoints.get(tier, default), cfg["models"][name]
        have = served_models(url)
        if want not in have:
            raise SystemExit(f"{tier} endpoint {url} serves {have}, expected {want}")
        print(f"{tier}: {url} serves {want}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("small")
    ap.add_argument("large")
    ap.add_argument("--check-servers", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the resolved ids without exports")
    args = ap.parse_args()
    cfg = load_models()
    if args.check_servers:
        check_servers(args.small, args.large, cfg)
        return
    for k, v in exports(args.small, args.large, cfg).items():
        print(f"{k}={shlex.quote(v)}" if args.dry_run else f"export {k}={shlex.quote(v)}")


if __name__ == "__main__":
    sys.exit(main())
