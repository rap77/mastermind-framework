# Intermediary Protocol

You are the bridge between code reality and brain knowledge. Every brain has 86+ books of expertise but zero access to your codebase. The quality of their response is determined entirely by the quality of your context.

## The 6-Step Protocol

### Step 1 — READ (never query cold)

Before writing a single word of the query:

```bash
# Always read these first:
cat .planning/BRAIN-FEED.md          # accumulated project reality
cat .planning/STATE.md               # current position + decisions

# For domain-specific context, read relevant code:
# - Phase 05-06+ : apps/web/src/stores/brainStore.ts
# - Frontend: apps/web/src/components/<domain>/
# - Backend: apps/api/mastermind_cli/api/routes/<domain>.py
```

### Step 2 — BUILD [IMPLEMENTED REALITY] block

Summarize what actually exists in the codebase:

```
[IMPLEMENTED REALITY]
Stack: Next.js 16 + React 19 + TypeScript + Tailwind 4 + shadcn/ui
State: Zustand 5 + Immer | Map<brainId, BrainState> + RAF batching
WS: wsDispatcher (module singleton) | token via /api/auth/token endpoint
Auth: httpOnly JWT | CVE-2025-29927 mitigated (proxy.ts + AuthGuardLayout)
Available: TanStack Query v5, @xyflow/react v12, DOMPurify

Phase 05 patterns proven:
- RAF batching in brainStore (not WS handler) — queues 24 events, drains before paint
- useBrainState(id) targeted selector — O(1) Map lookup, no cascade re-renders
- NODE_TYPES at module level (not inline) — prevents infinite re-render loop
```

Rule: **Include only what's actually implemented.** Not what's planned. Not what's in the ROADMAP.

### Step 3 — LIST [CORRECTED ASSUMPTIONS]

What will the brain likely assume wrong? Correct it explicitly:

```
[CORRECTED ASSUMPTIONS]
❌ "24 brains activate simultaneously" → ✅ 3-5 brains activate per brief (typical task)
❌ "React Flow needs layout recalculation on WS updates" → ✅ positions locked post-dagre
❌ "Immer is not available" → ✅ Immer 10 installed, used in brainStore since Phase 05
❌ "JWT is only validated at middleware" → ✅ dual-layer: proxy.ts + Server Components
```

Rule: Only correct assumptions that would lead to bad recommendations. Don't over-explain.

### Step 4 — QUERY with delta

Structure the query as: reality + corrections + specific question about the gap.

```
[IMPLEMENTED REALITY]
... (from Step 2)

[CORRECTED ASSUMPTIONS]
... (from Step 3)

[WHAT I NEED]
Phase 07 introduces NexusCanvas with dagre layout + WS illumination.
The specific question: how should BrainNode differentiate `active` vs `complete` visually
given that 8% of users are colorblind? We already use neon glow for active state.
No generic UX theory — I need specific implementation decisions for this stack.
```

### Step 5 — FILTER the response

For every concern or recommendation the brain raises:

| If brain says... | Action |
|-----------------|--------|
| "Consider adding X" where X exists | Mark ✅ already solved — skip |
| "Watch out for Y in Phase N+1" | Mark 📅 deferred — log in CONTEXT.md |
| "You need Z which is missing" | Mark 🔴 real gap — proceed to Step 6 |
| "Implement W using library L" | Grep: does L exist? Is W already done? |

```bash
# Verification pattern
grep -r "AlertTriangle" apps/web/src/components/   # does error icon exist?
grep -r "animate-pulse" apps/web/src/              # is pulse animation used?
```

### Step 6 — CASCADE real gaps immediately

Real gaps do NOT go into todos. They go into action:

```
🔴 Real gap found: error state needs AlertTriangle icon + pulse (not just color)
→ Consult Brain-03 (UI) in parallel with same [IMPLEMENTED REALITY] block
→ Get specific: CSS tokens, icon name, animation class
→ Update PLAN.md Task 2 with concrete change before execute
```

## Context Block Template

```
Project: MasterMind Framework — War Room Frontend
Stack: Next.js 16 + React 19 + TypeScript + Tailwind 4 + Zustand 5 + Immer + TanStack Query v5
Phase: [N] — [Name] | Current: [describe what's being planned]

[IMPLEMENTED REALITY]
[paste relevant patterns from BRAIN-FEED.md + code reading]

[CORRECTED ASSUMPTIONS]
[explicit corrections of what brain might assume wrong]

[WHAT I NEED]
[specific question — not generic. Name the exact component, decision, or tradeoff]
No generic theory. Give me implementation decisions for this specific stack.
```

## Anti-patterns

| ❌ Wrong | ✅ Right |
|----------|----------|
| Query with only plan text | Read code first, query with reality |
| Accept first response as truth | Grep each concern against codebase |
| Note gaps as todos | Cascade to domain brain immediately |
| Re-query same brain with same context | Different brain or different angle |
| Include everything in context | Only include what's relevant to the question |
