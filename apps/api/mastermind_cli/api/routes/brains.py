"""Brains endpoint for Command Center Bento Grid.

This module provides GET /api/brains endpoint that returns all 24 brains
with live metadata (name, niche, status, uptime, last_called_at) for the
Command Center visualization.

Real-time status updates use existing WebSocket from Phase 05.

Requirements: BE-01
"""

from typing import Annotated
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from mastermind_cli.brain_registry import get_all_brains
from mastermind_cli.api.routes.auth import get_current_user

# Router configuration
router = APIRouter()


# Pydantic models for response
class BrainMetadata(BaseModel):
    """Brain metadata for Command Center."""

    id: int = Field(..., description="Brain ID")
    name: str = Field(..., description="Brain name")
    niche: str = Field(
        ..., description="Niche: software-development, marketing-digital, universal"
    )
    status: str = Field(..., description="Status: idle, active, error, complete")
    uptime: float = Field(..., description="Uptime in seconds (0 if not tracked)")
    last_called_at: str | None = Field(None, description="ISO datetime of last call")


class PaginatedBrainsResponse(BaseModel):
    """Paginated brains response."""

    brains: list[BrainMetadata] = Field(
        ..., description="List of brains for current page"
    )
    total: int = Field(..., description="Total number of brains")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of brains per page")


@router.get("/brains", response_model=PaginatedBrainsResponse)
async def get_brains_endpoint(
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=100, description="Number of brains per page (max 100)")
    ] = 24,
    current_user: str = Depends(get_current_user),
) -> PaginatedBrainsResponse:
    """
    Get all brains with pagination for Command Center.

    Args:
        page: Page number (1-indexed, default=1)
        page_size: Number of brains per page (default=24, max=100)
        current_user: User ID from JWT (injected by get_current_user)

    Returns:
        PaginatedBrainsResponse with brains metadata and pagination info

    Security:
        - JWT authentication required (get_current_user)
        - IDOR protection: current_user.id passed to get_all_brains()
        - In v2.1, all users see same 24 brains (single-tenant)

    Real-time updates:
        Use existing WebSocket from Phase 05 for live status updates.
        This endpoint provides initial state only.
    """
    # get_current_user validates JWT and returns user_id (str)
    # For v2.1 single-tenant, all users see same brains
    result = get_all_brains(page=page, page_size=page_size, user_id=current_user)

    # Transform to Pydantic models
    brains = [
        BrainMetadata(
            id=b["id"],
            name=b["name"],
            niche=b["niche"],
            status=b["status"],
            uptime=b["uptime"],
            last_called_at=b["last_called_at"],
        )
        for b in result["brains"]
    ]

    return PaginatedBrainsResponse(
        brains=brains,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )
