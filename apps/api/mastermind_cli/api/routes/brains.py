"""Brains endpoint for Command Center Bento Grid.

This module provides GET /api/brains endpoint that returns all 24 brains
with live metadata (name, niche, status, uptime, last_called_at) for the
Command Center visualization.

Phase 08 addition: GET /api/brains/{id}/yaml — returns brain config as YAML
text for the Engine Room config display.

Real-time status updates use existing WebSocket from Phase 05.

Requirements: BE-01, ER-03
"""

from typing import Annotated

import yaml
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

from mastermind_cli.api.routes.auth import get_current_user
from mastermind_cli.brain_registry import BRAIN_CONFIGS, get_all_brains

# Router configuration
router = APIRouter()


# Pydantic models for response
class BrainMetadata(BaseModel):
    """Brain metadata for Command Center."""

    id: str = Field(..., description="Brain ID (e.g. 'brain-01')")
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


@router.get("/brains/{brain_id}/yaml", response_class=Response)
async def get_brain_yaml(
    brain_id: str,
    current_user: str = Depends(get_current_user),
) -> Response:
    """Get brain configuration as YAML text.

    Returns the brain's full metadata as YAML for the Engine Room
    config display panel. Content-Type: text/plain.

    Args:
        brain_id: Brain identifier (e.g., "brain-01", "1", "9")
        current_user: JWT user_id (required)

    Returns:
        YAML-formatted brain config as plain text

    Raises:
        404: If brain not found in registry

    Cache:
        Brain config rarely changes — consumers may cache for 1 hour.

    Requirements: ER-03
    """
    # Normalize brain_id to numeric key
    numeric_id: int | None = None

    # Try "brain-01" format
    if brain_id.startswith("brain-"):
        try:
            numeric_id = int(brain_id[6:])
        except ValueError:
            pass

    # Try plain numeric "1" or "01" format
    if numeric_id is None:
        try:
            numeric_id = int(brain_id)
        except ValueError:
            pass

    brain_config = BRAIN_CONFIGS.get(numeric_id) if numeric_id is not None else None

    if brain_config is None:
        # Try string-based lookup by name (fallback)
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Brain '{brain_id}' not found")

    # Build YAML-friendly dict
    yaml_data = {
        "brain_id": f"brain-{numeric_id:02d}",
        "name": brain_config.get("name", "Unknown"),
        "niche": brain_config.get("niche", "software-development"),
        "skills": brain_config.get("skills", []),
        "description": brain_config.get("description", ""),
        "expertise_level": brain_config.get("expertise_level", "advanced"),
        "version": brain_config.get("version", "v1.0"),
        "status": brain_config.get("status", "idle"),
    }

    yaml_content = "---\n" + yaml.dump(
        yaml_data,
        default_flow_style=False,
        allow_unicode=True,
        indent=2,
        sort_keys=True,
    )

    return Response(
        content=yaml_content,
        media_type="text/plain",
        headers={"Cache-Control": "max-age=3600"},
    )
