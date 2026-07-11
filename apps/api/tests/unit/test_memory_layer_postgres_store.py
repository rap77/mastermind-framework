"""Tests for the SQL-backed PostgresMemoryStore."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TypeVar
from collections.abc import Awaitable

import pytest

from sqlalchemy import select

from mastermind_cli.memory_layer.store_postgres import (
    MemoryPreferenceRecord,
    MemorySessionRecord,
    PostgresMemoryStore,
)
from mastermind_cli.memory_layer.models import (
    CheckpointRecord,
    MemoryIndexPayload,
    MemoryItem,
    MemorySearchResult,
    VectorCandidate,
)
from mastermind_cli.memory_layer.contracts import MemoryIndexProvider
from mastermind_cli.memory_layer.graph_recall import (
    MetadataMemoryGraphRecallProvider,
    StaticMemoryGraphRecallProvider,
)
from mastermind_cli.memory_layer.reranking import HeuristicMemoryReranker
from mastermind_cli.memory_layer.vector import NoopVectorSearchProvider
from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
)

T = TypeVar("T")


def test_save_and_get_item_round_trip(tmp_path: Path) -> None:
    """Stored memory items should round-trip through the canonical model."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    saved = run_async(
        store.save_item(
            MemoryItem(
                memory_type="lesson",
                title="Avoid execution drift",
                content="Execution projections must read canonical artifacts first.",
                project_id="proj-001",
                brain_id="brain-07-growth-data",
                niche="software-development",
                visibility="project",
                tags=["executions", "artifacts"],
                metadata={"confidence": "high"},
            )
        )
    )

    fetched = run_async(store.get_item(saved.memory_id or ""))

    assert saved.memory_id is not None
    assert fetched is not None
    assert fetched.memory_id == saved.memory_id
    assert fetched.memory_type == "lesson"
    assert fetched.project_id == "proj-001"
    assert fetched.tags == ["executions", "artifacts"]
    assert fetched.metadata == {"confidence": "high"}


def test_checkpoint_round_trip_and_latest_selection(tmp_path: Path) -> None:
    """Checkpoint persistence should round-trip and resolve the latest record."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    older = run_async(
        store.save_checkpoint(
            CheckpointRecord(
                checkpoint_id="ckpt-old",
                project_id="proj-001",
                task_id="task-1",
                run_id="run-1",
                context_summary={"step": 1},
                resume_state={"phase": "draft"},
                next_step_summary="Earlier step.",
                created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            )
        )
    )
    newer = run_async(
        store.save_checkpoint(
            CheckpointRecord(
                checkpoint_id="ckpt-new",
                project_id="proj-001",
                task_id="task-2",
                run_id="run-2",
                context_summary={"step": 2},
                resume_state={"phase": "review"},
                next_step_summary="Latest step.",
                created_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
            )
        )
    )

    latest = run_async(store.get_latest_checkpoint("proj-001"))
    task_1_latest = run_async(store.get_latest_checkpoint("proj-001", "task-1"))
    recent = run_async(store.list_recent_checkpoints("proj-001", limit=10))

    assert older.checkpoint_id == "ckpt-old"
    assert newer.checkpoint_id == "ckpt-new"
    assert latest is not None
    assert latest.checkpoint_id == "ckpt-new"
    assert task_1_latest is not None
    assert task_1_latest.checkpoint_id == "ckpt-old"
    assert [checkpoint.checkpoint_id for checkpoint in recent] == [
        "ckpt-new",
        "ckpt-old",
    ]


def test_save_item_upserts_saved_memory_into_index_provider(tmp_path: Path) -> None:
    """Saving a memory item should feed the canonical payload into the index seam."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    indexed_payloads: list[MemoryIndexPayload] = []

    class StubIndexProvider:
        """Collect indexed items for assertion."""

        async def upsert(self, payload: MemoryIndexPayload) -> None:
            indexed_payloads.append(payload)

    index_provider: MemoryIndexProvider = StubIndexProvider()
    store = PostgresMemoryStore(database_url, index_provider=index_provider)

    saved = run_async(
        store.save_item(
            MemoryItem(
                memory_type="lesson",
                title="Index this memory",
                content="Semantic indexing will consume canonical memory items.",
                project_id="proj-001",
                visibility="project",
            )
        )
    )

    assert len(indexed_payloads) == 1
    assert indexed_payloads[0].memory_id == saved.memory_id
    assert indexed_payloads[0].title == "Index this memory"
    assert (
        "Semantic indexing will consume canonical memory items."
        in indexed_payloads[0].embedding_text
    )


