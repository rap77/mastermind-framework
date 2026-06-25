"""Domain models for governance evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class PolicyVerdict(str, Enum):
    """Supported governance verdicts."""

    ALLOW = "allow"
    DENY = "deny"
    PAUSE_AND_ASK = "pause_and_ask"


@dataclass(frozen=True)
class Intention:
    """Normalized action request to inspect before execution."""

    action: str
    targets: list[str]
    scope: str
    estimated_risk: str
    estimated_tokens: int | None
    requires_network: bool
    requires_write: bool
    requires_production_access: bool


@dataclass(frozen=True)
class TaskContext:
    """Operational context used by governance policies."""

    task_id: str
    session_id: str
    allowed_paths: list[str]
    sensitive_paths: list[str]
    task_type: str
    approval_state: str
    dry_run_enabled: bool
    production_mode: bool
    projected_file_count: int = 0
    projected_net_loc: int = 0


@dataclass(frozen=True)
class PolicyResult:
    """Structured single-policy evaluation result."""

    policy_name: str
    verdict: PolicyVerdict
    reason_code: str
    human_reason: str
    matched_targets: list[str]


@dataclass(frozen=True)
class AuditEvent:
    """Append-only governance evidence event."""

    session_id: str
    task_id: str
    intention_snapshot: Intention
    policy_name: str
    verdict: PolicyVerdict
    reason_code: str
    reason_text: str
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class GovernanceDecision:
    """Final decision consumed by callers before delegation."""

    final_verdict: PolicyVerdict
    triggering_policy: str
    audit_event_ref: str
    next_action: str
