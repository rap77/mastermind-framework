"""Repository tests for objective planning projections."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.repositories.planning_projection import (
    PlanningProjectionRepository,
)


def test_planning_projection_repository_persists_and_reads_back(tmp_path: Path) -> None:
    """The planning projection repository must persist and query rows."""
    database_url = f"sqlite:///{tmp_path}/planning_projection_repo_test.db"
    dispose_engines()
    initialize_database(database_url)

    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        repo = PlanningProjectionRepository(session)

        document = repo.record_document_snapshot(
            document_id="doc-001",
            objective_slug="multi-channel-gateway",
            doc_type="handoff",
            source_path=".planning/changes/multi-channel-gateway/HANDOFF-CURRENT.md",
            content_hash="sha256:abc",
            version=1,
            is_canonical=True,
            created_at=now,
            updated_at=now,
        )
        event = repo.record_event(
            event_id="evt-001",
            objective_slug="multi-channel-gateway",
            event_type="ObjectiveActivated",
            payload_json='{"objective_slug":"multi-channel-gateway"}',
            actor="tester",
            source_path=".planning/HANDOFF-CURRENT.md",
            occurred_at=now,
        )
        projection = repo.upsert_projection(
            objective_slug="multi-channel-gateway",
            current_status="active",
            current_task="T1",
            current_handoff_path=".planning/changes/multi-channel-gateway/HANDOFF-CURRENT.md",
            recommended_next="context-projection",
            last_event_id=event.event_id,
            last_synced_at=now,
        )
        sync_state = repo.upsert_sync_state(
            surface=".planning",
            last_scan_at=now,
            last_hash="sha256:def",
            last_error=None,
            sync_version=1,
        )
        latest = repo.get_latest_document("multi-channel-gateway", "handoff")

    assert document.objective_slug == "multi-channel-gateway"
    assert event.event_type == "ObjectiveActivated"
    assert projection.current_status == "active"
    assert sync_state.surface == ".planning"
    assert latest is not None
    assert latest.content_hash == "sha256:abc"
