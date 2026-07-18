"""Integration tests for retryable stage transition projections."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import func, select

from mastermind_cli.orchestrator.runtime_contracts.models import (
    RunCheckpoint,
    StageResult,
)
from mastermind_cli.orchestrator.runtime_contracts.stage_projection_worker import (
    StageProjectionWorker,
)
from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.models.stage_checkpoint import (
    StageTransitionOutbox,
    StageTransitionRecord,
)
from mastermind_cli.project_state.repositories.stage_checkpoints import (
    StageCheckpointRepository,
)


@pytest.fixture(scope="session", autouse=True)
def _database_url_for_integration() -> None:
    """This integration test owns an isolated SQLite project-state database."""


def _repository(tmp_path: Path) -> StageCheckpointRepository:
    """Create an isolated authoritative project-state repository."""
    database_url = f"sqlite:///{tmp_path}/stage-projection.db"
    dispose_engines()
    initialize_database(database_url)
    return StageCheckpointRepository(get_session_factory(database_url)())


def _commit_transition(repository: StageCheckpointRepository) -> RunCheckpoint:
    """Commit one transition and its planning and memory outbox events."""
    checkpoint = RunCheckpoint(
        checkpoint_id="checkpoint-run-001",
        version=1,
        run_id="run-001",
        bundle_id="bundle-001",
        objective_id="objective-001",
        bundle_content_hash="sha256:bundle-a",
        active_stage_id=None,
        active_attempt=0,
        completed_stage_ids=("delivery",),
        skipped_stage_ids=(),
        blocked_stage_ids=(),
        artifact_refs=("artifact-001",),
        evidence_refs=("evidence-001",),
        pending_approval_ids=(),
        budget_consumed=1,
        budget_remaining=9,
        recovery_state=None,
        replan_state=None,
        next_eligible_stage_ids=(),
    )
    repository.commit_transition(
        stage_result=StageResult(
            stage_id="delivery",
            status="passed",
            attempt=1,
            artifact_refs=("artifact-001",),
            evidence_refs=("evidence-001",),
            finding_refs=(),
            started_at="2026-07-16T12:00:00Z",
            completed_at="2026-07-16T12:01:00Z",
            next_stage_ids=(),
        ),
        checkpoint=checkpoint,
        expected_version=0,
        transition_sequence=1,
    )
    return checkpoint


def test_failed_projector_retries_without_changing_authoritative_state(
    tmp_path: Path,
) -> None:
    """A failed destination remains pending while committed state stays unchanged."""
    repository = _repository(tmp_path)
    checkpoint = _commit_transition(repository)
    projected: list[str] = []
    planning_attempts = 0

    def project_planning(payload: dict[str, object]) -> None:
        del payload
        nonlocal planning_attempts
        planning_attempts += 1
        if planning_attempts == 1:
            raise OSError("planning projection unavailable")
        projected.append("planning")

    def project_memory(payload: dict[str, object]) -> None:
        del payload
        projected.append("memory")

    worker = StageProjectionWorker(
        repository.session,
        projectors={"planning": project_planning, "memory": project_memory},
    )

    first = worker.process_pending()

    assert first.attempted == 2
    assert first.processed == 1
    assert first.failed_event_ids
    assert repository.get_checkpoint("run-001") == checkpoint
    assert (
        repository.session.scalar(
            select(func.count()).select_from(StageTransitionRecord)
        )
        == 1
    )

    second = worker.process_pending()

    assert second.attempted == 1
    assert second.processed == 1
    assert second.failed_event_ids == ()
    assert projected == ["memory", "planning"]
    assert repository.get_checkpoint("run-001") == checkpoint
    assert (
        repository.session.scalar(
            select(func.count())
            .select_from(StageTransitionOutbox)
            .where(StageTransitionOutbox.processed_at.is_(None))
        )
        == 0
    )
    repository.session.close()


def test_processed_outbox_events_are_not_projected_twice(tmp_path: Path) -> None:
    """Replaying the worker suppresses duplicate downstream projection effects."""
    repository = _repository(tmp_path)
    _commit_transition(repository)
    projected: list[str] = []
    worker = StageProjectionWorker(
        repository.session,
        projectors={
            "planning": lambda payload: projected.append(str(payload["run_id"])),
            "memory": lambda payload: projected.append(str(payload["run_id"])),
        },
    )

    first = worker.process_pending()
    replay = worker.process_pending()

    assert first.processed == 2
    assert replay.attempted == 0
    assert replay.processed == 0
    assert projected == ["run-001", "run-001"]
    repository.session.close()
