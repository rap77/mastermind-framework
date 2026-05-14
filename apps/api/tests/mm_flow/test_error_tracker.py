"""Unit tests for ErrorTracker — C3.15, C3.19, C3.25, C3.26.

TDD approach:
- C3.15/C3.19: subtask error → decision_type='error_resolution'
- C3.25/C3.26: same root_cause >= 2 times → decision_type='error_pattern'
"""

import pytest
import sys
from pathlib import Path

# ─── Path setup ───────────────────────────────────────────────────────────────
API_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(API_DIR))

from mastermind_cli.mm_flow.error_tracker import ErrorTracker  # noqa: E402


class TestErrorTrackerResolution:
    """C3.15/C3.19: single error → decision_type='error_resolution'."""

    def setup_method(self) -> None:
        self.tracker = ErrorTracker()

    def test_first_error_yields_error_resolution(self) -> None:
        """First occurrence of any error → decision_type='error_resolution'."""
        decision_type, is_pattern = self.tracker.record_error(
            subtask_id="C3.01",
            root_cause="import_error",
            error_message="ModuleNotFoundError: No module named 'httpx'",
            solution_applied="uv add httpx",
        )
        assert decision_type == "error_resolution"
        assert is_pattern is False

    def test_resolution_payload_structure(self) -> None:
        """Resolution payload has all required keys for db_write.py."""
        payload = self.tracker.get_resolution_decision_payload(
            subtask_id="C3.01",
            root_cause="import_error",
            error_message="ModuleNotFoundError: No module named 'httpx'",
            solution_applied="uv add httpx",
        )
        assert payload["decision_type"] == "error_resolution"
        assert "title" in payload
        assert "rationale" in payload
        assert "chosen_option" in payload
        assert payload["chosen_option"] == "uv add httpx"
        assert payload["made_by"] == "task-executor"
        assert isinstance(payload["confidence"], float)

    def test_confidence_default_is_07(self) -> None:
        """Default confidence for error_resolution is 0.7."""
        payload = self.tracker.get_resolution_decision_payload(
            subtask_id="C3.01",
            root_cause="test_failure",
            error_message="AssertionError: expected True but got False",
            solution_applied="fixed assertion",
        )
        assert payload["confidence"] == pytest.approx(0.7)

    def test_error_message_truncated_at_500_chars(self) -> None:
        """Long error messages are truncated to 500 chars."""
        long_error = "E " + "x" * 600
        payload = self.tracker.get_resolution_decision_payload(
            subtask_id="C3.02",
            root_cause="long_error",
            error_message=long_error,
            solution_applied="fixed",
        )
        assert len(payload["rationale"]) <= 500

    def test_tags_include_subtask_id(self) -> None:
        """Tags should include the subtask ID for filtering."""
        payload = self.tracker.get_resolution_decision_payload(
            subtask_id="C3.05",
            root_cause="import_error",
            error_message="error",
            solution_applied="fix",
        )
        assert "C3.05" in payload["tags"]
        assert "error_resolution" in payload["tags"]


