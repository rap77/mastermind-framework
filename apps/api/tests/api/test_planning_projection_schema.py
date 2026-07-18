"""Schema tests for the planning projection tables in project_state."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import inspect

from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_engine,
    initialize_database,
)


def test_initialize_database_creates_planning_projection_tables(tmp_path: Path) -> None:
    """initialize_database() must create the planning projection tables."""
    database_url = f"sqlite:///{tmp_path}/planning_projection_test.db"
    dispose_engines()
    initialize_database(database_url)

    inspector = inspect(get_engine(database_url))
    table_names = set(inspector.get_table_names())

    assert "ps_objective_documents" in table_names
    assert "ps_objective_events" in table_names
    assert "ps_objective_projection" in table_names
    assert "ps_objective_sync_state" in table_names


def test_planning_projection_models_are_exported() -> None:
    """project_state.models must export the planning projection models."""
    from mastermind_cli.project_state import models

    assert hasattr(models, "ObjectiveDocumentRecord")
    assert hasattr(models, "ObjectiveEventRecord")
    assert hasattr(models, "ObjectiveProjectionState")
    assert hasattr(models, "ObjectiveSyncState")
