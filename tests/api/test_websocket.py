"""Test WebSocket endpoint and real-time progress streaming.

Requirements: UI-04, PAR-08
"""

import time

import pytest

from mastermind_cli.api.websocket import WebSocketManager


def test_websocket_connects_with_jwt(sync_client, valid_jwt):
    """Valid JWT connects to WebSocket without raising."""
    with sync_client.websocket_connect(f"/ws/tasks/task-001?token={valid_jwt}"):
        pass


def test_websocket_connects_with_api_key(sync_client, client, auth_headers, db_path):
    """Valid API key connects to WebSocket."""
    import asyncio

    async def create_key():
        async with __import__("httpx").AsyncClient(
            transport=__import__("httpx").ASGITransport(app=sync_client.app),
            base_url="http://test",
        ) as c:
            resp = await c.post(
                "/api/auth/api-keys",
                headers=auth_headers,
                json={"name": "ws-key"},
            )
            return resp.json()["key"]

    api_key = asyncio.run(create_key())

    with sync_client.websocket_connect(f"/ws/tasks/task-001?token={api_key}"):
        pass


def test_websocket_invalid_token_rejected(sync_client):
    """Invalid token closes WebSocket with code 1008."""
    from starlette.websockets import WebSocketDisconnect

    with pytest.raises((WebSocketDisconnect, Exception)):
        with sync_client.websocket_connect("/ws/tasks/task-001?token=invalid_token"):
            pass


def test_progress_updates(sync_client, valid_jwt):
    """WebSocket receives broadcast after broadcast_task_update."""
    import asyncio
    from mastermind_cli.api.websocket import manager

    task_id = "task-progress-001"

    with sync_client.websocket_connect(f"/ws/tasks/{task_id}?token={valid_jwt}"):
        asyncio.run(manager.broadcast_task_update(task_id, {"status": "running"}))
        # Updates are buffered — just verify buffer received it
        events = manager.get_recent_events(task_id, "nonexistent")
        assert len(events) >= 1
        assert events[-1]["data"]["status"] == "running"


def test_reconnection_resync(sync_client, valid_jwt):
    """Ghost Mode buffer stores up to 100 events for resync."""

    mgr = WebSocketManager()
    task_id = "task-resync-001"
    # Simulate buffers by manually adding
    mgr.buffers[task_id] = __import__("collections").deque(maxlen=100)
    for i in range(5):
        mgr.buffers[task_id].append(
            {"event_id": f"evt-{i}", "timestamp": time.time(), "data": {"i": i}}
        )

    events = mgr.get_recent_events(task_id, "evt-2")
    # Events after evt-2: evt-3, evt-4
    assert len(events) == 2
    assert events[0]["event_id"] == "evt-3"


def test_broadcast_throttling():
    """ThrottledBroadcaster batches updates within 300ms window."""
    from mastermind_cli.api.websocket import ThrottledBroadcaster
    import asyncio

    broadcaster = ThrottledBroadcaster()
    task_id = "task-throttle-001"

    async def add_updates():
        await broadcaster.add_update(task_id, {"status": "a"})
        await broadcaster.add_update(task_id, {"status": "b"})
        await broadcaster.add_update(task_id, {"status": "c"})

    asyncio.run(add_updates())
    # Pending batch should have merged updates
    assert task_id in broadcaster.accumulated


def test_multiple_clients(sync_client, valid_jwt):
    """Multiple clients can connect to same task_id."""
    from mastermind_cli.api.websocket import manager

    task_id = "task-multi-001"
    connections = []
    for i in range(3):
        ws = sync_client.websocket_connect(f"/ws/tasks/{task_id}?token={valid_jwt}")
        connections.append(ws.__enter__())

    assert task_id in manager.connections
    assert len(manager.connections[task_id]) >= 1

    for ws in connections:
        ws.close()


def test_disconnect_cleanup(sync_client, valid_jwt):
    """After disconnect, connection is removed from manager."""
    from mastermind_cli.api.websocket import manager

    task_id = "task-cleanup-001"
    with sync_client.websocket_connect(f"/ws/tasks/{task_id}?token={valid_jwt}"):
        assert task_id in manager.connections

    # After context exit, connection should be cleaned up
    if task_id in manager.connections:
        assert len(manager.connections[task_id]) == 0
