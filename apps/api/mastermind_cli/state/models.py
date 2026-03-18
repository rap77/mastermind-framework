"""
Pydantic models for task state persistence.

This module provides TaskRecord model for mapping SQLite rows
to Python objects with validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from typing import Optional


class TaskRecord(BaseModel):
    """Task state record for SQLite persistence.

    This model represents a task in the database with all execution
    state including status, progress, result, and error information.

    Attributes:
        id: Unique task identifier
        brain_id: Brain being executed
        status: Task state (pending, running, completed, failed, cancelled, killed)
        progress: JSON progress data (optional)
        result: JSON result data (optional)
        error: Error message if failed (optional)
        created_at: Task creation timestamp
        updated_at: Last update timestamp
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique task ID")
    brain_id: str = Field(..., description="Brain being executed")
    status: str = Field(..., description="Task state")
    progress: Optional[str] = Field(None, description="JSON progress data")
    result: Optional[str] = Field(None, description="JSON result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
