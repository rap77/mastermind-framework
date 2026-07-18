"""Persistence, lineage, resume, and data-minimization for security assurance."""

from __future__ import annotations

from collections.abc import Iterator
import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from mastermind_cli.orchestrator.runtime_contracts.models import (
    RunCheckpoint,
    SecurityControl,
    SecurityOverlay,
    SecurityProfile,
    StageResult,
)
from mastermind_cli.orchestrator.runtime_contracts.security_assurance import (
    ControlEvidenceVerdict,
)
from mastermind_cli.orchestrator.runtime_contracts.security_assurance_runtime import (
    SecurityAssuranceRuntime,
)
from mastermind_cli.orchestrator.runtime_contracts.security_readiness import (
    HumanRiskAuthority,
    RiskAcceptanceRecord,
    SecurityReadinessVerdict,
)
from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.models.artifact import ArtifactLink, ArtifactVersion
from mastermind_cli.project_state.models.project import Project
from mastermind_cli.project_state.models.stage_checkpoint import (
    StageCheckpointRecord,
    StageTransitionOutbox,
)
from mastermind_cli.project_state.repositories.gaps import GapRepository

PRIVATE_TEST_TEXT = "credential-marker-42"


@pytest.fixture(scope="session", autouse=True)
def _database_url_for_integration() -> None:
    """Override the Postgres gate for this isolated project-state SQLite slice."""


@pytest.fixture()
def session_factory(tmp_path: Path) -> Iterator[sessionmaker[Session]]:
    """Return a fresh project-state database containing two isolated projects."""
    database_url = f"sqlite:///{tmp_path}/security-runtime.db"
    dispose_engines()
    initialize_database(database_url)
    factory = get_session_factory(database_url)
    with factory() as session:
        session.add_all(
            [
                Project(
                    project_id="project-alpha",
                    name="Alpha",
                    status="active",
                    adapter_id="software",
                    metadata_json={},
                ),
                Project(
                    project_id="project-beta",
                    name="Beta",
                    status="active",
                    adapter_id="software",
                    metadata_json={},
                ),
            ]
        )
        session.commit()
    yield factory
    dispose_engines()


def _profile(version: str = "1.0") -> SecurityProfile:
    baseline = SecurityOverlay(
        overlay_id="baseline",
        version="2026.1",
        scope="global",
        controls=(SecurityControl("CTRL-1", "mandatory", "source-2026.1"),),
    )
    return SecurityProfile.compose(
        security_profile_id="profile-alpha",
        profile_version=version,
        project_id="project-alpha",
        domain="software",
        jurisdictions=("AR",),
        global_baseline=baseline,
        data_classes=("credential-data",),
        critical_assets=("asset://payments",),
    )


def _evidence_verdict(status: str = "failed") -> ControlEvidenceVerdict:
    return ControlEvidenceVerdict(
        control_id="CTRL-1",
        applicability="applicable",
        applicability_rationale=None,
        expected_evidence=("scanner raw payload must not persist",),
        observed_evidence_refs=("evidence://scan/1",),
        verification_method="scanner",
        performed_at="2026-07-16T19:00:00+00:00",
        verifier="verifier://security/1",
        status=status,  # type: ignore[arg-type]
        limitations=(f"credential {PRIVATE_TEST_TEXT} must not persist",),
        source_version="source-2026.1",
    )


def _readiness(status: str = "blocked") -> SecurityReadinessVerdict:
    blocked = ("SEC-1",) if status == "blocked" else ()
    return SecurityReadinessVerdict(
        policy_id="policy-security-assurance",
        status=status,  # type: ignore[arg-type]
        blocking_finding_ids=blocked,
        accepted_finding_ids=(),
        reasons=("sensitive explanatory text must not persist",),
        evaluated_at=datetime(2026, 7, 16, 19, 1, tzinfo=timezone.utc),
    )


