#!/usr/bin/env python3
"""Validate and hand off a task-specific objective package to execution."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from planning_paths import get_planning_dir


ROOT_TASK_PATTERN = re.compile(r"^##\s+([A-Z]{1,4}\d+):\s*(.+)$", re.MULTILINE)
SUBTASK_HEADER_PATTERN = re.compile(r"^### Execution Subtasks\s*$", re.MULTILINE)
DEPENDS_ON_PATTERN = re.compile(r"^### Depends On\s*\n([^\n]+)\s*$", re.MULTILINE)
CHILD_PATTERN = re.compile(r"^-\s+([A-Z]{1,4}\d+\.\d+):\s*(\S.*)$")
REQUIRED_ARTIFACTS = ("requirements.md", "design.md", "tasks.md", "HANDOFF-CURRENT.md")


@dataclass(frozen=True)
class RootTask:
    """A root task parsed from the package task plan."""

    task_id: str
    title: str
    body: str


def find_project_root() -> Path:
    """Return the repository root from the current command invocation."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError("refine-objective must run inside a Git repository")
    return Path(result.stdout.strip())


def validate_objective_slug(slug: str) -> str:
    """Validate and normalize an objective directory name."""
    normalized = slug.strip().lower()
    if (
        not normalized
        or normalized in {".", ".."}
        or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", normalized)
        or Path(normalized).is_absolute()
        or Path(normalized).name != normalized
    ):
        raise ValueError("Objective slug must be a safe single path component")
    return normalized


def get_objective_dir(root_dir: Path, slug: str) -> Path:
    """Resolve an objective directory on the preferred planning surface."""
    planning_dir = get_planning_dir(root_dir)
    changes_dir = (planning_dir / "changes").resolve()
    objective_dir = (changes_dir / slug).resolve()
    try:
        relative = objective_dir.relative_to(changes_dir)
    except ValueError as exc:
        raise ValueError(
            f"Objective `{slug}` escapes the planning changes directory"
        ) from exc
    if relative.parts != (slug,) or not objective_dir.is_dir():
        raise ValueError(
            f"Objective package does not exist: {planning_dir / 'changes' / slug}"
        )
    return objective_dir


def require_artifacts(objective_dir: Path) -> dict[str, Path]:
    """Return required local artifacts or fail before reading package content."""
    artifacts: dict[str, Path] = {}
    for name in REQUIRED_ARTIFACTS:
        path = (objective_dir / name).resolve()
        try:
            path.relative_to(objective_dir)
        except ValueError as exc:
            raise ValueError(f"Artifact `{name}` escapes objective package") from exc
        if not path.is_file():
            raise ValueError(f"Objective package is missing required artifact: {name}")
        artifacts[name] = path
    return artifacts


def parse_root_tasks(tasks_path: Path) -> list[RootTask]:
    """Parse ordered `## ID:` root task sections from a task plan."""
    content = tasks_path.read_text(encoding="utf-8")
    matches = list(ROOT_TASK_PATTERN.finditer(content))
    if not matches:
        raise ValueError("tasks.md has no root tasks using `## ID:` headings")
    roots: list[RootTask] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        roots.append(
            RootTask(
                task_id=match.group(1),
                title=match.group(2).strip(),
                body=content[match.start() : end],
            )
        )
    return roots


def validate_task_topology(roots: list[RootTask]) -> None:
    """Require executable children and valid root-task dependency references."""
    root_ids = {root.task_id for root in roots}
    seen_children: set[str] = set()
    for root in roots:
        subtask_headers = list(SUBTASK_HEADER_PATTERN.finditer(root.body))
        if len(subtask_headers) != 1:
            raise ValueError(
                f"Root task {root.task_id} requires exactly one Execution Subtasks block"
            )
        header = subtask_headers[0]
        next_heading = re.search(r"^###\s+", root.body[header.end() :], re.MULTILINE)
        body_end = (
            header.end() + next_heading.start() if next_heading else len(root.body)
        )
        child_lines = [
            line for line in root.body[header.end() : body_end].splitlines() if line
        ]
        if not child_lines:
            raise ValueError(f"Root task {root.task_id} has no execution subtasks")
        for line in child_lines:
            child_match = CHILD_PATTERN.fullmatch(line)
            if child_match is None or not child_match.group(1).startswith(
                f"{root.task_id}."
            ):
                raise ValueError(
                    f"Malformed execution subtask for {root.task_id}: {line}"
                )
            child_id, description = child_match.groups()
            if child_id in seen_children:
                raise ValueError(f"Duplicate execution subtask ID: {child_id}")
            generic_descriptions = {
                f"Review requirements and design context for {root.task_id}",
                f"Implement {root.task_id} end-to-end",
                f"Run validation for {root.task_id}",
            }
            if description.strip() in generic_descriptions:
                raise ValueError(
                    f"Execution subtask {child_id} uses a generic placeholder description"
                )
            seen_children.add(child_id)

        dependency_matches = list(DEPENDS_ON_PATTERN.finditer(root.body))
        if len(dependency_matches) != 1:
            raise ValueError(f"Root task {root.task_id} requires one Depends On block")
        dependency_text = dependency_matches[0].group(1).strip()
        if dependency_text.lower() == "none":
            continue
        dependencies = [item.strip() for item in dependency_text.split(",")]
        if not dependencies or any(not item for item in dependencies):
            raise ValueError(f"Root task {root.task_id} has malformed dependencies")
        unresolved = [
            dependency for dependency in dependencies if dependency not in root_ids
        ]
        if unresolved:
            raise ValueError(
                f"Root task {root.task_id} depends on unknown task(s): {', '.join(unresolved)}"
            )


