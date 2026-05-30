"""Participant model for the collaboration-rbac slice."""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.project_state.database.base import Base


class ParticipantRole(str, enum.Enum):
    """Roles a participant can hold on a project.

    Human roles: owner, architect, implementer, reviewer, approver, observer.
    Agent roles: planner, executor, critic, evaluator, synthesizer.
    """

    # Human roles
    owner = "owner"
    architect = "architect"
    implementer = "implementer"
    reviewer = "reviewer"
    approver = "approver"
    observer = "observer"
    # Agent roles
    planner = "planner"
    executor = "executor"
    critic = "critic"
    evaluator = "evaluator"
    synthesizer = "synthesizer"


class Participant(Base):
    """Participant record linking a human or agent to a project with an explicit role."""

    __tablename__ = "ps_participants"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("ps_projects.project_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    participant_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        nullable=False,
    )
    participant_type: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
