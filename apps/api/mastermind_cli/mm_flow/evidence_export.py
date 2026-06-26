"""Lightweight helpers for execution export payloads."""

from __future__ import annotations

from typing import Any, Mapping


def build_execution_export(
    results: Mapping[str, Any],
    runtime_contracts: object | None = None,
    evidence_routing: object | None = None,
) -> dict[str, object]:
    """Build the exported payload with optional routing metadata."""
    export_payload: dict[str, Any] = {
        "results": {
            brain_id: brain_output.model_dump()
            for brain_id, brain_output in results.items()
        }
    }
    execution_summary: dict[str, Any] | None = None
    if evidence_routing is not None:
        routing_payload = (
            dict(evidence_routing)
            if isinstance(evidence_routing, Mapping)
            else dict(vars(evidence_routing))
        )
        execution_summary = {"evidence_routing": routing_payload}
    if runtime_contracts is not None:
        contracts_payload = (
            dict(runtime_contracts)
            if isinstance(runtime_contracts, Mapping)
            else dict(vars(runtime_contracts))
        )
        if execution_summary is None:
            execution_summary = {}
        execution_summary["runtime_contracts"] = contracts_payload
    if execution_summary is not None:
        export_payload["execution_summary"] = execution_summary
    return dict(export_payload)
