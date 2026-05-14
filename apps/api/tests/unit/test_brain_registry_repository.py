"""
Unit tests for BrainRegistryRepository (C1.08) and DynamicDispatchEngine
integration with BrainRegistryRepository (C1.09).

All tests use mocked asyncpg connections — no real PostgreSQL required.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import asyncpg
import pytest

from mastermind_cli.brain_registry_module.repository import (
    BrainRecord,
    BrainRegistryRepository,
)
from mastermind_cli.mm_flow.dispatch_engine import (
    DispatchResult,
    DynamicDispatchEngine,
)


# ---------------------------------------------------------------------------
# Helpers: build fake asyncpg Records
# ---------------------------------------------------------------------------


def _make_brain_registry_row(
    brain_id: int,
    name: str = "Test Brain",
    model_quality: str = "claude-opus-4-6",
    model_balanced: str = "claude-sonnet-4-6",
    model_budget: str = "claude-haiku-4-5",
    capabilities: list[str] | None = None,
    trigger_conditions: list[str] | None = None,
    enabled: bool = True,
) -> MagicMock:
    """Build a fake asyncpg Record-like object for brain_registry rows.

    Args:
        brain_id: Integer brain identifier (1-7).
        name: Human-readable brain name.
        model_quality: Model for quality tier.
        model_balanced: Model for balanced tier.
        model_budget: Model for budget tier.
        capabilities: List of capability strings.
        trigger_conditions: List of trigger condition strings.
        enabled: Whether brain is active.

    Returns:
        MagicMock with dict-style key access for all brain_registry columns.
    """
    caps = capabilities or ["test-capability"]
    triggers = trigger_conditions or ["test-trigger"]
    row: MagicMock = MagicMock(spec=asyncpg.Record)
    data = {
        "brain_id": brain_id,
        "name": name,
        "model_quality": model_quality,
        "model_balanced": model_balanced,
        "model_budget": model_budget,
        "capabilities": caps,
        "trigger_conditions": triggers,
        "enabled": enabled,
    }
    row.__getitem__ = MagicMock(side_effect=lambda k: data[k])
    return row


def _make_7_brain_rows() -> list[MagicMock]:
    """Return 7 mock brain_registry rows (IDs 1-7)."""
    brain_names = [
        "Product Strategy",
        "UX Research",
        "UI Design",
        "Frontend",
        "Backend",
        "QA/DevOps",
        "Growth/Data",
    ]
    return [
        _make_brain_registry_row(brain_id=i, name=brain_names[i - 1])
        for i in range(1, 8)
    ]


def _make_mock_conn(rows: list[MagicMock]) -> AsyncMock:
    """Build a mock asyncpg connection returning the given rows on fetch/fetchrow.

    Args:
        rows: Rows to return from fetch(). fetchrow() returns rows[0] or None.

    Returns:
        AsyncMock with fetch, fetchrow, and close methods.
    """
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=rows)
    conn.fetchrow = AsyncMock(return_value=rows[0] if rows else None)
    conn.close = AsyncMock()
    return conn


# ---------------------------------------------------------------------------
# C1.08: BrainRegistryRepository.get_all() returns 7 rows
# ---------------------------------------------------------------------------


class TestBrainRegistryRepositoryGetAll:
    """C1.08: get_all() returns all 7 brain rows from brain_registry."""

    @pytest.mark.asyncio
    async def test_get_all_returns_7_records(self) -> None:
        """get_all() returns exactly 7 BrainRecord instances when DB has 7 rows."""
        rows = _make_7_brain_rows()
        conn = _make_mock_conn(rows)

        repo = BrainRegistryRepository(conn)
        result = await repo.get_all()

        assert len(result) == 7

    @pytest.mark.asyncio
    async def test_get_all_returns_brain_records(self) -> None:
        """get_all() returns a list of BrainRecord dataclass instances."""
        rows = _make_7_brain_rows()
        conn = _make_mock_conn(rows)

        repo = BrainRegistryRepository(conn)
        result = await repo.get_all()

        assert all(isinstance(r, BrainRecord) for r in result)

    @pytest.mark.asyncio
    async def test_get_all_brain_ids_are_1_to_7(self) -> None:
        """get_all() returns brains with IDs 1 through 7."""
        rows = _make_7_brain_rows()
        conn = _make_mock_conn(rows)

        repo = BrainRegistryRepository(conn)
        result = await repo.get_all()

        assert [r.brain_id for r in result] == list(range(1, 8))

    @pytest.mark.asyncio
    async def test_get_all_brain_names_match(self) -> None:
        """get_all() preserves the name from each row."""
        rows = _make_7_brain_rows()
        conn = _make_mock_conn(rows)

        repo = BrainRegistryRepository(conn)
        result = await repo.get_all()

        expected_names = [
            "Product Strategy",
            "UX Research",
            "UI Design",
            "Frontend",
            "Backend",
            "QA/DevOps",
            "Growth/Data",
        ]
        assert [r.name for r in result] == expected_names

    @pytest.mark.asyncio
    async def test_get_all_calls_fetch_with_correct_query(self) -> None:
        """get_all() issues a SELECT with ORDER BY brain_id ASC."""
        rows = _make_7_brain_rows()
        conn = _make_mock_conn(rows)

        repo = BrainRegistryRepository(conn)
        await repo.get_all()

        conn.fetch.assert_called_once()
        query_arg = conn.fetch.call_args.args[0]
        assert "brain_registry" in query_arg
        assert "brain_id ASC" in query_arg

    @pytest.mark.asyncio
    async def test_get_all_empty_db_returns_empty_list(self) -> None:
        """get_all() returns [] when brain_registry has no rows."""
        conn = _make_mock_conn([])

        repo = BrainRegistryRepository(conn)
        result = await repo.get_all()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_brain_record_has_capabilities(self) -> None:
        """get_all() populates capabilities list from each row."""
        row = _make_brain_registry_row(1, capabilities=["product-discovery", "roadmap"])
        conn = _make_mock_conn([row])

        repo = BrainRegistryRepository(conn)
        result = await repo.get_all()

        assert result[0].capabilities == ["product-discovery", "roadmap"]

    @pytest.mark.asyncio
    async def test_get_all_brain_record_has_trigger_conditions(self) -> None:
        """get_all() populates trigger_conditions list from each row."""
        row = _make_brain_registry_row(
            1, trigger_conditions=["should we build", "product decision"]
        )
        conn = _make_mock_conn([row])

        repo = BrainRegistryRepository(conn)
        result = await repo.get_all()

        assert result[0].trigger_conditions == ["should we build", "product decision"]


class TestBrainRegistryRepositoryGetById:
    """get_by_id() returns a single brain or None."""

    @pytest.mark.asyncio
    async def test_get_by_id_returns_brain_record(self) -> None:
        """get_by_id(1) returns BrainRecord with brain_id=1."""
        row = _make_brain_registry_row(1, name="Product Strategy")
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value=row)
        conn.close = AsyncMock()

        repo = BrainRegistryRepository(conn)
        result = await repo.get_by_id(1)

        assert result is not None
        assert result.brain_id == 1
        assert result.name == "Product Strategy"

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_not_found(self) -> None:
        """get_by_id(999) returns None when row doesn't exist."""
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value=None)
        conn.close = AsyncMock()

        repo = BrainRegistryRepository(conn)
        result = await repo.get_by_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_passes_brain_id_as_param(self) -> None:
        """get_by_id() passes brain_id as $1 parameter to the query."""
        row = _make_brain_registry_row(7)
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value=row)

        repo = BrainRegistryRepository(conn)
        await repo.get_by_id(7)

        conn.fetchrow.assert_called_once()
        assert conn.fetchrow.call_args.args[1] == 7