class TestErrorTrackerPattern:
    """C3.25/C3.26: same root_cause >= 2 times → decision_type='error_pattern'."""

    def setup_method(self) -> None:
        self.tracker = ErrorTracker()

    def test_second_same_root_cause_yields_error_pattern(self) -> None:
        """C3.26: Two errors with same root_cause → decision_type='error_pattern'."""
        # First occurrence
        decision_type_1, is_pattern_1 = self.tracker.record_error(
            subtask_id="C3.01",
            root_cause="type_error",
            error_message="TypeError: expected str got int",
            solution_applied="added type annotation",
        )
        assert decision_type_1 == "error_resolution"
        assert is_pattern_1 is False

        # Second occurrence — same root_cause
        decision_type_2, is_pattern_2 = self.tracker.record_error(
            subtask_id="C3.03",
            root_cause="type_error",  # Same root cause!
            error_message="TypeError: list indices must be integers",
            solution_applied="cast to int",
        )
        assert decision_type_2 == "error_pattern"
        assert is_pattern_2 is True

    def test_different_root_causes_dont_trigger_pattern(self) -> None:
        """Different root causes don't count toward each other's pattern threshold."""
        self.tracker.record_error(
            subtask_id="C3.01",
            root_cause="import_error",
            error_message="ImportError",
            solution_applied="install package",
        )
        decision_type, is_pattern = self.tracker.record_error(
            subtask_id="C3.02",
            root_cause="test_failure",  # Different root cause
            error_message="AssertionError",
            solution_applied="fix test",
        )
        assert decision_type == "error_resolution"
        assert is_pattern is False

    def test_pattern_payload_structure(self) -> None:
        """Error pattern payload has all required keys."""
        self.tracker.record_error(
            subtask_id="C3.01",
            root_cause="db_error",
            error_message="OperationalError: connection refused",
            solution_applied="retry with backoff",
        )
        self.tracker.record_error(
            subtask_id="C3.02",
            root_cause="db_error",
            error_message="OperationalError: connection reset",
            solution_applied="retry with backoff",
        )

        payload = self.tracker.get_pattern_decision_payload(root_cause="db_error")
        assert payload["decision_type"] == "error_pattern"
        assert "C3.01" in payload["rationale"]
        assert "C3.02" in payload["rationale"]
        assert payload["impact_level"] == "high"
        assert "tech-debt" in payload["tags"]
        assert "error_pattern" in payload["tags"]
        assert payload["confidence"] > 0.5  # Pattern = higher confidence

    def test_pattern_confidence_increases_with_count(self) -> None:
        """More occurrences = higher confidence (capped at 0.9)."""
        for i in range(5):
            self.tracker.record_error(
                subtask_id=f"C3.0{i}",
                root_cause="network_error",
                error_message="timeout",
                solution_applied="retry",
            )

        payload = self.tracker.get_pattern_decision_payload(root_cause="network_error")
        # Should be capped at 0.9
        assert payload["confidence"] <= 0.9
        # And higher than default 0.5
        assert payload["confidence"] > 0.5

    def test_recurring_root_causes_property(self) -> None:
        """recurring_root_causes returns list of root causes with >= 2 occurrences."""
        self.tracker.record_error("s1", "cause_a", "err", "fix")
        self.tracker.record_error("s2", "cause_a", "err", "fix")
        self.tracker.record_error("s3", "cause_b", "err", "fix")

        recurring = self.tracker.recurring_root_causes
        assert "cause_a" in recurring
        assert "cause_b" not in recurring

    def test_total_errors_count(self) -> None:
        """total_errors returns total across all root causes."""
        self.tracker.record_error("s1", "cause_a", "err", "fix")
        self.tracker.record_error("s2", "cause_a", "err", "fix")
        self.tracker.record_error("s3", "cause_b", "err", "fix")

        assert self.tracker.total_errors == 3

    def test_third_occurrence_still_yields_error_pattern(self) -> None:
        """Third occurrence of same root_cause is still error_pattern."""
        for i in range(3):
            decision_type, is_pattern = self.tracker.record_error(
                subtask_id=f"C3.0{i}",
                root_cause="timeout_error",
                error_message="Request timed out",
                solution_applied="increase timeout",
            )

        # All occurrences after the first should be error_pattern
        assert decision_type == "error_pattern"
        assert is_pattern is True


class TestErrorTrackerIntegration:
    """C3.19: Integration — simulate error in subtask → verify INSERT."""

    def test_error_tracker_produces_valid_db_payloads(self) -> None:
        """Both resolution and pattern payloads produce valid db_write.py format."""
        tracker = ErrorTracker()

        # First error → resolution
        decision_type, _ = tracker.record_error(
            subtask_id="C3.15",
            root_cause="syntax_error",
            error_message="SyntaxError: invalid syntax at line 42",
            solution_applied="fixed indentation",
        )
        resolution_payload = tracker.get_resolution_decision_payload(
            subtask_id="C3.15",
            root_cause="syntax_error",
            error_message="SyntaxError: invalid syntax at line 42",
            solution_applied="fixed indentation",
        )

        # Verify all required fields for db_write.py --type decision
        required_fields = [
            "decision_type",
            "title",
            "rationale",
            "chosen_option",
            "made_by",
        ]
        for field_name in required_fields:
            assert (
                field_name in resolution_payload
            ), f"Missing required field: {field_name}"

        assert resolution_payload["decision_type"] == "error_resolution"

        # Second error (same root cause) → pattern
        tracker.record_error(
            subtask_id="C3.20",
            root_cause="syntax_error",
            error_message="SyntaxError: unexpected EOF",
            solution_applied="fixed syntax",
        )
        pattern_payload = tracker.get_pattern_decision_payload("syntax_error")

        for field_name in required_fields:
            assert (
                field_name in pattern_payload
            ), f"Missing required field in pattern payload: {field_name}"

        assert pattern_payload["decision_type"] == "error_pattern"
