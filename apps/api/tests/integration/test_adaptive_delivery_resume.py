"""End-to-end persistence, recovery, replan, and resume for Adaptive Delivery."""

from dataclasses import dataclass, replace

import pytest

from mastermind_cli.orchestrator.runtime_contracts import (
    ApprovalRecord,
    DeliveryArtifactLineage,
    DeliveryRecoveryService,
    DeliveryResumeCheckpoint,
    DeliveryRouteDecision,
    DeliveryRoutePlan,
    DeliveryRuntimeService,
    DeliveryRuntimeSnapshot,
    DeliveryUnit,
    EvidenceRecord,
    IntegrationVerdict,
    LoopPolicy,
    StageDefinition,
    StageEdge,
    StageGraph,
    StageNode,
)


@pytest.fixture(scope="session", autouse=True)
def _database_url_for_integration() -> None:
    """This protocol integration uses an in-memory repository fake."""


@dataclass
class InMemoryDeliveryRuntimeRepository:
    """Repository fake that survives service recreation within a test."""

    snapshots: dict[str, DeliveryRuntimeSnapshot]

    def save(self, snapshot: DeliveryRuntimeSnapshot) -> None:
        """Store one immutable snapshot by run ID."""
        self.snapshots[snapshot.checkpoint.run_id] = snapshot

    def load(self, run_id: str) -> DeliveryRuntimeSnapshot | None:
        """Load the last immutable snapshot for a run."""
        return self.snapshots.get(run_id)


def _unit(unit_id: str, dependencies: tuple[str, ...] = ()) -> DeliveryUnit:
    """Create a minimal traceable delivery unit."""
    return DeliveryUnit(
        unit_id=unit_id,
        name=unit_id.title(),
        objective_ref="objective-1",
        requirement_refs=(f"requirement-{unit_id}",),
        dependency_unit_ids=dependencies,
        owned_artifact_types=(f"artifact-{unit_id}",),
        input_contract_refs=(),
        output_contract_refs=(f"contract-{unit_id}",),
        acceptance_criteria=(f"{unit_id} accepted",),
        risk_level="low",
        route_profile="standard",
        status="active" if unit_id == "publish" else "verified",
    )


def _route() -> DeliveryRoutePlan:
    """Create the persisted route for both units."""
    return DeliveryRoutePlan(
        route_plan_id="route-1",
        objective_id="objective-1",
        adapter_id="adapter-1@1",
        unit_ids=("draft", "publish"),
        decisions=tuple(
            DeliveryRouteDecision(
                unit_id=unit_id,
                concern="production",
                decision="execute",
                rationale="Required by delivery policy.",
                depth="standard",
                prerequisite_refs=(),
                risk_level="low",
            )
            for unit_id in ("draft", "publish")
        ),
    )


def _evidence(evidence_id: str, artifact_ref: str) -> EvidenceRecord:
    """Create passing evidence bound to one artifact version."""
    return EvidenceRecord(
        evidence_id=evidence_id,
        check_id=f"check-{evidence_id}",
        performed=True,
        method="tool",
        result="pass",
        summary="Evidence passed.",
        command_or_procedure=None,
        tool=None,
        environment=None,
        exit_status=0,
        artifact_refs=(artifact_ref,),
        metrics=(),
        detail_schema_ref=None,
        details_ref=None,
        limitations=(),
        recorded_at="2026-07-17T12:00:00Z",
    )


def _approval(approval_id: str, artifact_ref: str) -> ApprovalRecord:
    """Create an approval tied to one artifact version."""
    return ApprovalRecord(
        approval_id=approval_id,
        scope="artifact",
        decision="approved",
        actor="approver-1",
        rationale="Evidence is sufficient.",
        artifact_versions=(artifact_ref,),
        decided_at="2026-07-17T12:01:00Z",
        expires_at=None,
    )


