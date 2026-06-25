"""Error tracker for task-executor subtask error handling.

Handles:
- C3.15: Insert decision with decision_type='error_resolution' on subtask error
- C3.25: Insert decision with decision_type='error_pattern' when same root_cause >= 2 times
- C3.21: task-progress.json subtask started_at + completed_at tracking
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mastermind_cli.memory_layer.service import MemoryService


logger = logging.getLogger(__name__)


def _payload_tags(value: object) -> list[str]:
    """Normalize payload tags into a list of strings."""
    if not isinstance(value, list):
        return []
    return [str(tag) for tag in value if tag is not None]


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
    _memory_ids_by_root_cause: dict[str, list[str]] = field(
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

    async def record_error_memory(
        self,
        memory_service: "MemoryService",
        subtask_id: str,
        root_cause: str,
        error_message: str,
        solution_applied: str = "pending",
        confidence: float = 0.7,
        project_id: str | None = None,
    ) -> tuple[str, bool]:
        """Record an error and persist the resulting learning through MemoryService.

        Args:
            memory_service: First-party memory application service.
            subtask_id: The subtask that failed.
            root_cause: Normalized root cause category.
            error_message: Full error message or summary.
            solution_applied: Resolution taken for the error.
            confidence: Confidence in the resolution.
            project_id: Optional project identifier for project-scoped memory.

        Returns:
            Tuple of ``(decision_type, is_pattern)`` matching ``record_error``.
        """
        decision_type, is_pattern = self.record_error(
            subtask_id=subtask_id,
            root_cause=root_cause,
            error_message=error_message,
            solution_applied=solution_applied,
            confidence=confidence,
        )

        if is_pattern:
            related_memory_ids = list(self._memory_ids_by_root_cause[root_cause])
            payload = self.get_pattern_decision_payload(
                root_cause=root_cause,
                project_id=project_id,
            )
            try:
                saved_item = await memory_service.record_learning(
                    title=str(payload["title"]),
                    content=str(payload["rationale"]),
                    project_id=project_id,
                    memory_type="pattern",
                    visibility="project",
                    source_kind="error_tracker",
                    source_ref=f"error_pattern:{root_cause}",
                    tags=_payload_tags(payload["tags"]),
                    related_memory_ids=related_memory_ids or None,
                    metadata={
                        "decision_type": payload["decision_type"],
                        "chosen_option": payload["chosen_option"],
                        "confidence": payload["confidence"],
                        "impact_level": payload["impact_level"],
                        "made_by": payload["made_by"],
                    },
                )
            except Exception:
                logger.warning(
                    "error tracker pattern memory persistence failed", exc_info=True
                )
            else:
                if (
                    saved_item.memory_id
                    and saved_item.memory_id
                    not in self._memory_ids_by_root_cause[root_cause]
                ):
                    self._memory_ids_by_root_cause[root_cause].append(
                        saved_item.memory_id
                    )
            return decision_type, is_pattern

        related_memory_ids = list(self._memory_ids_by_root_cause[root_cause])
        payload = self.get_resolution_decision_payload(
            subtask_id=subtask_id,
            root_cause=root_cause,
            error_message=error_message,
            solution_applied=solution_applied,
            confidence=confidence,
            project_id=project_id,
        )
        try:
            saved_item = await memory_service.record_learning(
                title=str(payload["title"]),
                content=str(payload["rationale"]),
                project_id=project_id,
                memory_type="fix",
                visibility="project",
                source_kind="error_tracker",
                source_ref=f"error_resolution:{subtask_id}:{root_cause}",
                tags=_payload_tags(payload["tags"]),
                related_memory_ids=related_memory_ids or None,
                metadata={
                    "decision_type": payload["decision_type"],
                    "chosen_option": payload["chosen_option"],
                    "confidence": payload["confidence"],
                    "impact_level": payload["impact_level"],
                    "made_by": payload["made_by"],
                },
            )
        except Exception:
            logger.warning(
                "error tracker resolution memory persistence failed", exc_info=True
            )
        else:
            if (
                saved_item.memory_id
                and saved_item.memory_id
                not in self._memory_ids_by_root_cause[root_cause]
            ):
                self._memory_ids_by_root_cause[root_cause].append(saved_item.memory_id)
        return decision_type, is_pattern

    def get_pattern_decision_payload(
        self,
        root_cause: str,
        project_id: str | None = None,
    ) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
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
