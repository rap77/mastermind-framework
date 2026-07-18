---
description: Activate the roadmap's recommended next MasterMind objective.
agent: build
---

Execute the MasterMind activation lifecycle from the repository root.

1. Run `uv run python .claude/commands/mm/activate-next-objective-handler.py $ARGUMENTS`.
2. Parse the handler output without manually editing planning state.
3. On `STATUS: PASSED`, report the activated objective and the exact `NEXT_COMMAND`.
4. On `STATUS: BLOCKED` or `STATUS: FAILED`, report the exact reason and next gate command.
5. Never activate a second objective when one is already active.
