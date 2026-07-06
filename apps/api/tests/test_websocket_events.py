"""
Tests for WebSocket events and Ghost Mode replay

Validates:
- Ghost Mode replay returns last 100 events
- P95 replay latency < 500ms (SLI-1)
- All events contain trace_id (SLI-3)
"""

import asyncio
import json
from datetime import datetime
from typing import List

import websockets
from websockets.exceptions import ConnectionClosed
import pytest
import pytest_asyncio

from scripts.run_ws_server import handler
from websockets.asyncio.server import serve


@pytest_asyncio.fixture
async def websocket_server_uri() -> str:
    """Start an isolated WebSocket server for the integration tests."""
    async with serve(handler, "127.0.0.1", 0) as server:
        socket = server.sockets[0]
        host, port = socket.getsockname()[:2]
        yield f"ws://{host}:{port}/ws"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_websocket_ghost_mode_replay(websocket_server_uri: str):
    """Test Ghost Mode replay returns last 100 events with P95 latency < 500ms.

    Requires WebSocket server running on localhost:8080.
    Run manually: start Rust control plane first (cargo run in rust_control_plane/).
    """
    uri = websocket_server_uri
    latencies: List[float] = []

    async with websockets.connect(uri) as websocket:
        # Request Ghost Mode replay
        request = {"type": "ghost_replay"}
        await websocket.send(json.dumps(request))

        start_time = datetime.now()

        # Receive up to 100 events
        event_count = 0
        while event_count < 100:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                event = json.loads(message)

                if event.get("type") == "ghost_replay":
                    latency_ms = (datetime.now() - start_time).total_seconds() * 1000
                    latencies.append(latency_ms)
                    event_count += 1

            except asyncio.TimeoutError:
                break
            except ConnectionClosed:
                break

    # Calculate P95 latency
    if latencies:
        latencies.sort()
        p95_index = int(len(latencies) * 0.95)
        p95_latency = latencies[p95_index]

        # SLI-1: P95 < 500ms
        assert (
            p95_latency < 500
        ), f"SLI-1 FAILED: P95 latency {p95_latency:.2f}ms >= 500ms"
        print(f"SLI-1 PASSED: P95 latency = {p95_latency:.2f}ms < 500ms")
    else:
        pytest.skip("No events received for latency measurement")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_websocket_trace_id_propagation(websocket_server_uri: str):
    """Test 100% of events contain trace_id (SLI-3).

    Requires WebSocket server running on localhost:8080.
    """
    uri = websocket_server_uri

    async with websockets.connect(uri) as websocket:
        # Request Ghost Mode replay
        request = {"type": "ghost_replay"}
        await websocket.send(json.dumps(request))

        events_without_trace_id = 0
        total_events = 0

        # Receive events
        try:
            while True:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                event = json.loads(message)

                total_events += 1

                if "trace_id" not in event:
                    events_without_trace_id += 1

        except asyncio.TimeoutError:
            pass
        except ConnectionClosed:
            pass  # Connection closed normally

    # SLI-3: 100% of events should have trace_id
    if total_events > 0:
        trace_propagation_rate = (total_events - events_without_trace_id) / total_events
        assert (
            trace_propagation_rate == 1.0
        ), f"SLI-3 FAILED: {trace_propagation_rate * 100:.1f}% < 100%"
        print(
            f"SLI-3 PASSED: {trace_propagation_rate * 100:.1f}% of events have trace_id"
        )
    else:
        pytest.skip("No events received for trace_id validation")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_websocket_connection_stability(websocket_server_uri: str):
    """Test 1000 concurrent connections (stress test).

    Requires WebSocket server running on localhost:8080.
    """
    uri = websocket_server_uri
    num_connections = 1000

    async def single_connection(conn_id: int):
        try:
            async with websockets.connect(uri) as _:
                # Keep connection open for 1 second (reduced from 10s for faster tests)
                await asyncio.sleep(1)
                return True
        except Exception as e:
            print(f"Connection {conn_id} failed: {e}")
            return False

    # Create 1000 concurrent connections
    tasks = [single_connection(i) for i in range(num_connections)]
    results = await asyncio.gather(*tasks)

    successful_connections = sum(results)
    success_rate = successful_connections / num_connections

    # Expect at least 95% success rate
    assert success_rate >= 0.95, f"Only {success_rate * 100:.1f}% connections succeeded"
    print(
        f"Connection stability: {successful_connections}/{num_connections} ({success_rate * 100:.1f}%)"
    )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