def _risk_acceptance() -> RiskAcceptanceRecord:
    proposed_at = datetime(2026, 7, 16, 18, 0, tzinfo=timezone.utc)
    approved_at = proposed_at + timedelta(minutes=10)
    return RiskAcceptanceRecord(
        acceptance_id="acceptance-1",
        finding_id="SEC-1",
        decision="accept",
        status="active",
        owner=HumanRiskAuthority("principal://owner/1", "risk-owner"),
        scope=("SEC-1",),
        rationale=f"credential {PRIVATE_TEST_TEXT} must not persist",
        compensating_controls=("CTRL-COMP-1",),
        evidence_refs=("evidence://approval/1",),
        proposed_at=proposed_at,
        review_at=proposed_at + timedelta(days=7),
        expires_at=proposed_at + timedelta(days=30),
        approved_by=HumanRiskAuthority("principal://approver/1", "security-approver"),
        approved_at=approved_at,
        activated_at=approved_at + timedelta(minutes=1),
    )


def _checkpoint(version: int) -> RunCheckpoint:
    return RunCheckpoint(
        checkpoint_id=f"security-checkpoint-{version}",
        version=version,
        run_id="security-run-1",
        bundle_id="bundle-security-1",
        objective_id="security-objective-1",
        bundle_content_hash="sha256:" + "a" * 64,
        active_stage_id=None,
        active_attempt=1,
        completed_stage_ids=("security-assurance",),
        skipped_stage_ids=(),
        blocked_stage_ids=(),
        artifact_refs=(),
        evidence_refs=(),
        pending_approval_ids=(),
        budget_consumed=10,
        budget_remaining=90,
        recovery_state=None,
        replan_state=None,
        next_eligible_stage_ids=(),
    )


def _stage_result(status: str = "passed") -> StageResult:
    return StageResult(
        stage_id="security-assurance",
        status=status,  # type: ignore[arg-type]
        attempt=1,
        artifact_refs=(),
        evidence_refs=(),
        finding_refs=(),
        started_at="2026-07-16T19:00:00+00:00",
        completed_at="2026-07-16T19:01:00+00:00",
        next_stage_ids=(),
    )


def _create_finding(session: Session, *, project_id: str = "project-alpha") -> None:
    GapRepository(session).create_gap(
        gap_id="SEC-1",
        project_id=project_id,
        title="Authorization control requires verification",
        status="open",
        lens="security",
        impact="high",
        evidence_refs=("evidence://scan/1",),
        control_refs=("CTRL-1",),
    )


def test_persists_immutable_history_and_remediation_lineage(
    session_factory: sessionmaker[Session],
) -> None:
    """Two evaluations retain ordered history and explicit causal remediation."""
    with session_factory() as session:
        _create_finding(session)
        runtime = SecurityAssuranceRuntime(session)
        first = runtime.persist_transition(
            profile=_profile("1.0"),
            finding_ids=("SEC-1",),
            evidence_verdicts=(_evidence_verdict("failed"),),
            readiness_verdict=_readiness("blocked"),
            risk_acceptances=(),
            checkpoint=_checkpoint(1),
            stage_result=_stage_result("blocked"),
            expected_checkpoint_version=0,
            transition_sequence=1,
        )
        second = runtime.persist_transition(
            profile=_profile("2.0"),
            finding_ids=("SEC-1",),
            evidence_verdicts=(_evidence_verdict("passed"),),
            readiness_verdict=_readiness("ready"),
            risk_acceptances=(_risk_acceptance(),),
            checkpoint=_checkpoint(2),
            stage_result=_stage_result(),
            expected_checkpoint_version=1,
            transition_sequence=2,
            remediation_parent_version_ids=(first.readiness_version_id,),
        )

        profile_history = runtime.list_history(
            project_id="project-alpha", artifact_type="security-profile"
        )
        links = tuple(session.scalars(select(ArtifactLink)))

    assert [item.metadata_json["profile_version"] for item in profile_history] == [
        "1.0",
        "2.0",
    ]
    assert first.readiness_version_id != second.readiness_version_id
    assert any(
        link.source_artifact_id == first.readiness_version_id
        and link.target_artifact_id in second.artifact_version_ids
        and link.link_type == "remediated-by"
        for link in links
    )


