#!/bin/bash
# GGA wrapper for pre-commit review.
# Batches staged files through temporary indexes so gga run sees exact staged content
# without ever receiving positional file arguments.

set -euo pipefail

# Export required environment variables.
export CLAUDECODE=""
export CLAUDE_CODE_ENTRYPOINT=""

mapfile -d '' -t FILES < <(git diff --cached -z --name-only --diff-filter=ACM)

if [ "${#FILES[@]}" -eq 0 ]; then
    echo "No files to review"
    exit 0
fi

echo "GGA: Reviewing ${#FILES[@]} files"

BATCH_SIZE="${GGA_BATCH_SIZE:-10}"
if ! [[ "$BATCH_SIZE" =~ ^[1-9][0-9]*$ ]]; then
    echo "Invalid GGA_BATCH_SIZE: $BATCH_SIZE" >&2
    exit 1
fi

review_failed=0

run_batch() {
    local -a batch=("$@")
    local temp_dir temp_index status entry file

    temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/gga-index.XXXXXX")"
    temp_index="$temp_dir/index"

    GIT_INDEX_FILE="$temp_index" git read-tree --empty

    for file in "${batch[@]}"; do
        entry="$(git ls-files -s -- "$file" || true)"
        if [ -z "$entry" ]; then
            continue
        fi
        printf '%s\n' "$entry" | GIT_INDEX_FILE="$temp_index" git update-index --index-info
    done

    echo "GGA: Reviewing batch: ${batch[*]}"
    if GIT_INDEX_FILE="$temp_index" gga run; then
        status=0
    else
        status=$?
    fi

    rm -rf "$temp_dir"
    return "$status"
}

for ((i = 0; i < ${#FILES[@]}; i += BATCH_SIZE)); do
    batch=("${FILES[@]:i:BATCH_SIZE}")
    if ! run_batch "${batch[@]}"; then
        review_failed=1
    fi
done

echo "GGA: Review complete"
exit "$review_failed"
