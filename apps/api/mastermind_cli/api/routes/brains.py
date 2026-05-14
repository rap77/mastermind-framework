"""Brains endpoint for Command Center Bento Grid.

This module provides GET /api/brains endpoint that returns all 7 brains
with live metadata from the PostgreSQL brain_registry table.

Phase 08 addition: GET /api/brains/{id}/yaml — returns brain config as YAML
text for the Engine Room config display.

Phase C1: Data source changed from YAML (hardcoded) to brain_registry table.
Fallback to YAML-based registry if PostgreSQL is unavailable.

Real-time status updates use existing WebSocket from Phase 05.

Requirements: BE-01, ER-03, C1.07
"""

import logging
import os
from typing import Annotated

import asyncpg
import yaml
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

from mastermind_cli.api.routes.auth import get_current_user
from mastermind_cli.brain_registry import BRAIN_CONFIGS, get_all_brains
from mastermind_cli.brain_registry_module.repository import BrainRegistryRepository

log = logging.getLogger(__name__)

# Router configuration
router = APIRouter()

_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:devpassword@localhost:5434/mastermind_bd",
)


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


async def _get_brains_from_db(
    page: int, page_size: int
) -> PaginatedBrainsResponse | None:
    """Fetch brains from PostgreSQL brain_registry table.

    Args:
        page: 1-indexed page number.
        page_size: Number of brains per page (max 100).

    Returns:
        PaginatedBrainsResponse populated from brain_registry, or None if
        the table is unreachable (DB down, table missing).
    """
    try:
        conn: asyncpg.Connection = await asyncpg.connect(_DATABASE_URL, timeout=3.0)
        try:
            repo = BrainRegistryRepository(conn)
            all_records = await repo.get_all()
        finally:
            await conn.close()
    except Exception as exc:  # noqa: BLE001
        log.warning(
            "brain_registry unavailable (%s) — falling back to YAML registry", exc
        )
        return None

    # Paginate
    page_size = min(page_size, 100)
    offset = (page - 1) * page_size
    paginated = all_records[offset : offset + page_size]

    brains = [
        BrainMetadata(
            id=f"brain-{r.brain_id:02d}",
            name=r.name,
            niche="software-development",  # brain_registry v1: single niche
            status="idle" if r.enabled else "error",
            uptime=0.0,
            last_called_at=None,
        )
        for r in paginated
    ]

    return PaginatedBrainsResponse(
        brains=brains,
        total=len(all_records),
        page=page,
        page_size=page_size,
    )


def _get_brains_from_yaml(page: int, page_size: int) -> PaginatedBrainsResponse:
    """Fallback: build response from YAML brain registry.

    Args:
        page: 1-indexed page number.
        page_size: Number of brains per page (max 100).

    Returns:
        PaginatedBrainsResponse populated from BRAIN_CONFIGS YAML.
    """
    result = get_all_brains(page=page, page_size=page_size, user_id="system")
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

    Data source: PostgreSQL brain_registry table (Phase C1).
    Fallback: YAML registry if brain_registry is unreachable.

    Args:
        page: Page number (1-indexed, default=1)
        page_size: Number of brains per page (default=24, max=100)
        current_user: User ID from JWT (injected by get_current_user)

    Returns:
        PaginatedBrainsResponse with brains metadata and pagination info

    Security:
        - JWT authentication required (get_current_user)

    Real-time updates:
        Use existing WebSocket from Phase 05 for live status updates.
        This endpoint provides initial state only.
    """
    # Primary: brain_registry table (PostgreSQL)
    db_response = await _get_brains_from_db(page=page, page_size=page_size)
    if db_response is not None:
        return db_response

    # Fallback: YAML-backed registry
    return _get_brains_from_yaml(page=page, page_size=page_size)


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