class TestBrainRegistryRepositoryGetMatching:
    """get_matching() returns brains matching the context string."""

    @pytest.mark.asyncio
    async def test_get_matching_returns_list_of_brain_records(self) -> None:
        """get_matching() returns a list of BrainRecord instances."""
        rows = [_make_brain_registry_row(1), _make_brain_registry_row(3)]
        conn = _make_mock_conn(rows)

        repo = BrainRegistryRepository(conn)
        result = await repo.get_matching("product decision")

        assert all(isinstance(r, BrainRecord) for r in result)

    @pytest.mark.asyncio
    async def test_get_matching_returns_empty_when_no_match(self) -> None:
        """get_matching() returns [] when no brains match."""
        conn = _make_mock_conn([])

        repo = BrainRegistryRepository(conn)
        result = await repo.get_matching("unknown context")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_matching_query_includes_unnest_ilike(self) -> None:
        """get_matching() query uses unnest + ILIKE for GIN-compatible search."""
        conn = _make_mock_conn([])

        repo = BrainRegistryRepository(conn)
        await repo.get_matching("feature planning")

        conn.fetch.assert_called_once()
        query_arg = conn.fetch.call_args.args[0]
        assert "unnest" in query_arg.lower()
        assert "ilike" in query_arg.lower()


# ---------------------------------------------------------------------------
# C1.09: DynamicDispatchEngine uses BrainRegistryRepository (not dict)
# ---------------------------------------------------------------------------


