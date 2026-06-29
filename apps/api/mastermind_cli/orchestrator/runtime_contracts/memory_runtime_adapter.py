"""Adapter that persists runtime execution results into the memory layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from mastermind_cli.memory_layer.models import (
    CheckpointRecord,
    ContextSnapshot,
    DecisionRecord,
    RunSummary,
)
from mastermind_cli.orchestrator.runtime_contracts.models import (
    ExecutionEnvelope,
    LoopPolicy,
    RuntimeExecutionResult,
    RuntimeSelection,
)


@dataclass(frozen=True, slots=True)
class RuntimeMemoryWrite:
    """Summary of what was persisted for a single runtime execution."""

    project_id: str
    run_id: str
    checkpoint_id: str | None
    decision_id: str | None
    run_summary_id: str | None


@runtime_checkable
class MemoryRuntimeWriter(Protocol):
    """Contract for persisting a `RuntimeExecutionResult` into the memory layer."""

    async def persist_runtime_run(
        self,
        *,
        project_id: str,
        task_id: str | None,
        run_id: str,
        runtime_result: RuntimeExecutionResult,
        snapshot: ContextSnapshot | None = None,
    ) -> RuntimeMemoryWrite:
        """Persist the runtime run and return a traceable write summary."""


@runtime_checkable
class MemoryServiceWriter(Protocol):
    """Minimal memory-service contract required by the runtime adapter."""

    async def save_checkpoint(self, checkpoint: CheckpointRecord) -> CheckpointRecord:
        """Persist a checkpoint record."""

    async def save_decision(self, decision: DecisionRecord) -> DecisionRecord:
        """Persist a decision record."""

    async def save_run_summary(self, run_summary: RunSummary) -> RunSummary:
        """Persist a run summary record."""


@dataclass(frozen=True, slots=True)
class MemoryRuntimeAdapter:
    """Default writer that translates runtime results into memory records."""

    memory_service: MemoryServiceWriter | None = None

    async def persist_runtime_run(
        self,
        *,
        project_id: str,
        task_id: str | None,
        run_id: str,
        runtime_result: RuntimeExecutionResult | None,
        snapshot: ContextSnapshot | None = None,
    ) -> RuntimeMemoryWrite:
        """Persist checkpoint, decision, and run summary for one execution."""
        if self.memory_service is None:
            return RuntimeMemoryWrite(
                project_id=project_id,
                run_id=run_id,
                checkpoint_id=None,
                decision_id=None,
                run_summary_id=None,
            )
        if runtime_result is None:
            raise ValueError("runtime_result is required when memory_service is set")

        checkpoint = self._build_checkpoint(
            project_id=project_id,
            task_id=task_id,
            run_id=run_id,
            runtime_result=runtime_result,
            snapshot=snapshot,
        )
        decision = self._build_decision(
            project_id=project_id,
            task_id=task_id,
            run_id=run_id,
            runtime_result=runtime_result,
        )
        run_summary = self._build_run_summary(
            project_id=project_id,
            run_id=run_id,
            runtime_result=runtime_result,
        )

        persisted_checkpoint = await self.memory_service.save_checkpoint(checkpoint)
        persisted_decision = await self.memory_service.save_decision(decision)
        persisted_run_summary = await self.memory_service.save_run_summary(run_summary)

        return RuntimeMemoryWrite(
            project_id=project_id,
            run_id=run_id,
            checkpoint_id=persisted_checkpoint.checkpoint_id,
            decision_id=persisted_decision.decision_id,
            run_summary_id=(
                persisted_run_summary.run_id if persisted_run_summary.run_id else None
            ),
        )

    def _build_checkpoint(
        self,
        *,
        project_id: str,
        task_id: str | None,
        run_id: str,
        runtime_result: RuntimeExecutionResult,
        snapshot: ContextSnapshot | None,
    ) -> CheckpointRecord:
        """Build a checkpoint record capturing the resume state."""
        selection = runtime_result.selection
        envelope = runtime_result.execution_envelope
        loop_policy = selection.loop_policy
        next_step_summary = self._next_step_summary(envelope.next_actions)
        resume_state = self._resume_state(
            loop_policy=loop_policy,
            envelope=envelope,
            snapshot=snapshot,
        )
        context_summary = self._checkpoint_context_summary(
            selection=selection,
            envelope=envelope,
        )
        return CheckpointRecord(
            checkpoint_id=f"ckpt-{run_id}",
            project_id=project_id,
            task_id=task_id,
            run_id=run_id,
            context_summary=context_summary,
            resume_state=resume_state,
            next_step_summary=next_step_summary,
        )

    def _build_decision(
        self,
        *,
        project_id: str,
        task_id: str | None,
        run_id: str,
        runtime_result: RuntimeExecutionResult,
    ) -> DecisionRecord:
        """Build a decision record documenting the loop policy choice."""
        selection = runtime_result.selection
        loop_policy = selection.loop_policy
        rationale = self._decision_rationale(loop_policy, runtime_result)
        status = self._decision_status(runtime_result)
        metadata = self._decision_metadata(selection, runtime_result)
        return DecisionRecord(
            decision_id=f"dec-{selection.task_profile.task_id}-{run_id}",
            project_id=project_id,
            task_id=task_id,
            title=f"Loop policy: {loop_policy.base_loop}",
            status=status,
            rationale_markdown=rationale,
            metadata=metadata,
        )

    def _build_run_summary(
        self,
        *,
        project_id: str,
        run_id: str,
        runtime_result: RuntimeExecutionResult,
    ) -> RunSummary:
        """Build a run summary that mirrors the canonical execution envelope."""
        envelope = runtime_result.execution_envelope
        metadata = self._run_summary_metadata(runtime_result)
        return RunSummary(
            run_id=run_id,
            project_id=project_id,
            summary=envelope.summary,
            metadata=metadata,
        )

    @staticmethod
    def _next_step_summary(next_actions: tuple[str, ...]) -> str:
        """Render a deterministic next-step string from envelope actions."""
        if not next_actions:
            return "Await next instructions."
        return "; ".join(next_actions)

    @staticmethod
    def _resume_state(
        *,
        loop_policy: LoopPolicy,
        envelope: ExecutionEnvelope,
        snapshot: ContextSnapshot | None,
    ) -> dict[str, object]:
        """Compose the resume state captured at the checkpoint."""
        state: dict[str, object] = {
            "loop_policy_id": loop_policy.base_loop,
            "additional_loops": list(loop_policy.additional_loops),
            "recovery_policy_id": loop_policy.recovery_policy_id,
            "max_iterations": loop_policy.max_iterations,
            "time_budget_ms": loop_policy.time_budget_ms,
            "tool_budget": loop_policy.tool_budget,
            "status": envelope.status,
            "next_actions": list(envelope.next_actions),
            "open_gaps": list(snapshot.open_gaps) if snapshot is not None else [],
        }
        return state

    @staticmethod
    def _checkpoint_context_summary(
        *,
        selection: RuntimeSelection,
        envelope: ExecutionEnvelope,
    ) -> dict[str, object]:
        """Capture a compact, JSON-safe context summary at the checkpoint."""
        return {
            "task_id": selection.task_profile.task_id,
            "complexity": selection.task_profile.complexity,
            "risk_level": selection.task_profile.risk_level,
            "verifiability": selection.task_profile.verifiability,
            "subjectivity": selection.task_profile.subjectivity,
            "requires_checker": selection.task_profile.requires_checker,
            "acceptance_mode": selection.task_profile.acceptance_mode,
            "status": envelope.status,
            "artifact_count": len(envelope.artifacts),
        }

    @staticmethod
    def _decision_rationale(
        loop_policy: LoopPolicy, runtime_result: RuntimeExecutionResult
    ) -> str:
        """Render the decision rationale combining loop policy and outcomes."""
        lines: list[str] = [f"Selected loop `{loop_policy.base_loop}`."]
        if loop_policy.rationale:
            lines.append("Rationale: " + "; ".join(loop_policy.rationale))
        if runtime_result.review_outcome is not None:
            findings = list(runtime_result.review_outcome.findings)
            if findings:
                lines.append("Review findings: " + "; ".join(findings))
        if runtime_result.recovery_decision is not None:
            lines.append(
                "Recovery action: "
                f"{runtime_result.recovery_decision.action} "
                f"({runtime_result.recovery_decision.reason})"
            )
        return "\n".join(lines)

    @staticmethod
    def _decision_status(runtime_result: RuntimeExecutionResult) -> str:
        """Return the decision status derived from the recovery decision."""
        if runtime_result.recovery_decision is not None:
            action = runtime_result.recovery_decision.action
            if action in {"replan", "escalate"}:
                return "needs-revision"
            return action
        if runtime_result.review_outcome is not None and (
            not runtime_result.review_outcome.approved
        ):
            return "needs-revision"
        return "accepted"

    @staticmethod
    def _decision_metadata(
        selection: RuntimeSelection, runtime_result: RuntimeExecutionResult
    ) -> dict[str, object]:
        """Collect structured metadata for the decision record."""
        envelope = runtime_result.execution_envelope
        metadata: dict[str, object] = {
            "task_id": selection.task_profile.task_id,
            "loop_policy_id": selection.loop_policy.base_loop,
            "requires_review": selection.loop_policy.requires_review,
            "requires_verification": selection.loop_policy.requires_verification,
            "verification_passed": (
                runtime_result.verification_outcome.passed
                if runtime_result.verification_outcome is not None
                else None
            ),
            "review_approved": (
                runtime_result.review_outcome.approved
                if runtime_result.review_outcome is not None
                else None
            ),
            "envelope_status": envelope.status,
            "artifacts": list(envelope.artifacts),
            "risks": list(envelope.risks),
        }
        return metadata

    @staticmethod
    def _run_summary_metadata(
        runtime_result: RuntimeExecutionResult,
    ) -> dict[str, object]:
        """Collect metadata that mirrors the canonical execution envelope."""
        envelope = runtime_result.execution_envelope
        metadata: dict[str, object] = {
            "task_id": runtime_result.selection.task_profile.task_id,
            "envelope_status": envelope.status,
            "artifacts": list(envelope.artifacts),
            "risks": list(envelope.risks),
            "next_actions": list(envelope.next_actions),
        }
        if runtime_result.verification_outcome is not None:
            metadata["verification"] = {
                "performed": runtime_result.verification_outcome.performed,
                "passed": runtime_result.verification_outcome.passed,
            }
        if runtime_result.review_outcome is not None:
            metadata["review"] = {
                "performed": runtime_result.review_outcome.performed,
                "approved": runtime_result.review_outcome.approved,
            }
        if runtime_result.recovery_decision is not None:
            metadata["recovery"] = {
                "action": runtime_result.recovery_decision.action,
                "escalate_to_human": runtime_result.recovery_decision.escalate_to_human,
            }
        return metadata
