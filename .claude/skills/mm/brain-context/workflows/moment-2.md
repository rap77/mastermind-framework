# Moment 2 — Before plan-phase

**When:** Before `/gsd:plan-phase N` — you're about to plan a specific phase.

**Goal:** Domain brains inject expert knowledge into the CONTEXT.md **before** tasks and acceptance criteria are written. The plan should reflect expert decisions, not discover them mid-execution.

**Architecture post-Phase 12:** Parallel Agent dispatch replaces manual MCP. All 6 domain brains fire simultaneously. Brain #7 evaluates after. Total time ≈ Max(T_brain_1..6) + T_brain_7 (~90-110s).

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

## Step 5 — Phase A: SYNC Tag Resolution (Pre-Dispatch)

Before dispatching any agent, resolve SYNC tags inline.

**SYNC tag format:** `[SYNC: BF-NN-ID]` — points to a section in `BRAIN-FEED-NN-domain.md`.

For each domain brain that will be dispatched:
1. Read that brain's domain feed (`.planning/BRAIN-FEED-NN-domain.md`)
2. Scan for `[SYNC: BF-NN-ID]` tags using pattern `\[SYNC:\s+BF-(\d{2})-(\w+)\]`
3. For each tag found:
   a. Open the OWNER feed: `.planning/BRAIN-FEED-{NN}-{domain}.md` (NN from the tag)
   b. Extract ONLY the referenced section (search for the section ID in the owner feed)
   c. Store as: `"INJECTED FROM BRAIN-FEED-{NN}: [extracted text]"`
4. If a referenced section is NOT found in the owner feed: log a visible warning and continue without injection. Never block dispatch.

**Cross-talk rule (CRITICAL):** Each brain's prompt gets ONLY its own SYNC fragments. Brain #4's prompt gets BF-05 fragments only. Brain #1's prompt gets NO fragments unless it has its own SYNC tags. Build a per-brain injection map — zero cross-agent leakage.

Known SYNC tags as of Phase 10:
- Brain #4 Frontend: 4 tags → all point to `BRAIN-FEED-05-backend.md`
- All other brains: 0 SYNC tags (no injection needed)

---

## Step 6 — Phase B: Parallel Domain Dispatch

**Dispatch all 6 domain brains SIMULTANEOUSLY in a SINGLE orchestrator message.**

Use the `Task` tool (Agent dispatch) for each brain. All 6 calls in one response. Do NOT dispatch Brain #7 yet.

```
Agents to dispatch simultaneously (one message):
- brain-01-product — prompt: [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [user question] + [WHAT I NEED: product/strategy perspective]
- brain-02-ux      — prompt: [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [user question] + [WHAT I NEED: UX perspective]
- brain-03-ui      — prompt: [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [user question] + [WHAT I NEED: visual/design perspective]
- brain-04-frontend — prompt: [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [INJECTED FROM BRAIN-FEED-05: resolved BF-05 fragments] + [user question] + [WHAT I NEED: frontend architecture perspective]
- brain-05-backend  — prompt: [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [user question] + [WHAT I NEED: backend/API perspective]
- brain-06-qa       — prompt: [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [user question] + [WHAT I NEED: QA/testing/reliability perspective]
```

Wait for ALL 6 to return before proceeding to Phase C.

**Acceptance signal:** Claude Code UI shows multiple simultaneous "thinking" indicators (not one-at-a-time sequential).

**Anti-pattern:** Dispatching Brain #1, getting response, then Brain #2. Total time would equal Sum instead of Max. This is WRONG. Total time target: < 120s (≈ Max(T_1..6) + T_7).

---

## Step 7 — Phase C: Brain #7 Barrier (Only After Phase B Completes)

Only after ALL 6 domain agents have returned their outputs, dispatch `brain-07-growth`:

```
[CROSS-DOMAIN CONTEXT — paste actual outputs from Phase B]
Brain #1 Product Strategy output:
[paste brain-01-product return value]

Brain #2 UX Research output:
[paste brain-02-ux return value]

Brain #3 UI Design output:
[paste brain-03-ui return value]

Brain #4 Frontend output:
[paste brain-04-frontend return value]

Brain #5 Backend output:
[paste brain-05-backend return value]

Brain #6 QA/DevOps output:
[paste brain-06-qa return value]

[ANTI-MEDIOCRE CONSTRAINT]
Do NOT reconcile contradictions. Name the conflict. Pick the strongest expert position.
Mediocre synthesis is worse than no synthesis.
If Brain #4 and Brain #5 disagree on an API contract: name the disagreement and pick the technically stronger position. Do not average.

[WHAT I NEED]
Evaluate these 6 domain outputs using your Systems Thinker lens. Return your standard 5-section output:
1. Domain Summary — what each brain produced (brief, 1 line each)
2. Second-Order Effects — what the combined plan will cause downstream
3. Systemic Metric — specific SLI/OKR that would detect if the consensus is going wrong
4. Cascade Risk — which dependency, if it fails, causes the most damage
5. Verdict — APPROVED | APPROVED_WITH_CONDITIONS | REJECTED_REVISE
   If conditions: list them specifically (which plan, which task, what must change)

Global Rating (0-100): overall health of this dispatch
Brain Alerts: any domain agent output that looks like Rating 1 or 2 (corrupted/generic)
Delta-Velocity vs Phase 09 baselines (target 3.5-4.5)
Human-review flags: cross-domain patterns worth adding to global BRAIN-FEED.md (flag only — do NOT write)
```

Brain #7 fires AFTER Phase B. Never in the same message as domain agents.

---

## Step 8 — Filter Each Response

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

## Step 9 — Synthesize into CONTEXT.md

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
- [ ] Phase A: SYNC tags detected and resolved per-brain (Brain #4 gets BF-05 fragments only)
- [ ] Phase B: All 6 domain brains dispatched in ONE orchestrator message
- [ ] Phase B: All 6 returns received before Phase C begins
- [ ] Phase C: brain-07-growth dispatched with 6 domain outputs as context
- [ ] Brain #7 verdict received (APPROVED / APPROVED_WITH_CONDITIONS / REJECTED_REVISE)
- [ ] Each insight verified against codebase (✅ / 📅 / 🔴)
- [ ] CONTEXT.md written with concrete implementation decisions
- [ ] `/gsd:plan-phase N` will now produce plans that reflect expert knowledge
