#!/usr/bin/env python3
"""
verify_feed_paths.py
Assert: every BRAIN-FEED-NN-domain.md path referenced in agent files exists on disk.
"""

import re
from pathlib import Path

agents_root = Path(".claude/agents/mm")
pattern = re.compile(r"BRAIN-FEED-\d{2}-[\w-]+\.md")
planning = Path(".planning")

referenced = set()
for md in agents_root.glob("**/*.md"):
    for match in pattern.findall(md.read_text()):
        referenced.add(match)

missing = []
for fname in referenced:
    if not (planning / fname).exists():
        missing.append(fname)

if missing:
    print(f"MISSING feed files referenced in agents: {missing}")
    exit(1)

print(f"OK: {len(referenced)} feed file references — all paths exist.")