def test_search_matches_title_and_content_with_project_scope(tmp_path: Path) -> None:
    """Search should honor the project scope and return ranked canonical results."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    run_async(
        store.save_item(
            MemoryItem(
                memory_type="decision",
                title="Marketing launch checklist",
                content="Coordinate attribution, CRM sync, and CAC guardrails.",
                project_id="proj-mkt",
                visibility="project",
            )
        )
    )
    run_async(
        store.save_item(
            MemoryItem(
                memory_type="decision",
                title="Investment rebalance note",
                content="Review portfolio risk bands every Friday.",
                project_id="proj-invest",
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("launch", scope={"project_id": "proj-mkt"}, limit=5)
    )

    assert len(results) == 1
    assert results[0].title == "Marketing launch checklist"
    assert results[0].memory_type == "decision"
    assert results[0].project_id == "proj-mkt"
    assert results[0].score > 0


def test_search_ranks_title_matches_above_content_only_matches(tmp_path: Path) -> None:
    """A title hit should outrank a content-only hit for the same query."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    run_async(
        store.save_item(
            MemoryItem(
                memory_id=None,
                memory_type="lesson",
                title="Launch checklist",
                content="Coordinate GTM and CRM guardrails.",
                project_id="proj-001",
                brain_id=None,
                niche=None,
                visibility="project",
            )
        )
    )
    run_async(
        store.save_item(
            MemoryItem(
                memory_id=None,
                memory_type="lesson",
                title="Weekly review",
                content="Review the launch brief with the marketing team.",
                project_id="proj-001",
                brain_id=None,
                niche=None,
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("launch", scope={"project_id": "proj-001"}, limit=5)
    )

    assert len(results) == 2
    assert results[0].title == "Launch checklist"
    assert results[0].score > results[1].score


def test_search_honors_brain_niche_and_memory_type_scope(tmp_path: Path) -> None:
    """Search should respect the narrower retrieval scopes beyond project_id."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    run_async(
        store.save_item(
            MemoryItem(
                memory_id=None,
                memory_type="pattern",
                title="Finance risk pattern",
                content="Escalate concentration risk during portfolio review.",
                project_id="proj-001",
                brain_id="brain-07-growth-data",
                niche="investments",
                visibility="project",
            )
        )
    )
    run_async(
        store.save_item(
            MemoryItem(
                memory_id=None,
                memory_type="decision",
                title="Finance risk decision",
                content="Escalate concentration risk during portfolio review.",
                project_id="proj-001",
                brain_id="brain-07-growth-data",
                niche="investments",
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search(
            "risk",
            scope={
                "project_id": "proj-001",
                "brain_id": "brain-07-growth-data",
                "niche": "investments",
                "memory_type": "pattern",
            },
            limit=5,
        )
    )

    assert len(results) == 1
    assert results[0].title == "Finance risk pattern"
    assert results[0].memory_type == "pattern"


def test_search_uses_vector_fallback_when_lexical_has_no_hits(tmp_path: Path) -> None:
    """Vector seam should provide candidates only when lexical search is empty."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()

    vector_calls: list[tuple[str, dict[str, str | None] | None, int]] = []
    seeded_memory_id = "memory-vector-001"

    async def fake_vector_search(
        query: str,
        scope: dict[str, str | None] | None,
        limit: int,
    ) -> list[str]:
        vector_calls.append((query, scope, limit))
        return [seeded_memory_id]

    store = PostgresMemoryStore(database_url, vector_search=fake_vector_search)

    run_async(
        store.save_item(
            MemoryItem(
                memory_id=seeded_memory_id,
                memory_type="lesson",
                title="Cross-project CRM memory",
                content="Semantic note about account retention tooling.",
                project_id="proj-001",
                brain_id=None,
                niche="marketing-digital",
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("client graph", scope={"project_id": "proj-001"}, limit=5)
    )

    assert vector_calls == [("client graph", {"project_id": "proj-001"}, 5)]
    assert len(results) == 1
    assert results[0].memory_id == seeded_memory_id
    assert results[0].why_matched == "vector:fallback"


def test_search_fuses_vector_candidates_when_lexical_already_matches(
    tmp_path: Path,
) -> None:
    """Vector seam should add semantic candidates without disturbing lexical leaders."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()

    lexical_memory_id = "memory-lexical-001"
    semantic_memory_id = "memory-semantic-001"
    vector_calls: list[tuple[str, dict[str, str | None] | None, int]] = []

    async def fake_vector_search(
        query: str,
        scope: dict[str, str | None] | None,
        limit: int,
    ) -> list[str]:
        vector_calls.append((query, scope, limit))
        return [semantic_memory_id]

    store = PostgresMemoryStore(database_url, vector_search=fake_vector_search)

    run_async(
        store.save_item(
            MemoryItem(
                memory_id=lexical_memory_id,
                memory_type="lesson",
                title="Customer graph launch note",
                content="Launch note for customer graph recall.",
                project_id="proj-001",
                brain_id=None,
                niche="marketing-digital",
                visibility="project",
            )
        )
    )
    run_async(
        store.save_item(
            MemoryItem(
                memory_id=semantic_memory_id,
                memory_type="lesson",
                title="Retention playbook",
                content="Semantic note about account relationships and retention signals.",
                project_id="proj-001",
                brain_id=None,
                niche="marketing-digital",
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("customer graph", scope={"project_id": "proj-001"}, limit=5)
    )

    assert vector_calls == [("customer graph", {"project_id": "proj-001"}, 5)]
    assert len(results) == 2
    assert results[0].memory_id == lexical_memory_id
    assert results[0].why_matched == "lexical:title_or_content"
    assert results[1].memory_id == semantic_memory_id
    assert results[1].why_matched == "vector:fusion"


def test_search_dedupes_overlap_between_lexical_and_vector_candidates(
    tmp_path: Path,
) -> None:
    """A memory found by both lexical and vector paths should only appear once."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    shared_memory_id = "memory-shared-001"

    async def fake_vector_search(
        query: str,
        scope: dict[str, str | None] | None,
        limit: int,
    ) -> list[str]:
        return [shared_memory_id]

    store = PostgresMemoryStore(database_url, vector_search=fake_vector_search)

    run_async(
        store.save_item(
            MemoryItem(
                memory_id=shared_memory_id,
                memory_type="lesson",
                title="Customer graph launch note",
                content="Launch note for customer graph recall.",
                project_id="proj-001",
                brain_id=None,
                niche="marketing-digital",
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("customer graph", scope={"project_id": "proj-001"}, limit=5)
    )

    assert len(results) == 1
    assert results[0].memory_id == shared_memory_id
    assert results[0].why_matched == "fusion:lexical+vector"
    assert results[0].score > 2.0


def test_search_accepts_vector_provider_protocol(tmp_path: Path) -> None:
    """The store should support a pluggable vector provider implementation."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    seeded_memory_id = "memory-provider-001"

    class StubVectorProvider:
        async def search(
            self,
            query: str,
            scope: dict[str, str | None] | None = None,
            limit: int = 10,
        ) -> list[str]:
            assert query == "semantic recall"
            assert scope == {"project_id": "proj-001"}
            assert limit == 5
            return [seeded_memory_id]

    store = PostgresMemoryStore(
        database_url,
        vector_provider=StubVectorProvider(),
    )
    run_async(
        store.save_item(
            MemoryItem(
                memory_id=seeded_memory_id,
                memory_type="lesson",
                title="Semantic recall note",
                content="Project memory for semantic retrieval.",
                project_id="proj-001",
                brain_id=None,
                niche="software-development",
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("semantic recall", scope={"project_id": "proj-001"}, limit=5)
    )

    assert len(results) == 1
    assert results[0].memory_id == seeded_memory_id
    assert results[0].why_matched == "fusion:lexical+vector"


def test_search_accepts_explicit_vector_candidate_seam(tmp_path: Path) -> None:
    """The store should support scored vector candidates without changing callers."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    semantic_memory_id = "memory-candidate-001"

    class StubVectorCandidateProvider:
        async def search(
            self,
            query: str,
            scope: dict[str, str | None] | None = None,
            limit: int = 10,
        ) -> list[str]:
            del query, scope, limit
            raise AssertionError(
                "legacy search() should not be used when candidates exist"
            )

        async def search_candidates(
            self,
            query: str,
            scope: dict[str, str | None] | None = None,
            limit: int = 10,
        ) -> list[VectorCandidate]:
            assert query == "semantic recall"
            assert scope == {"project_id": "proj-001"}
            assert limit == 5
            return [VectorCandidate(memory_id=semantic_memory_id, score=0.9)]

    store = PostgresMemoryStore(
        database_url,
        vector_provider=StubVectorCandidateProvider(),
    )
    run_async(
        store.save_item(
            MemoryItem(
                memory_id=semantic_memory_id,
                memory_type="lesson",
                title="Semantic recall note",
                content="Project memory for semantic retrieval.",
                project_id="proj-001",
                brain_id=None,
                niche="software-development",
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("semantic recall", scope={"project_id": "proj-001"}, limit=5)
    )

    assert len(results) == 1
    assert results[0].memory_id == semantic_memory_id
    assert results[0].why_matched == "fusion:lexical+vector"
    assert results[0].score >= 2.9


def test_search_with_noop_vector_provider_keeps_lexical_only_behavior(
    tmp_path: Path,
) -> None:
    """A noop provider should preserve lexical-only retrieval semantics."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(
        database_url,
        vector_provider=NoopVectorSearchProvider(),
    )

    run_async(
        store.save_item(
            MemoryItem(
                memory_id=None,
                memory_type="lesson",
                title="Customer graph launch note",
                content="Launch note for customer graph recall.",
                project_id="proj-001",
                brain_id=None,
                niche="marketing-digital",
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("customer graph", scope={"project_id": "proj-001"}, limit=5)
    )

    assert len(results) == 1
    assert results[0].why_matched == "lexical:title_or_content"


def test_search_with_noop_reranker_preserves_existing_order(tmp_path: Path) -> None:
    """Default reranking should not perturb the canonical Retrieval v1 ordering."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    run_async(
        store.save_item(
            MemoryItem(
                memory_id=None,
                memory_type="lesson",
                title="Launch checklist",
                content="Coordinate GTM and CRM guardrails.",
                project_id="proj-001",
                brain_id=None,
                niche=None,
                visibility="project",
            )
        )
    )
    run_async(
        store.save_item(
            MemoryItem(
                memory_id=None,
                memory_type="lesson",
                title="Weekly review",
                content="Review the launch brief with the marketing team.",
                project_id="proj-001",
                brain_id=None,
                niche=None,
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("launch", scope={"project_id": "proj-001"}, limit=5)
    )

    assert [result.title for result in results] == ["Launch checklist", "Weekly review"]


def test_search_accepts_optional_reranker_without_changing_callers(
    tmp_path: Path,
) -> None:
    """The public search contract should stay stable when a reranker is injected."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    rerank_calls: list[tuple[str, dict[str, str | None] | None, int, int]] = []

    class StubReranker:
        async def rerank(
            self,
            query: str,
            results: list[MemorySearchResult],
            scope: dict[str, str | None] | None = None,
            limit: int = 10,
        ) -> list[MemorySearchResult]:
            rerank_calls.append((query, scope, limit, len(results)))
            return list(results)

    store = PostgresMemoryStore(database_url, reranker=StubReranker())
    run_async(
        store.save_item(
            MemoryItem(
                memory_id=None,
                memory_type="lesson",
                title="Launch checklist",
                content="Coordinate GTM and CRM guardrails.",
                project_id="proj-001",
                brain_id=None,
                niche=None,
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("launch", scope={"project_id": "proj-001"}, limit=5)
    )

    assert len(results) == 1
    assert rerank_calls == [("launch", {"project_id": "proj-001"}, 5, 1)]


def test_search_accepts_optional_graph_recall_without_changing_callers(
    tmp_path: Path,
) -> None:
    """The public search contract should stay stable when graph recall is injected."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    expand_calls: list[tuple[str, dict[str, str | None] | None, int, int]] = []

    class StubGraphRecall:
        async def expand(
            self,
            query: str,
            results: list[MemorySearchResult],
            scope: dict[str, str | None] | None = None,
            limit: int = 10,
        ) -> list[MemorySearchResult]:
            expand_calls.append((query, scope, limit, len(results)))
            return list(results)

    store = PostgresMemoryStore(database_url, graph_recall=StubGraphRecall())
    run_async(
        store.save_item(
            MemoryItem(
                memory_id=None,
                memory_type="lesson",
                title="Launch checklist",
                content="Coordinate GTM and CRM guardrails.",
                project_id="proj-001",
                brain_id=None,
                niche=None,
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("launch", scope={"project_id": "proj-001"}, limit=5)
    )

    assert len(results) == 1
    assert expand_calls == [("launch", {"project_id": "proj-001"}, 5, 1)]


def test_search_graph_recall_can_append_related_results(tmp_path: Path) -> None:
    """Graph recall should enrich the result set with related memory items."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    seed_memory_id = "memory-seed-001"
    related_memory_id = "memory-related-001"

    related_result = MemorySearchResult(
        memory_id=related_memory_id,
        title="Decision lineage note",
        snippet="linked from launch decision",
        score=0.5,
        memory_type="decision",
        project_id="proj-001",
    )
    store = PostgresMemoryStore(
        database_url,
        graph_recall=StaticMemoryGraphRecallProvider(
            {seed_memory_id: [related_result]}
        ),
    )

    run_async(
        store.save_item(
            MemoryItem(
                memory_id=seed_memory_id,
                memory_type="lesson",
                title="Launch checklist",
                content="Coordinate GTM and CRM guardrails.",
                project_id="proj-001",
                brain_id=None,
                niche=None,
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("launch", scope={"project_id": "proj-001"}, limit=5)
    )

    assert [result.memory_id for result in results] == [
        seed_memory_id,
        related_memory_id,
    ]
    assert results[1].why_matched == "graph:related"


def test_search_graph_recall_respects_project_scope(tmp_path: Path) -> None:
    """Graph recall should not append related memories outside the active project scope."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    seed_memory_id = "memory-seed-002"

    store = PostgresMemoryStore(
        database_url,
        graph_recall=StaticMemoryGraphRecallProvider(
            {
                seed_memory_id: [
                    MemorySearchResult(
                        memory_id="memory-other-project-001",
                        title="Cross-project link",
                        snippet="must stay filtered out",
                        score=0.5,
                        memory_type="decision",
                        project_id="proj-002",
                    ),
                    MemorySearchResult(
                        memory_id="memory-same-project-001",
                        title="Same-project link",
                        snippet="eligible related result",
                        score=0.4,
                        memory_type="decision",
                        project_id="proj-001",
                    ),
                ]
            }
        ),
    )

    run_async(
        store.save_item(
            MemoryItem(
                memory_id=seed_memory_id,
                memory_type="lesson",
                title="Launch checklist",
                content="Coordinate GTM and CRM guardrails.",
                project_id="proj-001",
                brain_id=None,
                niche=None,
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("launch", scope={"project_id": "proj-001"}, limit=5)
    )

    assert [result.memory_id for result in results] == [
        seed_memory_id,
        "memory-same-project-001",
    ]
    assert results[1].why_matched == "graph:related"


def test_search_metadata_graph_recall_reads_persisted_relations(tmp_path: Path) -> None:
    """Metadata graph recall should enrich results from persisted relation IDs."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(
        database_url,
        graph_recall=MetadataMemoryGraphRecallProvider(database_url),
    )

    run_async(
        store.save_item(
            MemoryItem(
                memory_id="memory-seed-metadata-001",
                memory_type="lesson",
                title="Launch checklist",
                content="Coordinate GTM and CRM guardrails.",
                project_id="proj-001",
                brain_id="brain-1",
                niche=None,
                visibility="project",
                metadata={"related_memory_ids": ["memory-related-metadata-001"]},
            )
        )
    )
    run_async(
        store.save_item(
            MemoryItem(
                memory_id="memory-related-metadata-001",
                memory_type="decision",
                title="Decision lineage",
                content="Persisted relation target.",
                project_id="proj-001",
                brain_id="brain-1",
                niche=None,
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("checklist", scope={"project_id": "proj-001"}, limit=5)
    )

    assert [result.memory_id for result in results] == [
        "memory-seed-metadata-001",
        "memory-related-metadata-001",
    ]
    assert results[1].why_matched == "graph:metadata"


def test_search_heuristic_reranker_can_reorder_fused_candidates(tmp_path: Path) -> None:
    """Heuristic reranking should promote stronger title matches over raw vector score."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    lexical_memory_id = "memory-lexical-rr-001"
    semantic_memory_id = "memory-semantic-rr-001"

    class StubVectorCandidateProvider:
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
            assert query == "launch"
            assert scope == {"project_id": "proj-001"}
            assert limit == 5
            return [VectorCandidate(memory_id=semantic_memory_id, score=3.0)]

    baseline_store = PostgresMemoryStore(
        database_url,
        vector_provider=StubVectorCandidateProvider(),
    )
    reranked_store = PostgresMemoryStore(
        database_url,
        vector_provider=StubVectorCandidateProvider(),
        reranker=HeuristicMemoryReranker(),
    )

    run_async(
        baseline_store.save_item(
            MemoryItem(
                memory_id=lexical_memory_id,
                memory_type="lesson",
                title="Launch note",
                content="Brief summary for release prep.",
                project_id="proj-001",
                brain_id=None,
                niche=None,
                visibility="project",
            )
        )
    )
    run_async(
        baseline_store.save_item(
            MemoryItem(
                memory_id=semantic_memory_id,
                memory_type="lesson",
                title="Release summary",
                content="Semantic note about release planning and rollout.",
                project_id="proj-001",
                brain_id=None,
                niche=None,
                visibility="project",
            )
        )
    )

    baseline_results = run_async(
        baseline_store.search("launch", scope={"project_id": "proj-001"}, limit=5)
    )
    reranked_results = run_async(
        reranked_store.search("launch", scope={"project_id": "proj-001"}, limit=5)
    )

    assert baseline_results[0].memory_id == semantic_memory_id
    assert reranked_results[0].memory_id == lexical_memory_id


def test_list_recent_orders_project_items_newest_first(tmp_path: Path) -> None:
    """Recent listing should return only project-scoped items in descending order."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    first = run_async(
        store.save_item(
            MemoryItem(
                memory_type="pattern",
                title="First lesson",
                content="First content.",
                project_id="proj-001",
                visibility="project",
            )
        )
    )
    second = run_async(
        store.save_item(
            MemoryItem(
                memory_type="pattern",
                title="Second lesson",
                content="Second content.",
                project_id="proj-001",
                visibility="project",
            )
        )
    )

    items = run_async(store.list_recent("proj-001", limit=10))

    assert [item.memory_id for item in items] == [second.memory_id, first.memory_id]


def test_save_session_summary_persists_dedicated_session_record(tmp_path: Path) -> None:
    """Session summaries should persist into the dedicated session continuity table."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    run_async(
        store.save_session_summary(
            session_id="session-123",
            summary="Closed auth migration and stabilized strategy vault projections.",
            project_id="proj-001",
            metadata={"objective": "memory-layer-v1"},
        )
    )

    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        record = session.scalar(
            select(MemorySessionRecord).where(
                MemorySessionRecord.session_id == "session-123"
            )
        )

    assert record is not None
    assert record.project_id == "proj-001"
    assert record.summary.startswith("Closed auth migration")
    assert record.metadata_json == {"objective": "memory-layer-v1"}


def test_save_session_summary_rejects_non_json_metadata(tmp_path: Path) -> None:
    """Session summaries should reject non-JSON metadata payloads."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    with pytest.raises(ValueError, match="Metadata values must be JSON-compatible"):
        run_async(
            store.save_session_summary(
                session_id="session-456",
                summary="Bad metadata payload",
                project_id="proj-001",
                metadata={"objective": object()},
            )
        )


def test_save_preference_persists_dedicated_preference_record(tmp_path: Path) -> None:
    """Preferences should persist outside the generic memory items table."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    run_async(
        store.save_preference(
            key="output_verbosity",
            value={"level": "brief"},
            scope="personal",
            project_id="proj-001",
        )
    )

    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        record = session.scalar(
            select(MemoryPreferenceRecord).where(
                MemoryPreferenceRecord.key == "output_verbosity"
            )
        )

    assert record is not None
    assert record.scope == "personal"
    assert record.project_id == "proj-001"
    assert record.value_json == {"level": "brief"}


def test_save_preference_rejects_non_json_compatible_values(tmp_path: Path) -> None:
    """Preferences should fail fast on unsupported value objects."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    with pytest.raises(ValueError, match="JSON-compatible"):
        run_async(
            store.save_preference(
                key="output_verbosity",
                value=object(),
                scope="personal",
                project_id="proj-001",
            )
        )


def test_save_item_rejects_non_json_metadata(tmp_path: Path) -> None:
    """Memory items should reject non-JSON metadata payloads."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    with pytest.raises(ValueError, match="Metadata values must be JSON-compatible"):
        run_async(
            store.save_item(
                MemoryItem(
                    memory_type="lesson",
                    title="Bad metadata",
                    content="bad",
                    project_id="proj-001",
                    visibility="project",
                    metadata={"objective": object()},
                )
            )
        )


def run_async(awaitable: Awaitable[T]) -> T:
    """Run an async store operation from sync unit tests."""
    import asyncio

    return asyncio.run(awaitable)
