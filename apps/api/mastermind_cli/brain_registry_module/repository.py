"""
BrainRegistryRepository — asyncpg-based data access for brain_registry.

Provides get_all(), get_by_id(), and get_matching(context) for reading
brain configurations from the PostgreSQL brain_registry table.

Design decisions:
  - Accepts asyncpg.Connection as parameter (no global state, C1 requirement).
  - All queries are SELECT-only (reads only); mutations are handled by migrate/seed.
  - get_matching() uses a simple contains-any GIN index scan on trigger_conditions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import asyncpg

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class BrainRecord:
    """Single row from brain_registry.

    Attributes:
        brain_id: Integer brain identifier (1-7).
        name: Human-readable brain name.
        model_quality: Model ID for quality tier.
        model_balanced: Model ID for balanced tier.
        model_budget: Model ID for budget tier.
        capabilities: List of capability strings.
        trigger_conditions: List of trigger condition strings.
        enabled: Whether this brain is active.
    """

    brain_id: int
    name: str
    model_quality: str
    model_balanced: str
    model_budget: str
    capabilities: list[str]
    trigger_conditions: list[str]
    enabled: bool

    @classmethod
    def from_row(cls, row: asyncpg.Record) -> "BrainRecord":
        """Build a BrainRecord from an asyncpg Record.

        Args:
            row: asyncpg Record from brain_registry query.

        Returns:
            BrainRecord populated from the row fields.
        """
        return cls(
            brain_id=row["brain_id"],
            name=row["name"],
            model_quality=row["model_quality"],
            model_balanced=row["model_balanced"],
            model_budget=row["model_budget"],
            capabilities=list(row["capabilities"] or []),
            trigger_conditions=list(row["trigger_conditions"] or []),
            enabled=row["enabled"],
        )


class BrainRegistryRepository:
    """Data access object for the brain_registry table.

    Accepts an asyncpg.Connection at construction time — the caller
    owns the connection lifecycle (open/close).

    Args:
        conn: Open asyncpg connection. Must remain open for the duration
              of all method calls. The caller is responsible for closing it.

    Example:
        conn = await asyncpg.connect(database_url)
        try:
            repo = BrainRegistryRepository(conn)
            brains = await repo.get_all()
        finally:
            await conn.close()
    """

    _SELECT_ALL_COLS = (
        "brain_id, name, model_quality, model_balanced, model_budget, "
        "capabilities, trigger_conditions, enabled"
    )

    def __init__(self, conn: asyncpg.Connection) -> None:
        """Initialise with an open asyncpg connection.

        Args:
            conn: Open asyncpg connection (caller owns lifecycle).
        """
        self._conn = conn

    async def get_all(self) -> list[BrainRecord]:
        """Return all brain rows ordered by brain_id.

        Returns:
            List of BrainRecord instances, one per row in brain_registry.
        """
        rows = await self._conn.fetch(
            f"SELECT {self._SELECT_ALL_COLS} "
            "FROM brain_registry "
            "ORDER BY brain_id ASC"
        )
        return [BrainRecord.from_row(r) for r in rows]

    async def get_by_id(self, brain_id: int) -> BrainRecord | None:
        """Return a single brain by its integer ID.

        Args:
            brain_id: Integer brain identifier (1-7).

        Returns:
            BrainRecord if found, None otherwise.
        """
        row = await self._conn.fetchrow(
            f"SELECT {self._SELECT_ALL_COLS} "
            "FROM brain_registry "
            "WHERE brain_id = $1",
            brain_id,
        )
        if row is None:
            return None
        return BrainRecord.from_row(row)

    async def get_matching(self, context: str) -> list[BrainRecord]:
        """Return enabled brains whose trigger_conditions overlap with the context.

        Performs a case-insensitive substring match: returns brains where at
        least one trigger condition appears as a substring of ``context``.

        Args:
            context: Free-form text describing the current execution context
                     (e.g. a moment name, task description, or user brief).

        Returns:
            List of enabled BrainRecord instances matching the context,
            ordered by brain_id. Returns empty list if no match.
        """
        context_lower = context.lower()
        # Use GIN-compatible array operator: any trigger_conditions element
        # that is a substring of the context string.
        # PostgreSQL: WHERE enabled = TRUE AND EXISTS (
        #   SELECT 1 FROM unnest(trigger_conditions) tc WHERE $1 ILIKE '%' || tc || '%'
        # )
        rows = await self._conn.fetch(
            f"SELECT {self._SELECT_ALL_COLS} "
            "FROM brain_registry "
            "WHERE enabled = TRUE "
            "  AND EXISTS ("
            "    SELECT 1 FROM unnest(trigger_conditions) AS tc "
            "    WHERE $1 ILIKE '%' || tc || '%'"
            "  ) "
            "ORDER BY brain_id ASC",
            context_lower,
        )
        return [BrainRecord.from_row(r) for r in rows]

    async def get_enabled(self) -> list[BrainRecord]:
        """Return all enabled brain rows ordered by brain_id.

        Returns:
            List of BrainRecord instances where enabled = TRUE.
        """
        rows = await self._conn.fetch(
            f"SELECT {self._SELECT_ALL_COLS} "
            "FROM brain_registry "
            "WHERE enabled = TRUE "
            "ORDER BY brain_id ASC"
        )
        return [BrainRecord.from_row(r) for r in rows]
