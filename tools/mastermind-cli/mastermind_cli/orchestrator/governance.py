"""Governance boundary for deterministic policy evaluation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Protocol, Sequence


class PolicyVerdict(str, Enum):
    """Possible governance policy verdicts."""

    ALLOW = "allow"
    DENY = "deny"
    PAUSE_AND_ASK = "pause_and_ask"


@dataclass(frozen=True, slots=True)
class Intention:
    """Structured description of the action to be governed."""

    action: str
    target: str
    scope: str
    estimated_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TaskContext:
    """Execution context associated with an intention."""

    brief: str
    flow_type: str | None = None
    plan_id: str | None = None
    task_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Append-only governance event."""

    timestamp: str
    intention: Intention
    verdict: PolicyVerdict
    source: str
    policy: str | None = None
    context: TaskContext | None = None
    details: dict[str, Any] = field(default_factory=dict)


class Policy(Protocol):
    """Protocol for deterministic governance policies."""

    name: str

    def check(self, intention: Intention, context: TaskContext) -> PolicyVerdict:
        """Return the policy verdict for the given intention."""


class EvidenceChainWriter:
    """Append-only JSONL writer for governance evidence."""

    def __init__(self, filepath: str | Path) -> None:
        """Create a writer for the given path."""
        self.filepath = Path(filepath)

    def append_event(self, event: AuditEvent) -> None:
        """Append one structured event as JSON Lines."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with self.filepath.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(self._to_jsonable(event), ensure_ascii=False))
            handle.write("\n")

    def load_session_events(self) -> list[AuditEvent]:
        """Load all events from the JSONL file."""
        if not self.filepath.exists():
            return []

        events: list[AuditEvent] = []
        for line in self.filepath.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            events.append(self._from_dict(json.loads(line)))
        return events

    def _to_jsonable(self, value: Any) -> Any:
        """Convert dataclasses and enums into JSON serializable values."""
        if isinstance(value, Enum):
            return value.value
        if is_dataclass(value):
            return {key: self._to_jsonable(item) for key, item in asdict(value).items()}
        if isinstance(value, dict):
            return {key: self._to_jsonable(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._to_jsonable(item) for item in value]
        return value

    def _from_dict(self, payload: dict[str, Any]) -> AuditEvent:
        """Rebuild an audit event from a JSON object."""
        intention = Intention(**payload["intention"])
        context_payload = payload.get("context")
        context = TaskContext(**context_payload) if context_payload else None
        return AuditEvent(
            timestamp=payload["timestamp"],
            intention=intention,
            verdict=PolicyVerdict(payload["verdict"]),
            source=payload["source"],
            policy=payload.get("policy"),
            context=context,
            details=payload.get("details", {}),
        )


class GovernanceInterceptor:
    """Deterministic policy chain that audits every decision."""

    def __init__(
        self,
        policies: Sequence[Policy] | None = None,
        evidence_writer: EvidenceChainWriter | None = None,
    ) -> None:
        """Initialize the interceptor."""
        self.policies = list(policies or [])
        self.evidence_writer = evidence_writer or EvidenceChainWriter(
            Path(".mm-flow") / "planning" / "audit" / "governance-events.jsonl"
        )

    def evaluate(self, intention: Intention, context: TaskContext) -> PolicyVerdict:
        """Run policies in order and return the first non-allow verdict."""
        for policy in self.policies:
            verdict = policy.check(intention, context)
            if verdict != PolicyVerdict.ALLOW:
                self.audit(
                    intention,
                    verdict,
                    policy_name=getattr(policy, "name", policy.__class__.__name__),
                    context=context,
                )
                return verdict

        self.audit(
            intention,
            PolicyVerdict.ALLOW,
            policy_name="GovernanceInterceptor",
            context=context,
        )
        return PolicyVerdict.ALLOW

    def audit(
        self,
        intention: Intention,
        verdict: PolicyVerdict,
        policy_name: str,
        context: TaskContext | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Write a governance evidence event."""
        event = AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            intention=intention,
            verdict=verdict,
            source="GovernanceInterceptor",
            policy=policy_name,
            context=context,
            details=details or {},
        )
        self.evidence_writer.append_event(event)
