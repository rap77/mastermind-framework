# Project Research Summary

**Project:** MasterMind Framework v2.2 — Brain Agents
**Domain:** Claude Code subagent system — autonomous brain consultation with domain-specific BRAIN-FEED accumulation
**Researched:** 2026-03-27
**Confidence:** HIGH

## Executive Summary

MasterMind v2.2 is a pure configuration and file-structure migration: the manual `mm:brain-context` skill workflow (4 sequential steps, human-executed) becomes 7 autonomous Claude Code subagents dispatched in parallel by an orchestrator. No new Python or npm packages are required. The entire implementation is `.md` files in `.claude/agents/mm/` and `.planning/BRAIN-FEED-NN-*.md`. The existing backend (`apps/api/`) and frontend (`apps/web/`) stacks remain untouched. The key technical mechanism is Claude Code's native `Task()` dispatch, which enables all domain brain agents to run simultaneously — a change that reduces Moment 2 consultation time from ~20 minutes (sequential) to ~5 minutes (parallel).

The recommended implementation order is strict: baseline measurement first (before any agent is written), then agent files + evaluation criteria + anti-patterns in parallel, then BRAIN-FEED split, then smoke tests, then parallel dispatch wiring, and finally the `mm:brain-context` command update. Skipping baselines before migration is the single unrecoverable failure mode — you cannot reconstruct pre-migration measurements after the fact. Every other pitfall has a recovery path.

The critical design insight from PROJECT.md — "intermediary protocol becomes built-in behavior, not a workflow to read and follow" — must govern how every agent system prompt is written. Agents are expert personas with embedded domain knowledge, not checklists. An agent that mirrors the old `moment-N.md` step list verbatim produces the same quality as the manual skill at higher maintenance cost. The differentiation comes from parallelism, per-brain feed accumulation, and explicit evaluation criteria that make filtering repeatable rather than judgment-based.

---

## Key Findings

### Recommended Stack

v2.2 is zero-dependency: Claude Code's built-in Agent tool (`Task()`) handles parallel dispatch, NotebookLM MCP is already integrated and agents inherit session MCP access, and BRAIN-FEED files are plain Markdown with no schema requirement. Agent files use a specific Claude Code frontmatter spec (`name`, `description`, `model`, `color`, `tools`) with `model: inherit` for all brain agents so they run at whatever model the orchestrator uses.

**Core technologies:**
- **Claude Code subagents** (`.claude/agents/mm/*.md`): brain consultation automation — native capability, zero infrastructure, replaces skill workflow steps with agent identity
- **Agent tool `Task()`**: parallel brain dispatch — the only mechanism for true parallel subagent execution; all `Task()` calls in a single message run simultaneously
- **NotebookLM MCP** (`mcp__notebooklm-mcp__notebook_query`): knowledge retrieval per brain — already functional, agents inherit parent session MCP access
- **Plain Markdown BRAIN-FEED files**: per-brain knowledge accumulation — no library needed, portable, human-readable; YAML schema deferred to v3.0

**Critical naming constraint:** Agent `name` field must be `lowercase-hyphens` only, 3-50 chars. The `subagent_type` in `Task()` must exactly match. Use `brain-01-product`, never `brain_01_product`.

### Expected Features

All 11 requirements are load-bearing. There is no valid partial migration — a hybrid manual/agent system is harder to maintain than either pure approach.

**Must have (table stakes) — all P1:**
- Embedded intermediary protocol in each agent system prompt (6 steps: read feeds, build [IMPLEMENTED REALITY], build [CORRECTED ASSUMPTIONS], query, filter with codebase verification, write to domain feed)
- Per-brain BRAIN-FEED split: global `BRAIN-FEED.md` (read-only for agents) + 7 domain feeds (each agent writes only to its own)
- Domain-specific [CORRECTED ASSUMPTIONS] baked into each agent — Brain #4 knows React Compiler is disabled; Brain #5 knows asyncio.TaskGroup replaces Redis/Celery
- Evaluation criteria per domain (7 files, AGT-02) — explicit quality gate that makes filtering repeatable, not vibes-based
- Anti-patterns per domain (7 files, AGT-03) — rejection list that prevents BRAIN-FEED poisoning at the source
- Smoke test per agent (AGT-04) — adversarial prompts designed to trigger at least one filter rejection per agent
- Parallel dispatch from orchestrator (DISP-01) — Brain #7 always runs last, after domain agents complete
- Updated `mm:brain-context` command (DISP-02) — replaces manual MCP workflow execution with Agent tool dispatch

