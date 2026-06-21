"""Repository for scheduler event audit records."""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from mastermind_cli.window_scheduler.models.scheduler_event import SchedulerEvent


class SchedulerEventsRepository:
    """Persistence access for scheduler event history."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a shared SQLAlchemy session."""
        self.session = session

    def create(self, event: SchedulerEvent) -> SchedulerEvent:
        """Persist a scheduler event."""
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def list_recent(
        self,
        *,
        project_id: str,
        run_id: str | None = None,
        limit: int = 20,
    ) -> list[SchedulerEvent]:
        """Return recent scheduler events for a project, optionally scoped to a run."""
        statement = (
            select(SchedulerEvent)
            .where(SchedulerEvent.project_id == project_id)
            .order_by(desc(SchedulerEvent.created_at), desc(SchedulerEvent.event_id))
            .limit(limit)
        )
        if run_id is not None:
            statement = statement.where(SchedulerEvent.run_id == run_id)
        result = self.session.execute(statement)
        return list(result.scalars().all())
