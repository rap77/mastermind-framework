"""Cross-domain conformance tests for the Adaptive Delivery core contract."""

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from mastermind_cli.orchestrator.runtime_contracts import (
    AdapterContractRef,
    AdaptiveDeliveryRequest,
    AdaptiveRoutePlanner,
    ArtifactContract,
    DeliveryReadinessEvaluator,
    DeliveryRecoveryService,
    DeliveryStageSelection,
    DeliveryUnit,
    DeliveryUnitDecomposer,
    DomainAdapterRegistry,
    DomainDeliveryAdapter,
    IntegrationAcceptanceEvidence,
    IntegrationAcceptanceService,
    LoopPolicy,
    ProducerCapability,
    ProductionPlan,
    ProductionPlanStep,
    ReplanService,
    ReviewOutcome,
    RunBundle,
    SecurityReadinessPolicy,
    StageDefinition,
    StageEdge,
    StageGraph,
    StageNode,
    StageVocabularyMapping,
    UnitDeliveryOrchestrator,
    UnitDeliveryTransition,
    VerificationStrategy,
)
from mastermind_cli.orchestrator.runtime_contracts.models import EvidenceRecord
from mastermind_cli.orchestrator.runtime_contracts.run_bundle_stage_executor import (
    CapabilityExecutionResult,
    RunBundleStageExecutor,
)

NOW = datetime(2026, 7, 17, 20, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="session", autouse=True)
def _database_url_for_integration() -> None:
    """Override the suite DB guard because these conformance tests perform no I/O."""


@dataclass(frozen=True)
class DomainFixture:
    """Minimal adapter-owned vocabulary consumed by the universal core."""

    domain: str
    mode: str
    adapter_id: str
    artifact_type: str
    producer_capability: str
    verifier_capability: str


DOMAIN_FIXTURES = (
    DomainFixture(
        domain="software",
        mode="change-production",
        adapter_id="software-conformance",
        artifact_type="change-set",
        producer_capability="change-producer",
        verifier_capability="change-verifier",
    ),
    DomainFixture(
        domain="publishing",
        mode="publication-production",
        adapter_id="publication-conformance",
        artifact_type="publication",
        producer_capability="publication-producer",
        verifier_capability="publication-verifier",
    ),
)


def _adapter(fixture: DomainFixture) -> DomainDeliveryAdapter:
    """Declare a minimal adapter fixture without implementing a domain producer."""
    return DomainDeliveryAdapter(
        adapter_id=fixture.adapter_id,
        version="1",
        supported_domains=(fixture.domain,),
        supported_modes=(fixture.mode,),
        decomposition_rule_refs=(AdapterContractRef("decomposition:unit", "1"),),
        stage_mappings=(
            StageVocabularyMapping("production", "produce", "1"),
            StageVocabularyMapping("unit-verification", "verify", "1"),
        ),
        artifact_contracts=(
            ArtifactContract(fixture.artifact_type, "domain-producer", "1"),
        ),
        producer_capabilities=(
            ProducerCapability(
                fixture.producer_capability,
                "1",
                (fixture.artifact_type,),
            ),
            ProducerCapability(
                fixture.verifier_capability,
                "1",
                (fixture.artifact_type,),
            ),
        ),
        verification_strategies=(
            VerificationStrategy(
                "artifact-verification", "1", (fixture.artifact_type,)
            ),
        ),
        integration_semantics_ref=AdapterContractRef("integration:single-unit", "1"),
        policy_pack_refs=(AdapterContractRef("policy:standard", "1"),),
        required_approval_refs=(AdapterContractRef("approval:plan", "1"),),
        security_overlay_ref=AdapterContractRef("security:standard", "1"),
        persistence_projection_refs=(AdapterContractRef("projection:lineage", "1"),),
    )


def _request(fixture: DomainFixture) -> AdaptiveDeliveryRequest:
    """Create one approved mutating request for a domain fixture."""
    return AdaptiveDeliveryRequest(
        objective_id=f"objective-{fixture.domain}",
        delivery_intent=f"Produce {fixture.artifact_type}",
        domain=fixture.domain,
        delivery_mode=fixture.mode,
        requirement_refs=("REQ-1",),
        constraint_refs=(),
        acceptance_criteria=("artifact is verified",),
        candidate_unit_refs=("unit-1",),
        dependency_refs=(),
        target_artifact_types=(fixture.artifact_type,),
        requires_write=True,
        approval_policy="standard",
        security_profile_ref="security:standard",
        budget=4,
        checkpoint_ref=None,
    )


