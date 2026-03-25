# Roadmap: MasterMind Framework

## Milestones

- ✅ **v2.0 Production Platform** — Phases 1–4 (shipped 2026-03-17)
- ✅ **v2.1 War Room Frontend** — Phases 5–8 (shipped 2026-03-25)
- 📋 **v2.2 Brain Agents** — Autonomous subagents per brain, two-level BRAIN-FEED, inter-agent coordination
- 📋 **v3.0 Custom Workflow Framework + RAG** — Replace GSD, declarative DSL, pluggable agents, per-agent vector stores
- 📋 **v3.1 OpenClaw Integration** — Brain agents as OpenClaw skills, omnichannel (22+ channels), voice, native apps

## Phases

<details>
<summary>✅ v2.0 Production Platform (Phases 1–4) — SHIPPED 2026-03-17</summary>

- [x] Phase 1: Type Safety Foundation (3/3 plans) — completed 2026-03-13
- [x] Phase 2: Parallel Execution Core (4/4 plans) — completed 2026-03-13
- [x] Phase 3: Web UI Platform (4/4 plans) — completed 2026-03-13
- [x] Phase 4: Experience Store & Production (5/5 plans) — completed 2026-03-14

See full details: `.planning/milestones/v2.0-ROADMAP.md`

</details>

<details>
<summary>✅ v2.1 War Room Frontend (Phases 5–8) — SHIPPED 2026-03-25</summary>

- [x] Phase 5: Foundation, Auth & WebSocket Infrastructure (5/5 plans) — completed 2026-03-20
- [x] Phase 6: Command Center (3/3 plans) — completed 2026-03-20
- [x] Phase 7: The Nexus (3/3 plans) — completed 2026-03-22
- [x] Phase 8: Strategy Vault, Engine Room & UX Polish (5/5 plans) — completed 2026-03-24

See full details: `.planning/milestones/v2.1-ROADMAP.md`

</details>

### 📋 v2.2 Brain Agents (planned)

**Milestone Goal:** Convert brain consultations from manual skill workflows to autonomous Claude Code subagents. Each agent embeds the intermediary protocol, maintains domain-specific memory, and accumulates expertise across phases.

**Evolution path:** `mm:brain-context` workflows (v2.1) → agent system prompts (v2.2). No work is thrown away.

**Key changes:**
- 7 brain subagents (`.claude/agents/brain-NN-*.md`) with built-in intermediary protocol
- Two-level BRAIN-FEED: `BRAIN-FEED.md` (project general) + `BRAIN-FEED-NN-*.md` (per-brain domain)
- Orchestrator dispatches agents in parallel (today: Claude follows workflows sequentially)
- Each agent filters responses against code and updates its domain feed autonomously
- Inter-agent coordination for cross-domain decisions (API contracts, state ownership)

**Phases:** TBD — start with `/gsd:new-milestone v2.2`

### 📋 v3.0 Custom Workflow Framework + RAG (future)

**Milestone Goal:** Replace GSD with MasterMind's own niche-agnostic workflow framework. Keep GSD's proven patterns (goal-backward, wave parallelization, atomic commits, deviation rules). Add brain integration at every gate, declarative DSL, pluggable agents, and niche-specific flow templates. Plus per-agent RAG for persistent brain memory.

**Research completed:** `.planning/research/GSD-FRAMEWORK-ANALYSIS.md`

**Phases:** TBD — requires v2.2 agent infrastructure.

### 📋 v3.1 OpenClaw Integration (future)

**Milestone Goal:** Brain agents as OpenClaw skills — omnichannel access (22+ channels), voice interfaces, native apps.

**Research completed:** `.planning/research/OPENCLAW-ANALYSIS.md`

**Phases:** TBD — requires v3.0 framework.

## Progress

| Phase | Milestone | Plans | Status | Completed |
|-------|-----------|-------|--------|-----------|
| 1. Type Safety Foundation | v2.0 | 3/3 | ✅ Complete | 2026-03-13 |
| 2. Parallel Execution Core | v2.0 | 4/4 | ✅ Complete | 2026-03-13 |
| 3. Web UI Platform | v2.0 | 4/4 | ✅ Complete | 2026-03-13 |
| 4. Experience Store & Production | v2.0 | 5/5 | ✅ Complete | 2026-03-14 |
| 5. Foundation, Auth & WS Infrastructure | v2.1 | 5/5 | ✅ Complete | 2026-03-20 |
| 6. Command Center | v2.1 | 3/3 | ✅ Complete | 2026-03-20 |
| 7. The Nexus | v2.1 | 3/3 | ✅ Complete | 2026-03-22 |
| 8. Strategy Vault, Engine Room & UX Polish | v2.1 | 5/5 | ✅ Complete | 2026-03-24 |

---
*Roadmap updated: 2026-03-25 — v2.1 archived, v2.2 next milestone*
