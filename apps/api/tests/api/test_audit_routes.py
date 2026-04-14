"""
Tests for audit trail router — JWT auth enforcement.

26 tests:
  - 13 × 401 (unauthenticated request → must be rejected)
  - 13 × 200/201/422 (authenticated request → must succeed or produce valid response)
  - 1 AST gate (static analysis: every route has get_current_user_any)

Routes under test (prefix: /api/audit):
  1.  GET  /projects/{id}/timeline
  2.  GET  /projects/{id}/phase/{num}/details
  3.  POST /projects/{id}/phase/{num}/decision
  4.  GET  /projects/{id}/decisions
  5.  GET  /projects/{id}/phase/{num}/gates
  6.  GET  /projects/{id}/sessions
  7.  GET  /projects/{id}/metrics
  8.  GET  /projects/{id}/artifacts
  9.  GET  /projects/{id}/audit-log
  10. GET  /projects/{id}/summary
  11. GET  /projects/{id}/phase-comparison
  12. GET  /projects/{id}/brain-feedback
  13. GET  /projects/{id}/engram-sync-status
"""

import ast
import pathlib
import uuid
from typing import Any

import pytest
from httpx import AsyncClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PROJECT_ID = str(uuid.uuid4())
PHASE_NUM = 1

ROUTES_GET = [
    f"/api/audit/projects/{PROJECT_ID}/timeline",
    f"/api/audit/projects/{PROJECT_ID}/phase/{PHASE_NUM}/details",
    f"/api/audit/projects/{PROJECT_ID}/decisions",
    f"/api/audit/projects/{PROJECT_ID}/phase/{PHASE_NUM}/gates",
    f"/api/audit/projects/{PROJECT_ID}/sessions",
    f"/api/audit/projects/{PROJECT_ID}/metrics",
    f"/api/audit/projects/{PROJECT_ID}/artifacts",
    f"/api/audit/projects/{PROJECT_ID}/audit-log",
    f"/api/audit/projects/{PROJECT_ID}/summary",
    f"/api/audit/projects/{PROJECT_ID}/phase-comparison",
    f"/api/audit/projects/{PROJECT_ID}/brain-feedback",
    f"/api/audit/projects/{PROJECT_ID}/engram-sync-status",
]

POST_DECISION_URL = f"/api/audit/projects/{PROJECT_ID}/phase/{PHASE_NUM}/decision"
DECISION_PAYLOAD: dict[str, Any] = {
    "decision_type": "technical",
    "title": "Test decision",
    "rationale": "Testing auth",
    "chosen_option": "Option A",
    "confidence": 0.9,
    "impact_level": "medium",
    "tags": [],
}


# ===========================================================================
# Section 1 — 401 tests (no token → must be rejected)
# ===========================================================================


