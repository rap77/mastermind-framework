#!/bin/bash
# MasterMind Framework - SessionStart Hook
#
# This hook activates when a Claude Code session starts in a project
# that has MasterMind Framework installed (.mastermind-active file exists)
#
# It loads the framework configuration and makes the 7 brains available
# for consultation via the mastermind-consultant skill.

set -e

PROJECT_ROOT="$PWD"
MASTERMIND_ACTIVE="$PROJECT_ROOT/.mastermind-active"
MASTERMIND_CONFIG="$PROJECT_ROOT/.mastermind/config.yaml"

# Check if MasterMind is installed in this project
if [ ! -f "$MASTERMIND_ACTIVE" ]; then
    # Not a MasterMind project, silently exit
    exit 0
fi

# Read activation file
if [ -f "$MASTERMIND_ACTIVE" ]; then
    # Parse key=value pairs (skip comments)
    while IFS='=' read -r key value; do
        # Skip empty lines and comments
        [[ -z "$key" || "$key" =~ ^#.* ]] && continue
        # Trim whitespace and export
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        export "MASTERMIND_$key=$value"
    done < "$MASTERMIND_ACTIVE"
fi

# Set framework path for tools to access
if [ -n "$MASTERMIND_framework_path" ]; then
    export MASTERMIND_FRAMEWORK_PATH="$MASTERMIND_framework_path"
fi

# Get active brains (default to all if not specified)
if [ -n "$MASTERMIND_brains" ]; then
    export MASTERMIND_ACTIVE_BRAINS="$MASTERMIND_brains"
else
    export MASTERMIND_ACTIVE_BRAINS="all"
fi

# Output to user (only in interactive mode)
if [ -t 1 ]; then
    echo "# 🧠 MasterMind Framework Active"
    echo "# Version: $MASTERMIND_version"
    echo "# Brains: $MASTERMIND_ACTIVE_BRAINS"
    echo ""
    echo "# Use mastermind-consultant skill to query the 7 brains"
    echo "# Run 'mastermind install status' for details"
fi

# The framework is now active and the mastermind-consultant skill
# will automatically detect the .mastermind-active file and activate.
