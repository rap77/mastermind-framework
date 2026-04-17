"""Cost Metrics API Router.

This module provides endpoints for querying brain cost metrics from PostgreSQL.
All metrics are sourced from cost_metrics_mv materialized view for performance.

Performance SLA: P50 < 10ms, P99 < 50ms (indexed MV queries)
"""

from __future__ import annotations

from typing import Any

import asyncpg
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from mastermind_cli.api.config import get_settings

# ===== ROUTER =====

router = APIRouter(prefix="/api/costs", tags=["costs"])

# ===== DATABASE CONFIG =====

settings = get_settings()
POSTGRES_DSN = settings.postgres_dsn

# ===== MODELS =====


class BrainCostMetric(BaseModel):
    """Brain cost metric model."""

    brain_id: str = Field(..., description="Brain identifier")
    total_requests: int = Field(..., description="Total number of requests")
    completed_requests: int = Field(..., description="Number of completed requests")
    failed_requests: int = Field(..., description="Number of failed requests")
    success_rate: float = Field(..., description="Success rate (0.0 to 1.0)")
    last_activity_at: str | None = Field(
        None, description="Last activity timestamp (ISO 8601)"
    )


# ===== ENDPOINTS =====


@router.get("/brains", response_model=list[BrainCostMetric])
async def get_brain_costs() -> list[BrainCostMetric]:
    """Get cost metrics for all brains.

    Queries cost_metrics_mv materialized view for aggregated metrics.
    Results are ordered by success_rate DESC (best performers first).

    Performance:
    - P50 < 10ms (indexed query on MV)
    - P99 < 50ms (concurrent refresh doesn't block reads)

    Returns:
        List of brain cost metrics, one per brain with activity.
        Empty list if no metrics available.

    Raises:
        HTTPException 503: If PostgreSQL connection fails
    """
    try:
        conn = await asyncpg.connect(POSTGRES_DSN)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {e!s}",
        ) from e

    try:
        # Query MV with ORDER BY success_rate DESC (uses index)
        query = """
            SELECT
                brain_id,
                total_requests,
                completed_requests,
                failed_requests,
                success_rate,
                last_activity_at
            FROM cost_metrics_mv
            ORDER BY success_rate DESC
        """

        rows = await conn.fetch(query)

        # Convert to Pydantic models
        metrics = [
            BrainCostMetric(
                brain_id=row["brain_id"],
                total_requests=row["total_requests"],
                completed_requests=row["completed_requests"],
                failed_requests=row["failed_requests"],
                success_rate=row["success_rate"],
                last_activity_at=row["last_activity_at"].isoformat()
                if row["last_activity_at"]
                else None,
            )
            for row in rows
        ]

        return metrics

    finally:
        await conn.close()


@router.post("/refresh")
async def refresh_cost_metrics() -> dict[str, str]:
    """Trigger manual refresh of cost_metrics_mv.

    Calls REFRESH MATERIALIZED VIEW CONCURRENTLY to update metrics
    without blocking reads. Normally called by cron job every 5 minutes.

    Returns:
        Confirmation message with refresh status.

    Raises:
        HTTPException 500: If refresh command fails
    """
    try:
        conn = await asyncpg.connect(POSTGRES_DSN)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {e!s}",
        ) from e

    try:
        await conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY cost_metrics_mv")
        return {"status": "success", "message": "Cost metrics refreshed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Refresh failed: {e!s}",
        ) from e
    finally:
        await conn.close()


@router.get("/health")
async def cost_metrics_health() -> dict[str, Any]:
    """Health check for cost metrics system.

    Returns:
        Health status including MV existence and row count.
    """
    try:
        conn = await asyncpg.connect(POSTGRES_DSN)
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }

    try:
        # Check MV exists and get row count
        result = await conn.fetchval("""
            SELECT COUNT(*) FROM cost_metrics_mv
        """)

        return {
            "status": "healthy",
            "database": "connected",
            "mv_rows": result,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e),
        }
    finally:
        await conn.close()
