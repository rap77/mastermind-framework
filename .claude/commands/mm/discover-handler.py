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
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


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
    return parser.parse_args()


def slugify(value: str) -> str:
    """Return a filesystem-safe objective slug."""
    lowered = value.strip().lower()
    slug = "".join(ch if ch.isalnum() else "-" for ch in lowered)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


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


def collect_handoff_candidates(root_dir: Path) -> list[ObjectiveCandidate]:
    """Collect active objective hints from handoff files."""
    candidates: list[ObjectiveCandidate] = []
    handoff_dir = root_dir / ".planning"
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
    for state_dir, status in (
        (root_dir / ".planning" / "changes", "active"),
        (root_dir / ".planning" / "archive" / "objectives", "done"),
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
                execution_state_path = child / "execution-state.json"
                handoff_path = child / "HANDOFF-CURRENT.md"
                execution_state_text = read_text(execution_state_path)
                handoff_text = read_text(handoff_path)
                if execution_state_text:
                    try:
                        execution_state = json.loads(execution_state_text)
                        task_statuses = [
                            task.get("status", "pending")
                            for task in execution_state.get("tasks", {}).values()
                        ]
                        if task_statuses and all(
                            status == "completed" for status in task_statuses
                        ):
                            child_status = "done"
                    except json.JSONDecodeError:
                        pass
                if (
                    child_status != "done"
                    and "## Current objective" in handoff_text
                    and "**COMPLETE**" in handoff_text
                ):
                    child_status = "done"
            candidates.append(
                ObjectiveCandidate(
                    slug=slug,
                    name=slug.replace("-", " ").title(),
                    summary=summary,
                    why_it_matters="Structured planning package already exists.",
                    status=child_status,
                    mvp=True,
                    evidence_sources=[str(child.relative_to(root_dir))],
                )
            )
    return candidates


def collect_phase_candidates(root_dir: Path) -> list[ObjectiveCandidate]:
    """Collect major workstreams from roadmap/source-of-truth phase headings."""
    candidates: list[ObjectiveCandidate] = []
    candidate_files = [
        root_dir / ".planning" / "SOURCE-OF-TRUTH.md",
        root_dir / ".planning" / "ROADMAP.md",
        root_dir / ".planning" / "ROADMAP-v3.2.md",
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
            phase_name = match.group("name").strip()
            phase_slug = canonical_objective_slug(slugify(phase_name))
            block = text[match.start() : match.start() + 600]
            status = "planned"
            if "complete" in block.lower() or "✅" in block:
                status = "done"
            elif "in progress" in block.lower() or "🔄" in block:
                status = "active"
            if status == "done":
                continue
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
                    why_it_matters="Declared roadmap phase in planning sources.",
                    status=status,
                    mvp=True,
                    evidence_sources=[str(path.relative_to(root_dir))],
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


def choose_recommended_next(
    objectives: list[ObjectiveCandidate],
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

    return sorted(
        ready,
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
    recommended_next = choose_recommended_next(objectives)
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
            f"- Why: ready now, highest deterministic priority ({recommended_next.priority_score}), "
            f"unlocks {count_unlocks(recommended_next.slug, objectives)} downstream objective(s)."
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
        "| Rank | Objective | Status | Ready Now | Priority | Recommended | MVP | Dependencies | Why it matters | Evidence |",
        "|---:|---|---|---|---:|---|---|---|---|---|",
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
        recommended = (
            recommended_next is not None and objective.slug == recommended_next.slug
        )
        lines.append(
            f"| {index} | `{objective.slug}` | {objective.status} | {'yes' if ready_now else 'no'} | {objective.priority_score} | {'yes' if recommended else 'no'} | {'yes' if objective.mvp else 'no'} | {deps} | {objective.why_it_matters} | {evidence} |"
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

    current_handoff_path = root_dir / ".planning" / "HANDOFF-CURRENT.md"
    if objectives:
        next_objective = recommended_next or display_order[0]
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
                "",
                "## Blockers / risks",
                "- Roadmap is heuristic and should be refined when new canonical docs or handoffs appear.",
                "- Legacy global discovery files still coexist with the target per-objective package model.",
                "",
                "## Exact next recommended task",
                f'- Run `/mm:discover --existing --objective {next_objective.slug} "{next_objective.name}"` to generate the active objective package.',
                (
                    f"- This objective is ready now and carries priority score {next_objective.priority_score}."
                ),
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
    source_of_truth = read_text(root_dir / ".planning" / "SOURCE-OF-TRUTH.md")
    project_state_handoff = read_text(
        root_dir / ".planning" / "HANDOFF-PROJECT-STATE-2026-05-24.md"
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
    elif "realtime" in objective_slug or "websocket" in objective_slug:
        task_sections = [
            {
                "id": "RT1",
                "title": "Event contract",
                "purpose": "Define the realtime contract before implementation diverges.",
                "depends_on": [],
                "parallelizable": False,
                "files_touched": ["docs/canonical/35-WEBSOCKET-EVENT-CONTRACT.md"],
                "validation_commands": [
                    "Review event contract for explicit payload fields and event names."
                ],
                "acceptance": [
                    "Event names, payloads, and source boundaries are documented.",
                    "The backend has a clear authority boundary for publishing events.",
                ],
            },
            {
                "id": "RT2",
                "title": "Backend publication path",
                "purpose": "Add a minimal publication path for the target objective.",
                "depends_on": ["RT1"],
                "parallelizable": False,
                "files_touched": ["apps/api/mastermind_cli"],
                "validation_commands": [
                    "Run targeted backend tests for realtime publication."
                ],
                "acceptance": [
                    "A minimal backend publication path exists for the target objective.",
                    "Tests or targeted validation cover the publication path.",
                ],
            },
            {
                "id": "RT3",
                "title": "Frontend consumption",
                "purpose": "Consume the realtime signal safely in the UI.",
                "depends_on": ["RT2"],
                "parallelizable": False,
                "files_touched": ["apps/web/src/components"],
                "validation_commands": [
                    "Run frontend lint/typecheck for the affected realtime components."
                ],
                "acceptance": [
                    "The frontend consumes the event signal safely.",
                    "The UI degrades gracefully if no live events arrive.",
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
            "- Source of truth exists in `.planning/SOURCE-OF-TRUTH.md` and should guide intent reconciliation."
        )
    if project_state_handoff and objective_slug.startswith("project-state"):
        context_notes.append(
            "- `.planning/HANDOFF-PROJECT-STATE-2026-05-24.md` provides concrete current-state guidance for this workstream."
        )
    dependency_lines = [
        f"- Depends on `{dependency}`"
        for dependency in dependency_hints(objective_slug)
    ] or ["- No explicit upstream dependency declared"]
    context_note_lines = context_notes or ["- No additional context note available."]

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
        task_lines.extend(
            [
                f"## {section['id']}: {section['title']}",
                "",
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
    target_dir = Path(str(payload["target_dir"]))
    ensure_directory(target_dir)
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
            depends_on_text = (
                depends_match.group(1).strip() if depends_match else "None"
            )
            validation_block = validation_match.group(1) if validation_match else ""
            validation_commands = [
                line.strip()[2:]
                for line in validation_block.splitlines()
                if line.strip().startswith("- ")
            ]
            details_by_task[task_id] = {
                "depends_on": []
                if depends_on_text.lower() == "none"
                else [
                    part.strip() for part in depends_on_text.split(",") if part.strip()
                ],
                "validation_commands": validation_commands,
            }
        for task_id, task_title in task_matches:
            detail = details_by_task.get(task_id, {})
            depends_on = detail.get("depends_on", [])
            validation_commands = detail.get("validation_commands", [])
            todo_lines.extend(
                [
                    f"- [ ] {task_id}: {task_title.strip()}",
                    f"  - [ ] {task_id}.1: Review requirements and design context for {task_id}",
                    f"  - [ ] {task_id}.2: Implement {task_id} end-to-end",
                    f"  - [ ] {task_id}.3: Run validation for {task_id}",
                    f"  - depends_on: {', '.join(depends_on) if depends_on else 'none'}",
                    f"  - validation: {' | '.join(validation_commands) if validation_commands else 'document validation command'}",
                    "",
                ]
            )
        todo_path = target_dir / "todo.md"
        todo_path.write_text("\n".join(todo_lines), encoding="utf-8")
        written_paths.append(todo_path)

    current_handoff_path = root_dir / ".planning" / "HANDOFF-CURRENT.md"
    current_handoff_path.write_text(files["HANDOFF-CURRENT.md"], encoding="utf-8")
    return written_paths


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

    planning_dir = root_dir / ".planning"
    if planning_dir.exists() and any(planning_dir.iterdir()):
        context["has_planning"] = True
    context["has_active_objectives"] = any(
        (root_dir / ".planning" / "changes").glob("*/")
    )
    context["has_archived_objectives"] = any(
        (root_dir / ".planning" / "archive" / "objectives").glob("*/")
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
        print("ERROR: --roadmap requires --existing")
        sys.exit(1)

    if args.objective and args.health:
        print("ERROR: --objective cannot be combined with --health")
        sys.exit(1)

    if args.objective and args.gaps:
        print("ERROR: --objective cannot be combined with --gaps")
        sys.exit(1)

    if args.objective and args.roadmap:
        print("ERROR: --objective cannot be combined with --roadmap")
        sys.exit(1)

    if args.quick and not args.objective:
        print("ERROR: --quick requires --objective")
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
        "roadmap_dir": str(root_dir / ".planning" / "roadmap"),
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
    objective_slug = slugify(objective_name)
    return {
        "mode": "objective",
        "objective_name": objective_name,
        "objective_slug": objective_slug,
        "objective_brief": idea,
        "discovery_mode": "fast" if quick else mode,
        "quick_mode": quick,
        "context": context,
        "working_dir": str(root_dir),
        "target_dir": str(root_dir / ".planning" / "changes" / objective_slug),
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
        print(
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
            print("MODE: roadmap")
            print("TASK: roadmap-planner")
            print(f"PAYLOAD: {json.dumps(payload, indent=2)}")
            print("LAUNCH: materialized-local")
            print(
                f"WRITTEN: {json.dumps([str(path) for path in written_paths], indent=2)}"
            )
            print()
            print(
                "INFO: Generating objective roadmap from explicit intent + implementation reality..."
            )
            print(f"INFO: Session ID: {payload['session_id']}")
            return

        if args.objective:
            payload = generate_objective_payload(
                args.objective,
                args.idea,
                context,
                args.mode,
                args.quick,
                root_dir,
            )
            written_paths = write_objective_package(root_dir, payload)
            print("MODE: objective")
            print("TASK: objective-packager")
            print(f"PAYLOAD: {json.dumps(payload, indent=2)}")
            print("LAUNCH: materialized-local")
            print(
                f"WRITTEN: {json.dumps([str(path) for path in written_paths], indent=2)}"
            )
            print()
            print(f"INFO: Preparing objective package for: {args.objective}")
            print(f"INFO: Target directory: {payload['target_dir']}")
            print(f"INFO: Session ID: {payload['session_id']}")
            return

        print(
            "ERROR: Legacy discover modes (--health/--gaps/--replan/plain --existing) were removed."
        )
        print("ERROR: Use one of:")
        print("  /mm:discover --roadmap --existing")
        print('  /mm:discover --existing --objective <slug> "Objective Name"')
        sys.exit(1)

    print(
        "ERROR: New-project legacy discover mode was removed from the active MM flow."
    )
    print("ERROR: Use the objective-package flow instead:")
    print("  /mm:discover --roadmap --existing")
    print('  /mm:discover --existing --objective <slug> "Objective Name"')
    sys.exit(1)


if __name__ == "__main__":
    main()
