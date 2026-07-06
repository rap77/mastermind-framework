"""Integration smoke tests for MemoryService against PostgreSQL."""

from __future__ import annotations

import os
from uuid import uuid4

import asyncpg
import pytest

from mastermind_cli.memory_layer.migrate import upgrade_to_head
from mastermind_cli.memory_layer.models import RunSummary
from mastermind_cli.memory_layer.runtime import build_memory_store_from_env
from mastermind_cli.memory_layer.service import MemoryService


def _database_url() -> str:
    """Return ``DATABASE_URL`` from the environment, skipping if missing."""
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL is not configured")
    return url


@pytest.mark.integration
@pytest.mark.asyncio
async def test_memory_service_round_trips_through_postgres() -> None:
    """MemoryService should persist and rehydrate canonical records on Postgres."""
    url = _database_url()
    upgrade_to_head(url)
    suffix = uuid4().hex
    project_id = f"proj-postgres-{suffix}"
    task_id = f"task-postgres-{suffix}"
    run_id = f"run-postgres-{suffix}"
    checkpoint_id = f"ckpt-postgres-{suffix}"
    decision_id = f"dec-postgres-{suffix}"
    service = MemoryService(
        build_memory_store_from_env(
            url,
            enable_vector=False,
            enable_index=False,
        )
    )

    checkpoint = await service.record_checkpoint(
        checkpoint_id=checkpoint_id,
        project_id=project_id,
        task_id=task_id,
        run_id=run_id,
        next_step_summary="Continue after the PostgreSQL smoke test.",
        context_summary={"task_id": task_id},
        resume_state={"loop_policy_id": "execute+verify-light"},
    )
    decision = await service.record_decision(
        decision_id=decision_id,
        project_id=project_id,
        task_id=task_id,
        title="Postgres smoke decision",
        status="accepted",
        rationale_markdown="The canonical Postgres store works end to end.",
        metadata={"source": "integration-smoke"},
    )
    await service.save_run_summary(
        RunSummary(
            run_id=run_id,
            project_id=project_id,
            summary="Postgres memory smoke test.",
            metadata={"suite": "integration", "task_id": task_id},
        )
    )

    snapshot = await service.build_context_snapshot(
        project_id,
        task_id=task_id,
    )

    assert checkpoint.checkpoint_id == checkpoint_id
    assert decision.decision_id == decision_id
    assert snapshot.checkpoints
    assert snapshot.decisions
    assert snapshot.checkpoints[0].checkpoint_id == checkpoint_id
    assert snapshot.decisions[0].decision_id == decision_id

    conn: asyncpg.Connection = await asyncpg.connect(url)
    try:
        row_count = await conn.fetchval(
            "SELECT COUNT(*) FROM mm_memory_items WHERE project_id = $1",
            project_id,
        )
        session_count = await conn.fetchval(
            "SELECT COUNT(*) FROM mm_memory_sessions WHERE project_id = $1",
            project_id,
        )
        assert row_count == 2
        assert session_count == 1
    finally:
        await conn.close()