def _unit(request: AdaptiveDeliveryRequest, fixture: DomainFixture) -> DeliveryUnit:
    """Create the same traceable unit shape for either domain."""
    return DeliveryUnit(
        unit_id="unit-1",
        name="Produce and verify",
        objective_ref=request.objective_id,
        requirement_refs=request.requirement_refs,
        dependency_unit_ids=(),
        owned_artifact_types=(fixture.artifact_type,),
        input_contract_refs=(),
        output_contract_refs=(f"contract:{fixture.artifact_type}",),
        acceptance_criteria=request.acceptance_criteria,
        risk_level="low",
        route_profile="standard",
        status="ready",
    )


def _stages(fixture: DomainFixture) -> tuple[StageDefinition, StageDefinition]:
    """Create universal production and verification concerns for one fixture."""
    produce = StageDefinition(
        stage_id="produce",
        name="Produce",
        required=True,
        prerequisites=(),
        capability_refs=(fixture.producer_capability,),
        input_artifact_types=(),
        output_artifact_types=(fixture.artifact_type,),
        gate_policy="check-produce",
        approval_policy="plan",
        recovery_policy="bounded",
        max_attempts=2,
    )
    verify = StageDefinition(
        stage_id="verify",
        name="Verify",
        required=True,
        prerequisites=("produce",),
        capability_refs=(fixture.verifier_capability,),
        input_artifact_types=(fixture.artifact_type,),
        output_artifact_types=(fixture.artifact_type,),
        gate_policy="check-verify",
        approval_policy="none",
        recovery_policy="bounded",
        max_attempts=2,
    )
    return produce, verify


def _graph(fixture: DomainFixture) -> StageGraph:
    """Create the shared executor graph used by delivery and replan tests."""
    stages = _stages(fixture)
    return StageGraph(
        schema_version="1",
        graph_id=f"graph-{fixture.domain}",
        bundle_id=f"bundle-{fixture.domain}",
        profile_ref="delivery:standard@1",
        entry_stage_ids=("produce",),
        exit_stage_ids=("verify",),
        nodes=tuple(StageNode(stage=stage, version="1") for stage in stages),
        edges=(StageEdge("produce", "verify", ("passed",), "1"),),
        loops=(),
        canonicalization_version="jcs-v1",
        content_hash=f"sha256:{fixture.domain}",
    )


def _plan(fixture: DomainFixture) -> ProductionPlan:
    """Create the required versioned plan before mutating production."""
    return ProductionPlan(
        plan_id=f"plan-{fixture.domain}",
        version="1",
        unit_id="unit-1",
        steps=tuple(
            ProductionPlanStep(
                step_id=f"step-{stage_id}",
                stage_id=stage_id,
                target_artifact_refs=(f"artifact:{fixture.artifact_type}:1",),
                requirement_refs=("REQ-1",),
                dependency_refs=("step-produce",) if stage_id == "verify" else (),
                contract_refs=(f"contract:{fixture.artifact_type}",),
                verification_refs=(f"check-{stage_id}",),
                side_effect_refs=("write-artifact",) if stage_id == "produce" else (),
                rollback_considerations=("Restore the previous artifact version.",),
                completion_criteria=(f"{stage_id} evidence passes",),
            )
            for stage_id in ("produce", "verify")
        ),
    )


@dataclass
class PassingInvoker:
    """Minimal capability fixture that returns evidence, not domain behavior."""

    calls: list[str]

    def invoke(
        self, capability_id: str, stage: StageDefinition
    ) -> CapabilityExecutionResult:
        """Return passing evidence for one adapter-declared capability."""
        self.calls.append(capability_id)
        return CapabilityExecutionResult(
            artifact_refs=(f"artifact:{stage.output_artifact_types[0]}:1",),
            evidence=(
                EvidenceRecord(
                    evidence_id=f"evidence-{stage.stage_id}",
                    check_id=stage.gate_policy,
                    performed=True,
                    method="tool",
                    result="pass",
                    summary="Conformance fixture passed.",
                    command_or_procedure=None,
                    tool=None,
                    environment=None,
                    exit_status=0,
                    artifact_refs=(),
                    metrics=(),
                    detail_schema_ref=None,
                    details_ref=None,
                    limitations=(),
                    recorded_at="2026-07-17T20:00:00Z",
                ),
            ),
            finding_refs=(),
        )


