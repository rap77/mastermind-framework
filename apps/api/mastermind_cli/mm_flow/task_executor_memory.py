"""Task-executor memory helpers — C3.16, C3.17.

Provides functions that task-executor can call (via Bash) to:
- C3.16: Query brain_memory.py for relevant patterns at subtask start
- C3.17: Log successful subtask completions to brain_memory.py

These are thin wrappers that produce Bash-callable shell commands.
The task-executor agent invokes these by running the generated commands.

Why this approach:
- brain_memory.py is a Bash CLI tool (not importable as Python module from agents)
- task-executor runs Bash tool to call brain_memory.py commands
- This module provides the argument construction logic and documentation

Usage (by task-executor agent in system prompt context):
    from mastermind_cli.mm_flow.task_executor_memory import (
        build_query_command,
        build_log_command,
    )

    # C3.16: At subtask start — get prior patterns
    cmd = build_query_command(brain_id="task-executor", limit=3)
    # Run: python3 apps/api/mastermind_cli/tools/brain_memory.py query --brain-id task-executor --limit 3

    # C3.17: After successful subtask — log what worked
    cmd = build_log_command(
        brain_id="task-executor",
        problem=subtask_description,
        solution=what_worked,
        status="success",
    )
"""

from __future__ import annotations

import json
import os
import shlex

# Default path to brain_memory.py (relative to repo root)
_DEFAULT_BRAIN_MEMORY_PATH = "apps/api/mastermind_cli/tools/brain_memory.py"
_DEFAULT_PROJECT_MEMORY_PATH = "apps/api/mastermind_cli/tools/project_memory.py"


def _build_memory_env_prefix() -> str:
    """Build a shell-safe env prefix for memory CLI commands.

    Prefers explicit SQLAlchemy URLs when present. Falls back to the legacy
    SQLite path only when the caller explicitly selected the sqlite backend.
    """
    env_parts: list[str] = []

    explicit_memory_url = os.environ.get("MM_MEMORY_DATABASE_URL")
    if explicit_memory_url:
        env_parts.append(f"MM_MEMORY_DATABASE_URL={shlex.quote(explicit_memory_url)}")

    explicit_database_url = os.environ.get("DATABASE_URL")
    if explicit_database_url:
        env_parts.append(f"DATABASE_URL={shlex.quote(explicit_database_url)}")

    memory_backend = os.environ.get("MM_MEMORY_BACKEND")
    if memory_backend:
        env_parts.append(f"MM_MEMORY_BACKEND={shlex.quote(memory_backend)}")

    db_path = os.environ.get("MM_DB_PATH")
    if db_path:
        env_parts.append(f"MM_DB_PATH={shlex.quote(db_path)}")

    if not env_parts:
        env_parts.append("MM_MEMORY_BACKEND=sqlite")
        env_parts.append("MM_DB_PATH=mastermind.db")

    return " ".join(env_parts)


def build_query_command(
    project_id: str | None = None,
    query: str | None = None,
    brain_id: str = "task-executor",
    limit: int = 3,
    brain_memory_path: str = _DEFAULT_BRAIN_MEMORY_PATH,
    project_memory_path: str = _DEFAULT_PROJECT_MEMORY_PATH,
) -> str:
    """Build the Bash command to query brain memory at subtask start.

    C3.16: At the start of each subtask, query brain_memory.py for
    the last N experience records of this brain. Include results in
    the subtask's execution context to reuse successful patterns.

    When ``project_id`` and ``query`` are provided, this returns a command for the
    first-party memory-layer retrieval bridge. Otherwise it keeps the legacy
    behavior of querying recent experience records by ``brain_id``.

    Args:
        project_id: Optional project identifier for first-party retrieval.
        query: Optional retrieval query for first-party project context.
        brain_id: Brain ID to query in the legacy experience store.
        limit: Max records to return (default: 3).
        brain_memory_path: Path to the legacy brain_memory.py script.
        project_memory_path: Path to the first-party project_memory.py script.

    Returns:
        Shell command string (safe to pass to Bash tool)

    Example output:
        MM_DB_PATH=mastermind.db python3 apps/api/mastermind_cli/tools/brain_memory.py
            query --brain-id task-executor --limit 3
    """
    env_prefix = _build_memory_env_prefix()
    if project_id and query:
        return (
            f"{env_prefix} "
            f"python3 {shlex.quote(project_memory_path)} "
            f"query --project-id {shlex.quote(project_id)} "
            f"--query {shlex.quote(query)} --limit {limit}"
        )
    return (
        f"{env_prefix} "
        f"python3 {shlex.quote(brain_memory_path)} "
        f"query --brain-id {shlex.quote(brain_id)} --limit {limit}"
    )


