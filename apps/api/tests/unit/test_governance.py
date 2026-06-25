"""Unit tests for governance core interceptor and policies."""

from dataclasses import replace

from mastermind_cli.orchestrator.governance import (
    AuditEvent,
    AuditWriter,
    CoordinatorAdapter,
    GovernanceDecision,
    GovernanceInterceptor,
    Intention,
    LargeChangePolicy,
    JsonLinesAuditWriter,
    MainBranchPolicy,
    PolicyResult,
    PolicyVerdict,
    ProductionWritePolicy,
    RiskPolicy,
    ScopePolicy,
    SecretPolicy,
    TaskContext,
)
from mastermind_cli.orchestrator.coordinator import Coordinator


class RecordingAuditWriter(AuditWriter):
    """Audit writer test double that records persisted events."""

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> str:
        """Record event and return deterministic reference."""
        self.events.append(event)
        return event.event_id


class FailingAuditWriter(AuditWriter):
    """Audit writer test double that always fails."""

    def append(self, event: AuditEvent) -> str:
        """Raise a persistence error."""
        raise RuntimeError("disk unavailable")


class StaticPolicy:
    """Simple policy stub for chain-order tests."""

    def __init__(self, result: PolicyResult) -> None:
        self.result = result
        self.calls = 0

    def evaluate(self, intention: Intention, context: TaskContext) -> PolicyResult:
        """Return the preconfigured result."""
        del intention, context
        self.calls += 1
        return self.result


class StubCoordinator:
    """Simple coordinator stub for adapter tests."""

    def __init__(self) -> None:
        self.calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def orchestrate(self, *args: object, **kwargs: object) -> dict[str, str]:
        """Record the call and return a stub response."""
        self.calls.append((args, kwargs))
        return {"status": "ok"}


class BlockingGovernance:
    """Governance stub that always denies."""

    def evaluate(
        self, intention: Intention, context: TaskContext
    ) -> GovernanceDecision:
        """Return a blocked decision."""
        del intention, context
        return GovernanceDecision(
            final_verdict=PolicyVerdict.DENY,
            triggering_policy="test",
            audit_event_ref="audit-1",
            next_action="do_not_delegate",
        )


def _build_intention() -> Intention:
    return Intention(
        action="edit_file",
        targets=["apps/api/mastermind_cli/orchestrator/stateless_coordinator.py"],
        scope="task-scope",
        estimated_risk="low",
        estimated_tokens=100,
        requires_network=False,
        requires_write=True,
        requires_production_access=False,
    )


def _build_context() -> TaskContext:
    return TaskContext(
        task_id="T1",
        session_id="S1",
        allowed_paths=["apps/api/mastermind_cli/orchestrator/"],
        sensitive_paths=[".env", "secrets/"],
        task_type="code_generation",
        approval_state="not_required",
        dry_run_enabled=False,
        production_mode=False,
    )


def test_governance_interceptor_allows_and_persists_audit() -> None:
    """Interceptor should allow safe changes and persist evidence."""
    writer = RecordingAuditWriter()
    interceptor = GovernanceInterceptor(
        policies=[SecretPolicy(), ScopePolicy(), LargeChangePolicy()],
        audit_writer=writer,
    )

    decision = interceptor.evaluate(_build_intention(), _build_context())

    assert decision.final_verdict is PolicyVerdict.ALLOW
    assert decision.triggering_policy == "allow"
    assert decision.audit_event_ref
    assert len(writer.events) == 1
    assert writer.events[0].verdict is PolicyVerdict.ALLOW


def test_governance_interceptor_short_circuits_on_first_deny() -> None:
    """Interceptor should stop at the first blocking policy."""
    deny_policy = StaticPolicy(
        PolicyResult(
            policy_name="DenyPolicy",
            verdict=PolicyVerdict.DENY,
            reason_code="outside_scope",
            human_reason="Denied for test",
            matched_targets=["forbidden.txt"],
        )
    )
    late_policy = StaticPolicy(
        PolicyResult(
            policy_name="LatePolicy",
            verdict=PolicyVerdict.ALLOW,
            reason_code="ok",
            human_reason="Should not run",
            matched_targets=[],
        )
    )
    interceptor = GovernanceInterceptor(
        policies=[deny_policy, late_policy],
        audit_writer=RecordingAuditWriter(),
    )

    decision = interceptor.evaluate(_build_intention(), _build_context())

    assert decision.final_verdict is PolicyVerdict.DENY
    assert decision.triggering_policy == "DenyPolicy"
    assert deny_policy.calls == 1
    assert late_policy.calls == 0


