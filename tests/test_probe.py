"""WP6: probe embeddings are deterministic and have the model's hidden size."""

import numpy as np
import pytest

from agentqo.backends.composite import CompositeBackend
from agentqo.backends.probe import PlaceholderProbe
from agentqo.workflows.dag import SMALL_FIDELITY
from agentqo.workflows.library import create_math_reasoning_workflow
from tests._real_fixtures import fake_backend

TINY = "trl-internal-testing/tiny-Qwen2ForCausalLM-2.5"


def test_composite_sets_embedding_and_kind():
    text, _, tm = fake_backend()
    backend = CompositeBackend(text, PlaceholderProbe(32))
    wf = create_math_reasoning_workflow(1, include_verifier=False)
    task = tm.generate_task(wf, None)
    ctx = {"task": task, "workflow": wf, "results": {}}
    a = backend.execute_node(wf.nodes["planner"], {}, SMALL_FIDELITY, ctx)
    b = backend.execute_node(wf.nodes["planner"], {}, SMALL_FIDELITY, ctx)
    assert a.embedding.shape == (32,) and backend.embedding_dim == 32
    assert np.array_equal(a.embedding, b.embedding)
    assert a.metadata["embedding_kind"] == "placeholder"
    assert backend.n_calls == 2  # counters delegate to the text backend


def test_hf_probe_deterministic_and_hidden_size():
    pytest.importorskip("transformers")
    from agentqo.backends.probe import HFHiddenStateProbe

    try:
        probe = HFHiddenStateProbe(TINY, device="cpu")
    except OSError:
        pytest.skip("tiny model not cached and offline")
    a = probe.encode("Problem: 2+2", "#### 4")
    probe._memo.clear()
    b = probe.encode("Problem: 2+2", "#### 4")
    c = probe.encode("Problem: 2+2", "#### 5")
    assert a.shape == (probe.model.config.hidden_size,) == (probe.dim,)
    assert np.allclose(a, b)
    assert not np.allclose(a, c)
    last = HFHiddenStateProbe(TINY, pool="last", layer=0, device="cpu")
    assert last.encode("x", "y").shape == (probe.dim,)
