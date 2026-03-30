---
plan: "12-04"
phase: "12-parallel-dispatch-command-update"
status: complete
wave: 2
completed_at: "2026-03-30"
---

# Plan 12-04 Summary — 7× ask-[domain].md Migration

## What Was Built

All 7 `ask-*.md` commands migrated from MCP manual to Agent dispatch via Task():

| File | Brain | Special |
|------|-------|---------|
| ask-product.md | brain-01-product | standard |
| ask-ux.md | brain-02-ux | standard |
| ask-design.md | brain-03-ui | standard |
| ask-backend.md | brain-05-backend | standard |
| ask-qa.md | brain-06-qa | standard |
| ask-frontend.md | brain-04-frontend | Phase A SYNC resolution (BF-05 fragments) |
| ask-growth.md | brain-07-growth | single-domain dispatch (no barrier/evaluator mode) |

## Verification

```
grep -rl "mcp__notebooklm-mcp__notebook_query" .claude/commands/mm/ | wc -l → 0
grep -c "brain-04-frontend" .claude/commands/mm/ask-frontend.md → 1
grep -c "brain-07-growth" .claude/commands/mm/ask-growth.md → 1
pytest tests/brain_agents/ → 2 static GREEN, stubs RED (expected)
```

## Self-Check: PASSED
