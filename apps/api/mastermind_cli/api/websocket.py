"""WebSocket manager for real-time progress streaming.

This module provides WebSocket connection management and task update broadcasting
with throttling (300ms batch updates) and Ghost Mode buffer.

Requirements: UI-04, PAR-08, PERF-03
"""

import asyncio
import logging
import os
import time
import uuid
from collections import deque
from typing import Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from starlette.websockets import WebSocketState

from mastermind_cli.api.dependencies import get_db_path

logger = logging.getLogger(__name__)


def _jwt_secret() -> str:
    """Return the configured JWT secret."""
    secret = os.getenv("MM_SECRET_KEY") or os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError(
            "JWT secret not configured. Set MM_SECRET_KEY or JWT_SECRET."
        )
    return secret


def _jwt_algorithm() -> str:
    """Return the configured JWT algorithm."""
    return str(os.getenv("MM_JWT_ALGORITHM", "HS256"))


class ThrottledBroadcaster:
    """Throttles WebSocket broadcasts to max 1 per 300ms (Smart Focus)."""

    def __init__(self, interval_ms: int = 300) -> None:
        self.interval = interval_ms / 1000
        self.accumulated: dict[str, list[dict[str, Any]]] = {}
        self.last_broadcast: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def add_update(self, task_id: str, update_data: dict[str, Any]) -> None:
        """Add update to accumulator, broadcast if interval elapsed."""
        async with self._lock:
            if task_id not in self.accumulated:
                self.accumulated[task_id] = []
            self.accumulated[task_id].append(update_data)

            if time.time() - self.last_broadcast.get(task_id, 0) >= self.interval:
                await self._flush(task_id)

    async def _flush(self, task_id: str) -> None:
        """Broadcast accumulated updates to all clients."""
        updates = self.accumulated.get(task_id, [])
        if not updates:
            return

        # Send batch to all connected clients
        for ws in connections.get(task_id, set()):
            try:
                await ws.send_json({"type": "task_update_batch", "data": updates})
            except RuntimeError as exc:
                logger.debug(
                    "websocket client disconnected during batch flush: %s",
                    exc,
                    exc_info=True,
                )  # Client disconnected

        self.accumulated[task_id] = []
        self.last_broadcast[task_id] = time.time()


class WebSocketManager:
    """Manage WebSocket connections with Ghost Mode buffer."""

    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = {}
        self.buffers: dict[
            str, deque[dict[str, Any]]
        ] = {}  # Ghost Mode: ~100 events per task
        self.broadcaster = ThrottledBroadcaster()

    async def connect(self, websocket: WebSocket, task_id: str, user_id: str) -> None:
        """Register WebSocket connection."""
        if task_id not in self.connections:
            self.connections[task_id] = set()
            self.buffers[task_id] = deque(maxlen=100)  # Ghost Mode buffer
        self.connections[task_id].add(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str) -> None:
        """Unregister WebSocket connection."""
        if task_id in self.connections:
            self.connections[task_id].discard(websocket)

    async def broadcast_task_update(
        self, task_id: str, update_data: dict[str, Any]
    ) -> None:
        """Broadcast task update (throttled to 300ms)."""
        # Add to Ghost Mode buffer
        if task_id in self.buffers:
            self.buffers[task_id].append(
                {
                    "event_id": str(uuid.uuid4()),
                    "timestamp": time.time(),
                    "data": update_data,
                }
            )

        # Throttled broadcast
        await self.broadcaster.add_update(task_id, update_data)

    def get_recent_events(
        self, task_id: str, last_event_id: str
    ) -> list[dict[str, Any]]:
        """Get recent events for resync (Ghost Mode)."""
        if task_id not in self.buffers:
            return []
        events = list(self.buffers[task_id])
        # Return events after last_event_id
        try:
            idx = next(
                i for i, e in enumerate(events) if e["event_id"] == last_event_id
            )
            return events[idx + 1 :]
        except StopIteration:
            return events


# Global manager instance
manager = WebSocketManager()
connections = manager.connections


# Router for WebSocket endpoint
router = APIRouter()


@router.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    task_id: str,
    token: str,
    db_path: str = Depends(get_db_path),
) -> None:
    """WebSocket endpoint for real-time progress updates.

    Query params:
        token: JWT access token OR API key
    """
    await websocket.accept()

    # Validate token
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[_jwt_algorithm()])
        user_id = payload.get("sub")
        if user_id is None:
            await websocket.close(code=1008)
            return
    except JWTError:
        from mastermind_cli.api.routes.keys import validate_api_key_v2

        user_id = await validate_api_key_v2(token, db_path)
        if user_id is None:
            await websocket.close(code=1008)
            return

    await manager.connect(websocket, task_id, str(user_id) if user_id else "anonymous")

    try:
        while True:
            if (
                websocket.client_state is not WebSocketState.CONNECTED
                or websocket.application_state is not WebSocketState.CONNECTED
            ):
                break
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)
    finally:
        manager.disconnect(websocket, task_id)
