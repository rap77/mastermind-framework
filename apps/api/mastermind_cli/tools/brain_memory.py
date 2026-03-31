#!/usr/bin/env python3
"""CLI bridge para que brain agents accedan al ExperienceLogger via Bash.

Usage:
    python3 apps/api/mastermind_cli/tools/brain_memory.py query --brain-id brain-01-product --limit 5
    python3 apps/api/mastermind_cli/tools/brain_memory.py log --brain-id brain-01-product \\
        --input '{"brief": "..."}' --output '{"recommendation": "..."}' --status success

Environment:
    MM_DB_PATH: Path to SQLite database (required in production)
"""

import argparse
import asyncio
import json
import os
import sys

# Allow running from repo root or from apps/api/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from mastermind_cli.state.database import DatabaseConnection
from mastermind_cli.experience.logger import ExperienceLogger


def _get_db_path() -> str:
    """Read MM_DB_PATH from environment. Fails loudly if not set in non-dev context."""
    path = os.environ.get("MM_DB_PATH", "mastermind.db")
    return path


async def _cmd_query(args: argparse.Namespace) -> None:
    """Query recent experience records for a brain."""
    async with DatabaseConnection(_get_db_path()) as db:
        await db.create_experience_schema()
        logger = ExperienceLogger(db)
        records = await logger.get_recent_by_brain(args.brain_id, limit=args.limit)

    output = [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "status": r.status,
            "duration_ms": r.duration_ms,
            "output_json": r.output_json,
            "custom_metadata": r.custom_metadata,
        }
        for r in records
    ]
    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))


async def _cmd_log(args: argparse.Namespace) -> None:
    """Log an experience record for a brain."""
    try:
        input_data = json.loads(args.input)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid --input JSON: {e}"}))
        sys.exit(1)

    try:
        output_data = json.loads(args.output)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid --output JSON: {e}"}))
        sys.exit(1)

    metadata: dict[str, object] = {}
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid --metadata JSON: {e}"}))
            sys.exit(1)

    async with DatabaseConnection(_get_db_path()) as db:
        await db.create_experience_schema()
        logger = ExperienceLogger(db)
        record_id = await logger.log_execution(
            brain_id=args.brain_id,
            input_json=input_data,
            output_json=output_data,
            duration_ms=args.duration_ms,
            status=args.status,
            trace_context_id=args.trace_id or None,
            custom_metadata=metadata,
        )

    print(json.dumps({"record_id": record_id, "status": "logged"}))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Brain memory CLI — query and log experience records"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # query subcommand
    q = sub.add_parser("query", help="Query recent records for a brain")
    q.add_argument("--brain-id", required=True, help="Brain ID (e.g. brain-01-product)")
    q.add_argument(
        "--limit", type=int, default=5, help="Max records to return (default: 5)"
    )

    # log subcommand
    log_parser = sub.add_parser("log", help="Log an experience record")
    log_parser.add_argument("--brain-id", required=True, help="Brain ID")
    log_parser.add_argument("--input", required=True, help="Input JSON string")
    log_parser.add_argument("--output", required=True, help="Output JSON string")
    log_parser.add_argument("--duration-ms", type=int, default=0, dest="duration_ms")
    log_parser.add_argument(
        "--status", default="success", choices=["success", "failure", "timeout"]
    )
    log_parser.add_argument("--trace-id", default=None, dest="trace_id")
    log_parser.add_argument(
        "--metadata", default="{}", help="Custom metadata JSON string"
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "query":
        asyncio.run(_cmd_query(args))
    elif args.command == "log":
        asyncio.run(_cmd_log(args))


if __name__ == "__main__":
    main()
