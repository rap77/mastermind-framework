"""
Tests for Execution Logger - brain execution logging to SQLite.

Tests cover:
- Schema creation
- Log entry creation
- Query functionality
- Statistics
- Context manager for timing
"""

import pytest
import asyncio
from pathlib import Path
from datetime import datetime, timezone

from mastermind_cli.state.logger import (
    ExecutionLogger,
    BrainExecutionLog,
    ExecutionQuery,
    log_brain_execution,
)
from mastermind_cli.types.interfaces import Brief, ProductStrategy


@pytest.fixture
async def temp_db_path(tmp_path):
    """Create temporary database file path."""
    return str(tmp_path / "test_logger.db")


@pytest.fixture
async def logger(temp_db_path):
    """Create ExecutionLogger instance with temp database."""
    logger = ExecutionLogger(db_path=temp_db_path, enabled=True)
    yield logger
    await logger.close()


@pytest.fixture
def sample_brief():
    """Create sample Brief for testing."""
    return Brief(
        problem_statement="Build a CRM for small businesses",
        context="Targeting companies with 10-50 employees",
        constraints=["Must be web-based", "Budget under $10k/month"],
        target_audience="Small business owners"
    )


@pytest.fixture
def sample_output():
    """Create sample ProductStrategy for testing."""
    return ProductStrategy(
        positioning="B2B CRM for small businesses with 10-50 employees",
        target_audience="Small business owners",
        key_features=["Contact management", "Pipeline tracking", "Email integration"],
        success_metrics=["User adoption rate", "Revenue growth"],
        risks=["Competition from Salesforce", "Market saturation"],
        generated_at=datetime.now(timezone.utc)
    )


class TestSchemaCreation:
    """Test database schema creation."""

    async def test_creates_brain_executions_table(self, temp_db_path):
        """Test that brain_executions table is created."""
        logger = ExecutionLogger(db_path=temp_db_path, enabled=True)
        conn = await logger._get_connection()

        # Check table exists
        cursor = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='brain_executions'"
        )
        result = await cursor.fetchone()
        assert result is not None
        assert result[0] == "brain_executions"

        await logger.close()

    async def test_creates_indexes(self, temp_db_path):
        """Test that indexes are created."""
        logger = ExecutionLogger(db_path=temp_db_path, enabled=True)
        conn = await logger._get_connection()

        # Check indexes exist
        cursor = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='brain_executions'"
        )
        indexes = await cursor.fetchall()
        index_names = [idx[0] for idx in indexes]

        # Verify expected indexes exist
        assert "idx_brain_executions_brain_id" in index_names
        assert "idx_brain_executions_status" in index_names
        assert "idx_brain_executions_timestamp" in index_names
        assert "idx_brain_executions_execution_id" in index_names

        await logger.close()


class TestLogExecution:
    """Test log_execution functionality."""

    async def test_log_success_execution(self, logger, sample_brief, sample_output):
        """Test logging a successful brain execution."""
        log_id = await logger.log_execution(
            execution_id="exec-123",
            brain_id="brain-01-product-strategy",
            brief=sample_brief,
            output=sample_output,
            status="success",
            duration_ms=1500,
            metadata={"user": "test-user"}
        )

        assert log_id != ""
        assert len(log_id) == 36  # UUID format

    async def test_log_error_execution(self, logger, sample_brief):
        """Test logging a failed brain execution."""
        log_id = await logger.log_execution(
            execution_id="exec-456",
            brain_id="brain-01-product-strategy",
            brief=sample_brief,
            output=None,
            status="error",
            error_message="MCP connection timeout",
            duration_ms=5000,
            metadata={"user": "test-user"}
        )

        assert log_id != ""

    async def test_retrieve_logged_execution(self, logger, sample_brief, sample_output):
        """Test retrieving a logged execution."""
        exec_id = "exec-789"

        await logger.log_execution(
            execution_id=exec_id,
            brain_id="brain-02-ux-research",
            brief=sample_brief,
            output=sample_output,
            status="success",
            duration_ms=2000
        )

        retrieved = await logger.get_execution_by_id(exec_id)
        assert retrieved is not None
        assert retrieved.execution_id == exec_id
        assert retrieved.brain_id == "brain-02-ux-research"
        assert retrieved.status == "success"
        assert retrieved.duration_ms == 2000

    async def test_disabled_logger_returns_empty_id(self, sample_brief, sample_output):
        """Test that disabled logger returns empty string."""
        logger = ExecutionLogger(db_path=":memory:", enabled=False)

        log_id = await logger.log_execution(
            execution_id="exec-disabled",
            brain_id="brain-01",
            brief=sample_brief,
            output=sample_output,
            status="success",
            duration_ms=1000
        )

        assert log_id == ""