def _mock_httpx_response(status_code: int = 204) -> MagicMock:
    """Return a fake httpx Response."""
    import httpx

    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    return resp


def _mock_httpx_client(status_code: int = 204) -> MagicMock:
    """Return a mock httpx.AsyncClient context manager."""
    client = AsyncMock()
    client.post = AsyncMock(return_value=_mock_httpx_response(status_code))
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=client)
    cm.__aexit__ = AsyncMock(return_value=None)
    return cm


@pytest.mark.asyncio
class TestDynamicDispatchEngineUsesRepository:
    """C1.09: DynamicDispatchEngine.dispatch() calls BrainRegistryRepository.get_by_id()."""

    async def test_dispatch_calls_get_by_id_for_each_brain(self) -> None:
        """dispatch() calls repo.get_by_id() for each brain_id in the routing config."""
        with (
            patch(
                "mastermind_cli.brain_registry_module.repository.BrainRegistryRepository.get_by_id"
            ) as mock_get_by_id,
            patch(
                "asyncpg.connect",
                new=AsyncMock(return_value=AsyncMock(close=AsyncMock())),
            ),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
            # Return a valid BrainRecord for any brain_id
            async def _make_record(brain_id: int) -> BrainRecord:
                return BrainRecord(
                    brain_id=brain_id,
                    name=f"Brain {brain_id}",
                    model_quality="claude-opus-4-6",
                    model_balanced="claude-sonnet-4-6",
                    model_budget="claude-haiku-4-5",
                    capabilities=["test"],
                    trigger_conditions=["test"],
                    enabled=True,
                )

            mock_get_by_id.side_effect = _make_record

            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            await engine.dispatch(19, "DISCUSSION")

        # DISCUSSION routes to brains 1,2,3 (parallel) + 7 (barrier) = 4 get_by_id calls
        assert mock_get_by_id.call_count == 4

    async def test_dispatch_uses_brain_registry_not_agent_registry(self) -> None:
        """dispatch() queries brain_registry table (via repo), not agent_registry."""
        # Track all SQL queries issued
        sql_queries: list[str] = []

        async def mock_fetchrow(query: str, *args: object) -> MagicMock | None:
            sql_queries.append(query)
            raw_id = args[0] if args else 0
            bid = int(str(raw_id))
            # Return a valid row for any brain_id
            return _make_brain_registry_row(
                bid,
                name=f"Brain {raw_id}",
            )

        conn = AsyncMock()
        conn.fetchrow = mock_fetchrow
        conn.close = AsyncMock()

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            await engine.dispatch(19, "DISCUSSION")

        # All queries must reference brain_registry, not agent_registry
        for query in sql_queries:
            assert "brain_registry" in query, f"Query references wrong table: {query}"
        assert all(
            "agent_registry" not in q for q in sql_queries
        ), "dispatch() still queries agent_registry — not migrated to BrainRegistryRepository"

    async def test_dispatch_returns_valid_result_from_repository(self) -> None:
        """dispatch() returns a valid DispatchResult when repo returns real BrainRecords."""
        row_brain1 = _make_brain_registry_row(1, name="Product Strategy")
        row_brain2 = _make_brain_registry_row(2, name="UX Research")
        row_brain3 = _make_brain_registry_row(3, name="UI Design")
        row_brain7 = _make_brain_registry_row(7, name="Growth/Data")

        brain_map = {1: row_brain1, 2: row_brain2, 3: row_brain3, 7: row_brain7}

        async def mock_fetchrow(query: str, *args: object) -> MagicMock | None:
            brain_id = int(str(args[0])) if args else 0
            return brain_map.get(brain_id)

        conn = AsyncMock()
        conn.fetchrow = mock_fetchrow
        conn.close = AsyncMock()

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "DISCUSSION")

        assert isinstance(result, DispatchResult)
        assert result.moment == "DISCUSSION"
        # parallel should have brains 1, 2, 3
        assert sorted([b.brain_id for b in result.parallel]) == [1, 2, 3]
        # barrier should have brain 7
        assert [b.brain_id for b in result.barrier] == [7]

    async def test_dispatch_brain_role_comes_from_brain_registry_name(self) -> None:
        """BrainDispatch.role is populated from BrainRecord.name (not hardcoded)."""
        row = _make_brain_registry_row(7, name="Growth/Data Evaluator")

        async def mock_fetchrow(query: str, *args: object) -> MagicMock | None:
            return row

        conn = AsyncMock()
        conn.fetchrow = mock_fetchrow
        conn.close = AsyncMock()

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            result = await engine.dispatch(19, "EXECUTION_WAVE")

        # Brain #7 is the only brain in EXECUTION_WAVE
        assert result.parallel[0].role == "Growth/Data Evaluator"

    async def test_dispatch_skips_missing_brain_gracefully(self) -> None:
        """dispatch() skips brain_ids not found in brain_registry (logs warning)."""
        # Return None for all brains (simulate empty registry)
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value=None)
        conn.close = AsyncMock()

        with (
            patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
            patch("httpx.AsyncClient", return_value=_mock_httpx_client()),
        ):
            engine = DynamicDispatchEngine(postgres_url="postgresql://fake/db")
            # Should not raise — missing brains are skipped
            result = await engine.dispatch(19, "DISCUSSION")

        # No brains found → empty parallel and barrier
        assert result.parallel == []
        assert result.barrier == []


