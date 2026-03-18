#!/usr/bin/env bash
# Archive rotation script for experience records
# Dumps old records to compressed JSONL and deletes from DB

set -euo pipefail

# ============================================
# Configuration
# ============================================
DB_PATH="${DB_PATH:-mastermind.db}"
ARCHIVE_DIR="${ARCHIVE_DIR:-./archive}"  # Changed from /archive to ./archive
RETENTION_DAYS=30
DRY_RUN=false

# ============================================
# Usage
# ============================================
show_usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Archive old experience records to compressed JSONL and delete from database.

OPTIONS:
    -h, --help              Show this help message
    -d, --dry-run           Show what would be done without making changes
    -a, --archive-dir DIR   Specify archive directory (default: ./archive)
    -r, --retention DAYS    Retention period in days (default: 30)

ENVIRONMENT VARIABLES:
    DB_PATH                 Database path (default: mastermind.db)
    ARCHIVE_DIR             Archive directory (default: ./archive)

EXAMPLES:
    # Dry run to see what would be archived
    $(basename "$0") --dry-run

    # Archive to custom directory
    $(basename "$0") --archive-dir /var/backups/mastermind

    # Custom retention period
    $(basename "$0") --retention 90

EOF
}

# ============================================
# CLI Parsing
# ============================================
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -a|--archive-dir)
            ARCHIVE_DIR="$2"
            shift 2
            ;;
        -r|--retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        *)
            echo "❌ Unknown option: $1" >&2
            echo "Run '$(basename "$0") --help' for usage." >&2
            exit 1
            ;;
    esac
done

# ============================================
# Pre-flight checks
# ============================================
if [[ ! -f "$DB_PATH" ]]; then
    echo "❌ Database not found: $DB_PATH" >&2
    exit 1
fi

# Create archive directory if not exists
mkdir -p "$ARCHIVE_DIR"

# ============================================
# Generate archive filename
# ============================================
DATE=$(date +%Y%m%d)
ARCHIVE_FILE="$ARCHIVE_DIR/mm-logs-$DATE.jsonl.gz"

# ============================================
# Dry run mode
# ============================================
if [[ "$DRY_RUN" == "true" ]]; then
    echo "🔍 DRY RUN MODE - No changes will be made"
    echo ""
    echo "Configuration:"
    echo "  Database:      $DB_PATH"
    echo "  Archive dir:   $ARCHIVE_DIR"
    echo "  Retention:     $RETENTION_DAYS days"
    echo "  Archive file:  $ARCHIVE_FILE"
    echo ""

    # Count records that would be archived
    COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM experience_records WHERE timestamp < datetime('now', '-$RETENTION_DAYS days')")
    echo "Records to archive: $COUNT"
    echo "Records to delete:  $COUNT"
    echo ""
    echo "✅ Dry run complete. Re-run without --dry-run to execute."
    exit 0
fi

# ============================================
# Archive execution
# ============================================
echo "📦 Starting archive rotation..."
echo "   Database:   $DB_PATH"
echo "   Archive:    $ARCHIVE_FILE"
echo "   Retention:  $RETENTION_DAYS days"
echo ""

# Dump records older than RETENTION_DAYS to JSONL format
sqlite3 "$DB_PATH" <<EOF | gzip > "$ARCHIVE_FILE"
.mode json
SELECT * FROM experience_records
WHERE timestamp < datetime('now', '-$RETENTION_DAYS days');
EOF

ARCHIVED_COUNT=$(zcat "$ARCHIVE_FILE" | wc -l)
echo "✅ Archived $ARCHIVED_COUNT records"

# Delete archived records from database
sqlite3 "$DB_PATH" <<EOF
DELETE FROM experience_records
WHERE timestamp < datetime('now', '-$RETENTION_DAYS days');
EOF

DELETED=$(sqlite3 "$DB_PATH" "SELECT changes()")
echo "🗑️  Deleted $DELETED records from database"

# Vacuum database to reclaim space
echo "🧹 Vacuuming database..."
sqlite3 "$DB_PATH" "VACUUM;"

# Show archive file size
ARCHIVE_SIZE=$(du -h "$ARCHIVE_FILE" | cut -f1)
echo ""
echo "✅ Archive rotation complete!"
echo "   Archive size: $ARCHIVE_SIZE"
echo "   Location:     $ARCHIVE_FILE"
