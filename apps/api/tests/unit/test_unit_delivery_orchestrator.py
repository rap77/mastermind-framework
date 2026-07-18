"""Tests for plan-governed, dependency-ready unit delivery."""

from dataclasses import dataclass, replace

import pytest

from mastermind_cli.orchestrator.runtime_contracts.delivery_models import DeliveryUnit
from mastermind_cli.orchestrator.runtime_contracts.models import (
    EvidenceRecord,
    RunBundle,
    StageDefinition,
    StageGraph,
    StageNode,
)
from mastermind_cli.orchestrator.runtime_contracts.production_plans import (
    ProductionPlan,
    ProductionPlanStep,
)
from mastermind_cli.orchestrator.runtime_contracts.run_bundle_stage_executor import (
    CapabilityExecutionResult,
    RunBundleStageExecutor,
)
from mastermind_cli.orchestrator.runtime_contracts.unit_delivery_orchestrator import (
    UnitDeliveryOrchestrator,
    UnitDeliveryTransition,
)


def _unit(unit_id: str, *, dependencies: tuple[str, ...] = ()) -> DeliveryUnit:
    """Create one delivery unit with explicit dependencies."""
    return DeliveryUnit(
        unit_id=unit_id,
        name=unit_id.title(),
        objective_ref="objective-001",
        requirement_refs=(f"requirement-{unit_id}",),
        dependency_unit_ids=dependencies,
        owned_artifact_types=(f"artifact-{unit_id}",),
        input_contract_refs=(),
        output_contract_refs=(f"contract-{unit_id}",),
        acceptance_criteria=(f"{unit_id} is verified",),
        risk_level="low",
        route_profile="standard",
        status="pending",
    )


def _bundle(unit_id: str) -> RunBundle:
    """Create a validated two-stage bundle for one unit."""
    stages = (
        StageDefinition(
            stage_id=f"{unit_id}-produce",
            name="Produce",
            required=True,
            prerequisites=(),
            capability_refs=(f"cap-{unit_id}-produce",),
            input_artifact_types=(),
            output_artifact_types=(f"artifact-{unit_id}",),
            gate_policy=f"check-{unit_id}-produce",
            approval_policy="plan",
            recovery_policy="bounded-retry",
            max_attempts=1,
        ),
        StageDefinition(
            stage_id=f"{unit_id}-verify",
            name="Verify",
            required=True,
            prerequisites=(f"{unit_id}-produce",),
            capability_refs=(f"cap-{unit_id}-verify",),
            input_artifact_types=(f"artifact-{unit_id}",),
            output_artifact_types=(),
            gate_policy=f"check-{unit_id}-verify",
            approval_policy="none",
            recovery_policy="bounded-retry",
            max_attempts=1,
        ),
    )
    graph = StageGraph(
        schema_version="1",
        graph_id=f"graph-{unit_id}",
        bundle_id=f"bundle-{unit_id}",
        profile_ref="profile:v1",
        entry_stage_ids=(f"{unit_id}-produce",),
        exit_stage_ids=(f"{unit_id}-verify",),
        nodes=tuple(StageNode(stage=stage, version="1") for stage in stages),
        edges=(),
        loops=(),
        canonicalization_version="jcs-v1",
        content_hash=f"sha256:{unit_id}",
    )
    return RunBundle(
        bundle_id=f"bundle-{unit_id}",
        objective_id="objective-001",
        plan_id=f"route-{unit_id}",
        path=f"/tmp/bundle-{unit_id}",
        harness_file=f"/tmp/bundle-{unit_id}/HARNESS.md",
        bundle_manifest=f"/tmp/bundle-{unit_id}/bundle.yaml",
        primary_harness_id="adaptive-delivery-lead",
        supporting_harness_ids=(),
        selected_skill_ids=(f"cap-{unit_id}-produce", f"cap-{unit_id}-verify"),
        validation_status="passed",
        stage_graph=graph,
        content_hash=graph.content_hash,
    )


def _plan(unit_id: str) -> ProductionPlan:
    """Create a complete versioned production plan for one bundle."""
    return ProductionPlan(
        plan_id=f"production-{unit_id}",
        version="1",
        unit_id=unit_id,
        steps=(
            ProductionPlanStep(
                step_id=f"{unit_id}-step-produce",
                stage_id=f"{unit_id}-produce",
                target_artifact_refs=(f"artifact-{unit_id}",),
                requirement_refs=(f"requirement-{unit_id}",),
                dependency_refs=(),
                contract_refs=(f"contract-{unit_id}",),
                verification_refs=(f"check-{unit_id}-produce",),
                side_effect_refs=(f"write-artifact-{unit_id}",),
                rollback_considerations=(f"restore-artifact-{unit_id}",),
                completion_criteria=(f"artifact-{unit_id} exists",),
            ),
            ProductionPlanStep(
                step_id=f"{unit_id}-step-verify",
                stage_id=f"{unit_id}-verify",
                target_artifact_refs=(f"artifact-{unit_id}",),
                requirement_refs=(f"requirement-{unit_id}",),
                dependency_refs=(f"{unit_id}-step-produce",),
                contract_refs=(f"contract-{unit_id}",),
                verification_refs=(f"check-{unit_id}-verify",),
                side_effect_refs=(),
                rollback_considerations=("No verification side effects.",),
                completion_criteria=(f"{unit_id} evidence passes",),
            ),
        ),
    )


