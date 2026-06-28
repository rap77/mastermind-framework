"""End-to-end harness run executor wired through the project adapter."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from mastermind_cli.memory_layer.models import ContextSnapshot
from mastermind_cli.memory_layer.service import MemoryService
from mastermind_cli.mm_flow.integrated_run import IntegratedRun
from mastermind_cli.mm_flow.project_adapter import ProjectAdapter
from mastermind_cli.orchestrator.runtime_contracts import MemoryRuntimeWriter
from mastermind_cli.orchestrator.stateless_coordinator import (
    CoordinatorConfig,
    StatelessCoordinator,
)
from mastermind_cli.types.interfaces import Brief


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
        )

    async def _load_memory_snapshot(self) -> ContextSnapshot | None:
        """Load the project memory snapshot via the injected service when available."""
        if self.memory_service is None:
            return None
        project_id = self.adapter.project_id
        if not project_id:
            return None
        try:
            return await self.memory_service.build_context_snapshot(project_id)
        except Exception:
            return None

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
