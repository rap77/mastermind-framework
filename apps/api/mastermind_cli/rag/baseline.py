"""
OEC Baseline Calculator — Phase 20C.

Reads the last N experience_records for brain-01 from PostgreSQL (records
without RAG enabled — i.e. pre-RAG baseline), computes mean and std of
quality_score, and writes the result to tasks/rag-baseline.json.

Usage:
    uv run python -m mastermind_cli.rag.baseline
    DATABASE_URL=postgresql://... uv run python -m mastermind_cli.rag.baseline
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
from datetime import datetime, timezone
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
_OEC_IMPROVEMENT = 0.08  # target improvement over baseline mean


async def compute_baseline(
    database_url: str = _DEFAULT_DATABASE_URL,
    brain_id: str = _BRAIN_ID,
    limit: int = _N_RECORDS,
    output_path: Path = _BASELINE_PATH,
) -> dict[str, object]:
    """Compute the pre-RAG quality baseline for a brain.

    Reads the last *limit* experience_records for *brain_id* from PostgreSQL,
    filters to rows where ``quality_score IS NOT NULL`` (records without RAG
    context), then computes mean and standard deviation of quality_score.

    Args:
        database_url: PostgreSQL DSN to connect to.
        brain_id: Brain identifier to evaluate (default: ``"brain-01"``).
        limit: Maximum number of records to evaluate (default: 100).
        output_path: Path where ``rag-baseline.json`` will be written.

    Returns:
        Dict matching the structure specified in plan.md 20C.
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

    if sessions_evaluated > 0:
        quality_score_mean = sum(scores) / sessions_evaluated
        # Population std dev (ddof=0) for small samples
        variance = (
            sum((s - quality_score_mean) ** 2 for s in scores) / sessions_evaluated
        )
        quality_score_std = math.sqrt(variance)
    else:
        quality_score_mean = 0.0
        quality_score_std = 0.0

    oec_target = f"mean + {_OEC_IMPROVEMENT}"

    baseline: dict[str, object] = {
        "brain_id": brain_id,
        "rag_enabled": False,
        "sessions_evaluated": sessions_evaluated,
        "quality_score_mean": round(quality_score_mean, 4),
        "quality_score_std": round(quality_score_std, 4),
        "measured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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
