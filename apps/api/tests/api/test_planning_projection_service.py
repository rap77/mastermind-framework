"""Service tests for applying planning file writes to the projection DB."""

from __future__ import annotations

from pathlib import Path

from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.services.planning_projection import (
    PlanningProjectionService,
)


def test_planning_projection_service_records_write_and_activity(tmp_path: Path) -> None:
    """A file write should create a document snapshot and event."""
    database_url = f"sqlite:///{tmp_path}/planning_projection_service_test.db"
    dispose_engines()
    initialize_database(database_url)

    session_factory = get_session_factory(database_url)

    with session_factory() as session:
        service = PlanningProjectionService(session)

        snapshot = service.record_document_write(
            objective_slug="multi-channel-gateway",
            doc_type="handoff",
            source_path=".planning/HANDOFF-CURRENT.md",
            content="# Handoff — multi-channel-gateway\n",
            actor="tester",
        )
        activity = service.record_objective_activity(
            objective_slug="multi-channel-gateway",
            event_type="ObjectiveActivated",
            payload={
                "current_status": "active",
                "current_task": "T1",
                "current_handoff_path": ".planning/HANDOFF-CURRENT.md",
                "recommended_next": "context-projection",
            },
            actor="tester",
            source_path=".planning/HANDOFF-CURRENT.md",
        )
        sync_state = service.mark_surface_synced(
            surface=".planning",
            content="# Handoff — multi-channel-gateway\n",
            error=None,
        )

    assert snapshot.objective_slug == "multi-channel-gateway"
    assert snapshot.content_hash
    assert activity.event_type == "ObjectiveActivated"
    assert sync_state.surface == ".planning"
