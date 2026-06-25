"""Deterministic governance policies."""

from __future__ import annotations

from typing import Protocol

from .models import AuditEvent, Intention, PolicyResult, PolicyVerdict, TaskContext


class GovernancePolicy(Protocol):
    """Protocol implemented by all governance policies."""

    def evaluate(self, intention: Intention, context: TaskContext) -> PolicyResult:
        """Evaluate an intention against the current context."""
        ...


class AuditWriter(Protocol):
    """Protocol for append-only governance evidence writers."""

    def append(self, event: AuditEvent) -> str:
        """Persist a governance event and return a durable reference."""
        ...


class SecretPolicy:
    """Deny secret exposure or secret-target operations."""

    _SECRET_PATTERNS = (".env", "secret", "credential", "token", "api_key")

    def evaluate(self, intention: Intention, context: TaskContext) -> PolicyResult:
        """Evaluate whether targets look like secrets."""
        del context

        matched_targets = [
            target
            for target in intention.targets
            if any(pattern in target.lower() for pattern in self._SECRET_PATTERNS)
        ]
        if matched_targets:
            return PolicyResult(
                policy_name="SecretPolicy",
                verdict=PolicyVerdict.DENY,
                reason_code="secret_target",
                human_reason="Target touches secret or credential material.",
                matched_targets=matched_targets,
            )

        return PolicyResult(
            policy_name="SecretPolicy",
            verdict=PolicyVerdict.ALLOW,
            reason_code="ok",
            human_reason="No secret targets detected.",
            matched_targets=[],
        )


class ScopePolicy:
    """Deny writes outside the allowed task scope."""

    def evaluate(self, intention: Intention, context: TaskContext) -> PolicyResult:
        """Ensure all targets stay within allowed paths."""
        allowed_prefixes = tuple(context.allowed_paths)
        matched_targets = [
            target
            for target in intention.targets
            if not target.startswith(allowed_prefixes)
        ]
        if matched_targets:
            return PolicyResult(
                policy_name="ScopePolicy",
                verdict=PolicyVerdict.DENY,
                reason_code="outside_scope",
                human_reason="Target is outside the allowed task scope.",
                matched_targets=matched_targets,
            )

        return PolicyResult(
            policy_name="ScopePolicy",
            verdict=PolicyVerdict.ALLOW,
            reason_code="ok",
            human_reason="All targets are within scope.",
            matched_targets=[],
        )


class LargeChangePolicy:
    """Pause for explicit approval when change volume crosses thresholds."""

    _MAX_FILES_WITHOUT_APPROVAL = 20
    _MAX_NET_LOC_WITHOUT_APPROVAL = 500

    def evaluate(self, intention: Intention, context: TaskContext) -> PolicyResult:
        """Require approval for large or sensitive changes."""
        del intention

        is_large_change = (
            context.projected_file_count > self._MAX_FILES_WITHOUT_APPROVAL
            or context.projected_net_loc > self._MAX_NET_LOC_WITHOUT_APPROVAL
        )
        if is_large_change and context.approval_state != "approved":
            return PolicyResult(
                policy_name="LargeChangePolicy",
                verdict=PolicyVerdict.PAUSE_AND_ASK,
                reason_code="large_change",
                human_reason="Projected change requires explicit approval.",
                matched_targets=[],
            )

        return PolicyResult(
            policy_name="LargeChangePolicy",
            verdict=PolicyVerdict.ALLOW,
            reason_code="ok",
            human_reason="Projected change is within approval thresholds.",
            matched_targets=[],
        )


class RiskPolicy:
    """Deny obviously destructive actions."""

    _BLOCKED_ACTIONS = {
        "rm -rf",
        "git reset --hard",
        "git clean -fdx",
        "delete_all",
    }

    def evaluate(self, intention: Intention, context: TaskContext) -> PolicyResult:
        """Deny destructive commands regardless of context."""
        del context

        if intention.action in self._BLOCKED_ACTIONS:
            return PolicyResult(
                policy_name="RiskPolicy",
                verdict=PolicyVerdict.DENY,
                reason_code="destructive_action",
                human_reason="Destructive action is not allowed.",
                matched_targets=intention.targets,
            )

        return PolicyResult(
            policy_name="RiskPolicy",
            verdict=PolicyVerdict.ALLOW,
            reason_code="ok",
            human_reason="Action is not destructive.",
            matched_targets=[],
        )


class ProductionWritePolicy:
    """Deny production mutations without dry-run and approval."""

    _MUTATING_ACTIONS = {"POST", "PUT", "PATCH", "DELETE"}

    def evaluate(self, intention: Intention, context: TaskContext) -> PolicyResult:
        """Require dry-run and explicit approval for production writes."""
        if (
            intention.requires_production_access
            and intention.action in self._MUTATING_ACTIONS
            and (not context.dry_run_enabled or context.approval_state != "approved")
        ):
            return PolicyResult(
                policy_name="ProductionWritePolicy",
                verdict=PolicyVerdict.DENY,
                reason_code="production_write_without_dry_run",
                human_reason="Production writes require dry-run and approval.",
                matched_targets=intention.targets,
            )

        return PolicyResult(
            policy_name="ProductionWritePolicy",
            verdict=PolicyVerdict.ALLOW,
            reason_code="ok",
            human_reason="No blocked production write detected.",
            matched_targets=[],
        )


class MainBranchPolicy:
    """Deny push/merge/release/tagging to main or master without approval."""

    _BLOCKED_BRANCHES = {"main", "master"}
    _BLOCKED_ACTIONS = {"push_branch", "merge_branch", "release", "tag_release"}

    def evaluate(self, intention: Intention, context: TaskContext) -> PolicyResult:
        """Protect main/master from unapproved operations."""
        del context

        if intention.action in self._BLOCKED_ACTIONS and any(
            target in self._BLOCKED_BRANCHES for target in intention.targets
        ):
            return PolicyResult(
                policy_name="MainBranchPolicy",
                verdict=PolicyVerdict.DENY,
                reason_code="protected_branch",
                human_reason="Protected branch requires explicit approval.",
                matched_targets=[
                    target
                    for target in intention.targets
                    if target in self._BLOCKED_BRANCHES
                ],
            )

        return PolicyResult(
            policy_name="MainBranchPolicy",
            verdict=PolicyVerdict.ALLOW,
            reason_code="ok",
            human_reason="No protected branch mutation detected.",
            matched_targets=[],
        )
