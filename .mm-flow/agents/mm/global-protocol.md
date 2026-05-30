# MasterMind Protocol — Global Constraints

All 7 brain agents read and obey this document. No exceptions.
A violation is a Level 1 Failure (Rating 1 — Blocker).

This file is the governance layer. One edit here propagates to all 7 brain agents.
Reference it from every agent system prompt. Never duplicate its constraints inline.

---

## Stack Hard-Lock

The ONLY approved stack. Any suggestion outside this list = Stack Hallucination = Rating 1.

| Layer | Approved | Prohibited |
|-------|----------|------------|
| Framework | Next.js 16 (App Router only — no Pages Router) | Any other framework, Pages Router |
| UI Runtime | React 19 (Compiler DISABLED — conflicts with React.memo on RF nodes) | React 18, React Compiler enabled |
| Language | TypeScript strict mode (no implicit any, no explicit any without suppression comment) | JavaScript, loose TypeScript |
| Styling | Tailwind 4 (CSS-only config — no tailwind.config.js) | CSS Modules, styled-components, Emotion, tailwind.config.js |
| State | Zustand 5 + Immer (never Redux, never Context for performance-critical state) | Redux, MobX, Context API for state |
| State access | `useBrainState(id)` targeted selector — never `useStore()` global | `useStore()` global, direct store access |
| Package manager (Node.js) | pnpm | npm, yarn, bun |
| Package manager (Python) | uv | pip, poetry, conda, pipenv |
| Python runtime | 3.14 | Any older Python version |
| Graph library | @xyflow/react v12 | react-flow (legacy), d3-force standalone |

**Hard rule:** Suggesting ANY library not declared in the root `uv.lock` or `pnpm-lock.yaml` = Stack Hallucination = automatic Rating 1.

---

## File Architecture

Only create files in these locations:

- `apps/web/src/` — frontend code (screaming architecture: feature-first, not layer-first)
- `apps/api/` — backend code
- `.planning/` — project planning and brain feed documents
- `tests/` — test files and baselines

Any file outside these locations requires **explicit orchestrator approval before creation**.

Prohibited locations without approval:
- Root directory (except config files that require it)
- `apps/web/public/` (assets only, no code)
- `.claude/agents/` (managed by authoring process, not brain output)

---

## WebSocket Protocol

Only use fields defined in the existing WS schema. Never invent protocol fields.

Locked patterns (do not modify):
- `wsDispatcher` is a **module singleton** — not a class, not a hook, not a service
- Token obtained via `/api/auth/token` endpoint (Server Action reading httpOnly cookie)
- RAF batching lives in `brainStore` — NOT in `wsDispatcher`
- 16ms drain cycle — 24 events maximum per frame
- Positions locked after dagre layout — no layout recalculation on WS events

Prohibited:
- Inventing new WS message fields not in the existing schema
- Moving RAF batching out of `brainStore`
- Bypassing the `/api/auth/token` token handoff
- Re-triggering dagre layout on state updates

---

## Cross-Domain Anti-Patterns

These trigger rejection across ALL brain domains regardless of context:

| Pattern | Rule | Rating Impact |
|---------|------|---------------|
| Functions > 50 lines | Split into focused units | Rating 2 max if present |
| `any` types without suppression comment | Add explicit suppression + reason | Rating 2 max if present |
| Commented-out production code | Remove it — git history exists | Rating 2 max if present |
| Hardcoded credentials | NEVER — not even in test examples | Rating 1 (Security Bypass = Blocker) |
| Manual production access steps | Direct DB changes, SSH without automation = architecture failure | Rating 1 (Toil-Inducer = Blocker) |
| `useStore()` global selector | Always use `useBrainState(id)` or equivalent targeted selector | Rating 2 max if present |
| `NODE_TYPES` inline in JSX | Must be at module level — prevents infinite re-render loop | Rating 1 (causes production bug) |

---

## Feed Write Scope

The BRAIN-FEED system has two levels:

| File | Access | Who writes |
|------|--------|------------|
| `.planning/BRAIN-FEED.md` | READ-ONLY for all agents | Orchestrator only — after cross-domain synthesis |
| `.planning/BRAIN-FEED-NN-domain.md` | READ + WRITE for the owning brain | Brain NN only — after filtering its NotebookLM response |

Rules:
- Agents read BOTH `.planning/BRAIN-FEED.md` AND their own `.planning/BRAIN-FEED-NN-domain.md` before querying
- Agents write ONLY to their own `.planning/BRAIN-FEED-NN-domain.md`
- A brain writing to `.planning/BRAIN-FEED.md` directly = context pollution = architectural violation

**A brain writing to the global BRAIN-FEED.md directly is a Level 1 Failure.**

---

## Oracle Pattern (for rejections)

**Stack Hard-Lock violations** use this format (also see domain agent RESPONSE GATE):

```
[STACK VIOLATION DETECTED]
Violation: <exact request>
Rejected: <reason in one line>
Source: global-protocol.md > Stack Hard-Lock
```

**Non-stack rejections** (anti-patterns, architecture violations) use:

```
Rejected: [specific library or pattern name] violates [constraint name].
Source: global-protocol.md > [Section name]
```

**Examples:**

```
[STACK VIOLATION DETECTED]
Violation: npm install framer-motion
Rejected: npm is prohibited — pnpm is the only valid Node.js package manager
Source: global-protocol.md > Stack Hard-Lock

Rejected: useStore() global selector violates Cross-Domain Anti-Patterns.
Source: global-protocol.md > Cross-Domain Anti-Patterns

Rejected: hardcoded API key violates Security Bypass rule.
Source: global-protocol.md > Cross-Domain Anti-Patterns
```

**Generic rejections without source citation = Rating 2 maximum.**
No citation = no proof of identity = the agent is guessing, not reasoning.

---

## Delta-Velocity Rating Scale

| Rating | Level | Definition |
|--------|-------|------------|
| 1 | Blocker | Hallucinates libraries, breaks TypeScript types, ignores Stack Hard-Lock or warnings.md. Unusable. |
| 2 | Junior | Correct but generic — doesn't use existing Zustand stores, React Flow architecture, or project-specific patterns. Full refactor needed. |
| 3 | Peer | Correct, respects stack and context, integrates with project architecture. PR-ready with minor tweaks. |
| 4 | Senior | Detects non-obvious optimization or gap not in the ticket (e.g., critical useMemo, unasked WS error handling). Improves the codebase. |
| 5 | Architect | Proposes game-changing solution that unlocks the next roadmap phase (e.g., DAG optimization reducing DOM load 40%). |

Target: Rating >= 3 = system is stable. Rating 4-5 = system is profitable.

**T1 Profitability Gate:** T1 (context setup time) < 300 seconds (5 minutes).
If context setup takes longer than 5 minutes, the agent is not profitable vs the manual skill.

---

## Session Start Reminder

Before every consultation, every brain agent must:

1. Read `.planning/BRAIN-FEED.md` (global project reality — READ ONLY)
2. Read `.planning/BRAIN-FEED-NN-domain.md` (own domain feed — read + write)
3. Build `[IMPLEMENTED REALITY]` block (what actually exists, not roadmap)
4. List `[CORRECTED ASSUMPTIONS]` (only corrections that prevent bad recommendations)
5. Query NotebookLM with full context (get notebook ID from `brain-selection.md`)
6. Filter response against codebase (grep before concluding)
7. Write insights ONLY to own domain feed

Never query cold. Never hallucinate. For Stack Hard-Lock violations, use `[STACK VIOLATION DETECTED]` block (see Oracle Pattern). For all other rejections, cite source explicitly.
