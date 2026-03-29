# Roadmap: MasterMind Framework

## Milestones

- ✅ **v2.0 Production Platform** — Phases 1–4 (shipped 2026-03-17)
- ✅ **v2.1 War Room Frontend** — Phases 5–8 (shipped 2026-03-25)
- 📋 **v2.2 Brain Agents** — Autonomous subagents per brain, two-level BRAIN-FEED, parallel dispatch
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

### 📋 v2.2 Brain Agents

**Milestone Goal:** Convert brain consultations from manual skill workflows to autonomous Claude Code subagents. Each agent embeds the intermediary protocol natively, maintains domain-specific memory via its own BRAIN-FEED, and is dispatched in parallel by an orchestrator — replacing sequential manual steps with autonomous expert collaboration.

**Evolution path:** `mm:brain-context` workflows (v2.1) → agent system prompts (v2.2). No work is thrown away.

- [x] **Phase 09: Baselines + Agent Authoring** — Capture pre-migration measurements and author all 7 brain subagents with embedded intermediary protocol, evaluation criteria, and anti-patterns (completed 2026-03-28)
- [ ] **Phase 10: BRAIN-FEED Split** — Migrate monolithic BRAIN-FEED to two-level architecture (1 global + 7 domain feeds)
- [ ] **Phase 11: Smoke Tests** — Validate each agent end-to-end with adversarial prompts before enabling parallel dispatch
- [ ] **Phase 12: Parallel Dispatch + Command Update** — Wire orchestrator parallel dispatch and update mm:brain-context command to use Agent tool

## Phase Details

### Phase 09: Baselines + Agent Authoring

**Goal**: Users have 5 documented pre-migration baselines and 7 functional brain subagents with embedded domain expertise — ready to be wired into the split feed architecture.

**Depends on**: Phase 8 (v2.1 complete — mm:brain-context skill is the specification)

**Requirements**: BASE-01, BASE-02, AGT-01, AGT-02, AGT-03, FEED-02, FEED-03

