"""Transactional project-state persistence for domain security assurance."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from hashlib import sha256

from sqlalchemy.orm import Session

from mastermind_cli.experience.redaction import redact_pii
from mastermind_cli.project_state.models.artifact import ArtifactVersion
from mastermind_cli.project_state.repositories.artifacts import ArtifactRepository
from mastermind_cli.project_state.repositories.gaps import GapRepository
from mastermind_cli.project_state.repositories.stage_checkpoints import (
    StageCheckpointRepository,
)

from .models import RunCheckpoint, SecurityProfile, StageResult
from .security_assurance import ControlEvidenceVerdict
from .security_readiness import RiskAcceptanceRecord, SecurityReadinessVerdict

_SAFE_REFERENCE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/#-]{0,254}\Z")
_EVIDENCE_STATUSES = frozenset(
    {"passed", "failed", "inconclusive", "skipped", "missing", "not_applicable"}
)
_APPLICABILITY_VALUES = frozenset({"applicable", "not_applicable"})


@dataclass(frozen=True, slots=True)
class PersistedSecurityTransition:
    """References committed atomically with one authoritative checkpoint."""

    artifact_version_ids: tuple[str, ...]
    readiness_version_id: str
    checkpoint: RunCheckpoint


class SecurityAssuranceRuntime:
    """Persist sanitized assurance history over existing project-state primitives."""

    def __init__(self, session: Session) -> None:
        """Initialize the runtime with one transactional project-state session."""
        self.session = session
        self.artifacts = ArtifactRepository(session)
        self.gaps = GapRepository(session)
        self.checkpoints = StageCheckpointRepository(session)

    def persist_transition(
        self,
        *,
        profile: SecurityProfile,
        finding_ids: tuple[str, ...],
        evidence_verdicts: tuple[ControlEvidenceVerdict, ...],
        readiness_verdict: SecurityReadinessVerdict,
        risk_acceptances: tuple[RiskAcceptanceRecord, ...],
        checkpoint: RunCheckpoint,
        stage_result: StageResult,
        expected_checkpoint_version: int,
        transition_sequence: int,
        remediation_parent_version_ids: tuple[str, ...] = (),
    ) -> PersistedSecurityTransition:
        """Atomically append safe artifacts, lineage, stage state, and checkpoint."""
        project_id = self._safe_reference(profile.project_id, "project_id")
        safe_finding_ids = self._safe_references(finding_ids, "finding_ids")
        safe_parent_ids = self._safe_references(
            remediation_parent_version_ids, "remediation_parent_version_ids"
        )
        evidence_refs = tuple(
            reference
            for verdict in evidence_verdicts
            for reference in self._safe_references(
                verdict.observed_evidence_refs, "observed_evidence_refs"
            )
        )
        self._validate_contract_scope(
            profile=profile,
            finding_ids=safe_finding_ids,
            evidence_verdicts=evidence_verdicts,
            readiness_verdict=readiness_verdict,
            risk_acceptances=risk_acceptances,
        )
        self._prepare_transaction()

        with self.session.begin():
            replay = self.checkpoints.get_committed_transition(
                stage_result=stage_result,
                checkpoint=checkpoint,
                transition_sequence=transition_sequence,
            )
            if replay is not None:
                return self._persisted_from_checkpoint(project_id, replay.checkpoint)
            self._require_security_findings(project_id, safe_finding_ids)
            self._require_project_artifacts(project_id, safe_parent_ids)
            versions = self._stage_artifacts(
                profile=profile,
                finding_ids=safe_finding_ids,
                evidence_verdicts=evidence_verdicts,
                readiness_verdict=readiness_verdict,
                risk_acceptances=risk_acceptances,
                remediation_parent_version_ids=safe_parent_ids,
            )
            artifact_refs = tuple(version.version_id for version in versions)
            persisted_checkpoint = replace(
                checkpoint,
                artifact_refs=artifact_refs,
                evidence_refs=tuple(sorted(set(evidence_refs))),
            )
            persisted_result = replace(
                stage_result,
                artifact_refs=artifact_refs,
                evidence_refs=tuple(sorted(set(evidence_refs))),
                finding_refs=safe_finding_ids,
            )
            committed = self.checkpoints.stage_transition(
                stage_result=persisted_result,
                checkpoint=persisted_checkpoint,
                expected_version=expected_checkpoint_version,
                transition_sequence=transition_sequence,
            )

        readiness_version = next(
            version
            for version in versions
            if version.artifact_type == "security-readiness"
        )
        return PersistedSecurityTransition(
            artifact_version_ids=artifact_refs,
            readiness_version_id=readiness_version.version_id,
            checkpoint=committed.checkpoint,
        )

    def _persisted_from_checkpoint(
        self, project_id: str, checkpoint: RunCheckpoint
    ) -> PersistedSecurityTransition:
        """Rebuild the persistence result from an idempotently replayed checkpoint."""
        versions = [
            self.artifacts.get_project_version(project_id, version_id)
            for version_id in checkpoint.artifact_refs
        ]
        if not versions or any(version is None for version in versions):
            raise ValueError("checkpoint artifacts violate project scope")
        readiness = next(
            (
                version
                for version in versions
                if version is not None and version.artifact_type == "security-readiness"
            ),
            None,
        )
        if readiness is None:
            raise ValueError("checkpoint lacks a security readiness artifact")
        return PersistedSecurityTransition(
            artifact_version_ids=checkpoint.artifact_refs,
            readiness_version_id=readiness.version_id,
            checkpoint=checkpoint,
        )

    def _prepare_transaction(self) -> None:
        """Close SQLAlchemy's read-only autobegin before owning the write boundary."""
        if not self.session.in_transaction():
            return
        if self.session.new or self.session.dirty or self.session.deleted:
            raise RuntimeError("security persistence requires a clean caller session")
        self.session.rollback()

    def resume(
        self, *, project_id: str, run_id: str, bundle_content_hash: str
    ) -> RunCheckpoint:
        """Resume from the HSR checkpoint after enforcing artifact project scope."""
        safe_project_id = self._safe_reference(project_id, "project_id")
        checkpoint = self.checkpoints.resume(
            run_id=run_id, bundle_content_hash=bundle_content_hash
        )
        if not checkpoint.artifact_refs or any(
            self.artifacts.get_project_version(safe_project_id, version_id) is None
            for version_id in checkpoint.artifact_refs
        ):
            raise ValueError("checkpoint artifacts violate project scope")
        return checkpoint

    def list_history(
        self, *, project_id: str, artifact_type: str
    ) -> list[ArtifactVersion]:
        """Return ordered assurance history within one project."""
        return self.artifacts.list_project_history(
            self._safe_reference(project_id, "project_id"), artifact_type
        )

    def _stage_artifacts(
        self,
        *,
        profile: SecurityProfile,
        finding_ids: tuple[str, ...],
        evidence_verdicts: tuple[ControlEvidenceVerdict, ...],
        readiness_verdict: SecurityReadinessVerdict,
        risk_acceptances: tuple[RiskAcceptanceRecord, ...],
        remediation_parent_version_ids: tuple[str, ...],
    ) -> list[ArtifactVersion]:
        """Stage allowlisted metadata and its causal links in canonical order."""
        created_at = datetime.now(timezone.utc)
        profile_version = self._stage_version(
            project_id=profile.project_id,
            artifact_id=(
                f"security-profile:{profile.project_id}:{profile.security_profile_id}"
            ),
            artifact_type="security-profile",
            metadata={
                "security_profile_id": profile.security_profile_id,
                "profile_version": profile.profile_version,
                "project_id": profile.project_id,
                "domain": profile.domain,
                "overlay_refs": [
                    f"{overlay.overlay_id}@{overlay.version}"
                    for overlay in profile.applied_overlays
                ],
                "source_versions": list(profile.source_versions),
            },
            created_at=created_at,
        )
        versions = [profile_version]
        evidence_versions = [
            self._stage_version(
                project_id=profile.project_id,
                artifact_id=(
                    f"security-evidence:{profile.project_id}:"
                    f"{profile.security_profile_id}:{verdict.control_id}"
                ),
                artifact_type="security-evidence-verdict",
                metadata={
                    "control_id": verdict.control_id,
                    "status": verdict.status,
                    "applicability": verdict.applicability,
                    "observed_evidence_refs": list(verdict.observed_evidence_refs),
                    "verification_method": verdict.verification_method,
                    "performed_at": verdict.performed_at,
                    "verifier_ref": verdict.verifier,
                    "source_version": verdict.source_version,
                },
                created_at=created_at,
            )
            for verdict in sorted(evidence_verdicts, key=lambda item: item.control_id)
        ]
        versions.extend(evidence_versions)
        risk_versions = [
            self._stage_version(
                project_id=profile.project_id,
                artifact_id=(
                    f"security-risk-decision:{profile.project_id}:"
                    f"{acceptance.acceptance_id}"
                ),
                artifact_type="security-risk-decision",
                metadata=self._risk_metadata(acceptance),
                created_at=created_at,
            )
            for acceptance in sorted(
                risk_acceptances, key=lambda item: item.acceptance_id
            )
        ]
        versions.extend(risk_versions)
        readiness_version = self._stage_version(
            project_id=profile.project_id,
            artifact_id=(
                f"security-readiness:{profile.project_id}:{profile.security_profile_id}"
            ),
            artifact_type="security-readiness",
            metadata={
                "policy_id": readiness_verdict.policy_id,
                "status": readiness_verdict.status,
                "finding_ids": list(finding_ids),
                "blocking_finding_ids": list(readiness_verdict.blocking_finding_ids),
                "accepted_finding_ids": list(readiness_verdict.accepted_finding_ids),
                "evaluated_at": readiness_verdict.evaluated_at.isoformat(),
            },
            created_at=created_at,
        )
        versions.append(readiness_version)

        for evidence_version in evidence_versions:
            self._stage_link(profile_version, evidence_version, "governs", created_at)
            self._stage_link(
                evidence_version, readiness_version, "supports", created_at
            )
        for risk_version in risk_versions:
            self._stage_link(risk_version, readiness_version, "authorizes", created_at)
        remediation_targets = evidence_versions or (readiness_version,)
        for parent_id in remediation_parent_version_ids:
            for target in remediation_targets:
                self._stage_link_id(parent_id, target, "remediated-by", created_at)
        return versions

    def _stage_version(
        self,
        *,
        project_id: str,
        artifact_id: str,
        artifact_type: str,
        metadata: dict[str, object],
        created_at: datetime,
    ) -> ArtifactVersion:
        """Stage one immutable artifact with a canonical metadata digest."""
        version = self.artifacts.next_version(project_id, artifact_id)
        version_id = f"{artifact_id}:v{version}"
        canonical = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
        return self.artifacts.stage_version(
            version_id=version_id,
            artifact_id=artifact_id,
            project_id=project_id,
            artifact_type=artifact_type,
            version=version,
            content_hash=f"sha256:{sha256(canonical.encode()).hexdigest()}",
            created_at=created_at,
            metadata_json=metadata,
        )

    def _stage_link(
        self,
        source: ArtifactVersion,
        target: ArtifactVersion,
        link_type: str,
        created_at: datetime,
    ) -> None:
        """Stage a causal link between new artifact versions."""
        self._stage_link_id(source.version_id, target, link_type, created_at)

    def _stage_link_id(
        self,
        source_version_id: str,
        target: ArtifactVersion,
        link_type: str,
        created_at: datetime,
    ) -> None:
        """Stage a deterministic causal link from an existing version."""
        digest = sha256(
            f"{source_version_id}\x1f{target.version_id}\x1f{link_type}".encode()
        ).hexdigest()
        self.artifacts.stage_link(
            link_id=f"security-link:{digest}",
            source_artifact_id=source_version_id,
            target_artifact_id=target.version_id,
            link_type=link_type,
            created_at=created_at,
        )

    def _require_security_findings(
        self, project_id: str, finding_ids: tuple[str, ...]
    ) -> None:
        """Resolve security findings from the universal Gap Registry only."""
        for finding_id in finding_ids:
            finding = self.gaps.get_by_id(project_id, finding_id)
            if finding is None or finding.lens != "security":
                raise ValueError(
                    f"{finding_id} is not a project-scoped security finding"
                )

    def _require_project_artifacts(
        self, project_id: str, version_ids: tuple[str, ...]
    ) -> None:
        """Reject remediation lineage crossing project boundaries."""
        if any(
            self.artifacts.get_project_version(project_id, version_id) is None
            for version_id in version_ids
        ):
            raise ValueError("remediation lineage violates project scope")

    @classmethod
    def _validate_contract_scope(
        cls,
        *,
        profile: SecurityProfile,
        finding_ids: tuple[str, ...],
        evidence_verdicts: tuple[ControlEvidenceVerdict, ...],
        readiness_verdict: SecurityReadinessVerdict,
        risk_acceptances: tuple[RiskAcceptanceRecord, ...],
    ) -> None:
        """Validate all persisted identities and cross-record references."""
        cls._safe_reference(profile.security_profile_id, "security_profile_id")
        cls._safe_reference(profile.profile_version, "profile_version")
        cls._safe_reference(profile.domain, "domain")
        cls._safe_references(profile.source_versions, "source_versions")
        for overlay in profile.applied_overlays:
            cls._safe_reference(overlay.overlay_id, "overlay_id")
            cls._safe_reference(overlay.version, "overlay_version")
        finding_set = set(finding_ids)
        readiness_refs = set(readiness_verdict.blocking_finding_ids) | set(
            readiness_verdict.accepted_finding_ids
        )
        if not readiness_refs.issubset(finding_set):
            raise ValueError("readiness finding references must match finding_ids")
        cls._safe_reference(readiness_verdict.policy_id, "policy_id")
        for verdict in evidence_verdicts:
            cls._safe_reference(verdict.control_id, "control_id")
            cls._safe_reference(verdict.source_version, "source_version")
            if verdict.status not in _EVIDENCE_STATUSES:
                raise ValueError(f"Unsupported evidence status: {verdict.status}")
            if verdict.applicability not in _APPLICABILITY_VALUES:
                raise ValueError(
                    f"Unsupported evidence applicability: {verdict.applicability}"
                )
            if verdict.verification_method is not None:
                cls._safe_reference(verdict.verification_method, "verification_method")
            if verdict.performed_at is not None:
                cls._require_timestamp(verdict.performed_at, "performed_at")
            if verdict.verifier is not None:
                cls._safe_reference(verdict.verifier, "verifier_ref")
        for acceptance in risk_acceptances:
            if acceptance.finding_id not in finding_set:
                raise ValueError("risk acceptance must reference a finding_id")
            cls._safe_reference(acceptance.acceptance_id, "acceptance_id")
            cls._safe_reference(acceptance.owner.principal_id, "owner_ref")
            if acceptance.approved_by is not None:
                cls._safe_reference(acceptance.approved_by.principal_id, "approver_ref")
            cls._safe_references(
                acceptance.compensating_controls, "compensating_controls"
            )
            cls._safe_references(acceptance.evidence_refs, "evidence_refs")

    @staticmethod
    def _risk_metadata(acceptance: RiskAcceptanceRecord) -> dict[str, object]:
        """Project allowlisted decision metadata without rationale or evidence bodies."""
        return {
            "acceptance_id": acceptance.acceptance_id,
            "finding_id": acceptance.finding_id,
            "decision": acceptance.decision,
            "status": acceptance.status,
            "owner_ref": acceptance.owner.principal_id,
            "scope": list(acceptance.scope),
            "compensating_control_refs": list(acceptance.compensating_controls),
            "evidence_refs": list(acceptance.evidence_refs),
            "proposed_at": acceptance.proposed_at.isoformat(),
            "review_at": acceptance.review_at.isoformat(),
            "expires_at": acceptance.expires_at.isoformat(),
            "approved_by_ref": (
                acceptance.approved_by.principal_id
                if acceptance.approved_by is not None
                else None
            ),
            "approved_at": (
                acceptance.approved_at.isoformat()
                if acceptance.approved_at is not None
                else None
            ),
            "activated_at": (
                acceptance.activated_at.isoformat()
                if acceptance.activated_at is not None
                else None
            ),
        }

    @classmethod
    def _safe_references(
        cls, references: tuple[str, ...], label: str
    ) -> tuple[str, ...]:
        """Validate a tuple of bounded opaque references."""
        return tuple(cls._safe_reference(reference, label) for reference in references)

    @staticmethod
    def _safe_reference(reference: str, label: str) -> str:
        """Reject raw or sensitive values in every persisted reference field."""
        if (
            not _SAFE_REFERENCE.fullmatch(reference)
            or redact_pii(reference) != reference
        ):
            raise ValueError(f"{label} must contain only safe opaque references")
        return reference

    @staticmethod
    def _require_timestamp(value: str, label: str) -> None:
        """Reject non-ISO or timezone-naive timestamp metadata."""
        try:
            timestamp = datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError(f"{label} must be an ISO timestamp") from error
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError(f"{label} must be timezone-aware")
