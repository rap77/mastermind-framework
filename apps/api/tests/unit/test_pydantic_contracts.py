"""Regression tests for shared Pydantic contract rules."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from mastermind_cli.api.models.execution import ExecutionSummary
from mastermind_cli.api.routes.tasks import CreateTaskRequest
from mastermind_cli.project_state.schemas.overview import CreateDecisionRequest
from mastermind_cli.state.models import TaskRecord
from mastermind_cli.types.parallel import TaskState


def test_create_task_request_rejects_unexpected_fields() -> None:
    """Public task creation payloads should reject unknown keys."""
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        CreateTaskRequest.model_validate(
            {
                "brief": "Need a product strategy for a travel SaaS",
                "unexpected": "value",
            }
        )


def test_create_decision_request_rejects_unexpected_fields() -> None:
    """Project-state decision writes should reject unknown keys."""
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        CreateDecisionRequest.model_validate(
            {
                "title": "Use Axum for the control plane",
                "status": "pending",
                "rationale_markdown": "Validated as the first slice.",
                "metadata": {},
                "unexpected": "value",
            }
        )


def test_execution_summary_status_uses_shared_enum() -> None:
    """Execution summary should reject invalid status values."""
    with pytest.raises(ValidationError, match="success|error|running"):
        ExecutionSummary(
            id="exec-1",
            task_id="task-1",
            brief="brief",
            status="completed",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )


def test_task_record_status_uses_task_state_enum() -> None:
    """Persisted task state should be limited to known orchestration states."""
    record = TaskRecord(
        id="task-1",
        brain_id="brain-01",
        status=TaskState.RUNNING,
        progress=None,
        result=None,
        error=None,
    )
    assert record.status == "running"

    with pytest.raises(ValidationError, match="pending|running|completed"):
        TaskRecord.model_validate(
            {
                "id": "task-1",
                "brain_id": "brain-01",
                "status": "in_progress",
                "progress": None,
                "result": None,
                "error": None,
            }
        )
