"""Eligibility and switch-policy helpers for the window scheduler."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from mastermind_cli.window_scheduler.models.availability_state import AvailabilityState
from mastermind_cli.window_scheduler.models.backend_session import BackendSession
from mastermind_cli.window_scheduler.models.run_policy import RunPolicy

_COST_TIER_ORDER = {"low": 0, "medium": 1, "high": 2}


@dataclass(frozen=True)
class EligibleBackend:
    """A backend that satisfies the current policy and availability constraints."""

    backend_id: str
    priority: int
    eligibility_basis: str
    automatic_switch_allowed: bool
    human_confirmation_required: bool


@dataclass(frozen=True)
class SwitchDecision:
    """A switch-policy outcome for the current scheduler step."""

    outcome: str
    selected_backend_id: str | None
    reason: str
    eligibility_basis: str | None
    retry_at: datetime | None = None


def compute_eligible_backends(
    *,
    backends: list[BackendSession],
    availability_by_backend: dict[str, AvailabilityState],
    policy: RunPolicy,
) -> list[EligibleBackend]:
    """Filter backends down to the currently eligible set."""
    max_cost_rank = _cost_rank(policy.max_cost_tier)
    eligible: list[EligibleBackend] = []

    for backend in backends:
        if not backend.enabled:
            continue
        if policy.overnight_mode and not backend.overnight_allowed:
            continue
        if _cost_rank(backend.cost_tier) > max_cost_rank:
            continue

        availability = availability_by_backend.get(backend.backend_id)
        if availability is None or availability.state != "active":
            continue

        eligible.append(
            EligibleBackend(
                backend_id=backend.backend_id,
                priority=backend.priority,
                eligibility_basis=(
                    "enabled + active + within cost/overnight policy constraints"
                ),
                automatic_switch_allowed=backend.automatic_switch_allowed,
                human_confirmation_required=backend.human_confirmation_required,
            )
        )

    eligible.sort(key=lambda candidate: (-candidate.priority, candidate.backend_id))
    return eligible


def plan_switch_decision(
    *,
    current_backend_id: str,
    eligible_backends: list[EligibleBackend],
    policy: RunPolicy,
    switches_used: int,
    task_risk_tier: str | None,
    current_availability: AvailabilityState | None = None,
) -> SwitchDecision:
    """Choose whether to continue, switch, or pause for user input."""
    eligible_by_id = {
        candidate.backend_id: candidate for candidate in eligible_backends
    }
    current = eligible_by_id.get(current_backend_id)
    if current is not None:
        return SwitchDecision(
            outcome="continue",
            selected_backend_id=current.backend_id,
            reason="current backend remains eligible",
            eligibility_basis=current.eligibility_basis,
        )

    if not eligible_backends:
        retry_decision = _plan_retry_decision(
            current_backend_id=current_backend_id,
            current_availability=current_availability,
            policy=policy,
        )
        if retry_decision is not None:
            return retry_decision
        return SwitchDecision(
            outcome="all_backends_blocked",
            selected_backend_id=None,
            reason="no eligible backends available",
            eligibility_basis=None,
        )

    target = eligible_backends[0]
    if switches_used >= policy.max_switches_per_run:
        return SwitchDecision(
            outcome="pause_for_user",
            selected_backend_id=target.backend_id,
            reason="switch budget exhausted",
            eligibility_basis=target.eligibility_basis,
        )
    if task_risk_tier == "high" and policy.require_human_for_high_risk_actions:
        return SwitchDecision(
            outcome="pause_for_user",
            selected_backend_id=target.backend_id,
            reason="high-risk action requires human confirmation",
            eligibility_basis=target.eligibility_basis,
        )
    if target.human_confirmation_required or not target.automatic_switch_allowed:
        return SwitchDecision(
            outcome="pause_for_user",
            selected_backend_id=target.backend_id,
            reason="target backend requires human confirmation",
            eligibility_basis=target.eligibility_basis,
        )

    return SwitchDecision(
        outcome="switch",
        selected_backend_id=target.backend_id,
        reason="current backend is not eligible and a higher-priority backend is ready",
        eligibility_basis=target.eligibility_basis,
    )


def _plan_retry_decision(
    *,
    current_backend_id: str,
    current_availability: AvailabilityState | None,
    policy: RunPolicy,
) -> SwitchDecision | None:
    """Return a retry-or-pause decision when no backend is currently eligible."""
    if current_availability is None or current_availability.estimated_reset_at is None:
        return None

    confidence = current_availability.estimation_confidence or "unknown"
    if confidence == "low" and policy.pause_on_low_confidence_reset:
        return SwitchDecision(
            outcome="pause_for_user",
            selected_backend_id=current_backend_id,
            reason="reset estimate confidence is too low for automatic retry",
            eligibility_basis=None,
            retry_at=None,
        )

    return SwitchDecision(
        outcome="retry_scheduled",
        selected_backend_id=current_backend_id,
        reason="no eligible backend is active, retry when the current backend resets",
        eligibility_basis=None,
        retry_at=_normalize_datetime(current_availability.estimated_reset_at),
    )


def _cost_rank(cost_tier: str) -> int:
    """Return the normalized rank for a cost tier."""
    return _COST_TIER_ORDER.get(cost_tier, len(_COST_TIER_ORDER))


def _normalize_datetime(value: datetime | None) -> datetime | None:
    """Ensure persisted datetimes are timezone-aware in UTC."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
