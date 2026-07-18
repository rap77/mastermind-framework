#!/usr/bin/env python3
"""MasterMind Discovery Handler.

Supports:
- legacy new-project discovery
- legacy existing-project rediscovery
- roadmap discovery for an existing project
- objective packaging for a named workstream/objective
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from planning_paths import get_planning_dir, planning_relpath


def emit(
    *parts: object,
    sep: str = " ",
    end: str = "\n",
    file: object | None = None,
    flush: bool = True,
) -> None:
    """Write a single structured line to stdout or stderr."""
    stream = sys.stderr if file is sys.stderr else sys.stdout
    stream.write(sep.join(str(part) for part in parts) + end)
    if flush:
        stream.flush()


PLANNING_LABEL = planning_relpath(Path.cwd())


def parse_args() -> argparse.Namespace:
    """Parse discovery command arguments."""
    parser = argparse.ArgumentParser(
        description="Discover and plan: from idea or codebase state to actionable work"
    )
    parser.add_argument(
        "idea",
        nargs="?",
        help="Project or objective idea (optional in existing modes)",
        default=None,
    )
    parser.add_argument(
        "--existing",
        action="store_true",
        help="Audit existing project instead of new idea",
    )
    parser.add_argument(
        "--mode",
        choices=["fast", "deep"],
        default="fast",
        help="Discovery mode: fast or deep",
    )
    parser.add_argument(
        "--health", action="store_true", help="Health check only (existing mode)"
    )
    parser.add_argument(
        "--gaps", action="store_true", help="Gap analysis only (existing mode)"
    )
    parser.add_argument(
        "--replan",
        action="store_true",
        help="Re-plan with current gaps (existing mode)",
    )
    parser.add_argument(
        "--roadmap",
        action="store_true",
        help="Generate/update the roadmap of objectives for the existing project",
    )
    parser.add_argument(
        "--objective",
        default=None,
        help="Create/update a planning package for one named objective/workstream",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Generate a lighter objective package (shortcut for objective-scoped fast planning)",
    )
    parser.add_argument(
        "--delegated-from",
        default=None,
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def slugify(value: str) -> str:
    """Return a filesystem-safe objective slug."""
    lowered = value.strip().lower()
    slug = "".join(ch if ch.isalnum() else "-" for ch in lowered)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def validate_objective_slug(value: str) -> str:
    """Return a safe objective slug or reject ambiguous filesystem input."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", value):
        raise ValueError(
            "Objective slug must use lowercase letters, numbers, and hyphens"
        )
    return value


def find_canonical_doc_for_objective(
    root_dir: Path, objective_slug: str
) -> Path | None:
    """Find a canonical doc that corresponds to this objective slug.

    Searches for:
    1. docs/canonical/XX-<slug>.md (explicit numbered format)
    2. docs/canonical/*<slug>*.md (anywhere in filename, stripping common suffixes like -v2, -v3)
    3. docs/canonical/XX-*.md where content's title matches objective_slug without version suffix
    """
    canonical_dir = root_dir / "docs" / "canonical"
    if not canonical_dir.exists():
        return None

    # Strip common version suffixes for matching
    base_slug = re.sub(r"[-_]?v\d+$", "", objective_slug.lower())

    # Pattern 1: explicit numbered format like "48-MM-CLI-DESIGN.md"
    number_prefix_pattern = re.compile(
        rf"^\d{{2,3}}-.*{re.escape(objective_slug)}.*\.md$", re.IGNORECASE
    )
    for path in canonical_dir.glob("*.md"):
        if number_prefix_pattern.match(path.name):
            return path

    # Pattern 2: any file containing the slug (or base slug without version)
    slug_variants = [objective_slug.lower(), base_slug]
    for slug_variant in slug_variants:
        slug_glob_patterns = [
            f"*{slug_variant.replace('-', '*')}*.md",
        ]
        for pattern in slug_glob_patterns:
            matches = list(canonical_dir.glob(pattern))
            numbered = [p for p in matches if re.match(r"^\d{2,3}-", p.name)]
            if numbered:
                return numbered[0]
            if matches:
                return matches[0]

    # Pattern 3: numbered docs where content title matches (strip version suffix)
    # Look for docs that have "MasterMind CLI" or similar in their content
    content_title_patterns = [
        objective_slug.replace("-", " ").replace("_", " ").title(),
        base_slug.replace("-", " ").replace("_", " ").title(),
    ]
    for path in canonical_dir.glob("*.md"):
        if not re.match(r"^\d{2,3}-", path.name):
            continue
        content = read_text(path)
        # Look for # Title or ## Title in the content
        title_match = re.search(r"^#+\s+(.+)$", content, re.MULTILINE)
        if title_match:
            doc_title = title_match.group(1).strip()
            for pattern in content_title_patterns:
                if pattern.lower() in doc_title.lower():
                    return path

    return None


