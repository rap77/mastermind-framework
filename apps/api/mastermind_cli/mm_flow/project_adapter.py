"""Repo-specific adapter for the MasterMind planning bridge."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import os
import subprocess
from pathlib import Path
import re

from .planning_bridge import (
    ArchiveRecord,
    HarnessRequest,
    PlanningBridgeError,
    PlanningBridge,
    PlanningManifestError,
    PlanningIntent,
    ProjectManifest,
    StructuredStatus,
    build_default_planning_bridge,
)
from .integrated_run import ValidationCheck, ValidationReport
from .adapter_warnings import AdapterWarning, AdapterWarnings

logger = logging.getLogger(__name__)


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

    def collect_warnings(self) -> AdapterWarnings:
        """Scan project-specific setup and return structured adapter warnings."""
        items: list[AdapterWarning] = []
        manifest: ProjectManifest | None = None
        if not self.manifest_path.exists():
            items.append(
                AdapterWarning(
                    code="manifest_missing",
                    message=(
                        "Canonical manifest not found at "
                        f"{self.manifest_path}; the adapter cannot identify the "
                        "active project."
                    ),
                    severity="error",
                )
            )
        else:
            try:
                manifest = self.planning_bridge.load_manifest()
            except (PlanningBridgeError, PlanningManifestError) as exc:
                items.append(
                    AdapterWarning(
                        code="manifest_unparseable",
                        message=(
                            "Manifest could not be parsed: "
                            f"{exc}. The adapter cannot build a harness request."
                        ),
                        severity="error",
                    )
                )
        intent: PlanningIntent | None = None
        if not self.handoff_path.exists():
            items.append(
                AdapterWarning(
                    code="handoff_missing",
                    message=(
                        "Planning handoff not found at "
                        f"{self.handoff_path}; runtime will fall back to the "
                        "design-side active objective."
                    ),
                    severity="warning",
                )
            )
        else:
            try:
                intent = self.planning_bridge.load_intent()
            except (PlanningBridgeError, PlanningManifestError) as exc:
                items.append(
                    AdapterWarning(
                        code="handoff_unparseable",
                        message=(
                            "Planning handoff could not be parsed: "
                            f"{exc}. The bridge cannot continue."
                        ),
                        severity="error",
                    )
                )
            else:
                if not intent.active_objective:
                    items.append(
                        AdapterWarning(
                            code="handoff_incomplete",
                            message=(
                                "Planning handoff does not declare an active "
                                "objective; the bridge cannot continue until it is "
                                "completed."
                            ),
                            severity="error",
                        )
                    )
        if not self.state_path.exists():
            items.append(
                AdapterWarning(
                    code="state_path_missing",
                    message=(
                        "MM-Flow state file not found at "
                        f"{self.state_path}; phase tracking will start fresh."
                    ),
                    severity="info",
                )
            )
        if manifest is not None:
            if (
                not manifest.source_of_truth_ai_dlc
                or not manifest.source_of_truth_planning
            ):
                items.append(
                    AdapterWarning(
                        code="source_of_truth_split_unclear",
                        message=(
                            "Manifest does not declare both source-of-truth flags "
                            "as true; AI-DLC and .planning ownership are ambiguous."
                        ),
                        severity="warning",
                    )
                )
            if not manifest.bridge_contract:
                items.append(
                    AdapterWarning(
                        code="bridge_contract_undeclared",
                        message=(
                            "Manifest omits a bridge_contract reference; another "
                            "project cannot locate the planning bridge contract."
                        ),
                        severity="info",
                    )
                )
            if not manifest.project_name:
                items.append(
                    AdapterWarning(
                        code="project_name_empty",
                        message=(
                            "Manifest project_name is empty; project_id will fall "
                            "back to the directory name."
                        ),
                        severity="warning",
                    )
                )
            if not self.project_id:
                items.append(
                    AdapterWarning(
                        code="project_id_unstable",
                        message=(
                            "Could not derive a stable project_id from the manifest "
                            "or environment; memory isolation is at risk."
                        ),
                        severity="warning",
                    )
                )
        return AdapterWarnings(items=tuple(items))


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
    except (OSError, subprocess.SubprocessError) as exc:
        logger.debug("git root detection failed; falling back to cwd: %s", exc)
    return Path.cwd()
