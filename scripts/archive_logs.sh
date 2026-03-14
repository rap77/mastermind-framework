#!/usr/bin/env bash
# Archive rotation script for experience records
# Dumps old records to compressed JSONL and deletes from DB

set -euo pipefail

# Configuration
DB_PATH="${DB_PATH:-mastermind.db}"
ARCHIVE_DIR="${ARCHIVE_DIR:-/archive}"
RETENTION_DAYS=30

# Create archive directory if not exists
mkdir -p "$ARCHIVE_DIR"

# Generate archive filename
DATE=$(date +%Y%m%d)
ARCHIVE_FILE="$ARCHIVE_DIR/mm-logs-$DATE.jsonl.gz"

echo "Starting archive rotation..."
echo "Archive: $ARCHIVE_FILE"

# Dump records older than RETENTION_DAYS to JSONL format
sqlite3 "$DB_PATH" <<EOF | gzip > "$ARCHIVE_FILE"
.mode json
SELECT * FROM experience_records
WHERE timestamp < datetime('now', '-$RETENTION_DAYS days');
EOF

echo "Archived $(zcat "$ARCHIVE_FILE" | wc -l) records"

# Delete archived records from database
sqlite3 "$DB_PATH" <<EOF
DELETE FROM experience_records
WHERE timestamp < datetime('now', '-$RETENTION_DAYS days');
EOF

DELETED=$(sqlite3 "$DB_PATH" "SELECT changes()")
echo "Deleted $DELETED records from database"

# Vacuum database to reclaim space
sqlite3 "$DB_PATH" "VACUUM;"

echo "Archive rotation complete!"
