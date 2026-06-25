"""Tests for budget persistence and enforcement."""

from __future__ import annotations

from pathlib import Path

import pytest

from mastermind_cli.orchestrator import Coordinator, OutputFormatter
from mastermind_cli.orchestrator.budget import (
    BudgetContext,
    BudgetEnforcer,
    BudgetLedger,
    BudgetVerdict,
)


pytestmark = pytest.mark.smoke


def test_budget_enforcer_pauses_and_denies_by_threshold(tmp_path: Path) -> None:
    """BudgetEnforcer must pause once over task budget and deny once exhausted."""
    ledger = BudgetLedger(tmp_path / "budget.jsonl")
    enforcer = BudgetEnforcer(
        task_budget_tokens=100,
        session_budget_tokens=300,
        ledger=ledger,
    )
    context = BudgetContext(session_id="session-1", task_id="task-1")

    assert enforcer.pre_call(80, context) == BudgetVerdict.ALLOW
    assert enforcer.pre_call(120, context) == BudgetVerdict.PAUSE_AND_ASK
    assert enforcer.pre_call(250, context) == BudgetVerdict.DENY


def test_budget_enforcer_persists_counts_across_restart(tmp_path: Path) -> None:
    """BudgetEnforcer must recover counts from the append-only ledger."""
    ledger_path = tmp_path / "budget.jsonl"
    context = BudgetContext(session_id="session-1", task_id="task-1")

    first = BudgetEnforcer(
        task_budget_tokens=100,
        session_budget_tokens=300,
        ledger=BudgetLedger(ledger_path),
    )
    first.post_call(60, context)

    reloaded = BudgetEnforcer(
        task_budget_tokens=100,
        session_budget_tokens=300,
        ledger=BudgetLedger(ledger_path),
    )
    snapshot = reloaded.snapshot(context)

    assert snapshot.task_consumed == 60
    assert snapshot.session_consumed == 60
    assert reloaded.pre_call(30, context) == BudgetVerdict.ALLOW
    assert reloaded.pre_call(50, context) == BudgetVerdict.PAUSE_AND_ASK


class _FakeGovernance:
    """Governance stub that always allows."""

    def evaluate(self, *args, **kwargs):
        return None


class _FakeBudgetEnforcer:
    """Budget stub that records the pre-call and returns a configured verdict."""

    def __init__(self, verdict: BudgetVerdict):
        self.verdict = verdict
        self.calls: list[tuple[int, BudgetContext]] = []
        self.post_calls: list[tuple[int, BudgetContext]] = []

    def pre_call(self, estimated_tokens: int, context: BudgetContext) -> BudgetVerdict:
        self.calls.append((estimated_tokens, context))
        return self.verdict

    def post_call(self, actual_tokens: int, context: BudgetContext) -> None:
        self.post_calls.append((actual_tokens, context))


def test_coordinator_blocks_on_budget_denial() -> None:
    """Coordinator must stop before execution when budget denies."""
    budget = _FakeBudgetEnforcer(BudgetVerdict.DENY)
    coordinator = Coordinator(
        formatter=OutputFormatter(),
        governance=None,
        budget_enforcer=budget,
    )

    def _fake_generate(brief: str, flow_type: str) -> dict:
        return {
            "plan_id": "PLAN-BUDGET-001",
            "date": "2026-06-23T00:00:00Z",
            "flow_type": flow_type,
            "brief": {"original": brief, "clarified": brief},
            "tasks": [],
            "summary": {
                "total_tasks": 0,
                "estimated_duration": "0m",
                "critical_path": [],
                "brains_involved": [],
            },
        }

    coordinator.plan_generator.generate = _fake_generate  # type: ignore[method-assign]

    def _fail_execute(*args, **kwargs):  # pragma: no cover - defensive
        raise AssertionError("execution must not run on budget denial")

    coordinator._execute_with_iterations = _fail_execute  # type: ignore[method-assign]

    result = coordinator.orchestrate(
        brief="Crear una app",
        flow="validation_only",
        session_id="session-1",
    )

    assert result["status"] == "blocked"
    assert "Budget" in result["error"]
    assert len(budget.calls) == 1
    assert budget.calls[0][0] > 0
    assert budget.calls[0][1].session_id == "session-1"


def test_coordinator_allows_budget_and_executes() -> None:
    """Coordinator must keep going when budget allows."""
    budget = _FakeBudgetEnforcer(BudgetVerdict.ALLOW)
    coordinator = Coordinator(
        formatter=OutputFormatter(),
        governance=None,
        budget_enforcer=budget,
    )

    def _fake_generate(brief: str, flow_type: str) -> dict:
        return {
            "plan_id": "PLAN-BUDGET-002",
            "date": "2026-06-23T00:00:00Z",
            "flow_type": flow_type,
            "brief": {"original": brief, "clarified": brief},
            "tasks": [],
            "summary": {
                "total_tasks": 0,
                "estimated_duration": "0m",
                "critical_path": [],
                "brains_involved": [],
            },
        }

    coordinator.plan_generator.generate = _fake_generate  # type: ignore[method-assign]
    coordinator._execute_with_iterations = lambda max_iterations: {  # type: ignore[method-assign]
        "plan_id": "PLAN-BUDGET-002",
        "status": "completed",
        "tasks_completed": 0,
        "tasks_total": 0,
        "outputs": {},
        "evaluations": {},
        "final_deliverable": "ok",
    }
    coordinator.formatter.format_final_deliverable = lambda report: "ok"  # type: ignore[method-assign]

    result = coordinator.orchestrate(
        brief="Crear una app",
        flow="validation_only",
        session_id="session-2",
    )

    assert result["status"] == "completed"
    assert len(budget.calls) == 1
    assert budget.calls[0][0] > 0
    assert budget.calls[0][1].session_id == "session-2"
    assert len(budget.post_calls) == 1
    assert budget.post_calls[0][0] == budget.calls[0][0]
    assert budget.post_calls[0][1].session_id == "session-2"
