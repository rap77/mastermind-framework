---
description: Capture and critically evaluate ideas with MasterMind brain consultation. Evaluates proposals against MasterMind v3.0 context, classifies by priority, saves to .planning/proposals/ with individual brain opinions and revision history. Includes iterative clarification (max 3 iterations) to reach unconditional approval.
argument-hint: "[your idea or observation about improvement opportunity, feature, or concern]"
---

# /mm:propose

Capture any idea, improvement opportunity, or feature proposal and get critical evaluation from MasterMind's expert brains.

## Usage

```bash
/mm:propose "Your idea or observation"

# Re-evaluate existing proposal with new information
/mm:propose --revisar PROP-001 "Nueva información sobre la propuesta"
```

## Examples

```bash
# UX improvement discovered while testing
/mm:propose "El flow selector de Paperclip es confuso, no sé qué significa cada flow"

# Feature idea
/mm:propose "Sería bueno tener dark mode en toda la app"

# Performance concern
/mm:propose "El grid es lento con 100+ items, necesitamos Redis"
```

## What Happens (Iterative Process)

### Iteration 1: Initial Capture

1. **Clarification** — System asks context questions (UX vs performance vs feature vs architecture)
2. **Brain Consultation** — Relevant brains evaluate critically
3. **Classification** — Priority (P0-P3), category, effort estimated
4. **Conditional Approval** — If APPROVED with conditions → Go to Step 5
   - If REJECTED → Save to proposals/ as rejected
   - If CONDITIONAL → Go to Step 4 (Clarification)
5. **Save** — Stored in `.planning/proposals/PROP-XXX.md`

### Iterations 2-3: Clarification Loop (Max 3 iterations total)

If **CONDITIONAL APPROVAL** (conditions not met):

4. **Clarification Interview** — System conducts structured clarification interview
   - Focus: Resolve BLOCKERs identified by brains
   - Format: Adaptive questioning based on gaps found
   - Goal: Turn conditional → unconditional

5. **Re-evaluation** — Dispatch Brain #7 for meta-evaluation of revised proposal
   - Synthesizes all domain brain opinions
   - Checks if BLOCKERs resolved
   - Returns: APPROVED / REJECTED / DEFERRED / NEEDS_MORE_INFO

6. **Repeat** — If still conditional, conduct another clarification round
   - Max 3 iterations (prevents analysis paralysis)

### Iteration 4: Final Approval

Once **UNCONDITIONAL APPROVAL** is achieved (or APPROVED_WITH_CONDITIONS):

7. **Condition Categorization** — Classify conditions by type to determine next action

| Type | Color | Action | Example |
|------|-------|--------|---------|
| **ACLARACIÓN** | 🟡 | Ask user NOW, keep iterating | "¿Opción A o B?" |
| **ACCIÓN INDEPENDIENTE** | 🟢 | Can start NOW, doesn't block | "3 entrevistas Mom Test" |
| **DEPENDENCIA EXTERNA** | 🔴 | PENDING until dependency resolves | "Phase 15 must exist first" |
| **IMPLEMENTACIÓN** | 🔵 | Add to backlog of target phase | "Add metrics tracking" |

**Rules:**
- 🟡 Ask clarification questions → user responds → iterate if needed
- 🟢 User approves → mark as READY TO START
- 🔴 Add to proposal: "BLOCKED - Waiting for [dependency]" → retomar when resolved
- 🔵 Add to phase backlog → implement when phase starts

8. **Integration Planning** — Determine how proposal fits into roadmap
   - If UX/UI → Check if Phase 15/16 scope covers it or add to roadmap
   - If new feature → Create standalone PRP
   - If enhancement → Update existing plan
   - If rejected → Save with rationale and lessons learned

9. **Commit to Phase** — Add to implementation backlog

## Proposal States

- **DRAFT** — Newly created, not yet evaluated
- **UNDER_REVIEW** — Brains evaluated, may need more info
- **APPROVED** — Ready for integration (unconditional or with conditions resolved)
- **REJECTED** — Not aligned with v3.0 goals (with rationale)
- **DEFERRED** — Good idea, wrong timing (v4.0+)
- **IMPLEMENTED** — Built and deployed

## Brain Consultation Matrix

Based on proposal type, relevant brains are consulted:

| Type | Primary Brains | Meta-evaluator |
|------|----------------|---------------|
| UX/UI | #2 (UX Research) + #3 (UI Design) | #7 (Growth) |
| Performance | #5 (Backend) + #6 (QA/DevOps) | #7 (Growth) |
| Feature | #1 (Product) + #4 (Frontend) | #7 (Growth) |
| Architecture | #5 (Backend) + #7 (Growth) | #7 (Growth) |
| Business | #1 (Product) + #7 (Growth) | #7 (Growth) |
| General | #1 (Product) + #7 (Growth) | #7 (Growth) |

**Brain #7 ALWAYS does final meta-evaluation** and synthesizes all opinions.

## Critical Feedback Format

Each brain provides:

- ✅ **Lo Bueno** — Strengths of the idea
- ⚠️ **Lo Que Falta** — Gaps, missing data, unconsidered risks
- 🚨 **Peligros** — What can go wrong
- 💭 **Sugerencias** — How to improve

## Output Files

Proposals are saved to:
```
.planning/proposals/
├── PROP-001-ux-flow-selector.md
├── PROP-002-perf-redis-cache.md
├── PROP-003-feature-dark-mode.md
└── PROP-XXX-APPROVED.md (approved proposals)
```

Each file includes:
- YAML frontmatter (id, status, timestamps, brain_evaluations)
- Individual brain opinions (detailed)
- Final verdict with rationale
- Revision history (iterations, how blockers were resolved)
- Next actions

## Related Commands

- `/mm:ask-all` — Consult all 7 brains directly
- `/mm:ask-product` — Product strategy consultation
- `/mm:ask-ux` — UX research consultation
- `/mm:ask-backend` — Backend architecture consultation
