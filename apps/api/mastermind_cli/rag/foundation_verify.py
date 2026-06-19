"""Focused verification surface for pgvector and LangSmith foundations.

This module audits the current repository for the minimum assumptions that make
the pgvector RAG foundation and LangSmith tracing foundation believable to
another operator or model. It is intentionally read-only and emits a JSON
report rather than changing runtime behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib.util
import json
from pathlib import Path

import click


@dataclass(frozen=True)
class FoundationCheck:
    """Single foundation verification result."""

    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class FoundationReport:
    """Operator-facing verification report for foundation assumptions."""

    status: str
    repo_root: str
    checks: list[FoundationCheck]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation of the report."""
        return {
            "status": self.status,
            "repo_root": self.repo_root,
            "checks": [asdict(check) for check in self.checks],
        }

    def to_json(self) -> str:
        """Serialize the report as pretty JSON."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


def build_foundation_report(repo_root: Path | None = None) -> FoundationReport:
    """Build a focused report for pgvector and LangSmith foundations.

    Args:
        repo_root: Optional repository root override.

    Returns:
        Structured foundation report.
    """
    root = repo_root or Path(__file__).resolve().parents[4]

    rag_migration = (
        root
        / "apps"
        / "api"
        / "mastermind_cli"
        / "rag"
        / "migrations"
        / "001_create_brain_embeddings.sql"
    )
    rag_search = root / "apps" / "api" / "mastermind_cli" / "rag" / "search.py"
    dispatch_engine = (
        root / "apps" / "api" / "mastermind_cli" / "mm_flow" / "dispatch_engine.py"
    )
    task_runner = (
        root / "apps" / "api" / "mastermind_cli" / "api" / "services" / "task_runner.py"
    )

    checks = [
        _check_pgvector_migration(rag_migration),
        _check_rag_similarity_query(rag_search),
        _check_langsmith_dispatch_hook(dispatch_engine),
        _check_langsmith_task_runner_hook(task_runner),
        _check_langsmith_import_availability(),
    ]
    status = "passed" if all(check.passed for check in checks) else "failed"
    return FoundationReport(status=status, repo_root=str(root), checks=checks)


def _check_pgvector_migration(migration_file: Path) -> FoundationCheck:
    """Verify the expected pgvector migration markers are present."""
    if not migration_file.exists():
        return FoundationCheck(
            name="pgvector_migration",
            passed=False,
            detail=f"Missing migration file: {migration_file}",
        )

    content = migration_file.read_text(encoding="utf-8")
    required_markers = [
        "CREATE EXTENSION IF NOT EXISTS vector;",
        "CREATE TABLE IF NOT EXISTS brain_embeddings",
        "embedding       vector(768)",
        "USING hnsw",
        "vector_cosine_ops",
    ]
    missing = [marker for marker in required_markers if marker not in content]
    if missing:
        return FoundationCheck(
            name="pgvector_migration",
            passed=False,
            detail=f"Missing expected migration markers: {missing}",
        )

    return FoundationCheck(
        name="pgvector_migration",
        passed=True,
        detail="brain_embeddings migration includes vector extension, schema, and HNSW cosine index markers",
    )


def _check_rag_similarity_query(search_file: Path) -> FoundationCheck:
    """Verify the RAG search path still uses pgvector cosine search semantics."""
    if not search_file.exists():
        return FoundationCheck(
            name="rag_similarity_query",
            passed=False,
            detail=f"Missing search file: {search_file}",
        )

    content = search_file.read_text(encoding="utf-8")
    required_markers = [
        "1.0 - (embedding <=> $1::vector) AS score",
        "collection_type = $3",
        "ORDER BY embedding <=> $1::vector",
    ]
    missing = [marker for marker in required_markers if marker not in content]
    if missing:
        return FoundationCheck(
            name="rag_similarity_query",
            passed=False,
            detail=f"Missing expected similarity-search markers: {missing}",
        )

    return FoundationCheck(
        name="rag_similarity_query",
        passed=True,
        detail="similarity_search still filters by collection and uses cosine-distance pgvector ordering",
    )


def _check_langsmith_dispatch_hook(dispatch_file: Path) -> FoundationCheck:
    """Verify the dispatch engine still exposes the intended LangSmith seam."""
    if not dispatch_file.exists():
        return FoundationCheck(
            name="langsmith_dispatch_hook",
            passed=False,
            detail=f"Missing dispatch engine file: {dispatch_file}",
        )

    content = dispatch_file.read_text(encoding="utf-8")
    required_markers = [
        "from langsmith import traceable",
        '@traceable(name="brain_dispatch")',
        "from langsmith import get_current_run_tree",
        "pass  # LangSmith is optional — never fail dispatch because of tracing",
    ]
    missing = [marker for marker in required_markers if marker not in content]
    if missing:
        return FoundationCheck(
            name="langsmith_dispatch_hook",
            passed=False,
            detail=f"Missing expected dispatch LangSmith markers: {missing}",
        )

    return FoundationCheck(
        name="langsmith_dispatch_hook",
        passed=True,
        detail="dispatch engine keeps traceable decorator plus fail-soft metadata update path",
    )


def _check_langsmith_task_runner_hook(task_runner_file: Path) -> FoundationCheck:
    """Verify task runner still treats LangSmith metadata updates as optional."""
    if not task_runner_file.exists():
        return FoundationCheck(
            name="langsmith_task_runner_hook",
            passed=False,
            detail=f"Missing task runner file: {task_runner_file}",
        )

    content = task_runner_file.read_text(encoding="utf-8")
    required_markers = [
        "from langsmith import get_current_run_tree",
        'rt.metadata.update({"rag_enabled": rag_enabled})',
        "pass  # LangSmith optional — never fail brain execution",
    ]
    missing = [marker for marker in required_markers if marker not in content]
    if missing:
        return FoundationCheck(
            name="langsmith_task_runner_hook",
            passed=False,
            detail=f"Missing expected task-runner LangSmith markers: {missing}",
        )

    return FoundationCheck(
        name="langsmith_task_runner_hook",
        passed=True,
        detail="task runner preserves fail-soft LangSmith metadata updates for rag_enabled",
    )


def _check_langsmith_import_availability() -> FoundationCheck:
    """Report whether the current environment can import LangSmith."""
    installed = importlib.util.find_spec("langsmith") is not None
    return FoundationCheck(
        name="langsmith_import_available",
        passed=installed,
        detail=(
            "langsmith import is available in the current environment"
            if installed
            else "langsmith import is not available in the current environment"
        ),
    )


def main() -> None:
    """CLI entry point for the foundation verification report."""
    report = build_foundation_report()
    click.echo(report.to_json())


if __name__ == "__main__":
    main()
