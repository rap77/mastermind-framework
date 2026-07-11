"""Application service for the first-party memory layer."""

from __future__ import annotations

from inspect import ismethod
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, cast

from .exceptions import MemorySnapshotError
from .contracts import MemoryStore
from .models import (
    CheckpointRecord,
    ContextSnapshot,
    DecisionRecord,
    MemoryItem,
    MemorySearchResult,
    RunSummary,
)


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

    async def save_checkpoint(self, checkpoint: CheckpointRecord) -> CheckpointRecord:
        """Persist a checkpoint record through the canonical memory store."""
        return await self.record_checkpoint(
            checkpoint_id=checkpoint.checkpoint_id,
            project_id=checkpoint.project_id,
            task_id=checkpoint.task_id,
            run_id=checkpoint.run_id,
            context_summary=checkpoint.context_summary,
            resume_state=checkpoint.resume_state,
            next_step_summary=checkpoint.next_step_summary,
        )

    async def save_decision(self, decision: DecisionRecord) -> DecisionRecord:
        """Persist a decision record through the canonical memory store."""
        return await self.record_decision(
            decision_id=decision.decision_id,
            project_id=decision.project_id,
            task_id=decision.task_id,
            title=decision.title,
            status=decision.status,
            rationale_markdown=decision.rationale_markdown,
            metadata=decision.metadata,
        )

    async def save_run_summary(self, run_summary: RunSummary) -> RunSummary:
        """Persist a run summary through the canonical memory store."""
        await self.record_session_summary(
            session_id=run_summary.run_id,
            summary=run_summary.summary,
            project_id=run_summary.project_id,
            metadata=run_summary.metadata,
        )
        return run_summary

    async def record_checkpoint(
        self,
        *,
        checkpoint_id: str,
        project_id: str,
        next_step_summary: str,
        context_summary: dict[str, object] | None = None,
        resume_state: dict[str, object] | None = None,
        task_id: str | None = None,
        run_id: str | None = None,
        visibility: str = "project",
    ) -> CheckpointRecord:
        """Persist a resumable checkpoint as canonical memory."""
        item = await self.record_learning(
            title=f"Checkpoint: {checkpoint_id}",
            content=next_step_summary,
            project_id=project_id,
            memory_type="checkpoint",
            visibility=visibility,
            source_kind="checkpoint",
            source_ref=run_id or checkpoint_id,
            tags=["checkpoint"],
            metadata={
                "checkpoint_id": checkpoint_id,
                "task_id": task_id,
                "run_id": run_id,
                "context_summary": context_summary or {},
                "resume_state": resume_state or {},
                "next_step_summary": next_step_summary,
            },
        )
        checkpoint = self._to_checkpoint_record(
            item, fallback_checkpoint_id=checkpoint_id
        )
        checkpoint_writer = cast(
            Callable[[CheckpointRecord], Awaitable[CheckpointRecord]] | None,
            self._checkpoint_method("save_checkpoint"),
        )
        if checkpoint_writer is not None:
            return await checkpoint_writer(checkpoint)
        return checkpoint

    async def record_decision(
        self,
        *,
        decision_id: str,
        project_id: str,
        title: str,
        status: str,
        rationale_markdown: str,
        task_id: str | None = None,
        metadata: dict[str, object] | None = None,
        visibility: str = "project",
    ) -> DecisionRecord:
        """Persist a durable decision as canonical memory."""
        item = await self.record_learning(
            title=title,
            content=rationale_markdown,
            project_id=project_id,
            memory_type="decision",
            visibility=visibility,
            source_kind="decision",
            source_ref=decision_id,
            tags=["decision", status],
            metadata={
                "decision_id": decision_id,
                "task_id": task_id,
                "status": status,
                **(metadata or {}),
            },
        )
        return self._to_decision_record(item, fallback_decision_id=decision_id)

    async def build_context_snapshot(
        self,
        project_id: str,
        task_id: str | None = None,
        *,
        limit: int = 10,
    ) -> ContextSnapshot:
        """Assemble a compact resume snapshot from recent project memory."""
        try:
            checkpoints = await self._load_recent_checkpoints(
                project_id,
                task_id,
                limit=limit,
            )
            recent_items = await self._store.list_recent(project_id, limit=limit * 5)
            decisions = [
                self._to_decision_record(
                    item, fallback_decision_id=item.memory_id or ""
                )
                for item in recent_items
                if item.memory_type == "decision"
                and self._matches_task_scope(item, task_id)
            ]
            run_summaries = [
                self._to_run_summary(item)
                for item in recent_items
                if item.memory_type == "session_summary"
                and self._matches_task_scope(item, task_id)
            ]
            checkpoints.sort(key=lambda record: record.created_at, reverse=True)
            decisions.sort(key=lambda record: record.created_at, reverse=True)
            run_summaries.sort(key=lambda record: record.created_at, reverse=True)
            checkpoints = checkpoints[:limit]
            decisions = decisions[:limit]
            run_summaries = run_summaries[:limit]
            latest_checkpoint = checkpoints[0] if checkpoints else None
            latest_decision = decisions[0] if decisions else None
            latest_summary = run_summaries[0] if run_summaries else None
            summary = (
                latest_checkpoint.next_step_summary
                if latest_checkpoint is not None
                else latest_decision.rationale_markdown
                if latest_decision is not None
                else latest_summary.summary
                if latest_summary is not None
                else "No stored context yet."
            )
            open_gaps = []
            if latest_checkpoint is None:
                open_gaps.append("No checkpoint available")
            if latest_decision is None:
                open_gaps.append("No decision available")
            return ContextSnapshot(
                project_id=project_id,
                task_id=task_id,
                checkpoints=checkpoints,
                decisions=decisions,
                run_summaries=run_summaries,
                summary=summary,
                open_gaps=open_gaps,
                applied_scopes={"project_id": project_id, "task_id": task_id},
            )
        except MemorySnapshotError:
            raise
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as exc:
            raise MemorySnapshotError(
                f"Failed to build context snapshot for project_id={project_id}: {exc}"
            ) from exc

    async def load_latest_checkpoint(
        self,
        project_id: str,
        task_id: str | None = None,
    ) -> CheckpointRecord | None:
        """Load the latest checkpoint when the backend exposes the checkpoint seam."""
        checkpoint_reader = cast(
            Callable[[str, str | None], Awaitable[CheckpointRecord | None]] | None,
            self._checkpoint_method("get_latest_checkpoint"),
        )
        if checkpoint_reader is None:
            return None
        return await checkpoint_reader(project_id, task_id)

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

    def _matches_task_scope(self, item: MemoryItem, task_id: str | None) -> bool:
        """Return whether a memory item belongs to the requested task scope."""
        if task_id is None:
            return True
        return str(item.metadata.get("task_id") or "") == task_id

    async def _load_recent_checkpoints(
        self,
        project_id: str,
        task_id: str | None,
        *,
        limit: int,
    ) -> list[CheckpointRecord]:
        """Load checkpoints from a dedicated backend when available."""
        checkpoint_lister = cast(
            Callable[[str, int], Awaitable[list[CheckpointRecord]]] | None,
            self._checkpoint_method("list_recent_checkpoints"),
        )
        if checkpoint_lister is not None:
            checkpoints = await checkpoint_lister(project_id, limit)
            return [
                checkpoint
                for checkpoint in checkpoints
                if task_id is None or checkpoint.task_id == task_id
            ]

        recent_items = await self._store.list_recent(project_id, limit=limit * 5)
        checkpoints = [
            self._to_checkpoint_record(
                item, fallback_checkpoint_id=item.memory_id or ""
            )
            for item in recent_items
            if item.memory_type == "checkpoint"
            and self._matches_task_scope(item, task_id)
        ]
        checkpoints.sort(key=lambda record: record.created_at, reverse=True)
        return checkpoints[:limit]

    def _to_checkpoint_record(
        self,
        item: MemoryItem,
        *,
        fallback_checkpoint_id: str,
    ) -> CheckpointRecord:
        """Map a memory item into a checkpoint record."""
        metadata = dict(item.metadata)
        return CheckpointRecord(
            checkpoint_id=str(metadata.get("checkpoint_id") or fallback_checkpoint_id),
            project_id=item.project_id or "",
            task_id=self._optional_metadata_string(metadata.get("task_id")),
            run_id=self._optional_metadata_string(metadata.get("run_id")),
            context_summary=self._mapping_value(metadata.get("context_summary")),
            resume_state=self._mapping_value(metadata.get("resume_state")),
            next_step_summary=str(
                metadata.get("next_step_summary") or item.content or item.title
            ),
            created_at=item.created_at,
        )

    def _to_decision_record(
        self,
        item: MemoryItem,
        *,
        fallback_decision_id: str,
    ) -> DecisionRecord:
        """Map a memory item into a decision record."""
        metadata = dict(item.metadata)
        return DecisionRecord(
            decision_id=str(metadata.get("decision_id") or fallback_decision_id),
            project_id=item.project_id or "",
            task_id=self._optional_metadata_string(metadata.get("task_id")),
            title=item.title,
            status=str(metadata.get("status") or item.memory_type),
            rationale_markdown=item.content,
            metadata=metadata,
            created_at=item.created_at,
        )

    def _to_run_summary(self, item: MemoryItem) -> RunSummary:
        """Map a memory item into a run summary record."""
        metadata = dict(item.metadata)
        return RunSummary(
            run_id=str(
                metadata.get("run_id") or item.source_ref or item.memory_id or ""
            ),
            project_id=item.project_id or "",
            summary=item.content,
            metadata=metadata,
            created_at=item.created_at,
        )

    def _optional_metadata_string(self, value: object) -> str | None:
        """Normalize optional metadata values into strings when present."""
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _mapping_value(self, value: object) -> dict[str, object]:
        """Return a dict copy when metadata contains a mapping-like value."""
        if isinstance(value, dict):
            return dict(value)
        return {}

    def _checkpoint_method(self, name: str) -> Any | None:
        """Return a bound checkpoint method when the backend exposes one."""
        method = getattr(self._store, name, None)
        if method is None or not ismethod(method):
            return None
        return method
