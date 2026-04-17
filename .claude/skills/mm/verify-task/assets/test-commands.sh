#!/bin/bash
# Verification commands for /mm:verify-task
# Usage: source this file in the skill execution

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check for hardcoded hex colors in TypeScript/TSX files
check_hardcoded_colors() {
    local target_dir="$1"
    echo "Checking for hardcoded hex colors in $target_dir..."

    local count=$(grep -rn '#[0-9a-fA-F]\{3,6\}' "$target_dir" 2>/dev/null \
        | grep -v '.test.' \
        | grep -v 'globals.css' \
        | grep -v 'var(' \
        | grep -v '//' \
        | wc -l)

    if [ "$count" -eq 0 ]; then
        echo_success "No hardcoded colors found"
        return 0
    else
        echo_error "Found $count hardcoded colors"
        grep -rn '#[0-9a-fA-F]\{3,6\}' "$target_dir" 2>/dev/null \
            | grep -v '.test.' \
            | grep -v 'globals.css' \
            | grep -v 'var(' \
            | grep -v '//' \
            | head -10
        return 1
    fi
}

# Check if theme tokens are being used
check_theme_tokens() {
    local target_dir="$1"
    echo "Checking for theme token usage in $target_dir..."

    local files_with_tokens=$(find "$target_dir" -name "*.tsx" -o -name "*.ts" 2>/dev/null \
        | xargs grep -l "var(--color-" 2>/dev/null \
        | wc -l)

    local files_with_semantic=$(find "$target_dir" -name "*.tsx" -o -name "*.ts" 2>/dev/null \
        | xargs grep -E "(text-foreground|bg-|border-)" 2>/dev/null \
        | wc -l)

    if [ "$files_with_tokens" -gt 0 ] || [ "$files_with_semantic" -gt 0 ]; then
        echo_success "Theme tokens in use ($files_with_tokens with var(), $files_with_semantic semantic)"
        return 0
    else
        echo_error "No theme tokens found"
        return 1
    fi
}

# Run frontend tests
run_frontend_tests() {
    echo "Running frontend tests..."
    cd apps/web && pnpm test 2>&1
}

# Run backend tests
run_backend_tests() {
    echo "Running backend tests..."
    cd apps/api && uv run pytest 2>&1
}

# Check if file exists
check_file_exists() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        echo_success "File exists: $file_path"
        return 0
    else
        echo_error "File missing: $file_path"
        return 1
    fi
}

# Export functions for use in skill
export -f echo_success echo_error echo_warning
export -f check_hardcoded_colors check_theme_tokens
export -f run_frontend_tests run_backend_tests
export -f check_file_exists
