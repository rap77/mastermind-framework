"""
Tests for mastermind_cli.mm_flow.dispatch_engine.

TDD: DISPATCH_ORACLE tests (SLI-3) verify that DynamicDispatchEngine.dispatch()
routes each moment to the correct parallel and barrier brain IDs.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from mastermind_cli.mm_flow.dispatch_engine import (
    DISPATCH_ORACLE,
    BrainDispatch,
    BudgetExceededError,
    DispatchResult,
    DynamicDispatchEngine,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_brain_row(
    brain_id: int,
    role: str = "test-brain",
    model_quality: str = "balanced",
    is_barrier: bool = False,
) -> MagicMock:
    """Build a fake asyncpg Record-like object for agent_registry rows.

    Args:
        brain_id: Integer brain identifier (1-7).
        role: Brain role string.
        model_quality: Model profile key (quality | balanced | budget).
        is_barrier: Whether this brain acts as a barrier brain.

    Returns:
        MagicMock with dict-style key access for all agent_registry columns.
    """
    row: MagicMock = MagicMock()
    row.__getitem__ = MagicMock(
        side_effect=lambda k: {
            "brain_id": brain_id,
            "role": role,
            "model_quality": model_quality,
            "is_barrier": is_barrier,
            "token_budget_per_phase": 100_000,
            "tokens_consumed_total": 0,
        }[k]
    )
    return row


def _make_conn(
    parallel_rows: list[MagicMock], barrier_rows: list[MagicMock]
) -> AsyncMock:
    """Build a mock asyncpg connection that returns rows on fetch().

    The first fetch() call returns parallel_rows and the second returns barrier_rows.

    Args:
        parallel_rows: Rows for parallel brain query (brains list).
        barrier_rows: Rows for barrier brain query.

    Returns:
        AsyncMock connection with a fetch() that cycles through both result sets.
    """
    conn = AsyncMock()
    conn.fetch = AsyncMock(side_effect=[parallel_rows, barrier_rows])
    conn.close = AsyncMock()
    return conn


# ---------------------------------------------------------------------------
# DISPATCH_ORACLE unit tests (SLI-3)
# ---------------------------------------------------------------------------


class TestDispatchOracle:
    """Verify DISPATCH_ORACLE routing table matches config.yml defaults."""

    def test_oracle_has_all_four_moments(self) -> None:
        """DISPATCH_ORACLE must define all 4 execution moments."""
        expected = {"DISCUSSION", "PLANNING", "EXECUTION_WAVE", "VERIFICATION"}
        assert set(DISPATCH_ORACLE.keys()) == expected

    def test_discussion_parallel_brains(self) -> None:
        """DISCUSSION moment routes to brains 1, 2, 3 in parallel."""
        oracle = DISPATCH_ORACLE["DISCUSSION"]
        assert oracle["parallel_brain_ids"] == [1, 2, 3]

    def test_discussion_barrier_brain(self) -> None:
        """DISCUSSION barrier must be Brain #7."""
        oracle = DISPATCH_ORACLE["DISCUSSION"]
        assert oracle["barrier_brain_ids"] == [7]

    def test_planning_parallel_brains(self) -> None:
        """PLANNING moment routes to brains 4, 5, 6 in parallel."""
        oracle = DISPATCH_ORACLE["PLANNING"]
        assert oracle["parallel_brain_ids"] == [4, 5, 6]

    def test_planning_barrier_brain(self) -> None:
        """PLANNING barrier must be Brain #7."""
        oracle = DISPATCH_ORACLE["PLANNING"]
        assert oracle["barrier_brain_ids"] == [7]

    def test_execution_wave_parallel_brains(self) -> None:
        """EXECUTION_WAVE routes only Brain #7 (sequential, no barrier)."""
        oracle = DISPATCH_ORACLE["EXECUTION_WAVE"]
        assert oracle["parallel_brain_ids"] == [7]

    def test_execution_wave_no_barrier(self) -> None:
        """EXECUTION_WAVE must have empty barrier (Brain #7 is executor, not barrier)."""
        oracle = DISPATCH_ORACLE["EXECUTION_WAVE"]
        assert oracle["barrier_brain_ids"] == []

    def test_verification_parallel_brains(self) -> None:
        """VERIFICATION routes only Brain #7."""
        oracle = DISPATCH_ORACLE["VERIFICATION"]
        assert oracle["parallel_brain_ids"] == [7]

    def test_verification_no_barrier(self) -> None:
        """VERIFICATION must have empty barrier."""
        oracle = DISPATCH_ORACLE["VERIFICATION"]
        assert oracle["barrier_brain_ids"] == []


