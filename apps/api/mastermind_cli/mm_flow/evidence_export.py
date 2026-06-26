"""Lightweight helpers for execution export payloads."""

from __future__ import annotations

from typing import Any, Mapping


def build_execution_export(
    results: Mapping[str, Any],
    evidence_routing: object | None = None,
) -> dict[str, object]:
    """Build the exported payload with optional routing metadata."""
    export_payload: dict[str, object] = {
        "results": {
            brain_id: brain_output.model_dump()
            for brain_id, brain_output in results.items()
        }
    }
    if evidence_routing is not None:
        routing_payload = (
            dict(evidence_routing)
            if isinstance(evidence_routing, Mapping)
            else dict(vars(evidence_routing))
        )
        export_payload["execution_summary"] = {
            "evidence_routing": routing_payload,
        }
    return export_payload
