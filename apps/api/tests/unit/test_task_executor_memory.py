"""Tests for task-executor memory helper commands."""

from __future__ import annotations

import os

from mastermind_cli.mm_flow.task_executor_memory import (
    _build_memory_env_prefix,
    build_query_command,
    format_project_context,
    parse_brain_memory_results,
)


def test_build_memory_env_prefix_defaults_to_legacy_sqlite() -> None:
    """Without env config, the helper should preserve the legacy sqlite defaults."""
    previous = {
        key: os.environ.get(key)
        for key in (
            "MM_MEMORY_DATABASE_URL",
            "DATABASE_URL",
            "MM_MEMORY_BACKEND",
            "MM_DB_PATH",
        )
    }
    try:
        for key in previous:
            os.environ.pop(key, None)
        assert (
            _build_memory_env_prefix()
            == "MM_MEMORY_BACKEND=sqlite MM_DB_PATH=mastermind.db"
        )
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_build_query_command_uses_project_memory_bridge_when_query_present() -> None:
    """Project retrieval should route to the first-party project-memory CLI."""
    command = build_query_command(
        project_id="proj-001",
        query="customer graph",
        limit=4,
    )

    assert "project_memory.py" in command
    assert "--project-id proj-001" in command
    assert "--query 'customer graph'" in command
    assert "--limit 4" in command


def test_build_query_command_passes_explicit_memory_database_url() -> None:
    """Project retrieval should forward explicit DB configuration when present."""
    previous = os.environ.get("MM_MEMORY_DATABASE_URL")
    try:
        os.environ["MM_MEMORY_DATABASE_URL"] = "postgresql://memory-url"
        command = build_query_command(project_id="proj-001", query="customer graph")
    finally:
        if previous is None:
            os.environ.pop("MM_MEMORY_DATABASE_URL", None)
        else:
            os.environ["MM_MEMORY_DATABASE_URL"] = previous

    assert "MM_MEMORY_DATABASE_URL=postgresql://memory-url" in command
    assert "project_memory.py" in command


def test_format_project_context_renders_retrieval_results() -> None:
    """Formatted project context should expose title, why_matched, and snippet."""
    rendered = format_project_context(
        [
            {
                "title": "Customer graph launch note",
                "snippet": "Launch note for customer graph recall.",
                "why_matched": "fusion:lexical+vector",
                "score": 2.75,
            }
        ]
    )

    assert "Relevant Project Memory" in rendered
    assert "Customer graph launch note" in rendered
    assert "fusion:lexical+vector" in rendered
    assert "Launch note for customer graph recall." in rendered


def test_parse_brain_memory_results_logs_invalid_json(caplog) -> None:
    """Invalid JSON should be logged instead of failing silently."""
    caplog.set_level("WARNING")

    records = parse_brain_memory_results("not-json")

    assert records == []
    assert "Failed to parse brain memory JSON output" in caplog.text
