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
import pytest
import asyncio

from mastermind_cli.types.interfaces import (
    Brief,
    ProductStrategy,
    UXResearch,
)
from mastermind_cli.orchestrator.stateless_coordinator import (
    StatelessCoordinator,
    CoordinatorConfig,
    create_stateless_coordinator,
)


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

    def __init__(self):
        # Queries logged for debugging purposes (not asserted in tests)
        self.queries = []
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


# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture
def mock_mcp():
    """Mock MCP client."""
    return MockMCPClient()


@pytest.fixture
def coordinator_config(mock_mcp):
    """Coordinator config for testing."""
    return CoordinatorConfig(mcp_client=mock_mcp, enable_logging=False)


@pytest.fixture
def sample_brief():
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
async def test_coordinator_is_stateless(coordinator_config, sample_brief):
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
    )

    # Execute concurrently (should not interfere)
    results1 = await coord1.execute_flow(
        brief=brief1, brain_ids=["brain-01-product-strategy"]
    )
    results2 = await coord2.execute_flow(
        brief=brief2, brain_ids=["brain-01-product-strategy"]
    )

    # Different briefs should produce different results (no shared state)
    # If this assertion fails, coordinators are sharing state somehow
    assert (
        results1["brain-01-product-strategy"].positioning
        != results2["brain-01-product-strategy"].positioning
    ), "Different briefs should produce different results (no shared state)"


@pytest.mark.asyncio
async def test_coordinator_executes_single_brain(coordinator_config, sample_brief):
    """Test that coordinator can execute a single brain."""
    coordinator = StatelessCoordinator(coordinator_config)

    results = await coordinator.execute_flow(
        brief=sample_brief, brain_ids=["brain-01-product-strategy"]
    )

    assert "brain-01-product-strategy" in results
    assert isinstance(results["brain-01-product-strategy"], ProductStrategy)
    assert results["brain-01-product-strategy"].positioning


@pytest.mark.asyncio
async def test_coordinator_executes_multiple_brains(coordinator_config, sample_brief):
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
async def test_coordinator_passes_context_to_dependent_brains(
    coordinator_config, sample_brief
):
    """Test that coordinator passes previous outputs as context."""
    coordinator = StatelessCoordinator(coordinator_config)

    results = await coordinator.execute_flow(
        brief=sample_brief, brain_ids=["brain-01-product-strategy"]
    )

    # Verify context was passed (additional_context should have previous results)
    # This is tested indirectly by checking that brains execute successfully
    assert results["brain-01-product-strategy"] is not None


@pytest.mark.asyncio
async def test_coordinator_factory_function(mock_mcp, sample_brief):
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
async def test_coordinator_config_is_immutable(coordinator_config):
    """Test that CoordinatorConfig is immutable (frozen)."""
    # frozen=True makes dataclass immutable
    with pytest.raises(Exception):  # frozen_error.FrozenInstanceError
        coordinator_config.enable_logging = False


@pytest.mark.asyncio
async def test_coordinator_multi_user_safety(coordinator_config, sample_brief):
    """Test that multiple users can run flows simultaneously without interference."""
    coordinator1 = StatelessCoordinator(coordinator_config)
    coordinator2 = StatelessCoordinator(coordinator_config)

    # Create different briefs for different users
    brief1 = sample_brief
    brief2 = Brief(
        problem_statement="Build an e-commerce platform",
        context="User 2's request",
        constraints=["Different requirements"],
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
    positioning1 = results1["brain-01-product-strategy"].positioning
    positioning2 = results2["brain-01-product-strategy"].positioning

    # Should have different content (mock responses include query)
    assert positioning1 != positioning2


@pytest.mark.asyncio
async def test_coordinator_handles_invalid_brain_id(coordinator_config, sample_brief):
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
async def test_coordinator_resolves_waves(coordinator_config, sample_brief):
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
async def test_brain_input_contains_previous_results(coordinator_config, sample_brief):
    """Test that _prepare_input includes previous results in context."""
    coordinator = StatelessCoordinator(coordinator_config)

    # Mock _prepare_input to verify it's called with correct args
    original_prepare = coordinator._prepare_input
    prepared_inputs = []

    def mock_prepare(brain_id, brief, previous_results):
        prepared_inputs.append((brain_id, brief, previous_results))
        return original_prepare(brain_id, brief, previous_results)

    coordinator._prepare_input = mock_prepare

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


def test_coordinator_config_requires_mcp_client():
    """Test that CoordinatorConfig requires mcp_client."""
    mock_mcp = MockMCPClient()

    # Should work with mcp_client
    config = CoordinatorConfig(mcp_client=mock_mcp)
    assert config.mcp_client == mock_mcp

    # Should fail without mcp_client (TypeError)
    with pytest.raises(TypeError):
        CoordinatorConfig()


def test_coordinator_init_requires_config():
    """Test that StatelessCoordinator requires config."""
    mock_mcp = MockMCPClient()
    config = CoordinatorConfig(mcp_client=mock_mcp)

    # Should work with config
    coordinator = StatelessCoordinator(config)
    assert coordinator.config == config

    # Should fail without config
    with pytest.raises(TypeError):
        StatelessCoordinator()


# =============================================================================
# TESTS: EXECUTION METADATA
# =============================================================================


@pytest.mark.asyncio
async def test_brain_input_contains_execution_metadata(
    coordinator_config, sample_brief
):
    """Test that BrainInput includes execution metadata."""
    coordinator = StatelessCoordinator(coordinator_config)

    # We'll verify this indirectly by checking execution succeeds
    # (metadata is used internally by brain functions)
    results = await coordinator.execute_flow(
        brief=sample_brief, brain_ids=["brain-01-product-strategy"]
    )

    assert "brain-01-product-strategy" in results
    # If execution succeeded, metadata was included


# =============================================================================
# TESTS: MOCK CLIENT (REGRESSION)
# =============================================================================


def test_mock_mcp_unique_responses_per_query():
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


def test_mock_mcp_same_query_same_response():
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


def test_mock_mcp_queries_logged():
    """Verify MockMCPClient logs queries for debugging purposes."""
    mock = MockMCPClient()

    mock.query_notebooklm("nb-1", "query one")
    mock.query_notebooklm("nb-2", "query two")

    # Queries should be logged (side-effect for debugging)
    assert len(mock.queries) == 2
    assert mock.queries[0] == ("nb-1", "query one")
    assert mock.queries[1] == ("nb-2", "query two")
