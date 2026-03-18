"""
Coordinator request and response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone


class CoordinatorRequest(BaseModel):
    """Request model for orchestration."""

    brief: str = Field(..., description="User's brief text", min_length=1)
    flow: Optional[str] = Field(
        None, description="Flow type (discovery, validation_only, etc.)"
    )
    dry_run: bool = Field(False, description="Generate plan without executing")
    output_file: Optional[str] = Field(None, description="Save output to file path")
    max_iterations: int = Field(
        3, description="Maximum iteration attempts", ge=1, le=10
    )
    use_mcp: bool = Field(False, description="Use MCP for real NotebookLM calls")


class CoordinatorResponse(BaseModel):
    """Response model for orchestration results."""

    status: str = Field(
        ..., description="Execution status: success, error, dry_run_complete"
    )
    plan: Optional[Dict[str, Any]] = Field(None, description="Generated execution plan")
    results: Optional[Dict[str, Any]] = Field(
        None, description="Execution results by brain"
    )
    output: Optional[str] = Field(None, description="Formatted output text")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response timestamp",
    )
    iterations: int = Field(0, description="Number of iterations performed")
