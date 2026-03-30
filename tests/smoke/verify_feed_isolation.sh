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

# ──────────────────────────────────────────────
# Optional checks — activated via --check flag
# Usage: ./verify_feed_isolation.sh brain-04-frontend BRAIN-FEED-04-frontend.md --check barrier-order
#        ./verify_feed_isolation.sh brain-04-frontend BRAIN-FEED-04-frontend.md --check crosstalk
#        ./verify_feed_isolation.sh brain-04-frontend BRAIN-FEED-04-frontend.md --check mcp-elimination
# Note: --check flags run standalone (no stash/dispatch needed) and exit early.
# ──────────────────────────────────────────────
CHECK_MODE="${3:-}"

if [[ "$CHECK_MODE" == "--check" ]]; then
  CHECK_TYPE="${4:-}"

  case "$CHECK_TYPE" in
    barrier-order)
      # Barrier order check — Phase 12 specific
      # Verifica que brain-07-growth NO fue el primer agente en escribir output
      # Observable: si un output file existe para brain-07 pero no para dominio previo = FAIL
      # In Phase 12: this check is MANUAL (observational via Claude Code UI)
      # This flag documents the check requirement and exits 0 (human must confirm)
      echo "CHECK barrier-order: Manual verification required."
      echo "In Claude Code UI: confirm Brain #7 dispatch prompt appears AFTER all 6 domain agent responses."
      echo "Observable: Multiple simultaneous 'thinking' indicators, then Brain #7 fires last."
      echo "PASS (manual confirmation required — script cannot automate UI observation)"
      exit 0
      ;;

    crosstalk)
      # Cross-talk isolation check — Phase 12 specific
      # Verifica que cada agente solo recibió sus propios fragmentos SYNC
      # Test estático: brain-04 solo tiene SYNC tags apuntando a BF-05, nunca a BF-01/02/03/06/07
      echo "CHECK crosstalk: Verifying SYNC tag isolation..."
      FEED_04=".planning/BRAIN-FEED-04-frontend.md"
      if [[ ! -f "$FEED_04" ]]; then
        echo "FAIL: BRAIN-FEED-04-frontend.md not found at .planning/"
        exit 1
      fi
      # Brain #4 feed should ONLY have SYNC tags pointing to BF-05 (backend)
      # Any SYNC tag pointing to other feeds = cross-talk violation
      CROSSTALK=$(grep '\[SYNC:' "$FEED_04" | grep -v 'BF-05' || true)
      if [[ -n "$CROSSTALK" ]]; then
        echo "FAIL: Brain #4 feed has SYNC tags pointing outside BF-05 (cross-talk risk):"
        echo "$CROSSTALK"
        exit 1
      fi
      echo "PASS: Brain #4 SYNC tags all point to BF-05 (backend) only. No cross-talk detected."
      exit 0
      ;;

    mcp-elimination)
      # Static check: confirm no MCP steps remain in command/skill files
      echo "CHECK mcp-elimination: Scanning for residual mcp__notebooklm-mcp__ steps..."
      VIOLATIONS=$(grep -r "mcp__notebooklm-mcp__notebook_query" .claude/commands/mm/ .claude/skills/mm/ 2>/dev/null || true)
      if [[ -n "$VIOLATIONS" ]]; then
        echo "FAIL: Found residual MCP steps (DISP-02 violation):"
        echo "$VIOLATIONS"
        exit 1
      fi
      echo "PASS: No mcp__notebooklm-mcp__notebook_query found in command/skill files."
      exit 0
      ;;

    *)
      echo "Unknown check type: $CHECK_TYPE"
      echo "Valid options: barrier-order, crosstalk, mcp-elimination"
      exit 1
      ;;
  esac
fi

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
