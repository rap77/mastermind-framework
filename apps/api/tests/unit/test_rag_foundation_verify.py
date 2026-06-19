"""Unit tests for pgvector + LangSmith foundation verification helper."""

from __future__ import annotations

import json
from pathlib import Path

from mastermind_cli.rag.foundation_verify import build_foundation_report


def test_foundation_report_passes_against_current_repo() -> None:
    """The current repository satisfies the expected foundation markers."""
    repo_root = Path(__file__).resolve().parents[4]

    report = build_foundation_report(repo_root=repo_root)

    assert report.status == "passed"
    assert all(check.passed for check in report.checks)


def test_foundation_report_json_is_operator_readable() -> None:
    """The report serializes to JSON with stable top-level keys."""
    repo_root = Path(__file__).resolve().parents[4]

    report = build_foundation_report(repo_root=repo_root)
    payload = json.loads(report.to_json())

    assert payload["status"] == "passed"
    assert payload["repo_root"] == str(repo_root)
    assert isinstance(payload["checks"], list)
    assert {check["name"] for check in payload["checks"]} >= {
        "pgvector_migration",
        "rag_similarity_query",
        "langsmith_dispatch_hook",
        "langsmith_task_runner_hook",
        "langsmith_import_available",
    }
