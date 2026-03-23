# Moment 3 — After PLAN.md, Before Execute

**When:** After `/gsd:plan-phase N` generates PLAN.md files. Brain-07 validates the plan with full code context before execution starts.

**Goal:** Brain-07 is the critical evaluator — finds blind spots, Planning Fallacy risks, and missing requirements BEFORE any code is written. One good pre-execution review > five mid-execution pivots.

---

## Step 1 — Read the Plans and the Code They Reference

```bash
# Read all plans for this phase
cat .planning/phases/NN-name/NN-01-PLAN.md
cat .planning/phases/NN-name/NN-02-PLAN.md
cat .planning/phases/NN-name/NN-03-PLAN.md   # if exists

# Read code files referenced in "files_modified" sections
# Typically for v2.1: brainStore, WS dispatcher, relevant components
cat apps/web/src/stores/brainStore.ts
cat apps/web/src/stores/wsDispatcher.ts

# Read BRAIN-FEED.md
cat .planning/BRAIN-FEED.md
```

Critical: **Read the actual code, not just the plan descriptions.** Brain-07 first run without code context = generic response. Brain-07 with RAF batching reality + actual activation pattern = surgical, actionable evaluation.

> Lesson from Phase 07: First Brain-07 query (plan text only) → generic concerns.
> Second Brain-07 query (with real brainStore code + activation behavior) → APROBADO with 2 specific gaps.

---

## Step 2 — Build the Full Context Block

This is the most important context block in the entire workflow. Include:

```
Project: MasterMind Framework — Phase [N]: [Name]
Stack: Next.js 16 + React 19 + TypeScript + Tailwind 4 + Zustand 5 + Immer + TanStack Query v5

[IMPLEMENTED REALITY]
[Paste key patterns from BRAIN-FEED.md relevant to this phase]
[Include actual code snippets for critical patterns, e.g.:]

brainStore.ts uses RAF batching:
  scheduleRafUpdate() → queues events → drains before paint → maintains 60fps

Actual activation pattern: 3-5 brains fire per brief (not 24 simultaneously).
WS message sequence: task_started → brain_activated (3-5x) → brain_completed (3-5x) → task_completed

[PLAN SUMMARY]
Plan NN-01: [Objective in 1 sentence] | Tasks: [N] | Key: [most important thing it does]
Plan NN-02: [Objective in 1 sentence] | Tasks: [N] | Key: [most important thing it does]
Plan NN-03: [Objective in 1 sentence] | Tasks: [N] | Key: [most important thing it does]

[CORRECTED ASSUMPTIONS]
❌ "[What Brain-07 might assume]" → ✅ "[What's actually true]"
[Include assumptions that would lead to wrong evaluation]

[WHAT I NEED]
Evaluate these 3 plans with your critical lens:

1. **Planning Fallacy check:** What are we underestimating? What takes 3x longer in reality?
2. **Omission Bias:** What's missing that will block execution?
3. **Systems Thinking:** What feedback loops between plans could cause problems?
4. **Over-engineering risk:** What are we building that won't be used?
5. **Acceptance criteria quality:** Are the done criteria verifiable?

Be specific about WHICH plan and WHICH task. No generic advice.
Give a verdict: APPROVED, APPROVED_WITH_CONDITIONS, or REJECTED_REVISE.
```

---

## Step 3 — Query Brain #7

```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="d8de74d6-7028-44ed-b4d4-784d6a9256e6",
    query="[Full context block from Step 2]"
)

# Or via CLI:
# uv run python -m mastermind_cli brain ask 7 "..." --use-mcp
```

---

## Step 4 — Filter the Response

For each concern or gap Brain-07 raises:

```bash
# Verify each concern against code:
grep -r "NexusSkeleton" apps/web/src/     # does it exist?
grep -r "reconnecting" apps/web/src/      # is reconnect state handled?
grep "historyStack" apps/web/src/stores/  # is Ghost Trace in brainStore?
```

| Brain-07 verdict | Action |
|-----------------|--------|
| APPROVED | Proceed to `/gsd:execute-phase N` |
| APPROVED_WITH_CONDITIONS | Fix conditions in PLAN.md, then execute |
| REJECTED_REVISE | Identify which plans need revision, consult domain brains |

For each concern:

| If concern... | Action |
|--------------|--------|
| Already implemented (grep confirms) | Mark ✅ — note in evaluation doc |
| Belongs to Phase N+1 (too much scope) | Mark 📅 — document as deferred |
| Real gap blocking execution | Mark 🔴 → Step 5 |

---

## Step 5 — Cascade Real Gaps to Domain Brains

Real gaps mean: something that will cause the plan to fail if not addressed before execution.

For each 🔴 gap:
1. Identify which domain brain knows best (see `references/brain-selection.md`)
2. Query that brain with the SAME `[IMPLEMENTED REALITY]` block + specific gap description
3. Get concrete implementation — specific CSS tokens, component structure, code pattern
4. Update the affected PLAN.md task with the concrete change

Example cascade from Phase 07:
```
🔴 Gap: NexusSkeleton needs "Reconectando..." banner when WS disconnects
→ Brain #2 UX: progressive status disclosure for disconnected state
→ Brain #4 Frontend: which store state to key off (wsDispatcher.status)
→ Updated 07-03-PLAN.md Task 1 with concrete acceptance criteria
```

---

## Step 6 — Update PLAN.md Files

For each real gap addressed:

```bash
# Edit the specific task in the affected PLAN.md
# Add to acceptance criteria or update task description
# Be specific: "NexusSkeleton shows 'Reconnecting...' banner when wsDispatcher.status === 'reconnecting'"
```

---

## Step 7 — Request Second Opinion (If Needed)

If Brain-07 raised concerns that you addressed via code changes (APPROVED_WITH_CONDITIONS):

Query Brain-07 again with:
```
[ORIGINAL CONTEXT BLOCK]

[CHANGES MADE]
Gap 1: [description] → Fixed in Plan NN-02, Task 2:
  - [what was added to acceptance criteria]
  - [code change or pattern added]

Gap 2: [description] → Fixed in Plan NN-03, Task 1:
  - [specific change]

Request: Confirm gaps are addressed. Approve or flag remaining issues.
```

---

## Done When

- [ ] All PLAN.md files read
- [ ] Code files referenced in plans read
- [ ] Brain-07 queried with [IMPLEMENTED REALITY] block (not just plan text)
- [ ] Each concern filtered (✅ / 📅 / 🔴)
- [ ] Real gaps cascaded to domain brains
- [ ] PLAN.md files updated with gap fixes
- [ ] Brain-07 verdict: APPROVED or APPROVED_WITH_CONDITIONS resolved
- [ ] Ready for `/gsd:execute-phase N`
