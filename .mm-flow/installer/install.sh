#!/usr/bin/env bash
# mm-flow installer
# Usage: ./install.sh [--target <path>] [--brains <niche>]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TARGET_DIR="${PWD}"
BRAINS_NICHE="${BRAINS_NICHE:-software-development}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET_DIR="$2"
      shift 2
      ;;
    --brains)
      BRAINS_NICHE="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

echo "=== mm-flow Installer ==="
echo "Source: $FRAMEWORK_ROOT"
echo "Target: $TARGET_DIR"

# Create .mm-flow in target if it doesn't exist
mkdir -p "$TARGET_DIR/.mm-flow"

# Copy framework
echo "Installing framework..."
cp -r "$FRAMEWORK_ROOT/.mm-flow/commands" "$TARGET_DIR/.mm-flow/"
cp -r "$FRAMEWORK_ROOT/.mm-flow/agents" "$TARGET_DIR/.mm-flow/"
cp -r "$FRAMEWORK_ROOT/.mm-flow/skills" "$TARGET_DIR/.mm-flow/"
cp -r "$FRAMEWORK_ROOT/.mm-flow/config" "$TARGET_DIR/.mm-flow/"
cp -r "$FRAMEWORK_ROOT/.mm-flow/assets" "$TARGET_DIR/.mm-flow/"

# Copy brains if specified
if [ "$BRAINS_NICHE" != "none" ]; then
  echo "Installing brain pack: $BRAINS_NICHE"
  mkdir -p "$TARGET_DIR/.mm-brains"
  if [ -d "$FRAMEWORK_ROOT/brains/$BRAINS_NICHE" ]; then
    cp -r "$FRAMEWORK_ROOT/brains/$BRAINS_NICHE" "$TARGET_DIR/.mm-brains/"
  else
    echo "WARNING: Brain pack '$BRAINS_NICHE' not found in brains/"
  fi
fi

# Copy planning structure
mkdir -p "$TARGET_DIR/.mm-flow/planning/changes"
mkdir -p "$TARGET_DIR/.mm-flow/planning/archive"
mkdir -p "$TARGET_DIR/.mm-flow/planning/roadmap"

# Claude Code compatibility wrappers (optional but useful)
mkdir -p "$TARGET_DIR/.claude/commands" "$TARGET_DIR/.claude/agents" "$TARGET_DIR/.claude/skills"
ln -sfn ../../.mm-flow/commands/mm "$TARGET_DIR/.claude/commands/mm"
ln -sfn ../../.mm-flow/agents/mm "$TARGET_DIR/.claude/agents/mm"
ln -sfn ../../.mm-flow/skills/mm "$TARGET_DIR/.claude/skills/mm"

echo "=== Installation complete ==="
echo "Framework installed at: $TARGET_DIR/.mm-flow/"
echo "Brains installed at: $TARGET_DIR/.mm-brains/"
echo "Claude compatibility wrappers installed at: $TARGET_DIR/.claude/"
echo "Framework ready."