# ---------------------------------------------------------------------------
# BrainRecord dataclass tests
# ---------------------------------------------------------------------------


class TestBrainRecord:
    """BrainRecord is an immutable frozen dataclass."""

    def test_brain_record_creation(self) -> None:
        """BrainRecord can be created with all required fields."""
        record = BrainRecord(
            brain_id=1,
            name="Product Strategy",
            model_quality="claude-opus-4-6",
            model_balanced="claude-sonnet-4-6",
            model_budget="claude-haiku-4-5",
            capabilities=["product-discovery"],
            trigger_conditions=["should we build"],
            enabled=True,
        )
        assert record.brain_id == 1
        assert record.name == "Product Strategy"
        assert record.capabilities == ["product-discovery"]

    def test_brain_record_is_frozen(self) -> None:
        """BrainRecord is immutable (frozen=True)."""
        record = BrainRecord(
            brain_id=1,
            name="Test",
            model_quality="q",
            model_balanced="b",
            model_budget="d",
            capabilities=[],
            trigger_conditions=[],
            enabled=True,
        )
        with pytest.raises((AttributeError, TypeError)):
            record.brain_id = 99  # type: ignore[misc]

    def test_brain_record_from_row(self) -> None:
        """BrainRecord.from_row() builds a record from asyncpg Row."""
        row = _make_brain_registry_row(
            5,
            name="Backend",
            capabilities=["api-design", "data-modeling"],
            trigger_conditions=["api design", "backend"],
        )
        record = BrainRecord.from_row(row)

        assert record.brain_id == 5
        assert record.name == "Backend"
        assert "api-design" in record.capabilities
        assert "api design" in record.trigger_conditions
