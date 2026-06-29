"""Tests for the runtime-to-memory persistence adapter."""

from __future__ import annotations

import pytest
from mastermind_cli.memory_layer.models import (
    CheckpointRecord,
    ContextSnapshot,
    DecisionRecord,
    RunSummary,
)
from mastermind_cli.orchestrator.runtime_contracts import (
    HarnessCore,
    MemoryRuntimeAdapter,
    RuntimeMemoryWrite,
    RuntimeRequest,
)
from mastermind_cli.orchestrator.runtime_contracts.models import RuntimeExecutionResult
from mastermind_cli.types.interfaces import Brief


class FakeMemoryService:
    """In-memory fake of `MemoryService` that records persisted records."""

    def __init__(self) -> None:
        """Initialize recorded record lists."""
        self.checkpoints: list[CheckpointRecord] = []
        self.decisions: list[DecisionRecord] = []
        self.run_summaries: list[RunSummary] = []
        self.save_calls: list[tuple[str, str | None, str]] = []

    async def save_checkpoint(self, checkpoint: CheckpointRecord) -> CheckpointRecord:
        """Record a checkpoint without persistence."""
        self.checkpoints.append(checkpoint)
        return checkpoint

    async def save_decision(self, decision: DecisionRecord) -> DecisionRecord:
        """Record a decision without persistence."""
        self.decisions.append(decision)
        return decision

    async def save_run_summary(self, run_summary: RunSummary) -> RunSummary:
        """Record a run summary without persistence."""
        self.run_summaries.append(run_summary)
        return run_summary


@pytest.fixture
def runtime_result() -> RuntimeExecutionResult:
    """Build a deterministic `RuntimeExecutionResult` for adapter tests."""
    core = HarnessCore()
    brief = Brief(
        problem_statement="Implement and design a production migration plan",
        context="Need latest research and design review",
        constraints=["Use current sources"],
    )
    selection = core.select_runtime(
        RuntimeRequest(
            brief=brief,
            brain_ids=("brain-01-product-strategy", "brain-03-ui-design"),
        )
    )
    return core.build_execution_result(
        selection,
        artifacts=("brain-01-product-strategy", "brain-03-ui-design"),
        risks=("cross-team dependency",),
        next_actions=("independent review required",),
    )


@pytest.mark.asyncio
async def test_adapter_skips_when_memory_service_missing() -> None:
    """A null memory service should produce a no-op write summary."""
    adapter = MemoryRuntimeAdapter(memory_service=None)

    write = await adapter.persist_runtime_run(
        project_id="proj-001",
        task_id="task-1",
        run_id="run-1",
        runtime_result=None,
    )

    assert isinstance(write, RuntimeMemoryWrite)
    assert write.checkpoint_id is None
    assert write.decision_id is None
    assert write.run_summary_id is None


@pytest.mark.asyncio
async def test_adapter_rejects_missing_runtime_result_when_service_exists() -> None:
    """A configured service still needs a runtime result to persist."""
    adapter = MemoryRuntimeAdapter(memory_service=FakeMemoryService())

    with pytest.raises(ValueError, match="runtime_result is required"):
        await adapter.persist_runtime_run(
            project_id="proj-001",
            task_id="task-1",
            run_id="run-1",
            runtime_result=None,
        )


@pytest.mark.asyncio
async def test_adapter_persists_checkpoint_decision_and_summary(
    runtime_result: RuntimeExecutionResult,
) -> None:
    """Successful runs should persist all three memory artifacts."""
    fake_service = FakeMemoryService()
    adapter = MemoryRuntimeAdapter(memory_service=fake_service)
    snapshot = ContextSnapshot(
        project_id="proj-001",
        summary="Prior checkpoint available.",
        open_gaps=["No decision available"],
    )

    write = await adapter.persist_runtime_run(
        project_id="proj-001",
        task_id=runtime_result.selection.task_profile.task_id,
        run_id="run-001",
        runtime_result=runtime_result,
        snapshot=snapshot,
    )

    assert len(fake_service.checkpoints) == 1
    assert len(fake_service.decisions) == 1
    assert len(fake_service.run_summaries) == 1
    checkpoint = fake_service.checkpoints[0]
    decision = fake_service.decisions[0]
    run_summary = fake_service.run_summaries[0]
    assert checkpoint.project_id == "proj-001"
    assert checkpoint.task_id == runtime_result.selection.task_profile.task_id
    assert checkpoint.run_id == "run-001"
    assert checkpoint.resume_state["loop_policy_id"] == (
        runtime_result.selection.loop_policy.base_loop
    )
    assert checkpoint.resume_state["open_gaps"] == ["No decision available"]
    assert decision.title.endswith(runtime_result.selection.loop_policy.base_loop)
    assert decision.metadata["task_id"] == (
        runtime_result.selection.task_profile.task_id
    )
    assert run_summary.run_id == "run-001"
    assert run_summary.summary == runtime_result.execution_envelope.summary
    assert write.checkpoint_id == checkpoint.checkpoint_id
    assert write.decision_id == decision.decision_id
    assert write.run_summary_id == run_summary.run_id


@pytest.mark.asyncio
async def test_adapter_uses_concrete_memory_service_when_provided() -> None:
    """Adapter must work with the real `MemoryService` protocol shape."""
    fake_service = FakeMemoryService()
    adapter = MemoryRuntimeAdapter(memory_service=fake_service)

    brief = Brief(problem_statement="Review this API metric")
    core = HarnessCore()
    selection = core.select_runtime(
        RuntimeRequest(
            brief=brief,
            brain_ids=("brain-07-growth-data",),
        )
    )
    runtime_result = core.build_execution_result(
        selection,
        artifacts=("brain-07-growth-data",),
        next_actions=("continue",),
    )

    write = await adapter.persist_runtime_run(
        project_id="proj-002",
        task_id=None,
        run_id="run-002",
        runtime_result=runtime_result,
    )

    assert write.project_id == "proj-002"
    assert write.run_id == "run-002"
    assert fake_service.checkpoints[0].project_id == "proj-002"
    assert isinstance(fake_service.checkpoints[0].resume_state, dict)


def test_adapter_keeps_memory_service_optional_in_constructor() -> None:
    """Default constructor must allow `None` memory service for skip semantics."""
    adapter = MemoryRuntimeAdapter()

    assert adapter.memory_service is None
