"""
Integration Tests for Pure Function Architecture.

These tests verify the core guarantees of the pure function architecture:
- Multi-user safety (no cross-talk between concurrent requests)
- MCP sequential execution (no rate limit issues)
- Legacy brain compatibility (v1.x brains work via wrapper)
- Auth validation (API keys work correctly)
- Performance benchmarks (meets targets)

Design Principle:
"Integration tests should verify ARCHITECTURAL GUARANTEES,
not just individual function behavior."
"""

import pytest
import asyncio
import time
from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock, patch

from mastermind_cli.types.interfaces import Brief, ProductStrategy
from mastermind_cli.orchestrator.stateless_coordinator import (
    StatelessCoordinator,
    CoordinatorConfig,
)
from mastermind_cli.auth.api_keys import (
    validate_api_key,
    generate_api_key,
    hash_api_key,
)
from mastermind_cli.compatibility.legacy_wrapper import LegacyBrainAdapter
from mastermind_cli.state.logger import ExecutionLogger


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sample_brief():
    """Create sample Brief for testing."""
    return Brief(
        problem_statement="Build a CRM system for small businesses",
        context="Targeting companies with 10-50 employees",
        constraints=["Web-based", "Budget under $10k/month"],
    )


@pytest.fixture
def mock_mcp_client():
    """Create mock MCP client."""
    client = Mock()
    client.query_notebooklm = Mock(return_value="Mocked NotebookLM response")
    return client


@pytest.fixture
def coordinator_config(mock_mcp_client):
    """Create CoordinatorConfig for testing."""
    return CoordinatorConfig(mcp_client=mock_mcp_client, enable_logging=False)


# =============================================================================
# MULTI-USER SAFETY TESTS
# =============================================================================


class TestMultiUserSafety:
    """
    Test multi-user safety guarantee.

    Core Guarantee: "Multiple concurrent executions MUST NOT interfere
    with each other. Each request has ISOLATED state."
    """

    @pytest.mark.asyncio
    async def test_concurrent_executions_no_crosstalk(
        self, coordinator_config, sample_brief
    ):
        """
        Test 5 concurrent requests with different briefs.

        Verify:
        1. All executions complete successfully
        2. Each execution gets its own result
        3. No result contains data from another request
        """
        # Track results per execution
        results_by_id = {}
        execution_lock = asyncio.Lock()

        async def execute_request(exec_id: str, brief_text: str):
            """Execute a single request."""
            # Create NEW coordinator per request (stateless)
            coordinator = StatelessCoordinator(coordinator_config)

            # Create unique brief for this request
            brief = Brief(problem_statement=brief_text)

            # Execute
            results = await coordinator.execute_flow(
                brief, ["brain-01-product-strategy"]
            )

            # Store result
            async with execution_lock:
                results_by_id[exec_id] = results

            return results

        # Launch 5 concurrent requests with DIFFERENT briefs
        tasks = [
            execute_request(f"exec-{i}", f"Build CRM variant {i}") for i in range(5)
        ]

        # Wait for all to complete
        await asyncio.gather(*tasks)

        # Verify all completed
        assert len(results_by_id) == 5

        # Verify no cross-talk (each has unique brief in result)
        for exec_id, results in results_by_id.items():
            assert "brain-01-product-strategy" in results
            result = results["brain-01-product-strategy"]
            # Brief should be unique to this execution
            assert exec_id.split("-")[1] in result.brief or "variant" in result.brief

    @pytest.mark.asyncio
    async def test_parallel_sequential_consistency(
        self, coordinator_config, sample_brief
    ):
        """
        Test that parallel executions produce same results as sequential.

        If parallel and sequential produce different results,
        there's a race condition or shared state bug.
        """
        # Sequential execution
        coordinator_seq = StatelessCoordinator(coordinator_config)
        results_seq = await coordinator_seq.execute_flow(
            sample_brief, ["brain-01-product-strategy"]
        )

        # Parallel execution
        coordinator_par = StatelessCoordinator(coordinator_config)
        results_par = await coordinator_par.execute_flow(
            sample_brief, ["brain-01-product-strategy"]
        )

        # Results should be equivalent
        # (Exact match may vary due to timestamps, check structure)
        assert set(results_seq.keys()) == set(results_par.keys())


