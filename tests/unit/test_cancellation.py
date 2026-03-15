"""
Tests for CancellationManager with grace period and checkpoint support.
"""

import pytest
import asyncio
from unittest.mock import MagicMock

from mastermind_cli.orchestrator.cancellation import CancellationManager


class TestCancellationManager:
    """Test suite for CancellationManager."""

    @pytest.fixture
    def manager(self):
        """Create a CancellationManager with 1-second grace period for testing."""
        return CancellationManager(grace_period=1.0)

    @pytest.fixture
    def mock_executor(self):
        """Create a mock ParallelExecutor."""
        executor = MagicMock()
        executor.cancel = MagicMock()
        return executor

    @pytest.mark.asyncio
    async def test_grace_period_checkpoint(self, manager, mock_executor):
        """Test that cancellation waits for grace period before hard kill."""
        # Track task completion
        checkpoint_called = False

        async def mock_brain_task():
            """Simulate a brain that saves checkpoint during grace period."""
            nonlocal checkpoint_called
            await asyncio.sleep(0.5)  # Complete within grace period
            checkpoint_called = True
            return "checkpoint_saved"

        # Create and register task
        task = asyncio.create_task(mock_brain_task())
        manager.register_task(task)

        # Start cancellation (should wait for grace period)
        cancel_task = asyncio.create_task(manager.cancel(mock_executor))

        # Wait a bit to ensure grace period is respected
        await asyncio.sleep(0.1)

        # Task should still be running during grace period
        assert not task.done(), "Task should not be cancelled immediately"

        # Wait for cancellation to complete
        results = await cancel_task

        # Verify results
        assert checkpoint_called, "Task should have completed during grace period"
        assert results["graceful"] == 1, "Task should be counted as graceful"
        assert results["force_killed"] == 0, "No tasks should be force killed"

    @pytest.mark.asyncio
    async def test_force_kill_after_grace_period(self, manager, mock_executor):
        """Test that tasks are force killed after grace period expires."""

        # Create a long-running task that won't complete
        async def long_running_task():
            """Simulate a brain that takes too long."""
            await asyncio.sleep(10)  # Longer than grace period
            return "should_not_complete"

        # Create and register task
        task = asyncio.create_task(long_running_task())
        manager.register_task(task)

        # Start cancellation
        results = await manager.cancel(mock_executor)

        # Verify task was cancelled
        assert task.cancelled(), "Task should be cancelled after grace period"
        assert results["graceful"] == 0, "No tasks completed gracefully"
        assert results["force_killed"] == 1, "Task should be force killed"

    @pytest.mark.asyncio
    async def test_cancel_event_is_set(self, manager, mock_executor):
        """Test that cancel_event is set when cancellation is triggered."""
        # Start cancellation (don't wait for it)
        cancel_task = asyncio.create_task(manager.cancel(mock_executor))

        # Give the task a chance to start and set the event
        await asyncio.sleep(0.01)

        # Check that cancel_event is set
        assert manager.is_cancelled(), "cancel_event should be set"

        # Clean up
        await cancel_task

    @pytest.mark.asyncio
    async def test_register_and_unregister_tasks(self, manager):
        """Test task registration and unregistration."""

        async def dummy_task():
            await asyncio.sleep(0.1)
            return "done"

        # Register task
        task = asyncio.create_task(dummy_task())
        manager.register_task(task)
        assert len(manager._tasks) == 1, "Task should be registered"

        # Unregister task
        manager.unregister_task(task)
        assert len(manager._tasks) == 0, "Task should be unregistered"

        # Clean up
        await task

    @pytest.mark.asyncio
    async def test_multiple_tasks_mixed_completion(self, manager, mock_executor):
        """Test cancellation with multiple tasks, some completing and some not."""

        # Create fast task (will complete)
        async def fast_task():
            await asyncio.sleep(0.3)
            return "fast_done"

        # Create slow task (won't complete)
        async def slow_task():
            await asyncio.sleep(10)
            return "slow_done"

        fast = asyncio.create_task(fast_task())
        slow = asyncio.create_task(slow_task())

        manager.register_task(fast)
        manager.register_task(slow)

        # Cancel with 1-second grace period
        results = await manager.cancel(mock_executor)

        # Verify mixed results
        assert results["graceful"] == 1, "Fast task should complete gracefully"
        assert results["force_killed"] == 1, "Slow task should be force killed"

    @pytest.mark.asyncio
    async def test_reset_clears_state(self, manager):
        """Test that reset clears cancellation state and tasks."""
        # Set cancelled flag
        manager.cancel_event.set()

        # Add a dummy task
        async def dummy():
            await asyncio.sleep(0.1)

        task = asyncio.create_task(dummy())
        manager.register_task(task)

        # Reset
        manager.reset()

        # Verify state is cleared
        assert not manager.is_cancelled(), "cancel_event should be cleared"
        assert len(manager._tasks) == 0, "Tasks should be cleared"

        # Clean up
        await task

    @pytest.mark.asyncio
    async def test_custom_grace_period(self):
        """Test that custom grace period is respected."""
        # Create manager with 0.5 second grace period
        custom_manager = CancellationManager(grace_period=0.5)
        mock_executor = MagicMock()
        mock_executor.cancel = MagicMock()

        # Track time elapsed
        start_time = asyncio.get_event_loop().time()

        # Cancel (no tasks, just measure time)
        await custom_manager.cancel(mock_executor)

        elapsed = asyncio.get_event_loop().time() - start_time

        # Should wait approximately 0.5 seconds (±0.1 for tolerance)
        assert (
            0.4 <= elapsed <= 0.6
        ), f"Grace period should be ~0.5s, got {elapsed:.2f}s"
