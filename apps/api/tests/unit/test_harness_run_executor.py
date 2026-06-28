"""End-to-end integration tests for the harness run executor."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import BaseModel

from mastermind_cli.memory_layer.models import ContextSnapshot
from mastermind_cli.mm_flow.harness_run_executor import HarnessRunExecutor
from mastermind_cli.mm_flow.integrated_run import IntegratedRun
from mastermind_cli.mm_flow.project_adapter import ProjectAdapter
from mastermind_cli.orchestrator.runtime_contracts import (
    HarnessCore,
    RuntimeExecutionResult,
    RuntimeMemoryWrite,
    RuntimeRequest,
)
from mastermind_cli.orchestrator.stateless_coordinator import (
    CoordinatorConfig,
    StatelessCoordinator,
)
from mastermind_cli.types.interfaces import Brief


def _write_planning_fixture(
    root: Path,
    *,
    include_next_command: bool = True,
    include_objective: bool = True,
) -> None:
    """Write the minimal aidlc-docs + .planning fixture used by the bridge."""
    (root / "aidlc-docs").mkdir(parents=True, exist_ok=True)
    (root / ".planning").mkdir(parents=True, exist_ok=True)
    (root / "aidlc-docs" / "aidlc-state.md").write_text(
        "\n".join(
            [
                "# AI-DLC State",
                "",
                "## Project Manifest",
                "- project_name: MasterMind Unified Harness + Memory",
                "- canonical_scope: reusable harness core, memory core, and project adapters",
                "- source_of_truth_ai_dlc: true",
                "- source_of_truth_planning: true",
                "- active_objective: harness-core-runtime-v1",
                "- active_uow: UOW-3",
                f"- project_root: {root}",
                "- operational_layer: .planning",
                "- design_layer: aidlc-docs",
                "- memory_layer: Engram persistent memory",
                "- harness_layer: apps/api/mastermind_cli and tools/mastermind-cli",
                "- adapter_name: mastermind-adapter",
                "- bridge_contract: aidlc-docs/inception/plans/planning-bridge-contract.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    handoff_lines = [
        "# Handoff — unified harness + memory",
        "",
        "## Last archived",
        "- `window-scheduler` — archived at 2026-06-21T19:23:46",
        "",
        "## Next recommended objective",
    ]
    if include_objective:
        handoff_lines.extend(
            [
                "- `harness-core-runtime-v1` — unified harness + memory platform",
                "- Build a reusable harness core plus memory layer.",
            ]
        )
    handoff_lines.append("")
    handoff_lines.append("## Next command")
    if include_next_command:
        handoff_lines.extend(
            [
                "- Review `aidlc-docs/inception/plans/harness-memory-roadmap.md`.",
            ]
        )
    handoff_lines.append("")
    (root / ".planning" / "HANDOFF-CURRENT.md").write_text(
        "\n".join(handoff_lines),
        encoding="utf-8",
    )


def _build_runtime_result(project_id: str = "proj-001") -> RuntimeExecutionResult:
    """Build a deterministic `RuntimeExecutionResult` from the harness core."""
    core = HarnessCore()
    selection = core.select_runtime(
        RuntimeRequest(
            brief=Brief(problem_statement="Implement and design a migration plan"),
            brain_ids=("brain-01-product-strategy", "brain-03-ui-design"),
        )
    )
    return core.build_execution_result(
        selection,
        artifacts=("brain-01-product-strategy", "brain-03-ui-design"),
        risks=("cross-team dependency",),
        next_actions=("independent review required",),
    )


class _FakeBrainOutput(BaseModel):
    """Minimal brain output used by the fake coordinator wave."""

    status: str = "ok"


def _patch_coordinator(coordinator: StatelessCoordinator) -> None:
    """Patch a coordinator so `execute_flow` runs without real brain functions."""

    async def fake_resolve_waves(
        _self: StatelessCoordinator, _brain_ids: list[str]
    ) -> SimpleNamespace:
        return SimpleNamespace(
            levels=[SimpleNamespace(brain_ids=["brain-01-product-strategy"])]
        )

    async def fake_execute_wave(
        _self: StatelessCoordinator,
        _brain_ids: list[str],
        _brief: Brief,
        _previous_results: dict[str, BaseModel],
        _correlation_id: str,
        conn: object | None = None,
    ) -> dict[str, BaseModel]:
        del conn
        return {"brain-01-product-strategy": _FakeBrainOutput()}

    coordinator._resolve_waves = fake_resolve_waves.__get__(  # type: ignore[method-assign]
        coordinator, StatelessCoordinator
    )
    coordinator._execute_wave = fake_execute_wave.__get__(  # type: ignore[method-assign]
        coordinator, StatelessCoordinator
    )


class _RecordingMemoryWriter:
    """Memory writer that records its inputs without touching real persistence."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def persist_runtime_run(
        self,
        *,
        project_id: str,
        task_id: str | None,
        run_id: str,
        runtime_result: RuntimeExecutionResult,
        snapshot: ContextSnapshot | None = None,
    ) -> RuntimeMemoryWrite:
        """Record the persistence call and return a deterministic summary."""
        self.calls.append(
            {
                "project_id": project_id,
                "task_id": task_id,
                "run_id": run_id,
                "runtime_result": runtime_result,
                "snapshot": snapshot,
            }
        )
        return RuntimeMemoryWrite(
            project_id=project_id,
            run_id=run_id,
            checkpoint_id="ckpt-rec",
            decision_id="dec-rec",
            run_summary_id="summary-rec",
        )