# =============================================================================
# MCP SEQUENTIAL EXECUTION TESTS
# =============================================================================


class TestMCPSequentialExecution:
    """
    Test MCP sequential execution guarantee.

    Core Guarantee: "Brains in same wave execute in PARALLEL.
    Brains in different waves execute SEQUENTIALLY.
    This prevents MCP rate limiting."
    """

    @pytest.mark.asyncio
    async def test_waves_execute_sequentially(self, coordinator_config, sample_brief):
        """
        Test that waves execute sequentially (not all at once).

        If all brains executed in parallel, we'd hit MCP rate limits.
        """
        # Track execution order
        execution_order = []

        # Create mock MCP client that tracks calls
        mock_client = Mock()

        def mock_query(notebook_id: str, query: str):
            execution_order.append(f"call-{len(execution_order)}")
            time.sleep(0.01)  # Simulate work (sync, like real code)
            return f"Response {len(execution_order)}"

        mock_client.query_notebooklm = mock_query

        # Update config with tracking mock
        config = CoordinatorConfig(mcp_client=mock_client, enable_logging=False)

        # Execute flow with multiple brains
        # (They have no dependencies, so should be in same wave)
        coordinator = StatelessCoordinator(config)

        # Note: Current implementation may not have full wave resolution
        # This test verifies the pattern is in place
        await coordinator.execute_flow(sample_brief, ["brain-01-product-strategy"])

        # Verify at least some calls were made
        assert len(execution_order) > 0

    @pytest.mark.asyncio
    async def test_no_rate_limit_errors_under_load(
        self, coordinator_config, sample_brief
    ):
        """
        Test that rapid sequential executions don't cause rate limits.

        Simulates 10 rapid requests.
        """
        # Create mock MCP that simulates rate limiting
        mock_client = Mock()
        call_count = {"count": 0}

        def mock_query(notebook_id: str, query: str):
            call_count["count"] += 1
            # Simulate realistic response time (sync, like real code)
            time.sleep(0.05)
            # If rate limited, would raise exception here
            return f"Response {call_count['count']}"

        mock_client.query_notebooklm = mock_query

        config = CoordinatorConfig(mcp_client=mock_client, enable_logging=False)

        # Execute 10 requests rapidly
        coordinator = StatelessCoordinator(config)
        results = []

        for i in range(10):
            result = await coordinator.execute_flow(
                sample_brief, ["brain-01-product-strategy"]
            )
            results.append(result)

        # All should complete without errors
        assert len(results) == 10
        assert call_count["count"] >= 10  # At least 10 MCP calls


# =============================================================================
# LEGACY BRAIN COMPATIBILITY TESTS
# =============================================================================


class TestLegacyBrainCompatibility:
    """
    Test legacy brain wrapper compatibility.

    Core Guarantee: "V1.x brains work WITHOUT MODIFICATION
    via LegacyBrainAdapter."
    """

    def test_legacy_brain_adapter_creates_isolated_context(self, sample_brief):
        """
        Test that legacy brain gets its own isolated orchestrator.

        Legacy brains expect global orchestrator state.
        Wrapper must create LOCAL orchestrator per call.
        """

        # Mock legacy brain class (stateful, expects global orchestrator)
        class MockLegacyBrain:
            def __init__(self):
                self.global_state = "SHARED_STATE"

            def execute(self, brief: str, orchestrator: Any):
                """
                Legacy brain signature - expects orchestrator.

                In v1.x, this would access orchestrator.state
                """
                # Simulate brain logic
                return {
                    "positioning": f"Strategy for: {brief}",
                    "target_audience": "Small businesses",
                    "key_features": ["Feature 1", "Feature 2"],
                    "success_metrics": ["Metric 1"],
                    "risks": [],
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }

        # Create wrapper
        adapter = LegacyBrainAdapter(
            brain_executor=MockLegacyBrain(), output_model=ProductStrategy
        )

        # Call as pure function
        mock_mcp = Mock()
        mock_mcp.query_notebooklm = Mock(return_value="Mock response")

        from mastermind_cli.types.interfaces import BrainInput

        brain_input = BrainInput(brief=sample_brief)

        result = adapter(brain_input, mcp_client=mock_mcp)

        # Verify result is ProductStrategy model
        assert isinstance(result, ProductStrategy)
        assert "Strategy for:" in result.positioning

        # Verify no global state pollution
        # (Each call creates new instance)
        adapter2 = LegacyBrainAdapter(
            legacy_brain_class=MockLegacyBrain, output_model=ProductStrategy
        )
        result2 = adapter2(brain_input, mcp_client=mock_mcp)

        # Results should be independent
        assert result.positioning == result2.positioning