@dataclass
class RecordingInvoker:
    """Record real shared-executor capability invocations."""

    calls: list[tuple[str, str]]

    def invoke(
        self,
        capability_id: str,
        stage: StageDefinition,
    ) -> CapabilityExecutionResult:
        """Return passing evidence for the invoked stage."""
        self.calls.append((stage.stage_id, capability_id))
        evidence = EvidenceRecord(
            evidence_id=f"evidence-{stage.stage_id}",
            check_id=stage.gate_policy,
            performed=True,
            method="tool",
            result="pass",
            summary="Stage passed.",
            command_or_procedure=None,
            tool=None,
            environment=None,
            exit_status=0,
            artifact_refs=(),
            metrics=(),
            detail_schema_ref=None,
            details_ref=None,
            limitations=(),
            recorded_at="2026-07-17T12:00:00Z",
        )
        return CapabilityExecutionResult(
            artifact_refs=(f"artifact-{stage.stage_id}",),
            evidence=(evidence,),
            finding_refs=(),
        )


@dataclass
class RecordingPersistence:
    """Capture atomic unit transitions."""

    transitions: list[UnitDeliveryTransition]

    def persist(self, transition: UnitDeliveryTransition) -> None:
        """Persist one complete unit transition."""
        self.transitions.append(transition)


@dataclass
class FailingPersistence:
    """Fail the atomic write before any dependent unit can start."""

    calls: int = 0

    def persist(self, transition: UnitDeliveryTransition) -> None:
        """Raise instead of committing the transition."""
        self.calls += 1
        raise OSError(f"Could not persist {transition.unit_id}")


@dataclass
class FailingStageInvoker(RecordingInvoker):
    """Return failed gate evidence for one stage."""

    failing_stage_id: str = ""

    def invoke(
        self,
        capability_id: str,
        stage: StageDefinition,
    ) -> CapabilityExecutionResult:
        """Fail the configured stage while preserving invocation evidence."""
        result = super().invoke(capability_id, stage)
        if stage.stage_id != self.failing_stage_id:
            return result
        return replace(
            result,
            evidence=(replace(result.evidence[0], result="fail", exit_status=1),),
        )


def test_mutating_units_require_all_approved_versioned_plans_before_side_effects() -> (
    None
):
    """Preflight must reject any missing plan before the first capability runs."""
    invoker = RecordingInvoker(calls=[])
    persistence = RecordingPersistence(transitions=[])
    units = (_unit("alpha"), _unit("beta"))

    with pytest.raises(
        ValueError,
        match="Mutating unit 'beta' requires a versioned production plan",
    ):
        UnitDeliveryOrchestrator(
            RunBundleStageExecutor(invoker),
            persistence,
            plan_is_approved=lambda plan: True,
        ).execute(
            units=units,
            bundles={unit.unit_id: _bundle(unit.unit_id) for unit in units},
            production_plans={"alpha": _plan("alpha")},
            mutating_unit_ids=("alpha", "beta"),
        )

    assert invoker.calls == []
    assert persistence.transitions == []


def test_unapproved_mutating_plan_blocks_all_units_before_side_effects() -> None:
    """Approval is a precondition tied to the versioned production plan."""
    invoker = RecordingInvoker(calls=[])
    unit = _unit("alpha")

    with pytest.raises(
        ValueError,
        match="Production plan 'production-alpha@1' is not approved",
    ):
        UnitDeliveryOrchestrator(
            RunBundleStageExecutor(invoker),
            RecordingPersistence(transitions=[]),
            plan_is_approved=lambda plan: False,
        ).execute(
            units=(unit,),
            bundles={unit.unit_id: _bundle(unit.unit_id)},
            production_plans={unit.unit_id: _plan(unit.unit_id)},
            mutating_unit_ids=(unit.unit_id,),
        )

    assert invoker.calls == []


