#!/bin/bash
# GGA wrapper for large file sets.
# Batches staged files to avoid ARG_MAX while preserving a failing exit code.

set -euo pipefail

# Build the review list from staged source files only.
mapfile -t FILES < <(
    git diff --cached --name-only --diff-filter=ACM |
        grep -E '\.(py|ts|tsx|js|jsx|go)$' |
        grep -v -E '(test|spec|\.d\.ts|dist/|build/|node_modules/)' || true
)

if [ "${#FILES[@]}" -eq 0 ]; then
    echo "No files to review"
    exit 0
fi

echo "GGA: Reviewing ${#FILES[@]} files"

# Export required environment variables.
export CLAUDECODE=""
export CLAUDE_CODE_ENTRYPOINT=""

BATCH_SIZE=10
review_failed=0

for ((i = 0; i < ${#FILES[@]}; i += BATCH_SIZE)); do
    batch=("${FILES[@]:i:BATCH_SIZE}")
    echo "GGA: Reviewing batch: ${batch[*]}"
    if ! gga run --no-commit -- "${batch[@]}"; then
        review_failed=1
    fi
done

echo "GGA: Review complete"
exit "$review_failed"
