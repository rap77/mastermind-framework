"""
Unit tests for Brain #1 RAG integration — Phase 21.

Tests:
- 21.15: mock build() returns block → system prompt includes [RETRIEVED CONTEXT]
- 21.16: mock build() returns "" → system prompt does NOT include [RETRIEVED CONTEXT]
- 21.21: log_execution(custom_metadata={"rag_enabled": True}) → persists in DB
"""

from __future__ import annotations

import json

import aiosqlite
import pytest

from mastermind_cli.orchestrator.brain_functions import brain_01_product_strategy
from mastermind_cli.types.interfaces import BrainInput, Brief


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeMCPClient:
    """Minimal fake MCPClient that captures the query text."""

    def __init__(self) -> None:
        self.last_query: str = ""

    def query_notebooklm(self, notebook_id: str, query: str) -> str:
        self.last_query = query
        # Return minimal parseable text so ProductStrategy doesn't crash
        return (
            "POSITIONING: test position\n"
            "AUDIENCE: test audience\n"
            "FEATURES:\n- feature A\nMETRICS:\n- metric 1\nRISKS:\n- none"
        )


def _make_brain_input(problem: str = "Build a SaaS CRM for SMBs") -> BrainInput:
    return BrainInput(
        brief=Brief(problem_statement=problem),
        additional_context={},
        execution_metadata={},
    )


# ---------------------------------------------------------------------------
# 21.15: rag_context non-empty → system prompt includes [RETRIEVED CONTEXT]
# ---------------------------------------------------------------------------


def test_brain1_system_prompt_includes_rag_context_when_non_empty() -> None:
    """21.15: When rag_context is non-empty, query appended to system prompt."""
    mcp = _FakeMCPClient()
    brain_input = _make_brain_input()
    rag_block = "[RETRIEVED CONTEXT]\n--- domain_knowledge (top-5) ---\n[1] (score: 0.90) [source: FUENTE-001] empowered teams\n[END RETRIEVED CONTEXT]"

    brain_01_product_strategy(brain_input, mcp_client=mcp, rag_context=rag_block)

    assert "[RETRIEVED CONTEXT]" in mcp.last_query
    assert "[END RETRIEVED CONTEXT]" in mcp.last_query
    assert "empowered teams" in mcp.last_query


# ---------------------------------------------------------------------------
# 21.16: rag_context empty → system prompt does NOT include [RETRIEVED CONTEXT]
# ---------------------------------------------------------------------------


def test_brain1_system_prompt_excludes_rag_block_when_empty() -> None:
    """21.16: When rag_context is '', system prompt has no [RETRIEVED CONTEXT]."""
    mcp = _FakeMCPClient()
    brain_input = _make_brain_input()

    brain_01_product_strategy(brain_input, mcp_client=mcp, rag_context="")

    assert "[RETRIEVED CONTEXT]" not in mcp.last_query
    assert "[END RETRIEVED CONTEXT]" not in mcp.last_query


# ---------------------------------------------------------------------------
# 21.16 (extra): default rag_context="" → backward compat, no block appended
# ---------------------------------------------------------------------------


def test_brain1_default_rag_context_no_block() -> None:
    """21.16 extra: Calling brain_01_product_strategy without rag_context → no block."""
    mcp = _FakeMCPClient()
    brain_input = _make_brain_input()

    brain_01_product_strategy(brain_input, mcp_client=mcp)  # no rag_context arg

    assert "[RETRIEVED CONTEXT]" not in mcp.last_query


# ---------------------------------------------------------------------------
# 21.21: log_execution(custom_metadata={"rag_enabled": True}) persists in DB
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_log_execution_persists_rag_enabled_true() -> None:
    """21.21: log_execution with custom_metadata={"rag_enabled": True} → DB has key."""
    from mastermind_cli.experience.logger import ExperienceLogger

    # Use an in-memory SQLite DB for isolation
    async with aiosqlite.connect(":memory:") as raw_conn:
        raw_conn.row_factory = aiosqlite.Row

        # Bootstrap schema via DatabaseConnection wrapper
        class _FakeDB:
            """Minimal DatabaseConnection stand-in for testing."""

            conn = raw_conn

            async def create_experience_schema(self) -> None:
                await self.conn.execute(
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
                await self.conn.commit()

        fake_db = _FakeDB()
        await fake_db.create_experience_schema()

        logger = ExperienceLogger(fake_db)  # type: ignore[arg-type]
        await logger.log_execution(
            brain_id="brain-01-product-strategy",
            input_json={"brief": "test brief"},
            output_json={"result": "ok"},
            duration_ms=100,
            status="success",
            custom_metadata={"rag_enabled": True},
        )

        cursor = await raw_conn.execute(
            "SELECT custom_metadata FROM experience_records ORDER BY timestamp DESC LIMIT 1"
        )
        row = await cursor.fetchone()
        assert row is not None, "No experience_records row found"

        metadata = json.loads(row[0])
        assert (
            "rag_enabled" in metadata
        ), f"rag_enabled key missing from custom_metadata: {metadata}"
        # json.loads may give us True (bool) or "true" (string) — both acceptable
        assert metadata["rag_enabled"] in (
            True,
            "true",
            1,
        ), f"Expected rag_enabled=True, got: {metadata['rag_enabled']}"
