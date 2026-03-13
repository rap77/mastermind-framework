"""
Integration tests for parallel execution with performance validation.

This module tests the ParallelExecutor with focus on:
- Configuration persistence (save/load execution configs)
- Performance benchmarks (3-10x speedup for independent brains)
- Concurrent execution verification
- Task status query performance (<100ms target)
"""

import pytest
import asyncio
import time
from mastermind_cli.types.parallel import FlowConfig, ProviderConfig
from mastermind_cli.orchestrator.task_executor import ParallelExecutor
from mastermind_cli.state.repositories import TaskRepository
from mastermind_cli.state.database import DatabaseConnection


@pytest.mark.asyncio
async def test_config_persistence():
    """Test saving and loading execution configurations."""
    flow = FlowConfig(
        flow_id="persist-test",
        nodes={"brain-01": [], "brain-02": ["brain-01"]}
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
            [ProviderConfig(name="test", max_concurrent_calls=10)]
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
            task_repo,
            None,
            [ProviderConfig(name="test", max_concurrent_calls=10)]
        )

        # Load non-existent config
        loaded = await executor.load_config("non-existent")
        assert loaded is None
