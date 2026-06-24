"""Application service for the first-party memory layer."""

from __future__ import annotations

from collections.abc import Sequence

from .contracts import MemoryStore
from .models import MemoryItem, MemorySearchResult


class MemoryService:
    """Thin application layer over a MemoryStore backend."""

    def __init__(self, store: MemoryStore) -> None:
        """Initialize the service with a concrete store backend."""
        self._store = store

    async def record_session_summary(
        self,
        session_id: str,
        summary: str,
        project_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        """Persist a session continuity summary."""
        await self._store.save_session_summary(
            session_id=session_id,
            summary=summary,
            project_id=project_id,
            metadata=metadata,
        )

    async def record_learning(
        self,
        *,
        title: str,
        content: str,
        project_id: str | None = None,
        brain_id: str | None = None,
        niche: str | None = None,
        memory_type: str = "lesson",
        visibility: str = "project",
        source_kind: str | None = None,
        source_ref: str | None = None,
        tags: list[str] | None = None,
        related_memory_ids: Sequence[str | None] | None = None,
        metadata: dict[str, object] | None = None,
    ) -> MemoryItem:
        """Persist a reusable lesson, fix, pattern, or decision memory item."""
        normalized_tags = [memory_type]
        if tags:
            normalized_tags.extend(tag for tag in tags if tag not in normalized_tags)

        normalized_metadata = dict(metadata or {})
        normalized_related_ids = self._normalize_related_memory_ids(
            related_memory_ids,
            normalized_metadata.get("related_memory_ids"),
        )
        if normalized_related_ids:
            normalized_metadata["related_memory_ids"] = normalized_related_ids
        elif "related_memory_ids" in normalized_metadata:
            normalized_metadata.pop("related_memory_ids")

        item = MemoryItem(
            memory_id=None,
            memory_type=memory_type,
            title=title,
            content=content,
            project_id=project_id,
            brain_id=brain_id,
            niche=niche,
            visibility=visibility,
            source_kind=source_kind,
            source_ref=source_ref,
            tags=normalized_tags,
            metadata=normalized_metadata,
        )
        return await self._store.save_item(item)

    async def record_preference(
        self,
        *,
        key: str,
        value: object,
        scope: str,
        project_id: str | None = None,
    ) -> None:
        """Persist an operational preference."""
        await self._store.save_preference(
            key=key,
            value=value,
            scope=scope,
            project_id=project_id,
        )

    async def fetch_project_context(
        self,
        project_id: str,
        query: str,
        *,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Retrieve project-scoped memory context for a query."""
        return await self._store.search(
            query,
            scope={"project_id": project_id},
            limit=limit,
        )

    def _normalize_related_memory_ids(
        self,
        related_memory_ids: Sequence[str | None] | None,
        existing_value: object,
    ) -> list[str]:
        """Merge and dedupe related memory IDs into a stable list."""
        merged: list[str] = []
        for value in self._coerce_related_memory_ids(existing_value):
            if value not in merged:
                merged.append(value)
        for value in self._coerce_related_memory_ids(related_memory_ids):
            if value not in merged:
                merged.append(value)
        return merged

    def _coerce_related_memory_ids(self, value: object) -> list[str]:
        """Coerce a metadata payload into related memory IDs when possible."""
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            coerced: list[str] = []
            for item in value:
                if not isinstance(item, str):
                    continue
                normalized = item.strip()
                if normalized:
                    coerced.append(normalized)
            return coerced
        return []
