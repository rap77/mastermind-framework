"""Repository for scheduler event audit records."""

from __future__ import annotations

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
