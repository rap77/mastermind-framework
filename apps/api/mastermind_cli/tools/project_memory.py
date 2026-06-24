#!/usr/bin/env python3
"""CLI bridge for first-party project memory retrieval via Bash.

Usage:
    python3 apps/api/mastermind_cli/tools/project_memory.py query \
        --project-id proj-001 --query "customer graph" --limit 3
    python3 apps/api/mastermind_cli/tools/project_memory.py backfill \
        --project-id proj-001 --limit 100
    python3 apps/api/mastermind_cli/tools/project_memory.py status \
        --project-id proj-001
    python3 apps/api/mastermind_cli/tools/project_memory.py doctor \
        --project-id proj-001

Environment:
    MM_MEMORY_DATABASE_URL: Optional explicit SQLAlchemy database URL.
    DATABASE_URL: Fallback explicit SQLAlchemy database URL.
    MM_MEMORY_BACKEND: Optional backend selector (currently ``sqlite`` only).
    MM_DB_PATH: SQLite file path fallback when ``MM_MEMORY_BACKEND=sqlite``.
    MM_MEMORY_VECTOR_BACKEND: Optional vector backend selector
        (``none`` | ``pgvector`` | ``qdrant``). Defaults to ``none``.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from typing import cast

from sqlalchemy import Table, func, select, text

# Allow running from repo root or from apps/api/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from mastermind_cli.memory_layer.embeddings import build_memory_index_payload
from mastermind_cli.memory_layer.contracts import (
    MemoryIndexProvider,
    VectorSearchProvider,
)
from mastermind_cli.memory_layer.indexing import create_memory_index_provider
from mastermind_cli.memory_layer.models import MemoryItem
from mastermind_cli.memory_layer.runtime import (
    build_graph_recall_from_env,
    build_memory_store_from_env,
    build_vector_provider_from_env,
)
from mastermind_cli.memory_layer.service import MemoryService
from mastermind_cli.memory_layer.store_postgres import (
    MemoryItemRecord,
    MemoryPreferenceRecord,
    MemorySessionRecord,
)
from mastermind_cli.project_state.database.base import Base
from mastermind_cli.project_state.database.session import (
    get_engine,
    get_session_factory,
)


logger = logging.getLogger(__name__)
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_handler)
logger.setLevel(logging.INFO)
logger.propagate = False


def _get_database_url() -> str:
    """Resolve the database URL for first-party memory retrieval.

    Resolution order:
    1. ``MM_MEMORY_DATABASE_URL``
    2. ``DATABASE_URL``
    3. ``MM_MEMORY_BACKEND=sqlite`` + ``MM_DB_PATH``

    Raises:
        ValueError: When no supported explicit configuration is available.

    """
    explicit_url = os.environ.get("MM_MEMORY_DATABASE_URL") or os.environ.get(
        "DATABASE_URL"
    )
    if explicit_url:
        return explicit_url

    backend = (os.environ.get("MM_MEMORY_BACKEND") or "").strip().lower()
    if backend == "sqlite":
        db_path = os.environ.get("MM_DB_PATH", "mastermind.db")
        if "://" in db_path:
            return db_path
        return f"sqlite:///{db_path}"

    if backend == "pglite":
        raise ValueError(
            "MM_MEMORY_BACKEND=pglite no está soportado por este CLI de Python. "
            "Usa MM_MEMORY_DATABASE_URL/DATABASE_URL con un backend SQLAlchemy real."
        )

    raise ValueError(
        "Configura MM_MEMORY_DATABASE_URL o DATABASE_URL. "
        "Si quieres SQLite local, usa MM_MEMORY_BACKEND=sqlite y MM_DB_PATH."
    )


def _emit_json(payload: object) -> None:
    """Emit a JSON payload through the module logger."""
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.stream = sys.stdout
    logger.info(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


def _get_vector_provider() -> VectorSearchProvider:
    """Resolve the configured vector provider for retrieval."""
    backend = os.environ.get("MM_MEMORY_VECTOR_BACKEND", "none").strip().lower()
    database_url = _get_database_url() if backend == "pgvector" else None
    return build_vector_provider_from_env(database_url)


def _get_index_provider() -> MemoryIndexProvider:
    """Resolve the configured index provider for backfill operations."""
    backend = os.environ.get("MM_MEMORY_INDEX_BACKEND", "none")
    database_url = (
        _get_database_url() if backend.strip().lower() == "pgvector" else None
    )
    return create_memory_index_provider(
        backend,
        database_url=database_url,
        embedding_backend=os.environ.get("MM_MEMORY_EMBEDDING_BACKEND", "none"),
        embedding_model=os.environ.get(
            "MM_MEMORY_EMBEDDING_MODEL",
            "sentence-transformers/all-mpnet-base-v2",
        ),
    )


def _record_to_memory_item(record: MemoryItemRecord) -> MemoryItem:
    """Convert a relational memory record into the canonical memory model."""
    return MemoryItem(
        memory_id=record.memory_id,
        memory_type=record.memory_type,
        title=record.title,
        content=record.content,
        project_id=record.project_id,
        brain_id=record.brain_id,
        niche=record.niche,
        visibility=record.visibility,
        source_kind=record.source_kind,
        source_ref=record.source_ref,
        tags=list(record.tags_json or []),
        metadata=dict(record.metadata_json or {}),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _ensure_memory_schema(database_url: str) -> None:
    """Create the canonical memory tables when they do not exist yet."""
    Base.metadata.create_all(
        bind=get_engine(database_url),
        tables=[
            cast(Table, MemoryItemRecord.__table__),
            cast(Table, MemoryPreferenceRecord.__table__),
            cast(Table, MemorySessionRecord.__table__),
        ],
    )


async def _cmd_query(
    args: argparse.Namespace,
    service: MemoryService | None = None,
) -> None:
    """Query project-scoped first-party memory results."""
    memory_service = service or MemoryService(
        build_memory_store_from_env(
            _get_database_url(),
            enable_vector=True,
            enable_index=False,
        )
    )
    results = await memory_service.fetch_project_context(
        project_id=args.project_id,
        query=args.query,
        limit=args.limit,
    )
    payload = [result.model_dump() for result in results]
    _emit_json(payload)


async def _cmd_backfill(
    args: argparse.Namespace,
    *,
    records: list[MemoryItemRecord] | None = None,
    index_provider: MemoryIndexProvider | None = None,
) -> None:
    """Backfill semantic index entries for existing canonical memory items."""
    selected_records = records
    if selected_records is None:
        database_url = _get_database_url()
        _ensure_memory_schema(database_url)
        session_factory = get_session_factory(database_url)
        with session_factory() as session:
            statement = select(MemoryItemRecord).order_by(
                MemoryItemRecord.created_at.asc()
            )
            if args.project_id:
                statement = statement.where(
                    MemoryItemRecord.project_id == args.project_id
                )
            selected_records = list(session.scalars(statement.limit(args.limit)))

    provider = index_provider or _get_index_provider()
    indexed = 0
    for record in selected_records:
        item = _record_to_memory_item(record)
        await provider.upsert(build_memory_index_payload(item))
        indexed += 1

    _emit_json(
        {
            "indexed": indexed,
            "project_id": args.project_id,
            "limit": args.limit,
        }
    )


def _detect_database_kind(database_url: str) -> str:
    """Return a compact database kind label for status output."""
    if database_url.startswith(("postgresql://", "postgres://")):
        return "postgresql"
    if database_url.startswith("sqlite"):
        return "sqlite"
    return "unknown"


def _collect_status(project_id: str | None = None) -> dict[str, object]:
    """Collect operational status for the first-party project memory layer."""
    database_url = _get_database_url()
    _ensure_memory_schema(database_url)
    database_kind = _detect_database_kind(database_url)
    vector_backend = os.environ.get("MM_MEMORY_VECTOR_BACKEND", "none")
    index_backend = os.environ.get("MM_MEMORY_INDEX_BACKEND", "none")
    graph_recall_backend = os.environ.get("MM_MEMORY_GRAPH_RECALL_BACKEND", "none")
    embedding_backend = os.environ.get("MM_MEMORY_EMBEDDING_BACKEND", "none")

    engine = get_engine(database_url)
    session_factory = get_session_factory(database_url)

    with engine.begin() as connection:
        table_rows = (
            connection.execute(
                text(
                    """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
                )
            ).fetchall()
            if database_kind == "sqlite"
            else connection.execute(
                text(
                    """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                """
                )
            ).fetchall()
        )

        table_names = {str(row[0]) for row in table_rows}
        pgvector_installed: bool | None = None
        if database_kind == "postgresql":
            pgvector_installed = bool(
                connection.execute(
                    text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                ).fetchone()
            )

    with session_factory() as session:
        memory_items_query = select(func.count()).select_from(MemoryItemRecord)
        if project_id:
            memory_items_query = memory_items_query.where(
                MemoryItemRecord.project_id == project_id
            )
        memory_items_count = int(session.scalar(memory_items_query) or 0)

    memory_embeddings_count: int | None = None
    if "mm_memory_embeddings" in table_names:
        with engine.begin() as connection:
            if project_id:
                result = connection.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM mm_memory_embeddings
                        WHERE project_id = :project_id
                        """
                    ),
                    {"project_id": project_id},
                ).scalar()
            else:
                result = connection.execute(
                    text("SELECT COUNT(*) FROM mm_memory_embeddings")
                ).scalar()
            memory_embeddings_count = int(result or 0)

    graph_recall_configured = True
    try:
        build_graph_recall_from_env(database_url)
    except Exception:
        graph_recall_configured = False

    return {
        "database_kind": database_kind,
        "project_id": project_id,
        "vector_backend": vector_backend,
        "index_backend": index_backend,
        "graph_recall_backend": graph_recall_backend,
        "graph_recall_configured": graph_recall_configured,
        "embedding_backend": embedding_backend,
        "tables": {
            "mm_memory_items": "mm_memory_items" in table_names,
            "mm_memory_embeddings": "mm_memory_embeddings" in table_names,
        },
        "counts": {
            "memory_items": memory_items_count,
            "memory_embeddings": memory_embeddings_count,
        },
        "pgvector_extension_installed": pgvector_installed,
    }


async def _cmd_status(args: argparse.Namespace) -> None:
    """Print operational status for the first-party project memory layer."""
    _emit_json(_collect_status(project_id=args.project_id))


def _build_doctor_report(status: dict[str, object]) -> dict[str, object]:
    """Build an actionable doctor report from raw status data."""
    database_kind = str(status.get("database_kind", "unknown"))
    vector_backend = str(status.get("vector_backend", "none"))
    index_backend = str(status.get("index_backend", "none"))
    graph_recall_backend = str(status.get("graph_recall_backend", "none"))
    graph_recall_configured = bool(
        status.get("graph_recall_configured", graph_recall_backend != "none")
    )
    counts = status.get("counts", {})
    tables = status.get("tables", {})

    memory_items = int(counts.get("memory_items", 0)) if isinstance(counts, dict) else 0
    memory_embeddings_raw = (
        counts.get("memory_embeddings") if isinstance(counts, dict) else None
    )
    memory_embeddings = (
        int(memory_embeddings_raw) if isinstance(memory_embeddings_raw, int) else None
    )
    has_items_table = (
        bool(tables.get("mm_memory_items")) if isinstance(tables, dict) else False
    )
    has_embeddings_table = (
        bool(tables.get("mm_memory_embeddings")) if isinstance(tables, dict) else False
    )
    pgvector_installed = status.get("pgvector_extension_installed")

    checks = {
        "has_memory_items_table": has_items_table,
        "has_memory_embeddings_table": has_embeddings_table,
        "pgvector_extension_ready": (
            True if database_kind != "postgresql" else bool(pgvector_installed)
        ),
        "vector_backend_enabled": vector_backend == "pgvector",
        "index_backend_enabled": index_backend == "pgvector",
        "graph_recall_enabled": graph_recall_configured,
        "has_memory_items": memory_items > 0,
        "has_memory_embeddings": (memory_embeddings or 0) > 0
        if memory_embeddings is not None
        else False,
    }

    next_steps: list[str] = []
    if database_kind != "postgresql":
        next_steps.append(
            "Usa PostgreSQL si quieres habilitar búsqueda semántica con pgvector."
        )
    if vector_backend != "pgvector":
        next_steps.append(
            "Configura MM_MEMORY_VECTOR_BACKEND=pgvector para consultas semánticas."
        )
    if index_backend != "pgvector":
        next_steps.append(
            "Configura MM_MEMORY_INDEX_BACKEND=pgvector para indexación semántica."
        )
    if graph_recall_backend == "none":
        next_steps.append(
            "Configura MM_MEMORY_GRAPH_RECALL_BACKEND=metadata para expansión relacional."
        )
    if graph_recall_backend != "none" and not graph_recall_configured:
        next_steps.append(
            "Corrige la configuración de graph recall; el backend actual no se puede inicializar."
        )
    if database_kind == "postgresql" and not bool(pgvector_installed):
        next_steps.append("Instala o habilita la extensión vector en PostgreSQL.")
    if memory_items > 0 and (memory_embeddings or 0) == 0:
        next_steps.append(
            "Ejecuta el comando backfill para indexar memorias históricas."
        )
    if memory_items == 0:
        next_steps.append(
            "Primero guarda memorias canónicas antes de probar retrieval semántico."
        )

    ready_for_semantic_query = (
        database_kind == "postgresql"
        and vector_backend == "pgvector"
        and index_backend == "pgvector"
        and graph_recall_configured
        and bool(pgvector_installed)
        and memory_items > 0
        and (memory_embeddings or 0) > 0
    )

    return {
        "ready_for_semantic_query": ready_for_semantic_query,
        "checks": checks,
        "next_steps": next_steps,
        "status": status,
    }


async def _cmd_doctor(args: argparse.Namespace) -> None:
    """Print an actionable doctor report for project memory readiness."""
    status = _collect_status(project_id=args.project_id)
    _emit_json(_build_doctor_report(status))


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Project memory CLI — query first-party memory results"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    query_parser = sub.add_parser("query", help="Query project-scoped memory")
    query_parser.add_argument("--project-id", required=True, help="Project ID")
    query_parser.add_argument("--query", required=True, help="Retrieval query")
    query_parser.add_argument(
        "--limit", type=int, default=3, help="Max results to return (default: 3)"
    )

    backfill_parser = sub.add_parser(
        "backfill", help="Backfill semantic index entries for existing memory"
    )
    backfill_parser.add_argument("--project-id", help="Optional project filter")
    backfill_parser.add_argument(
        "--limit", type=int, default=100, help="Max records to index (default: 100)"
    )

    status_parser = sub.add_parser("status", help="Show project memory status")
    status_parser.add_argument("--project-id", help="Optional project filter")

    doctor_parser = sub.add_parser(
        "doctor", help="Show readiness checks and next steps"
    )
    doctor_parser.add_argument("--project-id", help="Optional project filter")
    return parser


def main() -> None:
    """Run the project memory CLI."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "query":
        asyncio.run(_cmd_query(args))
    elif args.command == "backfill":
        asyncio.run(_cmd_backfill(args))
    elif args.command == "status":
        asyncio.run(_cmd_status(args))
    elif args.command == "doctor":
        asyncio.run(_cmd_doctor(args))


if __name__ == "__main__":
    main()
