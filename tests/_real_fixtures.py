"""Shared fake-server setup for real-pipeline tests (no network, no GPU)."""

from agentqo.backends.fake_server import FakeServer
from agentqo.backends.vllm_http import VLLMHTTPBackend, VLLMHTTPConfig
from agentqo.tasks.prompts import build_prompt, code_output
from agentqo.tasks.real_task_model import RealTaskModel

PROBLEMS = [
    {"qid": f"q{i}", "question": f"Sam has {i + 3} apples and buys {2 * i + 1} more. How many now?",
     "gold": str(3 * i + 4)}
    for i in range(12)
]


def fake_backend(small_err=0.3, large_err=0.05, cache=None, sleep_s=0.0, logprobs=True, **cfg):
    config = VLLMHTTPConfig(temperature=0.0, **cfg)
    server = FakeServer(PROBLEMS, {config.small_model: small_err, config.large_model: large_err},
                        sleep_s=sleep_s, logprobs=logprobs)
    backend = VLLMHTTPBackend(config, request_fn=server, prompt_fn=build_prompt,
                              code_fn=code_output, cache=cache)
    return backend, server, RealTaskModel(PROBLEMS)
