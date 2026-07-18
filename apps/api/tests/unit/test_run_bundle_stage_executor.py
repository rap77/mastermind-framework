"""Tests for deterministic, bundle-governed stage execution."""

from dataclasses import dataclass, replace

import pytest

from mastermind_cli.orchestrator.runtime_contracts.models import (
    EvidenceRecord,
    RunBundle,
    StageDecision,
    StageDefinition,
    StageGraph,
    StageNode,
)
from mastermind_cli.orchestrator.runtime_contracts.run_bundle_stage_executor import (
    CapabilityExecutionResult,
    RunBundleStageExecutor,
)


def _stage(
    stage_id: str,
    capability_id: str,
    *,
    prerequisites: tuple[str, ...] = (),
    required: bool = True,
) -> StageDefinition:
    """Create a minimal executable stage."""
    return StageDefinition(
        stage_id=stage_id,
        name=stage_id.title(),
        required=required,
        prerequisites=prerequisites,
        capability_refs=(capability_id,),
        input_artifact_types=(),
        output_artifact_types=(),
        gate_policy=f"check-{stage_id}",
        approval_policy="none",
        recovery_policy="bounded-retry",
        max_attempts=1,
    )


def _bundle(
    stages: tuple[StageDefinition, ...],
    *,
    selected_capabilities: tuple[str, ...],
) -> RunBundle:
    """Create a validated in-memory bundle with a stage graph."""
    graph = StageGraph(
        schema_version="1",
        graph_id="graph-001",
        bundle_id="bundle-001",
        profile_ref="profile:v1",
        entry_stage_ids=tuple(
            sorted(stage.stage_id for stage in stages if not stage.prerequisites)
        ),
        exit_stage_ids=(),
        nodes=tuple(StageNode(stage=stage, version="1") for stage in stages),
        edges=(),
        loops=(),
        canonicalization_version="jcs-v1",
        content_hash="sha256:abc123",
    )
    return RunBundle(
        bundle_id="bundle-001",
        objective_id="objective-001",
        plan_id="plan-001",
        path="/tmp/bundle-001",
        harness_file="/tmp/bundle-001/HARNESS.md",
        bundle_manifest="/tmp/bundle-001/bundle.yaml",
        primary_harness_id="delivery",
        supporting_harness_ids=(),
        selected_skill_ids=selected_capabilities,
        validation_status="passed",
        stage_graph=graph,
        content_hash=graph.content_hash,
    )


def _evidence(stage_id: str) -> EvidenceRecord:
    """Create passing evidence for one stage gate."""
    return EvidenceRecord(
        evidence_id=f"evidence-{stage_id}",
        check_id=f"check-{stage_id}",
        performed=True,
        method="tool",
        result="pass",
        summary=f"{stage_id} check passed.",
        command_or_procedure=None,
        tool=None,
        environment=None,
        exit_status=None,
        artifact_refs=(),
        metrics=(),
        detail_schema_ref=None,
        details_ref=None,
        limitations=(),
        recorded_at="2026-07-16T12:00:00Z",
    )


@dataclass
class RecordingInvoker:
    """Record capability invocations and return passing evidence."""

    calls: list[tuple[str, str]]

    def invoke(
        self,
        capability_id: str,
        stage: StageDefinition,
    ) -> CapabilityExecutionResult:
        """Record one selected capability invocation."""
        self.calls.append((stage.stage_id, capability_id))
        return CapabilityExecutionResult(
            artifact_refs=(f"artifact-{stage.stage_id}",),
            evidence=(_evidence(stage.stage_id),),
            finding_refs=(),
        )


