"""Immutable Adaptive Delivery persistence and exact-resume contracts.

The repository protocol is the authoritative project-state boundary. Memory and
planning consumers remain downstream projections of snapshots persisted there.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol, runtime_checkable

from .delivery_models import DeliveryRoutePlan, DeliveryUnit, IntegrationVerdict
from .models import ApprovalRecord, EvidenceRecord, ReplanRecord, StageGraph
from .replanning import ReplanService


@dataclass(frozen=True, slots=True)
class DeliveryArtifactLineage:
    """Requirement and source lineage for one immutable artifact reference."""

    artifact_ref: str
    unit_id: str
    requirement_refs: tuple[str, ...]
    source_artifact_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DeliveryResumeCheckpoint:
    """Attempt-aware cursor for exact unit, stage, and production-step resume."""

    checkpoint_id: str
    version: int
    run_id: str
    objective_id: str
    bundle_id: str
    bundle_content_hash: str
    active_unit_id: str
    active_stage_id: str
    active_step_id: str
    active_attempt: int
    completed_unit_ids: tuple[str, ...]
    completed_stage_ids: tuple[str, ...]
    completed_step_ids: tuple[str, ...]
    budget_consumed: int
    budget_remaining: int

    def __post_init__(self) -> None:
        if self.version < 0:
            raise ValueError("version must not be negative")
        if self.active_attempt < 1:
            raise ValueError("active_attempt must be at least 1")
        if self.budget_consumed < 0 or self.budget_remaining < 0:
            raise ValueError("checkpoint budgets must not be negative")
        if not self.bundle_content_hash.startswith("sha256:"):
            raise ValueError("bundle_content_hash must use the sha256:<digest> format")


@dataclass(frozen=True, slots=True)
class DeliveryRuntimeSnapshot:
    """Complete durable delivery state required without conversational context."""

    route_plan: DeliveryRoutePlan
    units: tuple[DeliveryUnit, ...]
    artifact_refs: tuple[str, ...]
    evidence: tuple[EvidenceRecord, ...]
    integration_verdict: IntegrationVerdict | None
    approvals: tuple[ApprovalRecord, ...]
    lineage: tuple[DeliveryArtifactLineage, ...]
    checkpoint: DeliveryResumeCheckpoint
    replan_records: tuple[ReplanRecord, ...] = ()

    def __post_init__(self) -> None:
        objective_id = self.checkpoint.objective_id
        if self.route_plan.objective_id != objective_id:
            raise ValueError("route plan objective does not match checkpoint")
        if any(unit.objective_ref != objective_id for unit in self.units):
            raise ValueError("delivery unit objective does not match checkpoint")
        unit_ids = tuple(unit.unit_id for unit in self.units)
        if unit_ids != self.route_plan.unit_ids:
            raise ValueError("snapshot units must match route plan unit order")
        if self.checkpoint.active_unit_id not in unit_ids:
            raise ValueError("active checkpoint unit is not in the delivery route")
        if self.integration_verdict is not None:
            if self.integration_verdict.objective_id != objective_id:
                raise ValueError(
                    "integration verdict objective does not match checkpoint"
                )
            evidence_ids = {item.evidence_id for item in self.evidence}
            if not set(self.integration_verdict.evidence_refs).issubset(evidence_ids):
                raise ValueError("integration verdict references missing evidence")


@runtime_checkable
class DeliveryRuntimeRepository(Protocol):
    """Authoritative storage contract for complete delivery snapshots."""

    def save(self, snapshot: DeliveryRuntimeSnapshot) -> None:
        """Atomically persist one complete immutable snapshot."""
        ...

    def load(self, run_id: str) -> DeliveryRuntimeSnapshot | None:
        """Return the latest snapshot for a run, if present."""
        ...


class DeliveryRuntimeService:
    """Persist, safely replan, and exactly resume Adaptive Delivery runs."""

    def __init__(
        self,
        repository: DeliveryRuntimeRepository,
        *,
        max_replans: int = 2,
    ) -> None:
        """Initialize against the authoritative snapshot repository."""
        self._repository = repository
        self._replan_service = ReplanService(max_replans=max_replans)

    def persist(self, snapshot: DeliveryRuntimeSnapshot) -> None:
        """Persist all delivery state through one repository operation."""
        self._repository.save(snapshot)

    def resume(
        self, *, run_id: str, bundle_content_hash: str
    ) -> DeliveryRuntimeSnapshot:
        """Load exact continuation state only for the same immutable bundle."""
        snapshot = self._repository.load(run_id)
        if snapshot is None:
            raise LookupError(f"no delivery snapshot exists for run {run_id}")
        persisted_hash = snapshot.checkpoint.bundle_content_hash
        if persisted_hash != bundle_content_hash:
            raise ValueError(
                f"run {run_id} checkpoint uses {persisted_hash}; "
                f"requested bundle is {bundle_content_hash}; safe replan required"
            )
        return snapshot

    def replan(
        self,
        *,
        snapshot: DeliveryRuntimeSnapshot,
        graph: StageGraph,
        replan_attempt: int,
        replan_id: str,
        changed_stage_ids: tuple[str, ...],
        artifact_refs_by_stage: dict[str, tuple[str, ...]],
        evidence_refs_by_stage: dict[str, tuple[str, ...]],
        approval_ids_by_stage: dict[str, tuple[str, ...]],
        unit_id_by_stage: dict[str, str],
        step_id_by_stage: dict[str, str],
        requested_change: str,
        reason: str,
        new_route_plan: DeliveryRoutePlan,
        new_bundle_id: str,
        new_bundle_version: str,
        new_bundle_content_hash: str,
        confirmation_required: bool,
        requested_at: str,
    ) -> DeliveryRuntimeSnapshot:
        """Invalidate impacted state, reset its exact cursor, and persist the replan."""
        record = self._replan_service.create_record(
            graph=graph,
            replan_attempt=replan_attempt,
            replan_id=replan_id,
            run_id=snapshot.checkpoint.run_id,
            changed_stage_ids=changed_stage_ids,
            artifact_refs_by_stage=artifact_refs_by_stage,
            approval_ids_by_stage=approval_ids_by_stage,
            evidence_refs_by_stage=evidence_refs_by_stage,
            invalidate_acceptance=snapshot.integration_verdict is not None,
            requested_change=requested_change,
            reason=reason,
            new_bundle_id=new_bundle_id,
            new_bundle_version=new_bundle_version,
            confirmation_required=confirmation_required,
            requested_at=requested_at,
        )
        safe_stage_id = record.safe_resume_stage_id
        if safe_stage_id is None:
            raise ValueError("replan did not produce a safe resume stage")
        try:
            safe_unit_id = unit_id_by_stage[safe_stage_id]
            safe_step_id = step_id_by_stage[safe_stage_id]
        except KeyError as exc:
            raise ValueError(
                f"missing delivery cursor mapping for stage: {safe_stage_id}"
            ) from exc

        invalidated_artifacts = set(record.invalidated_artifact_refs)
        invalidated_evidence = set(record.invalidated_evidence_refs)
        invalidated_approvals = set(record.invalidated_approval_ids)
        impacted_stages = set(record.dependency_impacts)
        impacted_steps = {
            step_id_by_stage[stage_id]
            for stage_id in impacted_stages
            if stage_id in step_id_by_stage
        }
        impacted_units = {
            unit_id_by_stage[stage_id]
            for stage_id in impacted_stages
            if stage_id in unit_id_by_stage
        }
        checkpoint = replace(
            snapshot.checkpoint,
            version=snapshot.checkpoint.version + 1,
            bundle_id=new_bundle_id,
            bundle_content_hash=new_bundle_content_hash,
            active_unit_id=safe_unit_id,
            active_stage_id=safe_stage_id,
            active_step_id=safe_step_id,
            active_attempt=1,
            completed_unit_ids=tuple(
                unit_id
                for unit_id in snapshot.checkpoint.completed_unit_ids
                if unit_id not in impacted_units
            ),
            completed_stage_ids=tuple(
                stage_id
                for stage_id in snapshot.checkpoint.completed_stage_ids
                if stage_id not in impacted_stages
            ),
            completed_step_ids=tuple(
                step_id
                for step_id in snapshot.checkpoint.completed_step_ids
                if step_id not in impacted_steps
            ),
        )
        replanned = DeliveryRuntimeSnapshot(
            route_plan=new_route_plan,
            units=snapshot.units,
            artifact_refs=tuple(
                ref
                for ref in snapshot.artifact_refs
                if ref not in invalidated_artifacts
            ),
            evidence=tuple(
                item
                for item in snapshot.evidence
                if item.evidence_id not in invalidated_evidence
            ),
            integration_verdict=None,
            approvals=tuple(
                item
                for item in snapshot.approvals
                if item.approval_id not in invalidated_approvals
            ),
            lineage=tuple(
                item
                for item in snapshot.lineage
                if item.artifact_ref not in invalidated_artifacts
            ),
            checkpoint=checkpoint,
            replan_records=(*snapshot.replan_records, record),
        )
        self.persist(replanned)
        return replanned
