"""Planning bridge between `.planning` intent and harness runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass(frozen=True, slots=True)
class ProjectManifest:
    """Canonical project manifest used by the planning bridge."""

    project_name: str
    canonical_scope: str
    source_of_truth_ai_dlc: bool
    source_of_truth_planning: bool
    active_objective: str
    active_uow: str
    project_root: Path
    operational_layer: str
    design_layer: str
    memory_layer: str
    harness_layer: str
    adapter_name: str | None = None
    bridge_contract: str | None = None


@dataclass(frozen=True, slots=True)
class PlanningIntent:
    """Normalized `.planning` objective and handoff state."""

    active_objective: str
    objective_description: str
    next_command: str | None
    last_archived: str | None


@dataclass(frozen=True, slots=True)
class HarnessRequest:
    """Normalized request handed from planning to the harness."""

    project_name: str
    design_objective: str
    operational_objective: str
    active_uow: str
    project_root: Path
    constraints: tuple[str, ...]
    expected_outputs: tuple[str, ...]
    required_checks: tuple[str, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class StructuredStatus:
    """Machine-readable write-back into `.planning`."""

    status: str
    summary: str
    next_action: str
    verification_outcome: str
    recovery_notes: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class HandoffRecord:
    """Traceable handoff record written to planning artifacts."""

    objective: str
    uow: str
    summary: str
    next_action: str
    verification_outcome: str
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ArchiveRecord:
    """Archive-ready completion record for finished work."""

    objective: str
    uow: str
    summary: str
    archived_at: str
    warnings: tuple[str, ...] = field(default_factory=tuple)


class PlanningBridge:
    """Translate `.planning` state into a harness request and back."""

    _MANIFEST_HEADING = "## Project Manifest"
    _HANDOFF_OBJECTIVE_HEADING = "## Next recommended objective"
    _HANDOFF_COMMAND_HEADING = "## Next command"
    _BRIDGE_SECTION_START = "<!-- bridge-status:start -->"
    _BRIDGE_SECTION_END = "<!-- bridge-status:end -->"

    def __init__(
        self,
        *,
        project_root: Path,
        manifest_path: Path | None = None,
        handoff_path: Path | None = None,
    ) -> None:
        """Initialize the bridge with repo-scoped file locations."""
        self.project_root = project_root
        self.manifest_path = (
            manifest_path or project_root / "aidlc-docs" / "aidlc-state.md"
        )
        self.handoff_path = (
            handoff_path or project_root / ".planning" / "HANDOFF-CURRENT.md"
        )

    def load_manifest(self) -> ProjectManifest:
        """Parse the canonical project manifest from AI-DLC state."""
        content = self.manifest_path.read_text(encoding="utf-8")
        fields = self._parse_key_value_section(content, self._MANIFEST_HEADING)
        return ProjectManifest(
            project_name=fields["project_name"],
            canonical_scope=fields["canonical_scope"],
            source_of_truth_ai_dlc=self._parse_bool(fields["source_of_truth_ai_dlc"]),
            source_of_truth_planning=self._parse_bool(
                fields["source_of_truth_planning"]
            ),
            active_objective=fields["active_objective"],
            active_uow=fields["active_uow"],
            project_root=Path(fields["project_root"]),
            operational_layer=fields["operational_layer"],
            design_layer=fields["design_layer"],
            memory_layer=fields["memory_layer"],
            harness_layer=fields["harness_layer"],
            adapter_name=fields.get("adapter_name"),
            bridge_contract=fields.get("bridge_contract"),
        )

    def load_intent(self) -> PlanningIntent:
        """Parse the active `.planning` handoff into a normalized intent."""
        content = self.handoff_path.read_text(encoding="utf-8")
        objective_section = self._parse_bullet_section(
            content,
            self._HANDOFF_OBJECTIVE_HEADING,
        )
        command_section = self._parse_bullet_section(
            content,
            self._HANDOFF_COMMAND_HEADING,
        )
        active_objective = ""
        objective_description = ""
        if objective_section:
            active_objective, objective_description = self._split_objective_line(
                objective_section[0]
            )
        next_command = command_section[0] if command_section else None
        last_archived = self._parse_last_archived(content)
        return PlanningIntent(
            active_objective=active_objective,
            objective_description=objective_description,
            next_command=next_command,
            last_archived=last_archived,
        )

    def build_request(self) -> HarnessRequest:
        """Build the harness request from manifest and planning intent."""
        manifest = self.load_manifest()
        intent = self.load_intent()
        warnings: list[str] = []
        operational_objective = intent.active_objective or manifest.active_objective
        if (
            intent.active_objective
            and intent.active_objective != manifest.active_objective
        ):
            warnings.append("planning_objective_differs_from_design_objective")
        if intent.next_command is None:
            warnings.append("planning_next_command_missing")
        constraints = [
            f"canonical_scope={manifest.canonical_scope}",
            f"operational_layer={manifest.operational_layer}",
            f"design_layer={manifest.design_layer}",
        ]
        if intent.next_command:
            constraints.append(f"next_command={intent.next_command}")
        if intent.objective_description:
            constraints.append(f"objective_description={intent.objective_description}")
        return HarnessRequest(
            project_name=manifest.project_name,
            design_objective=manifest.active_objective,
            operational_objective=operational_objective,
            active_uow=manifest.active_uow,
            project_root=manifest.project_root,
            constraints=tuple(constraints),
            expected_outputs=(
                "harness request",
                "structured status",
                "handoff record",
            ),
            required_checks=(
                "project manifest present",
                "planning objective present",
                "source-of-truth split explicit",
            ),
            warnings=tuple(warnings),
        )

    def write_structured_status(
        self,
        status: StructuredStatus,
        *,
        objective: str,
        uow: str,
    ) -> HandoffRecord:
        """Write a structured status block back into the handoff file."""
        record = HandoffRecord(
            objective=objective,
            uow=uow,
            summary=status.summary,
            next_action=status.next_action,
            verification_outcome=status.verification_outcome,
            warnings=status.warnings,
        )
        self._write_handoff_block(record, status)
        return record

    def archive(self, record: HandoffRecord, *, archived_at: str) -> ArchiveRecord:
        """Write a traceable archive block to the handoff file."""
        archive = ArchiveRecord(
            objective=record.objective,
            uow=record.uow,
            summary=record.summary,
            archived_at=archived_at,
            warnings=record.warnings,
        )
        self._write_archive_block(archive)
        return archive

    def _parse_key_value_section(self, content: str, heading: str) -> dict[str, str]:
        """Parse a heading-delimited key/value section."""
        section = self._extract_section(content, heading)
        fields: dict[str, str] = {}
        for line in section:
            match = re.match(r"^-\s*([A-Za-z0-9_]+):\s*(.+)$", line.strip())
            if not match:
                continue
            key = match.group(1).strip()
            value = match.group(2).strip().strip("`")
            fields[key] = value
        required_fields = {
            "project_name",
            "canonical_scope",
            "source_of_truth_ai_dlc",
            "source_of_truth_planning",
            "active_objective",
            "active_uow",
            "project_root",
            "operational_layer",
            "design_layer",
            "memory_layer",
            "harness_layer",
        }
        missing = sorted(required_fields - fields.keys())
        if missing:
            raise ValueError(f"Missing manifest fields: {', '.join(missing)}")
        return fields

    def _parse_bullet_section(self, content: str, heading: str) -> list[str]:
        """Return the bullet content for a heading-delimited section."""
        section = self._extract_section(content, heading)
        return [line[2:].strip() for line in section if line.startswith("- ")]

    def _parse_last_archived(self, content: str) -> str | None:
        """Return the last archived objective when present."""
        match = re.search(r"^\s*-\s*`?([^`]+)`?\s+—\s+archived", content, re.M)
        return match.group(1).strip() if match else None

    def _split_objective_line(self, line: str) -> tuple[str, str]:
        """Split a planning objective bullet into objective slug and description."""
        match = re.match(r"^`?([^`]+?)`?\s+[—-]\s+(.+)$", line)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return line.strip().strip("`"), ""

    def _extract_section(self, content: str, heading: str) -> list[str]:
        """Extract lines belonging to a markdown section."""
        lines = content.splitlines()
        start_index = None
        for index, line in enumerate(lines):
            if line.strip() == heading:
                start_index = index + 1
                break
        if start_index is None:
            return []
        section: list[str] = []
        for line in lines[start_index:]:
            if line.startswith("## "):
                break
            section.append(line)
        return section

    def _parse_bool(self, value: str) -> bool:
        """Parse a markdown boolean value."""
        return value.strip().lower() == "true"

    def _write_handoff_block(
        self,
        record: HandoffRecord,
        status: StructuredStatus,
    ) -> None:
        """Write or replace the structured status block in the handoff file."""
        content = self.handoff_path.read_text(encoding="utf-8")
        block = self._format_status_block(record, status)
        updated = self._replace_or_append_block(content, block)
        self.handoff_path.write_text(updated, encoding="utf-8")

    def _write_archive_block(self, archive: ArchiveRecord) -> None:
        """Write or replace the archive block in the handoff file."""
        content = self.handoff_path.read_text(encoding="utf-8")
        block = self._format_archive_block(archive)
        updated = self._replace_or_append_block(content, block)
        self.handoff_path.write_text(updated, encoding="utf-8")

    def _replace_or_append_block(self, content: str, block: str) -> str:
        """Replace a previous bridge block or append a new one."""
        pattern = re.compile(
            rf"{re.escape(self._BRIDGE_SECTION_START)}.*?{re.escape(self._BRIDGE_SECTION_END)}\n?",
            re.S,
        )
        if pattern.search(content):
            return pattern.sub(block, content).rstrip() + "\n"
        separator = "\n" if content.endswith("\n") else "\n\n"
        return content.rstrip() + separator + block

    def _format_status_block(
        self, record: HandoffRecord, status: StructuredStatus
    ) -> str:
        """Render the structured status as markdown."""
        lines = [
            self._BRIDGE_SECTION_START,
            "## Bridge Status",
            f"- objective: {record.objective}",
            f"- uow: {record.uow}",
            f"- status: {status.status}",
            f"- summary: {record.summary}",
            f"- next_action: {record.next_action}",
            f"- verification_outcome: {record.verification_outcome}",
        ]
        for note in status.recovery_notes:
            lines.append(f"- recovery_note: {note}")
        for warning in record.warnings:
            lines.append(f"- warning: {warning}")
        lines.append(self._BRIDGE_SECTION_END)
        return "\n".join(lines) + "\n"

    def _format_archive_block(self, archive: ArchiveRecord) -> str:
        """Render the archive record as markdown."""
        lines = [
            self._BRIDGE_SECTION_START,
            "## Bridge Archive",
            f"- objective: {archive.objective}",
            f"- uow: {archive.uow}",
            f"- summary: {archive.summary}",
            f"- archived_at: {archive.archived_at}",
        ]
        for warning in archive.warnings:
            lines.append(f"- warning: {warning}")
        lines.append(self._BRIDGE_SECTION_END)
        return "\n".join(lines) + "\n"


def build_default_planning_bridge(project_root: Path) -> PlanningBridge:
    """Build the repo-default bridge for MasterMind planning artifacts."""
    return PlanningBridge(project_root=project_root)
