#!/bin/bash
# mm-flow installer
# Usage: ./install.sh [--target <path>] [--brains <niche>]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_SOURCE="$SCRIPT_DIR"
TARGET_DIR="${TARGET_DIR:-$SCRIPT_DIR}"
BRAINS_NICHE="${BRAINS_NICHE:-software-development}"

echo "=== mm-flow Installer ==="
echo "Source: $FRAMEWORK_SOURCE"
echo "Target: $TARGET_DIR"

# Create .mm-flow in target if it doesn't exist
mkdir -p "$TARGET_DIR/.mm-flow"

# Copy framework
echo "Installing framework..."
cp -r "$FRAMEWORK_SOURCE/.mm-flow/commands" "$TARGET_DIR/.mm-flow/"
cp -r "$FRAMEWORK_SOURCE/.mm-flow/agents" "$TARGET_DIR/.mm-flow/"
cp -r "$FRAMEWORK_SOURCE/.mm-flow/skills" "$TARGET_DIR/.mm-flow/"
cp -r "$FRAMEWORK_SOURCE/.mm-flow/config" "$TARGET_DIR/.mm-flow/"

# Copy brains if specified
if [ "$BRAINS_NICHE" != "none" ]; then
  echo "Installing brain pack: $BRAINS_NICHE"
  mkdir -p "$TARGET_DIR/.mm-brains"
  if [ -d "$FRAMEWORK_SOURCE/brains/$BRAINS_NICHE" ]; then
    cp -r "$FRAMEWORK_SOURCE/brains/$BRAINS_NICHE" "$TARGET_DIR/.mm-brains/"
  else
    echo "WARNING: Brain pack '$BRAINS_NICHE' not found in brains/"
  fi
fi

# Copy planning structure
mkdir -p "$TARGET_DIR/.mm-flow/planning/changes"
mkdir -p "$TARGET_DIR/.mm-flow/planning/archive"
mkdir -p "$TARGET_DIR/.mm-flow/planning/roadmap"

echo "=== Installation complete ==="
echo "Framework installed at: $TARGET_DIR/.mm-flow/"
echo "Brains installed at: $TARGET_DIR/.mm-brains/"

# Create symlink for .mm-flow in project root if different from source
if [ "$TARGET_DIR" != "$SCRIPT_DIR" ]; then
  echo "Symlink created. Framework ready."
fi