class _FakeMemoryService:
    """Memory service stub that returns a deterministic snapshot."""

    def __init__(self, snapshot: ContextSnapshot) -> None:
        self.snapshot = snapshot
        self.calls: list[str] = []

    async def build_context_snapshot(self, project_id: str) -> ContextSnapshot:
        self.calls.append(project_id)
        return self.snapshot


@pytest.mark.asyncio
async def test_executor_runs_end_to_end_and_writes_handoff(tmp_path: Path) -> None:
    """The executor should drive the full pipeline and write a planning status."""
    _write_planning_fixture(tmp_path)
    adapter = ProjectAdapter.for_repo(tmp_path)
    snapshot = ContextSnapshot(
        project_id=adapter.project_id,
        summary="Resume from prior checkpoint.",
    )
    memory_service = _FakeMemoryService(snapshot)
    writer = _RecordingMemoryWriter()

    captured_configs: list[CoordinatorConfig] = []

    def coordinator_factory(**kwargs: Any) -> StatelessCoordinator:
        config = CoordinatorConfig(**kwargs)
        captured_configs.append(config)
        coordinator = StatelessCoordinator(config)
        _patch_coordinator(coordinator)
        return coordinator

    executor = HarnessRunExecutor(
        adapter=adapter,
        coordinator_factory=coordinator_factory,
        memory_service=memory_service,  # type: ignore[arg-type]
        memory_runtime_writer=writer,  # type: ignore[arg-type]
    )

    run = await executor.execute_harness_run(
        brief=Brief(problem_statement="Implement and design a migration plan"),
        brain_ids=("brain-01-product-strategy", "brain-03-ui-design"),
        status="in_progress",
        summary="Slice 4 integration run.",
    )

    assert isinstance(run, IntegratedRun)
    assert run.project_id == adapter.project_id
    assert run.request.active_uow == "UOW-3"
    assert run.memory_snapshot == snapshot
    assert run.runtime_result is not None
    assert run.runtime_result.execution_envelope.summary == (
        run.runtime_result.execution_envelope.summary
    )
    assert run.memory_write is not None
    assert run.memory_write.checkpoint_id == "ckpt-rec"
    assert run.archive_record is None  # status="in_progress" should NOT archive

    assert len(writer.calls) == 1
    call = writer.calls[0]
    assert call["project_id"] == adapter.project_id
    assert call["snapshot"] == snapshot

    assert memory_service.calls == [adapter.project_id]

    assert len(captured_configs) == 1
    config = captured_configs[0]
    assert config.project_id == adapter.project_id
    assert config.memory_runtime_writer is writer  # type: ignore[comparison-overlap]

    handoff = (tmp_path / ".planning" / "HANDOFF-CURRENT.md").read_text(
        encoding="utf-8"
    )
    assert "## Bridge Status" in handoff
    assert "- status: in_progress" in handoff
    assert "- summary: Slice 4 integration run." in handoff
    assert "- next_action: continue_phase_execution" in handoff


