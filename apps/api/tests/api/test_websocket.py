"""Test WebSocket auth and manager behavior."""

from __future__ import annotations

import asyncio
import time
from collections import deque
from unittest.mock import AsyncMock

import pytest
from jose import jwt
from starlette.websockets import WebSocketState

from mastermind_cli.api.websocket import (
    ThrottledBroadcaster,
    WebSocketManager,
    manager,
    websocket_endpoint,
)


class FakeWebSocket:
    """Minimal WebSocket test double for endpoint tests."""

    def __init__(self) -> None:
        self.accepted = False
        self.close_code: int | None = None
        self.sent_payloads: list[dict[str, object]] = []
        self.client_state = WebSocketState.DISCONNECTED
        self.application_state = WebSocketState.DISCONNECTED

    async def accept(self) -> None:
        """Mark the socket as accepted."""
        self.accepted = True
        self.client_state = WebSocketState.CONNECTED
        self.application_state = WebSocketState.DISCONNECTED

    async def close(self, code: int = 1000) -> None:
        """Record the close code."""
        self.close_code = code
        self.client_state = WebSocketState.DISCONNECTED
        self.application_state = WebSocketState.DISCONNECTED

    async def send_json(self, payload: dict[str, object]) -> None:
        """Collect outbound payloads."""
        self.sent_payloads.append(payload)


@pytest.mark.asyncio
async def test_websocket_connects_with_jwt(
    valid_jwt: str, monkeypatch: pytest.MonkeyPatch
):
    """Valid JWT connects to the WebSocket manager."""
    websocket = FakeWebSocket()
    connect_spy = AsyncMock()
    monkeypatch.setattr("mastermind_cli.api.websocket.manager.connect", connect_spy)

    await websocket_endpoint(
        websocket=websocket,
        task_id="task-001",
        token=valid_jwt,
        db_path="test.db",
    )

    assert websocket.accepted is True
    connect_spy.assert_awaited_once_with(websocket, "task-001", "test-user-id-001")


@pytest.mark.asyncio
async def test_websocket_connects_with_api_key(
    auth_headers: dict[str, str],
    client,
    db_path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Valid standard API key connects to the WebSocket manager."""
    create_resp = await client.post(
        "/api/keys",
        headers=auth_headers,
        json={"name": "ws-key"},
    )
    assert create_resp.status_code == 201
    api_key = create_resp.json()["full_key"]

    websocket = FakeWebSocket()
    connect_spy = AsyncMock()
    monkeypatch.setattr("mastermind_cli.api.websocket.manager.connect", connect_spy)

    await websocket_endpoint(
        websocket=websocket,
        task_id="task-001",
        token=api_key,
        db_path=db_path,
    )

    assert websocket.accepted is True
    connect_spy.assert_awaited_once_with(websocket, "task-001", "test-user-id-001")


@pytest.mark.asyncio
async def test_websocket_invalid_token_rejected() -> None:
    """Invalid token closes WebSocket with code 1008."""
    websocket = FakeWebSocket()

    await websocket_endpoint(
        websocket=websocket,
        task_id="task-001",
        token="invalid_token",
        db_path="test.db",
    )

    assert websocket.accepted is True
    assert websocket.close_code == 1008


@pytest.mark.asyncio
async def test_websocket_legacy_api_key_rejected() -> None:
    """Legacy mm_ API-key format is rejected by WebSocket auth."""
    websocket = FakeWebSocket()

    await websocket_endpoint(
        websocket=websocket,
        task_id="task-001",
        token="mm_test1234567890abcdef",
        db_path="test.db",
    )

    assert websocket.accepted is True
    assert websocket.close_code == 1008


@pytest.mark.asyncio
async def test_websocket_jwt_without_subject_rejected() -> None:
    """JWT without subject claim is rejected."""
    token = jwt.encode(
        {"type": "access"}, "test_secret_for_unit_tests_only", algorithm="HS256"
    )
    websocket = FakeWebSocket()

    await websocket_endpoint(
        websocket=websocket,
        task_id="task-001",
        token=token,
        db_path="test.db",
    )

    assert websocket.accepted is True
    assert websocket.close_code == 1008


def test_progress_updates() -> None:
    """WebSocket manager buffers task updates for resync."""
    task_id = "task-progress-001"
    manager.buffers[task_id] = deque(maxlen=100)
    asyncio.run(manager.broadcast_task_update(task_id, {"status": "running"}))
    events = manager.get_recent_events(task_id, "nonexistent")
    assert len(events) >= 1
    assert events[-1]["data"]["status"] == "running"


def test_reconnection_resync() -> None:
    """Ghost Mode buffer stores up to 100 events for resync."""
    mgr = WebSocketManager()
    task_id = "task-resync-001"
    mgr.buffers[task_id] = deque(maxlen=100)
    for i in range(5):
        mgr.buffers[task_id].append(
            {"event_id": f"evt-{i}", "timestamp": time.time(), "data": {"i": i}}
        )

    events = mgr.get_recent_events(task_id, "evt-2")
    assert len(events) == 2
    assert events[0]["event_id"] == "evt-3"


def test_broadcast_throttling() -> None:
    """ThrottledBroadcaster batches updates within 300ms window."""
    broadcaster = ThrottledBroadcaster()
    task_id = "task-throttle-001"

    async def add_updates() -> None:
        await broadcaster.add_update(task_id, {"status": "a"})
        await broadcaster.add_update(task_id, {"status": "b"})
        await broadcaster.add_update(task_id, {"status": "c"})

    asyncio.run(add_updates())
    assert task_id in broadcaster.accumulated


def test_multiple_clients() -> None:
    """Multiple clients can connect to the same task_id."""
    task_id = "task-multi-001"
    manager.connections.pop(task_id, None)
    manager.buffers.pop(task_id, None)

    sockets = [FakeWebSocket(), FakeWebSocket(), FakeWebSocket()]
    for socket in sockets:
        asyncio.run(manager.connect(socket, task_id, "user-1"))

    assert task_id in manager.connections
    assert len(manager.connections[task_id]) == 3


def test_disconnect_cleanup() -> None:
    """After disconnect, connection is removed from manager."""
    task_id = "task-cleanup-001"
    socket = FakeWebSocket()
    manager.connections.pop(task_id, None)
    manager.buffers.pop(task_id, None)

    asyncio.run(manager.connect(socket, task_id, "user-1"))
    assert task_id in manager.connections

    manager.disconnect(socket, task_id)
    assert len(manager.connections[task_id]) == 0
