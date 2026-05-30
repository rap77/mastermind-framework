"""Telemetry repository for project state."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

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


@dataclass(slots=True)
class ProjectQualityAggregate:
    """Aggregated quality signal and cost values for a project."""

    total_events: int
    review_pass_count: int
    review_fail_count: int
    review_pass_rate: float | None
    verification_pass_count: int
    verification_fail_count: int
    verification_pass_rate: float | None
    avg_rework_count: float | None
    total_estimated_cost: float
    cost_per_reviewed_event: float | None


class TelemetryRepository:
    """Repository for token and cost telemetry."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with an async SQLAlchemy session."""
        self.session = session

    def create_event(
        self,
        usage_event_id: str,
        project_id: str,
        task_id: str | None,
        model: str,
        provider: str,
        auth_mode: str,
        prompt_tokens: int,
        completion_tokens: int,
        estimated_cost: float,
        run_id: str | None = None,
        metadata_json: dict[str, object] | None = None,
    ) -> TokenUsageEvent:
        """Persist a new token usage event and return it."""
        event = TokenUsageEvent(
            usage_event_id=usage_event_id,
            project_id=project_id,
            task_id=task_id,
            run_id=run_id,
            provider=provider,
            model=model,
            auth_mode=auth_mode,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            estimated_cost=estimated_cost,
            metadata_json=metadata_json or {},
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

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

    def get_project_quality_aggregate(self, project_id: str) -> ProjectQualityAggregate:
        """Return quality signal aggregates for a project by scanning metadata_json."""
        result = self.session.execute(
            select(TokenUsageEvent)
            .where(TokenUsageEvent.project_id == project_id)
            .order_by(TokenUsageEvent.created_at.desc())
        )
        events = list(result.scalars().all())

        total_events = len(events)
        total_estimated_cost = sum(e.estimated_cost for e in events)

        review_pass_count = 0
        review_fail_count = 0
        verification_pass_count = 0
        verification_fail_count = 0
        rework_values: list[int] = []

        for event in events:
            meta = event.metadata_json if isinstance(event.metadata_json, dict) else {}
            review_pass = meta.get("review_pass")
            if review_pass is True:
                review_pass_count += 1
            elif review_pass is False:
                review_fail_count += 1

            verification_pass = meta.get("verification_pass")
            if verification_pass is True:
                verification_pass_count += 1
            elif verification_pass is False:
                verification_fail_count += 1

            rework_count = meta.get("rework_count")
            if isinstance(rework_count, int) and not isinstance(rework_count, bool):
                rework_values.append(rework_count)

        reviewed_count = review_pass_count + review_fail_count
        review_pass_rate: float | None = None
        if reviewed_count > 0:
            review_pass_rate = round(review_pass_count / reviewed_count, 3)

        verified_count = verification_pass_count + verification_fail_count
        verification_pass_rate: float | None = None
        if verified_count > 0:
            verification_pass_rate = round(verification_pass_count / verified_count, 3)

        avg_rework_count: float | None = None
        if rework_values:
            avg_rework_count = round(sum(rework_values) / len(rework_values), 3)

        cost_per_reviewed_event: float | None = None
        if reviewed_count > 0:
            cost_per_reviewed_event = round(total_estimated_cost / reviewed_count, 3)

        return ProjectQualityAggregate(
            total_events=total_events,
            review_pass_count=review_pass_count,
            review_fail_count=review_fail_count,
            review_pass_rate=review_pass_rate,
            verification_pass_count=verification_pass_count,
            verification_fail_count=verification_fail_count,
            verification_pass_rate=verification_pass_rate,
            avg_rework_count=avg_rework_count,
            total_estimated_cost=total_estimated_cost,
            cost_per_reviewed_event=cost_per_reviewed_event,
        )
