"""Execution history REST endpoints for Strategy Vault."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from mastermind_cli.api.dependencies import get_db_path, get_project_state_db_url
from mastermind_cli.api.models.execution import Execution, ExecutionHistoryResponse
from mastermind_cli.api.routes.auth import get_current_user_any
from mastermind_cli.api.services.execution_projection import (
    get_execution_detail_projection,
    get_execution_history_projection,
)

router = APIRouter()

_DEFAULT_LIMIT = 10
_MAX_LIMIT = 20


@router.get("/history", response_model=ExecutionHistoryResponse)
async def get_execution_history(
    cursor: Optional[str] = Query(
        default=None,
        description="Base64-encoded execution ID for cursor pagination (null = from newest)",
    ),
    limit: int = Query(
        default=_DEFAULT_LIMIT,
        ge=1,
        le=_MAX_LIMIT,
        description=f"Page size (default={_DEFAULT_LIMIT}, max={_MAX_LIMIT})",
    ),
    sort: str = Query(
        default="newest",
        description="Sort order: 'newest' (default) or 'oldest'",
    ),
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
    database_url: str = Depends(get_project_state_db_url),
) -> ExecutionHistoryResponse:
    """Get paginated execution history."""
    return await get_execution_history_projection(
        database_url=database_url,
        db_path=db_path,
        user_id=user_id,
        cursor=cursor,
        limit=limit,
        sort=sort,
    )


@router.get("/{execution_id}", response_model=Execution)
async def get_execution_detail(
    execution_id: str,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
    database_url: str = Depends(get_project_state_db_url),
) -> Execution:
    """Get full execution detail with brain outputs."""
    try:
        return await get_execution_detail_projection(
            database_url=database_url,
            db_path=db_path,
            user_id=user_id,
            execution_id=execution_id,
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Execution not found")
