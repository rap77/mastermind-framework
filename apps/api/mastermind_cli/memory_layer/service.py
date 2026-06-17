"""Application service for the first-party memory layer."""

from __future__ import annotations

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
        metadata: dict[str, object] | None = None,
    ) -> MemoryItem:
        """Persist a reusable lesson, fix, pattern, or decision memory item."""
        normalized_tags = [memory_type]
        if tags:
            normalized_tags.extend(tag for tag in tags if tag not in normalized_tags)

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
            metadata=dict(metadata or {}),
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