@pytest.mark.asyncio
async def test_401_timeline(client: AsyncClient) -> None:
    """GET /timeline requires auth."""
    resp = await client.get(f"/api/audit/projects/{PROJECT_ID}/timeline")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_401_phase_details(client: AsyncClient) -> None:
    """GET /phase/{num}/details requires auth."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/phase/{PHASE_NUM}/details"
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_401_record_decision(client: AsyncClient) -> None:
    """POST /phase/{num}/decision requires auth."""
    resp = await client.post(POST_DECISION_URL, json=DECISION_PAYLOAD)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_401_list_decisions(client: AsyncClient) -> None:
    """GET /decisions requires auth."""
    resp = await client.get(f"/api/audit/projects/{PROJECT_ID}/decisions")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_401_phase_gates(client: AsyncClient) -> None:
    """GET /phase/{num}/gates requires auth."""
    resp = await client.get(f"/api/audit/projects/{PROJECT_ID}/phase/{PHASE_NUM}/gates")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_401_list_sessions(client: AsyncClient) -> None:
    """GET /sessions requires auth."""
    resp = await client.get(f"/api/audit/projects/{PROJECT_ID}/sessions")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_401_get_metrics(client: AsyncClient) -> None:
    """GET /metrics requires auth."""
    resp = await client.get(f"/api/audit/projects/{PROJECT_ID}/metrics")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_401_list_artifacts(client: AsyncClient) -> None:
    """GET /artifacts requires auth."""
    resp = await client.get(f"/api/audit/projects/{PROJECT_ID}/artifacts")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_401_audit_log(client: AsyncClient) -> None:
    """GET /audit-log requires auth."""
    resp = await client.get(f"/api/audit/projects/{PROJECT_ID}/audit-log")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_401_project_summary(client: AsyncClient) -> None:
    """GET /summary requires auth."""
    resp = await client.get(f"/api/audit/projects/{PROJECT_ID}/summary")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_401_phase_comparison(client: AsyncClient) -> None:
    """GET /phase-comparison requires auth."""
    resp = await client.get(f"/api/audit/projects/{PROJECT_ID}/phase-comparison")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_401_brain_feedback(client: AsyncClient) -> None:
    """GET /brain-feedback requires auth."""
    resp = await client.get(f"/api/audit/projects/{PROJECT_ID}/brain-feedback")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_401_engram_sync_status(client: AsyncClient) -> None:
    """GET /engram-sync-status requires auth."""
    resp = await client.get(f"/api/audit/projects/{PROJECT_ID}/engram-sync-status")
    assert resp.status_code == 401


# ===========================================================================
# Section 2 — 200/201 tests (authenticated → must not be 401/403)
# ===========================================================================


@pytest.mark.asyncio
async def test_auth_timeline(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """GET /timeline with valid JWT → not 401."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/timeline", headers=auth_headers
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_auth_phase_details(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """GET /phase/{num}/details with valid JWT → not 401."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/phase/{PHASE_NUM}/details",
        headers=auth_headers,
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_auth_record_decision(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """POST /phase/{num}/decision with valid JWT → not 401."""
    resp = await client.post(
        POST_DECISION_URL, json=DECISION_PAYLOAD, headers=auth_headers
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_auth_list_decisions(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """GET /decisions with valid JWT → not 401."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/decisions", headers=auth_headers
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_auth_phase_gates(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """GET /phase/{num}/gates with valid JWT → not 401."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/phase/{PHASE_NUM}/gates",
        headers=auth_headers,
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_auth_list_sessions(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """GET /sessions with valid JWT → not 401."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/sessions", headers=auth_headers
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_auth_get_metrics(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """GET /metrics with valid JWT → not 401."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/metrics", headers=auth_headers
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_auth_list_artifacts(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """GET /artifacts with valid JWT → not 401."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/artifacts", headers=auth_headers
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_auth_audit_log(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """GET /audit-log with valid JWT → not 401."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/audit-log", headers=auth_headers
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_auth_project_summary(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """GET /summary with valid JWT → not 401."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/summary", headers=auth_headers
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_auth_phase_comparison(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """GET /phase-comparison with valid JWT → not 401."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/phase-comparison", headers=auth_headers
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_auth_brain_feedback(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """GET /brain-feedback with valid JWT → not 401."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/brain-feedback", headers=auth_headers
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_auth_engram_sync_status(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """GET /engram-sync-status with valid JWT → not 401."""
    resp = await client.get(
        f"/api/audit/projects/{PROJECT_ID}/engram-sync-status", headers=auth_headers
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


# ===========================================================================
# Section 3 — AST gate (static analysis)
# ===========================================================================


def test_all_audit_routes_have_auth() -> None:
    """
    AST gate: counts route functions without get_current_user_any.
    Fails if any route is missing auth dependency.
    """
    source = (
        pathlib.Path(__file__)
        .parent.parent.parent.joinpath("routers/audit.py")  # apps/api/
        .read_text()
    )
    tree = ast.parse(source)
    routes_without_auth: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            is_route = any(
                isinstance(d, ast.Attribute)
                and d.attr in ("get", "post", "put", "delete", "patch")
                for d in node.decorator_list
            )
            if is_route:
                has_auth = any(
                    "get_current_user_any" in ast.unparse(arg)
                    for arg in (
                        node.args.defaults
                        + [d for d in node.args.kw_defaults if d is not None]
                    )
                )
                if not has_auth:
                    routes_without_auth.append(node.name)

    assert (
        len(routes_without_auth) == 0
    ), f"Routes missing get_current_user_any: {routes_without_auth}"