def read_canonical_doc_enrichment(
    canonical_doc_path: Path, objective_name: str, objective_slug: str
) -> dict[str, str] | None:
    """Extract enriched content from a canonical doc for objective generation.

    Returns a dict with keys: purpose, scope, in_scope, out_of_scope,
    non_negotiables, architecture, commands_detail, tasks_section
    or None if the canonical doc doesn't have enough content.
    """
    content = read_text(canonical_doc_path)
    if not content:
        return None

    enrichment: dict[str, str] = {}

    # Extract ## Purpose or similar
    purpose_match = re.search(
        r"^##?\s*Purpose\s*\n+(.+?)(?=^##|\Z)", content, re.MULTILINE | re.DOTALL
    )
    if purpose_match:
        enrichment["purpose"] = purpose_match.group(1).strip()

    # Extract scope sections
    in_scope_match = re.search(
        r"^##?\s*In Scope\s*\n+(.*?)(?=^##?\s*Out|^-|^##|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if in_scope_match:
        lines = [
            ln.strip()
            for ln in in_scope_match.group(1).strip().splitlines()
            if ln.strip()
        ]
        enrichment["in_scope"] = "\n".join(
            f"- {ln}" if not ln.startswith("-") else ln for ln in lines
        )

    out_of_scope_match = re.search(
        r"^##?\s*Out of Scope\s*\n+(.*?)(?=^##|\Z)", content, re.MULTILINE | re.DOTALL
    )
    if out_of_scope_match:
        lines = [
            ln.strip()
            for ln in out_of_scope_match.group(1).strip().splitlines()
            if ln.strip()
        ]
        enrichment["out_of_scope"] = "\n".join(
            f"- {ln}" if not ln.startswith("-") else ln for ln in lines
        )

    # Extract Non-negotiables
    non_neg_match = re.search(
        r"^##?\s*Non-negotiables\s*\n+(.*?)(?=^##|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if non_neg_match:
        enrichment["non_negotiables"] = non_neg_match.group(1).strip()

    # Extract Architecture section
    arch_match = re.search(
        r"^##?\s*Arquitectura\s*\n+(.*?)(?=^##|\Z)", content, re.MULTILINE | re.DOTALL
    )
    if arch_match:
        enrichment["architecture"] = arch_match.group(1).strip()

    # Extract Commands section (for CLI objectives)
    commands_match = re.search(
        r"^##?\s*Comandos?\s*\n+\|(.*?)\|.*?\n+", content, re.MULTILINE
    )
    if commands_match:
        enrichment["commands_table"] = commands_match.group(0).strip()

    # Extract tasks if present (flexible: ## Tasks, ## Roadmap de Commands)
    # Look for sections that start with "## Tasks" or "## Roadmap de Commands"
    section_patterns = ["Tasks", "Roadmap de Commands"]
    for section_name in section_patterns:
        pattern = rf"(^##?\s+{re.escape(section_name)}.*?\n)(.*?)(?=^##\s|\Z)"
        tasks_match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if tasks_match:
            enrichment["tasks_section"] = tasks_match.group(0).strip()
            break

    return enrichment if enrichment else None


@dataclass
class ObjectiveCandidate:
    """Candidate objective discovered from one or more project sources."""

    slug: str
    name: str
    summary: str
    why_it_matters: str
    status: str
    mvp: bool
    evidence_sources: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    priority_score: int = 0


OBJECTIVE_SLUG_ALIASES: dict[str, str] = {
    "project-state": "project-state-mvp",
}


def canonical_objective_slug(slug: str) -> str:
    """Normalize known alias slugs to the canonical roadmap objective slug."""
    return OBJECTIVE_SLUG_ALIASES.get(slug, slug)


def read_text(path: Path) -> str:
    """Read UTF-8 text from a path, returning an empty string if absent."""
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def ensure_directory(path: Path) -> None:
    """Create a directory and its parents when missing."""
    path.mkdir(parents=True, exist_ok=True)


def load_active_objective_helpers() -> object:
    """Load shared active-objective helpers from the sibling module file."""
    module_path = Path(__file__).with_name("active-objective-state.py")
    spec = importlib.util.spec_from_file_location(
        "mm_active_objective_state", module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load active-objective helpers from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_gate_status_helpers() -> object:
    """Load shared gate-status helpers from the sibling module file."""
    module_path = Path(__file__).with_name("objective-gate-status.py")
    spec = importlib.util.spec_from_file_location(
        "mm_objective_gate_status", module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load gate-status helpers from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_GATE_STATUS_HELPERS = load_gate_status_helpers()
infer_objective_gate_status = _GATE_STATUS_HELPERS.infer_objective_gate_status
_ACTIVE_OBJECTIVE_HELPERS = load_active_objective_helpers()
active_objective_dirs = _ACTIVE_OBJECTIVE_HELPERS.active_objective_dirs
change_objective_status = _ACTIVE_OBJECTIVE_HELPERS.change_objective_status
find_active_objective_exception = (
    _ACTIVE_OBJECTIVE_HELPERS.find_active_objective_exception
)


def collect_handoff_candidates(root_dir: Path) -> list[ObjectiveCandidate]:
    """Collect active objective hints from handoff files."""
    candidates: list[ObjectiveCandidate] = []
    handoff_dir = get_planning_dir(root_dir)
    for handoff_path in sorted(handoff_dir.glob("HANDOFF-*.md")):
        if handoff_path.name == "HANDOFF-CURRENT.md":
            continue
        slug_source = handoff_path.stem.replace("HANDOFF-", "")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", slug_source):
            continue
        raw_slug = slugify(re.sub(r"-\d{4}-\d{2}-\d{2}$", "", slug_source))
        slug = canonical_objective_slug(raw_slug)
        text = read_text(handoff_path)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        goal_line = next((line for line in lines if line.startswith("## Goal")), "")
        summary = (
            lines[lines.index(goal_line) + 1]
            if goal_line and lines.index(goal_line) + 1 < len(lines)
            else ""
        )
        next_step_section = "Supports continuity for the next implementation slice."
        if "Best next steps" in text or "next steps" in text.lower():
            next_step_section = "Already has identified next implementation slices."
        status = "active"
        if raw_slug != slug:
            status = "stale"
            next_step_section = (
                "Historical handoff merged into the canonical objective alias."
            )
        candidates.append(
            ObjectiveCandidate(
                slug=slug,
                name=slug.replace("-", " ").title(),
                summary=summary
                or f"Continuation package derived from {handoff_path.name}.",
                why_it_matters=next_step_section,
                status=status,
                mvp=True,
                evidence_sources=[str(handoff_path.relative_to(root_dir))],
            )
        )
    return candidates


def collect_change_directory_candidates(root_dir: Path) -> list[ObjectiveCandidate]:
    """Collect objectives from active and archived per-objective planning directories."""
    candidates: list[ObjectiveCandidate] = []
    planning_dir = get_planning_dir(root_dir)
    for state_dir, status in (
        (planning_dir / "changes", "active"),
        (planning_dir / "archive" / "objectives", "done"),
    ):
        if not state_dir.exists():
            continue
        for child in sorted(state_dir.iterdir()):
            if not child.is_dir() or child.name.startswith("_"):
                continue
            slug = canonical_objective_slug(child.name)
            summary = f"Planning package present in {child.relative_to(root_dir)}."
            child_status = status
            if state_dir.name == "changes":
                child_status = change_objective_status(root_dir, child)
            dependencies = execution_state_objective_dependencies(child)
            candidates.append(
                ObjectiveCandidate(
                    slug=slug,
                    name=slug.replace("-", " ").title(),
                    summary=summary,
                    why_it_matters="Structured planning package already exists.",
                    status=child_status,
                    mvp=True,
                    dependencies=dependencies,
                    evidence_sources=[str(child.relative_to(root_dir))],
                )
            )
    return candidates


def execution_state_objective_dependencies(objective_dir: Path) -> list[str]:
    """Return external objective dependencies declared by root tasks."""
    state_path = objective_dir / "execution-state.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []
    if not isinstance(state, dict) or not isinstance(state.get("tasks"), dict):
        return []

    tasks = state["tasks"]
    task_ids = set(tasks)
    dependencies: set[str] = set()
    for task in tasks.values():
        if not isinstance(task, dict) or not isinstance(task.get("depends_on"), list):
            continue
        dependencies.update(
            canonical_objective_slug(dependency)
            for dependency in task["depends_on"]
            if isinstance(dependency, str) and dependency not in task_ids
        )
    return sorted(dependencies)


def completed_legacy_phase_sources(root_dir: Path) -> dict[str, list[str]]:
    """Return legacy task files that prove a phase completed in the old ledger."""
    planning_dir = get_planning_dir(root_dir)
    sources: dict[str, list[str]] = {}
    for todo_path in sorted((planning_dir / "archive" / "legacy").glob("**/todo.md")):
        text = read_text(todo_path)
        for match in re.finditer(
            r"^##\s+PHASE\s+(?P<id>[0-9.]+):.*?(?=^##\s+PHASE\s+|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        ):
            phase_id = match.group("id")
            if re.search(
                rf"^-\s+\[x\]\s+{re.escape(phase_id)}:",
                match.group(0),
                re.MULTILINE,
            ):
                sources.setdefault(phase_id, []).append(
                    str(todo_path.relative_to(root_dir))
                )
    return sources


def collect_phase_candidates(root_dir: Path) -> list[ObjectiveCandidate]:
    """Collect major workstreams from roadmap/source-of-truth phase headings."""
    candidates: list[ObjectiveCandidate] = []
    planning_dir = get_planning_dir(root_dir)
    legacy_completed = completed_legacy_phase_sources(root_dir)
    candidate_files = [
        planning_dir / "SOURCE-OF-TRUTH.md",
        planning_dir / "ROADMAP.md",
        planning_dir / "ROADMAP-v3.2.md",
    ]
    phase_pattern = re.compile(
        r"^#{2,6}\s+Phase\s+(?P<id>[0-9.]+):\s+(?P<name>.+?)(?:\s+[✅🔄⏳].*)?$",
        re.MULTILINE,
    )
    for path in candidate_files:
        text = read_text(path)
        if not text:
            continue
        for match in phase_pattern.finditer(text):
            phase_id = match.group("id")
            phase_name = match.group("name").strip()
            phase_slug = canonical_objective_slug(slugify(phase_name))
            block = text[match.start() : match.start() + 600]
            status = "planned"
            if "complete" in block.lower() or "✅" in block:
                status = "done"
            elif "in progress" in block.lower() or "🔄" in block:
                status = "active"
            legacy_sources = legacy_completed.get(phase_id, [])
            if legacy_sources:
                status = "done"
            goal_match = re.search(r"\*\*Goal:\*\*\s*(.+)", block)
            summary = (
                goal_match.group(1).strip()
                if goal_match
                else f"Phase objective: {phase_name}."
            )
            candidates.append(
                ObjectiveCandidate(
                    slug=phase_slug,
                    name=phase_name,
                    summary=summary,
                    why_it_matters=(
                        "Completed in the legacy task ledger."
                        if legacy_sources
                        else "Declared roadmap phase in planning sources."
                    ),
                    status=status,
                    mvp=True,
                    evidence_sources=[str(path.relative_to(root_dir)), *legacy_sources],
                )
            )
    return candidates


def collect_canonical_candidates(root_dir: Path) -> list[ObjectiveCandidate]:
    """Collect candidate objectives from implementation-oriented canonical docs."""
    candidates: list[ObjectiveCandidate] = []
    canonical_dir = root_dir / "docs" / "canonical"
    if not canonical_dir.exists():
        return candidates

    objective_docs: dict[str, tuple[str, str]] = {
        "window-scheduler": (
            "Window Scheduler",
            "Subscription-window-aware backend switching, checkpointing, and morning reports.",
        ),
        "context-window-management": (
            "Context Window Management",
            "Manage context-fit, packing, and compression across model backends.",
        ),
        "project-state-mvp": (
            "Project State MVP",
            "Operational memory, project state, dashboard, and write-side continuity layer.",
        ),
        "engineering-doctrine-layer": (
            "Engineering Doctrine Layer",
            "Persistent methodology, architecture rules, and phase gates for agents and humans.",
        ),
        "collaboration-rbac": (
            "Collaboration and RBAC",
            "Human + agent participation model with explicit roles and permissions.",
        ),
        "task-time-and-estimation": (
            "Task Time and Estimation",
            "Track effort, ETA, and estimation quality over time.",
        ),
        "token-cost-quality-telemetry": (
            "Token Cost and Quality Telemetry",
            "Track token usage, cost, and output quality trends by project and task.",
        ),
        "artifact-versioning-and-lineage": (
            "Artifact Versioning and Lineage",
            "Preserve causality between specs, tasks, decisions, and implementation state.",
        ),
        "postgres-hybrid-data-model": (
            "Postgres Hybrid Data Model",
            "Relational core + JSONB + vector memory for project state and retrieval.",
        ),
        "context-projection": (
            "Context Projection",
            "Build model-ready context from structured project state instead of chat history.",
        ),
        "dashboard-realtime": (
            "Dashboard Realtime",
            "Realtime events and live visibility for project operations.",
        ),
        "backend-service-boundary-for-agents": (
            "Backend Service Boundary For Agents",
            "Models interact through semantic services instead of direct database access.",
        ),
        "rust-control-plane-hardening": (
            "Rust Control Plane Hardening",
            "Stabilize and harden the canonical Rust control plane before further expansion.",
        ),
    }

    for slug, (name, summary) in objective_docs.items():
        slug = canonical_objective_slug(slug)
        matched_files = list(
            canonical_dir.glob(
                f"*{slug.upper().replace('-', '*').replace('_', '*')}*.md"
            )
        )
        if not matched_files:
            matched_files = [
                path
                for path in canonical_dir.glob("*.md")
                if slug.replace("-", " ").lower() in path.stem.replace("-", " ").lower()
            ]
        if not matched_files:
            continue
        evidence = [str(path.relative_to(root_dir)) for path in matched_files[:3]]
        candidates.append(
            ObjectiveCandidate(
                slug=slug,
                name=name,
                summary=summary,
                why_it_matters="Captured in canonical implementation docs.",
                status="planned",
                mvp=True,
                evidence_sources=evidence,
            )
        )
    return candidates


def dependency_hints(slug: str) -> list[str]:
    """Return lightweight dependency hints for known objectives."""
    slug = canonical_objective_slug(slug)
    hints: dict[str, list[str]] = {
        "project-state-realtime": ["project-state-mvp", "dashboard-realtime"],
        "dashboard-realtime": ["project-state-mvp"],
        "context-window-management": ["window-scheduler"],
        "engineering-doctrine-layer": ["project-state-mvp"],
        "collaboration-rbac": ["project-state-mvp"],
        "task-time-and-estimation": ["project-state-mvp"],
        "token-cost-quality-telemetry": ["project-state-mvp"],
        "artifact-versioning-and-lineage": ["project-state-mvp"],
        "postgres-hybrid-data-model": ["project-state-mvp"],
        "context-projection": ["project-state-mvp", "postgres-hybrid-data-model"],
        "backend-service-boundary-for-agents": ["project-state-mvp"],
        "rust-control-plane-hardening": ["backend-service-boundary-for-agents"],
    }
    return hints.get(slug, [])


def priority_hints(slug: str) -> int:
    """Return a deterministic priority hint for known objectives.

    Higher scores mean the objective should be preferred earlier once dependencies
    are satisfied. This encodes the repo's current architecture-first sequencing.
    """
    slug = canonical_objective_slug(slug)
    hints: dict[str, int] = {
        "backend-service-boundary-for-agents": 95,
        "postgres-hybrid-data-model": 92,
        "harness-stage-execution-runtime": 89,
        "domain-security-assurance-plane": 88,
        "adaptive-delivery-harness-runtime": 87,
        "engineering-doctrine-layer": 86,
        "token-cost-quality-telemetry": 84,
        "collaboration-rbac": 82,
        "dashboard-realtime": 78,
        "window-scheduler": 76,
        "context-window-management": 74,
        "context-projection": 72,
        "rust-control-plane-hardening": 70,
        "rust-control-plane": 68,
        "observability-real-time-hub": 66,
        "knowledge-distillation": 62,
        "knowledge-ingestion-manual": 60,
        "multi-channel-gateway": 58,
        "pgvector-schema-langsmith-foundation-paralelo": 56,
        "task-time-and-estimation": 55,
        "rag-evaluation-gate": 54,
        "rag-pilot-brain-1-only": 53,
        "rag-scale-out-brains-2-7": 52,
        "vertical-slice": 50,
    }
    return hints.get(slug, 40)


def status_priority(status: str) -> int:
    """Return precedence for merging and ordering statuses."""
    rank = {
        "active": 5,
        "done": 4,
        "missing-but-required": 3,
        "planned": 2,
        "deferred": 1,
        "stale": 0,
    }
    return rank.get(status, -1)


def compute_ready_now(
    objective: ObjectiveCandidate, all_objectives: list[ObjectiveCandidate]
) -> bool:
    """Return True when an objective has no unresolved dependencies and is not done."""
    if objective.status in {"done", "stale"}:
        return False
    if objective.status == "active":
        return True

    done_or_active = {
        item.slug for item in all_objectives if item.status in {"done", "active"}
    }
    return all(dependency in done_or_active for dependency in objective.dependencies)


def count_unlocks(slug: str, objectives: list[ObjectiveCandidate]) -> int:
    """Count downstream objectives that depend directly on the given slug."""
    return sum(1 for objective in objectives if slug in objective.dependencies)


def unblock_priority_reason(
    objective: ObjectiveCandidate,
    objectives: list[ObjectiveCandidate],
    gate_status: str,
) -> str:
    """Return deterministic reasoning for why a blocked objective should be unblocked first."""
    unlocks = count_unlocks(objective.slug, objectives)
    return (
        f"highest priority among blocked ready candidates "
        f"(priority={objective.priority_score}, unlocks={unlocks}, gate status={gate_status})"
    )


def is_activation_ready_objective(root_dir: Path, objective_slug: str) -> bool:
    """Return whether an objective is activation-ready from the gate perspective."""
    gate_status, _, _ = infer_objective_gate_status(root_dir, objective_slug)
    return gate_status in {"NO_CANONICAL", "PASSED"}


def choose_recommended_next(
    objectives: list[ObjectiveCandidate], root_dir: Path
) -> ObjectiveCandidate | None:
    """Choose the deterministic next objective to activate."""
    active = [objective for objective in objectives if objective.status == "active"]
    if active:
        return sorted(
            active,
            key=lambda item: (-item.priority_score, item.slug),
        )[0]

    ready = [
        objective
        for objective in objectives
        if objective.status in {"planned", "missing-but-required"}
        and compute_ready_now(objective, objectives)
    ]
    if not ready:
        return None

    gate_ready = [
        objective
        for objective in ready
        if is_activation_ready_objective(root_dir, objective.slug)
    ]
    candidate_pool = gate_ready or ready

    return sorted(
        candidate_pool,
        key=lambda item: (
            -item.priority_score,
            -count_unlocks(item.slug, objectives),
            item.slug,
        ),
    )[0]


def reconcile_candidates(
    candidates: list[ObjectiveCandidate],
) -> list[ObjectiveCandidate]:
    """Merge duplicated candidates and normalize status/evidence/dependencies."""
    merged: dict[str, ObjectiveCandidate] = {}

    for candidate in candidates:
        candidate.slug = canonical_objective_slug(candidate.slug)
        candidate.dependencies = [
            canonical_objective_slug(dependency)
            for dependency in candidate.dependencies
        ]
        candidate.priority_score = priority_hints(candidate.slug)
        existing = merged.get(candidate.slug)
        if existing is None:
            candidate.dependencies = sorted(
                set(candidate.dependencies + dependency_hints(candidate.slug))
            )
            merged[candidate.slug] = candidate
            continue

        if status_priority(candidate.status) > status_priority(existing.status):
            existing.status = candidate.status
        if len(candidate.summary) > len(existing.summary):
            existing.summary = candidate.summary
        if len(candidate.why_it_matters) > len(existing.why_it_matters):
            existing.why_it_matters = candidate.why_it_matters
        existing.mvp = existing.mvp or candidate.mvp
        existing.priority_score = max(existing.priority_score, candidate.priority_score)
        existing.evidence_sources = sorted(
            set(existing.evidence_sources + candidate.evidence_sources)
        )
        existing.dependencies = sorted(
            set(
                existing.dependencies
                + candidate.dependencies
                + dependency_hints(existing.slug)
            )
        )

    ordered = sorted(
        merged.values(),
        key=lambda item: (
            -status_priority(item.status),
            -item.priority_score,
            item.slug,
        ),
    )

    for index, objective in enumerate(ordered, start=1):
        objective.name = objective.name.strip()
        objective.summary = objective.summary.strip()
        objective.why_it_matters = objective.why_it_matters.strip()
        objective.evidence_sources = objective.evidence_sources[:6]
        if objective.status == "planned" and objective.slug == "project-state-mvp":
            objective.status = "active"
    return ordered


def build_roadmap_candidates(root_dir: Path) -> list[ObjectiveCandidate]:
    """Build the reconciled roadmap candidates for the current repository."""
    candidates: list[ObjectiveCandidate] = []
    candidates.extend(collect_handoff_candidates(root_dir))
    candidates.extend(collect_change_directory_candidates(root_dir))
    candidates.extend(collect_phase_candidates(root_dir))
    candidates.extend(collect_canonical_candidates(root_dir))
    return reconcile_candidates(candidates)


def write_roadmap_files(root_dir: Path, payload: dict[str, object]) -> list[Path]:
    """Materialize the roadmap outputs for roadmap discovery mode."""
    roadmap_dir = Path(str(payload["roadmap_dir"]))
    ensure_directory(roadmap_dir)
    objectives = build_roadmap_candidates(root_dir)
    recommended_next = choose_recommended_next(objectives, root_dir)
    recommended_blocked_fallback = (
        recommended_next is not None
        and not is_activation_ready_objective(root_dir, recommended_next.slug)
    )
    active_objectives = [obj for obj in objectives if obj.status == "active"]
    done_objectives = [obj for obj in objectives if obj.status == "done"]
    pending_objectives = [
        obj for obj in objectives if obj.status not in {"active", "done", "stale"}
    ]

    objectives_md = roadmap_dir / "objectives.md"
    dependency_graph_md = roadmap_dir / "dependency-graph.md"
    objectives_json = roadmap_dir / "objectives.json"

    lines = [
        "# Objective Roadmap",
        "",
        f"_Generated: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        "## Recommended next objective",
        "",
        f"- `{recommended_next.slug}`" if recommended_next else "- `none`",
        (
            (
                f"- Why: all dependency-ready objectives are currently gate-blocked; "
                f"`{recommended_next.slug}` remains the highest deterministic fallback "
                f"({recommended_next.priority_score}) until one candidate becomes gate-ready."
            )
            if recommended_blocked_fallback
            else (
                f"- Why: ready now, highest deterministic priority ({recommended_next.priority_score}), "
                f"unlocks {count_unlocks(recommended_next.slug, objectives)} downstream objective(s)."
            )
        )
        if recommended_next
        else "- Why: no ready objective could be derived from current dependencies.",
        "",
        "## Status summary",
        "",
        f"- Active: {len(active_objectives)}",
        f"- Planned/blocked: {len(pending_objectives)}",
        f"- Done: {len(done_objectives)}",
        "",
        "| Rank | Objective | Status | Ready Now | Gate | Priority | Recommended | MVP | Dependencies | Why it matters | Evidence |",
        "|---:|---|---|---|---|---:|---|---|---|---|---|",
    ]
    objective_payload: list[dict[str, object]] = []
    display_order = sorted(
        objectives,
        key=lambda item: (
            0
            if item.status == "active"
            else 1
            if compute_ready_now(item, objectives)
            else 2
            if item.status != "done"
            else 3,
            -item.priority_score,
            -count_unlocks(item.slug, objectives),
            item.slug,
        ),
    )
    for index, objective in enumerate(display_order, start=1):
        deps = ", ".join(objective.dependencies) if objective.dependencies else "—"
        evidence = (
            ", ".join(objective.evidence_sources) if objective.evidence_sources else "—"
        )
        ready_now = compute_ready_now(objective, objectives)
        gate_status, gate_guidance, gate_artifact = infer_objective_gate_status(
            root_dir, objective.slug
        )
        recommended = (
            recommended_next is not None and objective.slug == recommended_next.slug
        )
        blocked_reason = (
            unblock_priority_reason(objective, objectives, gate_status)
            if recommended and recommended_blocked_fallback
            else ""
        )
        lines.append(
            f"| {index} | `{objective.slug}` | {objective.status} | {'yes' if ready_now else 'no'} | {gate_status.lower() if gate_status != 'NO_CANONICAL' else 'n/a'} | {objective.priority_score} | {'yes' if recommended else 'no'} | {'yes' if objective.mvp else 'no'} | {deps} | {objective.why_it_matters} | {evidence} |"
        )
        objective_payload.append(
            {
                "rank": index,
                "stable_id": objective.slug,
                "slug": objective.slug,
                "name": objective.name,
                "summary": objective.summary,
                "status": objective.status,
                "ready_now": ready_now,
                "priority_score": objective.priority_score,
                "recommended_next": recommended,
                "mvp": objective.mvp,
                "dependencies": objective.dependencies,
                "why_it_matters": objective.why_it_matters,
                "evidence_sources": objective.evidence_sources,
                "gate_status": gate_status,
                "gate_guidance": gate_guidance,
                "gate_artifact": gate_artifact,
                "recommended_blocked_fallback": recommended
                and recommended_blocked_fallback,
                "unblock_priority_reason": blocked_reason,
            }
        )
    objectives_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    graph_lines = [
        "# Objective Dependency Graph",
        "",
        "## Edges",
        "",
    ]
    for objective in objectives:
        if not objective.dependencies:
            graph_lines.append(f"- `{objective.slug}` has no declared prerequisites")
        for dependency in objective.dependencies:
            graph_lines.append(f"- `{dependency}` -> `{objective.slug}`")
    graph_lines.extend(
        [
            "",
            "## Recommended next active objective",
            "",
            f"- `{recommended_next.slug if recommended_next else 'none'}`",
        ]
    )
    dependency_graph_md.write_text("\n".join(graph_lines) + "\n", encoding="utf-8")
    objectives_json.write_text(
        json.dumps(objective_payload, indent=2), encoding="utf-8"
    )

    current_handoff_path = get_planning_dir(root_dir) / "HANDOFF-CURRENT.md"
    if objectives:
        next_objective = recommended_next or display_order[0]
        next_gate_status, next_gate_guidance, _ = infer_objective_gate_status(
            root_dir, next_objective.slug
        )
        handoff_text = "\n".join(
            [
                f"# Handoff — {next_objective.name}",
                "",
                "## Current objective",
                f"- `{next_objective.slug}`",
                "",
                "## Decisions already made",
                "- Roadmap is derived from explicit intent, planning state, decision history, and implementation reality.",
                "- Only one objective package should be actively expanded at a time unless parallel tracks are explicitly justified.",
                *(
                    [
                        "- All dependency-ready objectives are currently gate-blocked, so the roadmap is surfacing the least-bad fallback recommendation instead of a directly activatable one."
                    ]
                    if recommended_blocked_fallback
                    else []
                ),
                *(
                    [
                        f"- Unblock priority reason: {unblock_priority_reason(next_objective, objectives, next_gate_status)}"
                    ]
                    if recommended_blocked_fallback
                    else []
                ),
                "",
                "## Blockers / risks",
                "- Roadmap is heuristic and should be refined when new canonical docs or handoffs appear.",
                "- Legacy global discovery files still coexist with the target per-objective package model.",
                *(
                    [
                        f"- Gate status for recommended objective: {next_gate_status}",
                        f"- {next_gate_guidance}",
                    ]
                    if next_gate_status != "NO_CANONICAL"
                    else []
                ),
                "",
                "## Exact next recommended task",
                *(
                    [
                        f"- Run `/mm:objective-context-check --objective {next_objective.slug}` before activating this objective.",
                        f'- After the gate passes, run `/mm:discover --existing --objective {next_objective.slug} "{next_objective.name}"` to generate the active objective package.',
                    ]
                    if next_gate_status not in {"NO_CANONICAL", "PASSED"}
                    else [
                        f'- Run `/mm:discover --existing --objective {next_objective.slug} "{next_objective.name}"` to generate the active objective package.'
                    ]
                ),
                f"- This objective is ready now and carries priority score {next_objective.priority_score}.",
                "",
                "## Validation commands",
                f"- `/mm:discover-contract-check --objective {next_objective.slug}`",
                f"- Verify `{roadmap_dir.relative_to(root_dir) / 'objectives.md'}` and `{roadmap_dir.relative_to(root_dir) / 'dependency-graph.md'}` were generated",
            ]
        )
        current_handoff_path.write_text(handoff_text + "\n", encoding="utf-8")

    return [objectives_md, dependency_graph_md, objectives_json]


def objective_template(payload: dict[str, object], root_dir: Path) -> dict[str, str]:
    """Build templated content for an objective package."""
    objective_name = str(payload["objective_name"])
    objective_slug = str(payload["objective_slug"])
    objective_brief = str(payload.get("objective_brief") or "").strip()
    planning_dir = get_planning_dir(root_dir)
    source_of_truth = read_text(planning_dir / "SOURCE-OF-TRUTH.md")
    project_state_handoff = read_text(
        planning_dir / "HANDOFF-PROJECT-STATE-2026-05-24.md"
    )

    # Check for a canonical doc to enrich the objective
    canonical_doc = find_canonical_doc_for_objective(root_dir, objective_slug)
    canonical_enrichment = None
    if canonical_doc:
        canonical_enrichment = read_canonical_doc_enrichment(
            canonical_doc, objective_name, objective_slug
        )

    summary = (
        objective_brief
        or f"Advance the `{objective_slug}` workstream in an execution-ready way."
    )
    scope_lines = [
        "- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.",
        "- Preserve backend-authority boundaries and the current incremental architecture.",
    ]
    out_of_scope_lines = [
        "- No unrelated rewrites or speculative refactors.",
        "- Do not bypass backend services with direct model/database access.",
    ]
    task_sections: list[dict[str, object]]

    if objective_slug == "project-state-mvp":
        summary = (
            objective_brief
            or "Continue the Project State MVP with realtime, richer write-side actions, and project_state-native auditability."
        )
        scope_lines = [
            "- Extend the current `project_state` thin slice without breaking existing endpoints or `/project-state` UI.",
            "- Prefer incremental backend + UI enhancements over large rewrites.",
            "- Keep PostgreSQL as the target architecture and avoid expanding legacy sqlite paths.",
        ]
        task_sections = [
            {
                "id": "PS1",
                "title": "Realtime events for project_state",
                "purpose": "Add explicit realtime signaling so the dashboard can observe project_state changes without relying only on periodic refresh.",
                "depends_on": [],
                "parallelizable": False,
                "files_touched": [
                    "apps/api/mastermind_cli/api/routes/project_overview.py",
                    "apps/api/mastermind_cli/project_state/services/project_overview.py",
                    "apps/web/src/components/project-state/ProjectStateLiveShell.tsx",
                ],
                "validation_commands": [
                    "cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_activity_feed.py tests/api/test_project_runs.py",
                    "cd apps/web && pnpm exec tsc --noEmit",
                ],
                "acceptance": [
                    "Backend emits project_state-relevant realtime events through an explicit contract.",
                    "`/project-state` can subscribe or refresh from realtime signals without degrading current functionality.",
                    "Validation commands for API/web changes are documented and pass.",
                ],
            },
            {
                "id": "PS2",
                "title": "Richer write-side operations",
                "purpose": "Expand the dashboard from passive observability to more operational project-state actions.",
                "depends_on": ["PS1"],
                "parallelizable": False,
                "files_touched": [
                    "apps/api/mastermind_cli/api/routes/project_overview.py",
                    "apps/web/src/app/actions/project-state.ts",
                    "apps/web/src/components/project-state/ProjectStateWritePanel.tsx",
                ],
                "validation_commands": [
                    "cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_write_side.py",
                    "cd apps/web && pnpm exec eslint src/app/actions/project-state.ts src/components/project-state/ProjectStateWritePanel.tsx",
                ],
                "acceptance": [
                    "At least one additional write-side action exists (task status, notes, or handoff).",
                    "The action respects backend authority and is visible in the dashboard.",
                    "Tests or targeted validation cover the new action.",
                ],
            },
            {
                "id": "PS3",
                "title": "Replace transitional audit gap",
                "purpose": "Remove the temporary audit skip and replace it with project_state-native activity/audit logging.",
                "depends_on": ["PS1", "PS2"],
                "parallelizable": False,
                "files_touched": [
                    "apps/api/mastermind_cli/api/app.py",
                    "apps/api/mastermind_cli/project_state/repositories",
                    "apps/api/mastermind_cli/project_state/services/project_overview.py",
                ],
                "validation_commands": [
                    "cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_write_side.py tests/api/test_project_activity_feed.py",
                ],
                "acceptance": [
                    "`/api/projects` write-side routes are no longer hidden behind a transitional audit skip.",
                    "project_state-native activity/audit events capture the key write-side actions.",
                    "The change is validated without regressing existing project_state flows.",
                ],
            },
        ]
    else:
        task_sections = [
            {
                "id": "T1",
                "title": "Define and stabilize the slice",
                "purpose": "Clarify the exact objective boundary before implementation expands.",
                "depends_on": [],
                "parallelizable": False,
                "files_touched": ["requirements.md", "design.md", "tasks.md"],
                "validation_commands": [
                    "Review requirements/design/tasks package for consistency."
                ],
                "acceptance": [
                    "The exact boundary of the objective is implemented or tightened.",
                    "Existing architecture constraints are preserved and documented.",
                ],
            },
            {
                "id": "T2",
                "title": "Implement the smallest coherent deliverable",
                "purpose": "Land the core behavior that proves the objective is advancing.",
                "depends_on": ["T1"],
                "parallelizable": False,
                "files_touched": ["implementation-specific files"],
                "validation_commands": [
                    "Run targeted validation commands for the touched area."
                ],
                "acceptance": [
                    "The main user-visible or system-visible behavior exists.",
                    "Tests or validation commands demonstrate the behavior.",
                ],
            },
            {
                "id": "T3",
                "title": "Close the continuity loop",
                "purpose": "Refresh handoff and validation context for the next model/session.",
                "depends_on": ["T2"],
                "parallelizable": False,
                "files_touched": ["HANDOFF-CURRENT.md", "tasks.md", "todo.md"],
                "validation_commands": [
                    "Refresh handoff and rerun discovery contract check."
                ],
                "acceptance": [
                    "Handoff notes are refreshed with next recommended work.",
                    "Validation commands are documented and pass.",
                ],
            },
        ]

    context_notes = []
    if source_of_truth:
        context_notes.append(
            f"- Source of truth exists in `{PLANNING_LABEL}/SOURCE-OF-TRUTH.md` and should guide intent reconciliation."
        )
    if project_state_handoff and objective_slug.startswith("project-state"):
        context_notes.append(
            f"- `{PLANNING_LABEL}/HANDOFF-PROJECT-STATE-2026-05-24.md` provides concrete current-state guidance for this workstream."
        )
    dependency_lines = [
        f"- Depends on `{dependency}`"
        for dependency in dependency_hints(objective_slug)
    ] or ["- No explicit upstream dependency declared"]
    context_note_lines = context_notes or ["- No additional context note available."]

    # Build requirements — use canonical enrichment if available
    if canonical_enrichment and canonical_enrichment.get("purpose"):
        req_lines = [
            f"# Requirements — {objective_name}",
            "",
            "## Problem / Purpose",
            canonical_enrichment.get("purpose", summary),
            "",
        ]
        if canonical_enrichment.get("in_scope"):
            req_lines.extend(["", "## Scope", canonical_enrichment["in_scope"]])
        if canonical_enrichment.get("out_of_scope"):
            req_lines.extend(
                ["", "## Out of Scope", canonical_enrichment["out_of_scope"]]
            )
        if canonical_enrichment.get("non_negotiables"):
            req_lines.extend(
                ["", "## Non-negotiables", canonical_enrichment["non_negotiables"]]
            )
        if canonical_enrichment.get("commands_table"):
            req_lines.extend(
                ["", "## Dual Interface", canonical_enrichment["commands_table"]]
            )
        if canonical_enrichment.get("tasks_section"):
            req_lines.extend(
                ["", "## Planned Tasks", canonical_enrichment["tasks_section"]]
            )
        req_lines.extend(
            [
                "",
                "## Objective-level Acceptance Criteria",
                "- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.",
                "- [ ] The implementation slice advances the target objective without breaking adjacent flows.",
                "- [ ] Validation commands are documented and usable by another model or human operator.",
                "",
                f"_Enriched from canonical doc: `{canonical_doc.name}`_",
            ]
        )
        requirements = "\n".join(req_lines)
    else:
        requirements = "\n".join(
            [
                f"# Requirements — {objective_name}",
                "",
                "## Problem / Purpose",
                summary,
                "",
                "## Stakeholders / Users",
                "- Primary: repository maintainers and future execution models",
                "- Secondary: human operators using the `/project-state` console or MM planning commands",
                "",
                "## Scope",
                *scope_lines,
                "",
                "## Out of Scope",
                *out_of_scope_lines,
                "",
                "## Non-negotiables",
                "- Preserve a model/provider-agnostic harness direction.",
                "- Keep the backend as the authority for state, validation, and auditability.",
                "- Do not introduce unstructured chat-only continuity as the primary workflow.",
                "",
                "## Objective-level Acceptance Criteria",
                "- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.",
                "- [ ] The implementation slice advances the target objective without breaking adjacent flows.",
                "- [ ] Validation commands are documented and usable by another model or human operator.",
            ]
        )

    # Build design — use canonical enrichment if available
    if canonical_enrichment and canonical_enrichment.get("architecture"):
        design_lines = [
            f"# Design — {objective_name}",
            "",
            "## Arquitectura",
            canonical_enrichment["architecture"],
        ]
        if canonical_enrichment.get("commands_table"):
            design_lines.extend(
                [
                    "",
                    "## Dual Interface",
                    "",
                    "```",
                    "CLI + Slash Command → Same Handler",
                    "```",
                    "",
                    canonical_enrichment["commands_table"],
                ]
            )
        design_lines.extend(
            [
                "",
                "## Dependencies",
                *dependency_lines,
                "",
                "## Validation Strategy",
                "- Run targeted Python tests or validation commands for touched areas.",
                "- Run relevant web lint/typecheck commands when frontend files change.",
                "- Refresh handoff state after completing or partially completing the objective.",
            ]
        )
        design = "\n".join(design_lines)
    else:
        design = "\n".join(
            [
                f"# Design — {objective_name}",
                "",
                "## Architecture / Boundaries",
                "- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.",
                "- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.",
                "",
                "## Technical Approach",
                "- Build the smallest coherent vertical slice that satisfies the acceptance criteria.",
                "- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.",
                "",
                "## Dependencies",
                *dependency_lines,
                "",
                "## Validation Strategy",
                "- Run targeted Python tests or validation commands for touched areas.",
                "- Run relevant web lint/typecheck commands when frontend files change.",
                "- Refresh handoff state after completing or partially completing the objective.",
                "",
                "## Important Tradeoffs",
                "- Prefer execution-ready specificity over speculative completeness.",
                "- Prefer incremental compatibility over large migration bursts.",
                "",
                "## Context Notes",
                *context_note_lines,
            ]
        )

    task_lines = [
        f"# Tasks — {objective_name}",
        "",
        "## Execution Rules",
        "- Execute tasks in dependency order unless parallelization is explicitly safe.",
        "- Update this file and the handoff when a task is completed or blocked.",
        "- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.",
        "",
    ]
    for section in task_sections:
        execution_subtasks: list[str] = []
        task_lines.extend(
            [
                f"## {section['id']}: {section['title']}",
                "",
                *(
                    [
                        "### Execution Subtasks",
                        *[f"- {item}" for item in execution_subtasks],
                        "",
                    ]
                    if execution_subtasks
                    else []
                ),
                "### Purpose",
                str(section["purpose"]),
                "",
                "### Depends On",
                ", ".join(section["depends_on"]) if section["depends_on"] else "None",
                "",
                "### Parallelizable",
                "yes" if section["parallelizable"] else "no",
                "",
                "### Files / Areas Likely Touched",
                *[f"- {item}" for item in section["files_touched"]],
                "",
                "### Validation Commands",
                *[f"- {item}" for item in section["validation_commands"]],
                "",
                "### Acceptance Criteria",
                *[f"- [ ] {item}" for item in section["acceptance"]],
                "",
            ]
        )
    tasks = "\n".join(task_lines)

    handoff = "\n".join(
        [
            f"# Handoff — {objective_name}",
            "",
            "## Current objective",
            f"- `{objective_slug}`",
            "",
            "## Decisions already made",
            "- Use a per-objective planning package instead of relying on a single root planning surface forever.",
            "- Another model should be able to resume from artifacts, not from chat memory alone.",
            "",
            "## Blockers / risks",
            "- The package is scaffolded from repository evidence and may need refinement for deeper implementation context.",
            "- Historical legacy material may still exist under archive/legacy, but it is not part of the active workflow.",
            "",
            "## Exact next recommended task",
            f"- Start with `{('PS1' if objective_slug == 'project-state-mvp' else 'T1')}` from `tasks.md`.",
            "",
            "## Validation commands",
            f"- `/mm:discover-contract-check --objective {objective_slug}`",
            "- Run targeted tests for touched files before handing off again",
        ]
    )

    return {
        "requirements.md": requirements + "\n",
        "design.md": design + "\n",
        "tasks.md": tasks + "\n",
        "HANDOFF-CURRENT.md": handoff + "\n",
    }


def write_objective_package(root_dir: Path, payload: dict[str, object]) -> list[Path]:
    """Materialize the objective package for objective discovery mode."""
    objective_slug = validate_objective_slug(str(payload["objective_slug"]))
    changes_dir = (get_planning_dir(root_dir) / "changes").resolve()
    changes_dir.mkdir(parents=True, exist_ok=True)
    target_dir = Path(str(payload["target_dir"]))
    resolved_target = target_dir.resolve(strict=False)
    try:
        relative = resolved_target.relative_to(changes_dir)
    except ValueError as exc:
        raise ValueError(
            "Objective target failed changes-directory containment"
        ) from exc
    if relative.parts != (objective_slug,):
        raise ValueError("Objective target failed changes-directory containment")
    ensure_directory(target_dir)
    existing_paths = sorted(path for path in target_dir.iterdir() if path.is_file())
    if existing_paths:
        required = {
            "requirements.md",
            "design.md",
            "tasks.md",
            "todo.md",
            "HANDOFF-CURRENT.md",
        }
        missing = sorted(required - {path.name for path in existing_paths})
        if missing:
            raise ValueError(
                "Partial objective package is missing required files: "
                + ", ".join(missing)
            )
        for path in existing_paths:
            try:
                path.resolve().relative_to(resolved_target)
            except ValueError as exc:
                raise ValueError("Objective artifact failed containment") from exc
        return existing_paths
    files = objective_template(payload, root_dir)
    written_paths: list[Path] = []
    for filename, content in files.items():
        file_path = target_dir / filename
        file_path.write_text(content, encoding="utf-8")
        written_paths.append(file_path)

    tasks_text = files["tasks.md"]
    task_matches = re.findall(
        r"^##\s+([A-Z]{1,4}\d+):\s*(.+)$", tasks_text, re.MULTILINE
    )
    if task_matches:
        todo_lines = [
            f"# Todo — {payload['objective_name']}",
            "",
            "<!-- topology-source: tasks.md -->",
            "",
            "## Execution Checklist",
            "",
        ]
        details_by_task: dict[str, dict[str, object]] = {}
        for task_id, _ in task_matches:
            block_match = re.search(
                rf"^##\s+{re.escape(task_id)}:.*?(?=^##\s+[A-Z]{{1,4}}\d+:|\Z)",
                tasks_text,
                re.MULTILINE | re.DOTALL,
            )
            block = block_match.group(0) if block_match else ""
            depends_match = re.search(r"### Depends On\n(.+?)\n\n", block, re.DOTALL)
            validation_match = re.search(
                r"### Validation Commands\n(.*?)(?=\n###|\Z)",
                block,
                re.DOTALL,
            )
            subtasks_match = re.search(
                r"### Execution Subtasks\n(.*?)(?=\n###|\Z)",
                block,
                re.DOTALL,
            )
            depends_on_text = (
                depends_match.group(1).strip() if depends_match else "None"
            )
            validation_block = validation_match.group(1) if validation_match else ""
            validation_commands = [
                line.strip()[2:]
                for line in validation_block.splitlines()
                if line.strip().startswith("- ")
            ]
            execution_subtasks = [
                line.strip()[2:]
                for line in (
                    subtasks_match.group(1) if subtasks_match else ""
                ).splitlines()
                if line.strip().startswith("- ")
            ]
            details_by_task[task_id] = {
                "depends_on": []
                if depends_on_text.lower() == "none"
                else [
                    part.strip() for part in depends_on_text.split(",") if part.strip()
                ],
                "validation_commands": validation_commands,
                "execution_subtasks": execution_subtasks,
            }
        for task_id, task_title in task_matches:
            detail = details_by_task.get(task_id, {})
            depends_on = detail.get("depends_on", [])
            validation_commands = detail.get("validation_commands", [])
            execution_subtasks = detail.get("execution_subtasks", [])
            todo_lines.extend(
                [
                    f"- [ ] {task_id}: {task_title.strip()}",
                    *[f"  - [ ] {subtask}" for subtask in execution_subtasks],
                    f"  - depends_on: {', '.join(depends_on) if depends_on else 'none'}",
                    f"  - validation: {' | '.join(validation_commands) if validation_commands else 'document validation command'}",
                    "",
                ]
            )
        todo_path = target_dir / "todo.md"
        todo_path.write_text("\n".join(todo_lines), encoding="utf-8")
        written_paths.append(todo_path)

    current_handoff_path = get_planning_dir(root_dir) / "HANDOFF-CURRENT.md"
    current_handoff_path.write_text(files["HANDOFF-CURRENT.md"], encoding="utf-8")
    return written_paths


def gap_registry_helper_path(root_dir: Path) -> Path | None:
    """Resolve the gap registry helper path for the current runtime context."""
    project_local = root_dir / ".mm-flow" / "commands" / "mm" / "gap-registry.py"
    if project_local.exists():
        return project_local
    sibling = Path(__file__).resolve().parent / "gap-registry.py"
    if sibling.exists():
        return sibling
    return None


def sync_gap_registry_for_discovered_objective(
    root_dir: Path, objective_slug: str
) -> tuple[bool, str]:
    """Best-effort sync of the gap registry after objective package creation."""
    helper_path = gap_registry_helper_path(root_dir)
    if helper_path is None:
        return False, "gap registry helper not found"

    result = subprocess.run(
        [
            sys.executable,
            str(helper_path),
            "sync-objective",
            "--objective-slug",
            objective_slug,
        ],
        cwd=root_dir,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    output = (result.stdout or "").strip()
    if result.returncode == 0:
        return True, output or f"Synchronized gap registry for {objective_slug}"
    if f"No gap found for suggested_followup: {objective_slug}" in output:
        return False, f"No matching gap registry entry for {objective_slug}"
    return False, output or f"Gap registry sync failed for {objective_slug}"


def read_context_files(root_dir: Path) -> dict[str, object]:
    """Read coarse context signals for existing projects."""
    context: dict[str, object] = {
        "root": str(root_dir),
        "has_readme": False,
        "has_claude_md": False,
        "has_planning": False,
        "has_active_objectives": False,
        "has_archived_objectives": False,
        "has_project_md": False,
        "has_docs_prd": False,
        "has_canonical_docs": False,
        "git_status": None,
    }

    files_to_check = {
        "README.md": "has_readme",
        "CLAUDE.md": "has_claude_md",
        "PROJECT.md": "has_project_md",
    }

    for file_path, key in files_to_check.items():
        if (root_dir / file_path).exists():
            context[key] = True

    planning_dir = get_planning_dir(root_dir)
    if planning_dir.exists() and any(planning_dir.iterdir()):
        context["has_planning"] = True
    context["has_active_objectives"] = any((planning_dir / "changes").glob("*/"))
    context["has_archived_objectives"] = any(
        (planning_dir / "archive" / "objectives").glob("*/")
    )

    context["has_docs_prd"] = (root_dir / "docs" / "PRD").exists()
    context["has_canonical_docs"] = (root_dir / "docs" / "canonical").exists()

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        status_lines = [line for line in result.stdout.splitlines() if line.strip()]
        context["git_status"] = "\n".join(status_lines[:40])
        context["git_status_total"] = len(status_lines)
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        context["recent_commits"] = result.stdout.strip()
    except Exception:
        context["recent_commits"] = ""

    return context


def validate_mode(args: argparse.Namespace) -> None:
    """Validate mutually exclusive/required discovery modes."""
    if args.roadmap and not args.existing:
        sys.stdout.write("ERROR: --roadmap requires --existing\n")
        sys.exit(1)

    if args.objective and args.health:
        sys.stdout.write("ERROR: --objective cannot be combined with --health\n")
        sys.exit(1)

    if args.objective and args.gaps:
        sys.stdout.write("ERROR: --objective cannot be combined with --gaps\n")
        sys.exit(1)

    if args.objective and args.roadmap:
        sys.stdout.write("ERROR: --objective cannot be combined with --roadmap\n")
        sys.exit(1)

    if args.quick and not args.objective:
        sys.stdout.write("ERROR: --quick requires --objective\n")
        sys.exit(1)


def generate_new_project_payload(
    idea: str, mode: str, root_dir: Path
) -> dict[str, object]:
    """Generate payload for legacy new-project discovery."""
    return {
        "mode": "new",
        "idea": idea,
        "discovery_mode": mode,
        "working_dir": str(root_dir),
        "timestamp": datetime.now().isoformat(),
        "session_id": f"discover-new-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    }


def generate_existing_project_payload(
    context: dict[str, object], options: dict[str, object], root_dir: Path
) -> dict[str, object]:
    """Generate payload for legacy existing-project rediscovery."""
    return {
        "mode": "existing",
        "context": context,
        "options": options,
        "working_dir": str(root_dir),
        "timestamp": datetime.now().isoformat(),
        "session_id": f"discover-existing-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    }


def generate_roadmap_payload(
    context: dict[str, object], mode: str, root_dir: Path
) -> dict[str, object]:
    """Generate payload for roadmap discovery from an existing project."""
    return {
        "mode": "roadmap",
        "context": context,
        "discovery_mode": mode,
        "working_dir": str(root_dir),
        "roadmap_dir": str(get_planning_dir(root_dir) / "roadmap"),
        "source_priority": [
            "explicit_intent",
            "planning_state",
            "decision_history",
            "implementation_reality",
        ],
        "timestamp": datetime.now().isoformat(),
        "session_id": f"discover-roadmap-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    }


def generate_objective_payload(
    objective_name: str,
    idea: str | None,
    context: dict[str, object],
    mode: str,
    quick: bool,
    root_dir: Path,
) -> dict[str, object]:
    """Generate payload for one objective planning package."""
    objective_slug = validate_objective_slug(objective_name)
    return {
        "mode": "objective",
        "objective_name": objective_name,
        "objective_slug": objective_slug,
        "objective_brief": idea,
        "discovery_mode": "fast" if quick else mode,
        "quick_mode": quick,
        "context": context,
        "working_dir": str(root_dir),
        "target_dir": str(get_planning_dir(root_dir) / "changes" / objective_slug),
        "required_files": [
            "requirements.md",
            "design.md",
            "tasks.md",
            "HANDOFF-CURRENT.md",
        ],
        "timestamp": datetime.now().isoformat(),
        "session_id": f"discover-objective-{objective_slug}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    }


def require_existing_context(context: dict[str, object]) -> None:
    """Fail when no useful existing-project context can be found."""
    if not any(
        [
            context["has_readme"],
            context["has_claude_md"],
            context["has_planning"],
            context["has_active_objectives"],
            context["has_archived_objectives"],
            context["has_project_md"],
            context["has_docs_prd"],
            context["has_canonical_docs"],
        ]
    ):
        emit(
            "ERROR: No project context found (README.md, PROJECT.md, CLAUDE.md, docs/PRD, docs/canonical, or .planning sources required for existing-project discovery)"
        )
        sys.exit(1)


def main() -> None:
    """Entrypoint for discovery command routing."""
    args = parse_args()
    validate_mode(args)
    root_dir = Path.cwd()

    if args.existing or args.roadmap or args.objective:
        context = read_context_files(root_dir)
        require_existing_context(context)

        if args.roadmap:
            payload = generate_roadmap_payload(context, args.mode, root_dir)
            written_paths = write_roadmap_files(root_dir, payload)
            emit("MODE: roadmap")
            emit("TASK: roadmap-planner")
            emit(f"PAYLOAD: {json.dumps(payload, indent=2)}")
            emit("LAUNCH: materialized-local")
            emit(
                f"WRITTEN: {json.dumps([str(path) for path in written_paths], indent=2)}"
            )
            emit()
            emit(
                "INFO: Generating objective roadmap from explicit intent + implementation reality..."
            )
            emit(f"INFO: Session ID: {payload['session_id']}")
            return

        if args.objective:
            try:
                validate_objective_slug(args.objective)
            except ValueError as exc:
                emit(f"ERROR: {exc}")
                sys.exit(1)
            active_dirs = active_objective_dirs(root_dir)
            conflicting_dirs = [
                path for path in active_dirs if path.name != args.objective
            ]
            if conflicting_dirs:
                matched_exception = find_active_objective_exception(
                    root_dir,
                    {path.name for path in active_dirs},
                    args.objective,
                    "discover --existing --objective",
                    args.delegated_from,
                )
                if matched_exception is None:
                    emit("STATUS: BLOCKED")
                    emit(
                        f"- Active objective package already exists: {conflicting_dirs[0].relative_to(root_dir)}"
                    )
                    emit(
                        "- Resolve the active objective first (complete/archive/resume) before opening a different objective package."
                    )
                    sys.exit(2)
                allowed_slugs = ", ".join(
                    str(slug) for slug in matched_exception.get("objective_slugs", [])
                )
                emit(f"ACTIVE_OBJECTIVE_EXCEPTION: {matched_exception.get('id', '')}")
                emit(f"ALLOWED_OBJECTIVES: {allowed_slugs}")
                emit(f"- {matched_exception.get('reason', '')}")
                emit(f"- Expires when: {matched_exception.get('expires_when', '')}")

            gate_status, gate_guidance, gate_artifact = infer_objective_gate_status(
                root_dir, args.objective
            )
            if gate_status != "NO_CANONICAL" and gate_status != "PASSED":
                emit("STATUS: BLOCKED")
                emit(f"GATE_STATUS: {gate_status}")
                if gate_artifact:
                    emit(f"GATE_ARTIFACT: {gate_artifact}")
                emit(f"- {gate_guidance}")
                sys.exit(2)

            try:
                payload = generate_objective_payload(
                    args.objective,
                    args.idea,
                    context,
                    args.mode,
                    args.quick,
                    root_dir,
                )
                written_paths = write_objective_package(root_dir, payload)
            except (OSError, ValueError) as exc:
                emit(f"ERROR: {exc}")
                sys.exit(1)
            sync_ok, sync_message = sync_gap_registry_for_discovered_objective(
                root_dir, str(payload["objective_slug"])
            )
            emit("MODE: objective")
            emit("TASK: objective-packager")
            emit(f"PAYLOAD: {json.dumps(payload, indent=2)}")
            emit("LAUNCH: materialized-local")
            emit(
                f"WRITTEN: {json.dumps([str(path) for path in written_paths], indent=2)}"
            )
            if sync_ok:
                emit(f"GAP_REGISTRY_SYNC: {sync_message}")
            else:
                emit(f"GAP_REGISTRY_SYNC_INFO: {sync_message}")
            emit()
            emit(f"INFO: Preparing objective package for: {args.objective}")
            emit(f"INFO: Target directory: {payload['target_dir']}")
            emit(f"INFO: Session ID: {payload['session_id']}")
            return

        emit(
            "ERROR: Legacy discover modes (--health/--gaps/--replan/plain --existing) were removed."
        )
        emit("ERROR: Use one of:")
        emit("  /mm:discover --roadmap --existing")
        emit('  /mm:discover --existing --objective <slug> "Objective Name"')
        sys.exit(1)

    emit("ERROR: New-project legacy discover mode was removed from the active MM flow.")
    emit("ERROR: Use the objective-package flow instead:")
    emit("  /mm:discover --roadmap --existing")
    emit('  /mm:discover --existing --objective <slug> "Objective Name"')
    sys.exit(1)


if __name__ == "__main__":
    main()
