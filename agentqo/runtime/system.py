"""
AgentQO runtime (proposal §V).

A serving optimizer, not an offline budget allocator. At each event it
co-selects a logical edit e and a physical plan P using epistemic
criticality and two-sided GPU cost, then applies value-aware KV
residency and speculative stopping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from zlib import crc32
from typing import Dict, List, Optional, Set

import numpy as np

from agentqo.backends.base import NodeResult
from agentqo.executor import WorkflowExecutor, _skippable
from agentqo.runtime.cluster import Cluster, KVRegion, RunningCall
from agentqo.runtime.edits import Edit, apply_edit
from agentqo.runtime.optimizer import Decision, JointOptimizer, OptimizerConfig
from agentqo.runtime.scores import branch_index, kv_value, speculative_delta_q
from agentqo.simulator.interaction_model import CallSpec
from agentqo.simulator.task_model import TaskInstance, TaskModel
from agentqo.workflows.dag import Fidelity, NodeRole, Workflow, SMALL_FIDELITY


@dataclass
class Arrival:
    workflow: Workflow
    task: TaskInstance
    seed: int
    time: float = 0.0
    ec_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class WorkflowRuntime:
    workflow_id: str
    workflow: Workflow
    task: TaskInstance
    seed: int
    arrival_time: float
    ec: Dict[str, float]
    completed: Dict[str, NodeResult] = field(default_factory=dict)
    skipped: Set[str] = field(default_factory=set)
    cancelled: Set[str] = field(default_factory=set)
    active: Dict[str, str] = field(default_factory=dict)
    fidelities: Dict[str, Fidelity] = field(default_factory=dict)
    edits: List[str] = field(default_factory=list)
    finish_time: Optional[float] = None
    gpu_time: float = 0.0
    wasted_speculative: float = 0.0
    decisions: List[Decision] = field(default_factory=list)


@dataclass
class ServeReport:
    records: List[WorkflowRuntime]
    makespan: float
    mean_quality: float
    mean_completion: float
    gpu_hours: float
    quality_per_gpu_hour: float
    edits_used: Dict[str, int]
    policy: str
    qualities: List[float] = field(default_factory=list)
    completions: List[float] = field(default_factory=list)


class AgentQO:
    """Joint logical/physical optimizer from the proposal.

    ``enable_edits=False`` is the Stage-3 fixed-plan ablation: criticality
    still affects fidelity and placement, but the graph does not change.
    """

    def __init__(
        self,
        backend,
        task_model: TaskModel,
        n_gpus: int = 2,
        enable_edits: bool = True,
        enable_kv: bool = True,
        enable_stopping: bool = True,
        config: Optional[OptimizerConfig] = None,
        kappa: float = 1.0,
        stop_threshold: float = 0.02,
        name: str = "AgentQO",
    ) -> None:
        self.backend = backend
        self.task_model = task_model
        self.executor = WorkflowExecutor(backend, task_model)
        self.cluster = Cluster(n_gpus=n_gpus)
        self.optimizer = JointOptimizer(self.cluster, config)
        self.enable_edits = enable_edits
        self.enable_kv = enable_kv
        self.enable_stopping = enable_stopping
        self.kappa = kappa
        self.stop_threshold = stop_threshold
        self.name = name
        self._instances: Dict[str, WorkflowRuntime] = {}
        self._call_owner: Dict[str, str] = {}

    def serve(self, arrivals: List[Arrival]) -> ServeReport:
        self.cluster.now = 0.0
        pending = sorted(arrivals, key=lambda a: a.time)
        seq = 0
        events = 0
        while pending or any(i.finish_time is None for i in self._instances.values()):
            events += 1
            if events > 20_000:
                for inst in self._instances.values():
                    if inst.finish_time is None:
                        inst.finish_time = self.cluster.now
                break
            unfinished = [i for i in self._instances.values() if i.finish_time is None]
            if pending and (
                not self._has_running()
                or pending[0].time <= self.cluster.now
            ):
                arrival = pending.pop(0)
                if arrival.time > self.cluster.now:
                    self.cluster.now = arrival.time
                seq += 1
                inst = self._admit_workflow(f"w{seq}", arrival)
                self._schedule_instance(inst)
                continue
            nxt = self.cluster.next_completion()
            if nxt is None:
                for inst in unfinished:
                    if not inst.active and inst.finish_time is None:
                        inst.finish_time = self.cluster.now
                if pending:
                    self.cluster.now = pending[0].time
                    continue
                break
            _, call = nxt
            self._on_complete(call)
        records = list(self._instances.values())
        self._instances = {}
        qualities = [
            self.task_model.compute_quality(r.task, r.completed, r.workflow)
            for r in records
        ]
        completions = [
            (r.finish_time or self.cluster.now) - r.arrival_time for r in records
        ]
        gpu_hours = sum(r.gpu_time for r in records) / 3600.0
        edits: Dict[str, int] = {}
        for rec in records:
            for name in rec.edits:
                edits[name] = edits.get(name, 0) + 1
        mean_q = float(np.mean(qualities)) if qualities else 0.0
        return ServeReport(
            records=records,
            makespan=self.cluster.now,
            mean_quality=mean_q,
            mean_completion=float(np.mean(completions)) if completions else 0.0,
            gpu_hours=gpu_hours,
            # Total quality delivered per (simulated) GPU-hour: the sim analogue
            # of correct answers per GPU-hour.
            quality_per_gpu_hour=float(sum(qualities)) / max(gpu_hours, 1e-9),
            edits_used=edits,
            policy=self.name,
            qualities=[float(q) for q in qualities],
            completions=[float(c) for c in completions],
        )

    def _has_running(self) -> bool:
        return any(g.running for g in self.cluster.gpus)

    def _admit_workflow(self, workflow_id: str, arrival: Arrival) -> WorkflowRuntime:
        inst = WorkflowRuntime(
            workflow_id=workflow_id,
            workflow=arrival.workflow,
            task=arrival.task,
            seed=arrival.seed,
            arrival_time=arrival.time,
            ec=dict(arrival.ec_scores),
            fidelities={
                nid: node.fidelities[0]
                for nid, node in arrival.workflow.nodes.items()
            },
        )
        self._instances[workflow_id] = inst
        return inst

    def _ready(self, inst: WorkflowRuntime) -> List[str]:
        ready = []
        done = set(inst.completed) | inst.skipped | inst.cancelled
        for node_id in inst.workflow.topological_order:
            if node_id in done or node_id in inst.active:
                continue
            node = inst.workflow.nodes[node_id]
            ok = True
            for inp in node.inputs:
                if inp in inst.completed:
                    continue
                if inp in inst.skipped or inp in inst.cancelled:
                    if _skippable(inst.workflow.nodes[inp]):
                        continue
                ok = False
                break
            if ok:
                ready.append(node_id)
        return ready

    def _schedule_instance(self, inst: WorkflowRuntime) -> None:
        if inst.finish_time is not None:
            return
        ready = self._ready(inst)
        if not ready and not inst.active:
            inst.finish_time = self.cluster.now
            return
        if not ready:
            if self.enable_stopping:
                self._maybe_stop_branches(inst)
            return

        decision = self.optimizer.decide(
            workflow=inst.workflow,
            skipped=inst.skipped,
            cancelled=inst.cancelled,
            completed=set(inst.completed),
            active=set(inst.active),
            fidelities=inst.fidelities,
            ec=inst.ec,
            ready_nodes=ready,
            prefix_id=inst.workflow_id,
        )
        if not self.enable_edits:
            decision.edit = Edit(kind="noop")
            if decision.gpu_id is None:
                decision.gpu_id = self.cluster.least_loaded_gpu()
        apply_edit(
            decision.edit, inst.skipped, inst.cancelled, inst.fidelities, inst.workflow
        )
        if decision.edit.kind != "noop":
            inst.edits.append(decision.edit.describe())
        inst.decisions.append(decision)

        if self.enable_kv:
            self._maybe_evict(decision.gpu_id if decision.gpu_id is not None else self.cluster.least_loaded_gpu())

        ready = [n for n in self._ready(inst) if n not in inst.skipped]
        if not ready:
            if not inst.active:
                inst.finish_time = self.cluster.now
            return
        cap = max(1, len(self.cluster.gpus) * 4)
        dispatched = 0
        while ready and dispatched < cap:
            node_id = self._pick_ready(inst, ready)
            gpu_id = self._best_gpu(inst, node_id)
            self._dispatch(inst, node_id, gpu_id)
            dispatched += 1
            ready = [n for n in self._ready(inst) if n not in inst.skipped]

    def _best_gpu(self, inst: WorkflowRuntime, node_id: str) -> int:
        fid = inst.fidelities.get(node_id, SMALL_FIDELITY)
        best_id = self.cluster.least_loaded_gpu()
        best_cost = float("inf")
        for gpu in self.cluster.gpus:
            spec = CallSpec(
                call_id="probe",
                model_id=fid.model_id,
                gpu_id=gpu.gpu_id,
                prompt_tokens=128,
                decode_tokens=64,
                prefix_id=inst.workflow_id,
            )
            _, _, c_phys = self.cluster.physical_cost(spec)
            # High-EC nodes prefer quieter GPUs (lower externality in C_phys).
            cost = c_phys - 0.5 * inst.ec.get(node_id, 0.0) * (1.0 / (1 + len(gpu.running)))
            if cost < best_cost:
                best_cost = cost
                best_id = gpu.gpu_id
        return best_id

    def _pick_ready(self, inst: WorkflowRuntime, ready: List[str]) -> str:
        return max(ready, key=lambda n: inst.ec.get(n, 0.0))

    def _dispatch(self, inst: WorkflowRuntime, node_id: str, gpu_id: int) -> None:
        node = inst.workflow.nodes[node_id]
        fid = inst.fidelities.get(node_id, SMALL_FIDELITY)
        rng = np.random.default_rng(inst.seed + (crc32(node_id.encode()) & 0x7FFFFFFF) % 10_000)
        inputs = {inp: inst.completed[inp] for inp in node.inputs if inp in inst.completed}
        result = self.backend.execute_node(
            node=node,
            inputs=inputs,
            fidelity=fid,
            task_context={"task": inst.task, "workflow": inst.workflow, "results": inst.completed},
            rng=rng,
        )
        prompt = 80 + 40 * inst.workflow.get_depth(node_id)
        decode = 24 if node.role == NodeRole.FORMATTER else 64
        spec = CallSpec(
            call_id=self.cluster.next_call_id(),
            model_id=fid.model_id,
            gpu_id=gpu_id,
            prompt_tokens=prompt,
            decode_tokens=decode,
            prefix_id=inst.workflow_id,
        )
        kv_size = 1.0 + decode / 128.0
        call = RunningCall(
            call_id=spec.call_id,
            workflow_id=inst.workflow_id,
            node_id=node_id,
            spec=spec,
            remaining=0.0,
            kv_size=kv_size,
            result=result,
        )
        self.cluster.admit(call)
        inst.active[node_id] = spec.call_id
        self._call_owner[spec.call_id] = inst.workflow_id
        inst.gpu_time += call.remaining

    def _on_complete(self, call: RunningCall) -> None:
        self.cluster.complete(call)
        inst = self._instances[call.workflow_id]
        node_id = call.node_id
        inst.active.pop(node_id, None)
        self._call_owner.pop(call.call_id, None)
        result = call.result
        if result is None:
            self._schedule_instance(inst)
            return
        inst.completed[node_id] = result
        if self.enable_kv:
            region = KVRegion(
                region_id=f"{inst.workflow_id}:{node_id}",
                owner_node=node_id,
                workflow_id=inst.workflow_id,
                gpu_id=call.spec.gpu_id,
                size=call.kv_size,
                reuse_prob=0.4 + 0.1 * inst.workflow.get_fan_out(node_id),
                recompute_cost=max(call.remaining, 1.0),
                last_use=self.cluster.now,
            )
            self.cluster.store_kv(region)
        if self.enable_stopping:
            self._maybe_stop_branches(inst)
        self._schedule_instance(inst)
        for other in self._instances.values():
            if other.workflow_id != inst.workflow_id and other.finish_time is None:
                self._schedule_instance(other)

    def _maybe_stop_branches(self, inst: WorkflowRuntime) -> None:
        groups = inst.workflow.get_speculative_groups()
        for node_ids in groups.values():
            done_ok = sum(
                1 for nid in node_ids
                if nid in inst.completed and inst.completed[nid].correctness
            )
            running = [nid for nid in node_ids if nid in inst.active]
            if not running:
                continue
            delta_q = speculative_delta_q(done_ok, len(running))
            remain = 32.0
            index = branch_index(delta_q, remain)
            if index < self.stop_threshold:
                for nid in running:
                    if not inst.workflow.nodes[nid].optional:
                        continue
                    call_id = inst.active[nid]
                    gpu = next(
                        g for g in self.cluster.gpus
                        if any(c.call_id == call_id for c in g.running)
                    )
                    call = next(c for c in gpu.running if c.call_id == call_id)
                    inst.wasted_speculative += call.remaining
                    gpu.running = [c for c in gpu.running if c.call_id != call_id]
                    inst.active.pop(nid, None)
                    inst.cancelled.add(nid)
                    inst.skipped.add(nid)
                    inst.edits.append(f"stop({nid})")

    def _maybe_evict(self, gpu_id: int) -> None:
        gpu = self.cluster.gpus[gpu_id]
        while gpu.hbm_used > gpu.hbm_cap and gpu.kv:
            def score(region: KVRegion) -> float:
                inst = self._instances.get(region.workflow_id)
                ec = inst.ec.get(region.owner_node, 0.0) if inst else 0.0
                return kv_value(region.reuse_prob, region.recompute_cost, ec, self.kappa)
            victim = min(gpu.kv.values(), key=score)
            gpu.kv.pop(victim.region_id, None)


class FCFSFixed(AgentQO):
    """Baseline: no edits, all-small fidelity, least-loaded GPU."""

    def __init__(self, backend, task_model, n_gpus: int = 2) -> None:
        super().__init__(
            backend, task_model, n_gpus=n_gpus,
            enable_edits=False, enable_kv=False, enable_stopping=False,
            name="FCFS-Fixed",
        )

    def _pick_ready(self, inst: WorkflowRuntime, ready: List[str]) -> str:
        return ready[0]


class FixedPlanEC(AgentQO):
    """Stage-3 ablation: EC-aware fidelity/placement, no plan edits."""

    def __init__(self, backend, task_model, n_gpus: int = 2) -> None:
        super().__init__(
            backend, task_model, n_gpus=n_gpus,
            enable_edits=False, enable_kv=True, enable_stopping=False,
            name="FixedPlan-EC",
        )

    def _admit_workflow(self, workflow_id: str, arrival: Arrival) -> WorkflowRuntime:
        inst = super()._admit_workflow(workflow_id, arrival)
        ranked = sorted(inst.ec.items(), key=lambda x: -x[1])
        n_up = max(1, len(ranked) // 3)
        for node_id, _ in ranked[:n_up]:
            node = inst.workflow.nodes[node_id]
            if len(node.fidelities) > 1:
                inst.fidelities[node_id] = node.fidelities[-1]
        return inst
