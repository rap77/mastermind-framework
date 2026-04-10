"""Tests for the costs API router.

This module tests the cost metrics endpoints that query PostgreSQL.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient

from mastermind_cli.api.app import create_app
from mastermind_cli.api.costs import router as costs_router


# ===== FIXTURES =====

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test client with costs router."""
    app = create_app()
    app.include_router(costs_router)
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ===== TESTS =====


@pytest.mark.asyncio
class TestGetBrainCosts:
    """Tests for GET /api/costs/brains endpoint."""

    async def test_returns_empty_list_when_no_metrics(self, client: AsyncClient) -> None:
        """Should return empty list when MV has no data."""
        with patch("mastermind_cli.api.costs.asyncpg.connect") as mock_connect:
            # Mock empty result
            mock_conn = AsyncMock()
            mock_conn.fetch.return_value = []
            mock_connect.return_value = mock_conn
            
            response = await client.get("/api/costs/brains")
            
            assert response.status_code == 200
            assert response.json() == []

    async def test_returns_brain_metrics_ordered_by_success_rate(
        self, client: AsyncClient
    ) -> None:
        """Should return metrics ordered by success_rate DESC."""
        with patch("mastermind_cli.api.costs.asyncpg.connect") as mock_connect:
            # Mock test data: brain-01 has 66.67%, brain-02 has 33.33%
            mock_conn = AsyncMock()
            mock_conn.fetch.return_value = [
                {
                    "brain_id": "brain-01",
                    "total_requests": 3,
                    "completed_requests": 2,
                    "failed_requests": 1,
                    "success_rate": 0.6666666666666666,
                    "last_activity_at": None,
                },
                {
                    "brain_id": "brain-02",
                    "total_requests": 3,
                    "completed_requests": 1,
                    "failed_requests": 2,
                    "success_rate": 0.3333333333333333,
                    "last_activity_at": None,
                },
            ]
            mock_connect.return_value = mock_conn
            
            response = await client.get("/api/costs/brains")
            
            assert response.status_code == 200
            data = response.json()
            
            assert len(data) == 2
            assert data[0]["brain_id"] == "brain-01"
            assert data[0]["success_rate"] > 0.6
            assert data[1]["brain_id"] == "brain-02"
            assert data[1]["success_rate"] < 0.4

    async def test_returns_correct_metric_fields(self, client: AsyncClient) -> None:
        """Should return all required fields for each brain."""
        with patch("mastermind_cli.api.costs.asyncpg.connect") as mock_connect:
            mock_conn = AsyncMock()
            mock_conn.fetch.return_value = [
                {
                    "brain_id": "brain-01",
                    "total_requests": 10,
                    "completed_requests": 9,
                    "failed_requests": 1,
                    "success_rate": 0.9,
                    "last_activity_at": None,
                },
            ]
            mock_connect.return_value = mock_conn
            
            response = await client.get("/api/costs/brains")
            
            assert response.status_code == 200
            data = response.json()
            brain = data[0]
            
            assert "brain_id" in brain
            assert "total_requests" in brain
            assert "completed_requests" in brain
            assert "failed_requests" in brain
            assert "success_rate" in brain
            assert "last_activity_at" in brain

    async def test_handles_postgresql_connection_error(
        self, client: AsyncClient
    ) -> None:
        """Should return 503 when PostgreSQL is unavailable."""
        with patch("mastermind_cli.api.costs.asyncpg.connect") as mock_connect:
            # Mock connection error
            mock_connect.side_effect = Exception("Connection refused")
            
            response = await client.get("/api/costs/brains")
            
            assert response.status_code == 503
            assert "Database connection failed" in response.json()["detail"]


@pytest.mark.asyncio
class TestRefreshCostMetrics:
    """Tests for POST /api/costs/refresh endpoint."""

    async def test_refresh_success(self, client: AsyncClient) -> None:
        """Should successfully trigger MV refresh."""
        with patch("mastermind_cli.api.costs.asyncpg.connect") as mock_connect:
            mock_conn = AsyncMock()
            mock_conn.execute.return_value = None
            mock_connect.return_value = mock_conn
            
            response = await client.post("/api/costs/refresh")
            
            assert response.status_code == 200
            assert response.json()["status"] == "success"

    async def test_refresh_failure(self, client: AsyncClient) -> None:
        """Should return 500 when refresh fails."""
        with patch("mastermind_cli.api.costs.asyncpg.connect") as mock_connect:
            mock_conn = AsyncMock()
            mock_conn.execute.side_effect = Exception("Refresh failed")
            mock_connect.return_value = mock_conn
            
            response = await client.post("/api/costs/refresh")
            
            assert response.status_code == 500
            assert "Refresh failed" in response.json()["detail"]