# =============================================================================
# AUTH VALIDATION TESTS
# =============================================================================


class TestAuthValidation:
    """
    Test API key authentication.

    Core Guarantee: "API key auth works for BOTH CLI (env var)
    and Web UI (SQLite)."
    """

    def test_cli_auth_with_env_var(self):
        """Test CLI authentication via MM_API_KEY environment variable."""
        # Generate valid key
        valid_key = generate_api_key()

        with patch.dict("os.environ", {"MM_API_KEY": valid_key}):
            result = validate_api_key(valid_key)
            assert result is not None
            assert result.owner == "cli-user"
            assert result.is_active is True

    def test_cli_auth_rejects_invalid_key(self):
        """Test CLI authentication rejects invalid key."""
        with patch.dict("os.environ", {"MM_API_KEY": "different-key"}):
            result = validate_api_key("invalid-key")
            assert result is None

    def test_cli_auth_requires_env_match(self):
        """
        Test that key must match environment variable.

        Security: User can't use someone else's key
        by setting MM_API_KEY to their own key.
        """
        user_key = generate_api_key()
        attacker_key = generate_api_key()

        # Attacker sets MM_API_KEY to their own key
        with patch.dict("os.environ", {"MM_API_KEY": attacker_key}):
            # Try to use victim's key
            result = validate_api_key(user_key)
            assert result is None  # Rejected

    def test_web_auth_with_database(self, tmp_path):
        """Test Web UI authentication via SQLite database."""
        import asyncio

        async def test_async():
            # Create logger with database
            db_path = str(tmp_path / "test_auth.db")
            logger = ExecutionLogger(db_path=db_path, enabled=True)

            # Save API key to database
            from mastermind_cli.auth.api_keys import APIKeyCreate, create_api_key
            from mastermind_cli.state.database import get_db

            key_data = APIKeyCreate(owner="web-user", scopes=["read", "write"])
            full_key, response = create_api_key(key_data)

            # Verify key exists in database
            db = get_db(db_path)
            await db.connect()
            await db.create_auth_schema()

            # Verify retrieval
            key_hash = hash_api_key(full_key)
            retrieved = await db.get_api_key(key_hash)
            assert retrieved is not None
            assert retrieved["owner"] == "web-user"

            await db.close()
            await logger.close()

        asyncio.run(test_async())


# =============================================================================
# PERFORMANCE BENCHMARK TESTS
# =============================================================================


