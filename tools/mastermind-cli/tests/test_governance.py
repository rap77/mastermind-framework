"""Tests for the governance boundary."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mastermind_cli.orchestrator import Coordinator, OutputFormatter
from mastermind_cli.orchestrator.governance import (
    AuditEvent,
    EvidenceChainWriter,
    GovernanceInterceptor,
    Intention,
    PolicyVerdict,
    TaskContext,
)


class _AllowPolicy:
    """Policy stub that always allows."""

    name = "allow"

    def check(self, intention: Intention, context: TaskContext) -> PolicyVerdict:
        """Allow every intention."""
        return PolicyVerdict.ALLOW


class _DenyPolicy:
    """Policy stub that always denies."""

    name = "deny"

    def check(self, intention: Intention, context: TaskContext) -> PolicyVerdict:
        """Deny every intention."""
        return PolicyVerdict.DENY


class _FakeGovernance:
    """Fake governance gate for Coordinator tests."""

    def __init__(self, verdict: PolicyVerdict):
        self.verdict = verdict
        self.calls: list[tuple[Intention, TaskContext]] = []

    def evaluate(self, intention: Intention, context: TaskContext) -> PolicyVerdict:
        """Record the call and return the configured verdict."""
        self.calls.append((intention, context))
        return self.verdict


pytestmark = pytest.mark.smoke


def test_evidence_chain_writer_appends_and_loads_jsonl(tmp_path: Path) -> None:
    """EvidenceChainWriter must persist append-only JSONL events."""
    audit_path = tmp_path / "governance.jsonl"
    writer = EvidenceChainWriter(audit_path)

    event = AuditEvent(
        timestamp="2026-06-23T00:00:00Z",
        intention=Intention(
            action="orchestrate",
            target="Coordinator.orchestrate",
            scope="validation_only",
            estimated_tokens=50,
        ),
        verdict=PolicyVerdict.ALLOW,
        source="test",
        policy="allow",
    )

    writer.append_event(event)

    events = writer.load_session_events()

    assert audit_path.exists()
    assert len(events) == 1
    assert events[0].verdict == PolicyVerdict.ALLOW
    assert events[0].intention.target == "Coordinator.orchestrate"

    raw = audit_path.read_text(encoding="utf-8").strip()
    assert json.loads(raw)["policy"] == "allow"


def test_governance_interceptor_denies_and_audits(tmp_path: Path) -> None:
    """GovernanceInterceptor must stop on the first non-allow verdict."""
    writer = EvidenceChainWriter(tmp_path / "audit.jsonl")
    gate = GovernanceInterceptor(policies=[_DenyPolicy()], evidence_writer=writer)

    verdict = gate.evaluate(
        Intention(
            action="orchestrate",
            target="Coordinator.orchestrate",
            scope="validation_only",
        ),
        TaskContext(brief="brief", flow_type="validation_only"),
    )

    events = writer.load_session_events()

    assert verdict == PolicyVerdict.DENY
    assert len(events) == 1
    assert events[0].verdict == PolicyVerdict.DENY
    assert events[0].policy == "deny"


def test_coordinator_blocks_before_plan_generation_on_denial() -> None:
    """Coordinator must short-circuit before generating a plan."""
    governance = _FakeGovernance(PolicyVerdict.DENY)
    coordinator = Coordinator(formatter=OutputFormatter(), governance=governance)

    def _fail_generate(*args, **kwargs):  # pragma: no cover - defensive
        raise AssertionError("plan_generator.generate must not run on denial")

    coordinator.plan_generator.generate = _fail_generate  # type: ignore[method-assign]

    result = coordinator.orchestrate(
        brief="Crear una app para viajes compartidos",
        flow="validation_only",
    )

    assert result["status"] == "blocked"
    assert "Governance" in result["error"]
    assert len(governance.calls) == 1
    assert governance.calls[0][0].action == "orchestrate"


def test_coordinator_allows_governance_and_keeps_existing_flow() -> None:
    """Coordinator must keep the normal flow when governance allows."""
    governance = _FakeGovernance(PolicyVerdict.ALLOW)
    coordinator = Coordinator(formatter=OutputFormatter(), governance=governance)

    def _fake_generate(brief: str, flow_type: str) -> dict:
        return {
            "plan_id": "PLAN-TEST-001",
            "date": "2026-06-23T00:00:00Z",
            "flow_type": flow_type,
            "brief": {"original": brief, "clarified": brief},
            "tasks": [],
            "summary": {
                "total_tasks": 0,
                "estimated_duration": "0m",
                "critical_path": [],
                "brains_involved": [],
            },
        }

    coordinator.plan_generator.generate = _fake_generate  # type: ignore[method-assign]

    result = coordinator.orchestrate(
        brief="Crear una app para viajes compartidos",
        flow="validation_only",
        dry_run=True,
    )

    assert result["status"] == "dry_run_complete"
    assert result["plan"]["plan_id"] == "PLAN-TEST-001"
    assert len(governance.calls) == 1
    assert governance.calls[0][1].flow_type == "validation_only"
