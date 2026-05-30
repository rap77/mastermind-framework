"""Pydantic schemas for the collaboration-rbac participant endpoints."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ParticipantRole(str, enum.Enum):
    """Valid roles for project participants.

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


class AddParticipantRequest(BaseModel):
    """Request body for adding a participant to a project."""

    participant_id: str
    participant_type: Literal["human", "agent"]
    role: ParticipantRole


class ParticipantResponse(BaseModel):
    """Response schema for a single participant record."""

    model_config = ConfigDict(from_attributes=True)

    project_id: str
    participant_id: str
    participant_type: str
    role: str
    joined_at: datetime


class ParticipantListResponse(BaseModel):
    """Response schema for a list of participants."""

    items: list[ParticipantResponse]
    total: int
