"""
RAG (Retrieval-Augmented Generation) module — Phase 20B / Phase 21.

Public API:
    similarity_search   — cosine-similarity search over brain_embeddings
    encode              — encode texts into 768-dim vectors
    compute_hash        — SHA-256 hash for chunk deduplication
    load_model          — load (and cache) a SentenceTransformer model
    RAGContextBuilder   — build [RETRIEVED CONTEXT] block for system prompts
"""

from .context_builder import RAGContextBuilder
from .embed import compute_hash, encode, load_model
from .search import similarity_search

__all__ = [
    "RAGContextBuilder",
    "similarity_search",
    "encode",
    "compute_hash",
    "load_model",
]
