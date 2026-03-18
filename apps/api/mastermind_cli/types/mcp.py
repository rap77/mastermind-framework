"""
MCP (NotebookLM) request and response models.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any


class MCPRequest(BaseModel):
    """Request model for MCP tool calls."""

    brain_id: str = Field(..., description="Brain identifier to query")
    query: str = Field(
        ..., description="Query text to send to NotebookLM", min_length=1
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Additional context for the query"
    )
    timeout: int = Field(30, description="Timeout in seconds", ge=5, le=300)


class MCPResponse(BaseModel):
    """Response model for MCP tool results with evolutivo approach."""

    model_config = ConfigDict(extra="allow")  # Preserve unknown fields per CONTEXT.md

    brain_id: str = Field(..., description="Brain identifier that was queried")
    response: str = Field(..., description="Raw response text from NotebookLM")
    success: bool = Field(..., description="Whether the call succeeded")
    error: Optional[str] = Field(None, description="Error message if success=False")
    timestamp: Optional[str] = Field(
        None, description="Response timestamp from NotebookLM"
    )
