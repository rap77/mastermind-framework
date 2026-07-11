"""End-to-end harness run executor wired through the project adapter."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from mastermind_cli.memory_layer.models import (
    CheckpointRecord,
    ContextSnapshot,
    build_latest_checkpoint_snapshot,
)
from mastermind_cli.memory_layer.service import MemoryService
from mastermind_cli.mm_flow.integrated_run import IntegratedRun
from mastermind_cli.mm_flow.project_adapter import ProjectAdapter
from mastermind_cli.orchestrator.runtime_contracts import MemoryRuntimeWriter
from mastermind_cli.orchestrator.runtime_contracts import (
    MultiHarnessPipeline,
    MultiHarnessPipelineResult,
    ObjectiveProfile,
)
from mastermind_cli.orchestrator.stateless_coordinator import (
    CoordinatorConfig,
    StatelessCoordinator,
)
from mastermind_cli.types.interfaces import Brief

logger = logging.getLogger(__name__)


@runtime_checkable
class _ExecutorMCPClient(Protocol):
    """Minimal MCP client protocol that the executor depends on."""

    def query_notebooklm(self, notebook_id: str, query: str) -> str:
        """Return a deterministic response for the given notebook + query."""
        ...


class _NoOpMCPClient:
    """Deterministic no-op MCP client used by the executor defaults."""

    def query_notebooklm(self, notebook_id: str, query: str) -> str:
        """Return an empty response for any notebook + query combination."""
        del notebook_id, query
        return ""


CoordinatorFactory = Callable[..., StatelessCoordinator]


@dataclass(frozen=True, slots=True)
class HarnessRunExecutor:
    """Compose the adapter, coordinator, and memory writer into a single run."""

    adapter: ProjectAdapter
    mcp_client: _ExecutorMCPClient = _NoOpMCPClient()
    coordinator_factory: CoordinatorFactory | None = None
    memory_service: MemoryService | None = None
    memory_runtime_writer: MemoryRuntimeWriter | None = None
    multi_harness_pipeline: MultiHarnessPipeline | None = None

    async def execute_harness_run(
        self,
        *,
        brief: Brief,
        brain_ids: tuple[str, ...],
        status: str = "in_progress",
        summary: str | None = None,
        verification_outcome: str = "pending",
    ) -> IntegratedRun:
        """Run the harness through the full pipeline and persist results."""
        request = self.adapter.load_harness_request()
        multi_harness_result = self._build_multi_harness_result(request, brief)
        snapshot = await self._load_memory_snapshot()
        coordinator = self._build_coordinator(snapshot)
        await coordinator.execute_flow(brief=brief, brain_ids=list(brain_ids))
        runtime_result = coordinator.runtime_execution_result
        memory_write = coordinator.runtime_memory_write
        envelope_summary = (
            runtime_result.execution_envelope.summary
            if runtime_result is not None
            else ""
        )
        archive = self.adapter.write_structured_status(
            status=status,
            summary=summary or envelope_summary,
            next_action=self._next_action(status),
            verification_outcome=verification_outcome,
            objective=request.operational_objective,
            uow=request.active_uow,
            warnings=request.warnings,
        )
        validation = self.adapter.validate_request(request)
        return IntegratedRun(
            project_id=self.adapter.project_id,
            request=request,
            memory_snapshot=snapshot,
            runtime_result=runtime_result,
            memory_write=memory_write,
            archive_record=archive,
            warnings=request.warnings,
            validation=validation,
            multi_harness_result=multi_harness_result,
        )

    def _build_multi_harness_result(
        self,
        request: object,
        brief: Brief,
    ) -> MultiHarnessPipelineResult | None:
        """Build and validate a multi-harness bundle when configured."""
        if self.multi_harness_pipeline is None:
            return None
        profile = self._build_objective_profile(request, brief)
        result = self.multi_harness_pipeline.build(profile)
        if result.bundle.validation_status == "failed":
            raise ValueError(
                "Multi-harness bundle validation failed: "
                + "; ".join(result.bundle.validation_errors)
            )
        return result

    def _build_objective_profile(
        self,
        request: object,
        brief: Brief,
    ) -> ObjectiveProfile:
        """Normalize planning + brief inputs into multi-harness selector signals."""
        operational_objective = str(getattr(request, "operational_objective", ""))
        active_uow = str(getattr(request, "active_uow", ""))
        expected_outputs = tuple(
            str(item) for item in getattr(request, "expected_outputs", ())
        )
        required_checks = tuple(
            str(item) for item in getattr(request, "required_checks", ())
        )
        text = f"{operational_objective} {brief.problem_statement}".lower()
        return ObjectiveProfile(
            objective_id=operational_objective or active_uow or "objective",
            objective_text=brief.problem_statement,
            domain=self._infer_domain(text),
            phase=self._infer_phase(text),
            output_type=self._infer_output_type(text, expected_outputs),
            complexity="medium",
            risk_level="medium",
            verifiability="high" if required_checks else "medium",
            requires_write=True,
            requires_fresh_context=False,
            requires_memory=self.memory_service is not None,
            requires_mcp=False,
            requires_review=bool(required_checks),
            requires_recovery=False,
            reasons=(
                f"objective={operational_objective or active_uow or 'objective'}",
                "source=planning_bridge+brief",
            ),
        )

    @staticmethod
    def _infer_domain(text: str) -> str:
        """Infer the broad selector domain from objective text."""
        if any(term in text for term in ("code", "implement", "migration", "runtime")):
            return "software"
        if any(term in text for term in ("prd", "product", "strategy")):
            return "product"
        return "general"

    @staticmethod
    def _infer_phase(text: str) -> str:
        """Infer lifecycle phase from objective text."""
        if any(term in text for term in ("implement", "code", "fix")):
            return "implementation"
        if any(term in text for term in ("discover", "research")):
            return "discovery"
        if any(term in text for term in ("verify", "test", "review")):
            return "verification"
        return "planning"

    @staticmethod
    def _infer_output_type(text: str, expected_outputs: tuple[str, ...]) -> str:
        """Infer expected output type for harness selection."""
        combined = " ".join((text, *expected_outputs)).lower()
        if "prd" in combined:
            return "prd"
        if "plan" in combined:
            return "plan"
        return "artifact"

    async def _load_memory_snapshot(self) -> ContextSnapshot | None:
        """Load the project memory snapshot via the injected service when available."""
        if self.memory_service is None:
            return None
        project_id = self.adapter.project_id
        if not project_id:
            return None
        checkpoint_reader = getattr(self.memory_service, "load_latest_checkpoint", None)
        try:
            snapshot = await self.memory_service.build_context_snapshot(project_id)
            if snapshot.checkpoints or checkpoint_reader is None:
                return snapshot
        except Exception as exc:  # noqa: BLE001 - memory snapshot is optional, log and continue
            logger.warning(
                "Failed to load memory snapshot for project_id=%s: %s",
                project_id,
                exc,
            )
            if checkpoint_reader is None:
                return None

        latest_checkpoint: CheckpointRecord | None = await checkpoint_reader(project_id)
        if latest_checkpoint is None:
            return None
        return build_latest_checkpoint_snapshot(project_id, latest_checkpoint)

    def _build_coordinator(
        self, snapshot: ContextSnapshot | None
    ) -> StatelessCoordinator:
        """Build the stateless coordinator with adapter + writer + snapshot wired in."""
        config_kwargs: dict[str, Any] = {
            "mcp_client": self.mcp_client,
            "enable_logging": False,
        }
        project_id = self.adapter.project_id
        if project_id:
            config_kwargs["project_id"] = project_id
        if self.memory_runtime_writer is not None:
            config_kwargs["memory_runtime_writer"] = self.memory_runtime_writer
        if snapshot is not None:

            def snapshot_provider(
                _project_id: str, _task_id: str | None
            ) -> ContextSnapshot | None:
                return snapshot

            config_kwargs["memory_context_provider"] = snapshot_provider

        if self.coordinator_factory is not None:
            return self.coordinator_factory(**config_kwargs)
        return StatelessCoordinator(CoordinatorConfig(**config_kwargs))

    @staticmethod
    def _next_action(status: str) -> str:
        """Return the deterministic next-action string for a given status."""
        if status == "completed":
            return "archive_objective"
        return "continue_phase_execution"
