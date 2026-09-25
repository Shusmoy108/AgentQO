"""WP5: generation cache makes labeling reproducible; threads make it fast."""

import time

from agentqo.backends.cache import GenerationCache, cache_key
from agentqo.labeling.ec_labeler import ECLabeler
from agentqo.workflows.library import create_math_reasoning_workflow
from tests._real_fixtures import fake_backend


def test_cache_key_covers_seed_and_temperature():
    base = {"model": "m", "messages": [{"role": "user", "content": "x"}], "temperature": 0.0,
            "top_p": 1.0, "max_tokens": 8, "seed": 1}
    assert cache_key(base) == cache_key(dict(base, logprobs=True))
    assert cache_key(base) != cache_key(dict(base, seed=2))
    assert cache_key(base) != cache_key(dict(base, temperature=0.7))


def _labels(backend, tm, workers=8):
    wf = create_math_reasoning_workflow(2, include_verifier=True)
    res = ECLabeler(backend, tm, mode="substitute", max_workers=workers).label_workflow(
        wf, num_tasks=6, show_progress=False)
    return {n: (l.consequence_mean, l.local_error_prob) for n, l in res.labels.items()}, res


def test_rerun_with_cache_is_identical_and_makes_no_http_calls(tmp_path):
    cache = GenerationCache(tmp_path / "gen.sqlite")
    backend, server, tm = fake_backend(cache=cache)
    first, _ = _labels(backend, tm)
    assert server.n_requests > 0
    # Fresh backend + server, same cache file: every request must be a hit.
    backend2, server2, tm2 = fake_backend(cache=GenerationCache(tmp_path / "gen.sqlite"))
    second, _ = _labels(backend2, tm2)
    assert second == first
    assert server2.n_requests == 0


def test_seed_is_in_every_request():
    backend, server, tm = fake_backend()
    payloads = []
    inner = backend._request_fn
    backend._request_fn = lambda url, payload, h, t: payloads.append(payload) or inner(url, payload, h, t)
    _labels(backend, tm)
    assert payloads and all(isinstance(p.get("seed"), int) for p in payloads)


def test_thread_pool_speedup():
    wf = create_math_reasoning_workflow(1, include_verifier=False)

    def timed(workers):
        backend, server, tm = fake_backend(sleep_s=0.01)
        t0 = time.perf_counter()
        ECLabeler(backend, tm, mode="substitute", k_samples=2, n_corruptions=1,
                  max_workers=workers).label_workflow(wf, num_tasks=32, show_progress=False)
        return time.perf_counter() - t0

    assert timed(1) / timed(32) >= 15
