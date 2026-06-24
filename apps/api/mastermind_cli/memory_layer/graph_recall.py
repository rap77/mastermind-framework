"""Optional graph-recall providers for retrieval follow-on work."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from mastermind_cli.project_state.database.session import get_session_factory

from .models import MemorySearchResult


class NoopMemoryGraphRecallProvider:
    """Graph recall provider that preserves the incoming results exactly."""

    async def expand(
        self,
        query: str,
        results: list[MemorySearchResult],
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Return results unchanged while the graph seam is disabled."""
        del query, scope
        return list(results[:limit])


class StaticMemoryGraphRecallProvider:
    """Minimal graph recall provider using a fixed adjacency map."""

    def __init__(
        self,
        related_by_memory_id: dict[str, list[MemorySearchResult]],
    ) -> None:
        """Store a fixed relation map for deterministic local expansion."""
        self._related_by_memory_id = related_by_memory_id

    async def expand(
        self,
        query: str,
        results: list[MemorySearchResult],
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Append related results after the ranked seed set without duplicates."""
        del query
        expanded = list(results)
        seen = {result.memory_id for result in expanded}

        for result in results:
            for related in self._related_by_memory_id.get(result.memory_id, []):
                if related.memory_id in seen:
                    continue
                if not self._matches_scope(related, scope):
                    continue
                expanded.append(
                    related.model_copy(
                        update={
                            "why_matched": "graph:related",
                        }
                    )
                )
                seen.add(related.memory_id)
                if len(expanded) >= limit:
                    return expanded[:limit]

        return expanded[:limit]

    def _matches_scope(
        self,
        result: MemorySearchResult,
        scope: dict[str, str | None] | None,
    ) -> bool:
        """Return whether a related result still satisfies the active retrieval scope."""
        if not scope:
            return True
        if scope.get("project_id") and result.project_id != scope["project_id"]:
            return False
        if scope.get("brain_id") and result.brain_id != scope["brain_id"]:
            return False
        if scope.get("memory_type") and result.memory_type != scope["memory_type"]:
            return False
        return True


class MetadataMemoryGraphRecallProvider:
    """Graph recall provider that expands persisted metadata relations."""

    def __init__(self, database_url: str) -> None:
        """Bind the provider to the shared memory database."""
        self._session_factory = get_session_factory(database_url)

    async def expand(
        self,
        query: str,
        results: list[MemorySearchResult],
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Append related memories listed in `metadata.related_memory_ids`."""
        del query
        expanded = list(results)
        seen = {result.memory_id for result in expanded}

        with self._session_factory() as session:
            for result in results:
                related_ids = self._load_related_ids(session, result.memory_id)
                for related_id in related_ids:
                    if related_id in seen:
                        continue
                    related = self._load_related_result(session, related_id)
                    if related is None or not self._matches_scope(related, scope):
                        continue
                    expanded.append(
                        related.model_copy(update={"why_matched": "graph:metadata"})
                    )
                    seen.add(related.memory_id)
                    if len(expanded) >= limit:
                        return expanded[:limit]

        return expanded[:limit]

    def _load_related_ids(self, session: Any, memory_id: str) -> list[str]:
        """Return persisted related-memory IDs for one memory item."""
        row = (
            session.execute(
                text(
                    """
                SELECT metadata
                FROM mm_memory_items
                WHERE memory_id = :memory_id
                """
                ),
                {"memory_id": memory_id},
            )
            .mappings()
            .first()
        )
        if row is None:
            return []
        metadata = row.get("metadata") or {}
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                return []
        if not isinstance(metadata, dict):
            return []
        related_ids = metadata.get("related_memory_ids")
        if not isinstance(related_ids, list):
            return []
        coerced: list[str] = []
        for related_id in related_ids:
            if isinstance(related_id, str):
                normalized = related_id.strip()
                if normalized:
                    coerced.append(normalized)
        return coerced

    def _load_related_result(
        self,
        session: Any,
        memory_id: str,
    ) -> MemorySearchResult | None:
        """Load one related memory row as a search result payload."""
        row = (
            session.execute(
                text(
                    """
                SELECT
                    memory_id,
                    title,
                    content,
                    memory_type,
                    project_id,
                    brain_id,
                    source_ref
                FROM mm_memory_items
                WHERE memory_id = :memory_id
                """
                ),
                {"memory_id": memory_id},
            )
            .mappings()
            .first()
        )
        if row is None:
            return None
        return MemorySearchResult(
            memory_id=str(row["memory_id"]),
            title=str(row["title"]),
            snippet=str(row["content"])[:240],
            score=0.25,
            memory_type=str(row["memory_type"]),
            project_id=str(row["project_id"])
            if row["project_id"] is not None
            else None,
            brain_id=str(row["brain_id"]) if row["brain_id"] is not None else None,
            why_matched=None,
            source_ref=str(row["source_ref"])
            if row["source_ref"] is not None
            else None,
        )

    def _matches_scope(
        self,
        result: MemorySearchResult,
        scope: dict[str, str | None] | None,
    ) -> bool:
        """Return whether a related result still satisfies the active retrieval scope."""
        if not scope:
            return True
        if scope.get("project_id") and result.project_id != scope["project_id"]:
            return False
        if scope.get("brain_id") and result.brain_id != scope["brain_id"]:
            return False
        if scope.get("memory_type") and result.memory_type != scope["memory_type"]:
            return False
        return True


__all__ = [
    "MetadataMemoryGraphRecallProvider",
    "NoopMemoryGraphRecallProvider",
    "StaticMemoryGraphRecallProvider",
]
