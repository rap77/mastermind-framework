"""
Stateless Coordinator - Per-request orchestration without shared state.

This coordinator creates a NEW instance per request, making it multi-user safe
by design. No global state, no instance variables beyond immutable config.

Architecture Principle:
"If every coordinator is a NEW instance per request,
we DON'T have shared state pollution."
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from pydantic import BaseModel
from mastermind_cli.types.interfaces import (
    BrainInput,
    Brief,
)
from mastermind_cli.orchestrator.governance import (
    GovernanceInterceptor,
    Intention,
    TaskContext,
)
from mastermind_cli.orchestrator.runtime_contracts import (
    CapabilityRegistry,
    ExecutionEnvelope,
    FailureClassifier,
    HarnessRegistry,
    LoopPolicy,
    LoopSelector,
    RecoveryDecision,
    RecoveryHarness,
    ReviewHarness,
    ReviewOutcome,
    ReviewRubricResolver,
    TaskProfile,
    VerificationHarness,
    VerificationOutcome,
    build_execution_envelope,
    synthesize_execution_envelope,
    validate_execution_envelope,
)
from mastermind_cli.types.protocol import BrainEnvelope, BrainOutputType
from mastermind_cli.types.parallel import ExecutionGraph, FlowConfig
from mastermind_cli.brain_registry import BrainRegistry

logger = logging.getLogger(__name__)


# =============================================================================
# MCP CLIENT PROTOCOL
# =============================================================================


@runtime_checkable
class MCPClient(Protocol):
    """MCP client protocol for type hints."""

    def query_notebooklm(self, notebook_id: str, query: str) -> str:
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
    governance: GovernanceInterceptor | None = None

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

    _RAG_ENABLED_BRAIN_IDS = frozenset(
        {
            "brain-01-product-strategy",
            "brain-02-ux-research",
            "brain-03-ui-design",
            "brain-07-growth-data",
        }
    )

    def __init__(self, config: CoordinatorConfig):
        """
        Initialize coordinator with immutable configuration.

        Args:
            config: CoordinatorConfig (immutable dataclass)
        """
        # Store ONLY immutable config (frozen dataclass)
        self.config = config

        # Per-request execution state (reset for each execute_flow call)
        self.message_log: list[BrainEnvelope] = []  # In-memory trace of BrainEnvelope
        self.brain_outputs: dict[
            str, BaseModel
        ] = {}  # brain_id -> output (for parent passing)
        self.correlation_id: str = ""  # Flow correlation ID
        self.runtime_task_profile: TaskProfile | None = None
        self.runtime_loop_policy: LoopPolicy | None = None
        self.runtime_envelope: ExecutionEnvelope | None = None
        self.runtime_verification_outcome: VerificationOutcome | None = None
        self.runtime_review_outcome: ReviewOutcome | None = None
        self.runtime_recovery_decision: RecoveryDecision | None = None

        # Flow configuration (for DAG execution)
        self.flow_config: FlowConfig | None = None

    async def execute_flow(
        self,
        brief: Brief,
        brain_ids: list[str],
        conn: object | None = None,
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
            conn: Optional asyncpg connection for RAG retrieval.  When provided,
                  Brain #1 calls RAGContextBuilder.build() before its LLM query
                  (21.13).  When None, RAG is skipped — safe for tests that do
                  not have a DB.

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
        self.runtime_task_profile = None
        self.runtime_loop_policy = None
        self.runtime_envelope = None
        self.runtime_verification_outcome = None
        self.runtime_review_outcome = None
        self.runtime_recovery_decision = None

        if self.config.governance is not None:
            intention = Intention(
                action="execute_flow",
                targets=list(brain_ids),
                scope="stateless_coordinator",
                estimated_risk="low",
                estimated_tokens=None,
                requires_network=False,
                requires_write=False,
                requires_production_access=False,
            )
            context = TaskContext(
                task_id="stateless-coordinator",
                session_id=self.correlation_id,
                allowed_paths=[],
                sensitive_paths=[],
                task_type="orchestration",
                approval_state="not_required",
                dry_run_enabled=False,
                production_mode=False,
            )
            decision = self.config.governance.evaluate(intention, context)
            if decision.final_verdict.value != "allow":
                return {}

        self._prepare_runtime_contracts(brief=brief, brain_ids=brain_ids)

        # Step 1: Resolve dependencies into waves
        waves = await self._resolve_waves(brain_ids)

        # Step 2: Execute wave by wave
        # - Sequential waves (dependencies between waves)
        # - Parallel within wave (independent brains)
        results: dict[str, BaseModel] = {}

        for wave in waves.levels:
            # Execute all brains in this wave in parallel
            wave_results = await self._execute_wave(
                wave.brain_ids, brief, results, self.correlation_id, conn=conn
            )

            # Merge wave results into main results
            results.update(wave_results)

        self._finalize_runtime_envelope(results)
        return results

    async def _execute_wave(
        self,
        brain_ids: list[str],
        brief: Brief,
        previous_results: dict[str, BaseModel],
        correlation_id: str,
        conn: object | None = None,
    ) -> dict[str, BaseModel]:
        """
        Execute a single wave of brains in parallel.

        All brains in a wave are independent (no dependencies on each other).

        Args:
            brain_ids: List of brain IDs to execute
            brief: User's brief
            previous_results: Outputs from previous waves
            correlation_id: Flow correlation ID
            conn: Optional asyncpg connection for RAG retrieval (Brain #1 only).

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
                    previous_results=previous_results,
                    conn=conn,
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
                    logger.exception(
                        "[StatelessCoordinator] Brain %s failed: %s", brain_id, e
                    )
                # Re-raise if needed, or return error model
                raise

        return results

    async def _execute_brain(
        self,
        brain_id: str,
        brief: Brief,
        previous_results: dict[str, BaseModel],
        conn: object | None = None,
    ) -> BaseModel:
        """
        Execute single brain - pure function call.

        This is the CORE of the pure function architecture.
        No state access, only input → output.

        Phase 21 RAG integration:
        For the first RAG-enabled cohort (Brains #1, #2, #3, and #7),
        RAGContextBuilder.build() is called BEFORE the LLM query when an
        asyncpg connection is provided.
        The resulting block (or "" when both collections are empty) is passed
        to the brain function as ``rag_context``.  Empty blocks are never
        appended to the system prompt (21.14 guard).

        Args:
            brain_id: Brain ID (e.g., "brain-01-product-strategy")
            brief: User's brief
            previous_results: Outputs from previous waves
            conn: Optional asyncpg connection used to run RAG retrieval for
                  the first RAG-enabled cohort. When None, RAG is skipped and ``rag_context``
                  defaults to "" (empty — no block appended).

        Returns:
            Brain output model (ProductStrategy, UXResearch, etc.)
        """
        from .brain_functions import brain_id_variants, get_brain_function

        # Get pure function for this brain
        brain_func = get_brain_function(brain_id)

        if brain_func is None:
            raise ValueError(f"Brain function not found: {brain_id}")

        # Prepare input for this brain
        brain_input = self._prepare_input(brain_id, brief, previous_results)

        # 21.13+: Retrieve RAG context for the selected cohort before the LLM call.
        # RAGContextBuilder.build() is async → awaited here inside the async
        # _execute_brain method. Other brains are not yet RAG-enabled.
        rag_context = ""
        if (
            self._RAG_ENABLED_BRAIN_IDS.intersection(brain_id_variants(brain_id))
            and conn is not None
        ):
            from mastermind_cli.rag.context_builder import RAGContextBuilder  # noqa: PLC0415

            rag_context = await RAGContextBuilder(conn).build(
                brain_id, brief.problem_statement
            )

        # Call pure function (synchronous for now, could be async)
        # In production, brains might be async too
        #
        # 21.13: Pass rag_context ONLY if the brain function accepts it.
        # inspect.signature is used so that test mocks that don't declare
        # rag_context still work without modification.
        import inspect  # noqa: PLC0415

        sig = inspect.signature(brain_func)
        if rag_context and "rag_context" in sig.parameters:
            output: BaseModel = brain_func(
                brain_input, mcp_client=self.config.mcp_client, rag_context=rag_context
            )
        else:
            output = brain_func(brain_input, mcp_client=self.config.mcp_client)

        if self.config.enable_logging:
            logger.info("[StatelessCoordinator] Completed: %s", brain_id)

        return output

    async def _execute_brain_with_message(
        self,
        brain_id: str,
        brief: Brief,
        correlation_id: str,
        previous_results: dict[str, BaseModel],
        conn: object | None = None,
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
            conn: Optional asyncpg connection for RAG retrieval (Brain #1 only).

        Returns:
            Brain output model (ProductStrategy, UXResearch, etc.)
        """
        # Get parent outputs for this brain (from flow config)
        parent_outputs = self._get_parent_outputs(brain_id, previous_results)

        # Execute brain
        output = await self._execute_brain(brain_id, brief, previous_results, conn=conn)

        # Store output for dependent brains
        self.brain_outputs[brain_id] = output

        # Create BrainEnvelope for logging
        # Cast output to BrainOutput type for envelope creation
        envelope = BrainEnvelope.create(
            from_brain=brain_id,
            to_brain="orchestrator",  # Or next brain in DAG
            payload=output,  # type: ignore[arg-type]  # BaseModel is BrainOutput union
            correlation_id=correlation_id,
            task_id=f"task-{brain_id}",
            message_type=BrainOutputType.OUTPUT,
        )

        # Add parent outputs to transport metadata for traceability
        if parent_outputs:
            envelope.transport_metadata["parent_outputs"] = [
                {k: v for k, v in po.model_dump().items() if k != "raw_output"}
                for po in parent_outputs
            ]
        if (
            self.runtime_task_profile is not None
            and self.runtime_loop_policy is not None
        ):
            envelope.transport_metadata["runtime_contracts"] = {
                "task_profile": {
                    "task_id": self.runtime_task_profile.task_id,
                    "complexity": self.runtime_task_profile.complexity,
                    "risk_level": self.runtime_task_profile.risk_level,
                    "requires_checker": self.runtime_task_profile.requires_checker,
                },
                "loop_policy": {
                    "base_loop": self.runtime_loop_policy.base_loop,
                    "additional_loops": list(self.runtime_loop_policy.additional_loops),
                    "requires_review": self.runtime_loop_policy.requires_review,
                    "requires_verification": self.runtime_loop_policy.requires_verification,
                },
            }

        self.message_log.append(envelope)

        return output

    def _get_parent_outputs(
        self, brain_id: str, previous_results: dict[str, BaseModel]
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
        self, brain_id: str, brief: Brief, previous_results: dict[str, BaseModel]
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

        from .brain_functions import brain_id_variants

        for prev_brain_id, prev_output in previous_results.items():
            payload = prev_output.model_dump()
            for variant_id in brain_id_variants(prev_brain_id):
                additional_context[variant_id] = payload

        return BrainInput(
            brief=brief,
            additional_context=additional_context,
            execution_metadata={
                "brain_id": brain_id,
                "timestamp": self._get_timestamp(),
            },
        )

    async def _resolve_waves(self, brain_ids: list[str]) -> ExecutionGraph:
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
        from .brain_functions import canonical_brain_id

        # Get brain registry (create if not provided)
        registry = self.config.brain_registry
        if registry is None:
            registry = BrainRegistry()

        # Create resolver
        resolver = DependencyResolver(registry)

        # Build simple flow config (no dependencies for now)
        # In production, load from brains.yaml with actual deps
        canonical_to_requested = {
            canonical_brain_id(brain_id): brain_id for brain_id in brain_ids
        }
        nodes: dict[str, list[str]] = {
            canonical_id: [] for canonical_id in canonical_to_requested
        }  # No deps for now

        flow_config = FlowConfig(
            flow_id="stateless-flow",
            nodes=nodes,
            description="Stateless coordinator flow",
        )

        # Resolve into waves
        execution_graph = await resolver.resolve(flow_config)

        for level in execution_graph.levels:
            level.brain_ids = [
                canonical_to_requested.get(brain_id, brain_id)
                for brain_id in level.brain_ids
            ]

        return execution_graph

    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    def _prepare_runtime_contracts(self, brief: Brief, brain_ids: list[str]) -> None:
        """Classify the task and select the minimum sufficient control policy."""
        selector = LoopSelector()
        capability_registry = CapabilityRegistry()
        harness_registry = HarnessRegistry()

        task_profile = selector.classify_task(brief, brain_ids)
        capability_set = capability_registry.resolve_for_task(task_profile)
        harness_registry.resolve_for_capabilities(capability_set)
        loop_policy = selector.select_loop(task_profile, capability_set)

        self.runtime_task_profile = task_profile
        self.runtime_loop_policy = loop_policy

    def _finalize_runtime_envelope(self, results: dict[str, BaseModel]) -> None:
        """Build and validate the execution envelope for the completed flow."""
        if self.runtime_task_profile is None or self.runtime_loop_policy is None:
            return
        artifacts = tuple(sorted(results.keys()))
        next_actions = (
            ("independent review required",)
            if self.runtime_loop_policy.requires_review
            else ("continue",)
        )
        base_envelope = build_execution_envelope(
            task_profile=self.runtime_task_profile,
            loop_policy=self.runtime_loop_policy,
            artifacts=artifacts,
            risks=tuple(self.runtime_task_profile.reasons),
            next_actions=next_actions,
        )
        verification_outcome: VerificationOutcome | None = None
        review_outcome: ReviewOutcome | None = None
        recovery_decision: RecoveryDecision | None = None
        if self.runtime_loop_policy.requires_verification:
            verification_outcome = VerificationHarness().verify(
                base_envelope, self.runtime_task_profile
            )
        if self.runtime_loop_policy.requires_review:
            review_rubric = ReviewRubricResolver().resolve(
                self.runtime_task_profile,
                self.runtime_loop_policy,
            )
            review_outcome = ReviewHarness().review(
                base_envelope,
                verification_outcome
                if verification_outcome is not None
                else VerificationOutcome(
                    performed=False,
                    passed=False,
                    checks=(),
                    acceptance_criteria_satisfied=False,
                ),
                review_rubric,
            )
        failure_record = FailureClassifier().classify(
            base_envelope=base_envelope,
            verification_outcome=verification_outcome,
            review_outcome=review_outcome,
        )
        if failure_record is not None:
            recovery_decision = RecoveryHarness().decide(
                failure_record,
                self.runtime_loop_policy,
            )
        envelope = synthesize_execution_envelope(
            base_envelope=base_envelope,
            verification_outcome=verification_outcome,
            review_outcome=review_outcome,
            recovery_decision=recovery_decision,
        )
        valid, errors = validate_execution_envelope(envelope)
        if not valid:
            raise ValueError("Invalid runtime execution envelope: " + "; ".join(errors))
        self.runtime_verification_outcome = verification_outcome
        self.runtime_review_outcome = review_outcome
        self.runtime_recovery_decision = recovery_decision
        self.runtime_envelope = envelope


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def create_stateless_coordinator(
    mcp_client: MCPClient,
    enable_logging: bool = True,
    governance: GovernanceInterceptor | None = None,
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
        enable_logging=enable_logging,
        governance=governance,
    )
    return StatelessCoordinator(config)