def test_governance_interceptor_fails_closed_when_audit_writer_fails() -> None:
    """Interceptor must deny delegation if audit persistence fails."""
    interceptor = GovernanceInterceptor(
        policies=[SecretPolicy(), ScopePolicy()],
        audit_writer=FailingAuditWriter(),
    )

    decision = interceptor.evaluate(_build_intention(), _build_context())

    assert decision.final_verdict is PolicyVerdict.DENY
    assert decision.triggering_policy == "AuditWriter"
    assert decision.next_action == "do_not_delegate"


def test_secret_policy_denies_secret_targets() -> None:
    """SecretPolicy should deny obvious secret paths."""
    intention = replace(_build_intention(), targets=[".env"])

    result = SecretPolicy().evaluate(intention, _build_context())

    assert result.verdict is PolicyVerdict.DENY
    assert result.reason_code == "secret_target"


def test_large_change_policy_pauses_sensitive_bulk_change() -> None:
    """LargeChangePolicy should request approval for large change thresholds."""
    intention = replace(
        _build_intention(),
        targets=["apps/api/mastermind_cli/orchestrator/", "docs/"],
    )
    context = replace(
        _build_context(),
        approval_state="not_required",
        projected_file_count=25,
        projected_net_loc=300,
    )

    result = LargeChangePolicy().evaluate(intention, context)

    assert result.verdict is PolicyVerdict.PAUSE_AND_ASK
    assert result.reason_code == "large_change"


def test_risk_policy_denies_destructive_commands() -> None:
    """RiskPolicy should deny destructive commands."""
    intention = replace(_build_intention(), action="rm -rf")

    result = RiskPolicy().evaluate(intention, _build_context())

    assert result.verdict is PolicyVerdict.DENY
    assert result.reason_code == "destructive_action"


def test_production_write_policy_denies_mutations_without_approval() -> None:
    """ProductionWritePolicy should deny production writes without approval."""
    intention = replace(
        _build_intention(),
        requires_production_access=True,
        action="POST",
    )
    context = replace(_build_context(), production_mode=True, dry_run_enabled=False)

    result = ProductionWritePolicy().evaluate(intention, context)

    assert result.verdict is PolicyVerdict.DENY
    assert result.reason_code == "production_write_without_dry_run"


def test_main_branch_policy_denies_push_to_main_without_approval() -> None:
    """MainBranchPolicy should deny push or merge to main/master."""
    intention = replace(_build_intention(), action="push_branch", targets=["main"])

    result = MainBranchPolicy().evaluate(intention, _build_context())

    assert result.verdict is PolicyVerdict.DENY
    assert result.reason_code == "protected_branch"


def test_coordinator_adapter_delegates_after_allow() -> None:
    """CoordinatorAdapter should delegate only after governance allows."""
    coordinator = StubCoordinator()
    adapter = CoordinatorAdapter(coordinator=coordinator, governance=None)

    result = adapter.orchestrate(
        _build_intention(),
        _build_context(),
        brief="ship it",
    )

    assert result == {"status": "ok"}
    assert len(coordinator.calls) == 1


def test_coordinator_adapter_blocks_on_deny() -> None:
    """CoordinatorAdapter should block delegation when governance denies."""
    coordinator = StubCoordinator()
    adapter = CoordinatorAdapter(
        coordinator=coordinator,
        governance=GovernanceInterceptor(
            policies=[RiskPolicy()],
            audit_writer=RecordingAuditWriter(),
        ),
    )

    result = adapter.orchestrate(
        replace(_build_intention(), action="rm -rf"),
        _build_context(),
        brief="ship it",
    )

    assert result["status"] == "blocked"
    assert len(coordinator.calls) == 0


def test_json_lines_audit_writer_appends_events(tmp_path) -> None:
    """JsonLinesAuditWriter should append one JSON line per event."""
    writer = JsonLinesAuditWriter(tmp_path / "audit.jsonl")
    event = AuditEvent(
        session_id="S1",
        task_id="T1",
        intention_snapshot=_build_intention(),
        policy_name="SecretPolicy",
        verdict=PolicyVerdict.ALLOW,
        reason_code="ok",
        reason_text="fine",
    )

    ref = writer.append(event)

    assert ref == event.event_id
    content = (tmp_path / "audit.jsonl").read_text(encoding="utf-8").strip()
    assert '"policy_name": "SecretPolicy"' in content


def test_coordinator_blocks_early_when_governance_denies() -> None:
    """Coordinator should stop before planning when governance denies."""
    coordinator = Coordinator(enable_logging=False, governance=BlockingGovernance())

    result = coordinator.orchestrate("Build a CRM")

    assert result["status"] == "blocked"
    assert result["policy"] == "test"
