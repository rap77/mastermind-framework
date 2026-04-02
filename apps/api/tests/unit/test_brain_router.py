"""Tests for brain_router.py — Fase 4 agent-restructuring.

Tests the brain-to-brain routing mechanism that allows Brain #1 to delegate
to other domain brains when it detects keywords in the brief.

Validates:
- route_to_brain() detects domain keywords correctly
- BRAIN_KEYWORDS covers all 7 domains
- emit_brain_routing_event() sends to parent task_id (Opción A)
- Sequential delegation (not parallel)
- No routing when keywords don't match

Brain #4 guidance: Opción A — reusar task_id padre, zero breaking changes.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mastermind_cli.types.interfaces import Brief


# ===== Constants =====

# Expected brain routing keywords — tested explicitly below
EXPECTED_BRAIN_KEYWORDS = {
    "brain-01-product": ["producto", "feature", "requerimiento", "user story", "prd"],
    "brain-02-ux": ["ux", "usuario", "flujo", "experiencia", "research", "journey"],
    "brain-03-ui": ["ui", "interfaz", "diseño", "componente", "layout", "visual"],
    "brain-04-frontend": [
        "frontend",
        "react",
        "nextjs",
        "component",
        "state",
        "zustand",
        "ws",
    ],
    "brain-05-backend": ["backend", "api", "endpoint", "database", "sql", "fastapi"],
    "brain-06-qa": ["test", "qa", "testing", "pytest", "coverage", "e2e"],
    "brain-07-growth": ["métrica", "analytics", "growth", "data", "kpi", "funnel"],
}


# ===== Fixtures =====


@pytest.fixture
def sample_brief():
    """Sample brief for testing."""
    return Brief(
        problem_statement="Implementar login con Google OAuth en Next.js",
        context="",  # Empty context to avoid keyword interference in tests
        target_audience=None,
    )


@pytest.fixture
def mock_websocket_manager():
    """Mock WebSocketManager for emit_brain_routing_event tests."""
    manager = MagicMock()
    manager.broadcast_task_update = AsyncMock()  # Must be AsyncMock for await
    return manager


# ===== BRAIN_KEYWORDS tests =====


def test_brain_keywords_covers_all_seven_domains():
    """BRAIN_KEYWORDS must cover all 7 brain domains."""
    from mastermind_cli.orchestrator.brain_router import BRAIN_KEYWORDS

    assert set(BRAIN_KEYWORDS.keys()) == set(EXPECTED_BRAIN_KEYWORDS.keys())


def test_brain_keywords_has_non_empty_lists():
    """Each brain must have at least one keyword for routing."""
    from mastermind_cli.orchestrator.brain_router import BRAIN_KEYWORDS

    for brain_id, keywords in BRAIN_KEYWORDS.items():
        assert len(keywords) > 0, f"{brain_id} has no keywords"


def test_brain_keywords_lowercase_for_matching():
    """All keywords must be lowercase for case-insensitive matching."""
    from mastermind_cli.orchestrator.brain_router import BRAIN_KEYWORDS

    for brain_id, keywords in BRAIN_KEYWORDS.items():
        for keyword in keywords:
            assert keyword.islower(), f"{brain_id} keyword '{keyword}' not lowercase"


# ===== route_to_brain tests =====


def test_route_to_frontend_brain_react_keyword(sample_brief):
    """Brain #1 delegates to Brain #4 when brief contains 'react'."""
    from mastermind_cli.orchestrator.brain_router import route_to_brain

    sample_brief.problem_statement = "Crear componente React para login"
    result = route_to_brain(sample_brief, from_brain_id="brain-01-product")

    assert result == "brain-04-frontend"


def test_route_to_frontend_brain_nextjs_keyword(sample_brief):
    """Brain #1 delegates to Brain #4 when brief contains 'nextjs'."""
    from mastermind_cli.orchestrator.brain_router import route_to_brain

    sample_brief.problem_statement = "Implementar router Next.js App Router"
    result = route_to_brain(sample_brief, from_brain_id="brain-01-product")

    assert result == "brain-04-frontend"


def test_route_to_backend_brain_api_keyword(sample_brief):
    """Brain #1 delegates to Brain #5 when brief contains 'api'."""
    from mastermind_cli.orchestrator.brain_router import route_to_brain

    sample_brief.problem_statement = "Crear endpoint POST /api/auth/login"
    result = route_to_brain(sample_brief, from_brain_id="brain-01-product")

    assert result == "brain-05-backend"


def test_route_to_backend_brain_fastapi_keyword(sample_brief):
    """Brain #1 delegates to Brain #5 when brief contains 'fastapi'."""
    from mastermind_cli.orchestrator.brain_router import route_to_brain

    sample_brief.problem_statement = "Implementar middleware FastAPI para JWT"
    result = route_to_brain(sample_brief, from_brain_id="brain-01-product")

    assert result == "brain-05-backend"


def test_no_routing_match_returns_none(sample_brief):
    """route_to_brain returns None when no domain keywords match."""
    from mastermind_cli.orchestrator.brain_router import route_to_brain

    sample_brief.problem_statement = "Revisar documentación del proyecto"
    result = route_to_brain(sample_brief, from_brain_id="brain-01-product")

    assert result is None


