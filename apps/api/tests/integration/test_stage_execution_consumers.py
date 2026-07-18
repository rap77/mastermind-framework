"""Consumer conformance tests for the shared stage execution runtime."""

from dataclasses import dataclass

import pytest

from mastermind_cli.orchestrator.runtime_contracts.models import (
    EvidenceRecord,
    RunBundle,
    StageDefinition,
    StageGraph,
    StageNode,
)
from mastermind_cli.orchestrator.runtime_contracts.run_bundle_stage_executor import (
    CapabilityExecutionResult,
    RunBundleStageExecutor,
)


@pytest.fixture(scope="session")
def _database_url_for_integration() -> None:
    """Keep this filesystem-only integration contract independent of PostgreSQL."""


@dataclass(frozen=True, slots=True)
class ConsumerFixture:
    """Representative domain graph expressed only through shared contracts."""

    consumer_id: str
    stage_ids: tuple[str, str]


@pytest.fixture(
    params=(
        ConsumerFixture("ui-ux", ("intake", "runtime-verification")),
        ConsumerFixture("onboarding", ("detect", "readiness-classification")),
        ConsumerFixture("delivery", ("readiness-resume", "integration-acceptance")),
    ),
    ids=lambda fixture: fixture.consumer_id,
)
def consumer_fixture(request: pytest.FixtureRequest) -> ConsumerFixture:
    """Provide the three canonical consumer graph shapes."""
    return request.param


class PassingInvoker:
    """Produce typed passing evidence for any selected consumer capability."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def invoke(
        self,
        capability_id: str,
        stage: StageDefinition,
    ) -> CapabilityExecutionResult:
        """Record one invocation and satisfy the stage's declared gate."""
        self.calls.append((stage.stage_id, capability_id))
        evidence = EvidenceRecord(
            evidence_id=f"evidence-{stage.stage_id}",
            check_id=stage.gate_policy,
            performed=True,
            method="tool",
            result="pass",
            summary=f"{stage.name} completed.",
            command_or_procedure=None,
            tool=None,
            environment=None,
            exit_status=0,
            artifact_refs=(),
            metrics=(),
            detail_schema_ref=None,
            details_ref=None,
            limitations=(),
            recorded_at="2026-07-16T12:00:00Z",
        )
        return CapabilityExecutionResult(
            artifact_refs=(f"artifact-{stage.stage_id}",),
            evidence=(evidence,),
            finding_refs=(),
        )


def _bundle(fixture: ConsumerFixture) -> RunBundle:
    """Build one validated consumer bundle using only foundation contracts."""
    first_stage_id, second_stage_id = fixture.stage_ids
    first = _stage(first_stage_id)
    second = _stage(second_stage_id, prerequisites=(first_stage_id,))
    bundle_id = f"bundle-{fixture.consumer_id}"
    graph = StageGraph(
        schema_version="1",
        graph_id=f"graph-{fixture.consumer_id}",
        bundle_id=bundle_id,
        profile_ref=f"{fixture.consumer_id}:v1",
        entry_stage_ids=(first_stage_id,),
        exit_stage_ids=(second_stage_id,),
        nodes=(
            StageNode(stage=second, version="1"),
            StageNode(stage=first, version="1"),
        ),
        edges=(),
        loops=(),
        canonicalization_version="jcs-v1",
        content_hash=f"sha256:{fixture.consumer_id}",
    )
    return RunBundle(
        bundle_id=bundle_id,
        objective_id=f"objective-{fixture.consumer_id}",
        plan_id=f"plan-{fixture.consumer_id}",
        path=f"/tmp/{bundle_id}",
        harness_file=f"/tmp/{bundle_id}/HARNESS.md",
        bundle_manifest=f"/tmp/{bundle_id}/bundle.yaml",
        primary_harness_id=fixture.consumer_id,
        supporting_harness_ids=(),
        selected_skill_ids=tuple(
            f"capability-{stage_id}" for stage_id in fixture.stage_ids
        ),
        validation_status="passed",
        stage_graph=graph,
        content_hash=graph.content_hash,
    )


def _stage(
    stage_id: str,
    *,
    prerequisites: tuple[str, ...] = (),
) -> StageDefinition:
    """Declare a required stage without domain-specific runtime types."""
    return StageDefinition(
        stage_id=stage_id,
        name=stage_id.replace("-", " ").title(),
        required=True,
        prerequisites=prerequisites,
        capability_refs=(f"capability-{stage_id}",),
        input_artifact_types=(),
        output_artifact_types=(),
        gate_policy=f"check-{stage_id}",
        approval_policy="none",
        recovery_policy="bounded-retry",
        max_attempts=1,
    )


def test_three_consumers_execute_through_one_runtime_contract(
    consumer_fixture: ConsumerFixture,
) -> None:
    """UI/UX, onboarding, and delivery graphs should share one executor API."""
    invoker = PassingInvoker()

    report = RunBundleStageExecutor(invoker).execute(_bundle(consumer_fixture))

    assert [record.result.stage_id for record in report.stages] == list(
        consumer_fixture.stage_ids
    )
    assert [record.result.status for record in report.stages] == ["passed", "passed"]
    assert invoker.calls == [
        (stage_id, f"capability-{stage_id}") for stage_id in consumer_fixture.stage_ids
    ]
