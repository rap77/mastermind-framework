"""Tests for GET /api/experiences/{brain_id} endpoint — Fase 2 validation.

Validates:
- Empty list for brain with no records
- Records returned in correct shape
- JWT auth required (401 without token)
- limit+offset pagination works
"""

import pytest

from mastermind_cli.experience.logger import ExperienceLogger
from mastermind_cli.state.database import DatabaseConnection

BRAIN_ID = "brain-01-product"


async def _seed_experiences(db_path: str, brain_id: str, count: int) -> None:
    """Insert N experience records for a brain."""
    async with DatabaseConnection(db_path) as db:
        await db.create_experience_schema()
        logger = ExperienceLogger(db)
        for i in range(count):
            await logger.log_execution(
                brain_id=brain_id,
                input_json={"brief": f"brief-{i}"},
                output_json={"result": f"output-{i}"},
                duration_ms=100 + i,
                status="success",
            )


# ===== Tests =====


@pytest.mark.asyncio
async def test_get_experiences_returns_empty_list(client, auth_headers):
    """Brain with no records returns empty list, not 404."""
    response = await client.get(
        "/api/experiences/brain-01-product", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_experiences_returns_records(client, auth_headers, db_path):
    """Records inserted are returned in correct shape."""
    await _seed_experiences(db_path, BRAIN_ID, count=3)

    response = await client.get(f"/api/experiences/{BRAIN_ID}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    record = data[0]
    assert "id" in record
    assert "timestamp" in record
    assert "status" in record
    assert "duration_ms" in record
    assert "output_json" in record
    assert record["status"] == "success"


@pytest.mark.asyncio
async def test_get_experiences_requires_auth(client):
    """Request without JWT returns 401."""
    response = await client.get("/api/experiences/brain-01-product")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_experiences_pagination(client, auth_headers, db_path):
    """limit+offset pagination returns correct slice."""
    await _seed_experiences(db_path, BRAIN_ID, count=5)

    # First page
    response = await client.get(
        f"/api/experiences/{BRAIN_ID}?limit=2&offset=0", headers=auth_headers
    )
    assert response.status_code == 200
    first_page = response.json()
    assert len(first_page) == 2

    # Second page
    response = await client.get(
        f"/api/experiences/{BRAIN_ID}?limit=2&offset=2", headers=auth_headers
    )
    assert response.status_code == 200
    second_page = response.json()
    assert len(second_page) == 2

    # IDs must not overlap between pages
    first_ids = {r["id"] for r in first_page}
    second_ids = {r["id"] for r in second_page}
    assert first_ids.isdisjoint(second_ids)
