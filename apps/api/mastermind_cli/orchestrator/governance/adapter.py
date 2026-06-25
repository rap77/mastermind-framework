"""Coordinator adapter that gates execution through governance."""

from __future__ import annotations

from typing import Any, Protocol

from .models import Intention, TaskContext
from .interceptor import GovernanceInterceptor


class Orchestrator(Protocol):
    """Protocol for coordinator-like objects."""

    def orchestrate(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Execute the requested orchestration."""
        ...


class CoordinatorAdapter:
    """Wrap a coordinator and optionally gate it with governance."""

    def __init__(
        self,
        coordinator: Orchestrator,
        governance: GovernanceInterceptor | None = None,
    ) -> None:
        """Store coordinator and optional governance interceptor."""
        self._coordinator = coordinator
        self._governance = governance

    def orchestrate(
        self,
        intention: Intention,
        context: TaskContext,
        /,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Evaluate governance before delegating to the wrapped coordinator."""
        if self._governance is None:
            return self._coordinator.orchestrate(*args, **kwargs)

        decision = self._governance.evaluate(intention, context)
        if decision.final_verdict.value != "allow":
            return {
                "status": "blocked",
                "verdict": decision.final_verdict.value,
                "policy": decision.triggering_policy,
                "audit_event_ref": decision.audit_event_ref,
                "next_action": decision.next_action,
            }

        return self._coordinator.orchestrate(*args, **kwargs)