@pytest.mark.asyncio
async def test_executor_archives_when_status_is_completed(tmp_path: Path) -> None:
    """Status=completed should produce an archive record and archive block in file."""
    _write_planning_fixture(tmp_path)
    adapter = ProjectAdapter.for_repo(tmp_path)
    writer = _RecordingMemoryWriter()

    def coordinator_factory(**kwargs: Any) -> StatelessCoordinator:
        coordinator = StatelessCoordinator(CoordinatorConfig(**kwargs))
        _patch_coordinator(coordinator)
        return coordinator

    executor = HarnessRunExecutor(
        adapter=adapter,
        coordinator_factory=coordinator_factory,
        memory_runtime_writer=writer,  # type: ignore[arg-type]
    )

    run = await executor.execute_harness_run(
        brief=Brief(problem_statement="Implement and design a migration plan"),
        brain_ids=("brain-01-product-strategy", "brain-03-ui-design"),
        status="completed",
        summary="Slice 4 closed.",
    )

    assert run.archive_record is not None
    assert run.archive_record.objective == "harness-core-runtime-v1"

    handoff = (tmp_path / ".planning" / "HANDOFF-CURRENT.md").read_text(
        encoding="utf-8"
    )
    assert "## Bridge Archive" in handoff
    assert "- archived_at:" in handoff


@pytest.mark.asyncio
async def test_executor_skips_memory_write_without_writer(tmp_path: Path) -> None:
    """No memory writer should leave persistence untouched but still write the handoff."""
    _write_planning_fixture(tmp_path)
    adapter = ProjectAdapter.for_repo(tmp_path)

    captured_configs: list[CoordinatorConfig] = []

    def coordinator_factory(**kwargs: Any) -> StatelessCoordinator:
        config = CoordinatorConfig(**kwargs)
        captured_configs.append(config)
        coordinator = StatelessCoordinator(config)
        _patch_coordinator(coordinator)
        return coordinator

    executor = HarnessRunExecutor(
        adapter=adapter,
        coordinator_factory=coordinator_factory,
        memory_runtime_writer=None,
    )

    run = await executor.execute_harness_run(
        brief=Brief(problem_statement="Implement and design a migration plan"),
        brain_ids=("brain-01-product-strategy", "brain-03-ui-design"),
        status="in_progress",
        summary="Slice 4 integration run.",
    )

    assert run.memory_write is None
    assert run.memory_snapshot is None
    assert captured_configs[0].project_id == adapter.project_id
    assert captured_configs[0].memory_runtime_writer is None

    handoff = (tmp_path / ".planning" / "HANDOFF-CURRENT.md").read_text(
        encoding="utf-8"
    )
    assert "## Bridge Status" in handoff


@pytest.mark.asyncio
async def test_executor_validation_reports_mismatches(tmp_path: Path) -> None:
    """Validation should surface planning mismatches without blocking the run."""
    _write_planning_fixture(tmp_path, include_next_command=False)
    adapter = ProjectAdapter.for_repo(tmp_path)

    def coordinator_factory(**kwargs: Any) -> StatelessCoordinator:
        coordinator = StatelessCoordinator(CoordinatorConfig(**kwargs))
        _patch_coordinator(coordinator)
        return coordinator

    executor = HarnessRunExecutor(
        adapter=adapter,
        coordinator_factory=coordinator_factory,
    )

    run = await executor.execute_harness_run(
        brief=Brief(problem_statement="Implement and design a migration plan"),
        brain_ids=("brain-01-product-strategy", "brain-03-ui-design"),
        status="in_progress",
        summary="Slice 4 integration run.",
    )

    check_ids = {check.check_id for check in run.validation.checks}
    assert check_ids == {
        "manifest_present",
        "planning_intent_present",
        "next_command_present",
        "objective_alignment",
    }
    assert run.validation.passed is False
    failed = {check.check_id for check in run.validation.checks if not check.passed}
    assert "next_command_present" in failed
