"""
Tests for BrainErrorFormatter - error message formatting without stack traces.
"""

import pytest
from unittest.mock import MagicMock

from mastermind_cli.orchestrator.error_formatter import BrainErrorFormatter


class TestBrainErrorFormatter:
    """Test suite for BrainErrorFormatter."""

    def test_format_basic_error(self):
        """Test basic error formatting without stack trace."""
        error = ValueError("Invalid input parameter")
        formatted = BrainErrorFormatter.format_error("brain-01", error)

        # Should contain brain_id and error type
        assert "brain-01" in formatted
        assert "ValueError" in formatted
        assert "Invalid input parameter" in formatted

        # Should NOT contain stack trace
        assert "Traceback" not in formatted
        assert "File " not in formatted
        assert "line " not in formatted

    def test_format_mcp_rate_limit_error(self):
        """Test that MCP rate limit errors get contextual hints."""
        error = Exception("Rate limit exceeded for API calls")
        formatted = BrainErrorFormatter.format_error("brain-02", error)

        # Should contain rate limit hint
        assert "rate limit" in formatted.lower()
        assert "Hint:" in formatted or "💡" in formatted

    def test_format_mcp_timeout_error(self):
        """Test that MCP timeout errors get contextual hints."""
        error = TimeoutError("Request timed out after 30s")
        formatted = BrainErrorFormatter.format_error("brain-03", error)

        # Should contain timeout hint
        assert "timeout" in formatted.lower()
        assert "Hint:" in formatted or "💡" in formatted

    def test_format_mcp_not_found_error(self):
        """Test that MCP not found errors get contextual hints."""
        error = Exception("Brain not found in registry")
        formatted = BrainErrorFormatter.format_error("unknown-brain", error)

        # Should contain not found hint
        assert "not found" in formatted.lower()
        assert "Hint:" in formatted or "💡" in formatted

    def test_format_mcp_unauthorized_error(self):
        """Test that MCP unauthorized errors get contextual hints."""
        error = PermissionError("Unauthorized: Invalid API key")
        formatted = BrainErrorFormatter.format_error("brain-05", error)

        # Should contain unauthorized hint
        assert "unauthorized" in formatted.lower() or "credentials" in formatted.lower()
        assert "Hint:" in formatted or "💡" in formatted

    def test_format_with_traceback_debug_mode(self):
        """Test that traceback is included in debug mode."""
        error = RuntimeError("Something went wrong")
        formatted = BrainErrorFormatter.format_error(
            "brain-06", error, include_traceback=True
        )

        # Should contain traceback in debug mode (has error type twice)
        assert (
            formatted.count("RuntimeError") >= 2
        ), "Should have error in message and traceback"

    def test_format_parallel_summary_all_success(self):
        """Test parallel summary when all tasks succeed."""
        results = {
            "brain-01": {"status": "completed", "result": "output1"},
            "brain-02": {"status": "completed", "result": "output2"},
            "brain-03": {"status": "completed", "result": "output3"},
        }
        summary = BrainErrorFormatter.format_parallel_summary(results)

        assert "3/3" in summary or "3 successful" in summary
        assert "Completed: 3" in summary
        assert "Failed:" not in summary
        assert "Cancelled:" not in summary

    def test_format_parallel_summary_with_failures(self):
        """Test parallel summary when some tasks fail."""
        results = {
            "brain-01": {"status": "completed", "result": "output1"},
            "brain-02": {"status": "failed", "error": "Something went wrong"},
            "brain-03": {"status": "completed", "result": "output3"},
        }
        summary = BrainErrorFormatter.format_parallel_summary(results)

        assert "2/3" in summary or "2 successful" in summary
        assert "Completed: 2" in summary
        assert "Failed: 1" in summary

    def test_format_parallel_summary_with_cancellations(self):
        """Test parallel summary when some tasks are cancelled."""
        results = {
            "brain-01": {"status": "completed", "result": "output1"},
            "brain-02": {"status": "cancelled"},
            "brain-03": {"status": "cancelled"},
        }
        summary = BrainErrorFormatter.format_parallel_summary(results)

        assert "1/3" in summary or "1 successful" in summary
        assert "Completed: 1" in summary
        assert "Cancelled: 2" in summary

    def test_format_parallel_summary_mixed(self):
        """Test parallel summary with mixed outcomes."""
        results = {
            "brain-01": {"status": "completed", "result": "output1"},
            "brain-02": {"status": "failed", "error": "Error 1"},
            "brain-03": {"status": "cancelled"},
            "brain-04": {"status": "completed", "result": "output4"},
            "brain-05": {"status": "failed", "error": "Error 2"},
        }
        summary = BrainErrorFormatter.format_parallel_summary(results)

        assert "2/5" in summary or "2 successful" in summary
        assert "Completed: 2" in summary
        assert "Failed: 2" in summary
        assert "Cancelled: 1" in summary


