"""Security extensions for the universal project-state Gap Registry."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy.orm import Session, sessionmaker

from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.models.gap import GapRecord
from mastermind_cli.project_state.models.project import Project
from mastermind_cli.project_state.repositories.gaps import GapRepository

SECRET_LIKE_VALUE = "sk-" + ("a" * 16)
TOKEN_LIKE_VALUE = ".".join(("eyJheader", "payload", "signature"))


@pytest.fixture()
def session_factory(tmp_path: Path) -> Iterator[sessionmaker[Session]]:
    """Return a session factory with one project in a fresh database."""
    database_url = f"sqlite:///{tmp_path}/security-gaps.db"
    dispose_engines()
    initialize_database(database_url)
    factory = get_session_factory(database_url)
    with factory() as session:
        session.add(
            Project(
                project_id="project-security",
                name="Security Project",
                status="active",
                adapter_id="software",
                metadata_json={},
            )
        )
        session.commit()
    yield factory
    dispose_engines()


@pytest.fixture()
def repository(session_factory: sessionmaker[Session]) -> Iterator[GapRepository]:
    """Return a repository whose database session is closed after each test."""
    with session_factory() as session:
        yield GapRepository(session)


def _create_security_gap(
    repository: GapRepository, gap_id: str = "SEC-001"
) -> GapRecord:
    """Persist a representative security finding through the shared registry."""
    return repository.create_gap(
        gap_id=gap_id,
        project_id="project-security",
        title="Unverified transaction authorization",
        status="open",
        lens="security",
        threat="unauthorized-transaction",
        impact="critical",
        likelihood="medium",
        residual_risk="high",
        treatment="mitigate",
        approval_required=True,
        risk_acceptance_id=None,
        review_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        evidence_refs=("artifact://verification/SEC-001",),
        control_refs=("FIN-AUTH-04",),
    )


def test_security_gap_persists_in_universal_registry(
    repository: GapRepository,
) -> None:
    """Security findings retain assurance metadata in the shared gap table."""
    gap = _create_security_gap(repository)

    assert gap.gap_id == "SEC-001"
    assert gap.lens == "security"
    assert gap.threat == "unauthorized-transaction"
    assert gap.impact == "critical"
    assert gap.likelihood == "medium"
    assert gap.evidence_refs == ["artifact://verification/SEC-001"]
    assert gap.control_refs == ["FIN-AUTH-04"]
    assert gap.residual_risk == "high"
    assert gap.treatment == "mitigate"
    assert gap.approval_required is True
    assert gap.risk_acceptance_id is None
    assert gap.review_at is not None


def test_non_security_gap_uses_same_registry(repository: GapRepository) -> None:
    """The schema remains universal instead of creating a security-only backlog."""
    gap = repository.create_gap(
        gap_id="GAP-001",
        project_id="project-security",
        title="Missing product decision",
        status="open",
        lens="product",
    )

    assert gap.lens == "product"
    assert gap.threat is None
    assert repository.get_by_id("project-security", "GAP-001") is not None


def test_evidence_and_control_references_are_queryable(
    repository: GapRepository,
) -> None:
    """Evidence and controls can locate findings without storing raw evidence."""
    _create_security_gap(repository, "SEC-QUERY")

    by_evidence = repository.list_by_evidence_ref(
        "project-security", "artifact://verification/SEC-001"
    )
    by_control = repository.list_by_control_ref("project-security", "FIN-AUTH-04")

    assert [gap.gap_id for gap in by_evidence] == ["SEC-QUERY"]
    assert [gap.gap_id for gap in by_control] == ["SEC-QUERY"]


def test_descriptive_values_are_redacted_before_persistence(
    repository: GapRepository,
) -> None:
    """Recognized secret material in descriptive text never reaches storage."""
    gap = repository.create_gap(
        gap_id="SEC-REDACT",
        project_id="project-security",
        title=f"Leaked key {SECRET_LIKE_VALUE}",
        status="open",
        lens="security",
        threat=f"token {TOKEN_LIKE_VALUE} was exposed",
    )

    assert gap.title == "Leaked key [REDACTED_SECRET]"
    assert gap.threat == "token [REDACTED_TOKEN] was exposed"


@pytest.mark.parametrize(
    "field_name, reference",
    [
        ("evidence_refs", SECRET_LIKE_VALUE),
        ("evidence_refs", "https://evidence.test/item?token=raw-value"),
        ("control_refs", "raw control payload with spaces"),
    ],
)
def test_sensitive_or_raw_references_are_rejected(
    repository: GapRepository, field_name: str, reference: str
) -> None:
    """Reference fields fail closed rather than persisting sensitive payloads."""
    arguments = {field_name: (reference,)}

    with pytest.raises(ValueError, match="safe opaque reference"):
        repository.create_gap(
            gap_id="SEC-REJECT",
            project_id="project-security",
            title="Unsafe reference",
            status="open",
            lens="security",
            **arguments,
        )

    assert repository.get_by_id("project-security", "SEC-REJECT") is None


def test_unknown_security_risk_value_fails_closed(
    repository: GapRepository,
) -> None:
    """Unrecognized security classifications cannot silently enter the registry."""
    with pytest.raises(ValueError, match="Unsupported likelihood"):
        repository.create_gap(
            gap_id="SEC-INVALID",
            project_id="project-security",
            title="Unknown classification",
            status="open",
            lens="security",
            likelihood="almost-certain",
        )


def test_sensitive_risk_acceptance_reference_is_rejected(
    repository: GapRepository,
) -> None:
    """Approval references cannot be used to smuggle secret material."""
    with pytest.raises(ValueError, match="safe opaque reference"):
        repository.create_gap(
            gap_id="SEC-APPROVAL",
            project_id="project-security",
            title="Unsafe approval reference",
            status="open",
            lens="security",
            risk_acceptance_id=SECRET_LIKE_VALUE,
        )
