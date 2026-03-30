---
phase: 09-baselines-agent-authoring
plan: "03"
subsystem: brain-agents
tags: [brain-bundle, ui-design, frontend, minimalist-nazi, performance-nazi, subagent-authoring]
dependency_graph:
  requires: [09-02]
  provides: [brain-03-ui bundle, brain-04-frontend bundle]
  affects: [Phase 11 smoke tests, Phase 12 dispatch wiring]
tech_stack:
  added: []
  patterns: [Brain Bundle pattern (agent + criteria + warnings), 6-step protocol as identity, [CORRECTED ASSUMPTIONS] verbatim embedding]
key_files:
  created:
    - .claude/agents/mm/brain-03-ui/brain-03-ui.md
    - .claude/agents/mm/brain-03-ui/criteria.md
    - .claude/agents/mm/brain-03-ui/warnings.md
    - .claude/agents/mm/brain-04-frontend/brain-04-frontend.md
    - .claude/agents/mm/brain-04-frontend/criteria.md
    - .claude/agents/mm/brain-04-frontend/warnings.md
  modified: []
decisions:
  - "Brain #3 persona: 'Remove it. Less is always more.' — subtraction bias drives all recommendations, not addition"
  - "Brain #3 5 domain-specific anti-patterns: Animation Inflation + Color-Only State + Tailwind Config Contamination + Component Bloat + Theme Scope Creep"
  - "Brain #4 gets 7 [CORRECTED ASSUMPTIONS] (4 from spec + 3 added): useStore() global, dagre locked, NODE_TYPES module-level — all verbatim from 09-RESEARCH.md"
  - "Brain #4 criteria.md: O(1) selector test is the observable signal distinguishing Rating 3 from Rating 4"
  - "Both agents: domain feed referenced in Step 1 + write constraint in Step 6 — FEED-02 and FEED-03 embedded as identity, not checklist"
  - "No notebook IDs embedded in either agent file — brain-selection.md is the single source of truth"
metrics:
  duration: "48 minutes"
  completed_date: "2026-03-28"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 6
---

# Phase 09 Plan 03: Brain Bundles #3 and #4 Summary

Brain Bundles #3 (UI Design — Minimalist Nazi) and #4 (Frontend Architecture — Performance Nazi) authored as self-contained 3-file directories with embedded 6-step intermediary protocol, domain-specific quality gates, and comprehensive anti-pattern rejection vocabulary.

## Files Created

| File | Description |
|------|-------------|
| `.claude/agents/mm/brain-03-ui/brain-03-ui.md` | Brain #3 subagent — Minimalist Nazi persona (Cooper/Wroblewski/Saffer), 6-step protocol as identity, 5 UI [CORRECTED ASSUMPTIONS], War Room panel context table |
| `.claude/agents/mm/brain-03-ui/criteria.md` | Brain #3 quality gate — Rating 3 vs 4 table (5 attributes), Animation Inflation auto-reject, Color-Only State blocker, Panel-Agnostic = Rating 2 max |
| `.claude/agents/mm/brain-03-ui/warnings.md` | Brain #3 anti-patterns — 4 universal poisoning patterns + 5 UI-specific (Animation Inflation, Color-Only State, Tailwind Config Contamination, Component Bloat, Theme Scope Creep) |
| `.claude/agents/mm/brain-04-frontend/brain-04-frontend.md` | Brain #4 subagent — Performance Nazi persona (Abramov/Markbåge/Kyle Simpson), 7 [CORRECTED ASSUMPTIONS] verbatim, additional frontend stack locks |
| `.claude/agents/mm/brain-04-frontend/criteria.md` | Brain #4 quality gate — Rating 3 vs 4 table (6 attributes), O(1) selector observable signal, 4 auto-reject conditions all at Rating 1 |
| `.claude/agents/mm/brain-04-frontend/warnings.md` | Brain #4 anti-patterns — 4 universal poisoning patterns + 5 frontend-specific (Global Selector, Compiler Assumption, Inline NODE_TYPES, Layout Drift, Redux Suggestion) |

## Key Authoring Decisions

### Brain #3: Subtraction as Primary Bias

The Minimalist Nazi persona was implemented with subtraction as the first response, not addition. The Output Format Section leads with "Removal Audit" before any design proposal — this enforces the persona's core principle at the structural level, not just in vocabulary.

The War Room panel context table was added to the agent (not specified in the plan) to ensure every design recommendation names the target panel. Without this, design advice is untargetable (Panel-Agnostic = Rating 2 max in criteria.md). This is a minor expansion within the spec's intent.

### Brain #4: 7 Corrected Assumptions (4 spec + 3 added)

The plan specified adding 3 corrections beyond the base 4. All 7 are embedded twice: once in the protocol section (where the agent builds the block) and once in the "Always Include" section (redundancy by design — ensures the block is never omitted). The O(1) selector test in criteria.md is named explicitly as the observable signal distinguishing Rating 3 from Rating 4.

### Both Agents: Protocol Embedded as Identity

The 6-step protocol follows the pattern established in Brain Bundles #1 and #2 (Plan 09-02): framed as "this is how you think," not "follow these steps." Step headers use first-person ("Before I Form Any Opinion…") to encode the protocol as identity, not checklist. The persona opening comes first, before any structure.

### Feed Paths Referenced but Not Created

Both agents reference `.planning/BRAIN-FEED-03-ui.md` and `.planning/BRAIN-FEED-04-frontend.md` in their Step 1 and Step 6 protocol steps. These files do not exist yet — Phase 10 creates them. This is correct per 09-RESEARCH.md (Pitfall 2: FEED-01 Scope Creep). No domain feed files were created in this plan.

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written.

### Minor Expansions (within spec intent)

**1. Brain #3: War Room Panel Context Table added**
- **Found during:** Task 1 authoring
- **Issue:** Without naming the target panel, UI recommendations are unverifiable (any design decision valid for Strategy Vault may be harmful for Command Center)
- **Fix:** Added "War Room Design Context" section with 4-panel table + rule "Any design suggestion without naming the target panel = incomplete recommendation"
- **Files modified:** `.claude/agents/mm/brain-03-ui/brain-03-ui.md`
- **Verdict:** Within spec intent — plan specified "design decisions must reference which panel is in scope" (line 158 of plan)

**2. Brain #4: "Always Include" section added**
- **Found during:** Task 2 authoring
- **Issue:** 7 corrections are easy to skip in practice without a dedicated "always include" block
- **Fix:** Added "Brain #4 Corrected Assumptions — Always Include" section with all 7 verbatim (matches Brain #1 pattern from Plan 09-02)
- **Files modified:** `.claude/agents/mm/brain-04-frontend/brain-04-frontend.md`
- **Verdict:** Pattern established in Plan 09-02; consistent across all bundles

## Verification Results

```
Total files created: 6 ✓
model: inherit in both agent files: 2 matches ✓
FEED-02 (global BRAIN-FEED.md referenced): 2 matches ✓
FEED-03 (domain feed paths): 2 matches ✓
React Compiler DISABLED correction in brain-04: present ✓
Rating 3 vs 4 table in both criteria.md files: 2 matches ✓
Universal poisoning patterns in warnings.md: 10 matches (>= 4 required) ✓
No notebook IDs embedded in agent files: confirmed ✓
No BRAIN-FEED-NN-domain.md files created: confirmed ✓
Backend regression suite: 575 passing ✓
Frontend regression suite: 407 passing ✓
```

## Self-Check: PASSED

All 6 files exist. Both task commits verified (449bb0e, 274dbe0). Regression suites green (575 + 407).
