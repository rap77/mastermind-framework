# Moment 3 — After PLAN.md, Before Execute

**When:** After `/gsd:plan-phase N` or `/mm:plan-phase N` generates PLAN.md files. Brain-07 validates the plan with full code context before execution starts.

**Goal:** Brain-07 is the critical evaluator — finds blind spots, Planning Fallacy risks, and missing requirements BEFORE any code is written. One good pre-execution review > five mid-execution pivots.

**Uses Option D (file-based):** Orchestrator writes context to `NN-PLAN-REVIEW.md`, Brain #7 reads the file. Orchestrator stays thin.

---

## Step 1 — Read the Plans and the Code They Reference

```bash
# Read all plans for this phase
cat .planning/phases/NN-name/NN-01-PLAN.md
cat .planning/phases/NN-name/NN-02-PLAN.md
cat .planning/phases/NN-name/NN-03-PLAN.md   # if exists

# Read code files referenced in "files_modified" sections
# Typically: brainStore, WS dispatcher, relevant components
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

## Step 3 — Write Context to NN-PLAN-REVIEW.md (Option D)

Write the full context block from Step 2 to a file for Brain #7 to read:

Write to `.planning/phases/NN-name/NN-PLAN-REVIEW.md`:

```markdown
# Phase NN — Plan Review Context

> Generated: [ISO timestamp]
> Purpose: Full context for Brain #7 plan validation
> Iteration: 1

---

[IMPLEMENTED REALITY]
[from Step 2 — paste full block]

[PLAN SUMMARY]
[from Step 2 — all plan objectives, tasks, acceptance criteria]

[CODE SNIPPETS]
[from Step 2 — actual code from files referenced in plans]

[CORRECTED ASSUMPTIONS]
[from Step 2]

[WHAT I NEED]
[from Step 2 — evaluation criteria]

<!-- This file is consumed by Brain #7 (brain-07-growth) -->
<!-- Brain #7: read this file as part of your evaluation protocol -->
<!-- Orchestrator: do NOT copy this content into Brain #7's prompt -->
```

---

## Step 4 — Dispatch brain-07-growth via Agent (Option D)

Dispatch `brain-07-growth` with a FILE REFERENCE, not inline context:

```
Agent(
    subagent_type="brain-07-growth",
    prompt="Read .planning/phases/NN-name/NN-PLAN-REVIEW.md before evaluating.
    That file contains the full plan context, code snippets, and evaluation criteria.

    Evaluate using your Systems Thinker lens.
    Return your standard 5-section output + verdict."
)
```

Brain #7 reads the file as part of its protocol.
The orchestrator receives only the verdict — context stays lean.

---

## Step 5 — Filter the Response

For each concern or gap Brain-07 raises:

```bash
# Verify each concern against code:
grep -r "NexusSkeleton" apps/web/src/     # does it exist?
grep -r "reconnecting" apps/web/src/      # is reconnect state handled?
grep "historyStack" apps/web/src/stores/  # is Ghost Trace in brainStore?
```

| Brain-07 verdict | Action |
|-----------------|--------|
| APPROVED | Proceed to `/gsd:execute-phase N` or `/mm:execute-phase N` |
| APPROVED_WITH_CONDITIONS | Fix conditions in PLAN.md, then execute |
| REJECTED_REVISE | Identify which plans need revision, consult domain brains |

For each concern:

| If concern... | Action |
|--------------|--------|
| Already implemented (grep confirms) | Mark ✅ — note in evaluation doc |
| Belongs to Phase N+1 (too much scope) | Mark 📅 — document as deferred |
| Real gap blocking execution | Mark 🔴 → Step 6 |

---

## Step 6 — Cascade Real Gaps to Domain Brains

Real gaps mean: something that will cause the plan to fail if not addressed before execution.

For each 🔴 gap:
1. Identify which domain brain knows best (see `references/brain-selection.md`)
2. Dispatch that brain with the SAME `[IMPLEMENTED REALITY]` block + specific gap description
3. Get concrete implementation — specific CSS tokens, component structure, code pattern
4. Update the affected PLAN.md task with the concrete change

Example cascade from Phase 07:
```
🔴 Gap: NexusSkeleton needs "Reconectando..." banner when WS disconnects
→ brain-02-ux: progressive status disclosure for disconnected state
→ brain-04-frontend: which store state to key off (wsDispatcher.status)
→ Updated 07-03-PLAN.md Task 1 with concrete acceptance criteria
```

---

## Step 7 — Update PLAN.md Files

For each real gap addressed:

```bash
# Edit the specific task in the affected PLAN.md
# Add to acceptance criteria or update task description
# Be specific: "NexusSkeleton shows 'Reconnecting...' banner when wsDispatcher.status === 'reconnecting'"
```

---

## Step 8 — Iteration Loop (Max 3)

Brain-07 raised concerns or returned APPROVED_WITH_CONDITIONS? Iterate until full approval.

**Update `NN-PLAN-REVIEW.md` with the delta** — don't create a new file, overwrite:

```markdown
# Phase NN — Plan Review Context

