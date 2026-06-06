#!/usr/bin/env python3
"""Shared helpers for active-objective coordination."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ACTIVE_OBJECTIVE_EXCEPTIONS_PATH = Path(
    ".mm-flow/planning/active-objective-exceptions.json"
)
ACTIVE_OBJECTIVE_COMMAND_BUNDLES_PATH = Path(
    ".mm-flow/planning/active-objective-command-bundles.json"
)


def load_roadmap(root_dir: Path) -> object | None:
    """Load roadmap objectives.json when present."""
    roadmap_path = root_dir / ".mm-flow" / "planning" / "roadmap" / "objectives.json"
    if not roadmap_path.exists():
        return None
    try:
        return json.loads(roadmap_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def roadmap_status_for_slug(root_dir: Path, slug: str) -> str | None:
    """Return the roadmap status for a slug when available."""
    roadmap = load_roadmap(root_dir)
    if isinstance(roadmap, list):
        for entry in roadmap:
            if not isinstance(entry, dict):
                continue
            if entry.get("slug") == slug or entry.get("stable_id") == slug:
                status = entry.get("status")
                return str(status) if status is not None else None
    if isinstance(roadmap, dict):
        objectives = roadmap.get("objectives", [])
        if isinstance(objectives, list):
            for entry in objectives:
                if not isinstance(entry, dict):
                    continue
                if entry.get("slug") == slug or entry.get("stable_id") == slug:
                    status = entry.get("status")
                    return str(status) if status is not None else None
    return None


def load_execution_state(objective_dir: Path) -> dict[str, object] | None:
    """Load execution-state.json for an objective directory when present."""
    path = objective_dir / "execution-state.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def load_active_objective_exceptions(root_dir: Path) -> list[dict[str, object]]:
    """Load valid active-objective exception entries from planning artifacts.

    Invalid files or malformed entries fail closed and return an empty or
    filtered list rather than raising.
    """
    path = root_dir / ACTIVE_OBJECTIVE_EXCEPTIONS_PATH
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, dict):
        return []

    version = data.get("version")
    exceptions = data.get("exceptions")
    if not isinstance(version, int) or version < 1:
        return []
    if not isinstance(exceptions, list):
        return []

    valid_entries: list[dict[str, object]] = []
    for entry in exceptions:
        normalized = normalize_active_objective_exception_entry(entry)
        if normalized is not None:
            valid_entries.append(normalized)
    return valid_entries


def load_active_objective_command_bundles(root_dir: Path) -> dict[str, set[str]]:
    """Load delegated command bundles from planning artifacts.

    Invalid or missing artifacts fail closed to an empty mapping.
    """
    named_bundles = load_named_active_objective_command_bundles(root_dir)
    bundles: dict[str, set[str]] = {}
    for bundle in named_bundles.values():
        parent_command = bundle["parent_command"]
        delegated_commands = bundle["delegated_commands"]
        bundles[parent_command] = set(delegated_commands)
    return bundles


def load_named_active_objective_command_bundles(
    root_dir: Path,
) -> dict[str, dict[str, object]]:
    """Load command bundles keyed by stable bundle name."""
    path = root_dir / ACTIVE_OBJECTIVE_COMMAND_BUNDLES_PATH
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    version = data.get("version")
    bundles = data.get("bundles")
    if not isinstance(version, int) or version < 1:
        return {}
    if not isinstance(bundles, list):
        return {}

    normalized: dict[str, dict[str, object]] = {}
    for entry in bundles:
        bundle = normalize_command_bundle_entry(entry)
        if bundle is None:
            continue
        normalized[bundle["name"]] = bundle
    return normalized


def normalize_command_bundle_entry(
    entry: object,
) -> dict[str, object] | None:
    """Return a normalized command bundle entry or None when invalid."""
    if not isinstance(entry, dict):
        return None
    name = entry.get("name")
    parent_command = entry.get("parent_command")
    delegated_commands = entry.get("delegated_commands")
    reason = entry.get("reason")
    if not isinstance(name, str) or not name.strip():
        return None
    if not isinstance(parent_command, str) or not parent_command.strip():
        return None
    if not isinstance(reason, str) or not reason.strip():
        return None
    if not isinstance(delegated_commands, list) or not delegated_commands:
        return None

    normalized_commands: set[str] = set()
    for command in delegated_commands:
        if not isinstance(command, str) or not command.strip():
            return None
        normalized_commands.add(command.strip())
    if not normalized_commands:
        return None
    return {
        "name": name.strip(),
        "parent_command": parent_command.strip(),
        "delegated_commands": normalized_commands,
        "reason": reason.strip(),
    }


def normalize_active_objective_exception_entry(
    entry: object,
) -> dict[str, object] | None:
    """Return a normalized exception entry or None when malformed."""
    if not isinstance(entry, dict):
        return None

    entry_id = entry.get("id")
    reason = entry.get("reason")
    expires_when = entry.get("expires_when")
    expires_at_utc = entry.get("expires_at_utc")
    objective_slugs = entry.get("objective_slugs")
    commands = entry.get("commands")
    command_bundle_refs = entry.get("command_bundle_refs", [])

    if not isinstance(entry_id, str) or not entry_id.strip():
        return None
    if not isinstance(reason, str) or not reason.strip():
        return None
    if not isinstance(expires_when, str) or not expires_when.strip():
        return None
    parsed_expires_at_utc = parse_utc_timestamp(expires_at_utc)
    if parsed_expires_at_utc is None:
        return None
    if not isinstance(objective_slugs, list) or len(objective_slugs) < 2:
        return None
    if commands is None:
        commands = []
    if not isinstance(commands, list):
        return None
    if not isinstance(command_bundle_refs, list):
        return None

    normalized_slugs: list[str] = []
    for slug in objective_slugs:
        if not isinstance(slug, str) or not slug.strip():
            return None
        normalized_slugs.append(slug.strip())

    normalized_commands: list[str] = []
    for command in commands:
        if not isinstance(command, str) or not command.strip():
            return None
        normalized_commands.append(command.strip())
    normalized_bundle_refs: list[str] = []
    for bundle_ref in command_bundle_refs:
        if not isinstance(bundle_ref, str) or not bundle_ref.strip():
            return None
        normalized_bundle_refs.append(bundle_ref.strip())

    unique_slugs = sorted(set(normalized_slugs))
    unique_commands = sorted(set(normalized_commands))
    unique_bundle_refs = sorted(set(normalized_bundle_refs))
    if len(unique_slugs) < 2 or (not unique_commands and not unique_bundle_refs):
        return None

    return {
        "id": entry_id.strip(),
        "objective_slugs": unique_slugs,
        "reason": reason.strip(),
        "commands": unique_commands,
        "command_bundle_refs": unique_bundle_refs,
        "expires_when": expires_when.strip(),
        "expires_at_utc": format_utc_timestamp(parsed_expires_at_utc),
    }


def parse_utc_timestamp(value: object) -> datetime | None:
    """Parse an ISO-8601 UTC timestamp ending in `Z`."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if not text.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def format_utc_timestamp(value: datetime) -> str:
    """Return a normalized ISO-8601 UTC timestamp with trailing `Z`."""
    return (
        value.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def is_exception_entry_active(entry: dict[str, object]) -> bool:
    """Return whether an exception entry is still active by machine timestamp."""
    parsed = parse_utc_timestamp(entry.get("expires_at_utc"))
    if parsed is None:
        return False
    return datetime.now(timezone.utc) < parsed


def find_active_objective_exception(
    root_dir: Path,
    active_slugs: set[str],
    requested_slug: str,
    command_name: str,
    delegated_from: str | None = None,
) -> dict[str, object] | None:
    """Return a matching multi-active exception for a command, if one exists."""
    requested_set = {slug for slug in active_slugs if slug}
    if requested_slug:
        requested_set.add(requested_slug)
    if len(requested_set) < 2:
        return None

    for entry in load_active_objective_exceptions(root_dir):
        if not is_exception_entry_active(entry):
            continue
        entry_slugs = entry.get("objective_slugs")
        entry_commands = resolve_exception_allowed_commands(root_dir, entry)
        if not isinstance(entry_slugs, list) or entry_commands is None:
            continue
        if set(str(slug) for slug in entry_slugs) != requested_set:
            continue
        if not command_scope_matches(
            {str(command) for command in entry_commands},
            command_name,
            root_dir,
            delegated_from,
        ):
            continue
        return entry
    return None


def resolve_exception_allowed_commands(
    root_dir: Path, entry: dict[str, object]
) -> set[str] | None:
    """Resolve explicit commands plus named bundle refs into effective commands."""
    commands = entry.get("commands", [])
    bundle_refs = entry.get("command_bundle_refs", [])
    if not isinstance(commands, list) or not isinstance(bundle_refs, list):
        return None

    effective_commands = {str(command) for command in commands}
    named_bundles = load_named_active_objective_command_bundles(root_dir)
    for bundle_ref in bundle_refs:
        if not isinstance(bundle_ref, str):
            return None
        bundle = named_bundles.get(bundle_ref)
        if bundle is None:
            return None
        parent_command = bundle.get("parent_command")
        if not isinstance(parent_command, str) or not parent_command:
            return None
        effective_commands.add(parent_command)
    return effective_commands if effective_commands else None


def command_scope_matches(
    allowed_commands: set[str],
    command_name: str,
    root_dir: Path,
    delegated_from: str | None = None,
) -> bool:
    """Return whether an exception entry authorizes a command scope.

    Direct command matches always work. Delegated matches work only when the
    child command is explicitly documented as delegatable from the named parent.
    """
    if command_name in allowed_commands:
        return True
    if not delegated_from:
        return False
    delegated_children = load_active_objective_command_bundles(root_dir).get(
        delegated_from
    )
    if not delegated_children or command_name not in delegated_children:
        return False
    return delegated_from in allowed_commands


def runtime_objective_slug(root_dir: Path) -> str | None:
    """Return the runtime state's objective slug when present."""
    runtime_path = root_dir / ".mm-flow" / "planning" / "task-progress.json"
    if not runtime_path.exists():
        return None
    try:
        data = json.loads(runtime_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    slug = data.get("objective_slug")
    return str(slug) if slug else None


def is_stale_bootstrapped_done_objective(root_dir: Path, objective_dir: Path) -> bool:
    """Return whether an active objective directory is a deterministic stale ghost.

    A directory qualifies when:
    - roadmap marks the objective `done`
    - execution-state was bootstrapped from artifacts
    - all root tasks are still `pending`
    - runtime state is absent or points to a different objective
    """
    slug = objective_dir.name
    if roadmap_status_for_slug(root_dir, slug) != "done":
        return False

    state = load_execution_state(objective_dir)
    if not state or not state.get("bootstrapped_from_artifacts"):
        return False

    tasks = state.get("tasks")
    if not isinstance(tasks, dict) or not tasks:
        return False
    statuses = []
    for task in tasks.values():
        if not isinstance(task, dict):
            return False
        statuses.append(str(task.get("status", "pending")))
    if not all(status == "pending" for status in statuses):
        return False

    runtime_slug = runtime_objective_slug(root_dir)
    if runtime_slug == slug:
        return False

    return True


def active_objective_dirs(root_dir: Path) -> list[Path]:
    """Return blocking active objective directories under planning/changes."""
    changes_dir = root_dir / ".mm-flow" / "planning" / "changes"
    if not changes_dir.exists():
        return []
    dirs = sorted(path for path in changes_dir.iterdir() if path.is_dir())
    return [
        path
        for path in dirs
        if not is_stale_bootstrapped_done_objective(root_dir, path)
    ]
