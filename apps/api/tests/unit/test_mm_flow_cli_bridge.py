"""Tests for MM-Flow CLI integration with the planning bridge adapter."""

from __future__ import annotations

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
    def __init__(self) -> None:
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.closed = False

    def transaction(self) -> _FakeTransaction:
        return _FakeTransaction()

    async def execute(self, sql: str, *args: object) -> None:
        self.executed.append((sql, args))

    async def close(self) -> None:
        self.closed = True


def test_execute_phase_start_updates_planning_bridge(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Starting a phase should write structured bridge status."""
    fake_conn = _FakeConnection()
    adapter_calls: list[dict[str, object]] = []
    runtime_state_calls: list[tuple[object, ...]] = []

    class FakeAdapter:
        def load_harness_request(self) -> SimpleNamespace:
            return SimpleNamespace(
                operational_objective="harness-memory-unification",
                active_uow="UOW-4",
                warnings=("planning_objective_differs_from_design_objective",),
            )

        def write_structured_status(self, **kwargs: object) -> None:
            adapter_calls.append(kwargs)

    async def fake_connect(database_url: str) -> _FakeConnection:
        del database_url
        return fake_conn

    def fake_build_project_adapter() -> FakeAdapter:
        return FakeAdapter()

    def fake_write_runtime_state(*args: object) -> None:
        runtime_state_calls.append(args)

    monkeypatch.setenv("DATABASE_URL", "postgresql://example.test/db")
    monkeypatch.delenv("MM_MEMORY_PROJECT_ID", raising=False)
    monkeypatch.setattr(mm_flow_cli.asyncpg, "connect", fake_connect)
    monkeypatch.setattr(
        mm_flow_cli, "_build_project_adapter", fake_build_project_adapter
    )
    monkeypatch.setattr(mm_flow_cli, "_write_runtime_state", fake_write_runtime_state)

    mm_flow_cli.execute_phase.callback(  # type: ignore[attr-defined]
        phase=19,
        start=True,
        complete=False,
        commit=None,
        tokens=0,
        summary="",
    )

    assert runtime_state_calls
    assert adapter_calls == [
        {
            "status": "in_progress",
            "summary": "Phase 19 execution started.",
            "next_action": "continue_phase_execution",
            "verification_outcome": "pending",
            "objective": "harness-memory-unification",
            "uow": "UOW-4",
            "warnings": ("planning_objective_differs_from_design_objective",),
        }
    ]
    assert fake_conn.closed is True
