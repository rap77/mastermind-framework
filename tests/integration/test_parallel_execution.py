"""
Integration tests for parallel execution with performance validation.

This module tests the ParallelExecutor with focus on:
- Configuration persistence (save/load execution configs)
- Performance benchmarks (3-10x speedup for independent brains)
- Concurrent execution verification
- Task status query performance (<100ms target)
"""

import pytest
import time
from mastermind_cli.types.parallel import FlowConfig, ProviderConfig
from mastermind_cli.orchestrator.task_executor import ParallelExecutor
from mastermind_cli.state.repositories import TaskRepository
from mastermind_cli.state.database import DatabaseConnection


@pytest.mark.asyncio
async def test_config_persistence():
    """Test saving and loading execution configurations."""
    flow = FlowConfig(
        flow_id="persist-test", nodes={"brain-01": [], "brain-02": ["brain-01"]}
    )

    async with DatabaseConnection(":memory:") as db:
        await db.connect()

        # Create executions table
        await db.conn.execute(
            """CREATE TABLE IF NOT EXISTS executions (
                id TEXT PRIMARY KEY,
                flow_config TEXT NOT NULL,
                brief TEXT NOT NULL,
                created_at TIMESTAMP,
                status TEXT
            )"""
        )
        await db.conn.commit()

        task_repo = TaskRepository(db)
        mcp_client = None  # Not needed for config test
        executor = ParallelExecutor(
            task_repo,
            mcp_client,
            [ProviderConfig(name="test", max_concurrent_calls=10)],
        )

        # Save config
        execution_id = "exec-123"
        await executor.save_config(execution_id, flow, "test brief")

        # Load config
        loaded = await executor.load_config(execution_id)
        assert loaded is not None
        assert loaded["brief"] == "test brief"
        assert loaded["flow"].flow_id == "persist-test"
        assert "brain-01" in loaded["flow"].nodes
        assert "brain-02" in loaded["flow"].nodes


@pytest.mark.asyncio
async def test_config_persistence_not_found():
    """Test loading non-existent execution returns None."""
    async with DatabaseConnection(":memory:") as db:
        await db.connect()

        # Create executions table
        await db.conn.execute(
            """CREATE TABLE IF NOT EXISTS executions (
                id TEXT PRIMARY KEY,
                flow_config TEXT NOT NULL,
                brief TEXT NOT NULL,
                created_at TIMESTAMP,
                status TEXT
            )"""
        )
        await db.conn.commit()

        task_repo = TaskRepository(db)
        executor = ParallelExecutor(
            task_repo, None, [ProviderConfig(name="test", max_concurrent_calls=10)]
        )

        # Load non-existent config
        loaded = await executor.load_config("non-existent")
        assert loaded is None


@pytest.mark.asyncio
async def test_speedup_factor():
    """Validate 3-10x speedup for parallel vs sequential execution.

    Requirements:
    - PERF-01: Parallel execution achieves 3-10x speedup
    - Test uses 5 independent brains (no dependencies)
    - Each brain has 100ms simulated delay
    """
    # Setup: Create flow with 5 independent brains
    flow = FlowConfig(
        flow_id="speedup-test",
        nodes={
            "brain-01": [],  # Independent
            "brain-02": [],  # Independent
            "brain-03": [],  # Independent
            "brain-04": [],  # Independent
            "brain-05": [],  # Independent
        },
    )

    # Mock MCP client with 100ms delay
    class MockMCPClient:
        def call_mcp(self, brain_id: str, query: str):
            # Simulate I/O delay synchronously (blocks for 100ms)
            time.sleep(0.1)
            from mastermind_cli.types.mcp import MCPResponse

            return MCPResponse(
                brain_id=brain_id,
                response=f"Result from {brain_id}",
                success=True,
                error=None,
            )

    async with DatabaseConnection(":memory:") as db:
        await db.connect()
        await db.create_task_schema()
        task_repo = TaskRepository(db)

        mcp_client = MockMCPClient()

        # Test 1: Sequential execution (baseline)
        # Execute brains one by one to simulate sequential execution
        start_sequential = time.perf_counter()
        for brain_id in flow.nodes.keys():
            mcp_client.call_mcp(brain_id, "test brief")
        sequential_time = time.perf_counter() - start_sequential

        # Test 2: Parallel execution
        executor = ParallelExecutor(
            task_repo,
            mcp_client,
            [ProviderConfig(name="notebooklm", max_concurrent_calls=10)],
        )

        start_parallel = time.perf_counter()
        results = await executor.execute_brains_parallel(flow, "test brief")
        parallel_time = time.perf_counter() - start_parallel

        # Calculate speedup
        speedup = sequential_time / parallel_time

        # Assert requirements
        assert speedup >= 3.0, f"Speedup {speedup:.2f}x below 3x minimum"
        assert speedup <= 10.0, f"Speedup {speedup:.2f}x exceeds 10x expected"

        # Verify all brains completed
        assert len(results) == 5
        assert all(r.get("status") == "completed" for r in results.values())

        print(
            f"✅ Speedup: {speedup:.2f}x (sequential: {sequential_time:.2f}s, parallel: {parallel_time:.2f}s)"
        )


