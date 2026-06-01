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

# Remove all legacy mastermind artifacts before installing
clean_legacy_mastermind() {
  local target="$1"
  echo "Cleaning legacy mastermind artifacts..."

  # Old planning directory (pre-.mm-flow era)
  if [ -e "$target/.planning" ]; then
    rm -rf "$target/.planning"
    echo "  Removed: .planning/"
  fi

  # Old .claude/commands/mm directory (may contain stale .py handlers)
  if [ -e "$target/.claude/commands/mm" ] && [ ! -L "$target/.claude/commands/mm" ]; then
    rm -rf "$target/.claude/commands/mm"
    echo "  Removed: .claude/commands/mm/ (stale directory)"
  fi

  # Old .claude/agents/mm directory
  if [ -e "$target/.claude/agents/mm" ] && [ ! -L "$target/.claude/agents/mm" ]; then
    rm -rf "$target/.claude/agents/mm"
    echo "  Removed: .claude/agents/mm/ (stale directory)"
  fi

  # Old .claude/skills/mm directory
  if [ -e "$target/.claude/skills/mm" ] && [ ! -L "$target/.claude/skills/mm" ]; then
    rm -rf "$target/.claude/skills/mm"
    echo "  Removed: .claude/skills/mm/ (stale directory)"
  fi
}

clean_legacy_mastermind "$TARGET_DIR"

# Create .mm-flow in target if it doesn't exist
mkdir -p "$TARGET_DIR/.mm-flow"

remove_existing_path() {
  local path="$1"
  if [ -L "$path" ] || [ -f "$path" ]; then
    rm -f "$path"
  elif [ -d "$path" ]; then
    rm -rf "$path"
  fi
}

# Install a source directory into a target directory using absolute symlinks.
# Symlinks follow the source path — edits in mastermind propagate automatically
# without needing to re-run the installer.
link_framework_dir() {
  local src="$1"
  local dst="$2"
  mkdir -p "$dst"
  find "$src" -type f | while read -r src_file; do
    rel="${src_file#"$src"/}"
    dst_file="$dst/$rel"
    mkdir -p "$(dirname "$dst_file")"
    rm -f "$dst_file"
    ln -sf "$src_file" "$dst_file"
  done
  # Recreate empty subdirs that contain no files
  find "$src" -type d | while read -r src_dir; do
    rel="${src_dir#"$src"/}"
    [ "$rel" = "$src_dir" ] && continue
    mkdir -p "$dst/$rel"
  done
}

# Install framework via absolute symlinks so source edits propagate automatically
echo "Installing framework (symlinks)..."
link_framework_dir "$FRAMEWORK_ROOT/.mm-flow/commands" "$TARGET_DIR/.mm-flow/commands"
link_framework_dir "$FRAMEWORK_ROOT/.mm-flow/agents"   "$TARGET_DIR/.mm-flow/agents"
link_framework_dir "$FRAMEWORK_ROOT/.mm-flow/skills"   "$TARGET_DIR/.mm-flow/skills"
link_framework_dir "$FRAMEWORK_ROOT/.mm-flow/config"   "$TARGET_DIR/.mm-flow/config"
link_framework_dir "$FRAMEWORK_ROOT/.mm-flow/assets"   "$TARGET_DIR/.mm-flow/assets"

# Install brain pack via hardlinks
if [ "$BRAINS_NICHE" != "none" ]; then
  echo "Installing brain pack: $BRAINS_NICHE"
  mkdir -p "$TARGET_DIR/.mm-brains"
  if [ -d "$FRAMEWORK_ROOT/brains/$BRAINS_NICHE" ]; then
    link_framework_dir "$FRAMEWORK_ROOT/brains/$BRAINS_NICHE" "$TARGET_DIR/.mm-brains/$BRAINS_NICHE"
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
remove_existing_path "$TARGET_DIR/.claude/commands/mm"
remove_existing_path "$TARGET_DIR/.claude/agents/mm"
remove_existing_path "$TARGET_DIR/.claude/skills/mm"
ln -sfn ../../.mm-flow/commands/mm "$TARGET_DIR/.claude/commands/mm"
ln -sfn ../../.mm-flow/agents/mm "$TARGET_DIR/.claude/agents/mm"
ln -sfn ../../.mm-flow/skills/mm "$TARGET_DIR/.claude/skills/mm"

echo "=== Installation complete ==="
echo "Framework installed at: $TARGET_DIR/.mm-flow/"
echo "Brains installed at: $TARGET_DIR/.mm-brains/"
echo "Claude compatibility wrappers installed at: $TARGET_DIR/.claude/"
echo "Framework ready."
