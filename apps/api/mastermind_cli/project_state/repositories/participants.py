"""Participants repository for the collaboration-rbac slice."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mastermind_cli.project_state.models.participant import Participant


class ParticipantsRepository:
    """Repository for participant records on a project."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a shared SQLAlchemy session."""
        self.session = session

    def add(
        self,
        project_id: str,
        participant_id: str,
        participant_type: str,
        role: str,
    ) -> Participant:
        """Add a participant to a project and return the new record."""
        participant = Participant(
            project_id=project_id,
            participant_id=participant_id,
            participant_type=participant_type,
            role=role,
        )
        self.session.add(participant)
        self.session.flush()
        return participant

    def list_by_project(self, project_id: str, limit: int = 100) -> list[Participant]:
        """Return all participants for a project ordered by join time."""
        result = self.session.execute(
            select(Participant)
            .where(Participant.project_id == project_id)
            .order_by(Participant.joined_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    def count_by_project(self, project_id: str) -> int:
        """Count all participants for a project."""
        result = self.session.execute(
            select(func.count())
            .select_from(Participant)
            .where(Participant.project_id == project_id)
        )
        return int(result.scalar_one())

    def get(self, project_id: str, participant_id: str) -> Participant | None:
        """Return a participant by project and participant ID, or None."""
        result = self.session.execute(
            select(Participant).where(
                Participant.project_id == project_id,
                Participant.participant_id == participant_id,
            )
        )
        return result.scalar_one_or_none()

    def remove(self, project_id: str, participant_id: str) -> bool:
        """Remove a participant from a project. Returns True if deleted, False if not found."""
        participant = self.get(project_id, participant_id)
        if participant is None:
            return False
        self.session.delete(participant)
        return True