def test_route_to_brain_case_insensitive(sample_brief):
    """Keyword matching is case-insensitive."""
    from mastermind_cli.orchestrator.brain_router import route_to_brain

    # Test uppercase
    sample_brief.problem_statement = "Crear componente REACT para login"
    result = route_to_brain(sample_brief, from_brain_id="brain-01-product")
    assert result == "brain-04-frontend"

    # Test mixed case
    sample_brief.problem_statement = "Implementar API endpoint con FastAPI"
    result = route_to_brain(sample_brief, from_brain_id="brain-01-product")
    assert result == "brain-05-backend"


def test_route_to_brain_matches_context_field(sample_brief):
    """Keyword matching scans both problem_statement AND context."""
    from mastermind_cli.orchestrator.brain_router import route_to_brain

    sample_brief.problem_statement = "Implementar login"
    sample_brief.context = "Usar React para el frontend"

    result = route_to_brain(sample_brief, from_brain_id="brain-01-product")
    assert result == "brain-04-frontend"


# ===== emit_brain_routing_event tests =====


@pytest.mark.asyncio
async def test_emit_brain_routing_event_uses_parent_task_id(mock_websocket_manager):
    """emit_brain_routing_event sends to parent task_id (Opción A).

    Brain #4 guidance: Reuse task_id padre, zero breaking changes.
    Sub-task ID is payload data, NOT WS endpoint.
    """
    from mastermind_cli.orchestrator.brain_router import emit_brain_routing_event

    task_id = "parent-task-123"
    from_brain = "brain-01-product"
    to_brain = "brain-04-frontend"
    sub_task_id = "sub-task-abc"  # Only in payload, NOT WS endpoint

    with patch(
        "mastermind_cli.api.websocket.manager",
        mock_websocket_manager,
    ):
        await emit_brain_routing_event(task_id, from_brain, to_brain, sub_task_id)

    # Verify broadcast_task_update was called with parent task_id
    mock_websocket_manager.broadcast_task_update.assert_called_once()
    call_args = mock_websocket_manager.broadcast_task_update.call_args

    assert (
        call_args[0][0] == task_id
    )  # First positional arg is task_id (parent, NOT sub)
    # Verify payload structure
    event_payload = call_args[0][1]
    assert event_payload["type"] == "brain_routing"
    assert event_payload["data"]["from"] == from_brain
    assert event_payload["data"]["to"] == to_brain
    assert event_payload["data"]["sub_task_id"] == sub_task_id


@pytest.mark.asyncio
async def test_emit_brain_routing_event_payload_structure(mock_websocket_manager):
    """emit_brain_routing_event sends correct WS payload structure."""
    from mastermind_cli.orchestrator.brain_router import emit_brain_routing_event

    with patch(
        "mastermind_cli.api.websocket.manager",
        mock_websocket_manager,
    ):
        await emit_brain_routing_event(
            task_id="task-001",
            from_brain="brain-01-product",
            to_brain="brain-05-backend",
            sub_task_id="sub-xyz",
        )

    call_args = mock_websocket_manager.broadcast_task_update.call_args
    event_payload = call_args[0][1]  # Second positional arg

    # Verify payload matches BrainRoutingEventSchema from frontend
    assert event_payload["type"] == "brain_routing"
    assert event_payload["data"]["from"] == "brain-01-product"
    assert event_payload["data"]["to"] == "brain-05-backend"
    assert event_payload["data"]["sub_task_id"] == "sub-xyz"
    assert "timestamp" in event_payload["data"]
    assert isinstance(event_payload["data"]["timestamp"], int)


# ===== Sequential delegation tests =====


def test_route_to_brain_returns_single_target_only(sample_brief):
    """route_to_brain returns ONE brain ID, never a list.

    Brain-to-brain routing is sequential delegation, not parallel dispatch.
    Parallel dispatch is handled by task_runner.py via StatelessCoordinator.
    """
    from mastermind_cli.orchestrator.brain_router import route_to_brain

    # Brief with multiple domain keywords
    sample_brief.problem_statement = "Implementar React frontend con FastAPI backend"

    result = route_to_brain(sample_brief, from_brain_id="brain-01-product")

    # Must be a string or None, never a list
    assert isinstance(result, str) or result is None
    assert not isinstance(result, list)


# ===== Integration scenarios =====


def test_product_brain_delegates_to_frontend_for_ui_tasks(sample_brief):
    """Scenario: Brain #1 receives UI task → delegates to Brain #4."""
    from mastermind_cli.orchestrator.brain_router import route_to_brain

    sample_brief.problem_statement = "Crear componente Button React con estado"
    result = route_to_brain(sample_brief, from_brain_id="brain-01-product")

    assert result == "brain-04-frontend"


def test_product_brain_delegates_to_backend_for_api_tasks(sample_brief):
    """Scenario: Brain #1 receives API task → delegates to Brain #5."""
    from mastermind_cli.orchestrator.brain_router import route_to_brain

    sample_brief.problem_statement = "Crear endpoint GET /api/vehicles"
    result = route_to_brain(sample_brief, from_brain_id="brain-01-product")

    assert result == "brain-05-backend"


def test_product_brain_executes_when_no_domain_match(sample_brief):
    """Scenario: Brain #1 receives product-only task → executes itself."""
    from mastermind_cli.orchestrator.brain_router import route_to_brain

    sample_brief.problem_statement = "Definir roadmap Q2 para nuevo feature"
    result = route_to_brain(sample_brief, from_brain_id="brain-01-product")

    assert result is None  # No delegation, Brain #1 handles it
