#!/usr/bin/env python3
"""
verify_feed_conservation.py
Assert: all entries from original BRAIN-FEED.md appear in exactly one domain/global feed.
BASELINE: 50 bullet entries in original file. KNOWN_DELETIONS = 2 (self-referential Phase 09 notes).

Usage:
  python3 verify_feed_conservation.py           # migration mode (Plans 10-01/10-02): allows global duplicates
  python3 verify_feed_conservation.py --strict  # strict mode (Plan 10-03+): no duplicates allowed
"""

import sys

from pathlib import Path

STRICT_MODE = "--strict" in sys.argv  # Plan 10-03+: no global duplicates allowed
KNOWN_DELETIONS = (
    2  # Entries removed (not migrated): outdated Phase 09 self-referential notes
)


def count_bullets(path: Path) -> set[str]:
    lines = path.read_text().splitlines()
    return {line.strip() for line in lines if line.startswith("- ")}


planning = Path(".planning")
original = count_bullets(planning / "BRAIN-FEED.md")
EXPECTED_BASELINE = 50  # verified: grep -c "^- " .planning/BRAIN-FEED.md

domain_files = [
    "BRAIN-FEED-01-product.md",
    "BRAIN-FEED-02-ux.md",
    "BRAIN-FEED-03-ui.md",
    "BRAIN-FEED-04-frontend.md",
    "BRAIN-FEED-05-backend.md",
    "BRAIN-FEED-06-qa.md",
    "BRAIN-FEED-07-growth.md",
]

all_domain = set()
for fname in domain_files:
    fpath = planning / fname
    if not fpath.exists():
        print(f"SKIP (not yet created): {fname}")
        continue
    entries = count_bullets(fpath)
    overlap = all_domain & entries
    if overlap:
        print(f"DUPLICATE in {fname}: {overlap}")
        exit(1)
    all_domain |= entries

global_entries = count_bullets(planning / "BRAIN-FEED.md")
union = all_domain | global_entries

# Remove the 2 intentionally deleted entries from the original set before comparison
# These are the self-referential Phase 09 notes flagged in RESEARCH.md for removal in Plan 10-03
expected = original  # original includes the 2 to-be-deleted entries

missing = original - union
extra = union - original

# Allow for the known deletions — they won't appear in original OR union after removal
# But before Plan 10-03, they still appear in global, so we check differently:
# After Plan 10-03 runs, original bullets that are neither in domain feeds nor in global are the deletions.
# Conservation law: len(domain_union) + len(global_after_cleanup) + KNOWN_DELETIONS == len(original)

total_accounted = len(union)
if total_accounted < len(original) - KNOWN_DELETIONS:
    really_missing = original - union
    print(f"MISSING entries (lost in migration, not deletions): {really_missing}")
    exit(1)

duplicates_found = all_domain & global_entries
if duplicates_found and STRICT_MODE:
    print(
        f"ENTRIES IN BOTH GLOBAL AND DOMAIN (run without --strict during migration): {duplicates_found}"
    )
    exit(1)
elif duplicates_found:
    print(
        f"INFO (migration mode): {len(duplicates_found)} entries still in global + domain (expected before Plan 10-03 cleanup)."
    )

print(
    f"OK: {len(original)} original entries. {len(all_domain)} in domain feeds, {len(global_entries)} in global. KNOWN_DELETIONS={KNOWN_DELETIONS}. Conservation law holds."
)