@dataclass
class RecordingPersistence:
    """Capture the atomic transition emitted by the universal unit loop."""

    transitions: list[UnitDeliveryTransition]

    def persist(self, transition: UnitDeliveryTransition) -> None:
        """Record one immutable transition."""
        self.transitions.append(transition)


@pytest.mark.parametrize("fixture", DOMAIN_FIXTURES, ids=lambda item: item.domain)
def test_domain_fixture_satisfies_the_same_universal_delivery_contract(
    fixture: DomainFixture,
) -> None:
    """Software and non-software fixtures must pass one core delivery pipeline."""
    request = _request(fixture)
    adapter = _adapter(fixture)
    resolution = DomainAdapterRegistry((adapter,)).resolve(
        domain=request.domain,
        mode=request.delivery_mode,
        required_capability_ids=frozenset(
            {fixture.producer_capability, fixture.verifier_capability}
        ),
    )
    readiness = DeliveryReadinessEvaluator().evaluate(
        request,
        adapter_id=resolution.adapter.versioned_id,
        available_permissions=frozenset({"write"}),
        evaluable_criteria=frozenset(request.acceptance_criteria),
        available_dependency_refs=frozenset(),
        available_checkpoint_refs=frozenset(),
    )
    unit = _unit(request, fixture)
    units = DeliveryUnitDecomposer().decompose(request, (unit,))
    selections = tuple(
        DeliveryStageSelection(
            unit_id=unit.unit_id,
            stage=stage,
            decision="execute",
            rationale="Required by the universal delivery contract.",
            depth="standard",
        )
        for stage in _stages(fixture)
    )
    route = AdaptiveRoutePlanner().plan(
        objective_id=request.objective_id,
        adapter_id=adapter.versioned_id,
        units=units,
        selections=selections,
    )
    graph = _graph(fixture)
    bundle = RunBundle(
        bundle_id=graph.bundle_id,
        objective_id=request.objective_id,
        plan_id=route.route_plan_id,
        path=f"/fixtures/{fixture.domain}",
        harness_file=f"/fixtures/{fixture.domain}/HARNESS.md",
        bundle_manifest=f"/fixtures/{fixture.domain}/bundle.yaml",
        primary_harness_id="adaptive-delivery-lead",
        supporting_harness_ids=(),
        selected_skill_ids=(fixture.producer_capability, fixture.verifier_capability),
        validation_status="passed",
        stage_graph=graph,
        content_hash=graph.content_hash,
    )
    invoker = PassingInvoker(calls=[])
    persistence = RecordingPersistence(transitions=[])
    delivery = UnitDeliveryOrchestrator(
        RunBundleStageExecutor(invoker),
        persistence,
        plan_is_approved=lambda plan: plan.versioned_id == _plan(fixture).versioned_id,
    ).execute(
        units=units,
        bundles={unit.unit_id: bundle},
        production_plans={unit.unit_id: _plan(fixture)},
        mutating_unit_ids=(unit.unit_id,),
    )
    acceptance = IntegrationAcceptanceService().evaluate(
        IntegrationAcceptanceEvidence(
            objective_id=request.objective_id,
            requirement_refs=request.requirement_refs,
            satisfied_requirement_refs=request.requirement_refs,
            unit_ids=(unit.unit_id,),
            completed_unit_ids=(unit.unit_id,),
            approved_excluded_unit_ids=(),
            contract_refs=unit.output_contract_refs,
            compatible_contract_refs=unit.output_contract_refs,
            dependency_refs=(),
            satisfied_dependency_refs=(),
            quality_requirement_refs=(),
            passed_quality_refs=(),
            expected_side_effect_refs=("write-artifact",),
            observed_side_effect_refs=("write-artifact",),
            unsafe_side_effect_refs=(),
            residual_risk_refs=(),
            recorded_residual_risk_refs=(),
            required_approval_refs=(),
            approvals=(),
            evidence_refs=("evidence-produce", "evidence-verify"),
            evaluated_at=NOW,
        ),
        security_verdict=SecurityReadinessPolicy().evaluate((), (), evaluated_at=NOW),
        review_outcome=ReviewOutcome(
            performed=True,
            approved=True,
            findings=(),
            risk_flags=(),
            recommended_next_action="continue",
        ),
    )

    assert readiness.status == "ready"
    assert route.adapter_id == adapter.versioned_id
    assert tuple(decision.concern for decision in route.decisions) == (
        "produce",
        "verify",
    )
    assert delivery.transitions[0].status == "verified"
    assert delivery.transitions == tuple(persistence.transitions)
    assert acceptance.verdict.status == "passed"
    assert invoker.calls == [fixture.producer_capability, fixture.verifier_capability]


