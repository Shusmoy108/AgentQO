"""Publication-style figures for H1–H4. Matplotlib is optional at import."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np


def _pyplot():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "figure.dpi": 140,
        "savefig.bbox": "tight",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.grid": True,
        "grid.alpha": 0.3,
    })
    return plt


def save_h1_histogram(
    labels: Mapping[str, Any],
    output_path: Path,
    title: Optional[str] = None,
) -> Path:
    """Horizontal bar chart of consequence with bootstrap CI whiskers."""
    plt = _pyplot()
    items = []
    for node_id, label in labels.items():
        if hasattr(label, "consequence_mean"):
            mean = float(label.consequence_mean)
            lo = float(label.consequence_ci_low)
            hi = float(label.consequence_ci_high)
        else:
            mean = float(label["consequence_mean"])
            lo = float(label.get("consequence_ci_low", mean))
            hi = float(label.get("consequence_ci_high", mean))
        items.append((node_id, mean, lo, hi))
    items.sort(key=lambda x: x[1])

    fig, ax = plt.subplots(figsize=(7.2, max(2.8, 0.38 * len(items) + 1.2)))
    ys = np.arange(len(items))
    means = np.array([it[1] for it in items])
    xerr = np.vstack([
        means - np.array([it[2] for it in items]),
        np.array([it[3] for it in items]) - means,
    ])
    xerr = np.clip(xerr, 0, None)
    ax.barh(ys, means, xerr=xerr, color="#3b6ea5", alpha=0.85, capsize=3)
    ax.set_yticks(ys)
    ax.set_yticklabels([it[0] for it in items])
    ax.set_xlabel("Consequence  E[Q | correct] − E[Q | incorrect]")
    ax.set_title(title or "H1: epistemic criticality varies across nodes")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def save_h2_ranking_figure(
    metrics_by_model: Mapping[str, Mapping[str, float]],
    output_path: Path,
) -> Path:
    plt = _pyplot()
    names = list(metrics_by_model.keys())
    spearman = [metrics_by_model[n].get("spearman_corr", 0.0) for n in names]
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    colors = ["#2a9d8f" if n in {"GBT", "MLP", "AgentQO"} else "#8a8a8a" for n in names]
    ax.bar(names, spearman, color=colors)
    ax.set_ylabel("Spearman correlation with true EC")
    ax.set_title("H2: EC ranking quality")
    ax.set_ylim(-0.05, 1.05)
    for i, v in enumerate(spearman):
        ax.text(i, v + 0.02, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def save_h3_quality_cost_figure(
    curves: Mapping[str, Sequence[Tuple[float, float]]],
    output_path: Path,
) -> Path:
    plt = _pyplot()
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    style = {
        "AgentQO": ("#2a9d8f", "o"),
        "Oracle-EC": ("#1d3557", "D"),
        "Confidence": ("#e76f51", "s"),
        "Uniform": ("#9b9b9b", "^"),
        "All-Small": ("#bdbdbd", "x"),
    }
    for name, points in curves.items():
        if not points:
            continue
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        color, marker = style.get(name, (None, "o"))
        ax.plot(xs, ys, marker=marker, label=name, color=color, linewidth=2)
    ax.set_xlabel("GPU cost")
    ax.set_ylabel("Task quality")
    ax.set_title("H3: value-aware allocation")
    ax.legend(frameon=False)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def save_h4_interaction_figure(
    contention: Sequence[float],
    reuse: Sequence[float],
    output_path: Path,
) -> Path:
    plt = _pyplot()
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.hist(contention, bins=20, alpha=0.6, label="contention (same GPU)", color="#e76f51")
    ax.hist(reuse, bins=20, alpha=0.6, label="prefix reuse (negative delay)", color="#2a9d8f")
    ax.set_xlabel("Imposed extra latency")
    ax.set_ylabel("Count")
    ax.set_title("H4: two-sided interaction has both signs")
    ax.legend(frameon=False)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path
