#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GRAPHIFY_OUT="$PROJECT_ROOT/graphify-out"
ROOT_FILE="$GRAPHIFY_OUT/.graphify_root"
LOG_FILE="${TMPDIR:-/tmp}/mastermind-graphify-refresh.log"

if ! command -v graphify >/dev/null 2>&1; then
    exit 0
fi

if [ ! -f "$ROOT_FILE" ]; then
    exit 0
fi

mkdir -p "$GRAPHIFY_OUT"

mkdir -p "${TMPDIR:-/tmp}/graphify-home" "${TMPDIR:-/tmp}/graphify-cache"

HOME="${TMPDIR:-/tmp}/graphify-home" \
XDG_CACHE_HOME="${TMPDIR:-/tmp}/graphify-cache" \
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434/v1}" \
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5-coder:7b}" \
GRAPHIFY_QUERY_LOG_DISABLE=1 \
GRAPHIFY_NO_BACKUP=1 \
GRAPHIFY_MAX_WORKERS=1 \
graphify update "$PROJECT_ROOT" --no-cluster >>"$LOG_FILE" 2>&1 || true
