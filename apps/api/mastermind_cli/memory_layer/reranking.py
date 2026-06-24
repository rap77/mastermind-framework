"""Optional reranking providers for Retrieval v1 follow-on work."""

from __future__ import annotations

from .models import MemorySearchResult


class NoopMemoryReranker:
    """Reranker that preserves the incoming result order exactly."""

    async def rerank(
        self,
        query: str,
        results: list[MemorySearchResult],
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Return the original ranked results unchanged."""
        del query, scope
        return list(results[:limit])


class HeuristicMemoryReranker:
    """Deterministic local reranker for Retrieval v1 follow-on work."""

    async def rerank(
        self,
        query: str,
        results: list[MemorySearchResult],
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Apply small exact-match and scope-aware boosts to fused results."""
        query_terms = [term for term in query.lower().split() if term]
        reranked = sorted(
            results,
            key=lambda result: (
                result.score + self._heuristic_bonus(result, query_terms, scope),
                result.score,
            ),
            reverse=True,
        )
        return list(reranked[:limit])

    def _heuristic_bonus(
        self,
        result: MemorySearchResult,
        query_terms: list[str],
        scope: dict[str, str | None] | None,
    ) -> float:
        """Return deterministic local boosts for reranking."""
        if not query_terms:
            return 0.0

        title = result.title.lower()
        snippet = result.snippet.lower()
        bonus = 0.0

        if all(term in title for term in query_terms):
            bonus += 2.0
        elif any(term in title for term in query_terms):
            bonus += 0.5

        if all(term in snippet for term in query_terms):
            bonus += 0.5

        if scope and scope.get("memory_type") == result.memory_type:
            bonus += 0.25
        if scope and scope.get("brain_id") and scope["brain_id"] == result.brain_id:
            bonus += 0.25

        return bonus


__all__ = ["HeuristicMemoryReranker", "NoopMemoryReranker"]
