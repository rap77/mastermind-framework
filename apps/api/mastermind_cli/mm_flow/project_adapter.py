"""Repo-specific adapter for the MasterMind planning bridge."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
import subprocess
from pathlib import Path
import re

from .planning_bridge import (
    ArchiveRecord,
    HarnessRequest,
    PlanningBridge,
    StructuredStatus,
    build_default_planning_bridge,
)
from .integrated_run import ValidationCheck, ValidationReport


@dataclass(frozen=True, slots=True)
class ProjectAdapter:
    """Project-specific wiring for the current repo."""

    project_root: Path
    planning_bridge: PlanningBridge

    @classmethod
    def for_repo(
        cls: type[ProjectAdapter], project_root: Path | None = None
    ) -> ProjectAdapter:
        """Create an adapter for the current repository."""
        root = project_root or _detect_project_root()
        return cls(
            project_root=root, planning_bridge=build_default_planning_bridge(root)
        )

    @property
    def manifest_path(self) -> Path:
        """Return the canonical manifest path for this repo."""
        return self.project_root / "aidlc-docs" / "aidlc-state.md"

    @property
    def handoff_path(self) -> Path:
        """Return the canonical handoff path for this repo."""
        return self.project_root / ".planning" / "HANDOFF-CURRENT.md"

    @property
    def state_path(self) -> Path:
        """Return the canonical MM-Flow state path for this repo."""
        return self.project_root / ".planning" / "STATE.md"

    @property
    def project_id(self) -> str:
        """Return the stable project-memory identifier for this repo."""
        explicit = os.environ.get("MM_MEMORY_PROJECT_ID")
        if explicit:
            return explicit.strip()
        project_name = self.planning_bridge.load_manifest().project_name
        normalized = re.sub(r"[^a-z0-9]+", "-", project_name.lower()).strip("-")
        return normalized or self.project_root.name

    def load_harness_request(self) -> HarnessRequest:
        """Load the normalized harness request from planning state."""
        return self.planning_bridge.build_request()

    def write_structured_status(
        self,
        *,
        status: str,
        summary: str,
        next_action: str,
        verification_outcome: str,
        objective: str,
        uow: str,
        recovery_notes: tuple[str, ...] = (),
        warnings: tuple[str, ...] = (),
    ) -> ArchiveRecord | None:
        """Write a machine-readable planning status back into `.planning`."""
        record = self.planning_bridge.write_structured_status(
            StructuredStatus(
                status=status,
                summary=summary,
                next_action=next_action,
                verification_outcome=verification_outcome,
                recovery_notes=recovery_notes,
                warnings=warnings,
            ),
            objective=objective,
            uow=uow,
        )
        if status == "completed":
            return self.planning_bridge.archive(
                record,
                archived_at=datetime.now(timezone.utc).isoformat(),
            )
        return None

    def validate_request(self, request: HarnessRequest) -> ValidationReport:
        """Produce a validation report describing the harness request readiness."""
        manifest_present = bool(
            request.project_name and request.active_uow and request.design_objective
        )
        planning_intent_present = bool(request.operational_objective)
        next_command_present = "planning_next_command_missing" not in request.warnings
        objective_aligned = (
            "planning_objective_differs_from_design_objective" not in request.warnings
        )
        checks = (
            ValidationCheck(
                check_id="manifest_present",
                label="Project manifest fields present",
                passed=manifest_present,
            ),
            ValidationCheck(
                check_id="planning_intent_present",
                label="Operational objective present",
                passed=planning_intent_present,
            ),
            ValidationCheck(
                check_id="next_command_present",
                label="Planning next command present",
                passed=next_command_present,
            ),
            ValidationCheck(
                check_id="objective_alignment",
                label="Planning objective matches design objective",
                passed=objective_aligned,
            ),
        )
        blocking_warnings = {
            "planning_next_command_missing",
            "planning_objective_differs_from_design_objective",
        }
        residual_warnings = tuple(
            w for w in request.warnings if w not in blocking_warnings
        )
        return ValidationReport(
            passed=all(check.passed for check in checks),
            checks=checks,
            warnings=residual_warnings,
        )


def _detect_project_root() -> Path:
    """Detect the repository root using git when possible."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return Path.cwd()
