"""Tests for high-value session detection in distillation service.

Plan 14-02 Task 1: TDD approach - RED phase first.
"""

import pytest

from mastermind_cli.orchestration.distillation_service import (
    DistillationTask,
    KnowledgeDistillationService,
)


class TestDistillationTaskModel:
    """Test DistillationTask Pydantic model validation."""

    def test_distillation_task_validates_required_fields(self):
        """Test 1: DistillationTask model validates required fields."""
        # Valid task with all required fields
        task = DistillationTask(
            session_id="test-session-123",
            brain_ids=["brain-01-product", "brain-07-growth"],
            brief_summary="Implement user authentication flow",
            execution_start_ms=1743801600000,
            execution_end_ms=1743801900000,
            invocation_method="mm:execute-phase",
        )

        assert task.session_id == "test-session-123"
        assert task.brain_ids == ["brain-01-product", "brain-07-growth"]
        assert task.brief_summary == "Implement user authentication flow"
        assert task.execution_start_ms == 1743801600000
        assert task.execution_end_ms == 1743801900000
        assert task.invocation_method == "mm:execute-phase"
        assert task.planning_score_delta is None  # Optional field
        assert task.user_id is None  # Optional field

    def test_distillation_task_with_optional_fields(self):
        """Test DistillationTask accepts optional fields."""
        task = DistillationTask(
            session_id="test-session-456",
            brain_ids=["brain-02-ux"],
            brief_summary="Design dashboard layout",
            execution_start_ms=1743801600000,
            execution_end_ms=1743802000000,
            invocation_method="mm:complete-phase",
            planning_score_delta=1.5,
            user_id="user-123",
        )

        assert task.planning_score_delta == 1.5
        assert task.user_id == "user-123"


class TestHighValueDetection:
    """Test high-value session detection logic."""

    def test_returns_true_when_duration_greater_than_5_minutes(self):
        """Test 2: High-value when duration > 5 minutes (300000ms)."""
        service = KnowledgeDistillationService(db_path=":memory:")

        # 6-minute session (> 5 min threshold)
        task = DistillationTask(
            session_id="long-session",
            brain_ids=["brain-01-product"],
            brief_summary="Strategic planning session",
            execution_start_ms=1743801600000,
            execution_end_ms=1743801960000,  # +6 minutes
            invocation_method="mm:execute-phase",
        )

        assert service._is_high_value_session(task) is True


class TestDistillationServiceDependencies:
    """Test dependency injection boundaries for distillation service."""

    @pytest.mark.asyncio
    async def test_trigger_evaluation_uses_injected_logger_and_extractor(self):
        """High-value sessions should run through injected logger/extractor dependencies."""

        class _FakeLogger:
            def __init__(self) -> None:
                self.logged_execution = None

            async def get_recent_by_brain(self, brain_id: str, limit: int = 10):
                assert brain_id == "brain-01-product"
                assert limit == 10
                return ["record-1", "record-2"]

            async def log_execution(self, **kwargs):
                self.logged_execution = kwargs

        class _FakeExtractor:
            def __init__(self, logger) -> None:
                self.logger = logger
                self.calls = []

            async def extract_and_store_template(self, record):
                self.calls.append(record)
                return "template-id" if record == "record-1" else None

        fake_logger = _FakeLogger()
        extractor_instances = []

        def _extractor_factory(logger):
            extractor = _FakeExtractor(logger)
            extractor_instances.append(extractor)
            return extractor

        service = KnowledgeDistillationService(
            logger=fake_logger,
            extractor_factory=_extractor_factory,
        )
        task = DistillationTask(
            session_id="injected-session",
            brain_ids=["brain-01-product"],
            brief_summary="Injected dependency path",
            execution_start_ms=0,
            execution_end_ms=600001,
            invocation_method="mm:execute-phase",
        )

        await service.trigger_evaluation_and_distillation(task)

        assert len(extractor_instances) == 1
        assert extractor_instances[0].calls == ["record-1", "record-2"]
        assert fake_logger.logged_execution is not None
        assert fake_logger.logged_execution["brain_id"] == "brain-07-growth"
        assert fake_logger.logged_execution["output_json"]["templates_extracted"] == 1

    def test_returns_true_when_planning_score_delta_nonzero(self):
        """Test 3: High-value when planning_score_delta != 0."""
        service = KnowledgeDistillationService(db_path=":memory:")

        # Short session BUT planning score changed (pivot detected)
        task = DistillationTask(
            session_id="pivot-session",
            brain_ids=["brain-01-product"],
            brief_summary="Reconsider architecture approach",
            execution_start_ms=1743801600000,
            execution_end_ms=1743801630000,  # Only 30 seconds
            invocation_method="mm:execute-phase",
            planning_score_delta=1.0,  # Score increased
        )

        assert service._is_high_value_session(task) is True

    def test_returns_true_when_invoked_via_complete_phase(self):
        """Test 4: High-value when invocation_method == 'mm:complete-phase'."""
        service = KnowledgeDistillationService(db_path=":memory:")

        # Short session, no score change, BUT explicit completion
        task = DistillationTask(
            session_id="completion-session",
            brain_ids=["brain-01-product", "brain-07-growth"],
            brief_summary="Phase completion review",
            execution_start_ms=1743801600000,
            execution_end_ms=1743801630000,  # Only 30 seconds
            invocation_method="mm:complete-phase",  # Explicit completion
        )

        assert service._is_high_value_session(task) is True

    def test_returns_false_for_short_sessions_with_no_changes(self):
        """Test 5: Returns False for short sessions with no changes."""
        service = KnowledgeDistillationService(db_path=":memory:")

        # Short session, no score change, not explicit completion
        task = DistillationTask(
            session_id="quick-session",
            brain_ids=["brain-04-frontend"],
            brief_summary="Quick component question",
            execution_start_ms=1743801600000,
            execution_end_ms=1743801620000,  # Only 20 seconds
            invocation_method="mm:execute-phase",
            planning_score_delta=0.0,  # No change
        )

        assert service._is_high_value_session(task) is False

    def test_returns_false_when_duration_exactly_5_minutes(self):
        """Edge case: Exactly 5 minutes is NOT high-value (must be > 5min)."""
        service = KnowledgeDistillationService(db_path=":memory:")

        # Exactly 5 minutes (300000ms) - should NOT be high-value
        task = DistillationTask(
            session_id="threshold-session",
            brain_ids=["brain-01-product"],
            brief_summary="Planning session at threshold",
            execution_start_ms=1743801600000,
            execution_end_ms=1743801900000,  # Exactly +5 minutes
            invocation_method="mm:execute-phase",
        )

        assert service._is_high_value_session(task) is False

    def test_returns_true_when_planning_score_negative(self):
        """Negative planning_score_delta (decrease) still counts as change."""
        service = KnowledgeDistillationService(db_path=":memory:")

        task = DistillationTask(
            session_id="score-decrease",
            brain_ids=["brain-01-product"],
            brief_summary="Planning complexity reduced",
            execution_start_ms=1743801600000,
            execution_end_ms=1743801630000,  # Short session
            invocation_method="mm:execute-phase",
            planning_score_delta=-0.5,  # Score decreased (still a change)
        )

        assert service._is_high_value_session(task) is True
