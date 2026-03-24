"""Graph builder service for niche-clustered DAG generation.

Converts brain execution data into a React Flow compatible niche-clustered
DAG with parentId relationships and execution_mode edge metadata.

Phase 08: Enhances the flat Phase 07 graph with sub-graph structure:
- Master node: single entry point for the brief
- Niche cluster nodes: group brains by domain (software-dev, marketing, etc.)
- Brain executor nodes: individual brains with parentId pointing to their niche

Requirements: SV-01, SV-02 (Graph snapshot for Strategy Vault replay)
"""

import math
from typing import Any

# Default positions for layout (client-side dagre is preferred, but server
# can provide hints for initial render stability)
_MASTER_POSITION = {"x": 0.0, "y": 0.0}
_NICHE_RADIUS = 400.0  # Distance of niche nodes from master (constellation)
_BRAIN_OFFSET_X = 200.0  # Horizontal offset for brain nodes within niche
_BRAIN_OFFSET_Y = 80.0  # Vertical spacing for brain nodes within niche


def _niche_position(index: int, total_niches: int) -> dict[str, float]:
    """Calculate constellation position for a niche node.

    Distributes niches evenly around the master in a circle.

    Args:
        index: 0-based index of this niche
        total_niches: Total number of niches

    Returns:
        {x, y} position dict
    """
    if total_niches == 0:
        return {"x": 0.0, "y": 0.0}
    angle = (2 * math.pi * index) / total_niches
    return {
        "x": round(_NICHE_RADIUS * math.cos(angle), 2),
        "y": round(_NICHE_RADIUS * math.sin(angle), 2),
    }


def _brain_position(index: int) -> dict[str, float]:
    """Calculate relative position for a brain node within its niche container.

    Args:
        index: 0-based index of this brain within the niche

    Returns:
        {x, y} position relative to niche container
    """
    return {
        "x": 10.0,
        "y": 10.0 + index * _BRAIN_OFFSET_Y,
    }


def build_niche_clustered_graph(
    task_id: str,
    brief: str,
    brains: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a niche-clustered React Flow DAG for task visualization.

    Creates a three-level hierarchy:
    1. Master node (single, represents the brief/task)
    2. Niche cluster nodes (one per unique niche in the brain list)
    3. Brain executor nodes (one per brain, parentId = their niche cluster)

    Edges:
    - Master → Niche: execution_mode="sequential" (niches run one at a time)
    - Niche → Brain: execution_mode="parallel" (brains within niche run in parallel)

    Args:
        task_id: Task UUID (used for edge IDs)
        brief: Task brief text (used as master node label)
        brains: List of brain dicts with fields:
            - id (str): e.g., "brain-01" or "brain-09"
            - name (str): Display name
            - niche (str): Domain identifier, e.g. "software-development"
            - status (str, optional): Current execution status

    Returns:
        Dict with keys:
            - nodes: List of React Flow node objects
            - edges: List of React Flow edge objects
            - layout_positions: None (client handles dagre layout)

    Example:
        >>> graph = build_niche_clustered_graph(
        ...     task_id="abc123",
        ...     brief="Build a landing page",
        ...     brains=[
        ...         {"id": "brain-01", "name": "Product Strategy",
        ...          "niche": "software-development", "status": "complete"},
        ...         {"id": "brain-04", "name": "Frontend",
        ...          "niche": "software-development", "status": "running"},
        ...     ]
        ... )
        >>> graph["nodes"][0]["id"]  # master
        'master'
        >>> graph["nodes"][1]["type"]  # niche cluster
        'niche_cluster'
    """
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    # ===== Master Node =====
    brief_label = brief[:80] + "..." if len(brief) > 80 else brief
    master_node: dict[str, Any] = {
        "id": "master",
        "type": "master",
        "data": {
            "label": brief_label,
            "task_id": task_id,
        },
        "position": _MASTER_POSITION.copy(),
    }
    nodes.append(master_node)

    if not brains:
        # Graceful degradation: return master-only graph
        return {"nodes": nodes, "edges": edges, "layout_positions": None}

    # ===== Group brains by niche =====
    niche_map: dict[str, list[dict[str, Any]]] = {}
    for brain in brains:
        brain_id = str(brain.get("id", ""))
        if not brain_id:
            # Skip brains with missing ID (backward compat)
            continue
        niche = str(brain.get("niche", "unclassified"))
        if niche not in niche_map:
            niche_map[niche] = []
        niche_map[niche].append(brain)

    total_niches = len(niche_map)

    # ===== Niche Cluster Nodes + Brain Executor Nodes =====
    for niche_index, (niche_id, niche_brains) in enumerate(sorted(niche_map.items())):
        niche_node_id = f"niche-{niche_id}"
        niche_position = _niche_position(niche_index, total_niches)

        niche_node: dict[str, Any] = {
            "id": niche_node_id,
            "type": "niche_cluster",
            "data": {
                "label": niche_id.replace("-", " ").title(),
                "niche_id": niche_id,
                "brain_count": len(niche_brains),
            },
            "position": niche_position,
        }
        nodes.append(niche_node)

        # Edge: Master → Niche (sequential)
        master_to_niche_edge: dict[str, Any] = {
            "id": f"e-master-{niche_node_id}",
            "source": "master",
            "target": niche_node_id,
            "data": {
                "execution_mode": "sequential",
            },
        }
        edges.append(master_to_niche_edge)

        # ===== Brain Executor Nodes =====
        for brain_index, brain in enumerate(niche_brains):
            brain_id = str(brain.get("id", ""))
            # Normalize brain ID format (numeric → string prefixed)
            if brain_id.isdigit():
                brain_node_id = f"brain-{int(brain_id):02d}"
            else:
                brain_node_id = (
                    brain_id if brain_id.startswith("brain-") else f"brain-{brain_id}"
                )

            brain_node: dict[str, Any] = {
                "id": brain_node_id,
                "type": "brain_executor",
                "parentId": niche_node_id,
                "extent": "parent",
                "data": {
                    "label": str(brain.get("name", brain_node_id)),
                    "niche_id": niche_id,
                    "status": str(brain.get("status", "idle")),
                    "brain_id": brain_id,
                },
                "position": _brain_position(brain_index),
            }
            nodes.append(brain_node)

            # Edge: Niche → Brain (parallel)
            niche_to_brain_edge: dict[str, Any] = {
                "id": f"e-{niche_node_id}-{brain_node_id}",
                "source": niche_node_id,
                "target": brain_node_id,
                "data": {
                    "execution_mode": "parallel",
                },
            }
            edges.append(niche_to_brain_edge)

    return {
        "nodes": nodes,
        "edges": edges,
        "layout_positions": None,  # Client handles dagre layout
    }
