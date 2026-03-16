"""
Parallel executor using asyncio.TaskGroup with semaphore throttling.

This module provides ParallelExecutor for running independent brains
concurrently with retry logic, Circuit Breaker, and state persistence.
"""

import asyncio
import random
from typing import Any, Dict, List, Optional

from ..types.parallel import FlowConfig, ProviderConfig, TaskState
from ..state.repositories import TaskRepository
from ..orchestrator.mcp_wrapper import TypeSafeMCPWrapper


class ParallelExecutor:
    """Execute brains in parallel using asyncio.TaskGroup.

    This executor manages concurrent brain execution with:
    - Per-provider semaphores for rate limiting
    - Retry logic with exponential backoff (1s, 2s, 4s) + jitter
    - Circuit Breaker that opens after 3 consecutive failures per brain
    - Task state persistence before/after execution

    Example:
        >>> executor = ParallelExecutor(task_repo, mcp_client, provider_configs)
        >>> results = await executor.execute_brains_parallel(flow, "brief")
        >>> print(results["brain-01"]["result"])
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        mcp_client: TypeSafeMCPWrapper,
        provider_configs: List[ProviderConfig],
    ):
        """Initialize executor with repository, MCP client, and provider configs.

        Args:
            task_repo: TaskRepository for state persistence
            mcp_client: TypeSafeMCPWrapper for brain queries
            provider_configs: List of ProviderConfig for rate limiting
        """
        self.task_repo = task_repo
        self.mcp_client = mcp_client
        self.semaphores = {
            p.name: asyncio.Semaphore(p.max_concurrent_calls) for p in provider_configs
        }
        self.cancel_event = asyncio.Event()
        # Circuit Breaker state: brain_id -> consecutive_failure_count
        self._circuit_breakers: Dict[str, int] = {}
        self.CIRCUIT_BREAKER_THRESHOLD = 3

    async def execute_brain(
        self, task_id: str, brain_id: str, query: str, provider_name: str = "notebooklm"
    ) -> Dict[str, Any]:
        """Execute a single brain with semaphore limiting and retry logic.

        Args:
            task_id: Unique task identifier
            brain_id: Brain to execute
            query: Query string
            provider_name: Provider for rate limiting (default: notebooklm)

        Returns:
            Dictionary with brain_id, status, and result/error

        Raises:
            asyncio.CancelledError: If task is cancelled
        """
        semaphore = self.semaphores.get(provider_name)
        if not semaphore:
            raise ValueError(f"Unknown provider: {provider_name}")

        # Check Circuit Breaker
        if self._circuit_breakers.get(brain_id, 0) >= self.CIRCUIT_BREAKER_THRESHOLD:
            await self.task_repo.update_status(
                task_id,
                TaskState.FAILED,
                error=f"Circuit Breaker open for {brain_id} (too many failures)",
            )
            return {
                "brain_id": brain_id,
                "status": "failed",
                "error": f"Circuit Breaker open for {brain_id}",
            }

        async with semaphore:
            if self.cancel_event.is_set():
                raise asyncio.CancelledError("Task cancelled")

            await self.task_repo.update_status(task_id, TaskState.RUNNING)

            # Retry loop with exponential backoff + jitter
            max_attempts = 3
            base_delay = 1.0  # seconds
            jitter_percent = 0.2  # ±20%

            for attempt in range(max_attempts):
                try:
                    # Call MCP wrapper's async method (if exists) or sync method
                    result = await self._call_brain(brain_id, query)
                    # Success: reset Circuit Breaker
                    self._circuit_breakers[brain_id] = 0
                    await self.task_repo.update_result(task_id, result)
                    return {
                        "brain_id": brain_id,
                        "status": "completed",
                        "result": result,
                    }

                except asyncio.CancelledError:
                    await self.task_repo.update_status(task_id, TaskState.CANCELLED)
                    raise

                except Exception as e:
                    is_last_attempt = attempt == max_attempts - 1

                    if is_last_attempt:
                        # All retries exhausted: increment Circuit Breaker
                        self._circuit_breakers[brain_id] = (
                            self._circuit_breakers.get(brain_id, 0) + 1
                        )

                        # Format error using BrainErrorFormatter
                        from .error_formatter import BrainErrorFormatter

                        formatted_error = BrainErrorFormatter.format_error(brain_id, e)

                        await self.task_repo.update_status(
                            task_id, TaskState.FAILED, error=formatted_error
                        )
                        return {
                            "brain_id": brain_id,
                            "status": "failed",
                            "error": formatted_error,
                        }
                    else:
                        # Exponential backoff with jitter
                        delay = base_delay * (2**attempt)  # 1s, 2s, 4s
                        jitter = (
                            delay * jitter_percent * (random.random() * 2 - 1)
                        )  # ±20%
                        await asyncio.sleep(delay + jitter)

            # Should never reach here, but mypy needs explicit return
            return {
                "brain_id": brain_id,
                "status": "failed",
                "error": "Unknown error in retry loop",
            }

    async def _call_brain(self, brain_id: str, query: str) -> Dict[str, Any]:
        """Call brain via MCP wrapper.

        This method uses TypeSafeMCPWrapper's call_mcp method, executed in a thread
        to avoid blocking the event loop during sync I/O operations.

        Args:
            brain_id: Brain identifier
            query: Query string

        Returns:
            Brain response as dictionary
        """
        # Run sync call_mcp in thread pool to avoid blocking event loop
        response = await asyncio.to_thread(self.mcp_client.call_mcp, brain_id, query)
        if response.success:
            return {"response": response.response}
        else:
            raise Exception(response.error or "MCP call failed")

    async def execute_brains_parallel(
        self, flow: FlowConfig, brief: str
    ) -> Dict[str, Any]:
        """Execute multiple brains in parallel using TaskGroup.

        This method creates tasks for all brains in the flow and executes
        them concurrently using asyncio.TaskGroup. Independent brains
        (no dependencies) run in parallel.

        Args:
            flow: FlowConfig with brain nodes
            brief: Brief/query to execute

        Returns:
            Dictionary mapping brain_id to execution results
        """
        # Generate execution_id and save config for re-run capability
        execution_id = f"exec-{flow.flow_id}-{id(brief)}"
        await self.save_config(execution_id, flow, brief)

        results = {}
        try:
            async with asyncio.TaskGroup() as tg:
                tasks = {}
                for brain_id in flow.nodes.keys():
                    task_id = f"{brain_id}-{id(brief)}"
                    await self.task_repo.create(task_id, brain_id)

                    task = tg.create_task(self.execute_brain(task_id, brain_id, brief))
                    tasks[brain_id] = task

            # TaskGroup already awaited all tasks - get results directly
            for brain_id, task in tasks.items():
                results[brain_id] = task.result()

        except* Exception as eg:
            # Handle exception group (multiple failures)
            for exc in eg.exceptions:
                print(f"Task failed: {exc}")

        return results

    def cancel(self) -> None:
        """Cancel all running tasks."""
        self.cancel_event.set()

    def reset_circuit_breaker(self, brain_id: str) -> None:
        """Reset Circuit Breaker for a specific brain (manual recovery).

        Args:
            brain_id: Brain to reset Circuit Breaker for
        """
        if brain_id in self._circuit_breakers:
            del self._circuit_breakers[brain_id]

    async def save_config(self, execution_id: str, flow: FlowConfig, brief: str) -> str:
        """Save execution configuration for re-run.

        This method persists the FlowConfig and brief to the executions table,
        enabling reproducible executions and workflow re-execution.

        Args:
            execution_id: Unique execution identifier
            flow: Flow configuration
            brief: User's brief

        Returns:
            execution_id (the same as input for convenience)
        """
        from datetime import datetime, timezone

        flow_json = flow.model_dump_json()
        now = datetime.now(timezone.utc).isoformat()

        await self.task_repo.db.conn.execute(
            """INSERT INTO executions (id, flow_config, brief, created_at, status)
               VALUES (?, ?, ?, ?, 'pending')""",
            (execution_id, flow_json, brief, now),
        )
        await self.task_repo.db.conn.commit()
        return execution_id

    async def load_config(self, execution_id: str) -> Optional[dict[str, Any]]:
        """Load saved execution configuration.

        This method retrieves a previously saved execution configuration,
        allowing workflows to be re-run with identical parameters.

        Args:
            execution_id: Execution identifier to load

        Returns:
            Dict with flow_config and brief, or None if not found
        """
        cursor = await self.task_repo.db.conn.execute(
            "SELECT flow_config, brief FROM executions WHERE id = ?", (execution_id,)
        )
        row = await cursor.fetchone()

        if row:
            from ..types.parallel import FlowConfig

            flow_config = FlowConfig.model_validate_json(row[0])
            return {"flow": flow_config, "brief": row[1]}
        return None
