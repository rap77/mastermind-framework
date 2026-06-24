"""Offline retrieval eval harness for deterministic memory baselines."""

from __future__ import annotations

from .evaluation_baseline import build_retrieval_baseline_cases
from .contracts import MemoryStore
from .models import (
    RetrievalEvalCase,
    RetrievalEvalCaseResult,
    RetrievalEvalReport,
)


class EvalHarnessService:
    """Run deterministic retrieval baselines over a MemoryStore."""

    def __init__(self, store: MemoryStore) -> None:
        """Initialize the harness with a concrete memory backend."""
        self._store = store

    async def run_project_baseline(
        self,
        *,
        project_id: str,
        cases: list[RetrievalEvalCase],
        limit: int = 10,
    ) -> RetrievalEvalReport:
        """Execute a fixed retrieval baseline and return a scorecard."""
        case_results: list[RetrievalEvalCaseResult] = []
        for case in cases:
            scope = {"project_id": project_id, **case.scope}
            results = await self._store.search(case.query, scope=scope, limit=limit)
            matched_memory_ids = [result.memory_id for result in results]
            passed = all(
                expected_memory_id in matched_memory_ids
                for expected_memory_id in case.expected_memory_ids
            )
            case_results.append(
                RetrievalEvalCaseResult(
                    case_id=case.case_id,
                    query=case.query,
                    passed=passed,
                    expected_memory_ids=list(case.expected_memory_ids),
                    matched_memory_ids=matched_memory_ids,
                    scope=scope,
                )
            )

        passed_cases = sum(1 for case in case_results if case.passed)
        total_cases = len(case_results)
        pass_rate = passed_cases / total_cases if total_cases else 0.0
        return RetrievalEvalReport(
            total_cases=total_cases,
            passed_cases=passed_cases,
            pass_rate=pass_rate,
            cases=case_results,
        )

    async def run_retrieval_v1_baseline(
        self,
        *,
        project_id: str,
        limit: int = 10,
    ) -> RetrievalEvalReport:
        """Execute the shared Retrieval v1 baseline cases for one project."""
        return await self.run_project_baseline(
            project_id=project_id,
            cases=build_retrieval_baseline_cases(),
            limit=limit,
        )
