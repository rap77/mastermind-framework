"""Tests for MM-Flow CLI integration with the planning bridge adapter."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from mastermind_cli.mm_flow import cli as mm_flow_cli


class _FakeTransaction:
    async def __aenter__(self) -> "_FakeTransaction":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        del exc_type, exc, tb
        return False


class _FakeConnection:
    def __init__(self, update_status: str = "UPDATE 1") -> None:
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.closed = False
        self._update_status = update_status

    def transaction(self) -> _FakeTransaction:
        return _FakeTransaction()

    async def execute(self, sql: str, *args: object) -> str:
        self.executed.append((sql, args))
        if sql.lstrip().upper().startswith("UPDATE"):
            return self._update_status
        return ""

    async def close(self) -> None:
        self.closed = True


def test_run_phase_in_progress_invokes_executor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """run-phase --start should build an executor and call execute_harness_run."""
    from mastermind_cli.mm_flow.integrated_run import (
        IntegratedRun,
        ValidationCheck,
        ValidationReport,
    )
    from mastermind_cli.mm_flow.planning_bridge import HarnessRequest

    fake_conn = _FakeConnection()
    executor_calls: list[dict[str, object]] = []
    runtime_state_calls: list[tuple[object, ...]] = []

    class FakeExecutor:
        def __init__(self, **_: object) -> None:
            pass

        async def execute_harness_run(self, **kwargs: object) -> IntegratedRun:
            executor_calls.append(kwargs)
            return IntegratedRun(
                project_id="proj-001",
                request=HarnessRequest(
                    project_name="Project Alpha",
                    design_objective="alpha-v1",
                    operational_objective="alpha-v1",
                    active_uow="UOW-1",
                    project_root=Path("/tmp/project-alpha"),
                    constraints=(),
                    expected_outputs=(),
                    required_checks=(),
                ),
                memory_snapshot=None,
                runtime_result=None,
                memory_write=None,
                archive_record=None,
                warnings=(),
                validation=ValidationReport(
                    passed=True,
                    checks=(
                        ValidationCheck(
                            check_id="manifest_present",
                            label="Project manifest fields present",
                            passed=True,
                        ),
                    ),
                    warnings=(),
                ),
            )

    def fake_build_memory_store_from_env(
        database_url: str, enable_vector: bool, enable_index: bool
    ) -> SimpleNamespace:
        del database_url, enable_vector, enable_index
        return SimpleNamespace()

    def fake_write_runtime_state(*args: object) -> None:
        runtime_state_calls.append(args)

    async def fake_connect(database_url: str) -> _FakeConnection:
        del database_url
        return fake_conn

    monkeypatch.setenv("DATABASE_URL", "postgresql://example.test/db")
    monkeypatch.setattr(mm_flow_cli.asyncpg, "connect", fake_connect)
    monkeypatch.setattr(
        mm_flow_cli, "build_memory_store_from_env", fake_build_memory_store_from_env
    )
    monkeypatch.setattr(mm_flow_cli, "_write_runtime_state", fake_write_runtime_state)
    monkeypatch.setattr(mm_flow_cli, "HarnessRunExecutor", FakeExecutor)

    mm_flow_cli.run_phase.callback(  # type: ignore[attr-defined]
        phase=21,
        brief="Implement and design a migration plan",
        brain_ids="brain-01-product-strategy,brain-03-ui-design",
        status="in_progress",
        summary="Alpha slice 6 run.",
        tokens=0,
        commit=None,
    )

    assert len(executor_calls) == 1
    call = executor_calls[0]
    assert call["status"] == "in_progress"
    assert call["brain_ids"] == ("brain-01-product-strategy", "brain-03-ui-design")
    assert call["summary"] == "Alpha slice 6 run."
    assert len(runtime_state_calls) == 1
    assert runtime_state_calls[0][2] == "EXECUTION_WAVE"
    assert fake_conn.closed is True


def test_run_phase_completed_archives_bridge_status(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """run-phase --complete should trigger archive path on the bridge and reuse the started execution_id."""

    from mastermind_cli.mm_flow.integrated_run import (
        IntegratedRun,
        ValidationCheck,
        ValidationReport,
    )
    from mastermind_cli.mm_flow.planning_bridge import (
        ArchiveRecord,
        HarnessRequest,
    )

    fake_conn = _FakeConnection()
    fake_conn.executed.append(("__seeded_in_progress__", ("exec-aaaa-1111", 21)))
    executor_calls: list[dict[str, object]] = []
    runtime_state_calls: list[tuple[object, ...]] = []
    started_execution_id = "exec-aaaa-1111"
    runtime_state_dir = tmp_path / ".planning" / ".mm-flow"
    runtime_state_dir.mkdir(parents=True, exist_ok=True)
    (runtime_state_dir / "runtime-state.json").write_text(
        '{"execution_id": "' + started_execution_id + '"}',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    class FakeExecutor:
        def __init__(self, **_: object) -> None:
            pass

        async def execute_harness_run(self, **kwargs: object) -> IntegratedRun:
            executor_calls.append(kwargs)
            return IntegratedRun(
                project_id="proj-001",
                request=HarnessRequest(
                    project_name="Project Alpha",
                    design_objective="alpha-v1",
                    operational_objective="alpha-v1",
                    active_uow="UOW-1",
                    project_root=Path("/tmp/project-alpha"),
                    constraints=(),
                    expected_outputs=(),
                    required_checks=(),
                ),
                memory_snapshot=None,
                runtime_result=None,
                memory_write=None,
                archive_record=ArchiveRecord(
                    objective="alpha-v1",
                    uow="UOW-1",
                    summary="Alpha slice 6 closed.",
                    archived_at=datetime.now(timezone.utc).isoformat(),
                ),
                warnings=(),
                validation=ValidationReport(
                    passed=True,
                    checks=(
                        ValidationCheck(
                            check_id="manifest_present",
                            label="Project manifest fields present",
                            passed=True,
                        ),
                    ),
                    warnings=(),
                ),
            )

    def fake_write_runtime_state(*args: object) -> None:
        runtime_state_calls.append(args)

    def fake_build_memory_store_from_env(
        database_url: str, enable_vector: bool, enable_index: bool
    ) -> SimpleNamespace:
        del database_url, enable_vector, enable_index
        return SimpleNamespace()

    monkeypatch.setenv("DATABASE_URL", "postgresql://example.test/db")
    monkeypatch.setattr(
        mm_flow_cli.asyncpg, "connect", lambda url: _async_return(fake_conn)
    )
    monkeypatch.setattr(
        mm_flow_cli, "build_memory_store_from_env", fake_build_memory_store_from_env
    )
    monkeypatch.setattr(mm_flow_cli, "_write_runtime_state", fake_write_runtime_state)
    monkeypatch.setattr(mm_flow_cli, "HarnessRunExecutor", FakeExecutor)

    mm_flow_cli.run_phase.callback(  # type: ignore[attr-defined]
        phase=21,
        brief="Implement and design a migration plan",
        brain_ids="brain-01-product-strategy",
        status="completed",
        summary="Alpha slice 6 closed.",
        tokens=42,
        commit="abc123",
    )

    assert len(executor_calls) == 1
    assert executor_calls[0]["status"] == "completed"
    assert executor_calls[0]["verification_outcome"] == "passed"
    assert len(runtime_state_calls) == 1
    assert runtime_state_calls[0][0] == started_execution_id
    assert runtime_state_calls[0][2] == "COMPLETED"
    update_sql, update_args = fake_conn.executed[-1]
    assert "UPDATE phase_executions" in update_sql
    assert update_args[0] == started_execution_id
    assert fake_conn.closed is True


async def _async_return(value: object) -> object:
    return value
