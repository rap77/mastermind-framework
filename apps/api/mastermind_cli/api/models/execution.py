"""Pydantic schemas for execution history.

Provides response models for Strategy Vault:
- SnapshotMilestone: Point-in-time snapshot during execution
- BrainOutput: Per-brain output with Markdown content
- ExecutionSummary: Lightweight summary for list views
- Execution: Full execution record with all brain outputs

Requirements: SV-01, SV-02
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SnapshotMilestone(BaseModel):
    """Point-in-time milestone captured during task execution.

    Attributes:
        index: Position in milestone array (0-based)
        timestamp: Unix milliseconds when milestone was captured
        label: Human-readable label (e.g., "Brain #1 complete")
        brain_count: Number of brains active at this milestone
    """

    index: int = Field(..., ge=0, description="Position in milestone array (0-based)")
    timestamp: int = Field(..., ge=0, description="Unix milliseconds")
    label: str = Field(..., min_length=1, max_length=200, description="Milestone label")
    brain_count: int = Field(..., ge=0, description="Active brains at milestone")


class BrainOutput(BaseModel):
    """Per-brain execution output.

    Attributes:
        brain_id: Brain identifier (e.g., "brain-01")
        status: Final status of this brain execution
        output: Markdown-formatted brain output
        duration_ms: Execution time in milliseconds
        timestamp: Start time in Unix milliseconds
    """

    brain_id: str = Field(..., min_length=1, description="Brain identifier")
    status: str = Field(
        ...,
        description="Execution status: idle, running, complete, error",
    )
    output: str = Field(default="", description="Markdown-formatted brain output")
    duration_ms: int = Field(default=0, ge=0, description="Execution time in ms")
    timestamp: int = Field(default=0, ge=0, description="Start time in Unix ms")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of allowed values."""
        allowed = {"idle", "running", "complete", "error"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}, got '{v}'")
        return v


class ExecutionSummary(BaseModel):
    """Lightweight execution summary for list views.

    Used in GET /api/executions/history responses.

    Attributes:
        id: UUID primary key
        task_id: FK to parent task (executions table)
        brief: First 100 chars of brief text
        status: Overall execution status
        duration_ms: Total execution time
        brain_count: Number of brains that participated
        created_at: ISO timestamp
    """

    id: str = Field(..., description="UUID primary key")
    task_id: str = Field(..., description="FK to parent task")
    brief: str = Field(..., max_length=200, description="Brief preview (100 chars)")
    status: str = Field(..., description="success, error, running")
    duration_ms: int = Field(default=0, ge=0, description="Total execution time in ms")
    brain_count: int = Field(
        default=0, ge=0, description="Number of brains participated"
    )
    created_at: datetime = Field(..., description="ISO timestamp")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value."""
        allowed = {"success", "error", "running"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}, got '{v}'")
        return v


class Execution(BaseModel):
    """Full execution record with all brain outputs.

    Used in GET /api/executions/{id} response.

    Attributes:
        id: UUID primary key
        task_id: FK to parent task
        brief: First 100 chars of brief text
        status: success/error/running
        duration_ms: Total execution time
        brain_count: Number of brains that participated
        created_at: ISO timestamp
        milestones: Timeline snapshots (max 10)
        brain_outputs: Per-brain outputs keyed by brain_id
        graph_snapshot: Final DAG state for replay
    """

    id: str = Field(..., description="UUID primary key")
    task_id: str = Field(..., description="FK to parent task")
    brief: str = Field(..., max_length=200, description="Brief preview")
    status: str = Field(..., description="success, error, running")
    duration_ms: int = Field(default=0, ge=0)
    brain_count: int = Field(default=1, ge=1)
    created_at: datetime = Field(..., description="ISO timestamp")
    milestones: list[SnapshotMilestone] = Field(
        default_factory=list,
        description="Timeline snapshots (max 10)",
    )
    brain_outputs: dict[str, BrainOutput] = Field(
        default_factory=dict,
        description="Per-brain outputs keyed by brain_id",
    )
    graph_snapshot: dict[str, object] = Field(
        default_factory=dict,
        description="Final DAG state for replay",
    )

    @field_validator("milestones")
    @classmethod
    def validate_milestones_length(
        cls, v: list[SnapshotMilestone]
    ) -> list[SnapshotMilestone]:
        """Enforce max 10 milestones."""
        if len(v) > 10:
            raise ValueError(f"milestones must have at most 10 items, got {len(v)}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value."""
        allowed = {"success", "error", "running"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}, got '{v}'")
        return v


class ExecutionHistoryResponse(BaseModel):
    """Paginated execution history response.

    Used in GET /api/executions/history.
    """

    executions: list[ExecutionSummary] = Field(default_factory=list)
    next_cursor: Optional[str] = Field(
        default=None, description="Base64 cursor for next page"
    )
    has_more: bool = Field(default=False)
