"""
Stateless Coordinator - Per-request orchestration without shared state.

This coordinator creates a NEW instance per request, making it multi-user safe
by design. No global state, no instance variables beyond immutable config.

Architecture Principle:
"If every coordinator is a NEW instance per request,
we DON'T have shared state pollution."
"""

import asyncio
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from pydantic import BaseModel
from mastermind_cli.types.interfaces import (
    BrainInput,
    Brief,
)
from mastermind_cli.types.protocol import BrainEnvelope, BrainOutputType
from mastermind_cli.types.parallel import FlowConfig
from mastermind_cli.brain_registry import BrainRegistry


# =============================================================================
# MCP CLIENT PROTOCOL
# =============================================================================

@runtime_checkable
class MCPClient(Protocol):
    """MCP client protocol for type hints."""

    def query_notebooklm(
        self,
        notebook_id: str,
        query: str
    ) -> str:
        """Query NotebookLM via MCP."""
        ...


# =============================================================================
# COORDINATOR CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class CoordinatorConfig:
    """
    Immutable coordinator configuration.

    Using frozen=True makes this dataclass immutable (hashable, safer).
    All configuration is set at creation time and cannot be modified.
    """
    mcp_client: MCPClient
    enable_logging: bool = True
    brain_registry: BrainRegistry | None = None

    # Future: Add timeout, retry config, etc.
    # timeout_ms: int = 30000
    # retry_attempts: int = 1


# =============================================================================
# STATELESS COORDINATOR
# =============================================================================