def test_units_execute_dependency_ready_and_end_to_end() -> None:
    """A unit must finish production and verification before its dependent starts."""
    invoker = RecordingInvoker(calls=[])
    persistence = RecordingPersistence(transitions=[])
    units = (
        _unit("gamma", dependencies=("alpha", "beta")),
        _unit("beta"),
        _unit("alpha"),
    )

    report = UnitDeliveryOrchestrator(
        RunBundleStageExecutor(invoker),
        persistence,
        plan_is_approved=lambda plan: True,
    ).execute(
        units=units,
        bundles={unit.unit_id: _bundle(unit.unit_id) for unit in units},
        production_plans={unit.unit_id: _plan(unit.unit_id) for unit in units},
        mutating_unit_ids=tuple(unit.unit_id for unit in units),
    )

    assert invoker.calls == [
        ("alpha-produce", "cap-alpha-produce"),
        ("alpha-verify", "cap-alpha-verify"),
        ("beta-produce", "cap-beta-produce"),
        ("beta-verify", "cap-beta-verify"),
        ("gamma-produce", "cap-gamma-produce"),
        ("gamma-verify", "cap-gamma-verify"),
    ]
    assert tuple(item.unit_id for item in report.transitions) == (
        "alpha",
        "beta",
        "gamma",
    )
    assert report.transitions == tuple(persistence.transitions)
    assert all(item.status == "verified" for item in report.transitions)


def test_production_plan_rejects_incomplete_step_contracts() -> None:
    """Every production step must declare verification and completion criteria."""
    with pytest.raises(ValueError, match="verification_refs must not be empty"):
        ProductionPlanStep(
            step_id="alpha-step",
            stage_id="alpha-produce",
            target_artifact_refs=("artifact-alpha",),
            requirement_refs=("requirement-alpha",),
            dependency_refs=(),
            contract_refs=("contract-alpha",),
            verification_refs=(),
            side_effect_refs=("write-alpha",),
            rollback_considerations=("restore-alpha",),
            completion_criteria=("alpha exists",),
        )


def test_atomic_transition_rejects_checkpoint_progress_drift() -> None:
    """Step and stage progress cannot diverge from the persisted checkpoint."""
    invoker = RecordingInvoker(calls=[])
    persistence = RecordingPersistence(transitions=[])
    unit = _unit("alpha")
    UnitDeliveryOrchestrator(
        RunBundleStageExecutor(invoker),
        persistence,
        plan_is_approved=lambda plan: True,
    ).execute(
        units=(unit,),
        bundles={unit.unit_id: _bundle(unit.unit_id)},
        production_plans={unit.unit_id: _plan(unit.unit_id)},
        mutating_unit_ids=(unit.unit_id,),
    )
    transition = persistence.transitions[0]

    with pytest.raises(
        ValueError,
        match="Transition step progress does not match checkpoint",
    ):
        replace(
            transition,
            completed_step_ids=("different-step",),
        )


def test_failed_stage_and_checkpoint_are_persisted_in_one_blocked_transition() -> None:
    """A failed stage must checkpoint only completed progress and block its unit."""
    invoker = FailingStageInvoker(
        calls=[],
        failing_stage_id="alpha-produce",
    )
    persistence = RecordingPersistence(transitions=[])
    unit = _unit("alpha")

    report = UnitDeliveryOrchestrator(
        RunBundleStageExecutor(invoker),
        persistence,
        plan_is_approved=lambda plan: True,
    ).execute(
        units=(unit,),
        bundles={unit.unit_id: _bundle(unit.unit_id)},
        production_plans={unit.unit_id: _plan(unit.unit_id)},
        mutating_unit_ids=(unit.unit_id,),
    )

    assert len(persistence.transitions) == 1
    transition = persistence.transitions[0]
    assert report.transitions == (transition,)
    assert transition.status == "blocked"
    assert tuple(record.result.status for record in transition.stage_records) == (
        "failed",
        "blocked",
    )
    assert transition.completed_step_ids == ()
    assert transition.checkpoint.completed_step_ids == ()
    assert transition.checkpoint.completed_stage_ids == ()


def test_atomic_persistence_failure_does_not_release_dependent_unit() -> None:
    """A unit is not complete, and its dependent cannot start, until commit succeeds."""
    invoker = RecordingInvoker(calls=[])
    persistence = FailingPersistence()
    units = (_unit("beta", dependencies=("alpha",)), _unit("alpha"))

    with pytest.raises(OSError, match="Could not persist alpha"):
        UnitDeliveryOrchestrator(
            RunBundleStageExecutor(invoker),
            persistence,
            plan_is_approved=lambda plan: True,
        ).execute(
            units=units,
            bundles={unit.unit_id: _bundle(unit.unit_id) for unit in units},
            production_plans={unit.unit_id: _plan(unit.unit_id) for unit in units},
            mutating_unit_ids=tuple(unit.unit_id for unit in units),
        )

    assert persistence.calls == 1
    assert invoker.calls == [
        ("alpha-produce", "cap-alpha-produce"),
        ("alpha-verify", "cap-alpha-verify"),
    ]
