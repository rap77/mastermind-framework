"""Tests for the offline retrieval eval harness."""

from __future__ import annotations

from pathlib import Path

import pytest

from mastermind_cli.memory_layer.evaluation import EvalHarnessService
from mastermind_cli.memory_layer.evaluation_baseline import (
    BASELINE_PROJECT_ID,
    build_retrieval_baseline_cases,
    seed_retrieval_baseline_fixture,
)
from mastermind_cli.memory_layer.models import RetrievalEvalCase, VectorCandidate
from mastermind_cli.memory_layer.store_postgres import PostgresMemoryStore
from mastermind_cli.project_state.database.session import dispose_engines


@pytest.mark.asyncio
async def test_eval_harness_reports_all_cases_passing(tmp_path: Path) -> None:
    """The harness should return a green scorecard when expected hits are present."""
    store = build_store(tmp_path)
    await seed_retrieval_baseline_fixture(store)
    harness = EvalHarnessService(store)

    report = await harness.run_project_baseline(
        project_id=BASELINE_PROJECT_ID,
        cases=build_retrieval_baseline_cases(),
        limit=5,
    )

    assert report.total_cases == 3
    assert report.passed_cases == 3
    assert report.pass_rate == 1.0
    assert [case.passed for case in report.cases] == [True, True, True]


@pytest.mark.asyncio
async def test_eval_harness_flags_missing_expected_hit(tmp_path: Path) -> None:
    """The harness should fail a case when the expected memory is absent."""
    store = build_store(tmp_path)
    await seed_retrieval_baseline_fixture(store)
    harness = EvalHarnessService(store)

    report = await harness.run_project_baseline(
        project_id=BASELINE_PROJECT_ID,
        cases=[
            RetrievalEvalCase(
                case_id="case-miss",
                query="marketing crm",
                expected_memory_ids=["missing-memory"],
            )
        ],
        limit=5,
    )

    assert report.total_cases == 1
    assert report.passed_cases == 0
    assert report.pass_rate == 0.0
    assert report.cases[0].passed is False
    assert report.cases[0].matched_memory_ids == ["mem-marketing"]


@pytest.mark.asyncio
async def test_eval_harness_runs_shared_retrieval_v1_baseline(tmp_path: Path) -> None:
    """The shared Retrieval v1 baseline should run green through the convenience API."""
    store = build_store(tmp_path)
    await seed_retrieval_baseline_fixture(store)
    harness = EvalHarnessService(store)

    report = await harness.run_retrieval_v1_baseline(
        project_id=BASELINE_PROJECT_ID,
        limit=5,
    )

    assert report.total_cases == 3
    assert report.passed_cases == 3
    assert report.pass_rate == 1.0


@pytest.mark.asyncio
async def test_eval_harness_shared_baseline_stays_green_with_vector_fusion(
    tmp_path: Path,
) -> None:
    """Shared baseline should remain green when semantic candidates are fused in."""
    database_url = f"sqlite:///{tmp_path / 'memory_eval_harness_vector.db'}"
    dispose_engines()

    class StubVectorCandidateProvider:
        """Return one semantic candidate for the auth-drift case."""

        async def search(
            self,
            query: str,
            scope: dict[str, str | None] | None = None,
            limit: int = 10,
        ) -> list[str]:
            del query, scope, limit
            raise AssertionError("legacy vector seam should not run in this test")

        async def search_candidates(
            self,
            query: str,
            scope: dict[str, str | None] | None = None,
            limit: int = 10,
        ) -> list[VectorCandidate]:
            del scope, limit
            if query == "jwt drift":
                return [VectorCandidate(memory_id="mem-auth", score=0.8)]
            return []

    store = PostgresMemoryStore(
        database_url,
        vector_provider=StubVectorCandidateProvider(),
    )
    await seed_retrieval_baseline_fixture(store)
    harness = EvalHarnessService(store)

    report = await harness.run_retrieval_v1_baseline(
        project_id=BASELINE_PROJECT_ID,
        limit=5,
    )

    assert report.total_cases == 3
    assert report.passed_cases == 3
    assert report.pass_rate == 1.0


def build_store(tmp_path: Path) -> PostgresMemoryStore:
    """Create an isolated store for offline retrieval eval tests."""
    database_url = f"sqlite:///{tmp_path / 'memory_eval_harness.db'}"
    dispose_engines()
    return PostgresMemoryStore(database_url)
