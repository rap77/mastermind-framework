#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GRAPHIFY_OUT="$PROJECT_ROOT/graphify-out"
ROOT_FILE="$GRAPHIFY_OUT/.graphify_root"
PID_FILE="$GRAPHIFY_OUT/.graphify_watch.pid"
LOG_FILE="${TMPDIR:-/tmp}/mastermind-graphify-watch.log"

if ! command -v graphify >/dev/null 2>&1; then
    exit 0
fi

if [ ! -f "$ROOT_FILE" ]; then
    exit 0
fi

mkdir -p "$GRAPHIFY_OUT" "${TMPDIR:-/tmp}/graphify-home" "${TMPDIR:-/tmp}/graphify-cache"

if [ -f "$PID_FILE" ]; then
    WATCH_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [ -n "${WATCH_PID:-}" ] && kill -0 "$WATCH_PID" >/dev/null 2>&1; then
        exit 0
    fi
fi

nohup setsid env \
    HOME="${TMPDIR:-/tmp}/graphify-home" \
    XDG_CACHE_HOME="${TMPDIR:-/tmp}/graphify-cache" \
    GRAPHIFY_QUERY_LOG_DISABLE=1 \
    GRAPHIFY_NO_BACKUP=1 \
    GRAPHIFY_MAX_WORKERS=1 \
    graphify watch "$PROJECT_ROOT" --debounce 2 >>"$LOG_FILE" 2>&1 </dev/null &
echo $! > "$PID_FILE"
