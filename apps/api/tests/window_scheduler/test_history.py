"""TDD coverage for WS-05 scheduler event history queries."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from mastermind_cli.window_scheduler import dispose_engines, initialize_database
from mastermind_cli.window_scheduler.database.session import get_session_factory
from mastermind_cli.window_scheduler.models.scheduler_event import SchedulerEvent
from mastermind_cli.window_scheduler.service import WindowSchedulerService


def _build_service(tmp_path: Path) -> WindowSchedulerService:
    """Create a scheduler service backed by a temporary SQLite database."""
    database_url = f"sqlite:///{tmp_path / 'window_scheduler_history.db'}"
    dispose_engines()
    initialize_database(database_url)
    return WindowSchedulerService(get_session_factory(database_url))


def _record_event(
    service: WindowSchedulerService,
    *,
    event_id: str,
    run_id: str,
    project_id: str,
    event_type: str,
    created_at: datetime,
) -> None:
    """Persist a scheduler event with an explicit timestamp for ordering tests."""
    service.record_event(
        SchedulerEvent(
            event_id=event_id,
            run_id=run_id,
            project_id=project_id,
            task_id="task-1",
            type=event_type,
            from_backend="claude-sub-01",
            to_backend="codex-sub-01",
            reason="history-test",
            decision_outcome=event_type,
            created_at=created_at,
        )
    )


def test_list_recent_events_returns_project_history_in_descending_order(
    tmp_path: Path,
) -> None:
    """The scheduler should return the newest project events first."""
    service = _build_service(tmp_path)
    _record_event(
        service,
        event_id="evt-older",
        run_id="run-1",
        project_id="project-1",
        event_type="window_started",
        created_at=datetime(2026, 6, 21, 9, 0, tzinfo=timezone.utc),
    )
    _record_event(
        service,
        event_id="evt-newest",
        run_id="run-2",
        project_id="project-1",
        event_type="backend_switch",
        created_at=datetime(2026, 6, 21, 10, 0, tzinfo=timezone.utc),
    )
    _record_event(
        service,
        event_id="evt-other-project",
        run_id="run-3",
        project_id="project-2",
        event_type="pause_for_user",
        created_at=datetime(2026, 6, 21, 11, 0, tzinfo=timezone.utc),
    )

    events = service.list_recent_events(project_id="project-1")

    assert [event.event_id for event in events] == ["evt-newest", "evt-older"]


def test_list_recent_events_can_filter_by_run_id(tmp_path: Path) -> None:
    """The scheduler should narrow history to a specific run when requested."""
    service = _build_service(tmp_path)
    _record_event(
        service,
        event_id="evt-run-1-a",
        run_id="run-1",
        project_id="project-1",
        event_type="window_started",
        created_at=datetime(2026, 6, 21, 9, 0, tzinfo=timezone.utc),
    )
    _record_event(
        service,
        event_id="evt-run-2",
        run_id="run-2",
        project_id="project-1",
        event_type="backend_switch",
        created_at=datetime(2026, 6, 21, 10, 0, tzinfo=timezone.utc),
    )
    _record_event(
        service,
        event_id="evt-run-1-b",
        run_id="run-1",
        project_id="project-1",
        event_type="retry_scheduled",
        created_at=datetime(2026, 6, 21, 11, 0, tzinfo=timezone.utc),
    )

    events = service.list_recent_events(project_id="project-1", run_id="run-1")

    assert [event.event_id for event in events] == ["evt-run-1-b", "evt-run-1-a"]
