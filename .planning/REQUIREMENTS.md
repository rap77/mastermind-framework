# Requirements: v2.2 Brain Agents

**Status:** APPROVED
**Approved:** 2026-03-27 (Brain #1 Product Strategy + Brain #7 Growth/Data consultation)
**Milestone:** v2.2 Brain Agents
**Branch:** feat/v2.2-brain-agents

## Summary

11 requirements across 4 groups. Convert brain consultations from manual `mm:brain-context` skill workflows to autonomous Claude Code subagents with domain expertise accumulation.

Evolution path: `mm:brain-context` workflows (v2.1) → agent system prompts (v2.2). No work thrown away.

---

## AGT — Brain Subagents (4 requirements)

### AGT-01: Brain subagent files
Each of the 7 brains gets a Claude Code subagent file at `.claude/agents/brain-NN-domain.md`. The system prompt embeds the intermediary protocol natively (what Brain #1 consultation taught about consulting NotebookLM + filtering for codebase reality).

**Acceptance:** 7 `.claude/agents/brain-NN-*.md` files exist and are functional.

### AGT-02: Evaluation criteria per agent
Each agent has an `evaluation-criteria.md` that defines what a "good response" looks like for that domain. Without this, agents have no standard to filter against — they'll either pass everything or nothing.

**Acceptance:** 7 `evaluation-criteria.md` files exist (one per brain domain).

### AGT-03: Anti-patterns per agent
Each agent has an `anti-patterns.md` that defines what NOT to include in the BRAIN-FEED — patterns that have burned us before, shallow advice, domain mismatches. Prevents BRAIN-FEED poisoning.

**Note:** v2.2 scope = manual curation only (no auto-pruning). Auto-pruning deferred to v2.3.

**Acceptance:** 7 `anti-patterns.md` files exist (one per brain domain).

### AGT-04: All 7 brain subagents functional
End-to-end test: each agent can be dispatched, reads its feeds, queries its NotebookLM brain, filters for codebase reality, and returns verified insights.

**Acceptance:** Manual smoke test of each agent passing the intermediary protocol.

---

## FEED — Two-Level BRAIN-FEED (3 requirements)

### FEED-01: BRAIN-FEED split into global + per-brain
Current `.planning/BRAIN-FEED.md` is monolithic. Split into:
- `.planning/BRAIN-FEED.md` — general project feed (architecture decisions, cross-domain patterns)
- `.planning/BRAIN-FEED-NN-domain.md` — per-brain domain feed (e.g., `BRAIN-FEED-01-product.md`)

**Acceptance:** All 8 feed files exist (1 global + 7 per-brain). Existing content migrated from old BRAIN-FEED.md.

### FEED-02: Each agent reads both feeds before querying
Agent system prompts include instructions to read `BRAIN-FEED.md` (general) + `BRAIN-FEED-NN-domain.md` (own domain) before consulting NotebookLM. This prevents asking questions that the project already has answers to.

**Acceptance:** Both feed reads are part of each agent's system prompt workflow.

### FEED-03: Each agent writes only to its own feed
Agents update only their domain BRAIN-FEED (not the global one). Global feed is updated by the Orchestrator after cross-domain synthesis. This prevents context pollution between brain domains.

**Acceptance:** Agent system prompts include write instructions scoped to own domain feed only.

---

## BASE — Baseline Measurement (2 requirements)

### BASE-01: 5 manual consultation baselines documented
Before migrating to agents, document 5 real brain consultations using the current `mm:brain-context` skill workflow. Captures time, gaps found, re-consultations needed, quality of insights.

**Why:** Without baseline, there's no way to know if agents are better, worse, or the same as manual workflows.

**Acceptance:** `docs/baselines/consultation-baseline-01..05.md` files (or similar) with structured data.

### BASE-02: Metric framework defined
Define the measurement schema: time-per-consultation, gap-count, re-consultation-count, insight-quality-rating (1-5). Used to compare manual (baseline) vs agent (v2.2) performance.

**Acceptance:** Metric schema documented and applied to BASE-01 baselines.

---

## DISP — Dispatch (2 requirements)

### DISP-01: Orchestrator dispatches brain agents in parallel
Today: Claude follows `mm:brain-context` workflows sequentially (Brain #1, then Brain #7, etc.). v2.2: Orchestrator dispatches multiple brain agents simultaneously using the Agent tool.

**Acceptance:** `/mm:brain-context` or equivalent dispatches agents in parallel (not sequential skill steps).

### DISP-02: mm:brain-context updated for agent dispatch
The `mm:brain-context` slash command (created 2026-03-27, commit 862c4a0) gets updated to dispatch brain agents instead of running manual MCP workflows directly.

**Acceptance:** `mm:brain-context` command uses Agent tool dispatch, not manual MCP steps.

---

## Deferred to v2.3

- **YAML inter-agent coordination** — formal protocol for cross-agent structured handoffs. v2.2 uses agents reading each other's feeds directly (simpler, validate first).
- **Auto-pruning BRAIN-FEED** — removing stale/wrong entries automatically. v2.2 uses manual curation only.

---

## Out of Scope for v2.2

- RAG / vector stores (v3.0)
- Cross-brain machine learning (v3.0)
- PostgreSQL migration (v3.0)
- OpenClaw integration (v3.1)

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BASE-01 | Phase 09 | Complete |
| BASE-02 | Phase 09 | Complete |
| AGT-01 | Phase 09 | Complete |
| AGT-02 | Phase 09 | Complete |
| AGT-03 | Phase 09 | Complete |
| FEED-02 | Phase 09 | Complete |
| FEED-03 | Phase 09 | Complete |
| FEED-01 | Phase 10 | Pending |
| AGT-04 | Phase 11 | Pending |
| DISP-01 | Phase 12 | Pending |
| DISP-02 | Phase 12 | Pending |
