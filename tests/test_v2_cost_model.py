"""M1 and M9."""

import csv
import math
import subprocess
import sys

import pytest

from agentqo.metrics.cost_model import api_usd, gpu_usd, large_small_ratio, load_prices, price_plans
from agentqo.metrics.io import mark_done, resolve_output_dir
from scripts.v2.model_env import exports, load_models

PRICES = load_prices()


def call(plan, task, tier, tin=1000, tout=100, lat=2.0):
    return {"plan": plan, "task_id": task, "fidelity": tier, "prompt_tokens": tin,
            "completion_tokens": tout, "latency_s": lat}


def test_default_prices_match_the_spec():
    assert api_usd(PRICES, "small", 1e6, 0) == pytest.approx(0.10)
    assert api_usd(PRICES, "small", 0, 1e6) == pytest.approx(0.50)
    assert api_usd(PRICES, "large", 1e6, 0) == pytest.approx(2.00)
    assert api_usd(PRICES, "large", 0, 1e6) == pytest.approx(10.00)
    assert gpu_usd(3600, 2) == 2


def test_plan_row_is_mean_per_problem():
    calls = [call("p", "a", "small"), call("p", "a", "large"), call("p", "b", "small")]
    row = price_plans(calls, PRICES)[0]
    assert row["n_problems"] == 2
    assert row["tokens_in"] == 1500
    assert row["cost_units"] == (1 + 4 + 1) / 2
    assert row["gpu_seconds"] == 3.0
    assert row["gpu_seconds_shared"] == pytest.approx((2 * .25 + 2 * .55 + 2 * .25) / 2)
    assert row["gpu_usd_4"] == pytest.approx(3.0 * 4 / 3600)
    assert row["gpu_usd"] == row["gpu_usd_2"]


def test_large_small_ratio_for_h4b():
    rows = price_plans([call("all_small", "a", "small"), call("all_large", "a", "large")], PRICES)
    assert large_small_ratio(rows) == pytest.approx(20.0)
    assert math.isnan(large_small_ratio(rows[:1]))


def test_memory_fractions_over_one_rejected(tmp_path):
    bad = tmp_path / "p.yaml"
    bad.write_text("shared_memory_fraction: {small: 0.6, large: 0.6}\n")
    with pytest.raises(ValueError):
        load_prices(bad)


def test_output_dir_resumes_same_config_and_suffixes_otherwise(tmp_path):
    base = tmp_path / "run"
    d1, done = resolve_output_dir(base, {"a": 1})
    assert d1 == base and not done
    assert resolve_output_dir(base, {"a": 1}) == (base, False)
    mark_done(d1)
    assert resolve_output_dir(base, {"a": 1}) == (base, True)
    d2, done = resolve_output_dir(base, {"a": 2})
    assert d2.name == "run_2" and not done
    assert resolve_output_dir(base, {"a": 2})[0] == d2
    assert resolve_output_dir(base, {"a": 3}, create=False)[0].name == "run_3"
    assert not (tmp_path / "run_3").exists()
    # A directory that is not ours is never written into.
    (tmp_path / "other").mkdir()
    assert resolve_output_dir(tmp_path / "other", {"a": 1})[0].name == "other_2"


def test_cost_report_cli(tmp_path):
    path = tmp_path / "calls.csv"
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(call("p", "a", "small")))
        w.writeheader()
        w.writerows([call("all_small", "a", "small"), call("all_large", "a", "large")])
    out = tmp_path / "cost"
    cmd = [sys.executable, "scripts/v2/cost_report.py", "--calls", str(path), "--output-dir", str(out)]
    subprocess.run(cmd + ["--dry-run"], check=True)
    assert not out.exists()
    subprocess.run(cmd, check=True)
    assert (out / "plan_costs.csv").exists() and (out / "DONE").exists()
    assert "already finished" in subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def test_model_configs_have_every_spec_entry():
    cfg = load_models()
    assert cfg["models"] == {
        "qwen_small": "Qwen/Qwen2.5-1.5B-Instruct", "qwen_large": "Qwen/Qwen2.5-7B-Instruct",
        "qwen3b": "Qwen/Qwen2.5-3B-Instruct", "qwen14b": "Qwen/Qwen2.5-14B-Instruct",
        "granite_small": "ibm-granite/granite-3.1-2b-instruct",
        "granite_large": "ibm-granite/granite-3.1-8b-instruct",
    }
    assert cfg["max_tokens"] == {"qwen_math": 256, "granite": 512, "hotpotqa": 384}
    env = exports("qwen3b", "qwen14b", cfg)
    assert env["VLLM_LARGE_MODEL"] == "Qwen/Qwen2.5-14B-Instruct" and "OLLAMA_LARGE_MODEL" not in env
