"""Embedding helpers for semantic memory indexing."""

from __future__ import annotations

import json
from urllib import request

from mastermind_cli.rag.embed import encode

from .contracts import EmbeddingProvider
from .models import MemoryIndexPayload, MemoryItem


def build_memory_embedding_text(item: MemoryItem) -> str:
    """Build a stable embedding string from a canonical memory item."""
    lines = [
        f"type: {item.memory_type}",
        f"title: {item.title}",
        f"content: {item.content}",
    ]
    if item.tags:
        lines.append(f"tags: {', '.join(item.tags)}")
    if item.niche:
        lines.append(f"niche: {item.niche}")
    return "\n".join(lines)


def build_memory_index_payload(item: MemoryItem) -> MemoryIndexPayload:
    """Project a canonical memory item into the indexing payload shape."""
    return MemoryIndexPayload(
        memory_id=item.memory_id or "",
        memory_type=item.memory_type,
        title=item.title,
        content=item.content,
        tags=list(item.tags),
        project_id=item.project_id,
        brain_id=item.brain_id,
        niche=item.niche,
        source_ref=item.source_ref,
        embedding_text=build_memory_embedding_text(item),
    )


class NoopEmbeddingProvider:
    """Embedding provider that deliberately returns no embeddings."""

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Return no embeddings when semantic indexing is disabled."""
        del texts
        return []


class SentenceTransformerEmbeddingProvider:
    """Embedding provider backed by the existing local sentence-transformers flow."""

    def __init__(
        self, model_name: str = "sentence-transformers/all-mpnet-base-v2"
    ) -> None:
        """Store the model name used for embedding generation."""
        self._model_name = model_name

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using the existing RAG encoder helper."""
        return encode(texts, model_name=self._model_name)


class OllamaEmbeddingProvider:
    """Embedding provider backed by a local Ollama instance."""

    def __init__(
        self,
        model_name: str = "mxbai-embed-large",
        *,
        base_url: str = "http://localhost:11434",
    ) -> None:
        """Store the Ollama host and model used for embedding generation."""
        self._model_name = model_name
        self._base_url = base_url.rstrip("/")

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings by calling the local Ollama embeddings API."""
        embeddings: list[list[float]] = []
        for text in texts:
            payload = json.dumps(
                {
                    "model": self._model_name,
                    "input": text,
                }
            ).encode("utf-8")
            response = request.urlopen(
                request.Request(
                    f"{self._base_url}/api/embed",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
            )
            raw_body = response.read().decode("utf-8")
            data = json.loads(raw_body)

            if "embeddings" in data:
                values = data["embeddings"]
                if isinstance(values, list) and values and isinstance(values[0], list):
                    embeddings.extend(values)
                    continue
            if "embedding" in data:
                embeddings.append(data["embedding"])
                continue

            raise ValueError(
                f"Ollama embedding response for model {self._model_name!r} did not "
                "contain 'embedding' or 'embeddings'."
            )
        return embeddings


def create_embedding_provider(
    backend: str | None = None,
    *,
    model_name: str = "sentence-transformers/all-mpnet-base-v2",
    base_url: str = "http://localhost:11434",
) -> EmbeddingProvider:
    """Create an embedding provider from a small backend selector."""
    normalized = (backend or "none").strip().lower()

    if normalized in {"", "none", "off", "disabled"}:
        return NoopEmbeddingProvider()
    if normalized == "sentence-transformers":
        return SentenceTransformerEmbeddingProvider(model_name=model_name)
    if normalized == "ollama":
        return OllamaEmbeddingProvider(model_name=model_name, base_url=base_url)

    raise ValueError(
        f"Unsupported embedding backend: {backend!r}. "
        "Usa none, sentence-transformers u ollama."
    )


__all__ = [
    "EmbeddingProvider",
    "NoopEmbeddingProvider",
    "OllamaEmbeddingProvider",
    "SentenceTransformerEmbeddingProvider",
    "build_memory_embedding_text",
    "build_memory_index_payload",
    "create_embedding_provider",
]
