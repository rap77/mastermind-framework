"""Repository tests for authoritative stage transition checkpoints."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from sqlalchemy import func, select

from mastermind_cli.orchestrator.runtime_contracts.models import (
    RunCheckpoint,
    StageResult,
)
from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.models.stage_checkpoint import (
    StageCheckpointRecord,
    StageTransitionOutbox,
    StageTransitionRecord,
)
from mastermind_cli.project_state.repositories.stage_checkpoints import (
    CheckpointVersionConflict,
    StageCheckpointRepository,
)


def _stage_result() -> StageResult:
    """Return a completed stage result with persisted lineage references."""
    return StageResult(
        stage_id="analysis",
        status="passed",
        attempt=1,
        artifact_refs=("artifact-001",),
        evidence_refs=("evidence-001",),
        finding_refs=(),
        started_at="2026-07-16T12:00:00Z",
        completed_at="2026-07-16T12:01:00Z",
        next_stage_ids=("delivery",),
    )


def _checkpoint(*, version: int = 1) -> RunCheckpoint:
    """Return the checkpoint produced by the analysis transition."""
    return RunCheckpoint(
        checkpoint_id="checkpoint-run-001",
        version=version,
        run_id="run-001",
        bundle_id="bundle-001",
        objective_id="objective-001",
        bundle_content_hash="sha256:bundle-a",
        active_stage_id="delivery",
        active_attempt=1,
        completed_stage_ids=("analysis",),
        skipped_stage_ids=(),
        blocked_stage_ids=(),
        artifact_refs=("artifact-001",),
        evidence_refs=("evidence-001",),
        pending_approval_ids=(),
        budget_consumed=1,
        budget_remaining=9,
        recovery_state=None,
        replan_state=None,
        next_eligible_stage_ids=("delivery",),
    )


@pytest.fixture
def repository(tmp_path: Path) -> StageCheckpointRepository:
    """Create an isolated repository backed by the real project-state schema."""
    database_url = f"sqlite:///{tmp_path}/stage-checkpoints.db"
    dispose_engines()
    initialize_database(database_url)
    session = get_session_factory(database_url)()
    repository = StageCheckpointRepository(session)
    yield repository
    session.close()


def test_transition_commits_result_checkpoint_and_outbox_atomically(
    repository: StageCheckpointRepository,
) -> None:
    """One commit must make the result, checkpoint, and both projections visible."""
    committed = repository.commit_transition(
        stage_result=_stage_result(),
        checkpoint=_checkpoint(),
        expected_version=0,
        transition_sequence=1,
    )

    session = repository.session
    assert committed.replayed is False
    assert committed.stage_result == _stage_result()
    assert committed.checkpoint == _checkpoint()
    assert {event.destination for event in committed.outbox_events} == {
        "memory",
        "planning",
    }
    assert session.scalar(select(func.count()).select_from(StageTransitionRecord)) == 1
    assert session.scalar(select(func.count()).select_from(StageCheckpointRecord)) == 1
    assert session.scalar(select(func.count()).select_from(StageTransitionOutbox)) == 2


def test_expected_version_conflict_leaves_authoritative_state_unchanged(
    repository: StageCheckpointRepository,
) -> None:
    """A stale writer must not append a result, checkpoint, or outbox event."""
    repository.commit_transition(
        stage_result=_stage_result(),
        checkpoint=_checkpoint(),
        expected_version=0,
        transition_sequence=1,
    )

    with pytest.raises(
        CheckpointVersionConflict,
        match="expected checkpoint version 0, found 1",
    ):
        repository.commit_transition(
            stage_result=replace(_stage_result(), stage_id="delivery", attempt=1),
            checkpoint=replace(
                _checkpoint(version=1),
                active_stage_id=None,
                completed_stage_ids=("analysis", "delivery"),
            ),
            expected_version=0,
            transition_sequence=2,
        )

    session = repository.session
    assert session.scalar(select(func.count()).select_from(StageTransitionRecord)) == 1
    assert session.scalar(select(func.count()).select_from(StageCheckpointRecord)) == 1
    assert session.scalar(select(func.count()).select_from(StageTransitionOutbox)) == 2
    assert repository.get_checkpoint("run-001") == _checkpoint()


def test_replaying_idempotency_key_returns_persisted_transition_without_duplicates(
    repository: StageCheckpointRepository,
) -> None:
    """A committed canonical key must replay even after its expected version advanced."""
    first = repository.commit_transition(
        stage_result=_stage_result(),
        checkpoint=_checkpoint(),
        expected_version=0,
        transition_sequence=1,
    )
    replayed = repository.commit_transition(
        stage_result=replace(_stage_result(), status="failed"),
        checkpoint=replace(_checkpoint(), active_stage_id="unexpected"),
        expected_version=0,
        transition_sequence=1,
    )

    session = repository.session
    assert replayed.replayed is True
    assert replayed.transition_id == first.transition_id
    assert replayed.stage_result == _stage_result()
    assert replayed.checkpoint == _checkpoint()
    assert session.scalar(select(func.count()).select_from(StageTransitionRecord)) == 1
    assert session.scalar(select(func.count()).select_from(StageTransitionOutbox)) == 2


def test_replay_returns_the_checkpoint_committed_by_that_transition(
    repository: StageCheckpointRepository,
) -> None:
    """Historical replay must not combine an old result with a newer checkpoint."""
    first_checkpoint = _checkpoint()
    repository.commit_transition(
        stage_result=_stage_result(),
        checkpoint=first_checkpoint,
        expected_version=0,
        transition_sequence=1,
    )
    repository.commit_transition(
        stage_result=replace(
            _stage_result(),
            stage_id="delivery",
            artifact_refs=("artifact-002",),
            evidence_refs=("evidence-002",),
            next_stage_ids=(),
        ),
        checkpoint=replace(
            first_checkpoint,
            version=2,
            active_stage_id=None,
            active_attempt=0,
            completed_stage_ids=("analysis", "delivery"),
            artifact_refs=("artifact-001", "artifact-002"),
            evidence_refs=("evidence-001", "evidence-002"),
            next_eligible_stage_ids=(),
        ),
        expected_version=1,
        transition_sequence=2,
    )

    replayed = repository.commit_transition(
        stage_result=_stage_result(),
        checkpoint=first_checkpoint,
        expected_version=0,
        transition_sequence=1,
    )

    assert replayed.replayed is True
    assert replayed.checkpoint == first_checkpoint
    current = repository.get_checkpoint("run-001")
    assert current is not None
    assert current.version == 2
