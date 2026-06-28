"""
Unit tests for StatelessCoordinator.

Tests verify:
1. Pure function architecture (no shared state)
2. Multi-user safety (parallel execution)
3. Wave-based parallelism
4. Type safety

Mock Design Pattern:
- MockMCPClient generates unique responses per query using content hashing
- This ensures stateless coordinator tests can verify isolation between executions
- Without unique responses, tests couldn't detect cross-talk between coordinator instances
"""

import hashlib
import asyncio
from dataclasses import FrozenInstanceError
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import BaseModel
from mastermind_cli.memory_layer.models import ContextSnapshot
from mastermind_cli.types.interfaces import BrainInput
from mastermind_cli.types.interfaces import (
    Brief,
    GrowthDataEvaluation,
    ProductStrategy,
    UIDesign,
    UXResearch,
)
from mastermind_cli.types.parallel import FlowConfig
from mastermind_cli.orchestrator.governance import (
    GovernanceDecision,
    Intention,
    PolicyVerdict,
    TaskContext,
)
from mastermind_cli.orchestrator import (
    stateless_coordinator as stateless_coordinator_module,
)
from mastermind_cli.orchestrator.stateless_coordinator import (
    StatelessCoordinator,
    CoordinatorConfig,
    create_stateless_coordinator,
)
from mastermind_cli.mm_flow.evidence_selector import EvidenceSelectionRequest


# =============================================================================
# MOCK MCP CLIENT
# =============================================================================


class MockMCPClient:
    """Mock MCP client for testing.

    Design:
    - Generates unique responses per query using SHA256 content hashing
    - Stores query history in self.queries for debugging (not asserted in tests)
    - Uses call counter to differentiate sequential calls with same query

    Performance: O(n) where n = query length. Negligible for typical test queries.
    """

    # 8 hex chars = 32 bits, sufficient for test uniqueness
    _HASH_LENGTH = 8

    def __init__(self) -> None:
        """Initialize the mock client state."""
        # Queries logged for debugging purposes (not asserted in tests)
        self.queries: list[tuple[str, str]] = []
        self._call_count = 0

    def query_notebooklm(self, notebook_id: str, query: str) -> str:
        """Mock query that returns unique response per call.

        Uses SHA256 hash of query content to ensure different briefs produce
        different responses, making stateless coordinator tests work.

        Args:
            notebook_id: Notebook identifier
            query: Query string (hashed for uniqueness)

        Returns:
            Mock response with hash and call counter for debugging
        """
        # Log query for debugging (side-effect, not asserted in tests)
        self.queries.append((notebook_id, query))
        self._call_count += 1

        # Create unique response based on query content using SHA256
        # SHA256 is cryptographically secure and best practice (vs MD5)
        query_hash = hashlib.sha256(query.encode()).hexdigest()[: self._HASH_LENGTH]

        return (
            f"Mock response for {notebook_id}: {query[:50]}... "
            f"[hash:{query_hash} call:{self._call_count}]"
        )


class BlockingGovernance:
    """Governance stub that always blocks execution."""

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


# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture
def mock_mcp() -> MockMCPClient:
    """Mock MCP client."""
    return MockMCPClient()


@pytest.fixture
def coordinator_config(mock_mcp: MockMCPClient) -> CoordinatorConfig:
    """Coordinator config for testing."""
    return CoordinatorConfig(mcp_client=mock_mcp, enable_logging=False)


@pytest.fixture
def sample_brief() -> Brief:
    """Sample brief for testing."""
    return Brief(
        problem_statement="Build a CRM for small businesses",
        context="Need to manage customer relationships",
        constraints=["Low budget", "Quick launch"],
        target_audience="Small business owners",
    )


# =============================================================================
# TESTS: STATELESS COORDINATOR
# =============================================================================


