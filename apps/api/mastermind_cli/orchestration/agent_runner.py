"""AgentRunner wrapper for session metadata capture.

This module provides the AgentRunner class that wraps brain agent execution
to capture session metadata for post-session evaluation by Brain #7.

Captured metadata:
- T1 (time to completion): execution_start_ms → execution_end_ms
- Planning score delta: planning_score_after - planning_score_before
- Session duration: execution_end_ms - execution_start_ms

Plan 14-02 Task 3: Create AgentRunner wrapper interface.
Integration into StatelessCoordinator deferred to future phases.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from mastermind_cli.orchestration.distillation_service import DistillationTask


class AgentRunner:
    """Wrapper to capture session metadata for distillation.

    This wraps brain agent execution to capture:
    - T1 (time to completion)
    - Planning score delta
    - Session duration

    Usage:
        runner = AgentRunner(session_id="task-123")
        runner.start_execution()
        # ... run brain orchestration ...
        runner.end_execution()

        # Convert to DistillationTask for post-session evaluation
        distillation_task = runner.to_distillation_task(
            brain_ids=["brain-01-product"],
            brief_summary="Implement feature X",
            invocation_method="mm:execute-phase",
            user_id="user-123",
        )
    """

    def __init__(self, session_id: str):
        """Initialize AgentRunner with session ID.

        Args:
            session_id: Unique identifier for this orchestration session
        """
        self.session_id = session_id
        self.execution_start_ms: Optional[int] = None
        self.execution_end_ms: Optional[int] = None
        self.planning_score_before: Optional[float] = None
        self.planning_score_after: Optional[float] = None

    def start_execution(self) -> None:
        """Mark execution start time.

        Should be called before brain orchestration begins.
        """
        self.execution_start_ms = int(datetime.now().timestamp() * 1000)

    def end_execution(self) -> None:
        """Mark execution end time.

        Should be called after brain orchestration completes.
        """
        self.execution_end_ms = int(datetime.now().timestamp() * 1000)

    @property
    def duration_ms(self) -> int:
        """Calculate session duration in milliseconds.

        Returns:
            Duration in milliseconds, or 0 if start/end times not set
        """
        if self.execution_start_ms is None or self.execution_end_ms is None:
            return 0
        return self.execution_end_ms - self.execution_start_ms

    @property
    def planning_score_delta(self) -> Optional[float]:
        """Calculate planning score change.

        Returns:
            Score delta (after - before), or None if scores not set
        """
        if self.planning_score_before is None or self.planning_score_after is None:
            return None
        return self.planning_score_after - self.planning_score_before

    def to_distillation_task(
        self,
        brain_ids: list[str],
        brief_summary: str,
        invocation_method: str,
        user_id: Optional[str] = None,
    ) -> "DistillationTask":
        """Convert to DistillationTask for post-session evaluation.

        Import DistillationTask locally to avoid circular dependency.

        Args:
            brain_ids: List of brain IDs invoked in this session
            brief_summary: Brief description of the session (truncated)
            invocation_method: How the session was invoked (e.g., "mm:execute-phase")
            user_id: Optional user ID who triggered the session

        Returns:
            DistillationTask instance with captured session metadata
        """
        from mastermind_cli.orchestration.distillation_service import (
            DistillationTask,
        )

        return DistillationTask(
            session_id=self.session_id,
            brain_ids=brain_ids,
            brief_summary=brief_summary,
            execution_start_ms=self.execution_start_ms or 0,
            execution_end_ms=self.execution_end_ms or 0,
            planning_score_delta=self.planning_score_delta,
            invocation_method=invocation_method,
            user_id=user_id,
        )
