"""Deterministic prerequisite-safe execution for validated RunBundles."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from .models import (
    EvidenceRecord,
    RunBundle,
    StageDecision,
    StageDefinition,
    StageGraph,
    StageResult,
    StageResultStatus,
)
from .stage_gates import GateEvaluation, GateEvaluator


@dataclass(frozen=True, slots=True)
class CapabilityExecutionResult:
    """Typed artifacts, evidence, and findings returned by one capability."""

    artifact_refs: tuple[str, ...]
    evidence: tuple[EvidenceRecord, ...]
    finding_refs: tuple[str, ...]


class CapabilityInvoker(Protocol):
    """Boundary used by the executor to invoke bundle-selected capabilities."""

    def invoke(
        self,
        capability_id: str,
        stage: StageDefinition,
    ) -> CapabilityExecutionResult:
        """Invoke one capability for one stage."""
        ...


@dataclass(frozen=True, slots=True)
class StageExecutionRecord:
    """Auditable decision, gate verdict, and result for one stage."""

    decision: StageDecision
    gate: GateEvaluation | None
    result: StageResult


@dataclass(frozen=True, slots=True)
class StageExecutionReport:
    """Ordered results produced by executing one validated stage graph."""

    bundle_id: str
    stages: tuple[StageExecutionRecord, ...]


class RunBundleStageExecutor:
    """Execute dependency-ready stages without inferring capabilities."""

    def __init__(
        self,
        capability_invoker: CapabilityInvoker,
        gate_evaluator: GateEvaluator | None = None,
        clock: Callable[[], str] | None = None,
    ) -> None:
        self._capability_invoker = capability_invoker
        self._gate_evaluator = gate_evaluator or GateEvaluator()
        self._clock = clock or self._now_iso

    def execute(
        self,
        bundle: RunBundle,
        *,
        decisions: tuple[StageDecision, ...] = (),
    ) -> StageExecutionReport:
        """Execute all dependency-ready stages in stable stage ID order."""
        graph = self._validate_bundle(bundle)
        stages = {node.stage.stage_id: node.stage for node in graph.nodes}
        decisions_by_stage = self._validate_decisions(stages, decisions)
        pending = set(stages)
        statuses: dict[str, StageResultStatus] = {}
        records: list[StageExecutionRecord] = []

        while pending:
            ready = sorted(
                stage_id
                for stage_id in pending
                if all(
                    statuses.get(prerequisite) == "passed"
                    for prerequisite in stages[stage_id].prerequisites
                )
            )
            if not ready:
                records.extend(
                    self._blocked_records(pending, stages, statuses, decisions_by_stage)
                )
                break

            for stage_id in ready:
                stage = stages[stage_id]
                decision = decisions_by_stage.get(stage_id) or self._execute_decision(
                    stage
                )
                record = self._execute_stage(
                    stage,
                    decision,
                    graph,
                    pending,
                    stages,
                    statuses,
                )
                records.append(record)
                statuses[stage_id] = record.result.status
                pending.remove(stage_id)

        return StageExecutionReport(bundle_id=bundle.bundle_id, stages=tuple(records))

    @staticmethod
    def _validate_bundle(bundle: RunBundle) -> StageGraph:
        """Reject invalid graphs and capability references before side effects."""
        if bundle.validation_status != "passed":
            raise ValueError("RunBundle must pass validation before execution")
        graph = bundle.stage_graph
        if graph is None:
            raise ValueError("RunBundle has no stage graph")
        if graph.bundle_id != bundle.bundle_id:
            raise ValueError("Stage graph bundle_id does not match RunBundle")

        stages = {node.stage.stage_id: node.stage for node in graph.nodes}
        if len(stages) != len(graph.nodes):
            raise ValueError("Stage graph contains duplicate stage IDs")
        selected = set(bundle.selected_skill_ids)
        for stage_id in sorted(stages):
            stage = stages[stage_id]
            for prerequisite in stage.prerequisites:
                if prerequisite not in stages:
                    raise ValueError(
                        f"Stage {stage_id} has unknown prerequisite: {prerequisite}"
                    )
            if not stage.capability_refs:
                raise ValueError(f"Stage {stage_id} has no capability")
            for capability_id in sorted(stage.capability_refs):
                if capability_id not in selected:
                    raise ValueError(
                        f"Stage {stage_id} references capability not selected by bundle: "
                        f"{capability_id}"
                    )
        return graph

    @staticmethod
    def _validate_decisions(
        stages: dict[str, StageDefinition],
        decisions: tuple[StageDecision, ...],
    ) -> dict[str, StageDecision]:
        """Validate decision coverage and reject ambiguous stage policy."""
        decisions_by_stage = {decision.stage_id: decision for decision in decisions}
        if len(decisions_by_stage) != len(decisions):
            raise ValueError("Stage decisions contain duplicate stage IDs")
        unknown = sorted(set(decisions_by_stage) - set(stages))
        if unknown:
            raise ValueError(f"Stage decision references unknown stage: {unknown[0]}")
        for stage_id in sorted(stages):
            stage = stages[stage_id]
            decision = decisions_by_stage.get(stage_id)
            if not stage.required and decision is None:
                raise ValueError(f"Optional stage {stage_id} requires a decision")
            if stage.required and decision is not None and decision.decision == "skip":
                raise ValueError(f"Required stage {stage_id} cannot be skipped")
        return decisions_by_stage

    def _execute_stage(
        self,
        stage: StageDefinition,
        decision: StageDecision,
        graph: StageGraph,
        pending: set[str],
        stages: dict[str, StageDefinition],
        statuses: dict[str, StageResultStatus],
    ) -> StageExecutionRecord:
        """Apply a stage decision, invoke capabilities, and evaluate its gate."""
        started_at = self._clock()
        if decision.decision != "execute":
            status: StageResultStatus = (
                "skipped" if decision.decision == "skip" else "blocked"
            )
            return StageExecutionRecord(
                decision=decision,
                gate=None,
                result=StageResult(
                    stage_id=stage.stage_id,
                    status=status,
                    attempt=1,
                    artifact_refs=(),
                    evidence_refs=(),
                    finding_refs=(),
                    started_at=started_at,
                    completed_at=self._clock(),
                    next_stage_ids=(),
                ),
            )

        capability_results = tuple(
            self._capability_invoker.invoke(capability_id, stage)
            for capability_id in sorted(stage.capability_refs)
        )
        evidence = tuple(
            item
            for capability_result in capability_results
            for item in capability_result.evidence
        )
        gate = self._gate_evaluator.evaluate(stage.gate_policy, evidence)
        status = "passed" if gate.passed else "failed"
        next_stage_ids = self._next_stage_ids(
            stage.stage_id,
            status,
            graph,
            pending,
            stages,
            statuses,
        )
        return StageExecutionRecord(
            decision=decision,
            gate=gate,
            result=StageResult(
                stage_id=stage.stage_id,
                status=status,
                attempt=1,
                artifact_refs=tuple(
                    sorted(
                        artifact_ref
                        for item in capability_results
                        for artifact_ref in item.artifact_refs
                    )
                ),
                evidence_refs=tuple(sorted(item.evidence_id for item in evidence)),
                finding_refs=tuple(
                    sorted(
                        finding_ref
                        for item in capability_results
                        for finding_ref in item.finding_refs
                    )
                ),
                started_at=started_at,
                completed_at=self._clock(),
                next_stage_ids=next_stage_ids,
            ),
        )

    @staticmethod
    def _next_stage_ids(
        completed_stage_id: str,
        completed_status: StageResultStatus,
        graph: StageGraph,
        pending: set[str],
        stages: dict[str, StageDefinition],
        statuses: dict[str, StageResultStatus],
    ) -> tuple[str, ...]:
        """Return stages made eligible by the proposed stage result."""
        proposed_statuses = {**statuses, completed_stage_id: completed_status}
        successors = {
            edge.to_stage_id
            for edge in graph.edges
            if edge.from_stage_id == completed_stage_id
            and completed_status in edge.on_status
        }
        return tuple(
            sorted(
                stage_id
                for stage_id in successors & pending
                if stage_id != completed_stage_id
                and all(
                    proposed_statuses.get(prerequisite) == "passed"
                    for prerequisite in stages[stage_id].prerequisites
                )
            )
        )

    def _blocked_records(
        self,
        pending: set[str],
        stages: dict[str, StageDefinition],
        statuses: dict[str, StageResultStatus],
        decisions: dict[str, StageDecision],
    ) -> tuple[StageExecutionRecord, ...]:
        """Record stages that cannot run because prerequisites did not pass."""
        records: list[StageExecutionRecord] = []
        for stage_id in sorted(pending):
            failed_prerequisites = tuple(
                prerequisite
                for prerequisite in stages[stage_id].prerequisites
                if statuses.get(prerequisite) != "passed"
            )
            rationale = (
                "Prerequisites did not pass: " + ", ".join(failed_prerequisites) + "."
            )
            decision = decisions.get(stage_id)
            if decision is None or decision.decision == "execute":
                decision = StageDecision(
                    stage_id=stage_id,
                    decision="block",
                    rationale=rationale,
                    decided_by="policy",
                    risk="low",
                    affected_artifacts=(),
                )
            timestamp = self._clock()
            records.append(
                StageExecutionRecord(
                    decision=decision,
                    gate=None,
                    result=StageResult(
                        stage_id=stage_id,
                        status="blocked",
                        attempt=1,
                        artifact_refs=(),
                        evidence_refs=(),
                        finding_refs=(),
                        started_at=timestamp,
                        completed_at=timestamp,
                        next_stage_ids=(),
                    ),
                )
            )
        return tuple(records)

    @staticmethod
    def _execute_decision(stage: StageDefinition) -> StageDecision:
        """Create the explicit default execute decision for a required stage."""
        return StageDecision(
            stage_id=stage.stage_id,
            decision="execute",
            rationale="Required stage selected by the validated bundle.",
            decided_by="selector",
            risk="low",
            affected_artifacts=(),
        )

    @staticmethod
    def _now_iso() -> str:
        """Return the current UTC timestamp."""
        return datetime.now(UTC).isoformat()
