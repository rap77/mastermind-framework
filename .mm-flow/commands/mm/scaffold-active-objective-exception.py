#!/usr/bin/env python3
"""Scaffold one active-objective exception entry to stdout.

This helper does not mutate the exceptions artifact. It prints a single JSON
entry that operators can paste into the active planning surface's
`active-objective-exceptions.json` and then validate with
`validate-active-objective-exceptions.py`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from planning_paths import planning_relpath

ROOT = Path.cwd()
PLANNING_LABEL = planning_relpath(ROOT)


def parse_args() -> argparse.Namespace:
    """Parse scaffold command arguments."""
    parser = argparse.ArgumentParser(
        description="Scaffold one active-objective exception entry to stdout."
    )
    parser.add_argument("--id", required=True, help="Stable exception identifier.")
    parser.add_argument(
        "--objective-slug",
        action="append",
        dest="objective_slugs",
        required=True,
        help="Objective slug allowed by this exception. Repeat for at least two slugs.",
    )
    parser.add_argument("--reason", required=True, help="Why the exception exists.")
    parser.add_argument(
        "--command",
        action="append",
        dest="commands",
        default=[],
        help="Explicit command scope. Repeat as needed.",
    )
    parser.add_argument(
        "--command-bundle-ref",
        action="append",
        dest="command_bundle_refs",
        default=[],
        help="Named command bundle reference. Repeat as needed.",
    )
    parser.add_argument(
        "--expires-at-utc",
        required=True,
        help="Machine-checkable UTC expiry timestamp, e.g. 2026-12-31T23:59:59Z.",
    )
    parser.add_argument(
        "--expires-context",
        required=True,
        help="Plain-language context appended after the timestamp in expires_when.",
    )
    return parser.parse_args()


def build_entry(args: argparse.Namespace) -> dict[str, object]:
    """Build one scaffolded exception entry from parsed args."""
    objective_slugs = sorted(
        set(slug.strip() for slug in args.objective_slugs if slug.strip())
    )
    commands = sorted(
        set(command.strip() for command in args.commands if command.strip())
    )
    command_bundle_refs = sorted(
        set(bundle.strip() for bundle in args.command_bundle_refs if bundle.strip())
    )

    if len(objective_slugs) < 2:
        raise ValueError("Provide at least two --objective-slug values.")
    if not commands and not command_bundle_refs:
        raise ValueError("Provide at least one --command or --command-bundle-ref.")

    entry: dict[str, object] = {
        "id": args.id.strip(),
        "objective_slugs": objective_slugs,
        "reason": args.reason.strip(),
        "expires_at_utc": args.expires_at_utc.strip(),
        "expires_when": f"Expires at {args.expires_at_utc.strip()} — {args.expires_context.strip()}",
    }
    if commands:
        entry["commands"] = commands
    if command_bundle_refs:
        entry["command_bundle_refs"] = command_bundle_refs
    return entry


def main() -> int:
    """Print one scaffolded JSON object to stdout."""
    try:
        entry = build_entry(parse_args())
    except ValueError as exc:
        sys.stdout.write("STATUS: FAILED\n")
        sys.stdout.write(f"- {exc}\n")
        return 1

    sys.stdout.write("STATUS: PASSED\n")
    sys.stdout.write(
        f"- Copy the JSON object below into {PLANNING_LABEL}/active-objective-exceptions.json and then run validate-active-objective-exceptions.py"
    )
    sys.stdout.write("\n")
    sys.stdout.write(json.dumps(entry, indent=2))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