class TestErrorFormatterWiredToExecutor:
    """Test that BrainErrorFormatter is wired to TaskExecutor."""

    @pytest.mark.asyncio
    async def test_executor_uses_error_formatter_on_failure(self):
        """Test that TaskExecutor uses BrainErrorFormatter for error messages."""
        from mastermind_cli.orchestrator.task_executor import ParallelExecutor
        from mastermind_cli.state.repositories import TaskRepository
        from mastermind_cli.state.database import DatabaseConnection
        from mastermind_cli.types.parallel import ProviderConfig

        # Setup in-memory database
        async with DatabaseConnection(":memory:") as db:
            await db.create_task_schema()
            task_repo = TaskRepository(db)

            # Create mock MCP client that fails
            mcp_client = MagicMock()
            mcp_client.call_mcp = MagicMock(
                return_value=MagicMock(
                    success=False, error="Rate limit exceeded for API calls"
                )
            )

            # Create executor with single provider
            provider_config = ProviderConfig(
                name="notebooklm",
                max_concurrent_calls=5,
                base_url="http://localhost:8000",
            )
            executor = ParallelExecutor(task_repo, mcp_client, [provider_config])

            # Create task in database first
            await task_repo.create(task_id="test-001", brain_id="brain-01")

            # Execute brain (will fail)
            result = await executor.execute_brain(
                task_id="test-001",
                brain_id="brain-01",
                query="test query",
                provider_name="notebooklm",
            )

            # Verify result contains formatted error
            assert result["status"] == "failed"
            assert "error" in result

            # Verify error is formatted (has brain_id and hint, not just raw message)
            error_msg = result["error"]
            assert "brain-01" in error_msg, "Error should contain brain_id"
            assert (
                "Hint:" in error_msg or "💡" in error_msg
            ), "Error should contain hint"
            assert "Rate limit" in error_msg, "Error should contain original message"

    @pytest.mark.asyncio
    async def test_executor_hides_stack_trace_by_default(self):
        """Test that TaskExecutor doesn't include stack traces in errors."""
        from mastermind_cli.orchestrator.task_executor import ParallelExecutor
        from mastermind_cli.state.repositories import TaskRepository
        from mastermind_cli.state.database import DatabaseConnection
        from mastermind_cli.types.parallel import ProviderConfig

        # Setup in-memory database
        async with DatabaseConnection(":memory:") as db:
            await db.create_task_schema()
            task_repo = TaskRepository(db)

            # Create mock MCP client that fails with exception
            mcp_client = MagicMock()
            mcp_client.call_mcp = MagicMock(
                side_effect=ValueError("Invalid input parameter")
            )

            # Create executor
            provider_config = ProviderConfig(
                name="notebooklm",
                max_concurrent_calls=5,
                base_url="http://localhost:8000",
            )
            executor = ParallelExecutor(task_repo, mcp_client, [provider_config])

            # Create task in database first
            await task_repo.create(task_id="test-002", brain_id="brain-02")

            # Execute brain (will fail)
            result = await executor.execute_brain(
                task_id="test-002",
                brain_id="brain-02",
                query="test query",
                provider_name="notebooklm",
            )

            # Verify error doesn't contain stack trace
            error_msg = result["error"]
            assert "Traceback" not in error_msg, "Error should not contain traceback"
            assert "File " not in error_msg, "Error should not contain file references"
            assert "line " not in error_msg, "Error should not contain line numbers"
            assert "brain-02" in error_msg, "Error should contain brain_id"
