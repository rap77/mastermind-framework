#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> tools/mastermind-cli governance/budget/orchestration"
(
  cd "$ROOT_DIR/tools/mastermind-cli"
  UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m pytest \
    tests/test_budget.py \
    tests/test_governance.py \
    tests/test_orchestration.py \
    tests/test_orchestration_e2e.py \
    -q
)

echo
echo "==> apps/api governance wiring"
(
  cd "$ROOT_DIR/apps/api"
  UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m pytest \
    tests/unit/test_governance.py \
    tests/unit/test_stateless_coordinator.py \
    tests/api/test_task_runner.py \
    tests/api/test_executions.py \
    -q
)
