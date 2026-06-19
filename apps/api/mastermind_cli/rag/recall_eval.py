"""Offline Recall@K evaluation helper for the RAG evaluation gate."""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

import asyncpg
import click

from .search import similarity_search

_DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "",
)
_REPO_ROOT = Path(__file__).parents[4]
_DEFAULT_EVAL_PAIRS_PATH = (
    _REPO_ROOT / "apps/api/tests/rag/fixtures/brain1_recall_pairs.json"
)
_DEFAULT_OUTPUT_PATH = (
    _REPO_ROOT
    / ".mm-flow/planning/changes/rag-evaluation-gate/artifacts/brain1-recall-results.json"
)
_DEFAULT_BRAIN_ID = "brain-01-product-strategy"
_DEFAULT_COLLECTION = "domain_knowledge"
_DEFAULT_LIMIT = 5
_RECALL_THRESHOLD = 0.70


@dataclass(frozen=True)
class RecallEvalPair:
    """One labeled retrieval-evaluation query."""

    query: str
    relevant_chunk_refs: list[str]


@dataclass(frozen=True)
class RecallPairResult:
    """Per-query evaluation outcome."""

    query: str
    relevant_chunk_refs: list[str]
    retrieved_chunk_refs: list[str]
    hit: bool


@dataclass(frozen=True)
class RecallResult:
    """Aggregate Recall@K result for one retrieval evaluation run."""

    brain_id: str
    collection: str
    limit: int
    threshold: float
    hits: int
    total: int
    recall_at_k: float
    passes_sli: bool
    eval_pairs_path: str
    measured_at: str
    pair_results: list[RecallPairResult]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        payload = asdict(self)
        payload["pair_results"] = [asdict(result) for result in self.pair_results]
        return payload


def load_eval_pairs(eval_pairs_path: Path) -> list[RecallEvalPair]:
    """Load labeled retrieval-evaluation pairs from JSON.

    Args:
        eval_pairs_path: JSON file containing either a top-level list of pairs or
            an object with a ``pairs`` list.

    Returns:
        Parsed evaluation pairs.

    Raises:
        ValueError: If the JSON shape is invalid or no valid pairs are present.
    """
    raw_data = json.loads(eval_pairs_path.read_text(encoding="utf-8"))
    if isinstance(raw_data, dict):
        raw_pairs = raw_data.get("pairs")
    else:
        raw_pairs = raw_data

    if not isinstance(raw_pairs, list):
        raise ValueError(
            f"Evaluation pairs in {eval_pairs_path} must be a list or object with 'pairs'."
        )

    pairs: list[RecallEvalPair] = []
    for index, raw_pair in enumerate(raw_pairs, start=1):
        if not isinstance(raw_pair, dict):
            raise ValueError(
                f"Evaluation pair #{index} in {eval_pairs_path} must be an object."
            )

        query = raw_pair.get("query")
        relevant_chunk_refs = raw_pair.get("relevant_chunk_refs")

        if not isinstance(query, str) or not query.strip():
            raise ValueError(
                f"Evaluation pair #{index} in {eval_pairs_path} has an invalid 'query'."
            )
        if not isinstance(relevant_chunk_refs, list) or not relevant_chunk_refs:
            raise ValueError(
                f"Evaluation pair #{index} in {eval_pairs_path} must declare non-empty 'relevant_chunk_refs'."
            )

        normalized_refs = [
            str(ref).strip() for ref in relevant_chunk_refs if str(ref).strip()
        ]
        if not normalized_refs:
            raise ValueError(
                f"Evaluation pair #{index} in {eval_pairs_path} has no usable chunk refs."
            )

        pairs.append(
            RecallEvalPair(
                query=query.strip(),
                relevant_chunk_refs=normalized_refs,
            )
        )

    if not pairs:
        raise ValueError(f"No evaluation pairs found in {eval_pairs_path}.")

    return pairs


async def evaluate_recall(
    conn: asyncpg.Connection,
    brain_id: str = _DEFAULT_BRAIN_ID,
    collection: str = _DEFAULT_COLLECTION,
    eval_pairs_path: Path = _DEFAULT_EVAL_PAIRS_PATH,
    limit: int = _DEFAULT_LIMIT,
    output_path: Path | None = _DEFAULT_OUTPUT_PATH,
) -> RecallResult:
    """Evaluate Recall@K for one brain/collection using labeled pairs.

    Args:
        conn: Open asyncpg connection used for retrieval queries.
        brain_id: Brain identifier to evaluate.
        collection: Collection name (`domain_knowledge` or `project_memory`).
        eval_pairs_path: JSON file with manual evaluation pairs.
        limit: Retrieval depth `K`.
        output_path: Optional JSON output report path. When ``None``, no file is
            written.

    Returns:
        Aggregate recall result.
    """
    pairs = load_eval_pairs(eval_pairs_path)
    pair_results: list[RecallPairResult] = []
    hits = 0

    for pair in pairs:
        search_results = await similarity_search(
            conn,
            brain_id=brain_id,
            collection=collection,
            query_text=pair.query,
            limit=limit,
        )
        retrieved_chunk_refs = [
            str(row.get("source_ref")).strip()
            for row in search_results
            if row.get("source_ref") is not None
        ]
        hit = bool(set(retrieved_chunk_refs).intersection(pair.relevant_chunk_refs))
        if hit:
            hits += 1

        pair_results.append(
            RecallPairResult(
                query=pair.query,
                relevant_chunk_refs=pair.relevant_chunk_refs,
                retrieved_chunk_refs=retrieved_chunk_refs,
                hit=hit,
            )
        )

    total = len(pair_results)
    recall_at_k = round(hits / total, 4) if total else 0.0
    result = RecallResult(
        brain_id=brain_id,
        collection=collection,
        limit=limit,
        threshold=_RECALL_THRESHOLD,
        hits=hits,
        total=total,
        recall_at_k=recall_at_k,
        passes_sli=recall_at_k >= _RECALL_THRESHOLD,
        eval_pairs_path=str(eval_pairs_path),
        measured_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        pair_results=pair_results,
    )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

    return result


async def _run_cli(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the CLI flow and return the JSON payload."""
    if not args.database_url:
        raise ValueError(
            "database_url is required via --database-url or DATABASE_URL environment variable"
        )
    conn = await asyncpg.connect(args.database_url)
    try:
        result = await evaluate_recall(
            conn,
            brain_id=args.brain_id,
            collection=args.collection,
            eval_pairs_path=Path(args.eval_pairs_path),
            limit=args.limit,
            output_path=Path(args.output_path) if args.output_path else None,
        )
    finally:
        await conn.close()

    return result.to_dict()


def main() -> None:
    """Run the offline Recall@K evaluator from the CLI."""
    parser = argparse.ArgumentParser(
        description="Evaluate Brain #1 retrieval Recall@K for the RAG gate."
    )
    parser.add_argument("--database-url", default=_DEFAULT_DATABASE_URL)
    parser.add_argument("--brain-id", default=_DEFAULT_BRAIN_ID)
    parser.add_argument("--collection", default=_DEFAULT_COLLECTION)
    parser.add_argument("--eval-pairs-path", default=str(_DEFAULT_EVAL_PAIRS_PATH))
    parser.add_argument("--limit", type=int, default=_DEFAULT_LIMIT)
    parser.add_argument("--output-path", default=str(_DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    click.echo(json.dumps(asyncio.run(_run_cli(args)), indent=2))


if __name__ == "__main__":
    main()
