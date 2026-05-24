"""Decision repository for project state."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from mastermind_cli.project_state.models.decision import DecisionRecord


class DecisionsRepository:
    """Repository for decision records."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with an async SQLAlchemy session."""
        self.session = session

    def get_by_id(self, project_id: str, decision_id: str) -> DecisionRecord | None:
        """Return a decision by project and decision ID, or None if missing."""
        result = self.session.execute(
            select(DecisionRecord).where(
                DecisionRecord.project_id == project_id,
                DecisionRecord.decision_id == decision_id,
            )
        )
        return result.scalar_one_or_none()

    def list_recent_by_task(
        self, project_id: str, task_id: str, limit: int
    ) -> list[DecisionRecord]:
        """Return recent decisions scoped to a task ordered by creation time."""
        result = self.session.execute(
            select(DecisionRecord)
            .where(
                DecisionRecord.project_id == project_id,
                DecisionRecord.task_id == task_id,
            )
            .order_by(desc(DecisionRecord.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    def list_recent_by_project(
        self, project_id: str, limit: int
    ) -> list[DecisionRecord]:
        """Return recent decisions for a project ordered by creation time."""
        result = self.session.execute(
            select(DecisionRecord)
            .where(DecisionRecord.project_id == project_id)
            .order_by(desc(DecisionRecord.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    def get_latest_by_project(self, project_id: str) -> DecisionRecord | None:
        """Return the most recent decision for a project, if any."""
        result = self.session.execute(
            select(DecisionRecord)
            .where(DecisionRecord.project_id == project_id)
            .order_by(desc(DecisionRecord.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    def create_decision(
        self,
        decision_id: str,
        project_id: str,
        task_id: str | None,
        title: str,
        status: str,
        rationale_markdown: str,
        metadata_json: dict[str, object],
        created_at: datetime,
    ) -> DecisionRecord:
        """Create and persist a new decision record."""
        decision = DecisionRecord(
            decision_id=decision_id,
            project_id=project_id,
            task_id=task_id,
            title=title,
            status=status,
            rationale_markdown=rationale_markdown,
            metadata_json=metadata_json,
            created_at=created_at,
        )
        self.session.add(decision)
        self.session.commit()
        self.session.refresh(decision)
        return decision
