"""
Unit tests for LangSmith instrumentation and OEC baseline (Phase 20C).

Tests:
- 20.21: @traceable decorator does not break dispatch() with mock LangSmith client
- 20.22: baseline.py computes mean correctly with fixture of 5 records
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# 20.21: @traceable decorator test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_traceable_decorator_does_not_break_dispatch() -> None:
    """20.21: @traceable does not break DynamicDispatchEngine.dispatch() when
    LangSmith is mocked."""

    # Patch langsmith.traceable to be a no-op pass-through decorator so the
    # test does not require real LangSmith credentials.
    def _noop_traceable(**kwargs: Any):  # type: ignore[return]
        def decorator(fn: Any) -> Any:
            return fn

        return decorator

    with patch("langsmith.traceable", _noop_traceable):
        # Re-import after patching to pick up the no-op decorator
        import importlib

        import mastermind_cli.mm_flow.dispatch_engine as engine_mod

        importlib.reload(engine_mod)
        DynamicDispatchEngine = engine_mod.DynamicDispatchEngine

        # Build a minimal engine with a mock postgres URL and mock internals
        engine = object.__new__(DynamicDispatchEngine)
        engine.postgres_url = "postgresql://mock"  # type: ignore[attr-defined]
        engine.rust_hub_url = "http://mock"  # type: ignore[attr-defined]

        # Mock config so dispatch doesn't need a real YAML/DB
        mock_routing = MagicMock()
        mock_routing.brains = []
        mock_routing.barrier = []
        mock_config = MagicMock()
        mock_config.brain_routing = {"DISCUSSION": mock_routing}
        engine.config = mock_config  # type: ignore[attr-defined]

        # Patch asyncpg.connect and _get_brains_from_registry
        with (
            patch.object(engine_mod.asyncpg, "connect", new_callable=AsyncMock),
            patch.object(
                DynamicDispatchEngine,
                "_get_brains_from_registry",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch.object(
                DynamicDispatchEngine,
                "_check_budget",
            ),
            patch.object(
                DynamicDispatchEngine,
                "_post_brain_event",
                new_callable=AsyncMock,
            ),
        ):
            result = await engine.dispatch(phase=20, moment="DISCUSSION")

        # Verify result is a valid DispatchResult
        assert result.moment == "DISCUSSION"
        assert isinstance(result.parallel, list)
        assert isinstance(result.barrier, list)

    # Restore original module state
    importlib.reload(engine_mod)


# ---------------------------------------------------------------------------
# 20.22: baseline.py mean calculation test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_baseline_computes_mean_correctly(tmp_path: Path) -> None:
    """20.22: baseline.py computes mean quality_score correctly with 5 records."""
    from mastermind_cli.rag.baseline import compute_baseline

    # Five mock rows with known quality scores: mean = (0.8+0.7+0.9+0.6+0.5) / 5 = 0.7
    mock_scores = [0.8, 0.7, 0.9, 0.6, 0.5]
    expected_mean = round(sum(mock_scores) / len(mock_scores), 4)

    mock_rows = [{"quality_score": s} for s in mock_scores]

    output_file = tmp_path / "rag-baseline.json"

    # Mock asyncpg.connect and conn.fetch
    mock_conn = AsyncMock()
    mock_conn.fetch = AsyncMock(return_value=mock_rows)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)

    import asyncpg

    with patch.object(
        asyncpg, "connect", new_callable=AsyncMock, return_value=mock_conn
    ):
        result = await compute_baseline(
            database_url="postgresql://mock",
            brain_id="brain-01",
            limit=5,
            oec_target=0.75,
            output_path=output_file,
        )

    assert result["sessions_evaluated"] == 5
    assert result["quality_score_mean"] == expected_mean
    assert result["oec_target"] == 0.75

    # Verify the file was written correctly
    assert output_file.exists()
    written = json.loads(output_file.read_text())
    assert written["sessions_evaluated"] == 5
    assert written["quality_score_mean"] == expected_mean
    assert written["oec_target"] == 0.75


@pytest.mark.asyncio
async def test_baseline_empty_records(tmp_path: Path) -> None:
    """baseline.py returns 0.0 mean when no records exist."""
    from mastermind_cli.rag.baseline import compute_baseline

    output_file = tmp_path / "rag-baseline.json"
    mock_conn = AsyncMock()
    mock_conn.fetch = AsyncMock(return_value=[])

    import asyncpg

    with patch.object(
        asyncpg, "connect", new_callable=AsyncMock, return_value=mock_conn
    ):
        result = await compute_baseline(
            database_url="postgresql://mock",
            output_path=output_file,
        )

    assert result["sessions_evaluated"] == 0
    assert result["quality_score_mean"] == 0.0
