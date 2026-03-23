# Moment 2 — Before plan-phase

**When:** Before `/gsd:plan-phase N` — you're about to plan a specific phase.

**Goal:** Domain brains inject expert knowledge into the CONTEXT.md **before** tasks and acceptance criteria are written. The plan should reflect expert decisions, not discover them mid-execution.

---

## Step 1 — Read Everything First

```bash
cat .planning/BRAIN-FEED.md                          # codebase reality
cat .planning/STATE.md                               # current position
cat .planning/phases/NN-name/NN-CONTEXT.md 2>/dev/null  # if discuss-phase ran already

# Read code relevant to this phase's domain:
# Frontend phase: stores, existing components, hooks
# Backend phase: existing routes, models, schemas
# WS/realtime: wsDispatcher, brainStore
```

Key information to extract:
- What patterns are already implemented (prevent re-inventing)
- What dependencies exist (APIs, stores, types)
- What constraints apply (performance, security, accessibility)

---

## Step 2 — Select Brains (use `references/brain-selection.md`)

Match phase domain to brains:

| Phase type | Primary brains | Always add |
|-----------|---------------|-----------|
| Frontend UI/UX heavy | #2 UX + #3 UI + #4 Frontend | #6 QA |
| Frontend state/perf | #4 Frontend | #6 QA |
| Backend API | #5 Backend | #6 QA |
| Full stack feature | #4 + #5 | #2 or #3 if UI matters, #6 |
| Infra/testing | #6 QA | — |

**Brain #7 is Moment 3.** Don't query #7 here unless you need early risk assessment.

---

## Step 3 — Build [IMPLEMENTED REALITY] Block

From `BRAIN-FEED.md` and code reading, extract what's relevant to this phase:

```
[IMPLEMENTED REALITY]
Stack: [relevant subset — not everything]

[What already exists that this phase builds on:]
- [Component/store/API already implemented]
- [Pattern proven: e.g., RAF batching, useBrainState(id)]
- [Library available: e.g., @xyflow/react v12, dagre, DOMPurify]

[Dependencies this phase needs from prior phases:]
- [API endpoint: GET /api/brains — exists, returns BrainConfig[]]
- [Store: brainStore with Map<brainId, BrainState> + Immer]
```

---

## Step 4 — Build [CORRECTED ASSUMPTIONS] Block

What will each brain likely assume wrong?

```
[CORRECTED ASSUMPTIONS]
❌ "[Brain assumption]" → ✅ "[Reality from code]"

Examples for Frontend brain:
❌ "React Compiler available" → ✅ DISABLED — conflicts with React.memo on React Flow nodes
❌ "NODE_TYPES can be inline" → ✅ MUST be module-level — infinite re-render otherwise
❌ "dagre recalculates on updates" → ✅ runs ONCE, positions locked in Zustand
```

---

## Step 5 — Query Brains in Parallel

Use MCP directly for speed. Same `[IMPLEMENTED REALITY]` block to all brains. Different `[WHAT I NEED]`.

```python
# Example for a frontend-heavy phase:

# Brain #2 UX (ea006ece-00a9-4d5c-91f5-012b8b712936)
query_ux = """
[IMPLEMENTED REALITY]
...

[CORRECTED ASSUMPTIONS]
...

[WHAT I NEED]
This phase builds [component/feature].
User flow: [describe user journey]
Specific UX questions:
1. [Concrete interaction decision]
2. [State feedback — what user sees during X]
3. [Edge cases — what happens when Y fails]
No generic UX theory. Specific decisions for this component.
"""

# Brain #3 UI (8d544475-6860-4cd7-9037-8549325493dd)
query_ui = """
[IMPLEMENTED REALITY]
...

[WHAT I NEED]
Visual design decisions for [component]:
1. State differentiation: [active/idle/error/complete] — how to visually distinguish them?
   Note: 8% of users are colorblind — never rely on color alone.
2. Animation: which states warrant animation? What duration? Tailwind 4 classes?
3. Accessibility: WCAG requirements for this type of component?
Give me CSS tokens, class names, Lucide icon names — not theory.
"""

# Brain #4 Frontend (85e47142-0a65-41d9-9848-49b8b5d2db33)
query_fe = """
[IMPLEMENTED REALITY]
...

[CORRECTED ASSUMPTIONS]
...

[WHAT I NEED]
Architecture decisions for [component]:
1. Component hierarchy: what's the right split?
2. State: what lives in Zustand vs local state vs TanStack Query?
3. Performance: any 60fps concerns given [specific interaction]?
4. Testing: what's the hardest part to test here?
Specific to Next.js 16 App Router + React 19 + @xyflow/react v12.
```

---

## Step 6 — Filter Each Response

For every recommendation:

```bash
# Example verification:
grep -r "AlertTriangle" apps/web/src/  # Does the icon exist?
grep -r "animate-pulse" apps/web/src/  # Is pulse already used?
grep "NODE_TYPES" apps/web/src/components/  # Is the pattern followed?
```

| Concern | Action |
|---------|--------|
| Library suggested that's not installed | Check package.json — add to phase plan if needed |
| Pattern suggested that already exists | Mark ✅ — skip, just reference it |
| Design decision that contradicts existing system | Flag — must align with design tokens |
| Real new insight | → Step 7 |

---

## Step 7 — Synthesize into CONTEXT.md

Write `.planning/phases/NN-name/NN-CONTEXT.md`:

```markdown
# Phase [N] — [Name] Context

## Expert Brain Synthesis

### UX Decisions (Brain #2)
- [Concrete decision 1]
- [Concrete decision 2]

### Visual Design (Brain #3)
- [Color token: --color-X for state Y]
- [Animation: X ms, only for Z state]
- [Accessibility: always icon + color, never color alone]

### Frontend Architecture (Brain #4)
- [Component hierarchy]
- [State ownership]
- [Performance invariants]

### QA Coverage (Brain #6)
- [What to test and how]
- [Edge cases to cover]

## Non-Negotiables
[Hard rules that PLAN.md tasks must follow]

## Deferred
[What brains suggested that we're deferring to Phase N+1]
```

---

## Done When

- [ ] BRAIN-FEED.md read before querying
- [ ] Code relevant to phase read
- [ ] All domain brains queried with [IMPLEMENTED REALITY] block
- [ ] Each insight verified against codebase (✅ / 📅 / 🔴)
- [ ] CONTEXT.md written with concrete implementation decisions
- [ ] `/gsd:plan-phase N` will now produce plans that reflect expert knowledge
