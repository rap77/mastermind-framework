"""Memory Layer protocol contracts."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import MemoryItem, MemorySearchResult


@runtime_checkable
class MemoryStore(Protocol):
    """Contract for persistent memory backends."""

    async def save_item(self, item: MemoryItem) -> MemoryItem:
        """Persist a memory item and return the stored representation."""

    async def get_item(self, memory_id: str) -> MemoryItem | None:
        """Return a memory item by identifier, or None when missing."""

    async def search(
        self,
        query: str,
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Search memory using an optional scope and bounded result limit."""

    async def list_recent(
        self,
        project_id: str,
        limit: int = 10,
    ) -> list[MemoryItem]:
        """Return recent memory items for a project."""

    async def save_session_summary(
        self,
        session_id: str,
        summary: str,
        project_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        """Persist a session summary for later continuity retrieval."""

    async def save_preference(
        self,
        key: str,
        value: object,
        scope: str,
        project_id: str | None = None,
    ) -> None:
        """Persist an operational preference in the selected scope."""