def test_resume_uses_authoritative_project_scoped_checkpoint(
    session_factory: sessionmaker[Session],
) -> None:
    """A new runtime resumes only a checkpoint whose artifacts belong to the project."""
    with session_factory() as session:
        _create_finding(session)
        committed = SecurityAssuranceRuntime(session).persist_transition(
            profile=_profile(),
            finding_ids=("SEC-1",),
            evidence_verdicts=(_evidence_verdict(),),
            readiness_verdict=_readiness(),
            risk_acceptances=(),
            checkpoint=_checkpoint(1),
            stage_result=_stage_result("blocked"),
            expected_checkpoint_version=0,
            transition_sequence=1,
        )

    with session_factory() as session:
        runtime = SecurityAssuranceRuntime(session)
        resumed = runtime.resume(
            project_id="project-alpha",
            run_id="security-run-1",
            bundle_content_hash="sha256:" + "a" * 64,
        )
        with pytest.raises(ValueError, match="project scope"):
            runtime.resume(
                project_id="project-beta",
                run_id="security-run-1",
                bundle_content_hash="sha256:" + "a" * 64,
            )

    assert resumed.version == 1
    assert resumed.artifact_refs == committed.artifact_version_ids


def test_rejects_cross_project_findings_without_partial_persistence(
    session_factory: sessionmaker[Session],
) -> None:
    """A finding from another project cannot enter artifacts or checkpoint state."""
    with session_factory() as session:
        _create_finding(session, project_id="project-beta")
        runtime = SecurityAssuranceRuntime(session)

        with pytest.raises(ValueError, match="project-scoped security finding"):
            runtime.persist_transition(
                profile=_profile(),
                finding_ids=("SEC-1",),
                evidence_verdicts=(_evidence_verdict(),),
                readiness_verdict=_readiness(),
                risk_acceptances=(),
                checkpoint=_checkpoint(1),
                stage_result=_stage_result("blocked"),
                expected_checkpoint_version=0,
                transition_sequence=1,
            )

        assert session.scalar(select(ArtifactVersion)) is None
        assert session.get(StageCheckpointRecord, "security-run-1") is None


def test_checkpoint_conflict_rolls_back_staged_artifacts(
    session_factory: sessionmaker[Session],
) -> None:
    """A late checkpoint CAS failure leaves no partial artifact or lineage writes."""
    with session_factory() as session:
        _create_finding(session)
        runtime = SecurityAssuranceRuntime(session)
        runtime.persist_transition(
            profile=_profile(),
            finding_ids=("SEC-1",),
            evidence_verdicts=(_evidence_verdict(),),
            readiness_verdict=_readiness(),
            risk_acceptances=(),
            checkpoint=_checkpoint(1),
            stage_result=_stage_result("blocked"),
            expected_checkpoint_version=0,
            transition_sequence=1,
        )
        artifact_count = len(tuple(session.scalars(select(ArtifactVersion))))
        link_count = len(tuple(session.scalars(select(ArtifactLink))))

        with pytest.raises(ValueError, match="checkpoint version"):
            runtime.persist_transition(
                profile=_profile("2.0"),
                finding_ids=("SEC-1",),
                evidence_verdicts=(_evidence_verdict("passed"),),
                readiness_verdict=_readiness("ready"),
                risk_acceptances=(),
                checkpoint=_checkpoint(2),
                stage_result=_stage_result(),
                expected_checkpoint_version=0,
                transition_sequence=2,
            )

        assert len(tuple(session.scalars(select(ArtifactVersion)))) == artifact_count
        assert len(tuple(session.scalars(select(ArtifactLink)))) == link_count