@pytest.mark.asyncio
class TestCostMetricsHealth:
    """Tests for GET /api/costs/health endpoint."""

    async def test_health_healthy(self, client: AsyncClient) -> None:
        """Should return healthy status when DB is connected."""
        with patch("mastermind_cli.api.costs.asyncpg.connect") as mock_connect:
            mock_conn = AsyncMock()
            mock_conn.fetchval.return_value = 5  # 5 rows in MV
            mock_connect.return_value = mock_conn
            
            response = await client.get("/api/costs/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
            assert data["mv_rows"] == 5

    async def test_health_unhealthy_disconnected(self, client: AsyncClient) -> None:
        """Should return unhealthy status when DB is disconnected."""
        with patch("mastermind_cli.api.costs.asyncpg.connect") as mock_connect:
            mock_connect.side_effect = Exception("Connection refused")
            
            response = await client.get("/api/costs/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"

    async def test_health_unhealthy_query_error(self, client: AsyncClient) -> None:
        """Should return unhealthy status when query fails."""
        with patch("mastermind_cli.api.costs.asyncpg.connect") as mock_connect:
            mock_conn = AsyncMock()
            mock_conn.fetchval.side_effect = Exception("Table not found")
            mock_connect.return_value = mock_conn
            
            response = await client.get("/api/costs/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "error"


@pytest.mark.asyncio
class TestCostMetricCalculations:
    """Tests for metric calculation logic."""

    async def test_success_rate_calculation(self, client: AsyncClient) -> None:
        """success_rate should be calculated correctly by MV."""
        with patch("mastermind_cli.api.costs.asyncpg.connect") as mock_connect:
            # Test: 3 completed, 1 failed = 75%
            mock_conn = AsyncMock()
            mock_conn.fetch.return_value = [
                {
                    "brain_id": "test-brain",
                    "total_requests": 4,
                    "completed_requests": 3,
                    "failed_requests": 1,
                    "success_rate": 0.75,
                    "last_activity_at": None,
                },
            ]
            mock_connect.return_value = mock_conn
            
            response = await client.get("/api/costs/brains")
            data = response.json()
            
            assert data[0]["success_rate"] == 0.75

    async def test_last_activity_timestamp_format(
        self, client: AsyncClient
    ) -> None:
        """last_activity_at should be ISO 8601 string."""
        from datetime import datetime
        
        with patch("mastermind_cli.api.costs.asyncpg.connect") as mock_connect:
            test_time = datetime(2026, 4, 10, 12, 0, 0)
            mock_conn = AsyncMock()
            mock_conn.fetch.return_value = [
                {
                    "brain_id": "test-brain",
                    "total_requests": 1,
                    "completed_requests": 1,
                    "failed_requests": 0,
                    "success_rate": 1.0,
                    "last_activity_at": test_time,
                },
            ]
            mock_connect.return_value = mock_conn
            
            response = await client.get("/api/costs/brains")
            data = response.json()
            
            assert data[0]["last_activity_at"] == "2026-04-10T12:00:00"

    async def test_last_activity_null_when_no_data(
        self, client: AsyncClient
    ) -> None:
        """last_activity_at should be None when no activity."""
        with patch("mastermind_cli.api.costs.asyncpg.connect") as mock_connect:
            mock_conn = AsyncMock()
            mock_conn.fetch.return_value = [
                {
                    "brain_id": "test-brain",
                    "total_requests": 0,
                    "completed_requests": 0,
                    "failed_requests": 0,
                    "success_rate": 0.0,
                    "last_activity_at": None,
                },
            ]
            mock_connect.return_value = mock_conn
            
            response = await client.get("/api/costs/brains")
            data = response.json()
            
            assert data[0]["last_activity_at"] is None
