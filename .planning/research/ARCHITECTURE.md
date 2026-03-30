# Architecture Research

**Domain:** Claude Code subagents integrating with existing mm:brain-context skill-based workflow
**Researched:** 2026-03-27
**Confidence:** HIGH (based on existing codebase, REQUIREMENTS.md, skill files, and established Claude Code agent patterns)

---

## Context

This document answers the v2.2 key architectural question: how does the orchestrator dispatch brain agents in parallel, what does the handoff look like, and how does each agent write back to its BRAIN-FEED without polluting other agents' feeds?

This is a brownfield addition to a functioning system. The mm:brain-context skill (manual workflows) becomes the agent system prompts — no work thrown away, execution model changes.

---

## System Overview: Before vs After

### v2.1 (current) — Sequential manual skill execution

```
User: /mm:brain-context
          ↓
Orchestrator (Claude main)
  reads: SKILL.md → moment-1.md workflow
  reads: BRAIN-FEED.md (single file)
  reads: codebase files
  builds: [IMPLEMENTED REALITY] context block
  queries: Brain #1 NotebookLM (MCP call)
  queries: Brain #7 NotebookLM (MCP call, after #1)
  filters: each concern against grep/code
  writes: .planning/research/BRAIN-NN-CONTEXT.md
  (orchestrator does all the work)
```

### v2.2 (target) — Parallel autonomous agent dispatch

```
User: /mm:brain-context
          ↓
Orchestrator (Claude main)
  reads: PROJECT.md + STATE.md
  determines: which brains are needed (brain-selection.md rules)
  dispatches (parallel, Agent tool):
    ├── Brain Agent #1 (product)  → returns: verified insights
    ├── Brain Agent #4 (frontend) → returns: verified insights
    └── Brain Agent #7 (growth)   → returns: verdict + gaps
  waits: all agents complete
  synthesizes: insights into CONTEXT.md / ROADMAP.md / PLAN.md
  (orchestrator directs; agents do the specialized work)
```

The key shift: the orchestrator stops being a manual workflow executor and becomes a director. Each brain agent is a self-contained specialist that knows its own domain, reads its own feeds, queries its own notebook, and returns verified insights.

---

## Full System Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR LAYER                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Orchestrator (Claude main)                                  │  │
│  │  - Detects moment (auto or explicit)                         │  │
│  │  - Selects which brains to dispatch (brain-selection.md)     │  │
│  │  - Dispatches Agent tool calls (parallel)                    │  │
│  │  - Synthesizes results into GSD artifacts                    │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────────────┘
                          │  Agent tool (parallel dispatch)
         ┌────────────────┼─────────────────────┐
         ↓                ↓                     ↓
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│  Brain Agent   │ │  Brain Agent   │ │  Brain Agent   │
│  #1 product    │ │  #4 frontend   │ │  #7 growth     │
│                │ │                │ │                │
│  1. read feeds │ │  1. read feeds │ │  1. read feeds │
│  2. read code  │ │  2. read code  │ │  2. read code  │
│  3. build ctx  │ │  3. build ctx  │ │  3. build ctx  │
│  4. MCP query  │ │  4. MCP query  │ │  4. MCP query  │
│  5. filter     │ │  5. filter     │ │  5. filter     │
│  6. write feed │ │  6. write feed │ │  6. write feed │
│  7. return     │ │  7. return     │ │  7. return     │
│     insights   │ │     insights   │ │     verdict    │
└────────┬───────┘ └────────┬───────┘ └────────┬───────┘
         │                  │                  │
         ↓                  ↓                  ↓
