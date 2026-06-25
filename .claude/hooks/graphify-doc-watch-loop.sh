#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PID_FILE="$PROJECT_ROOT/graphify-out/.graphify_doc_watch.pid"
FLAG_FILE="$PROJECT_ROOT/graphify-out/needs_update"
LOG_FILE="${TMPDIR:-/tmp}/mastermind-graphify-doc-watch.log"

export HOME="${TMPDIR:-/tmp}/graphify-home"
export XDG_CACHE_HOME="${TMPDIR:-/tmp}/graphify-cache"
export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434/v1}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5-coder:7b}"
export GRAPHIFY_QUERY_LOG_DISABLE=1
export GRAPHIFY_NO_BACKUP=1
export GRAPHIFY_MAX_WORKERS=1

while true; do
    if [ -f "$FLAG_FILE" ]; then
        "$SCRIPT_DIR/refresh-graphify.sh" >>"$LOG_FILE" 2>&1 || true
        rm -f "$FLAG_FILE"
    fi
    sleep 3
done
