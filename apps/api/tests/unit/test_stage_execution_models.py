"""Tests for the shared stage execution runtime contracts."""

from dataclasses import replace

import pytest

from mastermind_cli.orchestrator.runtime_contracts import (
    ApprovalRecord,
    EvidenceEnvironment,
    EvidenceMetric,
    EvidenceRecord,
    EvidenceTool,
    ReplanRecord,
    RunCheckpoint,
    StageDecision,
    StageDefinition,
    StageEdge,
    StageGraph,
    StageLoop,
    StageNode,
    StageResult,
)


def _stage(stage_id: str = "implement") -> StageDefinition:
    """Create a minimal valid stage definition for contract tests."""
    return StageDefinition(
        stage_id=stage_id,
        name="Implement",
        required=True,
        prerequisites=(),
        capability_refs=("python-editor",),
        input_artifact_types=("spec",),
        output_artifact_types=("source",),
        gate_policy="tests-pass",
        approval_policy="none",
        recovery_policy="bounded-retry",
        max_attempts=2,
    )


def test_stage_graph_exposes_versioned_canonical_hash_input() -> None:
    """Graph hash input should be stable and exclude the digest being computed."""
    graph = StageGraph(
        schema_version="1",
        graph_id="delivery",
        bundle_id="bundle-001",
        profile_ref="profile:v1",
        entry_stage_ids=("implement",),
        exit_stage_ids=("verify",),
        nodes=(
            StageNode(stage=_stage("verify"), version="2"),
            StageNode(stage=_stage(), version="1"),
        ),
        edges=(
            StageEdge(
                from_stage_id="implement",
                to_stage_id="verify",
                on_status=("passed",),
                version="1",
            ),
        ),
        loops=(
            StageLoop(
                loop_id="implementation-loop",
                member_stage_ids=("verify", "implement"),
                entry_stage_id="implement",
                entry_condition_ref="implementation-required",
                exit_condition_ref="verification-passed",
                max_iterations=2,
                checkpoint_each_iteration=True,
                exhausted_action="needs_recovery",
                version="1",
            ),
        ),
        canonicalization_version="jcs-v1",
        content_hash="sha256:abc123",
    )

    hash_input = graph.canonical_hash_input()

    assert "content_hash" not in hash_input
    assert [node["stage"]["stage_id"] for node in hash_input["nodes"]] == [
        "implement",
        "verify",
    ]
    assert hash_input["loops"][0]["member_stage_ids"] == (
        "implement",
        "verify",
    )
    assert hash_input["nodes"][0]["version"] == "1"


def test_stage_execution_records_preserve_decisions_results_and_approvals() -> None:
    """Decision, result, and approval records should retain auditable state."""
    decision = StageDecision(
        stage_id="implement",
        decision="execute",
        rationale="Required output has not been produced.",
        decided_by="policy",
        risk="medium",
        affected_artifacts=("src/app.py",),
    )
    result = StageResult(
        stage_id="implement",
        status="needs_review",
        attempt=1,
        artifact_refs=("artifact:source:1",),
        evidence_refs=("evidence:pytest:1",),
        finding_refs=(),
        started_at="2026-07-16T10:00:00Z",
        completed_at="2026-07-16T10:01:00Z",
        next_stage_ids=("review",),
    )
    approval = ApprovalRecord(
        approval_id="approval-001",
        scope="stage",
        decision="approved",
        actor="reviewer-001",
        rationale="Independent review passed.",
        artifact_versions=("artifact:source:1",),
        decided_at="2026-07-16T10:02:00Z",
        expires_at=None,
    )

    assert decision.decision == "execute"
    assert result.status == "needs_review"
    assert approval.scope == "stage"


def test_evidence_record_derives_passed_from_performed_result() -> None:
    """Evidence should expose pass only when the check ran and passed."""
    evidence = EvidenceRecord(
        evidence_id="evidence-001",
        check_id="pytest-unit",
        performed=True,
        method="command",
        result="pass",
        summary="Targeted unit tests passed.",
        command_or_procedure="uv run pytest -q tests/unit/test_models.py",
        tool=EvidenceTool(id="pytest", version="8"),
        environment=EvidenceEnvironment(name="local", configuration_refs=()),
        exit_status=0,
        artifact_refs=("report:pytest:1",),
        metrics=(
            EvidenceMetric(
                name="tests_passed",
                actual=12,
                expected=12,
                unit="tests",
                passed=True,
            ),
        ),
        detail_schema_ref=None,
        details_ref="report:pytest:1",
        limitations=(),
        recorded_at="2026-07-16T10:03:00Z",
    )

    assert evidence.passed is True
    assert replace(evidence, performed=False, result="skipped").passed is False


