"""End-to-end integrated run trace and validation reports."""

from __future__ import annotations

from dataclasses import dataclass

from mastermind_cli.memory_layer.models import ContextSnapshot
from mastermind_cli.mm_flow.planning_bridge import (
    ArchiveRecord,
    HarnessRequest,
)
from mastermind_cli.orchestrator.runtime_contracts import (
    RuntimeExecutionResult,
    RuntimeMemoryWrite,
)


@dataclass(frozen=True, slots=True)
class ValidationCheck:
    """One explicit integration validation check."""

    check_id: str
    label: str
    passed: bool
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Aggregate validation report for an integrated run."""

    passed: bool
    checks: tuple[ValidationCheck, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class IntegratedRun:
    """End-to-end trace from project manifest to planning handoff."""

    project_id: str
    request: HarnessRequest
    memory_snapshot: ContextSnapshot | None
    runtime_result: RuntimeExecutionResult | None
    memory_write: RuntimeMemoryWrite | None
    archive_record: ArchiveRecord | None
    warnings: tuple[str, ...]
    validation: ValidationReport
