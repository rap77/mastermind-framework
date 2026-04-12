# Brain #4 Citation Architecture Fix

**Date:** 2026-03-29
**Context:** Phase 11 smoke test — adversarial npm prompt

## Problem
Brain #04-frontend rejected npm correctly but cited CLAUDE.md instead of `global-protocol.md > Stack Hard-Lock`. Two runs both Rating 2 Silver (FAIL).

## Root Cause
1. Protocol section read BRAIN-FEED files but NOT global-protocol.md explicitly
2. Agent has `model: inherit` → CLAUDE.md persona loaded first with pnpm knowledge → natural fallback
3. Output Format section had no mandatory citation block for violations

## Fix Applied (2 commits)
**f944a0d** — brain-04-frontend.md + criteria.md:
- Added `cat .claude/agents/mm/global-protocol.md` to mandatory pre-read list in Protocol
- Added citation rule: "Any Stack Hard-Lock violation MUST be cited as `Source: global-protocol.md > Stack Hard-Lock`"
- Added Auto-Reject condition for npm/yarn to criteria.md with exact rejection format

**588d5b4** — brain-04-frontend.md Output Format:
- Added `## Stack Violation Response (MANDATORY FORMAT)` section BEFORE standard format
- Template: `[STACK VIOLATION DETECTED]` block with Violation/Rejected/Source fields
- Verbatim example included so model has zero ambiguity

## Pattern for Other Brains
If other brains (#5, #6, etc.) show same citation issue:
1. Add global-protocol.md to mandatory pre-read in their Protocol section
2. Add [STACK VIOLATION DETECTED] block to their Output Format
3. Match the exact format from brain-04-frontend.md Output Format section

## Sentinel Script Note
Sentinel PASS on all runs — feed isolation was working correctly throughout. The fix is purely about citation FORMAT, not about constraint enforcement.