class TestQueryExecutions:
    """Test query functionality."""

    async def test_query_all_executions(self, logger, sample_brief, sample_output):
        """Test querying all executions."""
        # Log multiple executions
        for i in range(3):
            await logger.log_execution(
                execution_id=f"exec-{i}",
                brain_id="brain-01-product-strategy",
                brief=sample_brief,
                output=sample_output,
                status="success",
                duration_ms=1000 + i * 500
            )

        query = ExecutionQuery()
        results = await logger.query_executions(query)

        assert len(results) == 3
        assert all(isinstance(r, BrainExecutionLog) for r in results)

    async def test_filter_by_brain_id(self, logger, sample_brief, sample_output):
        """Test filtering by brain_id."""
        # Log different brains
        await logger.log_execution(
            execution_id="exec-1",
            brain_id="brain-01-product-strategy",
            brief=sample_brief,
            output=sample_output,
            status="success",
            duration_ms=1000
        )
        await logger.log_execution(
            execution_id="exec-2",
            brain_id="brain-02-ux-research",
            brief=sample_brief,
            output=sample_output,
            status="success",
            duration_ms=1000
        )

        query = ExecutionQuery(brain_id="brain-01-product-strategy")
        results = await logger.query_executions(query)

        assert len(results) == 1
        assert results[0].brain_id == "brain-01-product-strategy"

    async def test_filter_by_status(self, logger, sample_brief, sample_output):
        """Test filtering by status."""
        # Log mixed statuses
        await logger.log_execution(
            execution_id="exec-success",
            brain_id="brain-01",
            brief=sample_brief,
            output=sample_output,
            status="success",
            duration_ms=1000
        )
        await logger.log_execution(
            execution_id="exec-error",
            brain_id="brain-01",
            brief=sample_brief,
            output=None,
            status="error",
            error_message="Test error",
            duration_ms=500
        )

        query = ExecutionQuery(status="error")
        results = await logger.query_executions(query)

        assert len(results) == 1
        assert results[0].status == "error"

    async def test_pagination(self, logger, sample_brief, sample_output):
        """Test pagination with limit and offset."""
        # Log 5 executions
        for i in range(5):
            await logger.log_execution(
                execution_id=f"exec-{i}",
                brain_id="brain-01",
                brief=sample_brief,
                output=sample_output,
                status="success",
                duration_ms=1000
            )

        # Get first page
        query = ExecutionQuery(limit=2, offset=0)
        page1 = await logger.query_executions(query)
        assert len(page1) == 2

        # Get second page
        query = ExecutionQuery(limit=2, offset=2)
        page2 = await logger.query_executions(query)
        assert len(page2) == 2

        # Pages should be different
        page1_ids = {r.execution_id for r in page1}
        page2_ids = {r.execution_id for r in page2}
        assert page1_ids.isdisjoint(page2_ids)

    async def test_sort_by_duration(self, logger, sample_brief, sample_output):
        """Test sorting by duration."""
        # Log executions with different durations
        durations = [1000, 3000, 2000, 5000, 4000]
        for i, duration in enumerate(durations):
            await logger.log_execution(
                execution_id=f"exec-{i}",
                brain_id="brain-01",
                brief=sample_brief,
                output=sample_output,
                status="success",
                duration_ms=duration
            )

        # Sort ascending
        query = ExecutionQuery(sort_by="duration_ms", sort_order="ASC")
        results = await logger.query_executions(query)
        result_durations = [r.duration_ms for r in results]
        assert result_durations == sorted(durations)


