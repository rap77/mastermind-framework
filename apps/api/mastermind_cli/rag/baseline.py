"""
OEC Baseline Calculator — Phase 20C.

Reads the last N experience_records for brain-01 from PostgreSQL (records
without RAG enabled — i.e. pre-RAG baseline), computes the mean quality_score,
and writes the result to tasks/rag-baseline.json.

The OEC target is the minimum acceptable quality improvement after RAG is
enabled.  Default: 0.75 (75% mean quality score).

Usage:
    uv run python -m mastermind_cli.rag.baseline
    DATABASE_URL=postgresql://... uv run python -m mastermind_cli.rag.baseline
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path

import asyncpg

log = logging.getLogger(__name__)

_DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:devpassword@localhost:5434/mastermind_bd",
)
_BASELINE_PATH = Path(__file__).parents[4] / "tasks" / "rag-baseline.json"
_BRAIN_ID = "brain-01"
_N_RECORDS = 100
_OEC_TARGET = 0.75


async def compute_baseline(
    database_url: str = _DEFAULT_DATABASE_URL,
    brain_id: str = _BRAIN_ID,
    limit: int = _N_RECORDS,
    oec_target: float = _OEC_TARGET,
    output_path: Path = _BASELINE_PATH,
) -> dict[str, object]:
    """Compute the pre-RAG quality baseline for a brain.

    Reads the last *limit* experience_records for *brain_id* from PostgreSQL,
    filters to rows where ``quality_score IS NOT NULL`` (records without RAG
    context), then computes the mean quality_score.

    Args:
        database_url: PostgreSQL DSN to connect to.
        brain_id: Brain identifier to evaluate (default: ``"brain-01"``).
        limit: Maximum number of records to evaluate (default: 100).
        oec_target: Minimum quality score the brain must reach after RAG
            is enabled.  Written to the output file as ``oec_target``.
        output_path: Path where ``rag-baseline.json`` will be written.

    Returns:
        Dict with ``sessions_evaluated``, ``quality_score_mean``, and
        ``oec_target`` keys.
    """
    conn: asyncpg.Connection = await asyncpg.connect(database_url)
    try:
        rows = await conn.fetch(
            """
            SELECT quality_score
            FROM experience_records
            WHERE brain_id = $1
              AND quality_score IS NOT NULL
            ORDER BY created_at DESC
            LIMIT $2
            """,
            brain_id,
            limit,
        )
    finally:
        await conn.close()

    scores = [float(row["quality_score"]) for row in rows]
    sessions_evaluated = len(scores)
    quality_score_mean = (
        sum(scores) / sessions_evaluated if sessions_evaluated > 0 else 0.0
    )

    baseline: dict[str, object] = {
        "sessions_evaluated": sessions_evaluated,
        "quality_score_mean": round(quality_score_mean, 4),
        "oec_target": oec_target,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(baseline, indent=2))
    log.info("Baseline written to %s: %s", output_path, baseline)

    return baseline


def main() -> None:
    """Entry point for computing the OEC baseline from the CLI."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    baseline = asyncio.run(compute_baseline())
    print(json.dumps(baseline, indent=2))


if __name__ == "__main__":
    main()
