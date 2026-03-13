"""
BrainErrorFormatter - Format brain execution errors for user-facing output.

This module provides error formatting utilities that hide raw stack traces
from users while showing actionable error messages with contextual hints.
"""

from typing import Dict, Any


class BrainErrorFormatter:
    """Format brain execution errors for user-facing output.

    This formatter provides:
    - Clear error messages with brain_id and error type
    - Contextual hints for common MCP errors (rate limit, timeout, etc.)
    - Optional stack traces for debug mode only
    - Summary formatting for parallel execution results

    Example:
        >>> error = ValueError("Invalid input")
        >>> formatted = BrainErrorFormatter.format_error("brain-01", error)
        >>> print(formatted)
        ❌ Brain 'brain-01' failed: ValueError
           Invalid input
    """

    MCP_ERROR_HINTS = {
        "rate limit": "The API rate limit was reached. Try reducing concurrent tasks or wait a moment.",
        "timeout": "The brain took too long to respond. Try a simpler query or check network connectivity.",
        "timed out": "The brain took too long to respond. Try a simpler query or check network connectivity.",
        "not found": "The requested brain was not found. Check brain_id in configuration.",
        "unauthorized": "API credentials are invalid. Check MCP configuration.",
    }

    @classmethod
    def format_error(
        cls,
        brain_id: str,
        error: Exception,
        include_traceback: bool = False
    ) -> str:
        """Format error for user display.

        This method creates a user-friendly error message with:
        - Brain identifier and error type
        - Error message
        - Contextual hint (if known error pattern)
        - Optional traceback (debug mode only)

        Args:
            brain_id: Brain that failed
            error: Exception that occurred
            include_traceback: If True, include full traceback (debug mode only)

        Returns:
            Formatted error message as string
        """
        error_type = type(error).__name__
        error_msg = str(error)

        # Check for known MCP error patterns
        hint = None
        error_lower = error_msg.lower()
        for pattern, hint_text in cls.MCP_ERROR_HINTS.items():
            if pattern in error_lower:
                hint = hint_text
                break

        # Build formatted message
        lines = [
            f"❌ Brain '{brain_id}' failed: {error_type}",
            f"   {error_msg}"
        ]

        if hint:
            lines.append(f"   💡 Hint: {hint}")

        if include_traceback:
            import traceback
            lines.append("\n" + "".join(traceback.format_exception(type(error), error, error.__traceback__)))

        return "\n".join(lines)

    @classmethod
    def format_parallel_summary(
        cls,
        results: Dict[str, Dict[str, Any]]
    ) -> str:
        """Format summary of parallel execution results.

        This method creates a concise summary showing:
        - Total successful vs total tasks
        - Count of completed tasks
        - Count of failed tasks (if any)
        - Count of cancelled tasks (if any)

        Args:
            results: Dict of brain_id -> result dict with "status" key

        Returns:
            Formatted summary as string
        """
        completed = sum(1 for r in results.values() if r.get("status") == "completed")
        failed = sum(1 for r in results.values() if r.get("status") == "failed")
        cancelled = sum(1 for r in results.values() if r.get("status") == "cancelled")
        total = len(results)

        lines = [
            f"📊 Execution Summary: {completed}/{total} successful",
            f"   ✅ Completed: {completed}",
        ]

        if failed > 0:
            lines.append(f"   ❌ Failed: {failed}")
        if cancelled > 0:
            lines.append(f"   ⚠️  Cancelled: {cancelled}")

        return "\n".join(lines)
