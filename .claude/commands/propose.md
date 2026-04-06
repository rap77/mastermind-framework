---
description: >
  Capture and critically evaluate ideas with MasterMind brain consultation.
  Evaluates proposals against MasterMind v3.0 context, classifies by priority,
  saves to .planning/proposals/ with individual brain opinions and revision history.
---

# /mm:propose

Capture any idea, improvement opportunity, or feature proposal and get critical evaluation from MasterMind's expert brains.

## Usage

```bash
/mm:propose "Your idea or observation"

# Re-evaluate existing proposal with new information
/mm:propose --revisar PROP-001

# List all proposals
/mm:propose --list

# View proposal details
/mm:propose --ver PROP-001
```

## Examples

```bash
# UX improvement discovered while testing Paperclip
/mm:propose "El flow selector de Paperclip es confuso, no sé qué significa cada flow"

# Feature idea
/mm:propose "Sería bueno tener dark mode en toda la app"

# Performance concern
/mm:propose "El grid es lento con 100+ items, necesitamos Redis"
```

## What Happens

1. **Clarification** — System asks context (UX/performance/feature/etc)
2. **Brain Consultation** — Relevant brains evaluate critically
3. **Classification** — Priority (P0-P3), category, effort estimated
4. **Save** — Stored in `.planning/proposals/PROP-XXX.md`
5. **Report** — You get critical feedback + disposition

## Proposal Workflow

```
DRAFT → UNDER_REVIEW → APPROVED → IMPLEMENTED
                    ↓
                 REJECTED / DEFERRED
```

## States

- **DRAFT** — Newly created, not yet evaluated
- **UNDER_REVIEW** — Brains evaluated, may need more info
- **APPROVED** — Approved for implementation
- **REJECTED** — Not aligned with v3.0 goals
- **DEFERRED** — Good idea, wrong timing (v4.0+)
- **IMPLEMENTED** — Built and deployed

## Brain Consultation

Based on proposal type, relevant brains are consulted:

| Type | Brains Consulted |
|------|------------------|
| UX/UI | #2 (UX Research) + #3 (UI Design) + #7 |
| Performance | #5 (Backend) + #6 (QA/DevOps) + #7 |
| Feature | #1 (Product) + #4 (Frontend) + #7 |
| Architecture | #5 (Backend) + #7 |
| Business | #1 (Product) + #7 |
| General | #1 (Product) + #7 |

**Brain #7 ALWAYS does final meta-evaluation** and synthesizes all opinions.

## Critical Feedback Format

Each brain provides:

- ✅ **Lo Bueno** — Strengths of the idea
- ⚠️ **Lo Que Falta** — Gaps, missing data, unconsidered risks
- 🚨 **Peligros** — What can go wrong
- 💭 **Sugerencias** — How to improve

## Output File

Proposals are saved to:
```
.planning/proposals/
├── PROP-001-ux-flow-selector.md
├── PROP-002-perf-redis-cache.md
└── PROP-003-feature-dark-mode.md
```

Each file includes:
- YAML frontmatter (id, status, timestamps, brain_evaluations)
- Individual brain opinions (detailed)
- Final verdict with rationale
- Revision history
- Next actions

## Related Commands

- `/mm:ask-all` — Consult all 7 brains directly
- `/mm:ask-product` — Product strategy consultation
- `/mm:ask-ux` — UX research consultation
- `/mm:ask-backend` — Backend architecture consultation