> Iteration: [N] of 3
> Previous verdict: [REJECTED_REVISE / APPROVED_WITH_CONDITIONS]

---

[ORIGINAL CONTEXT BLOCK — same as iteration 1]

[CAMBIOS REALIZADOS en iteración N]
Gap 1: [descripción] → Resuelto en Plan NN-02, Task 2:
  - [qué se agregó a acceptance criteria]
  - [patrón o cambio de código]

Gap 2: [descripción] → Resuelto en Plan NN-03, Task 1:
  - [cambio específico]

[GAPS PENDIENTES — si los hay]
- [gap X]: [por qué no se resolvió / está fuera de scope]
```

Then re-dispatch Brain #7 with the same file reference:

```
Agent(
    subagent_type="brain-07-growth",
    prompt="Read .planning/phases/NN-name/NN-PLAN-REVIEW.md before evaluating.
    This is iteration [N] of 3. Confirm gaps resolved. Approve or flag remaining issues."
)
```

**Loop decision table:**

| Verdict | Iteración | Acción |
|---------|-----------|--------|
| APPROVED | cualquiera | ✅ Proceder a `/gsd:execute-phase N` |
| APPROVED_WITH_CONDITIONS | 1 o 2 | Resolver conditions → re-iterar |
| REJECTED_REVISE | 1 o 2 | Revisar gaps → cascade domain brains → re-iterar |
| cualquier verdict | 3 | Escalar a humano (ver abajo) |

---

## Escalation (Después de 3 Iteraciones Sin APPROVED)

Si Brain-07 no retorna APPROVED después de 3 iteraciones, detener y presentar:

```
⚠️  Brain #7 no aprobó después de 3 iteraciones.

Gaps no resueltos:
- [gap 1]: [por qué no pudo resolverse]
- [gap 2]: [por qué no pudo resolverse]

Historial de iteraciones:
  Iter 1: [verdict] — [summary de cambios]
  Iter 2: [verdict] — [summary de cambios]
  Iter 3: [verdict] — [summary de cambios]

Decisión requerida:
  A) Continuar de todas formas (aceptar el riesgo conscientemente)
  B) Revisar el scope del plan manualmente antes de ejecutar
  C) Simplificar el plan, reducir scope, re-iterar desde cero

¿Qué querés hacer?
```

**No ejecutar `/gsd:execute-phase` hasta recibir decisión del humano.**

---

## Done When

- [ ] All PLAN.md files read
- [ ] Code files referenced in plans read
- [ ] `NN-PLAN-REVIEW.md` written with full context (Option D)
- [ ] Brain-07 dispatched with file reference (not inline context)
- [ ] Each concern filtered (✅ / 📅 / 🔴)
- [ ] Real gaps cascaded to domain brains
- [ ] PLAN.md files updated with gap fixes
- [ ] Brain-07 verdict: **APPROVED** (no conditions) — loop complete
- [ ] OR: Human decision received after 3 iterations without APPROVED
- [ ] Ready for `/gsd:execute-phase N` or `/mm:execute-phase N`