def test_checkpoint_and_replan_capture_resume_and_invalidation_state() -> None:
    """Checkpoint and replan records should retain safe-resume lineage."""
    checkpoint = RunCheckpoint(
        checkpoint_id="checkpoint-001",
        version=3,
        run_id="run-001",
        bundle_id="bundle-001",
        objective_id="objective-001",
        bundle_content_hash="sha256:abc123",
        active_stage_id="review",
        active_attempt=1,
        completed_stage_ids=("implement",),
        skipped_stage_ids=(),
        blocked_stage_ids=(),
        artifact_refs=("artifact:source:1",),
        evidence_refs=("evidence:pytest:1",),
        pending_approval_ids=("approval-001",),
        budget_consumed=2,
        budget_remaining=8,
        recovery_state=None,
        replan_state="requested",
        next_eligible_stage_ids=("review",),
    )
    replan = ReplanRecord(
        replan_id="replan-001",
        run_id="run-001",
        requested_change="Replace review stage policy.",
        reason="Original reviewer is unavailable.",
        dependency_impacts=("review", "approve"),
        invalidated_artifact_refs=("artifact:approval-request:1",),
        archived_artifact_refs=(),
        invalidated_approval_ids=("approval-001",),
        new_bundle_id="bundle-002",
        new_bundle_version="2",
        confirmation_required=True,
        safe_resume_stage_id="review",
        requested_at="2026-07-16T10:04:00Z",
    )

    assert checkpoint.next_eligible_stage_ids == ("review",)
    assert checkpoint.version == 3
    assert replan.invalidated_approval_ids == ("approval-001",)
    assert replan.confirmation_required is True


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (
            lambda: replace(_stage(), max_attempts=0),
            "max_attempts must be at least 1",
        ),
        (
            lambda: replace(_stage(), gate_policy=""),
            "gate_policy must not be empty",
        ),
        (
            lambda: StageDecision(
                stage_id="implement",
                decision="invalid",  # type: ignore[arg-type]
                rationale="Not a supported boundary value.",
                decided_by="policy",
                risk="low",
                affected_artifacts=(),
            ),
            "Unsupported stage decision",
        ),
        (
            lambda: StageResult(
                stage_id="implement",
                status="unknown",  # type: ignore[arg-type]
                attempt=1,
                artifact_refs=(),
                evidence_refs=(),
                finding_refs=(),
                started_at="2026-07-16T10:00:00Z",
                completed_at="2026-07-16T10:01:00Z",
                next_stage_ids=(),
            ),
            "Unsupported stage result status",
        ),
        (
            lambda: EvidenceRecord(
                evidence_id="evidence-001",
                check_id="pytest-unit",
                performed=False,
                method="command",
                result="pass",
                summary="An unperformed check cannot pass.",
                command_or_procedure=None,
                tool=None,
                environment=None,
                exit_status=None,
                artifact_refs=(),
                metrics=(),
                detail_schema_ref=None,
                details_ref=None,
                limitations=(),
                recorded_at="2026-07-16T10:03:00Z",
            ),
            "Unperformed evidence cannot pass",
        ),
        (
            lambda: StageLoop(
                loop_id="loop",
                member_stage_ids=("implement",),
                entry_stage_id="implement",
                entry_condition_ref="required",
                exit_condition_ref="passed",
                max_iterations=0,
                checkpoint_each_iteration=True,
                exhausted_action="blocked",
                version="1",
            ),
            "max_iterations must be at least 1",
        ),
    ],
)
def test_invalid_stage_status_and_policy_states_fail_at_model_boundaries(
    factory: object, message: str
) -> None:
    """Invalid status and policy states should fail before runtime execution."""
    with pytest.raises(ValueError, match=message):
        factory()  # type: ignore[operator]
