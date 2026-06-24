"""Memory Layer domain models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator


class MemoryItem(BaseModel):
    """Canonical memory item stored by MasterMind."""

    memory_id: str | None = Field(None, description="Unique memory identifier.")
    memory_type: str = Field(..., min_length=1, description="Semantic memory type.")
    title: str = Field(..., min_length=1, description="Short human-readable title.")
    content: str = Field(..., min_length=1, description="Full memory content.")
    project_id: str | None = Field(None, description="Optional related project ID.")
    brain_id: str | None = Field(None, description="Optional source brain ID.")
    niche: str | None = Field(None, description="Optional niche classification.")
    visibility: str = Field(..., min_length=1, description="Visibility scope.")
    source_kind: str | None = Field(None, description="Origin category for the item.")
    source_ref: str | None = Field(None, description="Origin reference identifier.")
    tags: list[str] = Field(
        default_factory=list, description="Search and routing tags."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata for niche-specific extensions.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp in UTC.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp in UTC.",
    )

    @field_validator("title", "content", mode="before")
    @classmethod
    def _strip_required_text(cls, value: Any) -> Any:
        """Trim required text fields before validation."""
        if isinstance(value, str):
            return value.strip()
        return value


class MemorySearchResult(BaseModel):
    """Ranked search result returned by a memory backend."""

    memory_id: str = Field(..., description="Unique memory identifier.")
    title: str = Field(..., min_length=1, description="Memory item title.")
    snippet: str = Field(..., description="Short content excerpt.")
    score: float = Field(..., description="Backend relevance score.")
    memory_type: str = Field(..., min_length=1, description="Semantic memory type.")
    project_id: str | None = Field(None, description="Optional related project ID.")
    brain_id: str | None = Field(None, description="Optional related brain ID.")
    why_matched: str | None = Field(None, description="Explanation of the match.")
    source_ref: str | None = Field(None, description="Origin reference identifier.")


class VectorCandidate(BaseModel):
    """Ranked semantic candidate returned by a vector retrieval seam."""

    memory_id: str = Field(..., description="Unique memory identifier.")
    score: float = Field(..., description="Normalized vector relevance score.")


class MemoryContextBundle(BaseModel):
    """Structured context bundle assembled from memory search results."""

    items: list[MemorySearchResult] = Field(
        default_factory=list,
        description="Retrieved memory results.",
    )
    summary: str = Field(..., description="Condensed description of the context.")
    open_gaps: list[str] = Field(
        default_factory=list,
        description="Known gaps or missing context signals.",
    )
    applied_scopes: dict[str, str | None] = Field(
        default_factory=dict,
        description="Scopes applied while building this context.",
    )


class MemoryIndexPayload(BaseModel):
    """Canonical payload prepared for semantic indexing."""

    memory_id: str = Field(..., description="Unique memory identifier.")
    memory_type: str = Field(..., min_length=1, description="Semantic memory type.")
    title: str = Field(..., min_length=1, description="Memory item title.")
    content: str = Field(..., min_length=1, description="Memory item content.")
    tags: list[str] = Field(default_factory=list, description="Search tags.")
    project_id: str | None = Field(None, description="Optional related project ID.")
    brain_id: str | None = Field(None, description="Optional related brain ID.")
    niche: str | None = Field(None, description="Optional niche classification.")
    source_ref: str | None = Field(None, description="Origin reference identifier.")
    embedding_text: str = Field(..., min_length=1, description="Text to embed.")


class RetrievalEvalCase(BaseModel):
    """One deterministic retrieval eval expectation."""

    case_id: str = Field(..., min_length=1, description="Stable case identifier.")
    query: str = Field(..., min_length=1, description="Retrieval query to execute.")
    expected_memory_ids: list[str] = Field(
        default_factory=list,
        description="Memory IDs that must appear in the result set.",
    )
    scope: dict[str, str | None] = Field(
        default_factory=dict,
        description="Additional scope filters merged with the project scope.",
    )


class RetrievalEvalCaseResult(BaseModel):
    """Outcome for one retrieval eval case."""

    case_id: str = Field(..., min_length=1, description="Stable case identifier.")
    query: str = Field(..., min_length=1, description="Executed retrieval query.")
    passed: bool = Field(..., description="Whether the case passed.")
    expected_memory_ids: list[str] = Field(
        default_factory=list,
        description="Memory IDs required by the case.",
    )
    matched_memory_ids: list[str] = Field(
        default_factory=list,
        description="Actual ranked memory IDs returned by search.",
    )
    scope: dict[str, str | None] = Field(
        default_factory=dict,
        description="Effective scope used for the search.",
    )


class RetrievalEvalReport(BaseModel):
    """Aggregate scorecard for an offline retrieval baseline."""

    total_cases: int = Field(..., ge=0, description="Number of executed cases.")
    passed_cases: int = Field(..., ge=0, description="Number of passing cases.")
    pass_rate: float = Field(..., ge=0.0, le=1.0, description="Passing ratio.")
    cases: list[RetrievalEvalCaseResult] = Field(
        default_factory=list,
        description="Per-case retrieval outcomes.",
    )