class TestStatistics:
    """Test statistics functionality."""

    async def test_get_statistics_empty(self, logger):
        """Test statistics with no executions."""
        stats = await logger.get_statistics()
        assert stats["total_executions"] == 0
        assert stats["success_count"] == 0
        assert stats["success_rate"] == 0

    async def test_get_statistics_with_data(self, logger, sample_brief, sample_output):
        """Test statistics with execution data."""
        # Log 10 executions: 7 success, 3 error
        for i in range(10):
            await logger.log_execution(
                execution_id=f"exec-{i}",
                brain_id="brain-01",
                brief=sample_brief,
                output=sample_output if i < 7 else None,
                status="success" if i < 7 else "error",
                error_message=None if i < 7 else "Test error",
                duration_ms=1000 + i * 100
            )

        stats = await logger.get_statistics()
        assert stats["total_executions"] == 10
        assert stats["success_count"] == 7
        assert stats["success_rate"] == 0.7
        assert stats["avg_duration_ms"] > 0

    async def test_disabled_logger_returns_empty_stats(self):
        """Test that disabled logger returns empty stats."""
        logger = ExecutionLogger(db_path=":memory:", enabled=False)
        stats = await logger.get_statistics()
        assert stats == {}


class TestContextManager:
    """Test log_brain_execution context manager."""

    async def test_context_manager_success_timing(self, logger, sample_brief, sample_output):
        """Test context manager with successful execution."""
        import time

        exec_id = "exec-context-success"

        with pytest.raises(Exception):  # Context manager yields Timer, not async context
            async with log_brain_execution(
                logger,
                exec_id,
                "brain-01",
                sample_brief
            ) as timer:
                # Simulate work
                await asyncio.sleep(0.1)
                timer.complete(sample_output)

        # Verify logged
        logged = await logger.get_execution_by_id(exec_id)
        assert logged is not None
        assert logged.status == "success"
        assert logged.duration_ms >= 100  # At least 100ms

    async def test_context_manager_error_handling(self, logger, sample_brief):
        """Test context manager with exception."""
        exec_id = "exec-context-error"

        try:
            async with log_brain_execution(
                logger,
                exec_id,
                "brain-01",
                sample_brief
            ) as timer:
                raise ValueError("Test error")
        except ValueError:
            pass

        # Verify logged as error
        logged = await logger.get_execution_by_id(exec_id)
        assert logged is not None
        assert logged.status == "error"
        assert "Test error" in logged.error_message


class TestModelValidation:
    """Test Pydantic model validation."""

    def test_brain_execution_log_model(self):
        """Test BrainExecutionLog model validation."""
        log = BrainExecutionLog(
            execution_id="exec-123",
            brain_id="brain-01",
            brief="Test brief",
            input_context={"key": "value"},
            output={"result": "success"},
            status="success",
            duration_ms=1000,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={"user": "test"}
        )
        assert log.execution_id == "exec-123"
        assert log.brain_id == "brain-01"

    def test_execution_query_model_defaults(self):
        """Test ExecutionQuery default values."""
        query = ExecutionQuery()
        assert query.brain_id is None
        assert query.status is None
        assert query.limit == 100
        assert query.offset == 0
        assert query.sort_by == "timestamp"
        assert query.sort_order == "DESC"

    def test_execution_query_validation(self):
        """Test ExecutionQuery validation."""
        # Valid query
        query = ExecutionQuery(
            brain_id="brain-01",
            status="success",
            limit=50,
            offset=10,
            sort_by="duration_ms",
            sort_order="ASC"
        )
        assert query.limit == 50

        # Invalid limit (too high)
        with pytest.raises(ValueError):
            ExecutionQuery(limit=2000)

        # Invalid sort_by
        with pytest.raises(ValueError):
            ExecutionQuery(sort_by="invalid_field")

        # Invalid sort_order
        with pytest.raises(ValueError):
            ExecutionQuery(sort_order="INVALID")
