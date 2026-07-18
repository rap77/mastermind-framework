#!/usr/bin/env bash
# Run the real PostgreSQL smoke tests for the RAG evaluation gate.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:devpassword@localhost:5434/mastermind_bd}"

echo "Running RAG gate smoke tests against ${DATABASE_URL}"
uv run pytest tests/integration/test_rag_gate.py -q
