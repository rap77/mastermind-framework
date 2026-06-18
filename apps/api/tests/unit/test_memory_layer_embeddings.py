"""Tests for embedding helpers in the first-party memory layer."""

from __future__ import annotations

import pytest

from mastermind_cli.memory_layer.embeddings import (
    NoopEmbeddingProvider,
    OllamaEmbeddingProvider,
    build_memory_embedding_text,
    build_memory_index_payload,
    create_embedding_provider,
)
from mastermind_cli.memory_layer.models import MemoryItem


def test_build_memory_embedding_text_includes_core_fields() -> None:
    """Embedding text should include the semantic fields that matter for recall."""
    item = MemoryItem(
        memory_id="mem-1",
        memory_type="decision",
        title="Use agnostic memory indexing",
        content="Keep canonical memory independent from the vector backend.",
        niche="software-development",
        visibility="project",
        tags=["decision", "retrieval"],
    )

    text = build_memory_embedding_text(item)

    assert "type: decision" in text
    assert "title: Use agnostic memory indexing" in text
    assert "content: Keep canonical memory independent from the vector backend." in text
    assert "tags: decision, retrieval" in text
    assert "niche: software-development" in text


def test_build_memory_index_payload_projects_canonical_memory_item() -> None:
    """Index payloads should preserve the canonical memory identity and text."""
    item = MemoryItem(
        memory_id="mem-2",
        memory_type="lesson",
        title="Hybrid retrieval note",
        content="Lexical retrieval should remain deterministic before reranking.",
        project_id="proj-001",
        brain_id="brain-07-growth-data",
        visibility="project",
    )

    payload = build_memory_index_payload(item)

    assert payload.memory_id == "mem-2"
    assert payload.project_id == "proj-001"
    assert payload.brain_id == "brain-07-growth-data"
    assert "Hybrid retrieval note" in payload.embedding_text


@pytest.mark.asyncio
async def test_noop_embedding_provider_returns_no_embeddings() -> None:
    """The default provider should keep semantic generation disabled."""
    provider = NoopEmbeddingProvider()

    assert await provider.embed_texts(["hello"]) == []


def test_create_embedding_provider_defaults_to_noop() -> None:
    """The default embedding backend should remain disabled."""
    provider = create_embedding_provider()

    assert isinstance(provider, NoopEmbeddingProvider)


@pytest.mark.asyncio
async def test_sentence_transformer_embedding_provider_delegates_to_rag_encode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The sentence-transformers provider should reuse the existing RAG encoder."""
    captured: dict[str, object] = {}

    def fake_encode(texts: list[str], model_name: str) -> list[list[float]]:
        captured["texts"] = texts
        captured["model_name"] = model_name
        return [[0.1, 0.2]]

    monkeypatch.setattr("mastermind_cli.memory_layer.embeddings.encode", fake_encode)
    provider = create_embedding_provider(
        "sentence-transformers",
        model_name="sentence-transformers/test-model",
    )

    result = await provider.embed_texts(["customer graph"])

    assert result == [[0.1, 0.2]]
    assert captured["texts"] == ["customer graph"]
    assert captured["model_name"] == "sentence-transformers/test-model"


@pytest.mark.asyncio
async def test_ollama_embedding_provider_calls_local_embed_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The Ollama provider should call the local embed API and normalize the response."""
    captured: dict[str, object] = {}

    class FakeResponse:
        def read(self) -> bytes:
            return b'{"embeddings": [[0.1, 0.2, 0.3]]}'

    def fake_urlopen(request_obj: object) -> FakeResponse:
        captured["url"] = request_obj.full_url
        captured["body"] = request_obj.data.decode("utf-8")
        return FakeResponse()

    monkeypatch.setattr(
        "mastermind_cli.memory_layer.embeddings.request.urlopen", fake_urlopen
    )
    provider = create_embedding_provider(
        "ollama",
        model_name="mxbai-embed-large",
        base_url="http://localhost:11434",
    )

    result = await provider.embed_texts(["customer graph"])

    assert isinstance(provider, OllamaEmbeddingProvider)
    assert result == [[0.1, 0.2, 0.3]]
    assert captured["url"] == "http://localhost:11434/api/embed"
    assert '"model": "mxbai-embed-large"' in str(captured["body"])


def test_create_embedding_provider_rejects_unknown_backend() -> None:
    """Unknown embedding backends should fail validation early."""
    with pytest.raises(ValueError, match="Unsupported embedding backend"):
        create_embedding_provider("mystery")