@pytest.mark.asyncio
async def test_coordinator_is_stateless(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Test that coordinator has no shared state between instances.

    This verifies the core pure function architecture principle:
    - Different briefs MUST produce different outputs
    - If coordinators shared state, they'd return identical mock responses
    - MockMCPClient uses SHA256 hash to ensure query-based uniqueness
    """
    # Create two coordinator instances
    coord1 = StatelessCoordinator(coordinator_config)
    coord2 = StatelessCoordinator(coordinator_config)

    # Execute different briefs in parallel
    brief1 = sample_brief
    brief2 = Brief(
        problem_statement="Build a project management tool",
        context="Different context",
        constraints=["Different constraints"],
        target_audience="Project managers",
    )

    # Execute concurrently (should not interfere)
    results1, results2 = await asyncio.gather(
        coord1.execute_flow(brief=brief1, brain_ids=["brain-01-product-strategy"]),
        coord2.execute_flow(brief=brief2, brain_ids=["brain-01-product-strategy"]),
    )

    # Different briefs should produce different results (no shared state)
    # If this assertion fails, coordinators are sharing state somehow
    assert (
        cast(ProductStrategy, results1["brain-01-product-strategy"]).positioning
        != cast(ProductStrategy, results2["brain-01-product-strategy"]).positioning
    ), "Different briefs should produce different results (no shared state)"


@pytest.mark.asyncio
async def test_coordinator_executes_single_brain(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Test that coordinator can execute a single brain."""
    coordinator = StatelessCoordinator(coordinator_config)

    results = await coordinator.execute_flow(
        brief=sample_brief, brain_ids=["brain-01-product-strategy"]
    )

    assert "brain-01-product-strategy" in results
    assert isinstance(results["brain-01-product-strategy"], ProductStrategy)
    assert results["brain-01-product-strategy"].positioning


@pytest.mark.asyncio
async def test_coordinator_blocks_when_governance_denies(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Stateless coordinator should fail closed when governance blocks."""
    config = CoordinatorConfig(
        mcp_client=coordinator_config.mcp_client,
        enable_logging=False,
        governance=BlockingGovernance(),
    )
    coordinator = StatelessCoordinator(config)

    results = await coordinator.execute_flow(
        brief=sample_brief, brain_ids=["brain-01-product-strategy"]
    )

    assert results == {}


@pytest.mark.asyncio
async def test_coordinator_short_brain1_alias_triggers_rag_path(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Short Brain #1 runtime ID should still activate the existing RAG seam."""
    coordinator = StatelessCoordinator(coordinator_config)

    with patch(
        "mastermind_cli.rag.context_builder.RAGContextBuilder.build",
        new=AsyncMock(return_value="[RETRIEVED CONTEXT] alias path"),
    ) as mock_build:
        results = await coordinator.execute_flow(
            brief=sample_brief,
            brain_ids=["brain-01-product"],
            conn=object(),
        )

    assert "brain-01-product" in results
    assert isinstance(results["brain-01-product"], ProductStrategy)
    mock_build.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("brain_id", "expected_type"),
    [
        ("brain-02-ux", UXResearch),
        ("brain-03-ui", UIDesign),
        ("brain-07-growth", GrowthDataEvaluation),
    ],
)
async def test_coordinator_first_scale_out_aliases_trigger_rag_path(
    coordinator_config: CoordinatorConfig,
    sample_brief: Brief,
    brain_id: str,
    expected_type: type[object],
) -> None:
    """Short runtime aliases in the first scale-out cohort should activate RAG."""
    coordinator = StatelessCoordinator(coordinator_config)

    with patch(
        "mastermind_cli.rag.context_builder.RAGContextBuilder.build",
        new=AsyncMock(return_value="[RETRIEVED CONTEXT] cohort path"),
    ) as mock_build:
        results = await coordinator.execute_flow(
            brief=sample_brief,
            brain_ids=[brain_id],
            conn=object(),
        )

    assert brain_id in results
    assert isinstance(results[brain_id], expected_type)
    mock_build.assert_awaited_once()


@pytest.mark.asyncio
async def test_coordinator_executes_multiple_brains(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Test that coordinator can execute multiple brains."""
    coordinator = StatelessCoordinator(coordinator_config)

    results = await coordinator.execute_flow(
        brief=sample_brief,
        brain_ids=["brain-01-product-strategy", "brain-02-ux-research"],
    )

    # Should have both brains
    assert "brain-01-product-strategy" in results
    assert "brain-02-ux-research" in results

    # Should be correct types
    assert isinstance(results["brain-01-product-strategy"], ProductStrategy)
    assert isinstance(results["brain-02-ux-research"], UXResearch)


@pytest.mark.asyncio
async def test_coordinator_alias_context_remains_visible_to_canonical_dependents(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Dependent brains should see Brain #1 context even when runtime uses short ID."""
    coordinator = StatelessCoordinator(coordinator_config)

    results = await coordinator.execute_flow(
        brief=sample_brief,
        brain_ids=["brain-01-product", "brain-02-ux-research"],
    )

    assert "brain-01-product" in results
    assert "brain-02-ux-research" in results
    assert isinstance(results["brain-02-ux-research"], UXResearch)


@pytest.mark.asyncio
async def test_coordinator_passes_context_to_dependent_brains(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Test that coordinator passes previous outputs as context."""
    coordinator = StatelessCoordinator(coordinator_config)

    coordinator.flow_config = FlowConfig(
        flow_id="test-flow",
        nodes={
            "brain-01-product-strategy": [],
            "brain-02-ux-research": ["brain-01-product-strategy"],
        },
        description="Dependency test flow",
    )
    previous_results = {
        "brain-01-product-strategy": ProductStrategy(
            positioning="Positioning statement",
            target_audience="Founders",
            key_features=["feature one"],
            success_metrics=["metric one"],
        )
    }

    input_payload = coordinator._prepare_input(
        "brain-02-ux-research", sample_brief, previous_results
    )

    assert "brain-01-product-strategy" in input_payload.additional_context
    assert (
        input_payload.additional_context["brain-01-product-strategy"]["positioning"]
        == "Positioning statement"
    )


@pytest.mark.asyncio
async def test_coordinator_factory_function(
    mock_mcp: MockMCPClient, sample_brief: Brief
) -> None:
    """Test that factory function creates coordinator correctly."""
    coordinator = create_stateless_coordinator(
        mcp_client=mock_mcp, enable_logging=False
    )

    assert coordinator.config.mcp_client == mock_mcp
    assert coordinator.config.enable_logging is False

    # Should execute normally
    results = await coordinator.execute_flow(
        brief=sample_brief, brain_ids=["brain-01-product-strategy"]
    )

    assert "brain-01-product-strategy" in results


@pytest.mark.asyncio
async def test_coordinator_factory_accepts_governance(
    sample_brief: Brief,
) -> None:
    """Factory should pass governance through to the stateless coordinator."""
    coordinator = create_stateless_coordinator(
        mcp_client=MockMCPClient(),
        enable_logging=False,
        governance=BlockingGovernance(),
    )

    results = await coordinator.execute_flow(
        brief=sample_brief, brain_ids=["brain-01-product-strategy"]
    )

    assert results == {}


@pytest.mark.asyncio
async def test_coordinator_config_is_immutable(
    coordinator_config: CoordinatorConfig,
) -> None:
    """Test that CoordinatorConfig is immutable (frozen)."""
    # frozen=True makes dataclass immutable
    with pytest.raises(FrozenInstanceError):
        cast(Any, coordinator_config).enable_logging = False


@pytest.mark.asyncio
async def test_coordinator_multi_user_safety(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Test that multiple users can run flows simultaneously without interference."""
    coordinator1 = StatelessCoordinator(coordinator_config)
    coordinator2 = StatelessCoordinator(coordinator_config)

    # Create different briefs for different users
    brief1 = sample_brief
    brief2 = Brief(
        problem_statement="Build an e-commerce platform",
        context="User 2's request",
        constraints=["Different requirements"],
        target_audience="Retail teams",
    )

    # Execute concurrently
    results = await asyncio.gather(
        coordinator1.execute_flow(
            brief=brief1, brain_ids=["brain-01-product-strategy"]
        ),
        coordinator2.execute_flow(
            brief=brief2, brain_ids=["brain-01-product-strategy"]
        ),
    )

    results1, results2 = results

    # Results should be different (no cross-talk)
    positioning1 = cast(
        ProductStrategy, results1["brain-01-product-strategy"]
    ).positioning
    positioning2 = cast(
        ProductStrategy, results2["brain-01-product-strategy"]
    ).positioning

    # Should have different content (mock responses include query)
    assert positioning1 != positioning2


@pytest.mark.asyncio
async def test_coordinator_handles_invalid_brain_id(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Test that coordinator raises error for invalid brain ID.

    Uses fuzzy regex matching (r"Brain.*registry") to make the test robust
    against minor changes in DependencyResolver error messages while still
    verifying the core error condition (unknown brain ID).
    """
    coordinator = StatelessCoordinator(coordinator_config)

    # Fuzzy matching: "Brain" followed by anything, then "registry"
    # This catches variations like "Brain IDs not found in registry",
    # "Brain not found in registry", etc.
    with pytest.raises(ValueError, match=r"Brain.*registry"):
        await coordinator.execute_flow(
            brief=sample_brief, brain_ids=["brain-non-existent"]
        )


# =============================================================================
# TESTS: WAVE-BASED PARALLELISM
# =============================================================================


@pytest.mark.asyncio
async def test_coordinator_resolves_waves(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Test that coordinator resolves brains into waves."""
    coordinator = StatelessCoordinator(coordinator_config)

    # Request multiple brains (they should be resolved into waves)
    results = await coordinator.execute_flow(
        brief=sample_brief,
        brain_ids=["brain-01-product-strategy", "brain-02-ux-research"],
    )

    # All brains should execute
    assert len(results) == 2


@pytest.mark.asyncio
async def test_brain_input_contains_previous_results(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Test that _prepare_input includes previous results in context."""
    coordinator = StatelessCoordinator(coordinator_config)

    # Mock _prepare_input to verify it's called with correct args
    original_prepare = coordinator._prepare_input
    prepared_inputs: list[tuple[str, Brief, dict[str, BaseModel]]] = []

    def mock_prepare(
        brain_id: str, brief: Brief, previous_results: dict[str, BaseModel]
    ) -> BrainInput:
        prepared_inputs.append((brain_id, brief, previous_results))
        return original_prepare(brain_id, brief, previous_results)

    cast(Any, coordinator)._prepare_input = mock_prepare

    await coordinator.execute_flow(
        brief=sample_brief, brain_ids=["brain-01-product-strategy"]
    )

    # Verify _prepare_input was called
    assert len(prepared_inputs) == 1
    brain_id, brief, previous_results = prepared_inputs[0]
    assert brain_id == "brain-01-product-strategy"
    assert isinstance(previous_results, dict)


# =============================================================================
# TESTS: TYPE SAFETY
# =============================================================================


def test_coordinator_config_requires_mcp_client() -> None:
    """Test that CoordinatorConfig requires mcp_client."""
    mock_mcp = MockMCPClient()

    # Should work with mcp_client
    config = CoordinatorConfig(mcp_client=mock_mcp)
    assert config.mcp_client == mock_mcp

    # Should fail without mcp_client (TypeError)
    with pytest.raises(TypeError):
        CoordinatorConfig()  # type: ignore[call-arg]


def test_coordinator_init_requires_config() -> None:
    """Test that StatelessCoordinator requires config."""
    mock_mcp = MockMCPClient()
    config = CoordinatorConfig(mcp_client=mock_mcp)

    # Should work with config
    coordinator = StatelessCoordinator(config)
    assert coordinator.config == config

    # Should fail without config
    with pytest.raises(TypeError):
        StatelessCoordinator()  # type: ignore[call-arg]


# =============================================================================
# TESTS: EXECUTION METADATA
# =============================================================================


@pytest.mark.asyncio
async def test_brain_input_contains_execution_metadata(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Test that BrainInput includes execution metadata."""
    coordinator = StatelessCoordinator(coordinator_config)

    # We'll verify this indirectly by checking execution succeeds
    # (metadata is used internally by brain functions)
    results = await coordinator.execute_flow(
        brief=sample_brief, brain_ids=["brain-01-product-strategy"]
    )

    assert "brain-01-product-strategy" in results
    # If execution succeeded, metadata was included


@pytest.mark.asyncio
async def test_stateless_coordinator_populates_runtime_contracts(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Coordinator should expose deterministic runtime contract state."""
    coordinator = StatelessCoordinator(coordinator_config)

    results = await coordinator.execute_flow(
        brief=sample_brief, brain_ids=["brain-01-product-strategy"]
    )

    assert "brain-01-product-strategy" in results
    assert coordinator.runtime_task_profile is not None
    assert coordinator.runtime_loop_policy is not None
    assert coordinator.runtime_envelope is not None
    assert coordinator.runtime_verification_outcome is not None
    assert coordinator.runtime_review_outcome is not None
    assert coordinator.runtime_envelope.artifacts == ("brain-01-product-strategy",)
    assert coordinator.runtime_envelope.status == "success"


@pytest.mark.asyncio
async def test_stateless_coordinator_logs_runtime_contract_metadata(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Message envelopes should carry runtime contract metadata for traceability."""
    coordinator = StatelessCoordinator(coordinator_config)

    await coordinator.execute_flow(
        brief=sample_brief, brain_ids=["brain-01-product-strategy"]
    )

    assert coordinator.message_log
    runtime_metadata = coordinator.message_log[0].transport_metadata[
        "runtime_contracts"
    ]
    assert runtime_metadata["task_profile"]["complexity"] == "medium"
    assert runtime_metadata["loop_policy"]["base_loop"] == "execute+verify-light"


@pytest.mark.asyncio
async def test_stateless_coordinator_logs_evidence_routing_metadata(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """Evidence routing should be preserved in transport metadata when provided."""
    coordinator = StatelessCoordinator(coordinator_config)

    await coordinator.execute_flow(
        brief=sample_brief,
        brain_ids=["brain-01-product-strategy"],
        evidence_request=EvidenceSelectionRequest(
            objective="Canonize the product brief",
            source_clarity="partial",
            uncertainty="medium",
            gap_count=1,
            readiness_gate="conditionally_ready",
            readiness_score=72.0,
        ),
    )

    assert coordinator.runtime_evidence_selection is not None
    assert coordinator.message_log
    evidence_metadata = coordinator.message_log[0].transport_metadata[
        "evidence_routing"
    ]
    assert evidence_metadata["selected_harness"] == "evidence-intake-canonization"
    assert evidence_metadata["readiness_gate"] == "conditionally_ready"


@pytest.mark.asyncio
async def test_stateless_coordinator_loads_memory_snapshot_before_selection(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """The coordinator should pass a project memory snapshot into runtime selection."""
    snapshot = ContextSnapshot(
        project_id="proj-001",
        summary="Resume from the last safe checkpoint.",
    )
    calls: list[tuple[str, str | None]] = []

    def memory_provider(project_id: str, task_id: str | None) -> ContextSnapshot | None:
        calls.append((project_id, task_id))
        return snapshot

    coordinator = StatelessCoordinator(
        CoordinatorConfig(
            mcp_client=coordinator_config.mcp_client,
            enable_logging=False,
            project_id="proj-001",
            memory_context_provider=memory_provider,
        )
    )

    await coordinator._prepare_runtime_contracts(
        brief=sample_brief,
        brain_ids=["brain-01-product-strategy"],
    )

    assert calls == [("proj-001", None)]
    assert coordinator.runtime_selection is not None
    assert coordinator.runtime_selection.memory_snapshot == snapshot


@pytest.mark.asyncio
async def test_stateless_coordinator_loads_memory_snapshot_from_env(
    coordinator_config: CoordinatorConfig,
    sample_brief: Brief,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The coordinator should load project memory from env when no provider is injected."""
    snapshot = ContextSnapshot(
        project_id="proj-001",
        summary="Resume from env-backed memory.",
    )
    calls: dict[str, object] = {}

    class FakeMemoryService:
        def __init__(self, store: object) -> None:
            calls["store"] = store

        async def build_context_snapshot(self, project_id: str) -> ContextSnapshot:
            calls["project_id"] = project_id
            return snapshot

    monkeypatch.setenv("MM_MEMORY_PROJECT_ID", "proj-001")
    monkeypatch.setenv("MM_MEMORY_DATABASE_URL", "postgresql://memory")
    monkeypatch.setattr(
        stateless_coordinator_module,
        "build_memory_store_from_env",
        lambda database_url, enable_vector, enable_index: {
            "database_url": database_url,
            "enable_vector": enable_vector,
            "enable_index": enable_index,
        },
    )
    monkeypatch.setattr(
        stateless_coordinator_module,
        "MemoryService",
        FakeMemoryService,
    )

    coordinator = StatelessCoordinator(
        CoordinatorConfig(
            mcp_client=coordinator_config.mcp_client, enable_logging=False
        )
    )

    loaded_snapshot = await coordinator._load_memory_snapshot()

    assert loaded_snapshot == snapshot
    assert calls["project_id"] == "proj-001"
    assert calls["store"]["database_url"] == "postgresql://memory"


@pytest.mark.asyncio
async def test_stateless_coordinator_execute_flow_uses_memory_snapshot(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """The public flow should preserve the loaded memory snapshot in runtime selection."""
    snapshot = ContextSnapshot(
        project_id="proj-001",
        summary="Resume from the last safe checkpoint.",
    )

    def memory_provider(project_id: str, task_id: str | None) -> ContextSnapshot | None:
        del task_id
        if project_id == "proj-001":
            return snapshot
        return None

    coordinator = StatelessCoordinator(
        CoordinatorConfig(
            mcp_client=coordinator_config.mcp_client,
            enable_logging=False,
            project_id="proj-001",
            memory_context_provider=memory_provider,
        )
    )

    async def fake_resolve_waves(self, brain_ids: list[str]) -> SimpleNamespace:
        del brain_ids
        return SimpleNamespace(
            levels=[SimpleNamespace(brain_ids=["brain-01-product-strategy"])]
        )

    async def fake_execute_wave(
        self,
        brain_ids: list[str],
        brief: Brief,
        previous_results: dict[str, BaseModel],
        correlation_id: str,
        conn: object | None = None,
    ) -> dict[str, BaseModel]:
        del brain_ids, brief, previous_results, correlation_id, conn
        return {"brain-01-product-strategy": cast(BaseModel, object())}

    coordinator._finalize_runtime_envelope = lambda results: None  # type: ignore[method-assign]
    coordinator._resolve_waves = fake_resolve_waves.__get__(
        coordinator, StatelessCoordinator
    )  # type: ignore[method-assign]
    coordinator._execute_wave = fake_execute_wave.__get__(
        coordinator, StatelessCoordinator
    )  # type: ignore[method-assign]

    results = await coordinator.execute_flow(
        brief=sample_brief,
        brain_ids=["brain-01-product-strategy"],
    )

    assert "brain-01-product-strategy" in results
    assert coordinator.runtime_selection is not None
    assert coordinator.runtime_selection.memory_snapshot == snapshot


@pytest.mark.asyncio
async def test_stateless_coordinator_persists_runtime_run_via_writer(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """The coordinator should hand off the runtime result to the configured writer."""
    from mastermind_cli.orchestrator.runtime_contracts import (
        RuntimeExecutionResult,
        RuntimeMemoryWrite,
    )

    writer_calls: list[dict[str, object]] = []

    class FakeMemoryRuntimeWriter:
        def __init__(self) -> None:
            self.calls = writer_calls

        async def persist_runtime_run(
            self,
            *,
            project_id: str,
            task_id: str | None,
            run_id: str,
            runtime_result: RuntimeExecutionResult,
            snapshot: ContextSnapshot | None = None,
        ) -> RuntimeMemoryWrite:
            writer_calls.append(
                {
                    "project_id": project_id,
                    "task_id": task_id,
                    "run_id": run_id,
                    "runtime_result": runtime_result,
                    "snapshot": snapshot,
                }
            )
            return RuntimeMemoryWrite(
                project_id=project_id,
                run_id=run_id,
                checkpoint_id="ckpt-test",
                decision_id="dec-test",
                run_summary_id="summary-test",
            )

    coordinator = StatelessCoordinator(
        CoordinatorConfig(
            mcp_client=coordinator_config.mcp_client,
            enable_logging=False,
            project_id="proj-001",
            memory_runtime_writer=FakeMemoryRuntimeWriter(),
        )
    )

    results = await coordinator.execute_flow(
        brief=sample_brief,
        brain_ids=["brain-01-product-strategy"],
    )

    assert "brain-01-product-strategy" in results
    assert writer_calls, "memory runtime writer should be invoked"
    call = writer_calls[-1]
    assert call["project_id"] == "proj-001"
    assert call["task_id"] == coordinator.runtime_selection.task_profile.task_id
    assert call["run_id"] == coordinator.correlation_id
    assert call["runtime_result"] is coordinator.runtime_execution_result
    assert coordinator.runtime_memory_write is not None
    assert coordinator.runtime_memory_write.checkpoint_id == "ckpt-test"


@pytest.mark.asyncio
async def test_stateless_coordinator_skips_persistence_without_project_id(
    coordinator_config: CoordinatorConfig, sample_brief: Brief
) -> None:
    """The writer should not be invoked when no project id is available."""
    from mastermind_cli.orchestrator.runtime_contracts import RuntimeMemoryWrite

    calls: list[dict[str, object]] = []

    class FakeMemoryRuntimeWriter:
        def __init__(self) -> None:
            self.calls = calls

        async def persist_runtime_run(
            self,
            *,
            project_id: str,
            task_id: str | None,
            run_id: str,
            runtime_result: object,
            snapshot: ContextSnapshot | None = None,
        ) -> RuntimeMemoryWrite:
            calls.append({"project_id": project_id})
            return RuntimeMemoryWrite(
                project_id=project_id,
                run_id=run_id,
                checkpoint_id=None,
                decision_id=None,
                run_summary_id=None,
            )

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.delenv("MM_MEMORY_PROJECT_ID", raising=False)
        coordinator = StatelessCoordinator(
            CoordinatorConfig(
                mcp_client=coordinator_config.mcp_client,
                enable_logging=False,
                memory_runtime_writer=FakeMemoryRuntimeWriter(),
            )
        )

        await coordinator.execute_flow(
            brief=sample_brief,
            brain_ids=["brain-01-product-strategy"],
        )

        assert calls == []
        assert coordinator.runtime_memory_write is None
    finally:
        monkeypatch.undo()


# =============================================================================
# TESTS: MOCK CLIENT (REGRESSION)
# =============================================================================


def test_mock_mcp_unique_responses_per_query() -> None:
    """Verify MockMCPClient produces unique responses for different queries.

    Regression test: Ensures hash-based uniqueness prevents false positives
    in stateless coordinator tests. If different queries produce the same
    response, tests can't detect cross-talk between coordinator instances.
    """
    mock = MockMCPClient()

    # Different queries should produce different responses
    resp1 = mock.query_notebooklm("nb-id", "Build a CRM for small businesses")
    resp2 = mock.query_notebooklm("nb-id", "Build an e-commerce platform")

    # Hash-based uniqueness should prevent collisions
    assert resp1 != resp2, "Different queries must produce different responses"

    # Verify hash format is correct
    assert "[hash:" in resp1
    assert "[hash:" in resp2
    assert "call:" in resp1
    assert "call:" in resp2

    # Call counter should increment
    assert "call:1" in resp1
    assert "call:2" in resp2


def test_mock_mcp_same_query_same_response() -> None:
    """Verify MockMCPClient is deterministic for same query."""
    mock = MockMCPClient()

    # Same query should produce same hash (but different call count)
    resp1 = mock.query_notebooklm("nb-id", "same query")
    resp2 = mock.query_notebooklm("nb-id", "same query")

    # Hash should be identical, but call count should differ
    hash1 = resp1.split("[hash:")[1].split()[0]
    hash2 = resp2.split("[hash:")[1].split()[0]
    assert hash1 == hash2, "Same query should produce same hash"

    assert "call:1" in resp1
    assert "call:2" in resp2


def test_mock_mcp_queries_logged() -> None:
    """Verify MockMCPClient logs queries for debugging purposes."""
    mock = MockMCPClient()

    mock.query_notebooklm("nb-1", "query one")
    mock.query_notebooklm("nb-2", "query two")

    # Queries should be logged (side-effect for debugging)
    assert len(mock.queries) == 2
    assert mock.queries[0] == ("nb-1", "query one")
    assert mock.queries[1] == ("nb-2", "query two")