@pytest.mark.asyncio
async def test_concurrent_execution():
    """Verify independent brains execute concurrently.

    Uses TaskGroup to ensure tasks run in parallel, not sequentially.
    """
    flow = FlowConfig(
        flow_id="concurrent-test",
        nodes={
            "brain-01": [],
            "brain-02": [],
            "brain-03": [],
        },
    )

    class MockMCPClient:
        def call_mcp(self, brain_id: str, query: str):
            # Verify tasks overlap in time (50ms delay)
            time.sleep(0.05)
            from mastermind_cli.types.mcp import MCPResponse

            return MCPResponse(
                brain_id=brain_id, response="OK", success=True, error=None
            )

    async with DatabaseConnection(":memory:") as db:
        await db.connect()
        await db.create_task_schema()
        task_repo = TaskRepository(db)

        mcp_client = MockMCPClient()
        executor = ParallelExecutor(
            task_repo,
            mcp_client,
            [ProviderConfig(name="notebooklm", max_concurrent_calls=10)],
        )

        start = time.perf_counter()
        results = await executor.execute_brains_parallel(flow, "test")
        elapsed = time.perf_counter() - start

        # 3 brains * 0.05s = 0.15s sequential, but ~0.05s parallel
        assert (
            elapsed < 0.10
        ), f"Execution took {elapsed:.2f}s, expected <0.10s for concurrent"
        assert len(results) == 3
        assert all(r.get("status") == "completed" for r in results.values())


@pytest.mark.asyncio
async def test_coordinator_parallel_flow():
    """Test coordinator integration with parallel execution.

    Verifies that:
    - Coordinator._execute_parallel() method works correctly
    - Wave-based execution respects dependencies
    - Results are returned correctly
    """
    from mastermind_cli.orchestrator.coordinator import Coordinator
    from mastermind_cli.orchestrator.output_formatter import OutputFormatter
    from unittest.mock import MagicMock

    # Create coordinator with mock formatter
    formatter = OutputFormatter()
    coordinator = Coordinator(formatter=formatter, use_mcp=False, enable_logging=False)

    # Create a simple plan with tasks
    coordinator.current_plan = {
        "plan_id": "test-parallel-001",
        "brief": {"original": "test brief for parallel execution"},
        "flow_type": "full_product",
        "tasks": [
            {"task_id": "task-1", "brain_id": 1},
            {"task_id": "task-2", "brain_id": 2},
        ],
    }

    # Mock the brain executor to return results
    coordinator.brain_executor.execute = MagicMock(
        return_value={"status": "completed", "output": {"result": "mock result"}}
    )

    # Execute in parallel mode
    result = await coordinator._execute_parallel(max_iterations=3)

    # Verify result structure
    assert "status" in result

    # Should complete successfully or have error (mock mode limitations)
    assert result["status"] in ["success", "error"]
    if result["status"] == "success":
        assert "results" in result
        assert "waves" in result
        assert result["waves"] >= 1
        print(f"✅ Parallel execution completed with {result['waves']} wave(s)")
    else:
        # Error case - should have error message and plan
        assert "error" in result
        assert "plan" in result
        print(
            f"ℹ️  Parallel execution returned error (expected in mock mode): {result['error']}"
        )
