#!/usr/bin/env python3
"""Validate active-objective exception authoring artifacts.

This validator is authoring-focused: it does not change runtime semantics.
It helps operators keep human-readable and machine-checkable exception metadata
aligned before runtime helpers consume the files.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
PLANNING_DIR = ROOT / ".mm-flow" / "planning"
EXCEPTIONS_PATH = PLANNING_DIR / "active-objective-exceptions.json"
BUNDLES_PATH = PLANNING_DIR / "active-objective-command-bundles.json"
COMMANDS_DIR = ROOT / ".mm-flow" / "commands" / "mm"


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
parse_utc_timestamp = _HELPERS.parse_utc_timestamp
normalize_command_bundle_entry = _HELPERS.normalize_command_bundle_entry
load_named_active_objective_command_bundles = (
    _HELPERS.load_named_active_objective_command_bundles
)
resolve_exception_allowed_commands = _HELPERS.resolve_exception_allowed_commands


def read_json(path: Path) -> Any:
    """Read JSON from a path, returning None on missing or invalid content."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def validate_exceptions_artifact() -> list[str]:
    """Return authoring issues for active-objective-exceptions.json."""
    data = read_json(EXCEPTIONS_PATH)
    if data is None:
        if EXCEPTIONS_PATH.exists():
            return [f"{EXCEPTIONS_PATH}: invalid JSON"]
        return []
    if not isinstance(data, dict):
        return [f"{EXCEPTIONS_PATH}: root must be an object"]
    exceptions = data.get("exceptions", [])
    if not isinstance(exceptions, list):
        return [f"{EXCEPTIONS_PATH}: `exceptions` must be a list"]

    issues: list[str] = []
    for index, entry in enumerate(exceptions):
        label = f"{EXCEPTIONS_PATH}:exceptions[{index}]"
        if not isinstance(entry, dict):
            issues.append(f"{label}: entry must be an object")
            continue
        expires_at_utc = entry.get("expires_at_utc")
        expires_when = entry.get("expires_when")
        parsed = parse_utc_timestamp(expires_at_utc)
        if parsed is None:
            issues.append(f"{label}: missing or invalid `expires_at_utc`")
        if not isinstance(expires_when, str) or not expires_when.strip():
            issues.append(f"{label}: missing `expires_when`")
            continue
        if isinstance(expires_at_utc, str):
            expected_prefix = f"Expires at {expires_at_utc}"
            if not expires_when.startswith(expected_prefix):
                issues.append(
                    f"{label}: `expires_when` must start with `{expected_prefix}`"
                )
        effective_commands = resolve_exception_allowed_commands(ROOT, entry)
        if effective_commands is None:
            issues.append(
                f"{label}: invalid or unresolved commands/`command_bundle_refs`"
            )
        else:
            print(f"INFO: {label} effective commands = {sorted(effective_commands)}")
    return issues


def validate_command_bundles_artifact() -> list[str]:
    """Return authoring issues for active-objective-command-bundles.json."""
    data = read_json(BUNDLES_PATH)
    if data is None:
        if BUNDLES_PATH.exists():
            return [f"{BUNDLES_PATH}: invalid JSON"]
        return []
    if not isinstance(data, dict):
        return [f"{BUNDLES_PATH}: root must be an object"]
    bundles = data.get("bundles", [])
    if not isinstance(bundles, list):
        return [f"{BUNDLES_PATH}: `bundles` must be a list"]

    issues: list[str] = []
    seen_names: set[str] = set()
    for index, entry in enumerate(bundles):
        label = f"{BUNDLES_PATH}:bundles[{index}]"
        bundle = normalize_command_bundle_entry(entry)
        if bundle is None:
            issues.append(f"{label}: invalid bundle entry")
            continue
        name = bundle["name"]
        if name in seen_names:
            issues.append(f"{label}: duplicate bundle name `{name}`")
            continue
        seen_names.add(name)
    return issues


def main() -> int:
    """Run exception authoring validation and print a structured result."""
    issues = [*validate_exceptions_artifact(), *validate_command_bundles_artifact()]
    if issues:
        print("STATUS: FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("STATUS: PASSED")
    if EXCEPTIONS_PATH.exists():
        print(f"- Validated exception artifact: {EXCEPTIONS_PATH}")
    else:
        print(
            f"- No exception artifact present at {EXCEPTIONS_PATH}; nothing to validate"
        )
    if BUNDLES_PATH.exists():
        print(f"- Validated command bundles artifact: {BUNDLES_PATH}")
    else:
        print(f"- No command bundles artifact present at {BUNDLES_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
