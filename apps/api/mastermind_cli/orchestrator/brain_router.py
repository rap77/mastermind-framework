"""Brain-to-Brain Router — Fase 4 agent-restructuring.

Enables Brain #1 to delegate to other domain brains when it detects keywords
in the brief. Implements sequential delegation (not parallel dispatch).

Architecture Decision (Brain #4): Opción A — Reuse parent task_id for WS events.
Sub-task ID is payload data only, NOT a separate WS endpoint.

Brain #4 guidance:
- Zero breaking changes to wsStore.ts
- brain_routing is just another event type over the same socket
- Routing is transient topology, not persistent state
"""

import time
from mastermind_cli.types.interfaces import Brief


# =============================================================================
# BRAIN KEYWORDS FOR ROUTING
# =============================================================================

# Each brain domain has keywords that trigger delegation
# Keywords are lowercase for case-insensitive matching
# IMPORTANT: Order matters! More specific keywords first to avoid false matches
BRAIN_KEYWORDS: dict[str, list[str]] = {
    "brain-01-product": [
        "producto",
        "feature",
        "requerimiento",
        "user story",
        "prd",
        "roadmap",
        "backlog",
    ],
    "brain-02-ux": [
        "ux",
        "usuario",
        "flujo",
        "experiencia",
        "research",
        "journey",
        "pain point",
    ],
    "brain-03-ui": [
        "ui",
        "interfaz",
        "diseño visual",
        "layout",
        "estilo",
        "color",
        "tipografía",
    ],
    "brain-04-frontend": [
        "frontend",
        "react",
        "nextjs",
        "next.js",
        "componente",
        "state",
        "zustand",
        "ws",
        "websocket",
    ],
    "brain-05-backend": [
        "backend",
        "endpoint",
        "database",
        "sql",
        "fastapi",
        "pydantic",
        "servidor",
    ],
    "brain-06-qa": [
        "test",
        "qa",
        "testing",
        "pytest",
        "coverage",
        "e2e",
        "integration",
    ],
    "brain-07-growth": [
        "métrica",
        "analytics",
        "growth",
        "data",
        "kpi",
        "funnel",
        "retention",
    ],
}


# =============================================================================
# ROUTING LOGIC
# =============================================================================


def route_to_brain(brief: Brief, from_brain_id: str) -> str | None:
    """Determine if a brief should be delegated to another brain.

    Scans both problem_statement AND context for domain keywords.
    Returns the target brain ID if a match is found, None otherwise.

    Args:
        brief: The brief to analyze
        from_brain_id: The brain ID that is considering delegation (usually brain-01-product)

    Returns:
        Target brain ID (e.g., "brain-04-frontend") or None if no match

    Examples:
        >>> brief = Brief(problem_statement="Crear componente React", context="", target_audience=None)
        >>> route_to_brain(brief, "brain-01-product")
        'brain-04-frontend'

        >>> brief = Brief(problem_statement="Definir roadmap", context="", target_audience=None)
        >>> route_to_brain(brief, "brain-01-product")
        None  # Brain #1 handles this itself
    """
    # Combine both fields for keyword scanning
    combined_text = f"{brief.problem_statement} {brief.context or ''}".lower()

    # Check each brain's keywords (except the sender)
    for brain_id, keywords in BRAIN_KEYWORDS.items():
        if brain_id == from_brain_id:
            continue  # Don't route to self

        # Check if any keyword matches
        for keyword in keywords:
            if keyword.lower() in combined_text:
                return brain_id

    # No match found — sender handles the brief
    return None


# =============================================================================
# WEBSOCKET EVENT EMISSION
# =============================================================================


async def emit_brain_routing_event(
    task_id: str,
    from_brain: str,
    to_brain: str,
    sub_task_id: str,
) -> None:
    """Emit a brain_routing WebSocket event to the frontend.

    Architecture Decision (Brain #4): Opción A — Reuse parent task_id.
    The sub_task_id is payload data only, NOT a separate WS endpoint.

    Args:
        task_id: Parent task ID (same WS connection, NOT sub-task endpoint)
        from_brain: Source brain ID (e.g., "brain-01-product")
        to_brain: Target brain ID (e.g., "brain-04-frontend")
        sub_task_id: UUID for tracking (only in payload, NOT WS endpoint)

    Example WS payload:
        {
            "type": "brain_routing",
            "data": {
                "from": "brain-01-product",
                "to": "brain-04-frontend",
                "sub_task_id": "abc-123-def",
                "timestamp": 1672531200
            }
        }
    """
    from mastermind_cli.api.websocket import manager

    # Prepare event payload (matches BrainRoutingEventSchema from frontend)
    event_payload = {
        "type": "brain_routing",
        "data": {
            "from": from_brain,
            "to": to_brain,
            "sub_task_id": sub_task_id,
            "timestamp": int(time.time()),
        },
    }

    # Send to parent task_id (Opción A — same WS connection)
    await manager.broadcast_task_update(task_id, event_payload)
