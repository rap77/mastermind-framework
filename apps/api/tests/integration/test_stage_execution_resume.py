"""Integration tests for authoritative stage execution resume state."""

from __future__ import annotations

from pathlib import Path

import pytest

from mastermind_cli.orchestrator.runtime_contracts.models import (
    RunCheckpoint,
    StageResult,
)
from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.repositories.stage_checkpoints import (
    BundleHashMismatch,
    StageCheckpointRepository,
)


@pytest.fixture(scope="session", autouse=True)
def _database_url_for_integration() -> None:
    """This repository integration uses its own isolated project-state database."""


def _repository(tmp_path: Path) -> StageCheckpointRepository:
    """Create an isolated authoritative checkpoint repository."""
    database_url = f"sqlite:///{tmp_path}/stage-resume.db"
    dispose_engines()
    initialize_database(database_url)
    return StageCheckpointRepository(get_session_factory(database_url)())


def _persist_analysis_transition(repository: StageCheckpointRepository) -> None:
    """Persist the first stage and a checkpoint pointing at delivery."""
    repository.commit_transition(
        stage_result=StageResult(
            stage_id="analysis",
            status="passed",
            attempt=1,
            artifact_refs=("artifact-analysis",),
            evidence_refs=("evidence-analysis",),
            finding_refs=(),
            started_at="2026-07-16T12:00:00Z",
            completed_at="2026-07-16T12:01:00Z",
            next_stage_ids=("delivery",),
        ),
        checkpoint=RunCheckpoint(
            checkpoint_id="checkpoint-run-001",
            version=1,
            run_id="run-001",
            bundle_id="bundle-001",
            objective_id="objective-001",
            bundle_content_hash="sha256:bundle-a",
            active_stage_id="delivery",
            active_attempt=2,
            completed_stage_ids=("analysis",),
            skipped_stage_ids=(),
            blocked_stage_ids=(),
            artifact_refs=("artifact-analysis",),
            evidence_refs=("evidence-analysis",),
            pending_approval_ids=(),
            budget_consumed=2,
            budget_remaining=8,
            recovery_state="retry",
            replan_state=None,
            next_eligible_stage_ids=("delivery",),
        ),
        expected_version=0,
        transition_sequence=1,
    )


def test_resume_returns_the_persisted_next_stage_and_attempt(tmp_path: Path) -> None:
    """Resume must continue from the authoritative fine-grained checkpoint."""
    repository = _repository(tmp_path)
    _persist_analysis_transition(repository)

    checkpoint = repository.resume(
        run_id="run-001",
        bundle_content_hash="sha256:bundle-a",
    )

    assert checkpoint.active_stage_id == "delivery"
    assert checkpoint.active_attempt == 2
    assert checkpoint.completed_stage_ids == ("analysis",)
    assert checkpoint.next_eligible_stage_ids == ("delivery",)
    repository.session.close()


def test_resume_blocks_when_the_bundle_hash_changed(tmp_path: Path) -> None:
    """A stale checkpoint cannot be interpreted under a different executable bundle."""
    repository = _repository(tmp_path)
    _persist_analysis_transition(repository)

    with pytest.raises(
        BundleHashMismatch,
        match=(
            "run run-001 checkpoint uses sha256:bundle-a; "
            "requested bundle is sha256:bundle-b"
        ),
    ):
        repository.resume(
            run_id="run-001",
            bundle_content_hash="sha256:bundle-b",
        )

    repository.session.close()
