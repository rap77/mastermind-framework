#!/usr/bin/env python3
"""Replace one active-objective exception entry by id from a JSON object file.

This helper is intentionally narrow. It rewrites exactly one matching entry in
`.mm-flow/planning/active-objective-exceptions.json` using an explicit JSON
object from `--entry-file`, then instructs the operator to run
`validate-active-objective-exceptions.py`.
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
    """Parse CLI args for replacing one existing exception entry."""
    parser = argparse.ArgumentParser(
        description="Replace one active-objective exception entry by id."
    )
    parser.add_argument("--id", required=True, help="Stable exception identifier.")
    parser.add_argument(
        "--entry-file",
        required=True,
        help="Path to one JSON object that will replace the matching exception entry.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the normalized replacement without mutating the artifact.",
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


def find_exception_indexes(data: dict[str, object], exception_id: str) -> list[int]:
    """Return all indexes whose raw exception entry matches *exception_id*."""
    matches: list[int] = []
    for index, entry in enumerate(data.get("exceptions", [])):
        if isinstance(entry, dict) and entry.get("id") == exception_id:
            matches.append(index)
    return matches


def require_unique_exception_index(data: dict[str, object], exception_id: str) -> int:
    """Return the unique matching exception index or raise ValueError."""
    matches = find_exception_indexes(data, exception_id)
    if not matches:
        raise ValueError(f"Unknown exception id: {exception_id}")
    if len(matches) > 1:
        raise ValueError(f"Duplicate exception id: {exception_id}")
    return matches[0]


def load_replacement_entry(path: Path) -> dict[str, object]:
    """Load one replacement JSON object file or raise ValueError."""
    if not path.exists():
        raise ValueError(f"Missing entry file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Invalid entry file JSON: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Replacement entry file must contain one JSON object: {path}")
    return data


def normalize_replacement_entry(
    replacement: dict[str, object], exception_id: str
) -> dict[str, object]:
    """Validate and normalize the replacement entry."""
    replacement_id = replacement.get("id")
    if replacement_id != exception_id:
        raise ValueError("Replacement entry `id` must match --id.")
    normalized = normalize_active_objective_exception_entry(replacement)
    if normalized is None:
        raise ValueError("Replacement entry is invalid after normalization.")
    return normalized


def write_updated_artifact(
    artifact: dict[str, object], target_index: int, replacement: dict[str, object]
) -> None:
    """Rewrite the exception artifact with exactly one entry replaced."""
    exceptions = list(artifact["exceptions"])
    exceptions[target_index] = replacement
    updated_artifact = dict(artifact)
    updated_artifact["exceptions"] = exceptions
    EXCEPTIONS_PATH.write_text(
        json.dumps(updated_artifact, indent=2) + "\n",
        encoding="utf-8",
    )


def summarize_changed_fields(
    current: dict[str, object], replacement: dict[str, object]
) -> list[str]:
    """Return sorted top-level field names whose values would change."""
    changed_fields = {
        key
        for key in set(current.keys()) | set(replacement.keys())
        if current.get(key) != replacement.get(key)
    }
    return sorted(changed_fields)


def main() -> int:
    """Replace one exception entry by id and print a structured result."""
    try:
        args = parse_args()
        exception_id = args.id.strip()
        artifact = load_exceptions_artifact(EXCEPTIONS_PATH)
        target_index = require_unique_exception_index(artifact, exception_id)
        current_entry = artifact["exceptions"][target_index]
        if not isinstance(current_entry, dict):
            raise ValueError(
                f"Exception entry at index {target_index} must be an object."
            )
        replacement_file = Path(args.entry_file).expanduser()
        replacement = load_replacement_entry(replacement_file)
        normalized = normalize_replacement_entry(replacement, exception_id)
        if not args.dry_run:
            write_updated_artifact(artifact, target_index, normalized)
    except ValueError as exc:
        print("STATUS: FAILED")
        print(f"- {exc}")
        return 1

    print("STATUS: PASSED")
    if args.dry_run:
        print("DRY_RUN: true")
        print(f"TARGET_ID: {exception_id}")
        print(
            f"CHANGED_FIELDS: {', '.join(summarize_changed_fields(current_entry, normalized))}"
        )
        print("CURRENT_ENTRY:")
        print(json.dumps(current_entry, indent=2))
        print("REPLACEMENT_ENTRY:")
        print(json.dumps(normalized, indent=2))
        print("- Preview only; artifact not modified.")
    else:
        print(
            "- Replaced one exception entry in "
            ".mm-flow/planning/active-objective-exceptions.json; now run "
            "validate-active-objective-exceptions.py"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
