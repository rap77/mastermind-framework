"""
Tests for mastermind_cli.mm_flow.dispatch_engine.

TDD: DISPATCH_ORACLE tests (SLI-3) verify that DynamicDispatchEngine.dispatch()
routes each moment to the correct parallel and barrier brain IDs.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
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
# Shared mock for httpx so unit tests never hit the network
# ---------------------------------------------------------------------------


def _mock_httpx_response(status_code: int = 204) -> MagicMock:
    """Return a fake httpx Response."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    return resp


def _mock_httpx_client(status_code: int = 204) -> MagicMock:
    """Return a mock httpx.AsyncClient context manager."""
    client = AsyncMock()
    client.post = AsyncMock(return_value=_mock_httpx_response(status_code))
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=client)
    cm.__aexit__ = AsyncMock(return_value=None)
    return cm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_brain_row(
    brain_id: int,
    role: str = "test-brain",
    model_quality: str = "balanced",
    is_barrier: bool = False,
) -> MagicMock:
    """Build a fake asyncpg Record-like object for brain_registry rows.

    Args:
        brain_id: Integer brain identifier (1-7).
        role: Brain name string (maps to brain_registry.name).
        model_quality: Ignored — kept for backward-compat with test signatures.
        is_barrier: Ignored — is_barrier is now derived from routing config.

    Returns:
        MagicMock with dict-style key access for all brain_registry columns.
    """
    row: MagicMock = MagicMock()
    row.__getitem__ = MagicMock(
        side_effect=lambda k: {
            "brain_id": brain_id,
            "name": role,
            "model_quality": "claude-opus-4-6",
            "model_balanced": "claude-sonnet-4-6",
            "model_budget": "claude-haiku-4-5",
            "capabilities": ["test"],
            "trigger_conditions": ["test"],
            "enabled": True,
        }[k]
    )
    return row