def _snapshot() -> DeliveryRuntimeSnapshot:
    """Create a complete snapshot paused at a second stage attempt."""
    return DeliveryRuntimeSnapshot(
        route_plan=_route(),
        units=(_unit("draft"), _unit("publish", ("draft",))),
        artifact_refs=("artifact:draft:1", "artifact:publish:1"),
        evidence=(
            _evidence("evidence-draft", "artifact:draft:1"),
            _evidence("evidence-publish", "artifact:publish:1"),
        ),
        integration_verdict=IntegrationVerdict(
            status="passed",
            objective_id="objective-1",
            unit_ids=("draft", "publish"),
            requirement_refs=("requirement-draft", "requirement-publish"),
            evidence_refs=("evidence-draft", "evidence-publish"),
            blocker_refs=(),
            residual_risks=(),
            conditions=(),
            condition_owner=None,
            condition_expires_at=None,
            contract_refs=("contract-draft", "contract-publish"),
        ),
        approvals=(
            _approval("approval-draft", "artifact:draft:1"),
            _approval("approval-publish", "artifact:publish:1"),
        ),
        lineage=(
            DeliveryArtifactLineage(
                artifact_ref="artifact:draft:1",
                unit_id="draft",
                requirement_refs=("requirement-draft",),
                source_artifact_refs=(),
            ),
            DeliveryArtifactLineage(
                artifact_ref="artifact:publish:1",
                unit_id="publish",
                requirement_refs=("requirement-publish",),
                source_artifact_refs=("artifact:draft:1",),
            ),
        ),
        checkpoint=DeliveryResumeCheckpoint(
            checkpoint_id="checkpoint-1",
            version=4,
            run_id="run-1",
            objective_id="objective-1",
            bundle_id="bundle-1",
            bundle_content_hash="sha256:bundle-1",
            active_unit_id="publish",
            active_stage_id="publish-verify",
            active_step_id="publish-step-verify",
            active_attempt=2,
            completed_unit_ids=("draft",),
            completed_stage_ids=("draft-produce", "draft-verify", "publish-produce"),
            completed_step_ids=(
                "draft-step-produce",
                "draft-step-verify",
                "publish-step-produce",
            ),
            budget_consumed=7,
            budget_remaining=3,
        ),
    )


def _graph() -> StageGraph:
    """Create a graph where publish depends on draft."""
    stages = (
        StageDefinition(
            stage_id="draft-verify",
            name="Draft verify",
            required=True,
            prerequisites=(),
            capability_refs=("verify-draft",),
            input_artifact_types=(),
            output_artifact_types=("draft",),
            gate_policy="evidence-required",
            approval_policy="artifact",
            recovery_policy="bounded",
            max_attempts=2,
        ),
        StageDefinition(
            stage_id="publish-verify",
            name="Publish verify",
            required=True,
            prerequisites=("draft-verify",),
            capability_refs=("verify-publish",),
            input_artifact_types=("draft",),
            output_artifact_types=("publication",),
            gate_policy="evidence-required",
            approval_policy="artifact",
            recovery_policy="bounded",
            max_attempts=2,
        ),
    )
    return StageGraph(
        schema_version="1",
        graph_id="graph-1",
        bundle_id="bundle-1",
        profile_ref="profile-1",
        entry_stage_ids=("draft-verify",),
        exit_stage_ids=("publish-verify",),
        nodes=tuple(StageNode(stage=stage, version="1") for stage in stages),
        edges=(StageEdge("draft-verify", "publish-verify", ("passed",), "1"),),
        loops=(),
        canonicalization_version="jcs-v1",
        content_hash="sha256:bundle-1",
    )


def test_persisted_snapshot_resumes_exact_unit_stage_step_and_attempt() -> None:
    """A fresh service must resume exactly without relying on chat history."""
    repository = InMemoryDeliveryRuntimeRepository(snapshots={})
    DeliveryRuntimeService(repository).persist(_snapshot())

    resumed = DeliveryRuntimeService(repository).resume(
        run_id="run-1", bundle_content_hash="sha256:bundle-1"
    )

    assert resumed.checkpoint.active_unit_id == "publish"
    assert resumed.checkpoint.active_stage_id == "publish-verify"
    assert resumed.checkpoint.active_step_id == "publish-step-verify"
    assert resumed.checkpoint.active_attempt == 2
    assert resumed.route_plan.route_plan_id == "route-1"
    assert tuple(unit.unit_id for unit in resumed.units) == ("draft", "publish")
    assert tuple(item.evidence_id for item in resumed.evidence) == (
        "evidence-draft",
        "evidence-publish",
    )
    assert resumed.integration_verdict is not None
    assert tuple(item.approval_id for item in resumed.approvals) == (
        "approval-draft",
        "approval-publish",
    )
    assert resumed.lineage[1].source_artifact_refs == ("artifact:draft:1",)


