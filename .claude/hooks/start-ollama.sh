#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${TMPDIR:-/tmp}/mastermind-ollama.pid"
LOG_FILE="${TMPDIR:-/tmp}/mastermind-ollama.log"

if ! command -v ollama >/dev/null 2>&1; then
    exit 0
fi

if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    exit 0
fi

if [ -f "$PID_FILE" ]; then
    OLLAMA_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [ -n "${OLLAMA_PID:-}" ] && kill -0 "$OLLAMA_PID" >/dev/null 2>&1; then
        exit 0
    fi
fi

nohup setsid ollama serve >>"$LOG_FILE" 2>&1 </dev/null &
echo $! > "$PID_FILE"
