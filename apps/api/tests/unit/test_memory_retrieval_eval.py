"""Deterministic retrieval baseline tests for the first-party memory layer."""

from __future__ import annotations

import asyncio
from pathlib import Path

from mastermind_cli.memory_layer.evaluation_baseline import (
    BASELINE_PROJECT_ID,
    build_retrieval_baseline_cases,
    seed_retrieval_baseline_fixture,
)
from mastermind_cli.memory_layer.store_postgres import PostgresMemoryStore
from mastermind_cli.project_state.database.session import dispose_engines


def test_retrieval_eval_multiterm_query_matches_across_title_and_content(
    tmp_path: Path,
) -> None:
    """A multi-term query should match the best item even when terms span fields."""
    store = build_store(tmp_path)
    asyncio.run(seed_retrieval_baseline_fixture(store))

    results = asyncio.run(
        store.search(
            "marketing crm", scope={"project_id": BASELINE_PROJECT_ID}, limit=5
        )
    )

    assert results
    assert results[0].title == "Marketing launch checklist"


def test_retrieval_eval_scoped_query_prefers_investment_memory(tmp_path: Path) -> None:
    """The baseline should keep niche-specific retrieval deterministic."""
    store = build_store(tmp_path)
    asyncio.run(seed_retrieval_baseline_fixture(store))

    results = asyncio.run(
        store.search(
            "risk rebalance",
            scope={"project_id": BASELINE_PROJECT_ID, "niche": "investments"},
            limit=5,
        )
    )

    assert results
    assert results[0].title == "Investment rebalance note"


def test_retrieval_eval_returns_empty_for_out_of_scope_query(tmp_path: Path) -> None:
    """The baseline should return no hits when scope excludes all matching items."""
    store = build_store(tmp_path)
    asyncio.run(seed_retrieval_baseline_fixture(store))

    results = asyncio.run(
        store.search(
            "launch",
            scope={"project_id": BASELINE_PROJECT_ID, "memory_type": "pattern"},
            limit=5,
        )
    )

    assert results == []


def test_retrieval_eval_baseline_cases_have_expected_ids() -> None:
    """The reusable baseline should declare expected hits for each case."""
    cases = build_retrieval_baseline_cases()

    assert [case.case_id for case in cases] == [
        "baseline-marketing-crm",
        "baseline-investment-risk",
        "baseline-auth-drift",
    ]
    assert all(case.expected_memory_ids for case in cases)


def build_store(tmp_path: Path) -> PostgresMemoryStore:
    """Create an isolated store for deterministic retrieval tests."""
    database_url = f"sqlite:///{tmp_path / 'memory_retrieval_eval.db'}"
    dispose_engines()
    return PostgresMemoryStore(database_url)
