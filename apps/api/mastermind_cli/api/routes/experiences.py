"""Experience records REST endpoint.

Exposes accumulated brain memory for the Strategy Vault / Engine Room frontend.

IDOR decision: Option A — shared system telemetry. experience_records is not user-scoped.
Any authenticated user can read any brain's execution history. This is intentional
for a single-user internal tool. See agent-restructuring plan, Fase 2 notes.

Endpoints:
    GET /api/experiences/{brain_id}  - Recent experience records for a brain
"""

from typing import Any

from fastapi import APIRouter, Depends, Query

from mastermind_cli.api.dependencies import get_db_path
from mastermind_cli.api.routes.auth import get_current_user_any
from mastermind_cli.experience.logger import ExperienceLogger
from mastermind_cli.state.database import DatabaseConnection

router = APIRouter()

_DEFAULT_LIMIT = 10
_MAX_LIMIT = 100


@router.get("/{brain_id}")
async def get_brain_experiences(
    brain_id: str,
    limit: int = Query(default=_DEFAULT_LIMIT, ge=1, le=_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> list[dict[str, Any]]:
    """Get recent experience records for a brain.

    Returns execution history accumulated by the brain agent — used by the War Room
    to surface what each brain has learned over time.

    Args:
        brain_id: Brain identifier (e.g. 'brain-01-product')
        limit: Max records to return (default 10, max 100)
        offset: Skip N records for pagination (default 0)

    Returns:
        List of experience record dicts, ordered newest first.
        Empty list if brain has no records.
    """
    async with DatabaseConnection(db_path) as db:
        await db.create_experience_schema()
        logger = ExperienceLogger(db)
        records = await logger.get_recent_by_brain(brain_id, limit=limit + offset)

    # Apply offset in Python — get_recent_by_brain uses LIMIT only
    paged = records[offset : offset + limit]

    return [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "status": r.status,
            "duration_ms": r.duration_ms,
            "output_json": r.output_json,
            "custom_metadata": r.custom_metadata,
        }
        for r in paged
    ]
