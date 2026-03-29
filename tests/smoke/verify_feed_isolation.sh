#!/bin/bash
# Sentinel Script — Feed Isolation Verifier
# Usage: ./verify_feed_isolation.sh <brain-id> <expected-feed-file>
# Example: ./verify_feed_isolation.sh brain-04-frontend BRAIN-FEED-04-frontend.md
#
# Exit codes:
#   0 = PASS  — only expected feed modified (or no feed modified at all — valid for adversarial)
#   1 = FAIL  — unexpected files modified
#   2 = CRITICAL FAIL — global BRAIN-FEED.md was modified (read-only for agents)
#   3 = DIRTY WORKTREE — working tree was not clean before dispatch

set -euo pipefail

BRAIN_ID="${1:-}"
EXPECTED_FEED="${2:-}"

if [[ -z "$BRAIN_ID" || -z "$EXPECTED_FEED" ]]; then
  echo "Usage: $0 <brain-id> <expected-feed-file>"
  echo "Example: $0 brain-04-frontend BRAIN-FEED-04-frontend.md"
  exit 1
fi

# ──────────────────────────────────────────────
# Step 1: Pre-flight check — working tree must be clean
# ──────────────────────────────────────────────
DIRTY=$(git status --porcelain)
if [[ -n "$DIRTY" ]]; then
  echo "WARN: Working tree is dirty — cannot guarantee clean baseline for diff."
  echo "Dirty files:"
  echo "$DIRTY"
  echo ""
  echo "Commit or stash your changes before running this script."
  exit 3
fi

# ──────────────────────────────────────────────
# Step 2: Stash to create clean baseline (WSL2 belt-and-suspenders)
# ──────────────────────────────────────────────
echo "Stashing working tree to create clean baseline..."
git stash --include-untracked

# ──────────────────────────────────────────────
# Step 3: Ready for dispatch — wait for agent to complete
# ──────────────────────────────────────────────
echo ""
echo "READY: Dispatch $BRAIN_ID now. Press ENTER when agent completes."
read -r

# ──────────────────────────────────────────────
# Step 4: Capture diff — what did the agent modify?
# ──────────────────────────────────────────────
CHANGED_FILES=$(git diff --name-only)

# ──────────────────────────────────────────────
# Step 5: CRITICAL FAIL check — global BRAIN-FEED.md must NOT be modified
# Anchored regex: matches ".planning/BRAIN-FEED.md" exactly, not domain feeds
# ──────────────────────────────────────────────
if echo "$CHANGED_FILES" | grep -q "^\.planning/BRAIN-FEED\.md$"; then
  echo "CRITICAL FAIL: Global BRAIN-FEED.md was modified by agent."
  echo "Global feed is READ-ONLY for domain agents. Only the orchestrator may write it post-synthesis."
  git stash pop
  exit 2
fi

# ──────────────────────────────────────────────
# Step 6: FAIL check — no unexpected files beyond the expected feed
# Filter out the expected feed path. Anything remaining is a violation.
# "no feed modified at all" is VALID for adversarial dispatches (agent correctly refused to write)
# ──────────────────────────────────────────────
UNEXPECTED=$(echo "$CHANGED_FILES" | grep -v "^\.planning/$EXPECTED_FEED$" | grep -v "^$" || true)

if [[ -n "$UNEXPECTED" ]]; then
  echo "FAIL: Unexpected files modified by agent $BRAIN_ID:"
  echo "$UNEXPECTED"
  echo ""
  echo "Expected only: .planning/$EXPECTED_FEED (or no feed at all)"
  git stash pop
  exit 1
fi

# ──────────────────────────────────────────────
# Step 7: PASS
# ──────────────────────────────────────────────
echo "PASS: Only $EXPECTED_FEED modified (or no feeds modified — rejection-only)"
echo "Feed isolation verified for agent: $BRAIN_ID"
git stash pop
exit 0
