"""Unit tests for Brain #7 post-session evaluator — C3.09, C3.10.

TDD approach:
- C3.09: mock Brain #7 → verify ExperienceLogger.log_execution() called with quality_score
- C3.10: integration test → SELECT quality_score IS NOT NULL
"""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# ─── Path setup ───────────────────────────────────────────────────────────────
API_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(API_DIR))

from mastermind_cli.orchestrator.brain7_evaluator import (  # noqa: E402
    Brain7EvalResult,
    Brain7Evaluator,
    evaluate_session,
    HIGH_VALUE_DURATION_MS,
    HIGH_VALUE_SCORE_THRESHOLD,
)
from mastermind_cli.experience.logger import ExperienceLogger  # noqa: E402


# ─── Brain7Evaluator unit tests ───────────────────────────────────────────────


class TestBrain7Evaluator:
    """Unit tests for Brain7Evaluator heuristic scoring."""

    def setup_method(self) -> None:
        self.evaluator = Brain7Evaluator()

    def test_success_status_yields_positive_score(self) -> None:
        result = self.evaluator.evaluate(
            brain_id="brain-01-product",
            output_json={"recommendation": "Build MVP"},
            duration_ms=5000,
            status="success",
        )
        assert result.quality_score > 0.0
        assert 0.0 <= result.quality_score <= 1.0

    def test_failure_status_yields_low_score(self) -> None:
        result = self.evaluator.evaluate(
            brain_id="brain-01-product",
            output_json={},
            duration_ms=100,
            status="failure",
        )
        assert result.quality_score <= 0.2
        assert any("failed" in i.lower() for i in result.insights)

    def test_substantive_output_increases_score(self) -> None:
        with_output = self.evaluator.evaluate(
            brain_id="brain-01",
            output_json={"recommendation": "x", "analysis": "y", "strategy": "z"},
            duration_ms=2000,
            status="success",
        )
        empty_output = self.evaluator.evaluate(
            brain_id="brain-01",
            output_json={},
            duration_ms=2000,
            status="success",
        )
        assert with_output.quality_score > empty_output.quality_score

    def test_high_value_set_when_score_above_threshold(self) -> None:
        result = self.evaluator.evaluate(
            brain_id="brain-01",
            output_json={
                "recommendation": "x",
                "analysis": "y",
                "strategy": "z",
                "roadmap": "w",
            },
            duration_ms=5000,
            status="success",
        )
        if result.quality_score >= HIGH_VALUE_SCORE_THRESHOLD:
            assert result.high_value is True

    def test_high_value_set_when_duration_exceeds_threshold(self) -> None:
        result = self.evaluator.evaluate(
            brain_id="brain-01",
            output_json={"data": "some output"},
            duration_ms=HIGH_VALUE_DURATION_MS + 1,
            status="success",
        )
        assert result.high_value is True

    def test_stub_duration_penalized(self) -> None:
        """Executions under 100ms are flagged as potential stubs."""
        result = self.evaluator.evaluate(
            brain_id="brain-01",
            output_json={"recommendation": "stub"},
            duration_ms=50,
            status="success",
        )
        assert any("stub" in i.lower() or "100ms" in i for i in result.insights)

    def test_score_clamped_to_zero_one(self) -> None:
        """Brain7EvalResult clamps quality_score to [0.0, 1.0]."""
        result = Brain7EvalResult(quality_score=1.5, insights=[], high_value=False)
        assert result.quality_score == 1.0

        result_low = Brain7EvalResult(quality_score=-0.5, insights=[], high_value=False)
        assert result_low.quality_score == 0.0

    def test_evaluate_session_convenience_function(self) -> None:
        result = evaluate_session(
            brain_id="brain-06-qa",
            output_json={"test_results": "all pass"},
            duration_ms=3000,
            status="success",
        )
        assert isinstance(result, Brain7EvalResult)
        assert 0.0 <= result.quality_score <= 1.0
        assert isinstance(result.insights, list)


# ─── C3.09: ExperienceLogger integration ─────────────────────────────────────


