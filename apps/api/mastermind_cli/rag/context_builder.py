"""
RAG Context Builder — Phase 21.

Retrieves top-K chunks from two collections (domain_knowledge and
project_memory) and formats them as a structured [RETRIEVED CONTEXT] block
to be appended to a brain's system prompt before each LLM call.

Usage:
    from mastermind_cli.rag.context_builder import RAGContextBuilder

    builder = RAGContextBuilder(conn)
    context = await builder.build("brain-01-product", "product discovery strategy")
    if context:
        system_prompt += "\\n\\n" + context
"""

from __future__ import annotations

import asyncpg

from .search import similarity_search

_DOMAIN_LIMIT = 5
_MEMORY_LIMIT = 3


class RAGContextBuilder:
    """Builds a structured [RETRIEVED CONTEXT] block for brain system prompts.

    Retrieves the top-K most similar chunks from two pgvector collections:
    - ``domain_knowledge``: distilled expert knowledge from source files
    - ``project_memory``: persistent cross-session brain feed entries

    If a collection is empty (no rows for the given brain_id), its subsection
    is omitted from the output entirely — no placeholder text is emitted.
    If both collections are empty, an empty string is returned so the caller
    can skip appending to the system prompt.

    Args:
        conn: Open asyncpg connection.  The caller owns the connection lifecycle;
              this class does NOT close it.

    Example:
        >>> builder = RAGContextBuilder(conn)
        >>> ctx = await builder.build("brain-01-product", "continuous discovery")
        >>> assert ctx.startswith("[RETRIEVED CONTEXT]") or ctx == ""
    """

    def __init__(self, conn: asyncpg.Connection) -> None:
        self._conn = conn

    async def build(self, brain_id: str, query: str) -> str:
        """Retrieve and format context chunks for *brain_id* matching *query*.

        Args:
            brain_id: Brain identifier used to filter ``brain_embeddings`` rows.
            query: Natural-language query to embed and search against.

        Returns:
            A non-empty [RETRIEVED CONTEXT] block string when at least one
            collection returns results; an empty string ``""`` when both
            collections are empty or the query is blank.
        """
        if not query.strip():
            return ""

        domain_results = await similarity_search(
            self._conn, brain_id, "domain_knowledge", query, limit=_DOMAIN_LIMIT
        )
        memory_results = await similarity_search(
            self._conn, brain_id, "project_memory", query, limit=_MEMORY_LIMIT
        )

        if not domain_results and not memory_results:
            return ""

        lines: list[str] = ["[RETRIEVED CONTEXT]"]

        if domain_results:
            lines.append(f"--- domain_knowledge (top-{_DOMAIN_LIMIT}) ---")
            for i, row in enumerate(domain_results, start=1):
                score = row["score"]
                source = row["source_ref"]
                text = row["chunk_text"]
                lines.append(f"[{i}] (score: {score:.2f}) [source: {source}] {text}")

        if memory_results:
            lines.append(f"--- project_memory (top-{_MEMORY_LIMIT}) ---")
            for i, row in enumerate(memory_results, start=1):
                score = row["score"]
                source = row["source_ref"]
                text = row["chunk_text"]
                lines.append(f"[{i}] (score: {score:.2f}) [source: {source}] {text}")

        lines.append("[END RETRIEVED CONTEXT]")
        return "\n".join(lines)
