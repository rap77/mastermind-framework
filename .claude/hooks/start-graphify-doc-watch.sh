#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GRAPHIFY_OUT="$PROJECT_ROOT/graphify-out"
PID_FILE="$GRAPHIFY_OUT/.graphify_doc_watch.pid"
LOG_FILE="${TMPDIR:-/tmp}/mastermind-graphify-doc-watch.log"

if [ ! -f "$GRAPHIFY_OUT/.graphify_root" ]; then
    exit 0
fi

mkdir -p "$GRAPHIFY_OUT" "${TMPDIR:-/tmp}/graphify-home" "${TMPDIR:-/tmp}/graphify-cache"

if [ -f "$PID_FILE" ]; then
    DOC_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [ -n "${DOC_PID:-}" ] && kill -0 "$DOC_PID" >/dev/null 2>&1; then
        exit 0
    fi
fi

nohup setsid "$SCRIPT_DIR/graphify-doc-watch-loop.sh" >>"$LOG_FILE" 2>&1 </dev/null &
echo $! > "$PID_FILE"
