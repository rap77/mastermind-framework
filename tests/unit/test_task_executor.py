"""
Unit tests for ParallelExecutor.

Tests for asyncio.TaskGroup execution, semaphore throttling,
retry logic with exponential backoff, and Circuit Breaker.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from mastermind_cli.types.parallel import FlowConfig, TaskState, ProviderConfig
from mastermind_cli.orchestrator.task_executor import ParallelExecutor


@pytest.fixture
def mock_mcp_client():
    """Mock TypeSafeMCPWrapper for testing."""
    from unittest.mock import MagicMock
    from mastermind_cli.types import MCPResponse

    client = MagicMock()
    client.call_mcp = MagicMock(return_value=MCPResponse(
        brain_id="brain-01",
        response="test result",
        success=True
    ))
    return client


@pytest.fixture
def mock_task_repo():
    """Mock TaskRepository for testing."""
    repo = AsyncMock()
    repo.create = AsyncMock(return_value=MagicMock(
        id="test-001",
        brain_id="brain-01",
        status="pending"
    ))
    repo.update_status = AsyncMock(return_value=MagicMock(
        id="test-001",
        brain_id="brain-01",
        status="running"
    ))
    repo.update_result = AsyncMock(return_value=MagicMock(
        id="test-001",
        brain_id="brain-01",
        status="completed"
    ))
    return repo


@pytest.fixture
def provider_configs():
    """Get provider configurations for testing."""
    return [
        ProviderConfig(
            name="notebooklm",
            max_concurrent_calls=2,
            retry_attempts=3,
            backoff_base=1.0
        ),
        ProviderConfig(
            name="claude",
            max_concurrent_calls=10,
            retry_attempts=3,
            backoff_base=1.0
        )
    ]


@pytest.mark.asyncio
async def test_parallel_execution(mock_task_repo, mock_mcp_client, provider_configs):
    """Test parallel execution of independent brains."""
    executor = ParallelExecutor(
        task_repo=mock_task_repo,
        mcp_client=mock_mcp_client,
        provider_configs=provider_configs
    )

    flow = FlowConfig(
        flow_id="test-flow",
        nodes={
            "brain-01": [],
            "brain-02": [],
            "brain-03": []
        }
    )

    results = await executor.execute_brains_parallel(flow, "test brief")

    assert len(results) == 3
    assert "brain-01" in results
    assert "brain-02" in results
    assert "brain-03" in results


@pytest.mark.asyncio
async def test_retry_with_backoff(mock_task_repo, mock_mcp_client, provider_configs):
    """Test retry logic with exponential backoff."""
    from mastermind_cli.types import MCPResponse

    # Configure mock to fail twice, then succeed
    mock_mcp_client.call_mcp = MagicMock(
        side_effect=[
            Exception("Network error"),
            Exception("Timeout"),
            MCPResponse(
                brain_id="brain-01",
                response="success after retries",
                success=True
            )
        ]
    )

    executor = ParallelExecutor(
        task_repo=mock_task_repo,
        mcp_client=mock_mcp_client,
        provider_configs=provider_configs
    )

    flow = FlowConfig(
        flow_id="test-flow",
        nodes={"brain-01": []}
    )

    results = await executor.execute_brains_parallel(flow, "test brief")

    # Should succeed after 2 retries
    assert results["brain-01"]["status"] == "completed"
    assert mock_mcp_client.call_mcp.call_count == 3


@pytest.mark.asyncio
async def test_circuit_breaker_opens(mock_task_repo, mock_mcp_client, provider_configs):
    """Test Circuit Breaker opens after 3 consecutive failures."""
    # Configure mock to always fail
    mock_mcp_client.call_mcp = MagicMock(
        side_effect=Exception("Permanent failure")
    )

    executor = ParallelExecutor(
        task_repo=mock_task_repo,
        mcp_client=mock_mcp_client,
        provider_configs=provider_configs
    )

    flow = FlowConfig(
        flow_id="test-flow",
        nodes={"brain-01": []}
    )

    # Execute 4 times (should open circuit breaker after 3rd)
    for i in range(4):
        results = await executor.execute_brains_parallel(flow, "test brief")
        if i < 3:
            assert results["brain-01"]["status"] == "failed"
            assert "Permanent failure" in results["brain-01"]["error"]
        else:
            # 4th attempt should fail immediately due to circuit breaker
            assert results["brain-01"]["status"] == "failed"
            assert "Circuit Breaker open" in results["brain-01"]["error"]


@pytest.mark.asyncio
async def test_no_threading_used():
    """Verify no threading modules are imported."""
    import mastermind_cli.orchestrator.task_executor as executor_module
    import inspect
    import sys

    # Get all source code
    source = inspect.getsource(executor_module)

    # Verify no threading imports
    assert "import threading" not in source
    assert "from threading" not in source

    # Verify asyncio is used
    assert "import asyncio" in source


@pytest.mark.asyncio
async def test_semaphore_throttling(mock_task_repo, mock_mcp_client, provider_configs):
    """Test per-provider semaphore throttling."""
    executor = ParallelExecutor(
        task_repo=mock_task_repo,
        mcp_client=mock_mcp_client,
        provider_configs=provider_configs
    )

    # Verify semaphores are created
    assert "notebooklm" in executor.semaphores
    assert "claude" in executor.semaphores

    # Verify semaphore values
    assert executor.semaphores["notebooklm"]._value == 2
    assert executor.semaphores["claude"]._value == 10


@pytest.mark.asyncio
async def test_exponential_backoff_with_jitter(mock_task_repo, mock_mcp_client, provider_configs):
    """Test exponential backoff with jitter is applied."""
    call_times = []

    def track_time(*args, **kwargs):
        call_times.append(asyncio.get_event_loop().time())
        raise Exception("Fail")

    mock_mcp_client.call_mcp = MagicMock(side_effect=track_time)

    executor = ParallelExecutor(
        task_repo=mock_task_repo,
        mcp_client=mock_mcp_client,
        provider_configs=provider_configs
    )

    flow = FlowConfig(flow_id="test-flow", nodes={"brain-01": []})

    await executor.execute_brains_parallel(flow, "test brief")

    # Verify 3 attempts were made
    assert len(call_times) == 3

    # Verify delays between retries (exponential: 1s, 2s, 4s + jitter)
    if len(call_times) >= 2:
        delay1 = call_times[1] - call_times[0]
        # Should be approximately 1s ± 20% jitter
        assert 0.8 < delay1 < 1.2

    if len(call_times) >= 3:
        delay2 = call_times[2] - call_times[1]
        # Should be approximately 2s ± 20% jitter
        assert 1.6 < delay2 < 2.4