def find_canonical_doc(root_dir: Path, objective_slug: str) -> Path | None:
    """Return the canonical objective document when its filename matches the slug."""
    canonical_dir = root_dir / "docs" / "canonical"
    if not canonical_dir.is_dir():
        return None
    base_slug = re.sub(r"[-_]?v\d+$", "", objective_slug)
    for path in sorted(canonical_dir.glob("*.md")):
        filename = path.name.lower()
        if objective_slug in filename or base_slug and base_slug in filename:
            return path
    return None


def build_brief(root_dir: Path, slug: str, artifacts: dict[str, Path]) -> str:
    """Build the read-only instructions for an agent to refine one package."""
    roots = parse_root_tasks(artifacts["tasks.md"])
    source_docs: list[Path] = []
    canonical = find_canonical_doc(root_dir, slug)
    if canonical is not None:
        source_docs.append(canonical)
    source_docs.extend(
        artifacts[name]
        for name in ("requirements.md", "design.md", "tasks.md", "HANDOFF-CURRENT.md")
    )
    lines = [
        f"Objective: {slug}",
        "Root tasks:",
        *[f"- {root.task_id}: {root.title}" for root in roots],
        "Required source docs:",
        *[f"- {path.relative_to(root_dir)}" for path in source_docs],
        "Rules:",
        "- Refine requirements.md, design.md, and tasks.md with the actual objective scope.",
        "- Add exactly one nonempty `### Execution Subtasks` block to every root task.",
        "- Every child must use `<TASK>.<number>: description` and have a specific, non-placeholder description.",
        "- Do not manually update todo.md, HANDOFF-CURRENT.md, execution-state.json, or task-progress.json.",
        f"- When refinement is complete, run /mm:refine-objective --objective {slug} --sync.",
    ]
    return "\n".join(lines)


def emit(message: str) -> None:
    """Write one structured CLI message to standard output."""
    sys.stdout.write(f"{message}\n")


def emit_failure(reason: str) -> int:
    """Emit the command failure protocol and return its process status."""
    emit("STATUS: FAILED")
    emit(f"REASON: {reason}")
    return 1


def main() -> int:
    """Run the brief or validated synchronization lifecycle operation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--objective", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--brief", action="store_true")
    mode.add_argument("--sync", action="store_true")
    args = parser.parse_args()
    try:
        root_dir = find_project_root()
        slug = validate_objective_slug(args.objective)
        objective_dir = get_objective_dir(root_dir, slug)
        artifacts = require_artifacts(objective_dir)
        if args.brief:
            emit("MODEL_BRIEF_START")
            emit(build_brief(root_dir, slug, artifacts))
            emit("MODEL_BRIEF_END")
            return 0
        roots = parse_root_tasks(artifacts["tasks.md"])
        validate_task_topology(roots)
        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve().with_name("complete-task-handler.py")),
                "--resync-objective",
                slug,
            ],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "resync failed"
            raise ValueError(f"complete-task resync failed: {detail}")
        emit("STATUS: PASSED")
        emit(f"OBJECTIVE: {slug}")
        emit(f"NEXT_COMMAND: /mm:complete-task {roots[0].task_id} --brief")
        return 0
    except (OSError, ValueError) as exc:
        return emit_failure(str(exc))


if __name__ == "__main__":
    sys.exit(main())
