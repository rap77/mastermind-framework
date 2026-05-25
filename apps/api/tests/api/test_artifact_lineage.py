"""TDD tests for artifact versioning and lineage — AV1 schema foundation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.models import ArtifactVersion
from mastermind_cli.project_state.models.project import Project
from mastermind_cli.project_state.repositories.artifacts import ArtifactRepository


@pytest.fixture()
def db_url(tmp_path: Path) -> str:
    """Return a fresh SQLite URL and initialize the project-state schema."""
    url = f"sqlite:///{tmp_path}/artifact_lineage_test.db"
    dispose_engines()
    initialize_database(url)
    return url


@pytest.fixture()
def session_factory(db_url: str):
    """Return a session factory bound to the test database."""
    return get_session_factory(db_url)


@pytest.fixture()
def seeded_project(session_factory) -> str:
    """Insert a parent Project row and return its ID."""
    project_id = "project-lineage-001"
    with session_factory() as session:
        session.add(
            Project(
                project_id=project_id,
                name="Lineage Test Project",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.commit()
    return project_id


# ---------------------------------------------------------------------------
# AV1 — Schema creation
# ---------------------------------------------------------------------------


def test_initialize_database_creates_artifact_versions_table(db_url: str) -> None:
    """initialize_database() must create the ps_artifact_versions table."""
    from sqlalchemy import inspect

    from mastermind_cli.project_state.database.session import get_engine

    engine = get_engine(db_url)
    inspector = inspect(engine)
    assert "ps_artifact_versions" in inspector.get_table_names()


def test_initialize_database_creates_artifact_links_table(db_url: str) -> None:
    """initialize_database() must create the ps_artifact_links table."""
    from sqlalchemy import inspect

    from mastermind_cli.project_state.database.session import get_engine

    engine = get_engine(db_url)
    inspector = inspect(engine)
    assert "ps_artifact_links" in inspector.get_table_names()


# ---------------------------------------------------------------------------
# AV1 — Model imports
# ---------------------------------------------------------------------------


def test_artifact_version_importable_from_project_state_models() -> None:
    """ArtifactVersion must be importable from project_state.models."""
    from mastermind_cli.project_state import models

    assert hasattr(models, "ArtifactVersion")


def test_artifact_link_importable_from_project_state_models() -> None:
    """ArtifactLink must be importable from project_state.models."""
    from mastermind_cli.project_state import models

    assert hasattr(models, "ArtifactLink")


# ---------------------------------------------------------------------------
# AV1 — Repository: create_version
# ---------------------------------------------------------------------------


def test_create_version_persists_and_returns_artifact_version(
    session_factory, seeded_project: str
) -> None:
    """ArtifactRepository.create_version() must persist and return the record."""
    repo = ArtifactRepository(session_factory())
    version = repo.create_version(
        version_id="version-001",
        artifact_id="artifact-001",
        project_id=seeded_project,
        artifact_type="spec",
        version=1,
        content_hash="sha256:abc",
        created_at=datetime.now(timezone.utc),
        metadata_json={"author": "brain-01"},
    )
    assert version.version_id == "version-001"
    assert version.artifact_id == "artifact-001"
    assert version.project_id == seeded_project
    assert version.artifact_type == "spec"
    assert version.version == 1
    assert version.content_hash == "sha256:abc"
    assert version.metadata_json == {"author": "brain-01"}


def test_create_version_is_queryable_after_commit(
    session_factory, seeded_project: str
) -> None:
    """A version created via the repository must be readable in a new session."""
    repo = ArtifactRepository(session_factory())
    repo.create_version(
        version_id="version-002",
        artifact_id="artifact-002",
        project_id=seeded_project,
        artifact_type="plan",
        version=1,
        content_hash="sha256:def",
        created_at=datetime.now(timezone.utc),
        metadata_json={},
    )

    with session_factory() as fresh_session:
        from sqlalchemy import select

        row = fresh_session.execute(
            select(ArtifactVersion).where(ArtifactVersion.version_id == "version-002")
        ).scalar_one_or_none()
    assert row is not None
    assert row.artifact_type == "plan"


# ---------------------------------------------------------------------------
# AV1 — Repository: create_link
# ---------------------------------------------------------------------------


def test_create_link_persists_and_returns_artifact_link(
    session_factory, seeded_project: str
) -> None:
    """ArtifactRepository.create_link() must persist and return the record."""
    repo = ArtifactRepository(session_factory())

    source = repo.create_version(
        version_id="version-src",
        artifact_id="artifact-src",
        project_id=seeded_project,
        artifact_type="spec",
        version=1,
        content_hash="sha256:src",
        created_at=datetime.now(timezone.utc),
        metadata_json={},
    )
    target = repo.create_version(
        version_id="version-tgt",
        artifact_id="artifact-tgt",
        project_id=seeded_project,
        artifact_type="plan",
        version=1,
        content_hash="sha256:tgt",
        created_at=datetime.now(timezone.utc),
        metadata_json={},
    )

    link = repo.create_link(
        link_id="link-001",
        source_artifact_id=source.version_id,
        target_artifact_id=target.version_id,
        link_type="derived_from",
        created_at=datetime.now(timezone.utc),
    )
    assert link.link_id == "link-001"
    assert link.source_artifact_id == source.version_id
    assert link.target_artifact_id == target.version_id
    assert link.link_type == "derived_from"
    assert link.task_id is None
    assert link.decision_id is None
    assert link.checkpoint_id is None


# ---------------------------------------------------------------------------
# AV1 — Repository: get_versions_by_artifact_id
# ---------------------------------------------------------------------------


def test_get_versions_by_artifact_id_returns_in_ascending_version_order(
    session_factory, seeded_project: str
) -> None:
    """get_versions_by_artifact_id() must return versions sorted ascending by version."""
    repo = ArtifactRepository(session_factory())
    artifact_id = "artifact-multi"
    now = datetime.now(timezone.utc)

    repo.create_version(
        version_id="version-multi-2",
        artifact_id=artifact_id,
        project_id=seeded_project,
        artifact_type="decision",
        version=2,
        content_hash="sha256:v2",
        created_at=now,
        metadata_json={},
    )
    repo.create_version(
        version_id="version-multi-1",
        artifact_id=artifact_id,
        project_id=seeded_project,
        artifact_type="decision",
        version=1,
        content_hash="sha256:v1",
        created_at=now,
        metadata_json={},
    )
    repo.create_version(
        version_id="version-multi-3",
        artifact_id=artifact_id,
        project_id=seeded_project,
        artifact_type="decision",
        version=3,
        content_hash="sha256:v3",
        created_at=now,
        metadata_json={},
    )

    versions = repo.get_versions_by_artifact_id(artifact_id)
    assert [v.version for v in versions] == [1, 2, 3]


def test_get_versions_by_artifact_id_returns_empty_list_for_unknown_id(
    session_factory,
) -> None:
    """get_versions_by_artifact_id() must return [] when no versions exist."""
    repo = ArtifactRepository(session_factory())
    result = repo.get_versions_by_artifact_id("nonexistent-artifact")
    assert result == []