def test_transition_replay_does_not_duplicate_security_history(
    session_factory: sessionmaker[Session],
) -> None:
    """The HSR idempotency key reuses committed artifacts without appending history."""
    with session_factory() as session:
        _create_finding(session)
        runtime = SecurityAssuranceRuntime(session)
        arguments = {
            "profile": _profile(),
            "finding_ids": ("SEC-1",),
            "evidence_verdicts": (_evidence_verdict(),),
            "readiness_verdict": _readiness(),
            "risk_acceptances": (),
            "checkpoint": _checkpoint(1),
            "stage_result": _stage_result("blocked"),
            "expected_checkpoint_version": 0,
            "transition_sequence": 1,
        }
        first = runtime.persist_transition(**arguments)  # type: ignore[arg-type]
        artifact_count = len(tuple(session.scalars(select(ArtifactVersion))))
        link_count = len(tuple(session.scalars(select(ArtifactLink))))

        replay = runtime.persist_transition(**arguments)  # type: ignore[arg-type]

        assert replay.artifact_version_ids == first.artifact_version_ids
        assert len(tuple(session.scalars(select(ArtifactVersion)))) == artifact_count
        assert len(tuple(session.scalars(select(ArtifactLink)))) == link_count


def test_persists_safe_metadata_only_and_rejects_unsafe_references(
    session_factory: sessionmaker[Session],
) -> None:
    """Raw evidence, credentials, scanner payloads, and sensitive prose stay out."""
    with session_factory() as session:
        _create_finding(session)
        runtime = SecurityAssuranceRuntime(session)
        runtime.persist_transition(
            profile=_profile(),
            finding_ids=("SEC-1",),
            evidence_verdicts=(_evidence_verdict(),),
            readiness_verdict=_readiness(),
            risk_acceptances=(_risk_acceptance(),),
            checkpoint=_checkpoint(1),
            stage_result=_stage_result("blocked"),
            expected_checkpoint_version=0,
            transition_sequence=1,
        )
        artifact_dump = json.dumps(
            [item.metadata_json for item in session.scalars(select(ArtifactVersion))],
            sort_keys=True,
        )
        checkpoint_dump = json.dumps(
            session.get(StageCheckpointRecord, "security-run-1").checkpoint_payload,
            sort_keys=True,
        )
        outbox_dump = json.dumps(
            [item.payload for item in session.scalars(select(StageTransitionOutbox))],
            sort_keys=True,
        )

    persisted = artifact_dump + checkpoint_dump + outbox_dump
    assert PRIVATE_TEST_TEXT not in persisted
    assert "scanner raw payload" not in persisted
    assert "sensitive explanatory text" not in persisted
    assert "expected_evidence" not in persisted
    assert "limitations" not in persisted
    assert "rationale" not in persisted

    unsafe_verdicts = (
        replace(_evidence_verdict(), observed_evidence_refs=("raw scanner payload",)),
        replace(
            _evidence_verdict(),
            verification_method="scanner?payload",
        ),
    )
    for index, unsafe in enumerate(unsafe_verdicts, start=1):
        with session_factory() as session:
            runtime = SecurityAssuranceRuntime(session)
            run_id = f"unsafe-run-{index}"
            with pytest.raises(ValueError, match="safe opaque reference"):
                runtime.persist_transition(
                    profile=_profile(),
                    finding_ids=("SEC-1",),
                    evidence_verdicts=(unsafe,),
                    readiness_verdict=_readiness(),
                    risk_acceptances=(),
                    checkpoint=replace(
                        _checkpoint(1),
                        checkpoint_id=f"unsafe-checkpoint-{index}",
                        run_id=run_id,
                    ),
                    stage_result=_stage_result("blocked"),
                    expected_checkpoint_version=0,
                    transition_sequence=1,
                )
            assert session.get(StageCheckpointRecord, run_id) is None
