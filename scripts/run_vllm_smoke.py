#!/usr/bin/env python3
"""Smoke-test a live vLLM OpenAI-compatible server.

Exits cleanly when the server is down (no traceback spam). Does not claim
H2/H4 — embeddings are placeholders.

  vllm serve meta-llama/Meta-Llama-3-8B-Instruct --port 8000
  VLLM_BASE_URL=http://localhost:8000 python scripts/run_vllm_smoke.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentqo.backends.vllm_http import VLLMConnectionError, VLLMHTTPBackend, VLLMHTTPConfig
from agentqo.workflows.dag import SMALL_FIDELITY
from agentqo.workflows.library import create_math_reasoning_workflow


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test AgentQO ↔ vLLM HTTP")
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="vLLM base URL (default: VLLM_BASE_URL or http://localhost:8000)",
    )
    parser.add_argument("--model", type=str, default=None, help="Override small model id")
    parser.add_argument(
        "--problem",
        type=str,
        default="What is 17 + 25? Reply with the number only.",
    )
    args = parser.parse_args()

    config = VLLMHTTPConfig.from_env()
    if args.base_url:
        config.base_url = args.base_url
    if args.model:
        config.small_model = args.model
        config.large_model = args.model

    backend = VLLMHTTPBackend(config)
    print(f"Checking {config.base_url} ...")
    if not backend.health_check():
        print(
            "vLLM not reachable.\n"
            "Start a server, then re-run:\n"
            "  vllm serve meta-llama/Meta-Llama-3-8B-Instruct --port 8000\n"
            f"  VLLM_BASE_URL={config.base_url} python scripts/run_vllm_smoke.py"
        )
        sys.exit(2)

    workflow = create_math_reasoning_workflow(num_steps=1, include_verifier=False)
    node = workflow.nodes["planner"]
    try:
        result = backend.execute_node(
            node=node,
            inputs={},
            fidelity=SMALL_FIDELITY,
            task_context={"problem": args.problem},
        )
    except VLLMConnectionError as exc:
        print(f"Request failed: {exc}")
        sys.exit(2)

    text = result.output.get("text", "") if isinstance(result.output, dict) else result.output
    print("OK")
    print(f"  model={result.metadata.get('model')}")
    print(f"  latency_s={result.cost:.3f}")
    print(f"  confidence={result.confidence:.3f}")
    print(f"  embedding_kind={result.metadata.get('embedding_kind')}")
    print(f"  text={text!r:.200}")
    sys.exit(0)


if __name__ == "__main__":
    main()
