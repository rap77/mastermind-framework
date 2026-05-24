"""Telemetry repository for project state."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mastermind_cli.project_state.models.token_usage import TokenUsageEvent


@dataclass(slots=True)
class ProviderCostAggregate:
    """Aggregated token and cost values for a provider."""

    provider: str
    total_prompt_tokens: int
    total_completion_tokens: int
    total_estimated_cost: float


@dataclass(slots=True)
class ProjectCostAggregate:
    """Aggregated token and cost values for a project."""

    total_prompt_tokens: int
    total_completion_tokens: int
    total_estimated_cost: float
    providers: list[ProviderCostAggregate]


class TelemetryRepository:
    """Repository for token and cost telemetry."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with an async SQLAlchemy session."""
        self.session = session

    def list_recent_by_project(
        self, project_id: str, limit: int
    ) -> list[TokenUsageEvent]:
        """Return recent token usage events for a project ordered by creation time."""
        result = self.session.execute(
            select(TokenUsageEvent)
            .where(TokenUsageEvent.project_id == project_id)
            .order_by(TokenUsageEvent.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    def get_project_cost_total(self, project_id: str) -> float:
        """Return the total estimated cost for a project."""
        result = self.session.execute(
            select(func.coalesce(func.sum(TokenUsageEvent.estimated_cost), 0.0)).where(
                TokenUsageEvent.project_id == project_id
            )
        )
        value = result.scalar_one()
        return float(value)

    def get_project_cost_aggregate(self, project_id: str) -> ProjectCostAggregate:
        """Return total and per-provider cost aggregation for a project."""
        totals_result = self.session.execute(
            select(
                func.coalesce(func.sum(TokenUsageEvent.prompt_tokens), 0),
                func.coalesce(func.sum(TokenUsageEvent.completion_tokens), 0),
                func.coalesce(func.sum(TokenUsageEvent.estimated_cost), 0.0),
            ).where(TokenUsageEvent.project_id == project_id)
        )
        prompt_tokens, completion_tokens, estimated_cost = totals_result.one()

        providers_result = self.session.execute(
            select(
                TokenUsageEvent.provider,
                func.coalesce(func.sum(TokenUsageEvent.prompt_tokens), 0),
                func.coalesce(func.sum(TokenUsageEvent.completion_tokens), 0),
                func.coalesce(func.sum(TokenUsageEvent.estimated_cost), 0.0),
            )
            .where(TokenUsageEvent.project_id == project_id)
            .group_by(TokenUsageEvent.provider)
            .order_by(TokenUsageEvent.provider.asc())
        )
        providers = [
            ProviderCostAggregate(
                provider=row[0],
                total_prompt_tokens=int(row[1]),
                total_completion_tokens=int(row[2]),
                total_estimated_cost=float(row[3]),
            )
            for row in providers_result.all()
        ]

        return ProjectCostAggregate(
            total_prompt_tokens=int(prompt_tokens),
            total_completion_tokens=int(completion_tokens),
            total_estimated_cost=float(estimated_cost),
            providers=providers,
        )
