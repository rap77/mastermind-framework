# Moment 2 — Before plan-phase

**When:** Before `/gsd:plan-phase N` or `/mm:plan-phase N` — you're about to plan a specific phase.

**Goal:** Domain brains inject expert knowledge into the CONTEXT.md **before** tasks and acceptance criteria are written. The plan should reflect expert decisions, not discover them mid-execution.

**Architecture post-Phase 12:** Parallel Agent dispatch. Domain brains fire simultaneously. Brain #7 evaluates after. Uses Option D (file-based) for cross-brain communication — orchestrator stays thin.

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

## Step 5 — Parallel Domain Dispatch

**Dispatch all domain brains SIMULTANEOUSLY in a SINGLE orchestrator message.**

Use the `Agent` tool for each brain. All calls in one response. Do NOT dispatch Brain #7 yet.

```
Agents to dispatch simultaneously (one message):
- brain-01-product — prompt: [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [user question] + [WHAT I NEED: product/strategy perspective]
- brain-02-ux      — prompt: [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [user question] + [WHAT I NEED: UX perspective]
- brain-03-ui      — prompt: [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [user question] + [WHAT I NEED: visual/design perspective]
- brain-04-frontend — prompt: [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [user question] + [WHAT I NEED: frontend architecture perspective]
- brain-05-backend  — prompt: [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [user question] + [WHAT I NEED: backend/API perspective]
- brain-06-qa       — prompt: [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [user question] + [WHAT I NEED: QA/testing/reliability perspective]
```

**IMPORTANT:** Each brain agent is AUTONOMOUS. It reads its own `BRAIN-FEED-NN-domain.md` and global `BRAIN-FEED.md` before querying NotebookLM. You do NOT need to manually resolve SYNC tags or inject domain feed content — the agents handle this internally.

Wait for ALL 6 to return before proceeding to Step 5.5.

**Acceptance signal:** Claude Code UI shows multiple simultaneous "thinking" indicators (not one-at-a-time sequential).

**Anti-pattern:** Dispatching Brain #1, getting response, then Brain #2. Total time would equal Sum instead of Max. This is WRONG.

---

## Step 5.5 — Write Domain Outputs to NN-BRAIN-OUTPUTS.md (Option D)

After ALL domain agents return, write their outputs to the phase directory. This is the file-based communication channel for Brain #7.

Write to `.planning/phases/NN-name/NN-BRAIN-OUTPUTS.md`:

```markdown
# Phase NN — Domain Brain Outputs

> Generated: [ISO timestamp]
> Phase: NN - [phase-name]
> Purpose: Cross-domain input for Brain #7 evaluation
> Status: complete | partial (if any brain failed)

---

## Brain #1 — Product Strategy
<!-- Source: brain-01-product agent dispatch -->

[Full structured output from brain-01-product]

## Brain #2 — UX Research
<!-- Source: brain-02-ux agent dispatch -->

[Full structured output]

## Brain #3 — UI Design
<!-- Source: brain-03-ui agent dispatch -->

[Full structured output]

## Brain #4 — Frontend
<!-- Source: brain-04-frontend agent dispatch -->

[Full structured output]

## Brain #5 — Backend
<!-- Source: brain-05-backend agent dispatch -->

[Full structured output]

## Brain #6 — QA/DevOps
<!-- Source: brain-06-qa agent dispatch -->

[Full structured output]

---

## Dispatch Meta

| Property | Value |
|----------|-------|
| Total brains dispatched | 6 |
| All returned successfully | yes/no |
| Brains with Rating 1-2 | [list or "none"] |
| Total dispatch time | [approximate] |

<!-- This file is consumed by Brain #7 (brain-07-growth) -->
<!-- Brain #7: read this file as part of your evaluation protocol -->
<!-- Orchestrator: do NOT copy these outputs into Brain #7's prompt -->
```

**Why:** The orchestrator does NOT carry these outputs in conversation context. Brain #7 reads the file directly. This keeps the orchestrator thin.

---

## Step 6 — Brain #7 Barrier (Option D: File-Based)

Only after ALL domain agents have returned AND `NN-BRAIN-OUTPUTS.md` has been written, dispatch `brain-07-growth`:

```
Agent(
    subagent_type="brain-07-growth",
    prompt="[IMPLEMENTED REALITY block from Step 3]

[CORRECTED ASSUMPTIONS block from Step 4]

[IMPORTANT: Read .planning/phases/NN-name/NN-BRAIN-OUTPUTS.md before evaluating]
That file contains all 6 domain brain outputs. Read it as your cross-domain context.
Do NOT re-query domain feeds independently — work from what the file contains.

[ANTI-MEDIOCRE CONSTRAINT]
Do NOT reconcile contradictions. Name the conflict. Pick the strongest expert position.
Mediocre synthesis is worse than no synthesis.

[WHAT I NEED]
Evaluate these 6 domain outputs using your Systems Thinker lens. Return your standard 5-section output:
1. Domain Summary — what each brain produced (brief, 1 line each)
2. Second-Order Effects — what the combined plan will cause downstream
3. Systemic Metric — specific SLI/OKR that would detect if the consensus is going wrong
4. Cascade Risk — which dependency, if it fails, causes the most damage
5. Verdict — APPROVED | APPROVED_WITH_CONDITIONS | REJECTED_REVISE

Global Rating (0-100): overall health of this dispatch
Delta-Velocity vs Phase 09 baselines (target 3.5-4.5)"
)
```

Brain #7 reads the file as part of its protocol.
Orchestrator receives only the verdict — context stays lean.

---

## Step 7 — Filter Each Response

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
| Real new insight | → Step 8 |

---

## Step 8 — Synthesize into CONTEXT.md

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

- [ ] BRAIN-FEED.md + all domain feeds read before dispatch
- [ ] Code relevant to phase read
- [ ] All domain brains dispatched in ONE orchestrator message (no SYNC resolution needed)
- [ ] All domain brains returned
- [ ] `NN-BRAIN-OUTPUTS.md` written with all domain brain outputs (Option D)
- [ ] brain-07-growth dispatched with file reference (not inline outputs)
- [ ] Brain #7 verdict received (APPROVED / APPROVED_WITH_CONDITIONS / REJECTED_REVISE)
- [ ] Each insight verified against codebase (✅ / 📅 / 🔴)
- [ ] CONTEXT.md written with concrete implementation decisions
- [ ] `/gsd:plan-phase N` will now produce plans that reflect expert knowledge