**Should have (differentiators):**
- Baseline measurement: 5 manual consultations documented before migration (BASE-01) — the comparison point that validates whether agents actually improved quality
- Metric schema: time/consultation, gap-count, re-consultations, quality-rating recorded 24h after consultation (BASE-02)
- BRAIN-FEED self-update after each consultation (built into agent step 6 — no external trigger needed)

**Defer to v2.2.x / v2.3+:**
- Auto-pruning BRAIN-FEED entries (no validation mechanism in v2.2 scope)
- YAML inter-agent coordination protocol (file reads are sufficient; YAML adds overhead before value is validated)
- RAG per agent with ChromaDB/Qdrant (v3.0 — requires infrastructure work before any consultation improvement is validated)
- Brain auto-discovering which brains to consult (humans own moment routing; agents own execution)

### Architecture Approach

The architecture has two layers: an orchestrator layer (Claude main, via `mm:brain-context` command) that reads project state, selects which brains to dispatch, and synthesizes outputs into GSD artifacts; and a brain agent layer (7 parallel subagents) where each agent independently reads both feeds, verifies the codebase, queries its specific NotebookLM notebook, filters results, writes to its domain feed, and returns structured output. Brain #7 (Evaluator) is architecturally special — it always runs after domain agents, receives their outputs as context, and runs a 3-iteration verdict loop (APPROVED / APPROVED_WITH_CONDITIONS / REJECTED_REVISE) before escalating to human if unresolved.

**Major components:**
1. **Brain Agent files** (`.claude/agents/mm/brain-NN-*.md` x7) — subagent system prompts with embedded 6-step intermediary protocol; NOT external workflow references
2. **Domain BRAIN-FEED files** (`.planning/BRAIN-FEED-NN-*.md` x7) — per-brain accumulated patterns; isolated write boundaries enforced by behavioral contract in each agent's identity section
3. **Global BRAIN-FEED** (`.planning/BRAIN-FEED.md`) — cross-domain patterns only; write-protected from agents (orchestrator updates post-synthesis)
4. **Evaluation criteria + anti-patterns** (`.claude/agents/mm/criteria/` x14 files, or embedded inline) — quality gate and rejection list per domain
5. **Updated `mm:brain-context` command** — orchestration coordinator: builds shared context block, dispatches agents via `Task()`
6. **Baselines** (`docs/baselines/` — 5 consultation records + metric schema) — pre-migration measurement artifacts

**Key architectural constraint:** Parallel dispatch requires all `Task()` calls in a single orchestrator message. Agents dispatched across separate messages run sequentially. Brain #7's 3-iteration verdict loop must be native to its system prompt — it cannot be an external workflow the agent references.

### Critical Pitfalls

1. **Workflow-as-steps system prompt** — Copy-pasting `moment-N.md` steps into agent files produces a slow skill, not an autonomous agent. Write agents as expert personas ("You never query without loading project reality") not numbered checklists. Verify with AGT-04: agent reads BRAIN-FEED without being explicitly told to.

2. **BRAIN-FEED pollution on migration day** — Ambiguous patterns copied to multiple domain feeds on day one defeat the purpose of the split. Enforce a one-owner migration rule before splitting: every entry in the current `BRAIN-FEED.md` goes to exactly one file (global or one domain). No copies.

3. **No baseline before migration** — Unrecoverable. Baselines collected after migration cannot recreate pre-migration measurements. BASE-01 and BASE-02 must complete before ANY agent file is written. File timestamps are the only proof.

4. **Parallel write race to global BRAIN-FEED** — Agents writing "cross-domain insights" to `BRAIN-FEED.md` during parallel dispatch silently overwrite each other. Make the boundary absolute: agents include cross-domain patterns in their return value's `cross-domain-insights` section; orchestrator writes to global feed post-synthesis.

5. **Smoke test passes syntactically, not semantically** — Generic prompts ("what are best practices for X?") never trigger filter rejections. Each AGT-04 smoke test needs an adversarial question designed to trigger at least one rejection from the locked stack. Brain #4 asked about state management will get a Redux recommendation — agent must reject it because Zustand 5 + Immer is the locked stack.

