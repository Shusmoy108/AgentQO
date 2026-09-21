"""Multi-GPU cluster state: running sets R_g, KV regions, HBM.

This is the physical side of AgentQO. AgentIconq scores admission against
the current running set, not against an isolated call.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from agentqo.simulator.interaction_model import CallSpec, simulate_batch


@dataclass
class KVRegion:
    region_id: str
    owner_node: str
    workflow_id: str
    gpu_id: int
    size: float
    reuse_prob: float
    recompute_cost: float
    last_use: float


@dataclass
class RunningCall:
    call_id: str
    workflow_id: str
    node_id: str
    spec: CallSpec
    remaining: float
    kv_size: float
    result: Optional[Any] = None


@dataclass
class GPU:
    gpu_id: int
    gpu_type: str = "sim"
    hbm_cap: float = 16.0
    running: List[RunningCall] = field(default_factory=list)
    kv: Dict[str, KVRegion] = field(default_factory=dict)

    @property
    def hbm_used(self) -> float:
        live = sum(c.kv_size for c in self.running)
        cached = sum(r.size for r in self.kv.values())
        return live + cached


class Cluster:
    """A small multi-GPU fabric with two-sided admission."""

    def __init__(self, n_gpus: int = 2, hbm_cap: float = 16.0) -> None:
        if n_gpus < 1:
            raise ValueError("n_gpus must be >= 1")
        self.gpus = [
            GPU(gpu_id=i, hbm_cap=hbm_cap) for i in range(n_gpus)
        ]
        self.now = 0.0
        self._call_seq = 0

    def next_call_id(self) -> str:
        self._call_seq += 1
        return f"call_{self._call_seq}"

    def running_specs(self, gpu_id: int) -> List[CallSpec]:
        return [c.spec for c in self.gpus[gpu_id].running]

    def physical_cost(
        self,
        spec: CallSpec,
        lambda_move: float = 0.2,
        lambda_reuse: float = 0.4,
        move_cost: float = 0.0,
        reuse_bonus: float = 0.0,
    ) -> Tuple[float, float, float]:
        """Proposal eq. (1)–(3): own latency, total externality, C_phys."""
        gpu = self.gpus[spec.gpu_id]
        batch = self.running_specs(spec.gpu_id) + [spec]
        outcomes = {o.call_id: o for o in simulate_batch(batch)}
        own = outcomes[spec.call_id].own_latency
        # Externality: change in others' remaining time if we admit spec.
        without = {o.call_id: o for o in simulate_batch(self.running_specs(spec.gpu_id))}
        externality = 0.0
        for running in gpu.running:
            before = without[running.call_id].own_latency
            after = outcomes[running.call_id].own_latency
            externality += after - before
        c_phys = own + externality + lambda_move * move_cost - lambda_reuse * reuse_bonus
        return own, externality, c_phys

    def admit(self, call: RunningCall) -> None:
        gpu = self.gpus[call.spec.gpu_id]
        own, externality, _ = self.physical_cost(call.spec)
        if gpu.running:
            share = externality / len(gpu.running)
            for running in gpu.running:
                running.remaining += max(share, 0.0)
        call.remaining = own
        gpu.running.append(call)

    def evict_kv(self, gpu_id: int, region_id: str) -> Optional[KVRegion]:
        return self.gpus[gpu_id].kv.pop(region_id, None)

    def store_kv(self, region: KVRegion) -> None:
        self.gpus[region.gpu_id].kv[region.region_id] = region

    def next_completion(self) -> Optional[Tuple[float, RunningCall]]:
        best: Optional[Tuple[float, RunningCall]] = None
        for gpu in self.gpus:
            for call in gpu.running:
                t = self.now + call.remaining
                if best is None or t < best[0]:
                    best = (t, call)
        return best

    def complete(self, call: RunningCall) -> None:
        gpu = self.gpus[call.spec.gpu_id]
        elapsed = call.remaining
        self.now += elapsed
        for g in self.gpus:
            for other in g.running:
                if other.call_id == call.call_id:
                    continue
                other.remaining = max(0.0, other.remaining - elapsed)
        gpu.running = [c for c in gpu.running if c.call_id != call.call_id]

    def idle_gpu(self) -> Optional[int]:
        for gpu in self.gpus:
            if not gpu.running:
                return gpu.gpu_id
        return None

    def least_loaded_gpu(self) -> int:
        return min(self.gpus, key=lambda g: (len(g.running), g.hbm_used)).gpu_id
