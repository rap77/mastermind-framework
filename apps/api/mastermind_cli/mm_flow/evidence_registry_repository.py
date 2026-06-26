"""Async PostgreSQL repository for the evidence registry snapshot."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EvidenceRegistrySyncCounts:
    """Counts returned after syncing a registry snapshot to PostgreSQL."""

    sources: int
    versions: int
    deltas: int


class EvidenceRegistryRepository:
    """Persist evidence registry snapshots in PostgreSQL."""

    def __init__(self, conn: Any) -> None:
        """Initialize the repository with an open asyncpg connection."""
        self._conn = conn

    async def ensure_schema(self) -> None:
        """Create the evidence registry tables if they do not exist."""
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_registry_sources (
                registry_key    TEXT NOT NULL,
                source_id       TEXT NOT NULL,
                source_type     TEXT NOT NULL,
                name            TEXT NOT NULL,
                uri             TEXT NOT NULL,
                created_at_utc  TIMESTAMPTZ NOT NULL,
                updated_at_utc  TIMESTAMPTZ NOT NULL,
                PRIMARY KEY (registry_key, source_id)
            )
        """)
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_registry_versions (
                registry_key            TEXT NOT NULL,
                id                      TEXT NOT NULL,
                source_id               TEXT,
                source_type             TEXT NOT NULL,
                name                    TEXT NOT NULL,
                uri                     TEXT NOT NULL,
                version_ref             TEXT NOT NULL,
                version_hash            TEXT NOT NULL,
                summary                 TEXT NOT NULL,
                state                   TEXT NOT NULL,
                confidence              DOUBLE PRECISION NOT NULL,
                coverage                DOUBLE PRECISION NOT NULL,
                critical_gaps           INTEGER NOT NULL,
                important_gaps          INTEGER NOT NULL,
                optional_gaps           INTEGER NOT NULL,
                contradictions          INTEGER NOT NULL,
                user_answers_complete   BOOLEAN NOT NULL,
                created_at_utc          TIMESTAMPTZ NOT NULL,
                updated_at_utc          TIMESTAMPTZ NOT NULL,
                PRIMARY KEY (registry_key, id)
            )
        """)
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_registry_deltas (
                registry_key        TEXT NOT NULL,
                id                  TEXT NOT NULL,
                from_version_id     TEXT NOT NULL,
                to_version_id       TEXT NOT NULL,
                delta_type          TEXT NOT NULL,
                summary             TEXT NOT NULL,
                impact              TEXT NOT NULL,
                risk                TEXT NOT NULL,
                decision            TEXT NOT NULL,
                source_id           TEXT,
                created_at_utc      TIMESTAMPTZ NOT NULL,
                PRIMARY KEY (registry_key, id)
            )
        """)
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_evidence_versions_registry_source "
            "ON evidence_registry_versions(registry_key, source_id)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_evidence_deltas_registry_source "
            "ON evidence_registry_deltas(registry_key, source_id)"
        )

    async def sync_snapshot(
        self,
        *,
        registry_key: str,
        sources: list[Mapping[str, Any]],
        versions: list[Mapping[str, Any]],
        deltas: list[Mapping[str, Any]],
    ) -> EvidenceRegistrySyncCounts:
        """Upsert a registry snapshot into PostgreSQL."""
        await self.ensure_schema()
        async with self._conn.transaction():
            source_count = 0
            for entry in sources:
                source_id = self._require_text(entry.get("source_id"), "source_id")
                await self._conn.execute(
                    """
                    INSERT INTO evidence_registry_sources (
                        registry_key, source_id, source_type, name, uri,
                        created_at_utc, updated_at_utc
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (registry_key, source_id) DO UPDATE SET
                        registry_key = EXCLUDED.registry_key,
                        source_type = EXCLUDED.source_type,
                        name = EXCLUDED.name,
                        uri = EXCLUDED.uri,
                        updated_at_utc = EXCLUDED.updated_at_utc
                    """,
                    registry_key,
                    source_id,
                    str(entry.get("source_type") or "doc"),
                    str(entry.get("name") or ""),
                    str(entry.get("uri") or ""),
                    entry.get("created_at_utc"),
                    entry.get("updated_at_utc"),
                )
                source_count += 1

            version_count = 0
            for entry in versions:
                version_id = self._require_text(entry.get("id"), "id")
                await self._conn.execute(
                    """
                    INSERT INTO evidence_registry_versions (
                        registry_key, id, source_id, source_type, name, uri,
                        version_ref, version_hash, summary, state,
                        confidence, coverage, critical_gaps, important_gaps,
                        optional_gaps, contradictions, user_answers_complete,
                        created_at_utc, updated_at_utc
                    )
                    VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                        $11, $12, $13, $14, $15, $16, $17, $18, $19
                    )
                    ON CONFLICT (registry_key, id) DO UPDATE SET
                        registry_key = EXCLUDED.registry_key,
                        source_id = EXCLUDED.source_id,
                        source_type = EXCLUDED.source_type,
                        name = EXCLUDED.name,
                        uri = EXCLUDED.uri,
                        version_ref = EXCLUDED.version_ref,
                        version_hash = EXCLUDED.version_hash,
                        summary = EXCLUDED.summary,
                        state = EXCLUDED.state,
                        confidence = EXCLUDED.confidence,
                        coverage = EXCLUDED.coverage,
                        critical_gaps = EXCLUDED.critical_gaps,
                        important_gaps = EXCLUDED.important_gaps,
                        optional_gaps = EXCLUDED.optional_gaps,
                        contradictions = EXCLUDED.contradictions,
                        user_answers_complete = EXCLUDED.user_answers_complete,
                        updated_at_utc = EXCLUDED.updated_at_utc
                    """,
                    registry_key,
                    version_id,
                    entry.get("source_id"),
                    str(entry.get("source_type") or "doc"),
                    str(entry.get("name") or ""),
                    str(entry.get("uri") or ""),
                    str(entry.get("version_ref") or ""),
                    str(entry.get("version_hash") or ""),
                    str(entry.get("summary") or ""),
                    str(entry.get("state") or "current"),
                    float(entry.get("confidence") or 0.0),
                    float(entry.get("coverage") or 0.0),
                    int(entry.get("critical_gaps") or 0),
                    int(entry.get("important_gaps") or 0),
                    int(entry.get("optional_gaps") or 0),
                    int(entry.get("contradictions") or 0),
                    bool(entry.get("user_answers_complete")),
                    entry.get("created_at_utc"),
                    entry.get("updated_at_utc"),
                )
                version_count += 1

            delta_count = 0
            for entry in deltas:
                delta_id = self._require_text(entry.get("id"), "delta id")
                from_version_id = self._require_text(
                    entry.get("from_version_id"), "from_version_id"
                )
                to_version_id = self._require_text(
                    entry.get("to_version_id"), "to_version_id"
                )
                await self._conn.execute(
                    """
                    INSERT INTO evidence_registry_deltas (
                        registry_key, id, from_version_id, to_version_id,
                        delta_type, summary, impact, risk, decision,
                        source_id, created_at_utc
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (registry_key, id) DO UPDATE SET
                        registry_key = EXCLUDED.registry_key,
                        from_version_id = EXCLUDED.from_version_id,
                        to_version_id = EXCLUDED.to_version_id,
                        delta_type = EXCLUDED.delta_type,
                        summary = EXCLUDED.summary,
                        impact = EXCLUDED.impact,
                        risk = EXCLUDED.risk,
                        decision = EXCLUDED.decision,
                        source_id = EXCLUDED.source_id,
                        created_at_utc = EXCLUDED.created_at_utc
                    """,
                    registry_key,
                    delta_id,
                    from_version_id,
                    to_version_id,
                    str(entry.get("delta_type") or "decision"),
                    str(entry.get("summary") or ""),
                    str(entry.get("impact") or "medium"),
                    str(entry.get("risk") or "medium"),
                    str(entry.get("decision") or "adapted"),
                    entry.get("source_id"),
                    entry.get("created_at_utc"),
                )
                delta_count += 1

        return EvidenceRegistrySyncCounts(
            sources=source_count,
            versions=version_count,
            deltas=delta_count,
        )

    def _require_text(self, value: Any, field_name: str) -> str:
        """Require a non-empty text value for a registry field."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Registry snapshot is missing required field: {field_name}"
            )
        return value.strip()