---

## Implications for Roadmap

Based on the dependency graph in ARCHITECTURE.md, the build order is strict. There are 4 requirement groups (BASE, AGT, FEED, DISP) with hard cross-group dependencies. The recommended 4-phase structure maps directly to these groups.

### Phase 1: Baselines + Agent Authoring
**Rationale:** BASE must complete before AGT can start — skipping baselines is the only unrecoverable failure mode in v2.2. AGT-01, AGT-02, AGT-03 can proceed in parallel once baseline collection begins (no cross-dependency within the group). This phase is the highest-risk for shortcuts; it must be protected procedurally (timestamps prove sequence).
**Delivers:** 5 documented manual consultation baselines (BASE-01, BASE-02), 7 agent files with embedded intermediary protocol (AGT-01), 7 evaluation criteria files (AGT-02), 7 anti-patterns files (AGT-03). FEED-02 and FEED-03 are embedded in AGT-01 system prompts — completed as part of this phase.
**Avoids:** Pitfall 4 (no baseline before migration), Pitfall 1 (workflow-as-steps system prompt), Pitfall 3 (missing evaluation criteria), Pitfall 7 (BRAIN-FEED poisoning via unverified patterns)

### Phase 2: BRAIN-FEED Split
**Rationale:** FEED-01 is logically after AGT-01 draft because agent system prompts hardcode feed file paths (`BRAIN-FEED-NN-domain.md`) — the naming convention must be locked before creating the feed files. Migration requires applying the one-owner rule to every existing entry in the monolith. Splitting the feed before agent system prompts exist risks naming drift.
**Delivers:** 7 domain BRAIN-FEED files initialized with migrated content (FEED-01), global BRAIN-FEED.md cleaned to cross-domain patterns only, one-owner assignment verified for all migrated entries.
**Uses:** Naming convention locked during Phase 1 AGT-01 authoring.
**Avoids:** Pitfall 2 (BRAIN-FEED pollution on migration day)

### Phase 3: Smoke Tests
**Rationale:** AGT-04 requires AGT-01 + AGT-02 + AGT-03 + FEED-01 all complete. Smoke tests validate the full consultation loop against the split feeds before any dispatch wiring. Isolating individual agent failures is far easier than diagnosing failures in parallel execution.
**Delivers:** 7 individually validated agents — each confirmed to: read both feeds before querying, trigger at least 1 filter rejection on an adversarial prompt, write to domain feed only, return structured response with verified insights.
**Implements:** Validates FEED-03 behavioral contract (write isolation), evaluation criteria active in filter step, MCP tool inheritance from parent session.
**Avoids:** Pitfall 5 (dispatch before smoke test), Pitfall 8 (semantic smoke test failure — test prompts must be adversarial)

### Phase 4: Parallel Dispatch + Command Update
**Rationale:** DISP-01 requires AGT-04 passing — all building blocks validated before wiring parallel execution. DISP-02 requires DISP-01 working. This phase is lowest-risk because it is wiring, not creation. All 4 moment workflows in `mm:brain-context` must be updated, not just the SKILL.md routing table.
**Delivers:** Orchestrator parallel dispatch via Agent tool (DISP-01) with Brain #7 sequencing enforced, updated `mm:brain-context` command replacing manual MCP workflow execution for all 4 moments (DISP-02), integration test confirming global BRAIN-FEED.md unchanged during parallel dispatch.
**Avoids:** Pitfall 5 (parallel write race to global BRAIN-FEED), integration gotcha (all 4 moment workflows must be updated)

### Phase Ordering Rationale

- **BASE before AGT is the hardest constraint to enforce** and the most important. The sequencing rule is non-negotiable: the first git commit with any agent file must post-date the last BASE-01 consultation record by timestamp.
- **AGT-01/02/03 are parallelizable** within Phase 1. Two people can work simultaneously: one writing agent system prompts (AGT-01), one writing criteria and anti-patterns (AGT-02, AGT-03).
- **FEED-01 after AGT-01 draft** because the domain feed naming convention must be locked before creating the files. Refactoring path names in all 7 agent system prompts after the fact is expensive.
- **DISP last** because parallel dispatch errors are hardest to diagnose. Individual agent validation (AGT-04) isolates failures; parallel execution multiplies them.

### Research Flags