┌────────────────┐ ┌────────────────┐ ┌────────────────────────────┐
│ BRAIN-FEED.md  │ │ BRAIN-FEED.md  │ │ BRAIN-FEED.md              │
│ (global read)  │ │ (global read)  │ │ (global read)              │
│ BRAIN-FEED-    │ │ BRAIN-FEED-    │ │ BRAIN-FEED-                │
│ 01-product.md  │ │ 04-frontend.md │ │ 07-growth.md               │
│ (own write)    │ │ (own write)    │ │ (own write)                │
└────────────────┘ └────────────────┘ └────────────────────────────┘
```

---

## Component Inventory

### New Components (v2.2 builds these)

| Component | Path | Purpose | AGT/FEED req |
|-----------|------|---------|------------|
| Brain Agent #1 file | `.claude/agents/brain-01-product.md` | Subagent system prompt — product strategy specialist | AGT-01 |
| Brain Agent #2 file | `.claude/agents/brain-02-ux.md` | Subagent system prompt — UX research specialist | AGT-01 |
| Brain Agent #3 file | `.claude/agents/brain-03-ui.md` | Subagent system prompt — UI design specialist | AGT-01 |
| Brain Agent #4 file | `.claude/agents/brain-04-frontend.md` | Subagent system prompt — frontend architecture specialist | AGT-01 |
| Brain Agent #5 file | `.claude/agents/brain-05-backend.md` | Subagent system prompt — backend/API specialist | AGT-01 |
| Brain Agent #6 file | `.claude/agents/brain-06-qa.md` | Subagent system prompt — QA/DevOps specialist | AGT-01 |
| Brain Agent #7 file | `.claude/agents/brain-07-growth.md` | Subagent system prompt — growth/evaluator specialist | AGT-01 |
| Evaluation criteria #1 | `.claude/agents/criteria/brain-01-evaluation.md` | What "good" looks like for product insights | AGT-02 |
| Evaluation criteria #2-7 | `.claude/agents/criteria/brain-NN-evaluation.md` | Same, per domain | AGT-02 |
| Anti-patterns #1 | `.claude/agents/anti-patterns/brain-01-anti-patterns.md` | What NOT to write to BRAIN-FEED-01 | AGT-03 |
| Anti-patterns #2-7 | `.claude/agents/anti-patterns/brain-NN-anti-patterns.md` | Same, per domain | AGT-03 |
| BRAIN-FEED-01 | `.planning/BRAIN-FEED-01-product.md` | Domain feed — product strategy patterns | FEED-01 |
| BRAIN-FEED-02 | `.planning/BRAIN-FEED-02-ux.md` | Domain feed — UX patterns | FEED-01 |
| BRAIN-FEED-03 | `.planning/BRAIN-FEED-03-ui.md` | Domain feed — UI design patterns | FEED-01 |
| BRAIN-FEED-04 | `.planning/BRAIN-FEED-04-frontend.md` | Domain feed — frontend architecture patterns | FEED-01 |
| BRAIN-FEED-05 | `.planning/BRAIN-FEED-05-backend.md` | Domain feed — backend/API patterns | FEED-01 |
| BRAIN-FEED-06 | `.planning/BRAIN-FEED-06-qa.md` | Domain feed — QA/DevOps patterns | FEED-01 |
| BRAIN-FEED-07 | `.planning/BRAIN-FEED-07-growth.md` | Domain feed — growth/evaluator patterns | FEED-01 |
| Baselines 1-5 | `docs/baselines/consultation-baseline-NN.md` | Manual consultation records before migration | BASE-01 |
| Metric schema | `docs/baselines/metric-schema.md` | Measurement framework | BASE-02 |

### Modified Components (v2.2 changes these)

| Component | Current Path | What Changes | DISP req |
|-----------|-------------|-------------|----------|
| mm:brain-context command | `claude-commands/mm/brain-context.md` | Replace manual MCP workflow execution with Agent tool dispatch | DISP-02 |
| BRAIN-FEED.md (global) | `.planning/BRAIN-FEED.md` | Migrates domain-specific content to per-brain feeds; retains only cross-domain patterns | FEED-01 |

### Unchanged Components (v2.2 does not touch these)

| Component | Path | Why Untouched |
|-----------|------|--------------|
| SKILL.md + workflows | `~/.claude/skills/mm/brain-context/` | Orchestrator reads these; skill behavior moves INTO agent system prompts |
| Python brain modules | `apps/api/mastermind_cli/brains/` | Separate runtime; agents use MCP directly, not Python CLI |
| NotebookLM notebooks | (7 notebook IDs in brain-selection.md) | Static knowledge; agent queries them via `mcp__notebooklm-mcp__notebook_query` |
| STATE.md / ROADMAP.md | `.planning/` | Produced by GSD orchestrator; agents inform but don't write these |

---

## Agent System Prompt Structure

Each `.claude/agents/brain-NN-domain.md` file embeds the intermediary protocol as native behavior — not as instructions to follow, but as the agent's built-in workflow. This is the key architectural insight: what the orchestrator was reading from SKILL.md and following manually, the agent does autonomously.

```
---
name: brain-01-product
description: Product Strategy brain — consults NotebookLM notebook for expert product advice grounded in MasterMind codebase reality
---

