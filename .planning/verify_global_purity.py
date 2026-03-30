#!/usr/bin/env python3
"""
verify_global_purity.py
Assert: global BRAIN-FEED.md contains zero domain-specific vocabulary
(excluding Stack table — word-boundary matching + skip table rows prevents false positives).
Verbose fail: line number + 2-line context. Silent pass = CI-friendly.
"""

import re
import sys
from pathlib import Path

DOMAIN_VOCAB = [
    r"\bZustand\b",
    r"\bImmer\b",
    r"\buseBrainState\b",
    r"\bRAF\b",
    r"\bNODE_TYPES\b",
    r"\bEDGE_TYPES\b",
    r"\bdagre\b",
    r"\bFastAPI\b",
    r"\bSQLAlchemy\b",
    r"\basyncio\b",
    r"\bpytest\b",
    r"\bpydantic\b",
    r"\bVitest\b",
    r"\buv run\b",
    r"\bTanStack\b",
    r"\bReact Flow\b",
    r"\b@xyflow\b",
]

feed = Path(".planning/BRAIN-FEED.md")
lines = feed.read_text().splitlines()
failures = []

for i, line in enumerate(lines):
    if line.strip().startswith("|"):  # skip table rows (Stack table exemption)
        continue
    for vocab_pattern in DOMAIN_VOCAB:
        if re.search(vocab_pattern, line, re.IGNORECASE):
            ctx_start = max(0, i - 1)
            ctx_end = min(len(lines), i + 2)
            failures.append(
                {
                    "line": i + 1,
                    "match": vocab_pattern,
                    "content": line,
                    "context": lines[ctx_start:ctx_end],
                }
            )
            break  # one report per line is enough

if failures:
    print(
        f"PURITY FAIL: {len(failures)} domain-vocabulary match(es) in global BRAIN-FEED.md\n"
    )
    for f in failures:
        print(f"  Line {f['line']}: {f['content']}")
        print(f"  Pattern: {f['match']}")
        print("  Context:")
        for ctx_line in f["context"]:
            print(f"    {ctx_line}")
        print()
    sys.exit(1)

# Silent pass — no output