class StatelessCoordinator:
    """
    Stateless coordinator - NO mutable instance variables (except config).

    Each request creates a NEW instance.
    Multi-user safe by design.

    Why this matters:
    - Multiple users can run flows simultaneously
    - No cross-session pollution
    - Each execution is isolated
    - Easier to test (no hidden state)
    """

    def __init__(self, config: CoordinatorConfig):
        """
        Initialize coordinator with immutable configuration.

        Args:
            config: CoordinatorConfig (immutable dataclass)
        """
        # Store ONLY immutable config (frozen dataclass)
        self.config = config

        # Per-request execution state (reset for each execute_flow call)
        self.message_log: list = []  # In-memory trace of BrainEnvelope
        self.brain_outputs: dict = {}  # brain_id -> output (for parent passing)
        self.correlation_id: str = ""  # Flow correlation ID

        # Flow configuration (for DAG execution)
        self.flow_config = None

    async def execute_flow(
        self,
        brief: Brief,
        brain_ids: list[str]
    ) -> dict[str, BaseModel]:
        """
        Execute flow with wave-based parallelism.

        Pattern:
        1. Resolve dependencies into waves (sequential)
        2. Execute each wave in parallel (within wave)
        3. Pass outputs to dependent brains in next wave

        Args:
            brief: User's brief
            brain_ids: List of brain IDs to execute (e.g., ["brain-01", "brain-02"])

        Returns:
            Dict mapping brain_id → output_model

        Example:
            >>> coordinator = StatelessCoordinator(config)
            >>> results = await coordinator.execute_flow(
            ...     brief=Brief(problem_statement="Build a CRM"),
            ...     brain_ids=["brain-01-product-strategy", "brain-02-ux-research"]
            ... )
            >>> print(results["brain-01-product-strategy"].positioning)
        """
        # Reset per-request state
        self.message_log = []
        self.brain_outputs = {}
        self.correlation_id = f"corr-{id(brief)}-{id(self)}"

        # Step 1: Resolve dependencies into waves
        waves = await self._resolve_waves(brain_ids)

        # Step 2: Execute wave by wave
        # - Sequential waves (dependencies between waves)
        # - Parallel within wave (independent brains)
        results: dict[str, BaseModel] = {}

        for wave in waves.levels:
            # Execute all brains in this wave in parallel
            wave_results = await self._execute_wave(
                wave.brain_ids,
                brief,
                results,
                self.correlation_id
            )

            # Merge wave results into main results
            results.update(wave_results)

        return results

    async def _execute_wave(
        self,
        brain_ids: list[str],
        brief: Brief,
        previous_results: dict[str, BaseModel],
        correlation_id: str
    ) -> dict[str, BaseModel]:
        """
        Execute a single wave of brains in parallel.

        All brains in a wave are independent (no dependencies on each other).

        Args:
            brain_ids: List of brain IDs to execute
            brief: User's brief
            previous_results: Outputs from previous waves
            correlation_id: Flow correlation ID

        Returns:
            Dict mapping brain_id → output_model for this wave
        """
        # Create tasks for all brains in this wave
        tasks = {
            brain_id: asyncio.create_task(
                self._execute_brain_with_message(
                    brain_id=brain_id,
                    brief=brief,
                    correlation_id=correlation_id,
                    previous_results=previous_results
                )
            )
            for brain_id in brain_ids
        }

        # Wait for all tasks to complete
        results = {}
        for brain_id, task in tasks.items():
            try:
                output = await task
                results[brain_id] = output
            except Exception as e:
                # Log error and continue (don't fail entire flow)
                if self.config.enable_logging:
                    print(f"[StatelessCoordinator] Brain {brain_id} failed: {e}")
                # Re-raise if needed, or return error model
                raise

        return results

    async def _execute_brain(
        self,
        brain_id: str,
        brief: Brief,
        previous_results: dict[str, BaseModel]
    ) -> BaseModel:
        """
        Execute single brain - pure function call.

        This is the CORE of the pure function architecture.
        No state access, only input → output.

        Args:
            brain_id: Brain ID (e.g., "brain-01-product-strategy")
            brief: User's brief
            previous_results: Outputs from previous waves

        Returns:
            Brain output model (ProductStrategy, UXResearch, etc.)
        """
        from .brain_functions import get_brain_function

        # Get pure function for this brain
        brain_func = get_brain_function(brain_id)

        if brain_func is None:
            raise ValueError(f"Brain function not found: {brain_id}")

        # Prepare input for this brain
        brain_input = self._prepare_input(brain_id, brief, previous_results)

        # Call pure function (synchronous for now, could be async)
        # In production, brains might be async too
        output = brain_func(brain_input, mcp_client=self.config.mcp_client)

        if self.config.enable_logging:
            print(f"[StatelessCoordinator] Completed: {brain_id}")

        return output

    async def _execute_brain_with_message(
        self,
        brain_id: str,
        brief: Brief,
        correlation_id: str,
        previous_results: dict[str, BaseModel]
    ) -> BaseModel:
        """
        Execute brain with message logging and parent output passing.

        This wraps _execute_brain to add:
        - BrainEnvelope creation for logging
        - Parent output storage for dependent brains
        - Correlation ID tracking

        Args:
            brain_id: Brain ID (e.g., "brain-01-product-strategy")
            brief: User's brief
            correlation_id: Flow correlation ID
            previous_results: Outputs from previous waves (parent outputs)

        Returns:
            Brain output model (ProductStrategy, UXResearch, etc.)
        """
        # Get parent outputs for this brain (from flow config)
        parent_outputs = self._get_parent_outputs(brain_id, previous_results)

        # Execute brain
        output = await self._execute_brain(brain_id, brief, previous_results)

        # Store output for dependent brains
        self.brain_outputs[brain_id] = output

        # Create BrainEnvelope for logging
        envelope = BrainEnvelope.create(
            from_brain=brain_id,
            to_brain="orchestrator",  # Or next brain in DAG
            payload=output,
            correlation_id=correlation_id,
            task_id=f"task-{brain_id}",
            message_type=BrainOutputType.OUTPUT
        )

        # Add parent outputs to transport metadata for traceability
        if parent_outputs:
            envelope.transport_metadata["parent_outputs"] = [
                {k: v for k, v in po.model_dump().items() if k != 'raw_output'}
                for po in parent_outputs
            ]

        self.message_log.append(envelope)

        return output

    def _get_parent_outputs(
        self,
        brain_id: str,
        previous_results: dict[str, BaseModel]
    ) -> list[BaseModel]:
        """
        Get outputs from parent brains (dependencies).

        Args:
            brain_id: Brain being executed
            previous_results: All previous results

        Returns:
            List of parent brain outputs (empty if no dependencies)
        """
        if self.flow_config is None:
            return []

        # Get dependencies from flow config
        dependencies = self.flow_config.nodes.get(brain_id, [])

        # Resolve parent outputs
        parent_outputs = []
        for dep_id in dependencies:
            if dep_id in self.brain_outputs:
                parent_outputs.append(self.brain_outputs[dep_id])
            elif dep_id in previous_results:
                parent_outputs.append(previous_results[dep_id])

        return parent_outputs

    def _prepare_input(
        self,
        brain_id: str,
        brief: Brief,
        previous_results: dict[str, BaseModel]
    ) -> BrainInput:
        """
        Prepare BrainInput from brief and previous results.

        Args:
            brain_id: Brain being executed
            brief: User's brief
            previous_results: Outputs from previous waves

        Returns:
            BrainInput with brief + context from previous results
        """
        # Extract context from previous results
        additional_context = {}

        for prev_brain_id, prev_output in previous_results.items():
            # Convert Pydantic model to dict for context
            additional_context[prev_brain_id] = prev_output.model_dump()

        return BrainInput(
            brief=brief,
            additional_context=additional_context,
            execution_metadata={
                "brain_id": brain_id,
                "timestamp": self._get_timestamp()
            }
        )

    async def _resolve_waves(self, brain_ids: list[str]):
        """
        Resolve dependencies into execution waves.

        Reuses existing DependencyResolver logic.
        Groups brains into waves where:
        - Wave 0: No dependencies
        - Wave N: Depends only on brains in waves 0..N-1

        Args:
            brain_ids: List of brain IDs to resolve

        Returns:
            ExecutionGraph with waves
        """
        from .dependency_resolver import DependencyResolver
        from mastermind_cli.types.parallel import FlowConfig

        # Get brain registry (create if not provided)
        registry = self.config.brain_registry
        if registry is None:
            registry = BrainRegistry()

        # Create resolver
        resolver = DependencyResolver(registry)

        # Build simple flow config (no dependencies for now)
        # In production, load from brains.yaml with actual deps
        nodes = {brain_id: [] for brain_id in brain_ids}  # No deps for now

        flow_config = FlowConfig(
            flow_id="stateless-flow",
            nodes=nodes,
            description="Stateless coordinator flow"
        )

        # Resolve into waves
        execution_graph = await resolver.resolve(flow_config)

        return execution_graph

    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_stateless_coordinator(
    mcp_client: MCPClient,
    enable_logging: bool = True
) -> StatelessCoordinator:
    """
    Factory function to create a stateless coordinator.

    This is the RECOMMENDED way to create coordinators.
    Ensures consistent configuration.

    Args:
        mcp_client: MCP client instance
        enable_logging: Whether to log execution

    Returns:
        New StatelessCoordinator instance

    Example:
        >>> from mastermind_cli.orchestrator.mcp_integration import MCPIntegration
        >>> mcp_client = MCPIntegration()
        >>> coordinator = create_stateless_coordinator(mcp_client)
        >>> results = await coordinator.execute_flow(brief, brain_ids)
    """
    config = CoordinatorConfig(
        mcp_client=mcp_client,
        enable_logging=enable_logging
    )
    return StatelessCoordinator(config)
