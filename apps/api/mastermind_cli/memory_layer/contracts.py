"""Memory Layer protocol contracts."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import (
    CheckpointRecord,
    ContextSnapshot,
    DecisionRecord,
    MemoryIndexPayload,
    MemoryItem,
    MemorySearchResult,
    RunSummary,
    VectorCandidate,
)


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


@runtime_checkable
class CheckpointStore(Protocol):
    """Contract for project-scoped checkpoint persistence."""

    async def save_checkpoint(self, checkpoint: CheckpointRecord) -> CheckpointRecord:
        """Persist a checkpoint and return the stored record."""

    async def get_latest_checkpoint(
        self,
        project_id: str,
        task_id: str | None = None,
    ) -> CheckpointRecord | None:
        """Return the latest checkpoint for a project or task."""

    async def list_recent_checkpoints(
        self,
        project_id: str,
        limit: int = 10,
    ) -> list[CheckpointRecord]:
        """Return recent checkpoints for a project."""


@runtime_checkable
class DecisionStore(Protocol):
    """Contract for project-scoped decision persistence."""

    async def save_decision(self, decision: DecisionRecord) -> DecisionRecord:
        """Persist a decision and return the stored record."""

    async def list_recent_decisions(
        self,
        project_id: str,
        limit: int = 10,
        task_id: str | None = None,
    ) -> list[DecisionRecord]:
        """Return recent decisions for a project."""


@runtime_checkable
class ContextSnapshotStore(Protocol):
    """Contract for compact resume snapshots."""

    async def build_context_snapshot(
        self,
        project_id: str,
        task_id: str | None = None,
        limit: int = 10,
    ) -> ContextSnapshot:
        """Return a compact resume snapshot for the active project."""

    async def save_run_summary(self, run_summary: RunSummary) -> RunSummary:
        """Persist a run summary and return the stored record."""


@runtime_checkable
class VectorSearchProvider(Protocol):
    """Contract for optional vector candidate providers."""

    async def search(
        self,
        query: str,
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[str]:
        """Return ranked candidate memory IDs for the provided query."""


@runtime_checkable
class VectorCandidateProvider(Protocol):
    """Contract for optional scored vector candidate providers."""

    async def search_candidates(
        self,
        query: str,
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[VectorCandidate]:
        """Return ranked semantic candidates with explicit scores."""


@runtime_checkable
class MemoryIndexProvider(Protocol):
    """Contract for optional vector indexers over canonical memory items."""

    async def upsert(self, payload: MemoryIndexPayload) -> None:
        """Insert or refresh the vector index entry for a memory item."""


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Contract for optional embedding generators."""

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text."""


@runtime_checkable
class MemoryReranker(Protocol):
    """Contract for optional post-fusion reranking providers."""

    async def rerank(
        self,
        query: str,
        results: list[MemorySearchResult],
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Return reordered or rescored search results."""


@runtime_checkable
class MemoryGraphRecallProvider(Protocol):
    """Contract for optional post-ranking graph recall providers."""

    async def expand(
        self,
        query: str,
        results: list[MemorySearchResult],
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Return graph-enriched search results."""
