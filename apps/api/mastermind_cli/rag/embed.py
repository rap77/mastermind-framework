"""
RAG embedding utilities — Phase 20B.

Provides model loading, text encoding, and SHA256 hash computation for
chunk deduplication before insertion into brain_embeddings.

Usage:
    from mastermind_cli.rag.embed import load_model, encode, compute_hash

    model = load_model()
    vectors = encode(["hello world", "another chunk"])
    h = compute_hash("hello world")
"""

from __future__ import annotations

import hashlib
import threading
from functools import lru_cache

from sentence_transformers import SentenceTransformer

_DEFAULT_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
_model_lock = threading.Lock()


@lru_cache(maxsize=4)
def load_model(model_name: str = _DEFAULT_MODEL_NAME) -> SentenceTransformer:
    """Load (and cache) a SentenceTransformer model.

    The model is cached per model_name so repeated calls with the same name
    return the same object without reloading weights.

    Args:
        model_name: HuggingFace model identifier.  Defaults to
            ``sentence-transformers/all-mpnet-base-v2`` (768 dimensions).

    Returns:
        Loaded SentenceTransformer instance.
    """
    with _model_lock:
        return SentenceTransformer(model_name)


def encode(
    texts: list[str], model_name: str = _DEFAULT_MODEL_NAME
) -> list[list[float]]:
    """Encode a list of texts into embedding vectors.

    Args:
        texts: Non-empty list of strings to embed.
        model_name: HuggingFace model identifier (forwarded to :func:`load_model`).

    Returns:
        List of float vectors, one per input text.  Each vector has 768
        dimensions when using the default all-mpnet-base-v2 model.

    Raises:
        ValueError: If ``texts`` is empty.
    """
    if not texts:
        raise ValueError("texts must be a non-empty list")

    model = load_model(model_name)
    embeddings = model.encode(texts, normalize_embeddings=True)
    return [list(map(float, vec)) for vec in embeddings]


def compute_hash(text: str) -> str:
    """Compute the SHA-256 hex digest of a string.

    Used to generate ``chunk_hash`` values for deduplication.  Two identical
    chunks will always produce the same hash, enabling idempotent inserts via
    the UNIQUE constraint on ``brain_embeddings.chunk_hash``.

    Args:
        text: Raw chunk text.

    Returns:
        64-character lowercase hexadecimal SHA-256 digest.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