**Success Criteria** (what must be TRUE):
1. `tests/baselines/baseline-01..05.md` exist with git timestamps that predate any `.claude/agents/mm/` file — the git history proves measurement before migration
2. Each baseline record includes the full BASE-02 schema: context_id, brain_feed_snapshot, cognitive_trace (T1/T2/T3), delta_velocity_score (1-5), characterization_diff, human_intervention_log
3. `.claude/agents/mm/brain-NN-domain/brain-NN-domain.md` exists for all 7 brains — each file's system prompt reads both feeds before querying NotebookLM (FEED-02), writes only to its own domain feed (FEED-03), and includes domain-specific [CORRECTED ASSUMPTIONS]
4. Each brain has a `criteria.md` with observable Rating 3 vs Rating 4 distinction (not generic quality statement)
5. Each brain has a `warnings.md` with all 4 universal poisoning patterns + domain-specific rejections
6. Agent executes protocol in <20% of human T1 time (T1 < 300s = profitable threshold from Brain #1)

**Plans**: 4 plans

Plans:
- [ ] 09-01-PLAN.md — Baseline schema + 5 baseline records (tests/baselines/)
- [ ] 09-02-PLAN.md — global-protocol.md + Brain Bundles #1 (Product) + #2 (UX)
- [ ] 09-03-PLAN.md — Brain Bundles #3 (UI Design) + #4 (Frontend)
- [ ] 09-04-PLAN.md — Brain Bundles #5 (Backend) + #6 (QA) + #7 (Evaluator)

---

### Phase 10: BRAIN-FEED Split

**Goal**: The monolithic `.planning/BRAIN-FEED.md` is migrated to a two-level architecture — every existing entry has exactly one owner, domain feeds are initialized with relevant content, and the global feed retains only cross-domain patterns.

**Depends on**: Phase 09 (agent system prompts must be authored first — they hardcode feed file paths that must match)

**Requirements**: FEED-01

**Success Criteria** (what must be TRUE):
1. All 8 feed files exist: `.planning/BRAIN-FEED.md` (global, cross-domain only) + `.planning/BRAIN-FEED-NN-domain.md` for each of the 7 brains
2. Every entry from the old monolithic BRAIN-FEED.md appears in exactly one file — no entry is in both global and a domain feed, no entry is in two domain feeds
3. The global BRAIN-FEED.md contains zero entries that belong to a single brain's domain (validated by manual review)
4. Feed file paths in all 7 agent system prompts from Phase 09 exactly match the filenames created in this phase

**Plans**: 3 plans

Plans:
- [ ] 10-01-PLAN.md — Verification scripts (Wave 0) + Engineering Niche feeds (#4 Frontend + #5 Backend + #6 QA) + smoke test
- [ ] 10-02-PLAN.md — Strategy Niche feeds (#1 Product + #2 UX + #3 UI + #7 Growth) + Brain #8 validation
- [ ] 10-03-PLAN.md — Global BRAIN-FEED.md cleanup + purity linter pass + human verification

---

### Phase 11: Smoke Tests

**Goal**: Each of the 7 brain agents is individually validated end-to-end — proven to load project reality, filter responses against the locked stack, reject domain-inappropriate recommendations, and write only to its own feed.

**Depends on**: Phase 10 (split feeds must exist for agents to read; smoke tests validate the full loop including feed reads)

**Requirements**: AGT-04

**Success Criteria** (what must be TRUE):
1. Each agent, when dispatched individually, reads both `BRAIN-FEED.md` and its domain feed before querying NotebookLM — confirmed by agent output showing feed contents were loaded
2. Each agent triggers at least 1 filter rejection when given an adversarial prompt designed to produce a domain-inappropriate recommendation (e.g., Brain #4 asked about state management rejects a Redux suggestion because Zustand 5 is the locked stack)
3. After each smoke test, only the agent's own domain feed is modified — global `BRAIN-FEED.md` and all other domain feeds are unchanged
4. Each agent returns structured output with verified insights (not generic advice) and explicit codebase references

**Plans**: TBD

---

### Phase 12: Parallel Dispatch + Command Update

**Goal**: The orchestrator dispatches all domain brain agents simultaneously via the Agent tool, Brain #7 runs after domain agents complete (not in parallel with them), and the `mm:brain-context` command uses Agent tool dispatch instead of manual MCP workflow steps.

**Depends on**: Phase 11 (all 7 agents individually validated before parallel wiring)

**Requirements**: DISP-01, DISP-02

**Success Criteria** (what must be TRUE):
1. When `mm:brain-context` is invoked, all relevant domain brain agents are dispatched in a single orchestrator message (not sequentially across messages) — observable as simultaneous agent execution
2. Brain #7 (Evaluator) is dispatched only after all domain agents have returned their outputs — it receives domain agent results as context, never runs in parallel with them
3. After a full parallel dispatch, `BRAIN-FEED.md` (global) is identical to its pre-dispatch state — no agent wrote to it directly; any cross-domain patterns appear only in agent return values
4. The `mm:brain-context` slash command file no longer contains manual `mcp__notebooklm-mcp__notebook_query` steps — it dispatches agents via `Task()` and synthesizes their outputs

**Plans**: TBD

---

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Type Safety Foundation | v2.0 | 3/3 | ✅ Complete | 2026-03-13 |
| 2. Parallel Execution Core | v2.0 | 4/4 | ✅ Complete | 2026-03-13 |
| 3. Web UI Platform | v2.0 | 4/4 | ✅ Complete | 2026-03-13 |
| 4. Experience Store & Production | v2.0 | 5/5 | ✅ Complete | 2026-03-14 |
| 5. Foundation, Auth & WS Infrastructure | v2.1 | 5/5 | ✅ Complete | 2026-03-20 |
| 6. Command Center | v2.1 | 3/3 | ✅ Complete | 2026-03-20 |
| 7. The Nexus | v2.1 | 3/3 | ✅ Complete | 2026-03-22 |
| 8. Strategy Vault, Engine Room & UX Polish | v2.1 | 5/5 | ✅ Complete | 2026-03-24 |
| 9. Baselines + Agent Authoring | 4/4 | Complete   | 2026-03-28 | - |
| 10. BRAIN-FEED Split | 2/3 | In Progress|  | - |
| 11. Smoke Tests | v2.2 | 0/TBD | Not started | - |
| 12. Parallel Dispatch + Command Update | v2.2 | 0/TBD | Not started | - |

---
*Roadmap updated: 2026-03-28 — Phase 09 planned (4 plans, 3 waves)*