# ---------------------------------------------------------------------------
# DynamicDispatchEngine.dispatch() integration-style tests (mocked asyncpg)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestDynamicDispatchEngineDiscussion:
    """dispatch() with moment=DISCUSSION returns brains [1,2,3] + barrier [7]."""

    async def test_dispatch_returns_dispatch_result(self) -> None:
        """dispatch() returns a DispatchResult instance."""
        parallel_rows = [
            _make_brain_row(1, "product-strategy"),
            _make_brain_row(2, "ux-research"),
            _make_brain_row(3, "ui-design"),
        ]
        barrier_rows = [_make_brain_row(7, "growth-evaluator", "quality", True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "DISCUSSION")

        assert isinstance(result, DispatchResult)

    async def test_dispatch_discussion_parallel_brain_ids(self) -> None:
        """dispatch('DISCUSSION') parallel list contains brain IDs 1, 2, 3."""
        parallel_rows = [
            _make_brain_row(1),
            _make_brain_row(2),
            _make_brain_row(3),
        ]
        barrier_rows = [_make_brain_row(7, is_barrier=True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "DISCUSSION")

        parallel_ids = [b.brain_id for b in result.parallel]
        assert sorted(parallel_ids) == [1, 2, 3]

    async def test_dispatch_discussion_barrier_brain_id(self) -> None:
        """dispatch('DISCUSSION') barrier list contains only Brain #7."""
        parallel_rows = [_make_brain_row(1), _make_brain_row(2), _make_brain_row(3)]
        barrier_rows = [_make_brain_row(7, is_barrier=True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "DISCUSSION")

        barrier_ids = [b.brain_id for b in result.barrier]
        assert barrier_ids == [7]

    async def test_dispatch_discussion_moment_field(self) -> None:
        """DispatchResult.moment field matches the requested moment."""
        parallel_rows = [_make_brain_row(1), _make_brain_row(2), _make_brain_row(3)]
        barrier_rows = [_make_brain_row(7, is_barrier=True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "DISCUSSION")

        assert result.moment == "DISCUSSION"

    async def test_dispatch_result_execution_id_is_valid_uuid(self) -> None:
        """DispatchResult.execution_id must be a valid UUID string."""
        parallel_rows = [_make_brain_row(1), _make_brain_row(2), _make_brain_row(3)]
        barrier_rows = [_make_brain_row(7, is_barrier=True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "DISCUSSION")

        # raises ValueError if not a valid UUID
        uuid.UUID(result.execution_id)


@pytest.mark.asyncio
class TestDynamicDispatchEnginePlanning:
    """dispatch() with moment=PLANNING returns brains [4,5,6] + barrier [7]."""

    async def test_dispatch_planning_parallel_brain_ids(self) -> None:
        """dispatch('PLANNING') parallel list contains brain IDs 4, 5, 6."""
        parallel_rows = [_make_brain_row(4), _make_brain_row(5), _make_brain_row(6)]
        barrier_rows = [_make_brain_row(7, is_barrier=True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "PLANNING")

        parallel_ids = [b.brain_id for b in result.parallel]
        assert sorted(parallel_ids) == [4, 5, 6]

    async def test_dispatch_planning_barrier_is_brain7(self) -> None:
        """dispatch('PLANNING') barrier is Brain #7."""
        parallel_rows = [_make_brain_row(4), _make_brain_row(5), _make_brain_row(6)]
        barrier_rows = [_make_brain_row(7, is_barrier=True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "PLANNING")

        assert [b.brain_id for b in result.barrier] == [7]


@pytest.mark.asyncio
class TestDynamicDispatchEngineExecutionWave:
    """dispatch() with moment=EXECUTION_WAVE returns only Brain #7 (no barrier)."""

    async def test_dispatch_execution_wave_parallel_is_brain7(self) -> None:
        """EXECUTION_WAVE: parallel=[Brain #7], barrier=[]."""
        brain7_rows = [_make_brain_row(7, is_barrier=False)]
        conn = _make_conn(brain7_rows, [])  # no barrier rows

        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "EXECUTION_WAVE")

        assert [b.brain_id for b in result.parallel] == [7]
        assert result.barrier == []


@pytest.mark.asyncio
class TestDynamicDispatchEngineVerification:
    """dispatch() with moment=VERIFICATION returns only Brain #7 (no barrier)."""

    async def test_dispatch_verification_parallel_is_brain7(self) -> None:
        """VERIFICATION: parallel=[Brain #7], barrier=[]."""
        brain7_rows = [_make_brain_row(7)]
        conn = _make_conn(brain7_rows, [])

        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "VERIFICATION")

        assert [b.brain_id for b in result.parallel] == [7]
        assert result.barrier == []


# ---------------------------------------------------------------------------
# BrainDispatch Pydantic model tests
# ---------------------------------------------------------------------------


class TestBrainDispatchModel:
    """BrainDispatch strict Pydantic model validation."""

    def test_valid_brain_dispatch(self) -> None:
        """BrainDispatch accepts valid field types."""
        bd = BrainDispatch(
            brain_id=1,
            role="product-strategy",
            model_profile="quality",
            is_barrier=False,
        )
        assert bd.brain_id == 1
        assert bd.model_profile == "quality"

    def test_invalid_model_profile_raises(self) -> None:
        """BrainDispatch rejects unknown model_profile values."""
        with pytest.raises(ValidationError):
            BrainDispatch(
                brain_id=1,
                role="x",
                model_profile="invalid",
                is_barrier=False,  # type: ignore[arg-type]
            )


# ---------------------------------------------------------------------------
# BudgetExceededError
# ---------------------------------------------------------------------------


class TestBudgetExceededError:
    """BudgetExceededError is a plain exception (no asyncio.wait_for wrapping, C3)."""

    def test_budget_exceeded_error_is_exception(self) -> None:
        """BudgetExceededError must subclass Exception."""
        assert issubclass(BudgetExceededError, Exception)

    def test_budget_exceeded_error_raises(self) -> None:
        """BudgetExceededError can be raised and caught normally."""
        with pytest.raises(BudgetExceededError, match="budget"):
            raise BudgetExceededError("budget exceeded")