@pytest.mark.parametrize("fixture", DOMAIN_FIXTURES, ids=lambda item: item.domain)
def test_domain_fixture_blocks_before_production_without_write_permission(
    fixture: DomainFixture,
) -> None:
    """The same readiness gate blocks mutating production in either domain."""
    request = _request(fixture)

    readiness = DeliveryReadinessEvaluator().evaluate(
        request,
        adapter_id=_adapter(fixture).versioned_id,
        available_permissions=frozenset(),
        evaluable_criteria=frozenset(request.acceptance_criteria),
        available_dependency_refs=frozenset(),
        available_checkpoint_refs=frozenset(),
    )

    assert readiness.status == "blocked"
    assert readiness.permissions_compatible is False
    assert readiness.blocker_refs == ("permission:write",)


@pytest.mark.parametrize("fixture", DOMAIN_FIXTURES, ids=lambda item: item.domain)
def test_domain_fixture_uses_the_same_bounded_recovery_policy(
    fixture: DomainFixture,
) -> None:
    """Transient adapter capability failures use core retry and budget bounds."""
    decision = DeliveryRecoveryService().decide(
        failure_class="execution_error",
        reason=f"{fixture.producer_capability} timed out",
        retryable=True,
        active_attempt=1,
        loop_policy=LoopPolicy(
            base_loop="delivery",
            additional_loops=("recovery",),
            max_iterations=2,
            time_budget_ms=1_000,
            tool_budget=2,
            requires_review=True,
            requires_verification=True,
            recovery_policy_id="bounded-recovery",
        ),
        budget_consumed=1,
        budget_remaining=1,
        recovery_cost=1,
    )

    assert decision.action == "retry"
    assert decision.escalate_to_human is False


@pytest.mark.parametrize("fixture", DOMAIN_FIXTURES, ids=lambda item: item.domain)
def test_domain_fixture_replan_invalidates_changed_stage_and_descendants(
    fixture: DomainFixture,
) -> None:
    """A changed production assumption invalidates downstream domain evidence."""
    record = ReplanService(max_replans=1).create_record(
        graph=_graph(fixture),
        replan_attempt=1,
        replan_id=f"replan-{fixture.domain}",
        run_id=f"run-{fixture.domain}",
        changed_stage_ids=("produce",),
        artifact_refs_by_stage={
            "produce": (f"artifact:{fixture.artifact_type}:1",),
            "verify": (f"verification:{fixture.artifact_type}:1",),
        },
        evidence_refs_by_stage={
            "produce": ("evidence-produce",),
            "verify": ("evidence-verify",),
        },
        approval_ids_by_stage={"produce": ("approval-plan",)},
        requested_change="Replace the invalid production assumption.",
        reason="The original domain input changed.",
        new_bundle_id=f"bundle-{fixture.domain}-2",
        new_bundle_version="2",
        confirmation_required=True,
        requested_at="2026-07-17T20:01:00Z",
        invalidate_acceptance=True,
    )

    assert record.dependency_impacts == ("produce", "verify")
    assert record.invalidated_evidence_refs == (
        "evidence-produce",
        "evidence-verify",
    )
    assert record.invalidated_approval_ids == ("approval-plan",)
    assert record.invalidated_acceptance is True
    assert record.safe_resume_stage_id == "produce"
