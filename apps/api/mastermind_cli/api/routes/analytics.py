"""
Analytics API endpoints for dashboard metrics.

Exposes system health and outcome metrics for monitoring brain learning progress.
"""

from fastapi import APIRouter, Depends

from mastermind_cli.api.dependencies import get_db_path
from mastermind_cli.orchestration.analytics_service import (
    AnalyticsService,
    OutcomeMetrics,
    SystemHealthMetrics,
)
from mastermind_cli.state.database import DatabaseConnection
from typing import Dict, List, Any, Optional

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/system-health", response_model=SystemHealthMetrics)
async def get_system_health(
    db_path: str = Depends(get_db_path),
) -> SystemHealthMetrics:
    """Get system health metrics for dashboard monitoring.

    Returns:
        - record_count: Total non-expired records (unbounded growth detection)
        - avg_quality_score: Avg quality across all records (drift detection)
        - rejection_rate: % of rejected records (brain degradation)
        - p50_latency_ms: Median retrieval latency (ceiling detection)
        - p90_latency_ms: P90 retrieval latency (ceiling detection)
        - t1_trend: T1 over last 7 days (learning validation)
    """
    async with DatabaseConnection(db_path) as db:
        await db.create_experience_schema()
        service = AnalyticsService(db)
        return await service.get_system_health()


@router.get("/templates")
async def get_templates(
    brain_id: Optional[str] = None,
    limit: int = 20,
    min_success_rate: float = 0.5,
    db_path: str = Depends(get_db_path),
) -> List[Dict[str, Any]]:
    """Get templates with success rate tracking.

    Args:
        brain_id: Filter by brain (optional)
        limit: Max templates to return (default 20)
        min_success_rate: Minimum success rate threshold (default 0.5)

    Returns:
        Templates ordered by success_rate DESC (best first)
    """
    async with DatabaseConnection(db_path) as db:
        await db.create_experience_schema()
        service = AnalyticsService(db)
        return await service.get_templates(brain_id, limit, min_success_rate)


@router.get("/patterns")
async def get_patterns(
    brain_id: Optional[str] = None,
    limit: int = 10,
    db_path: str = Depends(get_db_path),
) -> Dict[str, List[Dict[str, Any]]]:
    """Get recurring patterns per brain.

    Groups experience_records by brain_id + brief similarity (input_hash).
    Shows which brief patterns recur most frequently.

    Args:
        brain_id: Filter by brain (optional)
        limit: Max patterns per brain (default 10)

    Returns:
        Dict mapping brain_id → list of patterns with frequency + avg_quality
    """
    async with DatabaseConnection(db_path) as db:
        await db.create_experience_schema()
        service = AnalyticsService(db)
        return await service.get_patterns(brain_id, limit)


@router.get("/outcome-metrics", response_model=OutcomeMetrics)
async def get_outcome_metrics(
    db_path: str = Depends(get_db_path),
) -> OutcomeMetrics:
    """Get outcome metrics for learning validation.

    Returns:
        - delta_velocity: T1 improvement (first - second consultation)
        - knowledge_yield: Template reuse rate (templates / total_records)
        - planning_accuracy: Avg quality_score across all records
    """
    async with DatabaseConnection(db_path) as db:
        await db.create_experience_schema()
        service = AnalyticsService(db)
        return await service.get_outcome_metrics()
