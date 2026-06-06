#!/usr/bin/env python3
"""Render one existing active-objective exception entry to stdout.

This helper is intentionally print-first. It does not mutate
`.mm-flow/planning/active-objective-exceptions.json`. Operators can render an
existing entry by `id`, optionally apply narrow overrides, then paste/replace
the JSON object manually and run `validate-active-objective-exceptions.py`.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
PLANNING_DIR = ROOT / ".mm-flow" / "planning"
EXCEPTIONS_PATH = PLANNING_DIR / "active-objective-exceptions.json"
COMMANDS_DIR = Path(__file__).resolve().parent


def load_active_objective_helpers() -> Any:
    """Load shared active-objective helpers from the sibling module file."""
    module_path = COMMANDS_DIR / "active-objective-state.py"
    spec = importlib.util.spec_from_file_location(
        "mm_active_objective_state", module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load active-objective helpers from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_HELPERS = load_active_objective_helpers()
normalize_active_objective_exception_entry = (
    _HELPERS.normalize_active_objective_exception_entry
)


def parse_args() -> argparse.Namespace:
    """Parse CLI args for rendering an existing exception entry."""
    parser = argparse.ArgumentParser(
        description="Render one active-objective exception entry to stdout."
    )
    parser.add_argument("--id", required=True, help="Stable exception identifier.")
    parser.add_argument(
        "--objective-slug",
        action="append",
        dest="objective_slugs",
        default=None,
        help="Replace objective_slugs with these values. Repeat as needed.",
    )
    parser.add_argument(
        "--reason",
        default=None,
        help="Replace the entry reason.",
    )
    parser.add_argument(
        "--command",
        action="append",
        dest="commands",
        default=None,
        help="Replace explicit commands with these values. Repeat as needed.",
    )
    parser.add_argument(
        "--command-bundle-ref",
        action="append",
        dest="command_bundle_refs",
        default=None,
        help="Replace named command bundle refs with these values. Repeat as needed.",
    )
    parser.add_argument(
        "--expires-at-utc",
        default=None,
        help="Replace machine-checkable UTC expiry timestamp.",
    )
    parser.add_argument(
        "--expires-context",
        default=None,
        help="Replace the plain-language expiry context used in expires_when.",
    )
    return parser.parse_args()


def load_exceptions_artifact(path: Path) -> dict[str, object]:
    """Load the raw exceptions artifact or raise ValueError with context."""
    if not path.exists():
        raise ValueError(f"Missing exception artifact: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Invalid exception artifact JSON: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Exception artifact root must be an object: {path}")
    exceptions = data.get("exceptions")
    if not isinstance(exceptions, list):
        raise ValueError(f"Exception artifact `exceptions` must be a list: {path}")
    return data


def find_raw_exception_entry(
    data: dict[str, object], exception_id: str
) -> dict[str, object]:
    """Return the unique raw exception entry matching *exception_id*."""
    matches: list[dict[str, object]] = []
    for entry in data.get("exceptions", []):
        if not isinstance(entry, dict):
            continue
        if entry.get("id") == exception_id:
            matches.append(entry)

    if not matches:
        raise ValueError(f"Unknown exception id: {exception_id}")
    if len(matches) > 1:
        raise ValueError(f"Duplicate exception id: {exception_id}")
    return json.loads(json.dumps(matches[0]))


def normalize_override_list(values: list[str] | None) -> list[str] | None:
    """Normalize repeated string overrides or return None when omitted."""
    if values is None:
        return None
    cleaned = sorted({value.strip() for value in values if value.strip()})
    return cleaned


def apply_overrides(
    entry: dict[str, object], args: argparse.Namespace
) -> dict[str, object]:
    """Apply narrow CLI overrides to a copied exception entry."""
    updated = json.loads(json.dumps(entry))

    objective_slugs = normalize_override_list(args.objective_slugs)
    commands = normalize_override_list(args.commands)
    command_bundle_refs = normalize_override_list(args.command_bundle_refs)

    if objective_slugs is not None:
        updated["objective_slugs"] = objective_slugs
    if args.reason is not None:
        updated["reason"] = args.reason.strip()
    if commands is not None:
        updated["commands"] = commands
    if command_bundle_refs is not None:
        updated["command_bundle_refs"] = command_bundle_refs

    if (args.expires_at_utc is None) != (args.expires_context is None):
        raise ValueError(
            "Provide both --expires-at-utc and --expires-context when overriding expiry."
        )
    if args.expires_at_utc is not None and args.expires_context is not None:
        expires_at_utc = args.expires_at_utc.strip()
        updated["expires_at_utc"] = expires_at_utc
        updated["expires_when"] = (
            f"Expires at {expires_at_utc} — {args.expires_context.strip()}"
        )

    normalized = normalize_active_objective_exception_entry(updated)
    if normalized is None:
        raise ValueError("Overrides produced an invalid exception entry.")
    return normalized


def main() -> int:
    """Render a normalized exception entry to stdout."""
    try:
        args = parse_args()
        artifact = load_exceptions_artifact(EXCEPTIONS_PATH)
        entry = find_raw_exception_entry(artifact, args.id.strip())
        rendered = apply_overrides(entry, args)
    except ValueError as exc:
        print("STATUS: FAILED")
        print(f"- {exc}")
        return 1

    print("STATUS: PASSED")
    print(
        "- Paste/replace the JSON object below into "
        ".mm-flow/planning/active-objective-exceptions.json and then run "
        "validate-active-objective-exceptions.py"
    )
    print(json.dumps(rendered, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
