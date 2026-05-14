"""Error tracker for task-executor subtask error handling.

Handles:
- C3.15: Insert decision with decision_type='error_resolution' on subtask error
- C3.25: Insert decision with decision_type='error_pattern' when same root_cause >= 2 times
- C3.21: task-progress.json subtask started_at + completed_at tracking
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class ErrorRecord:
    """Single error occurrence record."""

    subtask_id: str
    root_cause: str
    error_message: str
    solution_applied: str
    confidence: float = 0.7


@dataclass
class ErrorTracker:
    """Tracks subtask errors and detects recurring patterns.

    C3.15: On any error → emit decision with decision_type='error_resolution'
    C3.25: If same root_cause appears >= 2 times → emit decision_type='error_pattern'
    """

    # root_cause → list of ErrorRecord
    _errors_by_root_cause: dict[str, list[ErrorRecord]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def record_error(
        self,
        subtask_id: str,
        root_cause: str,
        error_message: str,
        solution_applied: str = "pending",
        confidence: float = 0.7,
    ) -> tuple[str, bool]:
        """Record an error and determine the decision_type to emit.

        Args:
            subtask_id: The subtask that failed
            root_cause: Normalized root cause category (e.g. "import_error", "test_failure")
            error_message: Full error message
            solution_applied: What was done to resolve it (if known)
            confidence: Confidence in the resolution (0.0-1.0)

        Returns:
            (decision_type, is_pattern) tuple where:
            - decision_type is 'error_resolution' or 'error_pattern'
            - is_pattern is True if this root_cause has appeared >= 2 times
        """
        record = ErrorRecord(
            subtask_id=subtask_id,
            root_cause=root_cause,
            error_message=error_message,
            solution_applied=solution_applied,
            confidence=confidence,
        )
        self._errors_by_root_cause[root_cause].append(record)

        count = len(self._errors_by_root_cause[root_cause])
        is_pattern = count >= 2

        decision_type = "error_pattern" if is_pattern else "error_resolution"
        return decision_type, is_pattern

    def get_pattern_decision_payload(
        self,
        root_cause: str,
        project_id: str | None = None,
    ) -> dict[str, object]:
        """Build the decision payload for a recurring error pattern.

        Args:
            root_cause: The root cause that appears multiple times
            project_id: Optional project UUID

        Returns:
            Dict suitable for db_write.py --type decision
        """
        records = self._errors_by_root_cause.get(root_cause, [])
        affected_subtasks = [r.subtask_id for r in records]

        return {
            "decision_type": "error_pattern",
            "title": f"Recurring error pattern: {root_cause}",
            "rationale": (
                f"Root cause '{root_cause}' occurred {len(records)} times "
                f"in subtasks: {', '.join(affected_subtasks)}. "
                "This is a systemic issue — consider addressing it proactively."
            ),
            "chosen_option": records[-1].solution_applied if records else "unknown",
            "made_by": "task-executor",
            "confidence": min(0.9, 0.5 + 0.1 * len(records)),
            "impact_level": "high",
            "impact_description": (
                f"Affects {len(records)} subtasks, may recur in future tasks. "
                "Flag as technical debt."
            ),
            "tags": ["error_pattern", root_cause, "tech-debt"],
            "project_id": project_id,
        }

    def get_resolution_decision_payload(
        self,
        subtask_id: str,
        root_cause: str,
        error_message: str,
        solution_applied: str,
        confidence: float = 0.7,
        project_id: str | None = None,
    ) -> dict[str, object]:
        """Build the decision payload for a single error resolution.

        Args:
            subtask_id: The subtask that failed
            root_cause: Root cause category
            error_message: Error message summary
            solution_applied: What was done to fix it
            confidence: Resolution confidence
            project_id: Optional project UUID

        Returns:
            Dict suitable for db_write.py --type decision
        """
        return {
            "decision_type": "error_resolution",
            "title": f"Error in {subtask_id}: {root_cause}",
            "rationale": error_message[:500],  # Truncate long messages
            "chosen_option": solution_applied,
            "made_by": "task-executor",
            "confidence": confidence,
            "impact_level": "low",
            "impact_description": f"Subtask {subtask_id} failed and required resolution",
            "tags": ["error_resolution", root_cause, subtask_id],
            "project_id": project_id,
        }

    @property
    def total_errors(self) -> int:
        """Total number of errors recorded."""
        return sum(len(v) for v in self._errors_by_root_cause.values())

    @property
    def recurring_root_causes(self) -> list[str]:
        """Root causes that have appeared >= 2 times (error_pattern candidates)."""
        return [
            cause
            for cause, records in self._errors_by_root_cause.items()
            if len(records) >= 2
        ]
