#!/usr/bin/env bash
# Install pre-commit hooks (one-time setup)

set -euo pipefail

echo "Installing pre-commit hooks..."

# Install pre-commit via uv
uv tool install pre-commit

# Install hooks from .pre-commit-config.yaml
pre-commit install

# Run initial check
pre-commit run --all-files

echo "✅ Pre-commit hooks installed!"
echo "Git hooks will now run automatically on git commit."
