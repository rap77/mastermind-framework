"""Tests for dependency-aware safe replanning."""

import pytest

from mastermind_cli.orchestrator.runtime_contracts import (
    StageDefinition,
    StageEdge,
    StageGraph,
    StageNode,
)
from mastermind_cli.orchestrator.runtime_contracts.replanning import ReplanService


def _stage(stage_id: str, prerequisites: tuple[str, ...]) -> StageDefinition:
    """Create a minimal executable stage for impact-analysis tests."""
    return StageDefinition(
        stage_id=stage_id,
        name=stage_id.title(),
        required=True,
        prerequisites=prerequisites,
        capability_refs=(f"capability-{stage_id}",),
        input_artifact_types=(),
        output_artifact_types=(f"artifact-{stage_id}",),
        gate_policy="evidence-required",
        approval_policy="none",
        recovery_policy="bounded-recovery",
        max_attempts=2,
    )


def _graph() -> StageGraph:
    """Create a graph with one affected branch and one unrelated branch."""
    stages = (
        _stage("discover", ()),
        _stage("implement", ("discover",)),
        _stage("review", ("implement",)),
        _stage("approve", ("review",)),
        _stage("report", ("discover",)),
    )
    return StageGraph(
        schema_version="1",
        graph_id="graph-1",
        bundle_id="bundle-1",
        profile_ref="profile-1",
        entry_stage_ids=("discover",),
        exit_stage_ids=("approve", "report"),
        nodes=tuple(StageNode(stage=stage, version="1") for stage in stages),
        edges=(
            StageEdge("discover", "implement", ("passed",), "1"),
            StageEdge("implement", "review", ("passed",), "1"),
            StageEdge("review", "approve", ("passed",), "1"),
            StageEdge("discover", "report", ("passed",), "1"),
        ),
        loops=(),
        canonicalization_version="jcs-v1",
        content_hash="sha256:graph",
    )


def test_replan_invalidates_only_changed_stage_and_its_downstream() -> None:
    """Upstream and unrelated branch evidence must remain valid."""
    record = ReplanService(max_replans=2).create_record(
        graph=_graph(),
        replan_attempt=1,
        replan_id="replan-1",
        run_id="run-1",
        changed_stage_ids=("implement",),
        artifact_refs_by_stage={
            "discover": ("artifact:discovery",),
            "implement": ("artifact:source",),
            "review": ("artifact:findings",),
            "approve": ("artifact:release",),
            "report": ("artifact:report",),
        },
        approval_ids_by_stage={
            "discover": ("approval:discovery",),
            "approve": ("approval:release",),
            "report": ("approval:report",),
        },
        evidence_refs_by_stage={
            "discover": ("evidence:discovery",),
            "implement": ("evidence:implementation",),
            "review": ("evidence:review",),
            "approve": ("evidence:acceptance",),
            "report": ("evidence:report",),
        },
        invalidate_acceptance=True,
        requested_change="Replace implementation capability.",
        reason="Capability unavailable.",
        new_bundle_id="bundle-2",
        new_bundle_version="2",
        confirmation_required=True,
        requested_at="2026-07-16T12:00:00Z",
    )

    assert record.dependency_impacts == ("implement", "review", "approve")
    assert record.invalidated_artifact_refs == (
        "artifact:source",
        "artifact:findings",
        "artifact:release",
    )
    assert record.invalidated_approval_ids == ("approval:release",)
    assert record.invalidated_evidence_refs == (
        "evidence:implementation",
        "evidence:review",
        "evidence:acceptance",
    )
    assert record.invalidated_acceptance is True
    assert record.safe_resume_stage_id == "implement"


def test_replan_rejects_unknown_stages_without_partial_invalidation() -> None:
    """Invalid change requests should fail before producing an impact record."""
    with pytest.raises(ValueError, match="unknown stage: missing"):
        ReplanService(max_replans=2).create_record(
            graph=_graph(),
            replan_attempt=1,
            replan_id="replan-1",
            run_id="run-1",
            changed_stage_ids=("missing",),
            artifact_refs_by_stage={},
            approval_ids_by_stage={},
            requested_change="Change a missing stage.",
            reason="Invalid request.",
            new_bundle_id="bundle-2",
            new_bundle_version="2",
            confirmation_required=False,
            requested_at="2026-07-16T12:00:00Z",
        )


def test_replan_escalates_after_declared_limit() -> None:
    """Replanning must not continue after its bounded attempt limit."""
    with pytest.raises(ValueError, match="maximum replan attempts reached; escalate"):
        ReplanService(max_replans=1).create_record(
            graph=_graph(),
            replan_attempt=2,
            replan_id="replan-2",
            run_id="run-1",
            changed_stage_ids=("implement",),
            artifact_refs_by_stage={},
            approval_ids_by_stage={},
            requested_change="Try another capability.",
            reason="Previous replan failed.",
            new_bundle_id="bundle-3",
            new_bundle_version="3",
            confirmation_required=True,
            requested_at="2026-07-16T12:01:00Z",
        )