class TestBrain7HookCallsExperienceLogger:
    """C3.09: mock Brain #7 → verify ExperienceLogger.log_execution() called with quality_score."""

    @pytest.mark.asyncio
    async def test_log_execution_called_with_quality_score(self) -> None:
        """Verify that after evaluate_session(), ExperienceLogger.log_execution
        is called with quality_score parameter."""
        from mastermind_cli.state.database import DatabaseConnection

        mock_db = MagicMock(spec=DatabaseConnection)
        mock_conn = AsyncMock()
        mock_db.conn = mock_conn

        logger = ExperienceLogger(mock_db)

        # Evaluate Brain #7
        eval_result = evaluate_session(
            brain_id="brain-01-product",
            output_json={"recommendation": "Build an MVP first"},
            duration_ms=3000,
            status="success",
        )

        # Simulate what task_runner does after getting eval_result
        await logger.log_execution(
            brain_id="brain-01-product",
            input_json={"brief": "Build a CRM", "flow": "validation_only"},
            output_json={"recommendation": "Build an MVP first"},
            duration_ms=3000,
            status="success",
            quality_score=eval_result.quality_score,
            custom_metadata={
                "model": "anthropic:claude-sonnet-4-6",
                "high_value": eval_result.high_value,
                "insights": eval_result.insights,
            },
        )

        # Verify DB insert was called
        assert mock_conn.execute.called
        call_args = mock_conn.execute.call_args[0]
        sql = call_args[0]
        params = call_args[1]

        assert "INSERT INTO experience_records" in sql

        # custom_metadata in params[9] (index 9 is custom_metadata JSON)
        custom_meta = json.loads(params[9])
        assert "quality_score" in custom_meta
        assert custom_meta["quality_score"] == pytest.approx(eval_result.quality_score)

    @pytest.mark.asyncio
    async def test_quality_score_propagated_to_metadata(self) -> None:
        """quality_score ends up in custom_metadata JSON blob."""
        from mastermind_cli.state.database import DatabaseConnection

        mock_db = MagicMock(spec=DatabaseConnection)
        mock_conn = AsyncMock()
        mock_db.conn = mock_conn

        logger = ExperienceLogger(mock_db)
        test_score = 0.87

        await logger.log_execution(
            brain_id="brain-07-growth",
            input_json={"brief": "test"},
            output_json={"insights": ["grow faster"]},
            duration_ms=1200,
            status="success",
            quality_score=test_score,
        )

        call_args = mock_conn.execute.call_args[0]
        params = call_args[1]
        custom_meta = json.loads(params[9])  # index 9 = custom_metadata

        assert custom_meta["quality_score"] == test_score


# ─── C3.10: Integration test (in-memory SQLite) ────────────────────────────────


@pytest.mark.asyncio
async def test_quality_score_persisted_in_sqlite() -> None:
    """C3.10: After evaluate_session() + log_execution(), quality_score IS NOT NULL."""
    import aiosqlite
    from mastermind_cli.state.database import DatabaseConnection
    from mastermind_cli.experience.logger import ExperienceLogger

    # Use in-memory SQLite for this test
    async with aiosqlite.connect(":memory:") as raw_conn:
        # Create schema
        await raw_conn.execute("""
            CREATE TABLE experience_records (
                id TEXT PRIMARY KEY,
                brain_id TEXT NOT NULL,
                input_hash TEXT NOT NULL,
                output_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                duration_ms INTEGER NOT NULL,
                status TEXT NOT NULL,
                embedding_stub BLOB,
                parent_brain_id TEXT,
                trace_context_id TEXT,
                custom_metadata TEXT NOT NULL,
                expires_at TEXT
            )
        """)
        await raw_conn.commit()

        # Build a fake DB connection
        mock_db = MagicMock(spec=DatabaseConnection)
        mock_db.conn = raw_conn

        logger = ExperienceLogger(mock_db)

        eval_result = evaluate_session(
            brain_id="brain-01-product",
            output_json={"recommendation": "ship it"},
            duration_ms=4000,
            status="success",
        )

        await logger.log_execution(
            brain_id="brain-01-product",
            input_json={"brief": "build product"},
            output_json={"recommendation": "ship it"},
            duration_ms=4000,
            status="success",
            quality_score=eval_result.quality_score,
        )

        # C3.10 assertion: SELECT quality_score IS NOT NULL
        cursor = await raw_conn.execute(
            """SELECT json_extract(custom_metadata, '$.quality_score')
               FROM experience_records
               ORDER BY timestamp DESC LIMIT 1"""
        )
        row = await cursor.fetchone()
        assert row is not None, "No records found after log_execution"
        assert row[0] is not None, "quality_score IS NULL — should not be"
        assert float(row[0]) == pytest.approx(eval_result.quality_score)
