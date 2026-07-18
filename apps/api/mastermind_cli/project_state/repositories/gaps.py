"""Repository for the universal project Gap Registry."""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from mastermind_cli.experience.redaction import redact_pii
from mastermind_cli.project_state.models.gap import GapRecord

_REFERENCE_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/#-]{0,254}\Z")
_STATUS_VALUES = frozenset({"open", "deferred", "promoted", "resolved", "closed"})
_RISK_VALUES = frozenset({"unknown", "low", "medium", "high", "critical"})
_TREATMENT_VALUES = frozenset({"mitigate", "avoid", "transfer", "accept", "escalate"})


class GapRepository:
    """Persist and query gaps without accepting raw evidence or control payloads."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a SQLAlchemy session."""
        self.session = session

    def create_gap(
        self,
        *,
        gap_id: str,
        project_id: str,
        title: str,
        status: str,
        lens: str,
        threat: str | None = None,
        impact: str | None = None,
        likelihood: str | None = None,
        evidence_refs: Sequence[str] = (),
        control_refs: Sequence[str] = (),
        residual_risk: str | None = None,
        treatment: str | None = None,
        approval_required: bool = False,
        risk_acceptance_id: str | None = None,
        review_at: datetime | None = None,
    ) -> GapRecord:
        """Validate, redact, and persist one gap in the shared registry."""
        self._validate_choice("status", status, _STATUS_VALUES)
        self._validate_identifier("gap_id", gap_id)
        self._validate_identifier("project_id", project_id)
        self._validate_identifier("lens", lens)
        self._validate_risk("impact", impact)
        self._validate_risk("likelihood", likelihood)
        self._validate_risk("residual_risk", residual_risk)
        if treatment is not None:
            self._validate_choice("treatment", treatment, _TREATMENT_VALUES)
        validated_acceptance_id = (
            self._validate_references("risk_acceptance_id", (risk_acceptance_id,))[0]
            if risk_acceptance_id is not None
            else None
        )

        gap = GapRecord(
            gap_id=gap_id,
            project_id=project_id,
            title=redact_pii(title),
            status=status,
            lens=lens,
            threat=redact_pii(threat) if threat is not None else None,
            impact=impact,
            likelihood=likelihood,
            evidence_refs=self._validate_references("evidence_refs", evidence_refs),
            control_refs=self._validate_references("control_refs", control_refs),
            residual_risk=residual_risk,
            treatment=treatment,
            approval_required=approval_required,
            risk_acceptance_id=validated_acceptance_id,
            review_at=review_at,
        )
        self.session.add(gap)
        self.session.commit()
        self.session.refresh(gap)
        return gap

    def get_by_id(self, project_id: str, gap_id: str) -> GapRecord | None:
        """Return one project-scoped gap, or None when it does not exist."""
        result = self.session.execute(
            select(GapRecord).where(
                GapRecord.project_id == project_id,
                GapRecord.gap_id == gap_id,
            )
        )
        return result.scalar_one_or_none()

    def list_by_evidence_ref(
        self, project_id: str, evidence_ref: str
    ) -> list[GapRecord]:
        """Return project gaps linked to an exact safe evidence reference."""
        reference = self._validate_references("evidence_refs", (evidence_ref,))[0]
        return [
            gap
            for gap in self._list_by_project(project_id)
            if reference in gap.evidence_refs
        ]

    def list_by_control_ref(self, project_id: str, control_ref: str) -> list[GapRecord]:
        """Return project gaps linked to an exact safe control reference."""
        reference = self._validate_references("control_refs", (control_ref,))[0]
        return [
            gap
            for gap in self._list_by_project(project_id)
            if reference in gap.control_refs
        ]

    def _list_by_project(self, project_id: str) -> list[GapRecord]:
        """Return a deterministic project-scoped gap list for reference filtering."""
        result = self.session.execute(
            select(GapRecord)
            .where(GapRecord.project_id == project_id)
            .order_by(asc(GapRecord.created_at), asc(GapRecord.gap_id))
        )
        return list(result.scalars().all())

    @staticmethod
    def _validate_identifier(field_name: str, value: str) -> None:
        """Reject empty or oversized identifiers at the persistence boundary."""
        if not value or len(value) > 255:
            raise ValueError(f"{field_name} must be between 1 and 255 characters")

    @staticmethod
    def _validate_choice(
        field_name: str, value: str, allowed_values: frozenset[str]
    ) -> None:
        """Reject unknown enum-like values instead of persisting ambiguity."""
        if value not in allowed_values:
            raise ValueError(f"Unsupported {field_name}: {value}")

    @classmethod
    def _validate_risk(cls, field_name: str, value: str | None) -> None:
        """Validate an optional risk classification."""
        if value is not None:
            cls._validate_choice(field_name, value, _RISK_VALUES)

    @staticmethod
    def _validate_references(field_name: str, references: Sequence[str]) -> list[str]:
        """Accept only bounded opaque references, never raw or sensitive payloads."""
        validated: list[str] = []
        for reference in references:
            if (
                not _REFERENCE_PATTERN.fullmatch(reference)
                or redact_pii(reference) != reference
            ):
                raise ValueError(
                    f"{field_name} must contain only safe opaque references"
                )
            validated.append(reference)
        return validated
