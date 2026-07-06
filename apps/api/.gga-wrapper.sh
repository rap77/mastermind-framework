#!/bin/bash
# GGA wrapper for pre-commit review.
# Delegates directly to gga run so the hook does not misread staged paths as a commit message.

set -euo pipefail

echo "GGA: Reviewing staged files"

# Export required environment variables.
export CLAUDECODE=""
export CLAUDE_CODE_ENTRYPOINT=""

exec gga run