Phases with standard patterns (no additional research needed):
- **Phase 2 (BRAIN-FEED Split):** The one-owner migration rule is fully defined in PITFALLS.md. Execution is manual but unambiguous.
- **Phase 4 (Parallel Dispatch):** `Task()` dispatch pattern is verified from GSD production workflows (HIGH confidence from `execute-phase.md` and `diagnose-issues.md`).

Phases that may need investigation during execution:
- **Phase 1 (Agent Authoring):** The [CORRECTED ASSUMPTIONS] section for each brain requires reading historical consultation outputs to identify which assumptions each specific NotebookLM brain reliably gets wrong. This is knowledge-capture, not research — but it requires time with each brain before authoring its agent file.
- **Phase 3 (Smoke Tests):** MCP tool inheritance from parent session to subagent is documented as MEDIUM confidence in STACK.md ("verify tool access inheritance empirically during AGT-04"). If NotebookLM MCP tools do not automatically inherit, all 7 agent frontmatter files need `mcp__notebooklm-mcp__notebook_query` added explicitly to the `tools` list. Verify on the first smoke test before running the remaining 6.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Claude Code agent format verified from first-party plugin source (claude-plugins-official); `Task()` dispatch pattern verified from GSD production; no external packages required |
| Features | HIGH | All 11 requirements derived directly from existing skill source files and approved REQUIREMENTS.md — no external validation needed; manual workflow IS the specification |
| Architecture | HIGH | Brownfield addition; existing codebase (skill files, workflows, brain-selection.md) is the specification; data flow is directly readable from current implementation |
| Pitfalls | HIGH | Derived from codebase analysis, production skill code, real Brain #7 consultation output that pre-identified BRAIN-FEED poisoning as top gap, and Claude Code agent format inspection |

**Overall confidence:** HIGH

### Gaps to Address

- **MCP tool inheritance in subagents:** STACK.md flags this as MEDIUM confidence. Verify empirically during the first AGT-04 smoke test that `mcp__notebooklm-mcp__notebook_query` is available to dispatched brain agents. If not available, update all 7 agent frontmatter `tools` fields. One-time verification, not a blocker for Phase 1.

- **Notebook ID embedding vs. reference file tradeoff:** STACK.md recommends embedding notebook IDs directly in agent system prompts for self-sufficiency. PITFALLS.md (security section) recommends keeping them in `brain-selection.md` to avoid committing IDs to the repo. Decide before Phase 1 authoring begins — changing this after 7 agents are written requires editing all of them. Recommendation: embed IDs (they are notebook IDs, not API keys; low sensitivity) and note the decision.

- **Evaluation criteria size vs. inline vs. separate files:** STACK.md recommends embedding criteria inline (under ~500 words each). If any domain's criteria grow beyond ~400 words during Phase 1, migrate to separate `.claude/agents/mm/criteria/brain-NN-evaluation.md` files before finalizing. Start inline; refactor if needed.

---

## Sources

### Primary (HIGH confidence)
- `.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/agent-development/SKILL.md` — Claude Code subagent format spec (frontmatter fields, validation rules, system prompt design)
- `.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/agents/agent-creator.md` — working agent example with complete format including model, color, tools
- `~/.claude/get-shit-done/workflows/execute-phase.md` and `diagnose-issues.md` — `Task(subagent_type=..., prompt=...)` dispatch pattern from GSD production usage
- `.claude/skills/mm/brain-context/SKILL.md` + all 4 workflow files — manual baseline being automated; the specification for agent behavior
- `.claude/skills/mm/brain-context/references/intermediary-protocol.md` — 6-step protocol to embed in agent system prompts
- `.claude/skills/mm/brain-context/references/brain-selection.md` — notebook IDs, cascade rules, dispatch rules
- `.planning/REQUIREMENTS.md` — 11 approved requirements (AGT-01..04, FEED-01..03, BASE-01..02, DISP-01..02)
- `.planning/PROJECT.md` — v2.2 architecture vision, "intermediary protocol becomes built-in behavior" design decision

### Secondary (MEDIUM confidence)
- Training knowledge on Claude Code subagent context window constraints, parallel Agent tool dispatch behavior, and MCP tool inheritance — confirmed against production plugin examples but MCP inheritance must be verified empirically during AGT-04

---
*Research completed: 2026-03-27*
*Ready for roadmap: yes*