def test_replan_invalidates_downstream_state_and_stale_acceptance() -> None:
    """Changed stage descendants cannot retain evidence, approvals, or acceptance."""
    repository = InMemoryDeliveryRuntimeRepository(snapshots={})
    service = DeliveryRuntimeService(repository)

    replanned = service.replan(
        snapshot=_snapshot(),
        graph=_graph(),
        replan_attempt=1,
        replan_id="replan-1",
        changed_stage_ids=("draft-verify",),
        artifact_refs_by_stage={
            "draft-verify": ("artifact:draft:1",),
            "publish-verify": ("artifact:publish:1",),
        },
        evidence_refs_by_stage={
            "draft-verify": ("evidence-draft",),
            "publish-verify": ("evidence-publish",),
        },
        approval_ids_by_stage={
            "draft-verify": ("approval-draft",),
            "publish-verify": ("approval-publish",),
        },
        unit_id_by_stage={
            "draft-verify": "draft",
            "publish-verify": "publish",
        },
        step_id_by_stage={
            "draft-verify": "draft-step-verify",
            "publish-verify": "publish-step-verify",
        },
        requested_change="Replace draft verification route.",
        reason="The original assumption is invalid.",
        new_route_plan=replace(_route(), route_plan_id="route-2"),
        new_bundle_id="bundle-2",
        new_bundle_version="2",
        new_bundle_content_hash="sha256:bundle-2",
        confirmation_required=True,
        requested_at="2026-07-17T12:05:00Z",
    )

    assert replanned.artifact_refs == ()
    assert replanned.evidence == ()
    assert replanned.approvals == ()
    assert replanned.lineage == ()
    assert replanned.integration_verdict is None
    assert replanned.replan_records[0].invalidated_evidence_refs == (
        "evidence-draft",
        "evidence-publish",
    )
    assert replanned.replan_records[0].invalidated_acceptance is True
    assert replanned.checkpoint.active_unit_id == "draft"
    assert replanned.checkpoint.active_stage_id == "draft-verify"
    assert replanned.checkpoint.active_step_id == "draft-step-verify"
    assert replanned.checkpoint.active_attempt == 1
    assert replanned.checkpoint.bundle_content_hash == "sha256:bundle-2"


def test_delivery_recovery_stops_at_attempt_or_remaining_budget_boundary() -> None:
    """Delivery recovery must preserve shared bounded-attempt and budget semantics."""
    policy = LoopPolicy(
        base_loop="delivery",
        additional_loops=("recovery",),
        max_iterations=2,
        time_budget_ms=1_000,
        tool_budget=3,
        requires_review=True,
        requires_verification=True,
        recovery_policy_id="bounded-recovery",
    )
    service = DeliveryRecoveryService()

    attempt_exhausted = service.decide(
        failure_class="execution_error",
        reason="timeout",
        retryable=True,
        active_attempt=2,
        loop_policy=policy,
        budget_consumed=5,
        budget_remaining=1,
        recovery_cost=1,
    )
    budget_exhausted = service.decide(
        failure_class="execution_error",
        reason="timeout",
        retryable=True,
        active_attempt=1,
        loop_policy=policy,
        budget_consumed=6,
        budget_remaining=0,
        recovery_cost=1,
    )

    assert attempt_exhausted.action == "stop"
    assert attempt_exhausted.reason == "max recovery attempts reached"
    assert budget_exhausted.action == "stop"
    assert budget_exhausted.reason == "delivery recovery budget exhausted"
