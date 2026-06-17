"""Engram-backed adapter for the Memory Layer contract."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from datetime import datetime, timezone
import json
from typing import Any

from .models import MemoryItem, MemorySearchResult

ObservationPayload = Mapping[str, Any]
SaveObservationCallable = Callable[..., Awaitable[ObservationPayload]]
SearchObservationsCallable = Callable[..., Awaitable[list[ObservationPayload]]]
GetObservationCallable = Callable[[str], Awaitable[ObservationPayload | None]]
SaveSessionSummaryCallable = Callable[..., Awaitable[None]]


class EngramMemoryStore:
    """Bridge Engram observation payloads into the first-party MemoryStore shape."""

    def __init__(
        self,
        *,
        save_observation: SaveObservationCallable,
        search_observations: SearchObservationsCallable,
        get_observation: GetObservationCallable | None = None,
        save_session_summary: SaveSessionSummaryCallable | None = None,
    ) -> None:
        """Initialize the adapter with Engram-facing callables.

        Args:
            save_observation: Raw Engram save hook for generic observations.
            search_observations: Raw Engram search hook.
            get_observation: Optional raw Engram lookup hook by observation ID.
            save_session_summary: Optional dedicated Engram session-summary hook.
        """
        self._save_observation = save_observation
        self._search_observations = search_observations
        self._get_observation = get_observation
        self._save_session_summary_hook = save_session_summary

    async def save_item(self, item: MemoryItem) -> MemoryItem:
        """Persist a canonical memory item through the Engram bridge."""
        saved = await self._save_observation(
            title=item.title,
            content=item.content,
            type=item.memory_type,
            project_id=item.project_id,
            brain_id=item.brain_id,
            niche=item.niche,
            visibility=item.visibility,
            source_kind=item.source_kind,
            source_ref=item.source_ref,
            tags=item.tags,
            metadata=item.metadata,
        )
        return self._to_memory_item(saved, fallback=item)

    async def get_item(self, memory_id: str) -> MemoryItem | None:
        """Return a single memory item if the underlying hook is available."""
        if self._get_observation is None:
            return None

        observation = await self._get_observation(memory_id)
        if observation is None:
            return None
        return self._to_memory_item(observation)

    async def search(
        self,
        query: str,
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Search Engram and normalize the ranked results."""
        observations = await self._search_observations(
            query=query,
            scope=scope,
            limit=limit,
        )
        return [self._to_search_result(observation) for observation in observations]

    async def list_recent(
        self,
        project_id: str,
        limit: int = 10,
    ) -> list[MemoryItem]:
        """List recent project-scoped items using the search hook as fallback."""
        observations = await self._search_observations(
            query="",
            scope={"project_id": project_id, "sort": "recent"},
            limit=limit,
        )
        return [self._to_memory_item(observation) for observation in observations]

    async def save_session_summary(
        self,
        session_id: str,
        summary: str,
        project_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        """Persist a session summary through the dedicated hook or generic save path."""
        if self._save_session_summary_hook is not None:
            await self._save_session_summary_hook(
                session_id=session_id,
                summary=summary,
                project_id=project_id,
                metadata=metadata,
            )
            return

        await self.save_item(
            MemoryItem(
                memory_id=None,
                memory_type="session_summary",
                title=f"Session summary: {session_id}",
                content=summary,
                project_id=project_id,
                brain_id=None,
                niche=None,
                visibility="project" if project_id else "personal",
                source_kind="session",
                source_ref=session_id,
                metadata={"session_id": session_id, **(metadata or {})},
            )
        )

    async def save_preference(
        self,
        key: str,
        value: object,
        scope: str,
        project_id: str | None = None,
    ) -> None:
        """Persist an operational preference through the generic memory bridge."""
        await self.save_item(
            MemoryItem(
                memory_id=None,
                memory_type="preference",
                title=f"Preference: {key}",
                content=json.dumps(value, separators=(",", ":")),
                project_id=project_id,
                brain_id=None,
                niche=None,
                visibility=scope,
                source_kind="preference",
                source_ref=f"preference:{key}",
                tags=["preference", key],
                metadata={"key": key, "scope": scope},
            )
        )

    def _to_memory_item(
        self,
        observation: ObservationPayload,
        *,
        fallback: MemoryItem | None = None,
    ) -> MemoryItem:
        """Map a raw Engram observation into the canonical memory item shape."""
        return MemoryItem(
            memory_id=self._string_or_none(observation.get("id"))
            or (fallback.memory_id if fallback else None),
            memory_type=self._string_or_none(observation.get("type"))
            or (fallback.memory_type if fallback else "note"),
            title=self._string_or_none(observation.get("title"))
            or (fallback.title if fallback else "Untitled memory"),
            content=self._string_or_none(observation.get("content"))
            or (fallback.content if fallback else ""),
            project_id=self._string_or_none(observation.get("project_id"))
            or (fallback.project_id if fallback else None),
            brain_id=self._string_or_none(observation.get("brain_id"))
            or (fallback.brain_id if fallback else None),
            niche=self._string_or_none(observation.get("niche"))
            or (fallback.niche if fallback else None),
            visibility=self._string_or_none(observation.get("visibility"))
            or (fallback.visibility if fallback else "project"),
            source_kind=self._string_or_none(observation.get("source_kind"))
            or (fallback.source_kind if fallback else None),
            source_ref=self._string_or_none(observation.get("source_ref"))
            or (fallback.source_ref if fallback else None),
            tags=self._string_list(observation.get("tags"))
            or (fallback.tags if fallback else []),
            metadata=self._mapping_copy(observation.get("metadata"))
            or (fallback.metadata if fallback else {}),
            created_at=self._parse_datetime(observation.get("created_at"))
            or (fallback.created_at if fallback else datetime.now(timezone.utc)),
            updated_at=self._parse_datetime(observation.get("updated_at"))
            or self._parse_datetime(observation.get("created_at"))
            or (fallback.updated_at if fallback else datetime.now(timezone.utc)),
        )

    def _to_search_result(self, observation: ObservationPayload) -> MemorySearchResult:
        """Map a raw Engram search observation into a ranked search result."""
        content = self._string_or_none(observation.get("content")) or ""
        return MemorySearchResult(
            memory_id=self._string_or_none(observation.get("id")) or "",
            title=self._string_or_none(observation.get("title")) or "Untitled memory",
            snippet=content[:240],
            score=self._float_value(observation.get("score")),
            memory_type=self._string_or_none(observation.get("type")) or "note",
            project_id=self._string_or_none(observation.get("project_id")),
            brain_id=self._string_or_none(observation.get("brain_id")),
            why_matched=self._string_or_none(observation.get("why_matched")),
            source_ref=self._string_or_none(observation.get("source_ref")),
        )

    def _parse_datetime(self, value: object) -> datetime | None:
        """Parse an ISO timestamp into a timezone-aware datetime when possible."""
        if not isinstance(value, str) or not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _string_or_none(self, value: object) -> str | None:
        """Normalize a payload scalar into an optional string."""
        if value is None:
            return None
        text = str(value)
        return text if text else None

    def _string_list(self, value: object) -> list[str]:
        """Normalize a payload field into a list of strings."""
        if not isinstance(value, list):
            return []
        return [str(item) for item in value if item is not None]

    def _mapping_copy(self, value: object) -> dict[str, Any]:
        """Return a detached dict copy when the payload metadata is mapping-like."""
        if not isinstance(value, Mapping):
            return {}
        return {str(key): data for key, data in value.items()}

    def _float_value(self, value: object) -> float:
        """Normalize a payload score into a float."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        return 0.0
