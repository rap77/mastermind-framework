"""SQL-backed first-party memory store."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TypeAlias, cast
from uuid import uuid4

from sqlalchemy import JSON, DateTime, String, Table, Text, func, or_, select
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.project_state.database.base import Base
from mastermind_cli.project_state.database.session import (
    get_engine,
    get_session_factory,
)

from .models import MemoryItem, MemorySearchResult

JsonValue: TypeAlias = dict[str, Any] | list[Any] | str | int | float | bool | None


class MemoryItemRecord(Base):
    """Relational record for canonical memory items."""

    __tablename__ = "mm_memory_items"

    memory_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    memory_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    project_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    brain_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    niche: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    visibility: Mapped[str] = mapped_column(String(64), nullable=False)
    source_kind: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags_json: Mapped[list[str]] = mapped_column("tags", JSON, default=list)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class MemoryPreferenceRecord(Base):
    """Dedicated relational record for operational preferences."""

    __tablename__ = "mm_memory_preferences"

    preference_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    project_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    scope: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value_json: Mapped[JsonValue] = mapped_column("value", JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class MemorySessionRecord(Base):
    """Dedicated relational record for persisted session continuity summaries."""

    __tablename__ = "mm_memory_sessions"

    session_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    project_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class PostgresMemoryStore:
    """First-party memory store backed by the framework SQL database."""

    def __init__(self, database_url: str) -> None:
        """Create a store bound to the provided database URL."""
        self._database_url = database_url
        self._session_factory = get_session_factory(database_url)
        self._schema_ready = False

    async def save_item(self, item: MemoryItem) -> MemoryItem:
        """Persist a memory item and return the stored canonical shape."""
        self._ensure_schema()
        now = datetime.now(timezone.utc)
        memory_id = item.memory_id or str(uuid4())

        with self._session_factory() as session:
            record = session.get(MemoryItemRecord, memory_id)
            if record is None:
                record = MemoryItemRecord(
                    memory_id=memory_id,
                    memory_type=item.memory_type,
                    title=item.title,
                    content=item.content,
                    project_id=item.project_id,
                    brain_id=item.brain_id,
                    niche=item.niche,
                    visibility=item.visibility,
                    source_kind=item.source_kind,
                    source_ref=item.source_ref,
                    tags_json=list(item.tags),
                    metadata_json=dict(item.metadata),
                    created_at=item.created_at,
                    updated_at=now,
                )
                session.add(record)
            else:
                record.memory_type = item.memory_type
                record.title = item.title
                record.content = item.content
                record.project_id = item.project_id
                record.brain_id = item.brain_id
                record.niche = item.niche
                record.visibility = item.visibility
                record.source_kind = item.source_kind
                record.source_ref = item.source_ref
                record.tags_json = list(item.tags)
                record.metadata_json = dict(item.metadata)
                record.updated_at = now
            session.commit()
            session.refresh(record)

        return self._to_memory_item(record)

    async def get_item(self, memory_id: str) -> MemoryItem | None:
        """Fetch a single memory item by identifier."""
        self._ensure_schema()
        with self._session_factory() as session:
            record = session.get(MemoryItemRecord, memory_id)
            return self._to_memory_item(record) if record is not None else None

    async def search(
        self,
        query: str,
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Run a simple lexical search over memory items with optional scoping."""
        self._ensure_schema()
        normalized_query = query.strip()
        with self._session_factory() as session:
            statement = select(MemoryItemRecord)
            statement = self._apply_scope(statement, scope)

            if normalized_query:
                like_query = f"%{normalized_query.lower()}%"
                statement = statement.where(
                    or_(
                        func.lower(MemoryItemRecord.title).like(like_query),
                        func.lower(MemoryItemRecord.content).like(like_query),
                    )
                )

            rows = list(
                session.scalars(
                    statement.order_by(MemoryItemRecord.created_at.desc()).limit(limit)
                )
            )

        return [self._to_search_result(row, normalized_query) for row in rows]

    async def list_recent(
        self,
        project_id: str,
        limit: int = 10,
    ) -> list[MemoryItem]:
        """List recent memory items for a project."""
        self._ensure_schema()
        with self._session_factory() as session:
            rows = list(
                session.scalars(
                    select(MemoryItemRecord)
                    .where(MemoryItemRecord.project_id == project_id)
                    .order_by(MemoryItemRecord.created_at.desc())
                    .limit(limit)
                )
            )
        return [self._to_memory_item(row) for row in rows]

    async def save_session_summary(
        self,
        session_id: str,
        summary: str,
        project_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        """Persist a session summary into the dedicated continuity table."""
        self._ensure_schema()
        with self._session_factory() as session:
            record = session.get(MemorySessionRecord, session_id)
            if record is None:
                session.add(
                    MemorySessionRecord(
                        session_id=session_id,
                        project_id=project_id,
                        summary=summary,
                        metadata_json=dict(metadata or {}),
                    )
                )
            else:
                record.project_id = project_id
                record.summary = summary
                record.metadata_json = dict(metadata or {})
            session.commit()

    async def save_preference(
        self,
        key: str,
        value: object,
        scope: str,
        project_id: str | None = None,
    ) -> None:
        """Persist an operational preference outside the generic memory table."""
        self._ensure_schema()
        with self._session_factory() as session:
            existing = session.scalar(
                select(MemoryPreferenceRecord).where(
                    MemoryPreferenceRecord.key == key,
                    MemoryPreferenceRecord.scope == scope,
                    MemoryPreferenceRecord.project_id == project_id,
                )
            )
            if existing is None:
                session.add(
                    MemoryPreferenceRecord(
                        preference_id=str(uuid4()),
                        project_id=project_id,
                        scope=scope,
                        key=key,
                        value_json=self._normalize_json_value(value),
                    )
                )
            else:
                existing.value_json = self._normalize_json_value(value)
                existing.updated_at = datetime.now(timezone.utc)
            session.commit()

    def _ensure_schema(self) -> None:
        """Create the memory tables once for the bound database."""
        if self._schema_ready:
            return
        Base.metadata.create_all(
            bind=get_engine(self._database_url),
            tables=[
                cast(Table, MemoryItemRecord.__table__),
                cast(Table, MemoryPreferenceRecord.__table__),
                cast(Table, MemorySessionRecord.__table__),
            ],
        )
        self._schema_ready = True

    def _apply_scope(self, statement: Any, scope: dict[str, str | None] | None) -> Any:
        """Apply supported filters to a memory search statement."""
        if not scope:
            return statement
        if scope.get("project_id"):
            statement = statement.where(
                MemoryItemRecord.project_id == scope["project_id"]
            )
        if scope.get("brain_id"):
            statement = statement.where(MemoryItemRecord.brain_id == scope["brain_id"])
        if scope.get("niche"):
            statement = statement.where(MemoryItemRecord.niche == scope["niche"])
        if scope.get("memory_type"):
            statement = statement.where(
                MemoryItemRecord.memory_type == scope["memory_type"]
            )
        return statement

    def _to_memory_item(self, record: MemoryItemRecord) -> MemoryItem:
        """Map a relational record into the canonical memory model."""
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
            created_at=self._ensure_utc(record.created_at),
            updated_at=self._ensure_utc(record.updated_at),
        )

    def _to_search_result(
        self,
        record: MemoryItemRecord,
        query: str,
    ) -> MemorySearchResult:
        """Build a basic lexical search result from a relational record."""
        lowered_query = query.lower()
        haystack = f"{record.title} {record.content}".lower()
        score = 1.0 if lowered_query and lowered_query in haystack else 0.5
        snippet = record.content[:240]
        why_matched = "lexical:title_or_content" if lowered_query else "recent"
        return MemorySearchResult(
            memory_id=record.memory_id,
            title=record.title,
            snippet=snippet,
            score=score,
            memory_type=record.memory_type,
            project_id=record.project_id,
            brain_id=record.brain_id,
            why_matched=why_matched,
            source_ref=record.source_ref,
        )

    def _ensure_utc(self, value: datetime) -> datetime:
        """Return a timezone-aware UTC datetime for persisted timestamps."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _normalize_json_value(self, value: object) -> JsonValue:
        """Normalize arbitrary preference payloads into JSON-compatible values."""
        if isinstance(value, dict):
            return dict(value)
        if isinstance(value, list):
            return list(value)
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)


__all__ = [
    "MemoryItemRecord",
    "MemoryPreferenceRecord",
    "MemorySessionRecord",
    "PostgresMemoryStore",
]