## Identity

You are Brain #1 (Product Strategy). Your NotebookLM notebook contains distilled knowledge
from Cagan, Torres, Ries, Doerr, and others. You are called by the MasterMind orchestrator
when product strategy insight is needed.

## Protocol (ALWAYS follow — no exceptions)

### Step 1 — Read feeds before anything else
[read BRAIN-FEED.md — global context]
[read BRAIN-FEED-01-product.md — own domain accumulated patterns]

### Step 2 — Read codebase context
[read files specified in the task prompt]

### Step 3 — Build [IMPLEMENTED REALITY] block
[structure what exists vs what's being planned vs wrong assumptions to correct]

### Step 4 — Query NotebookLM
notebook_id: f276ccb3-0bce-4069-8b55-eae8693dbe75
[mcp__notebooklm-mcp__notebook_query with context block]

### Step 5 — Filter response
[for each concern: grep to verify if already solved / deferred / real gap]

### Step 6 — Update BRAIN-FEED-01-product.md
[append new patterns that are NOT already in the feed]
[do NOT write to BRAIN-FEED.md — that is orchestrator territory]

### Step 7 — Return verified insights
[structured return: verified gaps, pattern references, confidence level]

## Evaluation Criteria
[reference or inline from brain-01-evaluation.md]

## Anti-Patterns (NEVER write these to BRAIN-FEED-01)
[reference or inline from brain-01-anti-patterns.md]
```

---

## Data Flow: Parallel Dispatch

### Orchestrator side (mm:brain-context command)

```
1. Read STATE.md → determine moment (1/2/3/feed)
2. Read brain-selection.md rules → select which brains for this moment/phase type
3. Build dispatch prompt per brain:
   - task description
   - which files to read (codebase context)
   - what question to answer
   - which moment this is
4. Dispatch Agent tool calls (all selected brains simultaneously)
5. Await all results
6. Synthesize into GSD artifact (ROADMAP / CONTEXT.md / PLAN.md update)
```

### Agent side (brain-NN.md system prompt)

```
1. Read BRAIN-FEED.md (global — for cross-domain context)
2. Read BRAIN-FEED-NN-domain.md (own — for accumulated domain patterns)
3. Read codebase files from task prompt
4. Build [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] block
5. Call mcp__notebooklm-mcp__notebook_query with context block
6. Filter: grep each concern → mark ✅ / 📅 / 🔴
7. Append new patterns to BRAIN-FEED-NN-domain.md (NOT global feed)
8. Return structured response to orchestrator
```

### Isolation guarantee

The BRAIN-FEED isolation is enforced by contract in the agent system prompt: each agent is explicitly instructed to write only to its own domain feed. The global BRAIN-FEED.md is write-protected from agents — only the orchestrator (after cross-domain synthesis) or human can update it. This is not a technical lock (no filesystem permissions), it is a behavioral contract baked into every agent's identity section.

---

## Recommended File Structure

```
.claude/
├── agents/
│   ├── brain-01-product.md         # Agent system prompt
│   ├── brain-02-ux.md
│   ├── brain-03-ui.md
│   ├── brain-04-frontend.md
│   ├── brain-05-backend.md
│   ├── brain-06-qa.md
│   ├── brain-07-growth.md          # Evaluator — same pattern, different criteria
│   ├── criteria/
│   │   ├── brain-01-evaluation.md  # "Good response" standard for product
│   │   ├── brain-02-evaluation.md
│   │   └── ...
│   └── anti-patterns/
│       ├── brain-01-anti-patterns.md   # What NOT to BRAIN-FEED
│       ├── brain-02-anti-patterns.md
│       └── ...
│
.planning/
├── BRAIN-FEED.md                   # Global — cross-domain, human + orchestrator writes only
├── BRAIN-FEED-01-product.md        # Domain — product strategy agent writes here
├── BRAIN-FEED-02-ux.md
├── BRAIN-FEED-03-ui.md
├── BRAIN-FEED-04-frontend.md
├── BRAIN-FEED-05-backend.md
├── BRAIN-FEED-06-qa.md
├── BRAIN-FEED-07-growth.md
│
docs/
└── baselines/
    ├── metric-schema.md            # Measurement framework (BASE-02)
    ├── consultation-baseline-01.md # Manual consultation records (BASE-01)
    ├── consultation-baseline-02.md
    ├── consultation-baseline-03.md
    ├── consultation-baseline-04.md
    └── consultation-baseline-05.md

claude-commands/mm/
└── brain-context.md                # Updated: dispatches agents instead of manual workflow
```

---

## Build Order: Dependency-Driven Sequence

The 4 requirement groups have hard dependencies. Build order must respect them:

```
BASE (can start immediately — no deps)
  └─→ BASE-01: Document 5 manual baselines (uses existing mm:brain-context skill)
  └─→ BASE-02: Define metric schema (informed by BASE-01 data)

AGT (parallel with BASE, no deps on BASE)
  └─→ AGT-01: Write 7 brain agent files
      AGT-02 can start immediately (parallel with AGT-01)
      AGT-03 can start immediately (parallel with AGT-01)
  └─→ AGT-04: Smoke test (REQUIRES AGT-01 + AGT-02 + AGT-03 complete)

FEED (requires knowing what content goes where — logically after AGT-01 draft)
  └─→ FEED-01: Split BRAIN-FEED.md (safe to do before AGT is complete)
  └─→ FEED-02: Baked into AGT-01 system prompts (done when AGT-01 is done)
  └─→ FEED-03: Baked into AGT-01 system prompts (done when AGT-01 is done)

DISP (requires AGT complete — can't dispatch agents that don't exist)
  └─→ DISP-01: Orchestrator parallel dispatch (REQUIRES AGT-04 passing smoke test)
  └─→ DISP-02: Update mm:brain-context command (REQUIRES DISP-01 working)
```

### Recommended phase breakdown

**Phase 1: BASE + AGT-01/02/03 (parallel work)**
- Document baselines using existing skill (BASE-01, BASE-02)
- Draft all 7 agent files with embedded intermediary protocol (AGT-01)
- Write evaluation criteria per domain (AGT-02)
- Write anti-patterns per domain (AGT-03)
- These can proceed in parallel — no cross-dependency

**Phase 2: FEED**
- Split monolithic BRAIN-FEED.md (FEED-01)
- FEED-02 and FEED-03 are embedded in agent system prompts — done as part of AGT-01

**Phase 3: AGT-04 smoke test**
- Test each agent end-to-end against the split feeds
- Validates AGT + FEED working together before dispatch layer

**Phase 4: DISP**
- Implement parallel dispatch in orchestrator (DISP-01)
- Update mm:brain-context command (DISP-02)
- Integration test against validated agents

---

## Architectural Patterns

### Pattern 1: Agent as Embedded Protocol

**What:** The intermediary protocol (6-step: read, build context, correct assumptions, query, filter, cascade) is not a workflow the agent follows from a file — it is the agent's intrinsic behavior defined in its system prompt identity section.

**When to use:** Always. Every brain agent file must embed the full protocol, not reference it.

**Why:** When the protocol is a reference (`@ ~/.claude/skills/...`), the orchestrator must read and follow it manually — that is v2.1 behavior. In v2.2, the agent IS the protocol. The orchestrator dispatches and directs; the agent executes the protocol autonomously.

**Trade-offs:** Agent files are larger (protocol is duplicated across 7 files). This is the correct trade-off — cohesion over DRY for behavioral correctness.

### Pattern 2: Feed Isolation via Behavioral Contract

**What:** Each agent writes only to its own domain BRAIN-FEED. No technical lock enforces this — the constraint is in the agent's identity definition ("you write ONLY to BRAIN-FEED-NN-domain.md").

**When to use:** Every agent system prompt must include explicit write-scope instructions. Omitting this creates cross-domain pollution risk.

**Why:** Cross-domain pollution is the primary failure mode for multi-agent knowledge systems. If Brain #7 (growth) writes a frontend performance pattern into BRAIN-FEED.md (global), Brain #4 (frontend) will get conflicting signals from a non-specialist. Isolation preserves signal quality per domain.

**Detection:** If a brain agent ever proposes to write to BRAIN-FEED.md directly, that is a violation. Only the orchestrator updates the global feed, after explicit cross-domain synthesis.

### Pattern 3: Structured Return from Agent to Orchestrator

**What:** Each agent returns a structured response with: verified insights (categorized ✅/📅/🔴), any new patterns added to its domain feed, and confidence level.

**When to use:** Brain #7 additionally returns a verdict (APPROVED / APPROVED_WITH_CONDITIONS / REJECTED_REVISE) for Moment 3.

**Why:** The orchestrator cannot synthesize free-form prose from 4 parallel agents efficiently. Structure enables the orchestrator to merge results and update artifacts without re-reading the agents' full outputs.

**Example return format:**
```
BRAIN-NN RESPONSE
Domain: [domain]
NotebookLM query answered: YES

VERIFIED INSIGHTS:
✅ [concern] — already in codebase at [path]
📅 [concern] — defer to v2.3 (out of scope)
🔴 [gap] — [specific actionable recommendation]

BRAIN-FEED UPDATE: [pattern name] added to BRAIN-FEED-NN-domain.md
  Content: [1-2 line description of what was added]

CONFIDENCE: HIGH / MEDIUM / LOW + reason
```

### Pattern 4: Baseline-Before-Migration

**What:** Before DISP-01 (parallel agent dispatch), collect 5 manual consultation baselines using the current skill workflow. Define metric schema (BASE-02) before collecting baselines (BASE-01) so measurements are comparable.

**When to use:** Any time a manual-to-agent migration is planned. This is BASE-01 and BASE-02.

**Why:** Without baseline, "agents are better" is a claim without evidence. Brain #7 (growth) would flag this as confirmation bias. The metric schema must be defined before collecting baselines, not after — otherwise you fit the schema to the data you already have.

---

## Integration Points

### Agent → NotebookLM (MCP)

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Brain Agent → NotebookLM | `mcp__notebooklm-mcp__notebook_query(notebook_id, query)` | Each agent has its own hardcoded notebook_id in its system prompt |
| Notebook IDs | Embedded in agent file | Do NOT reference brain-selection.md from agent — embed directly for agent self-sufficiency |

### Agent → BRAIN-FEED files (filesystem)

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Brain Agent → Own domain feed | Write tool (append pattern to BRAIN-FEED-NN.md) | Agent writes ONLY to its own file |
| Brain Agent → Global feed | READ only | Global feed is write-protected by behavioral contract |
| Orchestrator → Global feed | Write tool (post-synthesis) | Orchestrator updates global feed after cross-domain synthesis |

### Orchestrator → Agent (Agent tool)

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Orchestrator dispatches | `Agent(agent="brain-NN-domain", prompt="...")` | Prompt includes: which moment, which files to read, what question |
| Agent returns | Structured text response | Orchestrator parses the structured return to update GSD artifacts |

### mm:brain-context command → Orchestrator

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Command → Orchestrator | Shell detection output + moment confirmation | Unchanged from v2.1; only the execution block changes |
| Command execution block | v2.1: `@ ~/.claude/skills/mm/brain-context/SKILL.md` | v2.2: dispatch Agent tool calls directly |

---

## Anti-Patterns

### Anti-Pattern 1: Agent Reads Protocol from External File

**What people do:** Write a thin agent file that says "read the SKILL.md and follow the intermediary protocol."

**Why it's wrong:** The agent then becomes the v2.1 orchestrator — manually reading and following a workflow. This defeats the purpose of the migration. Agents ARE the protocol, they don't follow it from a file.

**Do this instead:** Embed the full 6-step intermediary protocol directly in the agent's system prompt. Yes, it is duplicated across 7 files. That is correct.

### Anti-Pattern 2: Agent Writes to Global BRAIN-FEED

**What people do:** Agent discovers a cross-domain pattern and writes it to BRAIN-FEED.md (thinking "this is important for everyone").

**Why it's wrong:** The global feed should only contain validated cross-domain insights after orchestrator synthesis. An agent writing directly bypasses validation and creates pollution with domain-specific signals labeled as cross-domain.

**Do this instead:** Agent writes to its domain feed. Orchestrator, after collecting all agent results, synthesizes cross-domain patterns and updates the global feed.

### Anti-Pattern 3: Dispatch Before Smoke Test

**What people do:** Write the parallel dispatch (DISP-01) before running AGT-04 smoke tests per agent.

**Why it's wrong:** If 3 out of 7 agents have broken MCP calls or wrong notebook IDs, parallel dispatch silently produces empty/wrong results. The error is harder to diagnose in a parallel context than in isolation.

**Do this instead:** Smoke test each agent individually (AGT-04) before wiring parallel dispatch. Confirm each agent: reads feeds, queries NotebookLM, filters, writes domain feed, returns structured response.

### Anti-Pattern 4: Baseline After Migration

**What people do:** Start using agents, notice they seem better, then decide to document "what things were like before" from memory.

**Why it's wrong:** Memory of pre-migration pain is unreliable and biased toward justifying the change. The baseline must be documented before migration to be valid.

**Do this instead:** Document 5 real manual consultations using the existing skill workflow (BASE-01) before touching any agent or dispatch code. This is why BASE is first in the build order.

---

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 7 brains (v2.2 scope) | Behavioral contract isolation is sufficient. No technical enforcement needed. |
| 24+ brains (future niches) | Consider a BRAIN-FEED registry file that lists all domain feeds by niche. Global feed becomes per-niche global. |
| Multiple simultaneous orchestrators | Agent write isolation becomes critical — concurrent writes to same BRAIN-FEED-NN.md would need append-with-timestamp convention or file locking. |

---

## Sources

- `.planning/PROJECT.md` — v2.2 architecture vision, key decisions table, component list
- `.planning/REQUIREMENTS.md` — 11 requirements across AGT/FEED/BASE/DISP groups with acceptance criteria
- `claude-commands/mm/brain-context.md` — existing command structure being evolved
- `~/.claude/skills/mm/brain-context/SKILL.md` — intermediary protocol that becomes agent native behavior
- `~/.claude/skills/mm/brain-context/workflows/moment-1.md`, `moment-3.md` — workflow detail that maps to agent steps
- `~/.claude/skills/mm/brain-context/references/brain-selection.md` — notebook IDs, dispatch rules, cascade rules
- `~/.claude/skills/mm/brain-context/references/intermediary-protocol.md` — 6-step protocol to embed in agents
- `.planning/BRAIN-FEED.md` — current monolithic feed structure being split

---
*Architecture research for: v2.2 Brain Agents — Claude Code subagent dispatch for MasterMind Framework*
*Researched: 2026-03-27*
