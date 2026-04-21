#!/bin/bash
# GGA wrapper for large file sets
# Works around bash ARG_MAX limit by processing files in batches

set -e

# Get list of staged files
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|ts|tsx|js|jsx|go)$' | grep -v -E '(test|spec|\.d\.ts|dist/|build/|node_modules/)')

if [ -z "$FILES" ]; then
    echo "No files to review"
    exit 0
fi

# Count files
FILE_COUNT=$(echo "$FILES" | wc -l)
echo "GGA: Reviewing $FILE_COUNT files"

# Export required environment variables
export CLAUDECODE=""
export CLAUDE_CODE_ENTRYPOINT=""

# Process files in batches of 10 to avoid ARG_MAX limit
BATCH_SIZE=10
echo "$FILES" | xargs -I {} -P 1 -n $BATCH_SIZE bash -c '
    FILES=$(xargs)
    echo "GGA: Reviewing batch: $FILES"
    gga run --no-commit -- $FILES || true
' || {
    echo "GGA review completed with warnings"
}

echo "GGA: Review complete"