def _make_conn(
    parallel_rows: list[MagicMock], barrier_rows: list[MagicMock]
) -> AsyncMock:
    """Build a mock asyncpg connection that returns rows on fetchrow().

    DynamicDispatchEngine now calls BrainRegistryRepository.get_by_id() which
    issues conn.fetchrow(query, brain_id) per brain. This helper maps each
    brain_id to its row so fetchrow() returns the right row per call.

    Args:
        parallel_rows: Rows for parallel brain group.
        barrier_rows: Rows for barrier brain group.

    Returns:
        AsyncMock connection with a fetchrow() that routes by brain_id.
    """
    # Build a map brain_id → row for quick lookup
    row_map: dict[int, MagicMock] = {}
    for row in parallel_rows + barrier_rows:
        # Extract brain_id from the mock row using __getitem__
        try:
            bid = row["brain_id"]
            row_map[bid] = row
        except Exception:
            pass

    async def _fetchrow(query: str, *args: object) -> MagicMock | None:
        brain_id = int(args[0]) if args else -1  # type: ignore[arg-type]
        return row_map.get(brain_id)

    conn = AsyncMock()
    conn.fetchrow = _fetchrow
    conn.fetch = AsyncMock(return_value=[])  # kept for compatibility
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

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
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

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "DISCUSSION")

        parallel_ids = [b.brain_id for b in result.parallel]
        assert sorted(parallel_ids) == [1, 2, 3]

    async def test_dispatch_discussion_barrier_brain_id(self) -> None:
        """dispatch('DISCUSSION') barrier list contains only Brain #7."""
        parallel_rows = [_make_brain_row(1), _make_brain_row(2), _make_brain_row(3)]
        barrier_rows = [_make_brain_row(7, is_barrier=True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "DISCUSSION")

        barrier_ids = [b.brain_id for b in result.barrier]
        assert barrier_ids == [7]

    async def test_dispatch_discussion_moment_field(self) -> None:
        """DispatchResult.moment field matches the requested moment."""
        parallel_rows = [_make_brain_row(1), _make_brain_row(2), _make_brain_row(3)]
        barrier_rows = [_make_brain_row(7, is_barrier=True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "DISCUSSION")

        assert result.moment == "DISCUSSION"

    async def test_dispatch_result_execution_id_is_valid_uuid(self) -> None:
        """DispatchResult.execution_id must be a valid UUID string."""
        parallel_rows = [_make_brain_row(1), _make_brain_row(2), _make_brain_row(3)]
        barrier_rows = [_make_brain_row(7, is_barrier=True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
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

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "PLANNING")

        parallel_ids = [b.brain_id for b in result.parallel]
        assert sorted(parallel_ids) == [4, 5, 6]

    async def test_dispatch_planning_barrier_is_brain7(self) -> None:
        """dispatch('PLANNING') barrier is Brain #7."""
        parallel_rows = [_make_brain_row(4), _make_brain_row(5), _make_brain_row(6)]
        barrier_rows = [_make_brain_row(7, is_barrier=True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
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

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
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

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
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


# ---------------------------------------------------------------------------
# B2.5 / B2.6: Brain event notification (POST to Rust hub)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestBrainEventNotification:
    """B2.5/B2.6: dispatch() posts brain lifecycle events to the Rust hub."""

    async def test_dispatch_posts_dispatched_events(self) -> None:
        """dispatch() sends a 'dispatched' POST for each brain selected (B2.5)."""
        parallel_rows = [_make_brain_row(1), _make_brain_row(2), _make_brain_row(3)]
        barrier_rows = [_make_brain_row(7, is_barrier=True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=_mock_httpx_response(204))
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=mock_client)
        cm.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=cm),
        ):
            engine = DynamicDispatchEngine(
                postgres_url="postgresql://fake/db",
                rust_hub_url="http://rust-test:8002",
            )
            trace = "trace-b25-test"
            await engine.dispatch(19, "DISCUSSION", trace_id=trace)

        # 4 brains total (1,2,3 parallel + 7 barrier) × 2 calls (dispatched + completed)
        assert mock_client.post.call_count == 8

        # Verify dispatched events were sent first (first 4 calls)
        dispatched_calls = mock_client.post.call_args_list[:4]
        for call in dispatched_calls:
            payload = (
                call.kwargs.get("json") or call.args[1]
                if len(call.args) > 1
                else call.kwargs["json"]
            )
            assert payload["trace_id"] == trace
            assert payload["status"] == "dispatched"

    async def test_dispatch_posts_completed_events(self) -> None:
        """dispatch() sends a 'completed' POST for each brain after dispatch (B2.6)."""
        parallel_rows = [_make_brain_row(4), _make_brain_row(5)]
        barrier_rows = [_make_brain_row(7, is_barrier=True)]
        conn = _make_conn(parallel_rows, barrier_rows)

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=_mock_httpx_response(204))
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=mock_client)
        cm.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=cm),
        ):
            engine = DynamicDispatchEngine(
                postgres_url="postgresql://fake/db",
                rust_hub_url="http://rust-test:8002",
            )
            await engine.dispatch(19, "PLANNING", trace_id="trace-b26")

        # 3 brains × 2 calls = 6 total
        assert mock_client.post.call_count == 6

        # Last 3 calls should be 'completed'
        completed_calls = mock_client.post.call_args_list[3:]
        for call in completed_calls:
            payload = call.kwargs.get("json") or call.kwargs["json"]
            assert payload["status"] == "completed"

    async def test_hub_failure_does_not_break_dispatch(self) -> None:
        """B2.5/B2.6: hub POST errors are fire-and-forget — dispatch still returns."""
        parallel_rows = [_make_brain_row(1)]
        barrier_rows = []
        conn = _make_conn(parallel_rows, barrier_rows)

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=mock_client)
        cm.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=cm),
        ):
            engine = DynamicDispatchEngine(
                postgres_url="postgresql://fake/db",
                rust_hub_url="http://unreachable:9999",
            )
            # Must not raise even though the hub is unreachable
            result = await engine.dispatch(19, "DISCUSSION", trace_id="trace-fail")

        # dispatch still returns a valid result
        assert isinstance(result, DispatchResult)
        assert [b.brain_id for b in result.parallel] == [1]

    async def test_post_brain_event_uses_rust_hub_url(self) -> None:
        """_post_brain_event targets the rust_hub_url constructor parameter."""
        engine = DynamicDispatchEngine(
            postgres_url="postgresql://fake/db",
            rust_hub_url="http://custom-host:9999",
        )

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=_mock_httpx_response(204))
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=mock_client)
        cm.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=cm):
            await engine._post_brain_event("trace-url-test", 3, "dispatched")

        url_called = mock_client.post.call_args.args[0]
        assert url_called == "http://custom-host:9999/internal/brain-event"