def build_log_command(
    problem: str,
    solution: str,
    brain_id: str = "task-executor",
    status: str = "success",
    duration_ms: int = 0,
    trace_id: str | None = None,
    brain_memory_path: str = _DEFAULT_BRAIN_MEMORY_PATH,
) -> str:
    """Build the Bash command to log a successful subtask completion.

    C3.17: After completing a subtask successfully, log what worked
    so future subtasks can reuse the pattern.

    Args:
        problem: Description of the problem solved (e.g. subtask description)
        solution: What worked (e.g. "used ExperienceLogger with quality_score param")
        brain_id: Brain ID (default: "task-executor")
        status: Execution status (default: "success")
        duration_ms: How long it took in milliseconds
        trace_id: Optional trace/session ID for lineage
        brain_memory_path: Path to brain_memory.py script

    Returns:
        Shell command string (safe to pass to Bash tool)
    """
    env_prefix = _build_memory_env_prefix()
    input_json = json.dumps({"problem": problem})
    output_json = json.dumps({"solution": solution})

    cmd = (
        f"{env_prefix} "
        f"python3 {shlex.quote(brain_memory_path)} "
        f"log --brain-id {shlex.quote(brain_id)} "
        f"--input {shlex.quote(input_json)} "
        f"--output {shlex.quote(output_json)} "
        f"--status {shlex.quote(status)} "
        f"--duration-ms {duration_ms}"
    )
    if trace_id:
        cmd += f" --trace-id {shlex.quote(trace_id)}"

    return cmd


def parse_brain_memory_results(
    json_output: str,
) -> list[dict[str, str | dict[str, str]]]:
    """Parse the JSON output from brain_memory.py query command.

    Args:
        json_output: Raw stdout from brain_memory.py query command

    Returns:
        List of experience record dicts, or [] on parse error

    Example record structure:
        {
            "id": "uuid",
            "timestamp": "2026-05-13T...",
            "status": "success",
            "duration_ms": 3000,
            "output_json": {"solution": "..."},
            "custom_metadata": {...}
        }
    """
    try:
        records = json.loads(json_output)
        if isinstance(records, list):
            return records
    except (json.JSONDecodeError, ValueError):
        pass
    return []


def format_memory_context(records: list[dict[str, str | dict[str, str]]]) -> str:
    """Format brain memory records as readable context for task-executor.

    Produces a concise summary of past patterns that the agent can
    include in its reasoning about the current subtask.

    Args:
        records: List of experience record dicts from parse_brain_memory_results()

    Returns:
        Human-readable context string (empty if no records)
    """
    if not records:
        return ""

    lines = ["## Prior Patterns from Brain Memory:"]
    for i, record in enumerate(records, 1):
        output_raw = record.get("output_json", {})
        output: dict[str, str] = output_raw if isinstance(output_raw, dict) else {}
        solution: str = (
            output.get("solution", "(no solution recorded)") or "(no solution recorded)"
        )
        status_raw = record.get("status", "unknown")
        status: str = status_raw if isinstance(status_raw, str) else "unknown"
        ts_raw = record.get("timestamp", "")
        timestamp: str = (
            ts_raw[:19] if isinstance(ts_raw, str) else ""
        )  # Trim to seconds

        lines.append(f"\n### Pattern {i} ({timestamp}, {status}):")
        lines.append(f"Solution: {solution}")

    return "\n".join(lines)


def format_project_context(records: list[dict[str, object]]) -> str:
    """Format first-party project retrieval results as readable context."""
    if not records:
        return ""

    lines = ["## Relevant Project Memory:"]
    for index, record in enumerate(records, 1):
        title = str(record.get("title", "(untitled)"))
        snippet = str(record.get("snippet", "(no snippet)"))
        why_matched = str(record.get("why_matched", "unknown"))
        score = record.get("score", 0.0)
        lines.append(f"\n### Memory {index}: {title}")
        lines.append(f"Why: {why_matched} (score={score})")
        lines.append(f"Snippet: {snippet}")
    return "\n".join(lines)
