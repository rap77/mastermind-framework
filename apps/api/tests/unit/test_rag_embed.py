"""
Unit tests for mastermind_cli.rag.embed (Phase 20B).

Tests:
- 20.12: encode(['hello world']) returns list with one 768-float element
- 20.13: compute_hash('text') returns 64-char hex string (SHA-256)
- 20.16: from mastermind_cli.rag import similarity_search raises no ImportError
"""

from __future__ import annotations

import pytest

from mastermind_cli.rag import similarity_search  # noqa: F401 (import test)
from mastermind_cli.rag.embed import compute_hash, encode


class _DummySentenceTransformer:
    """Lightweight stand-in for the external embedding model."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def encode(
        self, texts: list[str], normalize_embeddings: bool = True
    ) -> list[list[float]]:
        return [[float(index) for index in range(768)] for _ in texts]


@pytest.fixture(autouse=True)
def _stub_sentence_transformer(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid network-backed Hugging Face model loads in unit tests."""
    monkeypatch.setattr(
        "mastermind_cli.rag.embed.SentenceTransformer", _DummySentenceTransformer
    )


def test_encode_returns_768_floats() -> None:
    """20.12: encode(['hello world']) returns list with one 768-float element."""
    result = encode(["hello world"])

    assert isinstance(result, list), "encode must return a list"
    assert len(result) == 1, "encode(['hello world']) must return exactly 1 vector"

    vector = result[0]
    assert isinstance(vector, list), "Each element must be a list of floats"
    assert len(vector) == 768, f"Vector must have 768 dimensions, got {len(vector)}"
    assert all(
        isinstance(v, float) for v in vector
    ), "All vector elements must be float"


def test_encode_multiple_texts() -> None:
    """encode handles multiple texts, returning one vector per text."""
    texts = ["hello world", "another chunk", "third text"]
    result = encode(texts)

    assert len(result) == 3
    for vec in result:
        assert len(vec) == 768


def test_encode_empty_raises() -> None:
    """encode raises ValueError on empty input."""
    import pytest

    with pytest.raises(ValueError, match="non-empty"):
        encode([])


def test_compute_hash_returns_64_char_hex() -> None:
    """20.13: compute_hash('text') returns 64-char lowercase hex string."""
    result = compute_hash("text")

    assert isinstance(result, str), "compute_hash must return a string"
    assert len(result) == 64, f"SHA-256 hex must be 64 chars, got {len(result)}"
    # Validate it's a valid hex string
    int(result, 16)  # raises ValueError if not valid hex


def test_compute_hash_is_deterministic() -> None:
    """Same input always produces the same hash."""
    assert compute_hash("hello") == compute_hash("hello")


def test_compute_hash_different_inputs_differ() -> None:
    """Different inputs produce different hashes."""
    assert compute_hash("hello") != compute_hash("world")


def test_rag_import_works() -> None:
    """20.16: from mastermind_cli.rag import similarity_search raises no ImportError."""
    # Import already done at module level — if we reach this line, it passed
    assert callable(similarity_search)
