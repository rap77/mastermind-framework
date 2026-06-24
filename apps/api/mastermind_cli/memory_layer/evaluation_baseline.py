"""Reusable deterministic retrieval baseline fixtures."""

from __future__ import annotations

from .contracts import MemoryStore
from .models import MemoryItem, RetrievalEvalCase


BASELINE_PROJECT_ID = "proj-memory"


def build_retrieval_baseline_fixture() -> list[MemoryItem]:
    """Return the fixed corpus used by the offline retrieval baseline."""
    return [
        MemoryItem(
            memory_id="mem-marketing",
            memory_type="decision",
            title="Marketing launch checklist",
            content="Coordinate attribution, CRM sync, and CAC guardrails.",
            project_id=BASELINE_PROJECT_ID,
            brain_id="brain-01-product-strategy",
            niche="marketing-digital",
            visibility="project",
            source_kind=None,
            source_ref=None,
        ),
        MemoryItem(
            memory_id="mem-investments",
            memory_type="lesson",
            title="Investment rebalance note",
            content="Review portfolio risk bands every Friday before rebalance.",
            project_id=BASELINE_PROJECT_ID,
            brain_id="brain-07-growth-data",
            niche="investments",
            visibility="project",
            source_kind=None,
            source_ref=None,
        ),
        MemoryItem(
            memory_id="mem-auth",
            memory_type="pattern",
            title="Recurring auth drift",
            content="Refresh token handling breaks when JWT clocks drift.",
            project_id=BASELINE_PROJECT_ID,
            brain_id="brain-06-qa-devops",
            niche="software-development",
            visibility="project",
            source_kind=None,
            source_ref=None,
        ),
    ]


def build_retrieval_baseline_cases() -> list[RetrievalEvalCase]:
    """Return fixed retrieval eval cases with expected hits."""
    return [
        RetrievalEvalCase(
            case_id="baseline-marketing-crm",
            query="marketing crm",
            expected_memory_ids=["mem-marketing"],
        ),
        RetrievalEvalCase(
            case_id="baseline-investment-risk",
            query="risk rebalance",
            expected_memory_ids=["mem-investments"],
            scope={"niche": "investments"},
        ),
        RetrievalEvalCase(
            case_id="baseline-auth-drift",
            query="jwt drift",
            expected_memory_ids=["mem-auth"],
            scope={"memory_type": "pattern"},
        ),
    ]


async def seed_retrieval_baseline_fixture(store: MemoryStore) -> None:
    """Persist the fixed retrieval baseline corpus into a memory store."""
    for item in build_retrieval_baseline_fixture():
        await store.save_item(item)
