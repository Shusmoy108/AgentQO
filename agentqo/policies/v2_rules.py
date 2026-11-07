"""M4: allocation rules and plan-accuracy estimators.

A plan is a frozenset of upgraded agents. Each rule returns {k: plan} for
budgets k = 1..n. Labels are the rows of labels_v2.csv, keyed by agent.
"""

from __future__ import annotations

from itertools import combinations
from typing import Callable, Dict, FrozenSet, Iterable, List, Mapping, Sequence

Plan = FrozenSet[str]
Labels = Mapping[str, Mapping[str, float]]


def plan_name(upgraded: Iterable[str], topo: Sequence[str]) -> str:
    """all_small, all_large, only_<node>, or nodes joined by + in topological order."""
    chosen = [n for n in topo if n in set(upgraded)]
    if not chosen:
        return "all_small"
    if len(chosen) == len(topo):
        return "all_large"
    return f"only_{chosen[0]}" if len(chosen) == 1 else "+".join(chosen)


def parse_plan_name(name: str, topo: Sequence[str]) -> Plan:
    if name == "all_small":
        return frozenset()
    if name == "all_large":
        return frozenset(topo)
    nodes = {name[5:]} if name.startswith("only_") else set(name.split("+"))
    if not nodes <= set(topo):
        raise ValueError(f"plan {name} names nodes outside the workflow: {sorted(nodes - set(topo))}")
    return frozenset(nodes)


def structural_order(workflow) -> List[str]:
    """Largest downstream reach first; same definition as struct_top* in run_real_h3.py."""
    topo = list(workflow.topological_order)
    return sorted(topo, key=lambda n: (-workflow.get_downstream_reach(n), topo.index(n)))


def output_order(workflow) -> List[str]:
    """Closest to the answer first; same definition as output_top* in run_real_h2.py."""
    topo = list(workflow.topological_order)
    dist = {topo[-1]: 0}
    for n in reversed(topo[:-1]):
        dist[n] = 1 + max(dist[x] for x in topo if n in workflow.nodes[x].inputs and x in dist)
    return sorted(topo, key=lambda n: (dist[n], -topo.index(n)))


def _by(labels: Labels, column: str, topo: Sequence[str]) -> List[str]:
    return sorted(topo, key=lambda n: (-float(labels[n][column]), topo.index(n)))


def confident_uv_order(labels: Labels, workflow) -> List[str]:
    """Agents whose UV CI lower bound clears 0, by UV; the rest in structural order."""
    topo = list(workflow.topological_order)
    sure = [n for n in _by(labels, "uv", topo) if float(labels[n]["uv_ci_low"]) > 0]
    return sure + [n for n in structural_order(workflow) if n not in sure]


def rule_orders(labels: Labels, workflow) -> Dict[str, List[str]]:
    topo = list(workflow.topological_order)
    return {
        "structural_topk": structural_order(workflow),
        "output_topk": output_order(workflow),
        "ec_topk": _by(labels, "ec_synthetic", topo),
        "ec_real_topk": _by(labels, "ec_real", topo),
        "uv_topk": _by(labels, "uv", topo),
        "confident_uv": confident_uv_order(labels, workflow),
    }


def all_rules(labels: Labels, workflow) -> Dict[str, Dict[int, Plan]]:
    n = len(workflow.nodes)
    rules = {name: {k: frozenset(order[:k]) for k in range(1, n + 1)}
             for name, order in rule_orders(labels, workflow).items()}
    rules["all_small"] = {k: frozenset() for k in range(1, n + 1)}
    rules["all_large"] = {k: frozenset(workflow.nodes) for k in range(1, n + 1)}
    return rules


# ------------------------------------------------------------- estimators
Estimator = Callable[[Plan], float]


def _clip(x: float) -> float:
    return min(1.0, max(0.0, x))


def independence_additive(measured: Mapping[Plan, float]) -> Estimator:
    base = measured[frozenset()]
    return lambda plan: _clip(base + sum(measured[frozenset({v})] - base for v in plan))


def independence_multiplicative(measured: Mapping[Plan, float]) -> Estimator:
    base = measured[frozenset()]

    def estimate(plan: Plan) -> float:
        if base == 0:  # ratios undefined; a zero baseline has only additive information
            return independence_additive(measured)(plan)
        out = base
        for v in plan:
            out *= measured[frozenset({v})] / base
        return _clip(out)
    return estimate


def top_singles(measured: Mapping[Plan, float], agents: Iterable[str], m: int) -> List[str]:
    """The m agents with the largest single-upgrade gain; picked without any pair data."""
    return sorted(agents, key=lambda v: -measured[frozenset({v})])[:m]


def pairs_to_measure(measured: Mapping[Plan, float], agents: Iterable[str], m: int = 3) -> List[Plan]:
    return [frozenset(p) for p in combinations(top_singles(measured, agents, m), 2)]


def pairwise_corrected(measured: Mapping[Plan, float], agents: Iterable[str], m: int = 3) -> Estimator:
    """Additive estimate plus the measured interaction of each top-m pair in the plan."""
    base = measured[frozenset()]
    single = {v: measured[frozenset({v})] - base for v in agents}
    delta = {pair: measured[pair] - base - sum(single[v] for v in pair)
             for pair in pairs_to_measure(measured, agents, m)}

    def estimate(plan: Plan) -> float:
        return _clip(base + sum(single[v] for v in plan) + sum(d for p, d in delta.items() if p <= plan))
    return estimate
