"""Executable gate wrapper for the offline RAG Recall@K evaluation."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any, Sequence

import asyncpg
import click

from .contamination import evaluate_self_contamination
from .quality import compare_cold_vs_rag
from .recall_eval import (
    _DEFAULT_BRAIN_ID,
    _DEFAULT_COLLECTION,
    _DEFAULT_DATABASE_URL,
    _DEFAULT_EVAL_PAIRS_PATH,
    _DEFAULT_LIMIT,
    _DEFAULT_OUTPUT_PATH,
    evaluate_recall,
)


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the RAG evaluation gate."""
    parser = argparse.ArgumentParser(
        description="Run the Brain #1 RAG Recall@K evaluation gate."
    )
    parser.add_argument("--database-url", default=_DEFAULT_DATABASE_URL)
    parser.add_argument("--brain-id", default=_DEFAULT_BRAIN_ID)
    parser.add_argument("--collection", default=_DEFAULT_COLLECTION)
    parser.add_argument("--eval-pairs-path", default=str(_DEFAULT_EVAL_PAIRS_PATH))
    parser.add_argument("--limit", type=int, default=_DEFAULT_LIMIT)
    parser.add_argument("--output-path", default=str(_DEFAULT_OUTPUT_PATH))
    parser.add_argument("--cold-output-path", default="")
    parser.add_argument("--rag-output-path", default="")
    return parser


async def _run_gate(args: argparse.Namespace) -> dict[str, Any]:
    """Run the gate and return the serialized evaluation payload."""
    if not args.database_url:
        raise ValueError(
            "database_url is required via --database-url or DATABASE_URL "
            "environment variable"
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

    contamination = evaluate_self_contamination(
        eval_pairs_path=Path(args.eval_pairs_path),
        brain_id=args.brain_id,
    )

    payload = result.to_dict()
    payload["contamination"] = contamination.to_dict()
    payload["contamination_passed"] = contamination.passed

    cold_output_path = getattr(args, "cold_output_path", "")
    rag_output_path = getattr(args, "rag_output_path", "")

    if cold_output_path and rag_output_path:
        cold_output = json.loads(Path(cold_output_path).read_text(encoding="utf-8"))
        rag_output = json.loads(Path(rag_output_path).read_text(encoding="utf-8"))
        quality = compare_cold_vs_rag(
            brain_id=args.brain_id,
            cold_output_json=cold_output,
            rag_output_json=rag_output,
            output_path=None,
        )
        payload["quality_comparison"] = quality.to_dict()
        payload["quality_comparison_passed"] = quality.passes
    else:
        payload["quality_comparison"] = None
        payload["quality_comparison_passed"] = True

    if args.output_path:
        output_path = Path(args.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return payload


def run(argv: Sequence[str] | None = None) -> int:
    """Execute the gate and return the process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    payload = asyncio.run(_run_gate(args))
    click.echo(json.dumps(payload, indent=2))
    quality_passed = payload.get("quality_comparison_passed", False)
    return (
        0
        if payload["passes_sli"] and payload["contamination_passed"] and quality_passed
        else 1
    )


def main() -> None:
    """CLI entry point for the RAG evaluation gate."""
    raise SystemExit(run())


if __name__ == "__main__":
    main()
