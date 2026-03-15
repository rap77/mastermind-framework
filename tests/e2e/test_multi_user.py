"""Multi-user session isolation E2E tests.
pytestmark = pytest.mark.asyncio
These tests verify that multiple users can execute tasks simultaneously
without cross-session pollution, ensuring session isolation and data integrity.
Note: These tests use mock authentication to avoid complex setup in E2E tests.
The authentication system is tested separately in unit tests.
"""

import pytest
from unittest.mock import patch
from mastermind_cli.api.app import create_app
from mastermind_cli.state.database import DatabaseConnection


@pytest.fixture
async def app_with_mock_auth():
    """Create app with mocked authentication."""
    app = create_app(db_path=":memory:")
    # Initialize database schemas
    async with DatabaseConnection(":memory:") as db:
        await db.connect()
        await db.create_experience_schema()
        await db.create_task_schema()
        await db.create_auth_schema()
    yield app


async def test_multi_user_isolation(app_with_mock_auth):
    """Verify two users can execute tasks without cross-session pollution."""
    # Mock the auth dependency to return different user IDs
    user_ids = []

    async def mock_get_user_a():
        user_ids.append("user-a-123")
        return "user-a-123"

    async def mock_get_user_b():
        user_ids.append("user-b-456")
        return "user-b-456"

    from httpx import AsyncClient, ASGITransport

    # Patch auth for user A
    with patch(
        "mastermind_cli.api.routes.tasks.get_current_user_any",
        side_effect=mock_get_user_a,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app_with_mock_auth), base_url="http://test"
        ) as client_a:
            task_a = await client_a.post(
                "/api/tasks",
                json={
                    "brief": "User A's brief",
                    "flow": None,
                    "max_iterations": 3,
                    "use_mcp": False,
                },
            )
            assert task_a.status_code == 201
            task_a_id = task_a.json()["task_id"]
    # Patch auth for user B
    with patch(
        "mastermind_cli.api.routes.tasks.get_current_user_any",
        side_effect=mock_get_user_b,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app_with_mock_auth), base_url="http://test"
        ) as client_b:
            task_b = await client_b.post(
                "/api/tasks",
                json={
                    "brief": "User B's brief",
                    "flow": None,
                    "max_iterations": 3,
                    "use_mcp": False,
                },
            )
            assert task_b.status_code == 201
            task_b_id = task_b.json()["task_id"]
    # Verify IDs are different
    assert task_a_id != task_b_id
    # Verify both users were called
    assert "user-a-123" in user_ids
    assert "user-b-456" in user_ids


async def test_concurrent_task_creation(app_with_mock_auth):
    """Verify multiple users creating tasks doesn't corrupt database."""
    from httpx import AsyncClient, ASGITransport
    import asyncio

    created_ids = []

    async def mock_get_user_factory(user_num):
        async def mock_get_user():
            created_ids.append(f"user-{user_num}")
            return f"user-{user_num}"

        return mock_get_user

    async def create_task(user_num):
        with patch(
            "mastermind_cli.api.routes.tasks.get_current_user_any",
            side_effect=await mock_get_user_factory(user_num)(),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app_with_mock_auth), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/tasks",
                    json={
                        "brief": f"User {user_num}'s brief",
                        "flow": None,
                        "max_iterations": 3,
                        "use_mcp": False,
                    },
                )
                assert response.status_code == 201
                return response.json()["task_id"]

    # Create 5 tasks concurrently
    task_ids = await asyncio.gather(*[create_task(i) for i in range(5)])
    # Verify all IDs are unique
    assert len(set(task_ids)) == 5, "Task IDs should be unique"
    # Verify all users were created
    assert len(created_ids) == 5


async def test_per_request_orchestrator_instances(app_with_mock_auth):
    """Verify per-request orchestrator instances prevent state leakage."""
    from httpx import AsyncClient, ASGITransport

    async def mock_get_user():
        return "test-user-123"

    with patch(
        "mastermind_cli.api.routes.tasks.get_current_user_any",
        side_effect=mock_get_user,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app_with_mock_auth), base_url="http://test"
        ) as client:
            # Create tasks with different configurations
            task_1 = await client.post(
                "/api/tasks",
                json={
                    "brief": "Task 1 with flow A",
                    "flow": '{"flow_id": "flow-a"}',
                    "max_iterations": 3,
                    "use_mcp": False,
                },
            )
            assert task_1.status_code == 201
            task_2 = await client.post(
                "/api/tasks",
                json={
                    "brief": "Task 2 with flow B",
                    "flow": '{"flow_id": "flow-b"}',
                    "max_iterations": 5,
                    "use_mcp": True,
                },
            )
            assert task_2.status_code == 201
            # Verify each task has its own configuration
            task_1_id = task_1.json()["task_id"]
            task_2_id = task_2.json()["task_id"]
            assert task_1_id != task_2_id
            # Verify configurations are different
            response_1 = await client.get(f"/api/tasks/{task_1_id}")
            config_1 = response_1.json()
            response_2 = await client.get(f"/api/tasks/{task_2_id}")
            config_2 = response_2.json()
            assert config_1["flow_config"] != config_2["flow_config"]


async def test_task_cancellation_isolation(app_with_mock_auth):
    """Verify User A's cancellation doesn't affect User B's task."""
    from httpx import AsyncClient, ASGITransport

    task_a_id = None
    task_b_id = None

    async def mock_get_user_a():
        return "user-a-cancel"

    async def mock_get_user_b():
        return "user-b-keep"

    # User A creates task
    with patch(
        "mastermind_cli.api.routes.tasks.get_current_user_any",
        side_effect=mock_get_user_a,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app_with_mock_auth), base_url="http://test"
        ) as client_a:
            task_a = await client_a.post(
                "/api/tasks",
                json={
                    "brief": "User A's task to cancel",
                    "flow": None,
                    "max_iterations": 3,
                    "use_mcp": False,
                },
            )
            assert task_a.status_code == 201
            task_a_id = task_a.json()["task_id"]
            # User A cancels their task
            cancel_response = await client_a.delete(f"/api/tasks/{task_a_id}")
            assert cancel_response.status_code == 200
            # Verify User A's task is cancelled
            response_a = await client_a.get(f"/api/tasks/{task_a_id}")
            assert response_a.json()["status"] == "cancelled"
    # User B creates task
    with patch(
        "mastermind_cli.api.routes.tasks.get_current_user_any",
        side_effect=mock_get_user_b,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app_with_mock_auth), base_url="http://test"
        ) as client_b:
            task_b = await client_b.post(
                "/api/tasks",
                json={
                    "brief": "User B's task to keep",
                    "flow": None,
                    "max_iterations": 3,
                    "use_mcp": False,
                },
            )
            assert task_b.status_code == 201
            task_b_id = task_b.json()["task_id"]
            # Verify User B's task is NOT cancelled
            response_b = await client_b.get(f"/api/tasks/{task_b_id}")
            assert response_b.json()["status"] != "cancelled"


async def test_websocket_route_registered(app_with_mock_auth):
    """Verify WebSocket route is registered in the app."""
    # Verify app has WebSocket routes
    routes = [route.path for route in app_with_mock_auth.routes]
    assert any(
        "/ws" in route for route in routes
    ), "WebSocket route should be registered"
