"""Governance interceptor for deterministic pre-execution enforcement."""

from __future__ import annotations

import logging

from .models import (
    AuditEvent,
    GovernanceDecision,
    Intention,
    PolicyVerdict,
    TaskContext,
)
from .policies import AuditWriter, GovernancePolicy


logger = logging.getLogger(__name__)


class GovernanceInterceptor:
    """Evaluate policies before work is delegated to a coordinator."""

    def __init__(
        self,
        policies: list[GovernancePolicy],
        audit_writer: AuditWriter,
    ) -> None:
        """Store immutable policy chain and audit writer."""
        self._policies = policies
        self._audit_writer = audit_writer

    def evaluate(
        self, intention: Intention, context: TaskContext
    ) -> GovernanceDecision:
        """Run governance evaluation and persist an audit event."""
        final_result = None
        for policy in self._policies:
            result = policy.evaluate(intention, context)
            final_result = result
            if result.verdict is not PolicyVerdict.ALLOW:
                break

        if final_result is None:
            raise ValueError("GovernanceInterceptor requires at least one policy")

        event = AuditEvent(
            session_id=context.session_id,
            task_id=context.task_id,
            intention_snapshot=intention,
            policy_name=final_result.policy_name,
            verdict=final_result.verdict,
            reason_code=final_result.reason_code,
            reason_text=final_result.human_reason,
        )

        try:
            audit_ref = self._audit_writer.append(event)
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            logger.warning(
                "governance audit write failed for task_id=%s session_id=%s: %s",
                context.task_id,
                context.session_id,
                exc,
                exc_info=True,
            )
            return GovernanceDecision(
                final_verdict=PolicyVerdict.DENY,
                triggering_policy="AuditWriter",
                audit_event_ref="",
                next_action="do_not_delegate",
            )

        if final_result.verdict is PolicyVerdict.ALLOW:
            return GovernanceDecision(
                final_verdict=PolicyVerdict.ALLOW,
                triggering_policy="allow",
                audit_event_ref=audit_ref,
                next_action="delegate",
            )

        return GovernanceDecision(
            final_verdict=final_result.verdict,
            triggering_policy=final_result.policy_name,
            audit_event_ref=audit_ref,
            next_action="request_approval"
            if final_result.verdict is PolicyVerdict.PAUSE_AND_ASK
            else "do_not_delegate",
        )
