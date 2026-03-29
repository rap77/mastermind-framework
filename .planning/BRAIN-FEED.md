# BRAIN-FEED — MasterMind Framework v2.2

> Living document. Updated after each completed phase.
> Two-level architecture: this global feed (cross-domain) + 7 domain feeds (BRAIN-FEED-NN-domain.md).
> Global feed: product decisions, UX decisions, milestones affecting ALL 7 brains equally. Zero technical entries.
> Domain feeds: see .planning/BRAIN-FEED-NN-domain.md for each brain's domain-specific patterns.
> Last updated: 2026-03-28 after Phase 10 (BRAIN-FEED Split)

---

## Stack (Locked)

| Layer | Library | Version | Notes |
|-------|---------|---------|-------|
| Framework | Next.js | 16.x | App Router, no Pages |
| UI | React | 19.x | Compiler disabled (conflicts with React.memo on RF nodes) |
| Language | TypeScript | 5.x | strict mode |
| Styling | Tailwind CSS | 4.x | CSS-only config, no tailwind.config.js |
| Components | shadcn/ui | Nova preset | OKLCH color system, base-ui |
| State | Zustand | 5.x | + Immer middleware |
| Query | TanStack Query | v5 | staleTime: 30s default |
| Graph | @xyflow/react | v12 | React Flow v12 |
| Auth | jose | latest | Edge Runtime compatible |
| Sanitization | DOMPurify | latest | XSS prevention |
| Package mgr | pnpm | — | Never npm/yarn |
| Python | uv | — | Never pip/poetry |

---

## Architecture Patterns (Invariants)

Patterns proven in production that brains must know:

### Brain Agent Architecture (v2.2)
- Brain Bundle = 3-file directory: `brain-NN-domain.md` + `criteria.md` + `warnings.md` — never combine into one file
- `model: inherit` + `mcpServers: notebooklm-mcp` required in all brain agent frontmatter
- `global-protocol.md` is the governance layer — agents read it, never duplicate its constraints inline
- No notebook IDs in agent files — `brain-selection.md` is the single source of truth
- Brain #7 dispatched AFTER domain brains (#1-#6) always — never in parallel, never without domain context
- Brain #7 uses `[CROSS-DOMAIN REALITY]` block — synthesizes domain outputs, NOT codebase state

### Delta-Velocity Measurement
- Scale: 1=Wrong / 2=Junior / 3=Peer / 4=Senior / 5=Principal
- T1 Profitability Threshold: T1 > 300s = agent-unprofitable (manual is already losing money)
- Pre-migration manual T1 baseline: 210-270s — all profitable, agents reduce margin further
- Frozen Context Block = control variable — same product context, different ticket per baseline
- Measurement anchor commit: `bcfb93803e7ca5ca1c6b99c554fd190c77196f5a` — Phase 11 A/B comparison target

---

## Implemented Features (What Exists)

Prevents brains from suggesting what's already built:

| Feature | Location | Notes |
|---------|----------|-------|
| Auth flow | `apps/web/src/app/(auth)/login/` | Server Actions, httpOnly cookie |
| JWT verification | `apps/web/src/lib/auth.ts` | jose, Edge Runtime |
| WS infrastructure | `apps/web/src/stores/wsDispatcher.ts` | Module singleton |
| Brain state store | `apps/web/src/stores/brainStore.ts` | Map + Immer + RAF |
| GET /api/brains | `apps/api/.../routes/brains.py` | JWT, pagination, IDOR protection |
| POST /api/tasks | `apps/web/src/app/api/tasks/route.ts` | Creates task, returns taskId |
| Command Center | `apps/web/src/app/command-center/` | BentoGrid, BrainTile, BriefInputModal |
| The Nexus (Phase 07) | `apps/web/src/app/nexus/` | NexusCanvas, BrainNode, React Flow DAG |
| Strategy Vault (Phase 08) | `apps/web/src/app/strategy-vault/` | Phase 08 — see git history |
| Engine Room (Phase 08) | `apps/web/src/app/engine-room/` | Phase 08 — see git history |
| Brain Agent Bundles | `.claude/agents/mm/` | 7 brain bundles × 3 files + global-protocol.md (22 files) |
| Baseline anchors | `tests/baselines/` | baseline-schema.md + 5 pre-migration measurement records |

---

## Active Constraints

Hard limits that brains must respect:

- **No `npm` or `pip`** — pnpm for Node, uv for Python
- **Brain #7 dispatch order** — ALWAYS after domain brains complete, never concurrent
- **No notebook IDs in agent files** — decouple via `brain-selection.md`, prevents 7-file re-edit when IDs change
- **Structured output required in all brain agent responses** — free-text prose causes information leaks across multi-brain chains (proven in baseline 04: cascade re-run added 50s to T3)

---

## Phase Learnings

### Phase 09 — Baselines + Agent Authoring
Key discoveries:
- **Brain Bundle invariant**: 3 files per domain, persona opens verbatim first, 6-step protocol as identity (first-person, not step-list). Deviating from this produces checklists agents optionally follow instead of how they think.
- **`[CORRECTED ASSUMPTIONS]` twice rule**: embed once in protocol section, again in "Always Include" block — redundancy is intentional, prevents the block from being skipped under cognitive load
- **Output Format section is non-negotiable**: without it, free-text prose from domain brains causes cascade errors in Brain #7 (proven: baseline 04 T3 elevated 50s due to re-run caused by imprecise language)
- **Brain #7 `[CROSS-DOMAIN REALITY]` distinction**: it synthesizes domain agent outputs from orchestrator context — it does NOT independently query feeds or re-read codebase state

---

## Anti-patterns (Tried and Rejected)

| Pattern | Why rejected | What we use instead |
|---------|--------------|---------------------|
| Free-text prose in brain output | Information leak across multi-brain chain — Brain #7 receives garbage | Structured Output Format section in every agent |
| Notebook IDs hardcoded in agent files | Re-edit 7 files when IDs change | Reference `brain-selection.md` as single source of truth |
| Brain #7 dispatched in parallel with domain brains | Evaluates without seeing domain outputs — useless | Always dispatch AFTER domain brains complete |
