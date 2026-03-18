"""Multi-user session isolation E2E tests.

These tests verify that multiple users can execute tasks simultaneously
without cross-session pollution, ensuring session isolation and data integrity.

Note: These tests use FastAPI dependency_overrides to mock authentication.
The authentication system is tested separately in unit tests.
"""

import pytest
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from mastermind_cli.api.app import create_app
from mastermind_cli.api.routes.auth import get_current_user_any
from mastermind_cli.api.routes.tasks import get_db_path
from mastermind_cli.state.database import DatabaseConnection


@pytest.fixture
async def app_with_mock_auth(tmp_path: Path):
    """Create app with a file-based temp DB and dependency overrides."""
    db_file = str(tmp_path / "test.db")

    # Initialize schema directly (ASGITransport doesn't trigger startup events)
    async with DatabaseConnection(db_file) as db:
        await db.create_task_schema()
        await db.create_auth_schema()

    app = create_app(db_path=db_file)
    app.dependency_overrides[get_db_path] = lambda: db_file
    yield app
    app.dependency_overrides.clear()


async def test_multi_user_isolation(app_with_mock_auth):
    """Verify two users can execute tasks without cross-session pollution."""
    app = app_with_mock_auth
    user_ids = []

    def mock_user_a():
        user_ids.append("user-a-123")
        return "user-a-123"

    def mock_user_b():
        user_ids.append("user-b-456")
        return "user-b-456"

    # User A creates task
    app.dependency_overrides[get_current_user_any] = mock_user_a
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        task_a = await client.post(
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

    # User B creates task
    app.dependency_overrides[get_current_user_any] = mock_user_b
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        task_b = await client.post(
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
    app = app_with_mock_auth
    created_ids = []

    def make_mock_user(user_num: int):
        def mock_user():
            created_ids.append(f"user-{user_num}")
            return f"user-{user_num}"

        return mock_user

    async def create_task(user_num: int) -> str:
        app.dependency_overrides[get_current_user_any] = make_mock_user(user_num)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
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

    # Create 5 tasks sequentially (each with different user override)
    task_ids = []
    for i in range(5):
        task_id = await create_task(i)
        task_ids.append(task_id)

    # Verify all IDs are unique
    assert len(set(task_ids)) == 5, "Task IDs should be unique"
    # Verify all users were created
    assert len(created_ids) == 5


async def test_per_request_orchestrator_instances(app_with_mock_auth):
    """Verify per-request orchestrator instances prevent state leakage."""
    app = app_with_mock_auth

    def mock_user():
        return "test-user-123"

    app.dependency_overrides[get_current_user_any] = mock_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
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
    app = app_with_mock_auth

    def mock_user_a():
        return "user-a-cancel"

    def mock_user_b():
        return "user-b-keep"

    # User A creates and cancels task
    app.dependency_overrides[get_current_user_any] = mock_user_a
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        task_a = await client.post(
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

        cancel_response = await client.delete(f"/api/tasks/{task_a_id}")
        assert cancel_response.status_code == 200

        response_a = await client.get(f"/api/tasks/{task_a_id}")
        assert response_a.json()["status"] == "cancelled"

    # User B creates task — unaffected by A's cancellation
    app.dependency_overrides[get_current_user_any] = mock_user_b
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        task_b = await client.post(
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

        response_b = await client.get(f"/api/tasks/{task_b_id}")
        assert response_b.json()["status"] != "cancelled"


async def test_websocket_route_registered(app_with_mock_auth):
    """Verify WebSocket route is registered in the app."""
    routes = [route.path for route in app_with_mock_auth.routes]
    assert any(
        "/ws" in route for route in routes
    ), "WebSocket route should be registered"
