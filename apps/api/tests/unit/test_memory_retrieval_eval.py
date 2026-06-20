"""Deterministic retrieval baseline tests for the first-party memory layer."""

from __future__ import annotations

import asyncio
from pathlib import Path

from mastermind_cli.memory_layer.models import MemoryItem
from mastermind_cli.memory_layer.store_postgres import PostgresMemoryStore
from mastermind_cli.project_state.database.session import dispose_engines


def test_retrieval_eval_multiterm_query_matches_across_title_and_content(
    tmp_path: Path,
) -> None:
    """A multi-term query should match the best item even when terms span fields."""
    store = build_store(tmp_path)
    seed_retrieval_fixture(store)

    results = asyncio.run(
        store.search("marketing crm", scope={"project_id": "proj-memory"}, limit=5)
    )

    assert results
    assert results[0].title == "Marketing launch checklist"


def test_retrieval_eval_scoped_query_prefers_investment_memory(tmp_path: Path) -> None:
    """The baseline should keep niche-specific retrieval deterministic."""
    store = build_store(tmp_path)
    seed_retrieval_fixture(store)

    results = asyncio.run(
        store.search(
            "risk rebalance",
            scope={"project_id": "proj-memory", "niche": "investments"},
            limit=5,
        )
    )

    assert results
    assert results[0].title == "Investment rebalance note"


def test_retrieval_eval_returns_empty_for_out_of_scope_query(tmp_path: Path) -> None:
    """The baseline should return no hits when scope excludes all matching items."""
    store = build_store(tmp_path)
    seed_retrieval_fixture(store)

    results = asyncio.run(
        store.search(
            "launch",
            scope={"project_id": "proj-memory", "memory_type": "pattern"},
            limit=5,
        )
    )

    assert results == []


def build_store(tmp_path: Path) -> PostgresMemoryStore:
    """Create an isolated store for deterministic retrieval tests."""
    database_url = f"sqlite:///{tmp_path / 'memory_retrieval_eval.db'}"
    dispose_engines()
    return PostgresMemoryStore(database_url)


def seed_retrieval_fixture(store: PostgresMemoryStore) -> None:
    """Seed a fixed retrieval corpus for baseline memory-search assertions."""
    fixture_items = [
        MemoryItem(
            memory_id=None,
            memory_type="decision",
            title="Marketing launch checklist",
            content="Coordinate attribution, CRM sync, and CAC guardrails.",
            project_id="proj-memory",
            brain_id="brain-01-product-strategy",
            niche="marketing-digital",
            visibility="project",
        ),
        MemoryItem(
            memory_id=None,
            memory_type="lesson",
            title="Investment rebalance note",
            content="Review portfolio risk bands every Friday before rebalance.",
            project_id="proj-memory",
            brain_id="brain-07-growth-data",
            niche="investments",
            visibility="project",
        ),
        MemoryItem(
            memory_id=None,
            memory_type="pattern",
            title="Recurring auth drift",
            content="Refresh token handling breaks when JWT clocks drift.",
            project_id="proj-memory",
            brain_id="brain-06-qa-devops",
            niche="software-development",
            visibility="project",
        ),
    ]

    for item in fixture_items:
        asyncio.run(store.save_item(item))
