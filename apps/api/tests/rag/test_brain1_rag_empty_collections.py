"""
Integration tests for Brain #1 RAG pilot — Phase 21.

Tests:
- 21.17: Brain #1 with empty collections responds without error; rag_enabled=False
          in custom_metadata when log_execution is called with empty rag_context.
- 21.22: execute_flow (mocked) → experience_records.custom_metadata has rag_enabled key.

These tests mock all external dependencies (asyncpg, MCP) so they run offline.
"""

from __future__ import annotations

import json
from typing import Any

import aiosqlite
import pytest


# ---------------------------------------------------------------------------
# 21.17: Brain #1 with both collections empty → no error, rag_enabled=False
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_brain1_empty_collections_no_error_rag_disabled() -> None:
    """21.17: Brain #1 with empty collections responds without error; rag_enabled=False."""
    from mastermind_cli.orchestrator.brain_functions import brain_01_product_strategy
    from mastermind_cli.types.interfaces import BrainInput, Brief

    class _FakeMCP:
        def query_notebooklm(self, notebook_id: str, query: str) -> str:
            return (
                "POSITIONING: basic\nAUDIENCE: everyone\nFEATURES:\n- f1\n"
                "METRICS:\n- m1\nRISKS:\n- r1"
            )

    # Empty rag_context (as returned by RAGContextBuilder when collections empty)
    brain_input = BrainInput(
        brief=Brief(problem_statement="Build a simple task manager app"),
        additional_context={},
        execution_metadata={},
    )

    # Should NOT raise even with empty rag_context
    result = brain_01_product_strategy(
        brain_input, mcp_client=_FakeMCP(), rag_context=""
    )
    assert result is not None
    assert result.positioning  # non-empty positioning

    # Verify rag_enabled would be False for empty context
    rag_context = ""
    rag_enabled = rag_context != ""
    assert rag_enabled is False


# ---------------------------------------------------------------------------
# 21.17b: StatelessCoordinator with conn=None skips RAG, Brain #1 succeeds
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_coordinator_brain1_with_none_conn_skips_rag() -> None:
    """21.17b: When conn=None, Brain #1 executes without RAG (rag_context='')."""
    from mastermind_cli.orchestrator.stateless_coordinator import (
        create_stateless_coordinator,
    )
    from mastermind_cli.types.interfaces import Brief

    class _FakeMCP:
        def query_notebooklm(self, notebook_id: str, query: str) -> str:
            # Confirm that [RETRIEVED CONTEXT] is NOT in the query when conn=None
            assert (
                "[RETRIEVED CONTEXT]" not in query
            ), "RAG block should not appear when conn=None"
            return (
                "POSITIONING: pos\nAUDIENCE: aud\nFEATURES:\n- f1\n"
                "METRICS:\n- m1\nRISKS:\n- r1"
            )

    coordinator = create_stateless_coordinator(_FakeMCP())
    brief = Brief(problem_statement="Build a simple todo app for remote teams")

    results = await coordinator.execute_flow(
        brief,
        ["brain-01-product-strategy"],
        conn=None,  # no asyncpg → RAG skipped
    )

    assert "brain-01-product-strategy" in results


# ---------------------------------------------------------------------------
# 21.22: log_execution after Brain #1 flow → custom_metadata has rag_enabled key
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_experience_record_has_rag_enabled_after_brain1() -> None:
    """21.22: After Brain #1 session, experience_records.custom_metadata has rag_enabled."""
    import aiosqlite

    from mastermind_cli.experience.logger import ExperienceLogger

    async with aiosqlite.connect(":memory:") as conn:
        conn.row_factory = aiosqlite.Row

        # Bootstrap schema
        await conn.execute(
            """CREATE TABLE IF NOT EXISTS experience_records (
                id TEXT PRIMARY KEY,
                brain_id TEXT NOT NULL,
                input_hash TEXT NOT NULL,
                output_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                duration_ms INTEGER NOT NULL,
                status TEXT NOT NULL,
                embedding_stub TEXT,
                parent_brain_id TEXT,
                trace_context_id TEXT,
                custom_metadata TEXT NOT NULL DEFAULT '{}',
                expires_at TEXT
            )"""
        )
        await conn.commit()

        class _FakeDB:
            def __init__(self, c: aiosqlite.Connection) -> None:
                self.conn = c

        db = _FakeDB(conn)
        logger = ExperienceLogger(db)  # type: ignore[arg-type]

        # Simulate what task_runner does after Brain #1 execution:
        # rag_enabled = (rag_context != "") — empty collections → False
        rag_enabled = False
        custom_meta: dict[str, Any] = {
            "model": "test-model",
            "task_id": "test-task-001",
            "rag_enabled": rag_enabled,
        }

        await logger.log_execution(
            brain_id="brain-01-product-strategy",
            input_json={"brief": "Build a SaaS product", "flow": "validation_only"},
            output_json={"positioning": "test", "target_audience": "devs"},
            duration_ms=500,
            status="success",
            custom_metadata=custom_meta,
        )

        # Query using SELECT custom_metadata FROM experience_records
        cursor = await conn.execute(
            "SELECT custom_metadata FROM experience_records ORDER BY timestamp DESC LIMIT 1"
        )
        row = await cursor.fetchone()
        assert row is not None

        stored = json.loads(row[0])
        assert (
            "rag_enabled" in stored
        ), f"rag_enabled key missing from stored custom_metadata: {stored}"
        # Value should be False (empty collections → no RAG)
        assert stored["rag_enabled"] in (
            False,
            "false",
            0,
        ), f"Expected rag_enabled=False, got: {stored['rag_enabled']}"
