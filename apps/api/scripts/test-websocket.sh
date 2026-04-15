#!/bin/bash
# Test WebSocket server execution script
#
# Usage:
#   ./scripts/test-websocket.sh          # Start server and run tests
#   ./scripts/test-websocket.sh server   # Start server only
#   ./scripts/test-websocket.sh test     # Run tests only (server must be running)

set -euo pipefail

cd "$(dirname "$0")/.."

SERVER_PID=""
LOG_FILE="/tmp/ws-server-test.log"

cleanup() {
    if [ -n "$SERVER_PID" ]; then
        echo "Stopping WebSocket server (PID: $SERVER_PID)..."
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}

trap cleanup EXIT INT TERM

start_server() {
    echo "Starting WebSocket server..."
    uv run python scripts/run_ws_server.py > "$LOG_FILE" 2>&1 &
    SERVER_PID=$!

    # Wait for server to be ready
    for i in {1..10}; do
        if lsof -i :8080 >/dev/null 2>&1; then
            echo "Server started successfully (PID: $SERVER_PID)"
            return 0
        fi
        sleep 0.5
    done

    echo "ERROR: Server failed to start"
    cat "$LOG_FILE"
    return 1
}

run_tests() {
    echo "Running WebSocket tests..."
    uv run pytest tests/test_websocket_events.py -v -s
}

case "${1:-all}" in
    server)
        start_server
        echo "Server running. Press Ctrl+C to stop."
        wait
        ;;
    test)
        run_tests
        ;;
    all)
        start_server
        sleep 2  # Give server time to fully initialize
        run_tests
        ;;
    *)
        echo "Usage: $0 [server|test|all]"
        echo "  server - Start server only"
        echo "  test   - Run tests only (server must be running)"
        echo "  all    - Start server and run tests (default)"
        exit 1
        ;;
esac
