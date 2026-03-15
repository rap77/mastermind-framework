"""
CancellationManager - Graceful task cancellation with checkpoint support.

This module provides cooperative cancellation for parallel brain execution,
allowing in-flight tasks to save checkpoints before hard kill.
"""

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .task_executor import ParallelExecutor


class CancellationManager:
    """Manage graceful cancellation of parallel brain execution.

    This coordinator implements cooperative cancellation with a grace period:
    1. Sets cancel_event to signal all tasks to stop
    2. Waits for grace_period (default 5 seconds) for checkpoints
    3. Force-kills any remaining tasks after grace period

    Example:
        >>> manager = CancellationManager(grace_period=5.0)
        >>> task = asyncio.create_task(brain_execution())
        >>> manager.register_task(task)
        >>> results = await manager.cancel(executor)
        >>> print(results["graceful"], results["force_killed"])
    """

    def __init__(self, grace_period: float = 5.0) -> None:
        """Initialize cancellation manager.

        Args:
            grace_period: Seconds to wait for checkpoints before hard kill (default: 5.0)
        """
        self.grace_period = grace_period
        self.cancel_event = asyncio.Event()
        self._tasks: set[asyncio.Task[Any]] = set()

    async def cancel(self, executor: "ParallelExecutor") -> dict[str, int]:
        """Cancel all running tasks with grace period.

        This method orchestrates graceful cancellation:
        1. Signals executor to stop accepting new tasks
        2. Sets cancel_event (cooperative cancellation signal)
        3. Waits for grace_period for in-flight tasks to complete
        4. Force-kills any remaining tasks

        Args:
            executor: ParallelExecutor instance to cancel

        Returns:
            Dict with counts:
                - "graceful": Number of tasks that completed during grace period
                - "force_killed": Number of tasks that were force-killed
        """
        # Step 1: Signal cancellation to executor
        executor.cancel()
        self.cancel_event.set()

        # Step 2: Wait for grace period (allow checkpoints to save)
        try:
            await asyncio.sleep(self.grace_period)
        except asyncio.CancelledError:
            # If cancellation itself is cancelled, propagate
            pass

        # Step 3: Force kill remaining tasks
        results = {"graceful": 0, "force_killed": 0}

        for task in list(
            self._tasks
        ):  # Use list() to avoid modification during iteration
            if not task.done():
                task.cancel()
                # Wait for the task to actually be cancelled
                try:
                    await asyncio.wait_for(task, timeout=0.1)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
                results["force_killed"] += 1
            else:
                results["graceful"] += 1

        return results

    def register_task(self, task: asyncio.Task[Any]) -> None:
        """Track task for graceful cancellation.

        Tasks should be registered when created and unregistered when complete.

        Args:
            task: Asyncio task to track
        """
        self._tasks.add(task)

    def unregister_task(self, task: asyncio.Task[Any]) -> None:
        """Remove task from tracking.

        Call this when a task completes successfully or is cancelled.

        Args:
            task: Asyncio task to stop tracking
        """
        self._tasks.discard(task)

    def is_cancelled(self) -> bool:
        """Check if cancellation was requested.

        Returns:
            True if cancel_event is set (cancellation in progress)
        """
        return self.cancel_event.is_set()

    def reset(self) -> None:
        """Reset cancellation state (for testing or re-execution).

        Clears cancel_event and removes all task references.
        """
        self.cancel_event.clear()
        self._tasks.clear()