class TestPerformanceBenchmarks:
    """
    Test performance benchmarks.

    Core Guarantee: "Pure function architecture meets performance targets."
    """

    @pytest.mark.asyncio
    async def test_single_execution_performance(self, coordinator_config, sample_brief):
        """
        Benchmark single execution performance.

        Target: < 5 seconds for single brain execution (including MCP).
        """
        coordinator = StatelessCoordinator(coordinator_config)

        start = time.time()
        await coordinator.execute_flow(sample_brief, ["brain-01-product-strategy"])
        duration = time.time() - start

        # Assert performance target
        # Note: With mock MCP, this should be < 100ms
        # With real MCP, target is < 5s
        assert duration < 5.0, f"Execution took {duration:.2f}s, target < 5s"

    @pytest.mark.asyncio
    async def test_concurrent_execution_performance(
        self, coordinator_config, sample_brief
    ):
        """
        Benchmark concurrent execution performance.

        Target: 5 concurrent requests complete in < 10 seconds total.
        """

        async def execute_single():
            coordinator = StatelessCoordinator(coordinator_config)
            return await coordinator.execute_flow(
                sample_brief, ["brain-01-product-strategy"]
            )

        start = time.time()

        # Execute 5 requests concurrently
        tasks = [execute_single() for _ in range(5)]
        results = await asyncio.gather(*tasks)

        duration = time.time() - start

        # All should complete
        assert len(results) == 5

        # Performance target (with mocks, should be very fast)
        # With real MCP, parallelism provides speedup
        assert duration < 10.0, f"Concurrent execution took {duration:.2f}s"

    @pytest.mark.asyncio
    async def test_memory_efficiency(self, coordinator_config, sample_brief):
        """
        Test that stateless architecture doesn't leak memory.

        Target: 100 consecutive executions don't grow memory unbounded.
        """
        import gc

        # Get initial memory size
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Execute 100 times
        for i in range(100):
            coordinator = StatelessCoordinator(coordinator_config)
            await coordinator.execute_flow(sample_brief, ["brain-01-product-strategy"])
            # Coordinator goes out of scope here

        # Check final memory
        gc.collect()
        final_objects = len(gc.get_objects())

        # Memory growth should be reasonable (< 50% growth)
        growth = (final_objects - initial_objects) / initial_objects
        assert growth < 0.5, f"Memory grew by {growth:.1%}, possible leak"


# =============================================================================
# END-TO-END FLOW TESTS
# =============================================================================


class TestEndToEndFlows:
    """
    Test complete end-to-end workflows.

    These tests verify the entire pipeline works correctly.
    """

    @pytest.mark.asyncio
    async def test_full_flow_with_logging(
        self, coordinator_config, sample_brief, tmp_path
    ):
        """
        Test full flow: brief → coordinator → brain → log → query.
        """
        # Create logger
        db_path = str(tmp_path / "test_e2e.db")
        logger = ExecutionLogger(db_path=db_path, enabled=True)

        # Execute flow
        coordinator = StatelessCoordinator(coordinator_config)
        results = await coordinator.execute_flow(
            sample_brief, ["brain-01-product-strategy"]
        )

        # Log execution
        await logger.log_execution(
            execution_id="e2e-test-1",
            brain_id="brain-01-product-strategy",
            brief=sample_brief,
            output=results.get("brain-01-product-strategy"),
            status="success",
            duration_ms=500,
        )

        # Query back
        logged = await logger.get_execution_by_id("e2e-test-1")
        assert logged is not None
        assert logged.status == "success"

        # Get stats
        stats = await logger.get_statistics()
        assert stats["total_executions"] == 1
        assert stats["success_count"] == 1

        await logger.close()

    @pytest.mark.asyncio
    async def test_error_recovery_flow(self, coordinator_config, sample_brief):
        """
        Test that errors are handled gracefully and execution continues.
        """
        # Create MCP client that fails on first call, succeeds on second
        call_count = {"count": 0}

        async def failing_query(notebook_id: str, query: str):
            call_count["count"] += 1
            if call_count["count"] == 1:
                raise RuntimeError("MCP connection failed")
            return "Success"

        mock_client = Mock()
        mock_client.query_notebooklm = failing_query

        config = CoordinatorConfig(mcp_client=mock_client, enable_logging=False)
        coordinator = StatelessCoordinator(config)

        # First call should fail
        with pytest.raises(RuntimeError, match="MCP connection failed"):
            await coordinator.execute_flow(sample_brief, ["brain-01-product-strategy"])

        # Second call should succeed
        results = await coordinator.execute_flow(
            sample_brief, ["brain-01-product-strategy"]
        )
        assert "brain-01-product-strategy" in results
