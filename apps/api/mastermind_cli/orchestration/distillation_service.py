"""Post-session brain evaluation and template extraction service.

This module implements the KnowledgeDistillationService that evaluates high-value
orchestration sessions with Brain #7. The service hooks into the task completion
flow via FastAPI BackgroundTasks (fire-and-forget pattern), ensuring non-blocking
execution while users receive immediate 202 responses.

High-value criteria (Brain #7 conditions):
- Session duration > 5 minutes (300000ms)
- Planning score changed (pivot detected)
- Invoked via /mm:complete-phase (explicit completion)

Plan 14-02 Task 1: Create distillation service with high-value detection.
"""

from typing import Optional

from pydantic import BaseModel

from mastermind_cli.experience.logger import ExperienceLogger
from mastermind_cli.state.database import DatabaseConnection


class DistillationTask(BaseModel):
    """Metadata for post-session brain evaluation.

    Captures session metadata for Brain #7 evaluation:
    - execution_start_ms: Session start timestamp (milliseconds since epoch)
    - execution_end_ms: Session end timestamp (milliseconds since epoch)
    - planning_score_delta: Change in planning score (indicates pivot)
    - invocation_method: How the session was triggered
    """

    session_id: str
    brain_ids: list[str]
    brief_summary: str
    execution_start_ms: int
    execution_end_ms: int
    planning_score_delta: Optional[float] = None
    invocation_method: str  # "mm:execute-phase" | "mm:complete-phase"
    user_id: Optional[str] = None


class KnowledgeDistillationService:
    """Post-session evaluation and template extraction service.

    Provides high-value session detection and triggers Brain #7 evaluation
    after orchestration completes. Uses fire-and-forget pattern via
    FastAPI BackgroundTasks to avoid blocking user responses.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._db: Optional[DatabaseConnection] = None

    async def _get_db(self) -> DatabaseConnection:
        """Lazy database connection."""
        if self._db is None:
            self._db = DatabaseConnection(self.db_path)
            await self._db.connect()
        return self._db

    def _is_high_value_session(self, task: DistillationTask) -> bool:
        """Determine if session warrants Brain #7 evaluation.

        High-value criteria (Brain #7 conditions):
            1. Session duration > 5 minutes (300000ms)
            2. Planning score changed (planning_score_delta != 0)
            3. Invoked via /mm:complete-phase (explicit completion)

        Args:
            task: DistillationTask with session metadata

        Returns:
            True if session is high-value, False otherwise
        """
        duration_ms = task.execution_end_ms - task.execution_start_ms

        # Criterion 1: Long-running session (> 5 minutes)
        if duration_ms > 300000:
            return True

        # Criterion 2: Planning score changed (pivot detected)
        if task.planning_score_delta is not None and task.planning_score_delta != 0:
            return True

        # Criterion 3: Explicit phase completion
        if task.invocation_method == "mm:complete-phase":
            return True

        return False

    async def trigger_evaluation_and_distillation(self, task: DistillationTask) -> None:
        """Post-session hook: Evaluate high-value sessions with Brain #7.

        This runs in background (non-blocking) after user receives 202 response.
        Only high-value sessions trigger Brain #7 evaluation to avoid noise.

        For Plan 14-02: Logs evaluation trigger without calling Brain #7 yet.
        Brain #7 integration deferred to Plan 14-03.

        Args:
            task: DistillationTask with session metadata
        """
        if not self._is_high_value_session(task):
            return  # Skip evaluation for low-value sessions

        # TODO: In Plan 14-03, call Brain #7 agent here
        # For now: Log that evaluation was triggered
        db = await self._get_db()
        logger = ExperienceLogger(db)

        await logger.log_execution(
            brain_id="brain-07-growth",
            input_json={
                "session_id": task.session_id,
                "brief": task.brief_summary,
            },
            output_json={
                "evaluation_status": "triggered",
                "high_value": True,
            },
            duration_ms=task.execution_end_ms - task.execution_start_ms,
            status="success",
            custom_metadata={
                "evaluation_type": "post_session",
                "invocation_method": task.invocation_method,
                "planning_score_delta": task.planning_score_delta,
            },
        )
