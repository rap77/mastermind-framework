#!/usr/bin/env python3
"""WebSocket test server for test_websocket_events.py

Implements Ghost Mode replay with:
- Endpoint: ws://localhost:8080/ws
- Message type: ghost_replay (returns last 100 events)
- Trace ID propagation (100% of events)
- Connection stability support
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime

import websockets

logger = logging.getLogger(__name__)


# Pre-create 100 dummy events with trace_id for Ghost Mode replay
EVENT_BUFFER = []
for i in range(100):
    EVENT_BUFFER.append(
        {
            "type": "ghost_replay",
            "event_id": str(uuid.uuid4()),
            "trace_id": str(uuid.uuid4()),  # SLI-3: 100% trace_id coverage
            "timestamp": datetime.now().isoformat(),
            "data": {
                "event_number": i,
                "status": "completed" if i < 90 else "running",
            },
        }
    )


async def handle_ghost_replay(
    websocket: websockets.server.WebSocketServerProtocol,
) -> None:
    """Handle Ghost Mode replay request."""
    logger.info("Received ghost_replay request")
    start_time = datetime.now()

    for i, event in enumerate(EVENT_BUFFER):
        # Create a copy to avoid mutating the buffer
        event_copy = dict(event)
        event_copy["sent_at"] = datetime.now().isoformat()
        await websocket.send(json.dumps(event_copy))

        # Small delay to simulate real-world scenario
        await asyncio.sleep(0.001)

        if (i + 1) % 20 == 0:
            logger.debug(f"Sent {i + 1}/{len(EVENT_BUFFER)} events")

    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds() * 1000
    logger.info(f"Sent {len(EVENT_BUFFER)} events in {total_time:.2f}ms")


async def handler(websocket: websockets.server.WebSocketServerProtocol) -> None:
    """WebSocket connection handler."""
    logger.info("Client connected.")

    try:
        async for message in websocket:
            data = json.loads(message)
            logger.debug(f"Received message: {data.get('type')}")

            # Handle Ghost Mode replay request
            if data.get("type") == "ghost_replay":
                await handle_ghost_replay(websocket)
            else:
                # Echo back unknown messages
                await websocket.send(
                    json.dumps(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {data.get('type')}",
                        }
                    )
                )

    except websockets.exceptions.ConnectionClosed as e:
        logger.info(f"Client disconnected: {e}")
    except Exception as e:
        logger.error(f"Error handling client: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


async def main() -> None:
    """Main entry point."""
    logger.info("Starting WebSocket server on ws://localhost:8080")
    logger.info("Test endpoint: ws://localhost:8080/ws")

    async with websockets.serve(handler, "localhost", 8080):
        print("Server running. Press Ctrl+C to stop.")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