@dataclass
class FailingInvoker(RecordingInvoker):
    """Return failed evidence for a designated stage."""

    failing_stage_id: str

    def invoke(
        self,
        capability_id: str,
        stage: StageDefinition,
    ) -> CapabilityExecutionResult:
        """Record invocation and fail the designated stage gate."""
        result = super().invoke(capability_id, stage)
        if stage.stage_id != self.failing_stage_id:
            return result
        failed = _evidence(stage.stage_id)
        return CapabilityExecutionResult(
            artifact_refs=result.artifact_refs,
            evidence=(replace(failed, result="fail", exit_status=1),),
            finding_refs=result.finding_refs,
        )


def test_executor_orders_dependency_ready_stages_by_stage_id() -> None:
    """Ready stages should be stable and prerequisites must pass first."""
    invoker = RecordingInvoker(calls=[])
    stages = (
        _stage("zeta", "cap-zeta"),
        _stage("final", "cap-final", prerequisites=("zeta", "alpha")),
        _stage("alpha", "cap-alpha"),
    )
    executor = RunBundleStageExecutor(invoker)

    report = executor.execute(
        _bundle(
            stages,
            selected_capabilities=("cap-final", "cap-zeta", "cap-alpha"),
        )
    )

    assert invoker.calls == [
        ("alpha", "cap-alpha"),
        ("zeta", "cap-zeta"),
        ("final", "cap-final"),
    ]
    assert tuple(item.result.stage_id for item in report.stages) == (
        "alpha",
        "zeta",
        "final",
    )
    assert all(item.result.status == "passed" for item in report.stages)


def test_executor_records_optional_skip_rationale_without_invocation() -> None:
    """An optional skip should be auditable and execute no capability."""
    invoker = RecordingInvoker(calls=[])
    optional = _stage("review", "cap-review", required=False)
    decision = StageDecision(
        stage_id="review",
        decision="skip",
        rationale="Low-risk change does not require independent review.",
        decided_by="policy",
        risk="low",
        affected_artifacts=(),
    )

    report = RunBundleStageExecutor(invoker).execute(
        _bundle((optional,), selected_capabilities=("cap-review",)),
        decisions=(decision,),
    )

    assert invoker.calls == []
    assert report.stages[0].decision == decision
    assert report.stages[0].result.status == "skipped"
    assert report.stages[0].decision.rationale == decision.rationale


def test_executor_rejects_unselected_capabilities_before_any_invocation() -> None:
    """A graph cannot infer or invoke a capability absent from its bundle."""
    invoker = RecordingInvoker(calls=[])
    bundle = _bundle(
        (
            _stage("alpha", "cap-selected"),
            _stage("zeta", "cap-not-selected"),
        ),
        selected_capabilities=("cap-selected",),
    )

    with pytest.raises(
        ValueError,
        match="Stage zeta references capability not selected by bundle: cap-not-selected",
    ):
        RunBundleStageExecutor(invoker).execute(bundle)

    assert invoker.calls == []


def test_executor_does_not_invoke_selected_but_unreferenced_capabilities() -> None:
    """Bundle selection grants eligibility, not an instruction to invoke everything."""
    invoker = RecordingInvoker(calls=[])
    bundle = _bundle(
        (_stage("alpha", "cap-referenced"),),
        selected_capabilities=("cap-unused", "cap-referenced"),
    )

    RunBundleStageExecutor(invoker).execute(bundle)

    assert invoker.calls == [("alpha", "cap-referenced")]


def test_executor_blocks_dependents_when_a_prerequisite_gate_fails() -> None:
    """A dependent capability must not run unless every prerequisite passed."""
    invoker = FailingInvoker(calls=[], failing_stage_id="alpha")
    stages = (
        _stage("final", "cap-final", prerequisites=("alpha",)),
        _stage("alpha", "cap-alpha"),
    )

    report = RunBundleStageExecutor(invoker).execute(
        _bundle(stages, selected_capabilities=("cap-alpha", "cap-final"))
    )

    assert invoker.calls == [("alpha", "cap-alpha")]
    assert tuple(item.result.status for item in report.stages) == (
        "failed",
        "blocked",
    )
    assert report.stages[1].decision.rationale == ("Prerequisites did not pass: alpha.")
