"""Tests for niche-clustered graph builder service and enhanced /graph endpoint.

Tests:
- build_niche_clustered_graph() unit tests
- GET /api/tasks/{id}/graph integration (backward compat)
- Sub-graph structure: parentId, extent, execution_mode

Requirements: SV-01, SV-02 (graph snapshot for Strategy Vault)
"""

import pytest

from mastermind_cli.api.services.graph_builder import build_niche_clustered_graph


# ===== Unit tests: build_niche_clustered_graph =====


class TestBuildNicheClusteredGraph:
    """Tests for build_niche_clustered_graph() service function."""

    def _software_brains(self) -> list[dict]:
        return [
            {
                "id": "brain-01",
                "name": "Product Strategy",
                "niche": "software-development",
                "status": "complete",
            },
            {
                "id": "brain-04",
                "name": "Frontend",
                "niche": "software-development",
                "status": "running",
            },
        ]

    def _multi_niche_brains(self) -> list[dict]:
        return [
            {
                "id": "brain-01",
                "name": "Product Strategy",
                "niche": "software-development",
                "status": "complete",
            },
            {
                "id": "brain-09",
                "name": "Content Strategist",
                "niche": "marketing-digital",
                "status": "idle",
            },
        ]

    def test_master_node_present(self) -> None:
        """Master node is always first node, type='master', id='master'."""
        graph = build_niche_clustered_graph("task-001", "Build a landing page", [])
        assert len(graph["nodes"]) >= 1
        master = graph["nodes"][0]
        assert master["id"] == "master"
        assert master["type"] == "master"
        assert master["position"] == {"x": 0.0, "y": 0.0}

    def test_master_node_contains_brief(self) -> None:
        """Master node data.label contains the brief."""
        graph = build_niche_clustered_graph("task-001", "Build a landing page", [])
        master = graph["nodes"][0]
        assert "Build a landing page" in master["data"]["label"]

    def test_empty_brains_returns_master_only(self) -> None:
        """Empty brain list returns only master node, no edges."""
        graph = build_niche_clustered_graph("task-001", "Brief", [])
        assert len(graph["nodes"]) == 1
        assert graph["nodes"][0]["id"] == "master"
        assert graph["edges"] == []

    def test_layout_positions_is_none(self) -> None:
        """layout_positions is always None (client handles dagre)."""
        graph = build_niche_clustered_graph(
            "task-001", "Brief", self._software_brains()
        )
        assert graph["layout_positions"] is None

    def test_niche_nodes_have_correct_type(self) -> None:
        """Niche cluster nodes have type='niche_cluster'."""
        graph = build_niche_clustered_graph(
            "task-001", "Brief", self._software_brains()
        )
        niche_nodes = [n for n in graph["nodes"] if n["type"] == "niche_cluster"]
        assert len(niche_nodes) == 1
        niche = niche_nodes[0]
        assert niche["id"] == "niche-software-development"
        assert niche["type"] == "niche_cluster"
        assert niche["data"]["niche_id"] == "software-development"

    def test_niche_nodes_no_parent_id(self) -> None:
        """Niche cluster nodes do NOT have parentId (they are top-level)."""
        graph = build_niche_clustered_graph(
            "task-001", "Brief", self._software_brains()
        )
        niche_nodes = [n for n in graph["nodes"] if n["type"] == "niche_cluster"]
        for niche in niche_nodes:
            assert "parentId" not in niche

    def test_brain_nodes_have_correct_type(self) -> None:
        """Brain executor nodes have type='brain_executor'."""
        graph = build_niche_clustered_graph(
            "task-001", "Brief", self._software_brains()
        )
        brain_nodes = [n for n in graph["nodes"] if n["type"] == "brain_executor"]
        assert len(brain_nodes) == 2
        for brain in brain_nodes:
            assert brain["type"] == "brain_executor"

    def test_brain_nodes_have_parent_id(self) -> None:
        """Brain executor nodes have parentId pointing to their niche cluster."""
        graph = build_niche_clustered_graph(
            "task-001", "Brief", self._software_brains()
        )
        brain_nodes = [n for n in graph["nodes"] if n["type"] == "brain_executor"]
        for brain in brain_nodes:
            assert "parentId" in brain
            assert brain["parentId"] == "niche-software-development"

    def test_brain_nodes_have_extent_parent(self) -> None:
        """Brain executor nodes have extent='parent' for React Flow grouping."""
        graph = build_niche_clustered_graph(
            "task-001", "Brief", self._software_brains()
        )
        brain_nodes = [n for n in graph["nodes"] if n["type"] == "brain_executor"]
        for brain in brain_nodes:
            assert brain["extent"] == "parent"

    def test_master_to_niche_edges_sequential(self) -> None:
        """Master → Niche edges have execution_mode='sequential'."""
        graph = build_niche_clustered_graph(
            "task-001", "Brief", self._software_brains()
        )
        master_to_niche = [e for e in graph["edges"] if e["source"] == "master"]
        assert len(master_to_niche) == 1
        assert master_to_niche[0]["data"]["execution_mode"] == "sequential"
        assert master_to_niche[0]["target"] == "niche-software-development"

    def test_niche_to_brain_edges_parallel(self) -> None:
        """Niche → Brain edges have execution_mode='parallel'."""
        graph = build_niche_clustered_graph(
            "task-001", "Brief", self._software_brains()
        )
        niche_to_brain = [
            e for e in graph["edges"] if e["source"] == "niche-software-development"
        ]
        assert len(niche_to_brain) == 2
        for edge in niche_to_brain:
            assert edge["data"]["execution_mode"] == "parallel"

    def test_multi_niche_creates_multiple_clusters(self) -> None:
        """Brains from different niches create separate niche clusters."""
        graph = build_niche_clustered_graph(
            "task-001", "Brief", self._multi_niche_brains()
        )
        niche_nodes = [n for n in graph["nodes"] if n["type"] == "niche_cluster"]
        assert len(niche_nodes) == 2
        niche_ids = {n["id"] for n in niche_nodes}
        assert "niche-software-development" in niche_ids
        assert "niche-marketing-digital" in niche_ids

    def test_multi_niche_master_edges(self) -> None:
        """Multi-niche: master has edge to each niche cluster."""
        graph = build_niche_clustered_graph(
            "task-001", "Brief", self._multi_niche_brains()
        )
        master_edges = [e for e in graph["edges"] if e["source"] == "master"]
        assert len(master_edges) == 2

    def test_brain_status_in_data(self) -> None:
        """Brain executor node data includes status field."""
        graph = build_niche_clustered_graph(
            "task-001", "Brief", self._software_brains()
        )
        brain_nodes = [n for n in graph["nodes"] if n["type"] == "brain_executor"]
        statuses = {n["data"]["status"] for n in brain_nodes}
        assert "complete" in statuses
        assert "running" in statuses

    def test_unknown_brain_niche_grouped_unclassified(self) -> None:
        """Brains without niche field are grouped into 'unclassified' niche."""
        brains = [{"id": "brain-99", "name": "Unknown Brain"}]
        graph = build_niche_clustered_graph("task-001", "Brief", brains)
        niche_nodes = [n for n in graph["nodes"] if n["type"] == "niche_cluster"]
        assert len(niche_nodes) == 1
        assert niche_nodes[0]["data"]["niche_id"] == "unclassified"

    def test_brain_missing_id_skipped(self) -> None:
        """Brain with missing ID is skipped silently (backward compat)."""
        brains = [
            {"name": "No ID Brain", "niche": "software-development"},  # no id field
            {"id": "brain-01", "name": "With ID", "niche": "software-development"},
        ]
        graph = build_niche_clustered_graph("task-001", "Brief", brains)
        brain_nodes = [n for n in graph["nodes"] if n["type"] == "brain_executor"]
        # Only the brain with id should be included
        assert len(brain_nodes) == 1
        assert brain_nodes[0]["id"] == "brain-01"

    def test_graph_structure_has_required_keys(self) -> None:
        """Graph response always has nodes, edges, layout_positions."""
        graph = build_niche_clustered_graph("task-001", "Brief", [])
        assert "nodes" in graph
        assert "edges" in graph
        assert "layout_positions" in graph

    def test_no_duplicate_node_ids(self) -> None:
        """All node IDs are unique."""
        graph = build_niche_clustered_graph(
            "task-001", "Brief", self._multi_niche_brains()
        )
        node_ids = [n["id"] for n in graph["nodes"]]
        assert len(node_ids) == len(set(node_ids))

    def test_brief_truncated_at_80_chars(self) -> None:
        """Long briefs are truncated to 80 chars + '...' in master label."""
        long_brief = "x" * 100
        graph = build_niche_clustered_graph("task-001", long_brief, [])
        label = graph["nodes"][0]["data"]["label"]
        assert len(label) <= 84  # 80 + "..."
        assert "..." in label


# ===== Integration tests: GET /api/tasks/{id}/graph with sub-graph =====


@pytest.mark.asyncio
async def test_get_graph_endpoint_returns_valid_shape(client, auth_headers) -> None:
    """GET /api/tasks/{id}/graph returns nodes/edges/max_level/layout_positions."""
    create = await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Test sub-graph structure"},
    )
    assert create.status_code == 201
    task_id = create.json()["task_id"]

    response = await client.get(f"/api/tasks/{task_id}/graph", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # Required shape for Phase 07 React Flow compatibility
    assert "nodes" in data
    assert "edges" in data
    assert "layout_positions" in data


@pytest.mark.asyncio
async def test_get_graph_endpoint_404_for_unknown(client, auth_headers) -> None:
    """GET /api/tasks/{id}/graph returns 404 for nonexistent task."""
    response = await client.get(
        "/api/tasks/nonexistent-task-00001/graph", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_graph_endpoint_requires_auth(client) -> None:
    """GET /api/tasks/{id}/graph requires JWT authentication."""
    response = await client.get("/api/tasks/some-task-id/graph")
    assert response.status_code in (401, 403)
