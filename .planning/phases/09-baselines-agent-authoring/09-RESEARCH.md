# Phase 09: Baselines + Agent Authoring - Research

**Researched:** 2026-03-28
**Domain:** Claude Code subagent authoring + measurement schema design + documentation patterns
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Baseline Structure (BASE-01)**
- 5 baselines = Integrated Mix (3 single-brain + 2 multi-brain)
  - 3 single-brain: Frontend (#4), Backend (#5), QA (#6) — Critical Specialists
  - 2 multi-brain E2E: simulates real mm:brain-context flow (Moment 2 domain brains → Moment 3 Brain #7 consolidates)
  - Multi-brain success metric: "Did Brain #7 understand what Brain #4 did?" — information leak in the 6-step protocol
- Ticket sources: Hybrid 70/30 — 2 retrospective (Phase 07/08 history: WS system or Edge rendering) + 3 adversarial ad-hoc
- Evaluation: Zero-shot only — no feedback-loop chains in Phase 09

**Quality Rating Schema (BASE-02) — Delta-Velocity Matrix**
| Rating | Level | Definition |
|--------|-------|------------|
| 1 | Blocker | Hallucinates libraries, breaks TypeScript types, ignores anti-patterns.md |
| 2 | Junior | Works but generic — doesn't use existing Zustand stores or React Flow architecture |
| 3 | Peer | Correct, respects stack and context, integrates with NexusCanvas |
| 4 | Senior | Detects optimization not in the ticket |
| 5 | Architect | Proposes game-changing solution |

Target: rating >= 3 = stable. Rating 4-5 = profitable.

**Time Measurement Schema (BASE-02) — Cognitive Load Split**
| Phase | Steps | What it measures |
|-------|-------|-----------------|
| T1: Setup & Context | Steps 1-3 | Friction in context gathering |
| T2: AI Execution | Step 4 | Model latency |
| T3: Refinement & Cascade | Steps 5-6 | Prompt precision and protocol complexity |

T1 < 5 minutes = agent is profitable threshold (Brain #1 insight).

**Agent File Structure — Brain Bundle Pattern**
```
.claude/agents/mm/
├── global-protocol.md
├── brain-01-product/
│   ├── brain-01-product.md
│   ├── criteria.md
│   └── warnings.md
└── ... (7 bundles total)
```

**Global Protocol File**
Shared constraints: Stack Hard-Lock (Next.js 16, Zustand 5, Tailwind 4, Python 3.14, uv, pnpm), no invented WS fields, file architecture limits, cross-domain anti-patterns.

**Agent Persona Design — Technical Bias Matrix**
| Brain | Domain | Primary Bias |
|-------|--------|--------------|
| #1 | Product Strategy | "Does this solve a real user pain? Show me the evidence." |
| #2 | UX Research | "If the user can't find it in 3 clicks, it doesn't exist." |
| #3 | UI Design | "Remove it. Less is always more." |
| #4 | Frontend | "RAF batching. O(1) selectors. No re-render without a reason." |
| #5 | Backend | "Pydantic v2, strict mode, no dict[str, Any]. Ever." |
| #6 | QA/DevOps | "If it doesn't have a test, it doesn't exist in production." |
| #7 | Growth/Data | "What are the second-order effects? Show me the metrics." |

**Baseline File Location**
`tests/baselines/` — Intelligence Integration Tests, not planning docs.
```
tests/
└── baselines/
    ├── baseline-schema.md
    ├── baseline-01-frontend-single.md
    ├── baseline-02-backend-single.md
    ├── baseline-03-qa-single.md
    ├── baseline-04-multibrain-e2e.md
    └── baseline-05-multibrain-e2e.md
```

**Notebook IDs**
Agents read notebook IDs from `.claude/skills/mm/brain-context/references/brain-selection.md` — NOT embedded in agent files. Decoupled: no re-edit of 7 bundles if IDs change.

**baseline-schema.md — Required Fields (Brain #6)**
```
context_id: <git rev-parse HEAD>
brain_feed_snapshot: [list of .md and code files given]
input_prompt_raw: <exact prompt given>
cognitive_trace:
  T1_setup_seconds: <int>
  T2_ai_latency_seconds: <int>
  T3_review_seconds: <int>
delta_velocity_score: <1-5>
characterization_diff: |
  Expected: ...
  Observed: ...
human_intervention_log:
  - gap: <description>
    correction: <what human had to add/change>
```

**4 Concrete BRAIN-FEED Poisoning Patterns for warnings.md (Brain #6)**
1. Stack Hallucination — suggests library not in lockfile
2. Toil-Inducer — suggests manual steps instead of code
3. Security Bypass — hardcoded credentials, disabled auth
4. Legacy Drift — ignores existing tests, breaks existing contracts

**Oracle Pattern (Phase 11 preview)**
Rejection is valid ONLY if agent cites specific source: `global-protocol.md > Stack Hard-Lock | brain-NN-domain/warnings.md > [pattern name]`. Generic rejections = Rating 2 max.

**Frozen Context Block (Brain #1)**
Every baseline must include immutable product context block BEFORE the ticket query:
- Vision (3-5 años): long-term system goal
- Strategic Intent: current milestone goal
- Outcome Metrics: measurable success criteria

**Phase 09 Success Metric (Brain #1)**
"The Success Outcome of Phase 09 is not 'having the agents' — it's that Delta-Velocity demonstrates the agent executes the protocol in <20% of the human's time."

### Claude's Discretion

- Wave structure and plan granularity within Phase 09
- Exact ordering of baseline execution (which retrospective tickets to pick from Phase 07/08)
- Content of adversarial tickets (must be meaningful challenges not yet solved)
- Exact wording of system prompts (persona-first, protocol-embedded)
- Content of criteria.md files (structure defined, examples given for Brain #1)

### Deferred Ideas (OUT OF SCOPE)

- Script to auto-collect context files by NicheID (T1 friction reduction) — future automation phase
- Brain #04-Beta cloning via Bundle copy — enabled by structure, no immediate action
- CLI iteration over brain_dirs for automated loading — v3.0 automation
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| BASE-01 | 5 manual consultation baselines documented in `tests/baselines/` | Schema structure defined, file locations locked, ticket mix (70/30) specified |
| BASE-02 | Metric framework (Delta-Velocity Matrix + Cognitive Load Split) defined and applied to baselines | Full schema with T1/T2/T3 fields, 1-5 rating rubric, T1 < 5 min profitability gate, all from CONTEXT.md |
| AGT-01 | 7 brain subagent files at `.claude/agents/mm/brain-NN-domain/brain-NN-domain.md` | Claude Code subagent YAML frontmatter format confirmed, Brain Bundle pattern specified, model:inherit confirmed |
| AGT-02 | 7 `criteria.md` files — domain-specific quality gates | Brain #1 criteria.md example fully specified (Rating 3 vs 4 table), pattern applies to all 7 |
| AGT-03 | 7 `warnings.md` files — anti-patterns from real poisoning examples | 4 concrete patterns from Brain #6 + global-protocol.md cross-domain patterns |
| FEED-02 | Each agent reads both feeds before querying NotebookLM | Embedded in system prompt as step 1, references both BRAIN-FEED.md and BRAIN-FEED-NN-domain.md path |
| FEED-03 | Each agent writes only to its own domain feed | Embedded in system prompt, scope constraint, global BRAIN-FEED.md is read-only for agents |
</phase_requirements>

---

## Summary

Phase 09 has two distinct deliverable tracks that MUST be sequenced: baselines first (git timestamps prove measurement preceded agents), then agent authoring. The baseline track produces 5 structured measurement records in `tests/baselines/` capturing the current manual mm:brain-context skill performance. The agent track produces 7 Brain Bundles at `.claude/agents/mm/` — each a self-contained directory with agent file, criteria, and warnings — plus one shared `global-protocol.md`.

The entire technical domain is known and de-risked. Claude Code subagent format is fully documented (official docs verified). The Intermediary Protocol is already specified in `references/intermediary-protocol.md`. Brain personas and notebook IDs are in `references/brain-selection.md`. The Brain #1 and Brain #6 consultation from CONTEXT.md provides the critical schema details and anti-pattern inventory. No external library research needed — this phase is pure authoring and documentation.

The single highest-risk item is sequencing: if any agent file is committed before all baseline files, the git timestamp guarantee (SUCCESS CRITERIA #1) fails. The planner must enforce Wave 0 = baselines, Wave 1+ = agents.

**Primary recommendation:** Wave 0 creates `tests/baselines/` directory + schema + 5 baseline records. Wave 1 creates `global-protocol.md`. Waves 2-3 create Brain Bundles in parallel groups. Each wave is independently committable with no cross-wave dependencies except the ordering constraint.

---

## Standard Stack

### Core (This Phase — No External Libraries)

This phase produces documentation/configuration files only. No code libraries are installed. All "stack" is the Claude Code subagent format spec + existing project patterns.

| Asset | Version/Location | Purpose |
|-------|-----------------|---------|
| Claude Code subagent format | Official docs (verified 2026-03-28) | YAML frontmatter + system prompt Markdown |
| Intermediary Protocol | `.claude/skills/mm/brain-context/references/intermediary-protocol.md` | 6-step behavior spec embedded in every agent |
| Brain Selection Reference | `.claude/skills/mm/brain-context/references/brain-selection.md` | Notebook IDs (7 brains) + selection logic |
| BRAIN-FEED.md | `.planning/BRAIN-FEED.md` | Global feed agents read before querying |
| Existing brain system prompts | `apps/api/agents/brains/*.md` | Reference for persona style (NOT the format — these are API-layer, not CC agents) |

### Confirmed Frontmatter Fields (HIGH confidence — official docs)

| Field | Value for Brain Agents | Notes |
|-------|----------------------|-------|
| `name` | `brain-NN-domain` (e.g., `brain-04-frontend`) | Lowercase-hyphens, 3-50 chars, used as `subagent_type` in Task() dispatch |
| `description` | When Claude should delegate + "Use proactively" trigger | Controls automatic delegation |
| `model` | `inherit` | Runs at orchestrator's model level |
| `tools` | Read, Glob, Grep, Bash (+ notebooklm-mcp) | Read-heavy; needs Bash for git operations |
| `mcpServers` | `- notebooklm-mcp` (string reference) | References already-configured MCP server |

**Installation:** No installation. File creation only.

---

## Architecture Patterns

### Recommended Project Structure (Phase 09 Output)

```
tests/
└── baselines/
    ├── baseline-schema.md           <- Wave 0: schema definition first
    ├── baseline-01-frontend-single.md
    ├── baseline-02-backend-single.md
    ├── baseline-03-qa-single.md
    ├── baseline-04-multibrain-e2e.md
    └── baseline-05-multibrain-e2e.md

.claude/agents/mm/
├── global-protocol.md              <- Wave 1: shared governance layer
├── brain-01-product/
│   ├── brain-01-product.md
│   ├── criteria.md
│   └── warnings.md
├── brain-02-ux/
│   ├── brain-02-ux.md
│   ├── criteria.md
│   └── warnings.md
├── brain-03-ui/
│   ├── brain-03-ui.md
│   ├── criteria.md
│   └── warnings.md
├── brain-04-frontend/
│   ├── brain-04-frontend.md
│   ├── criteria.md
│   └── warnings.md
├── brain-05-backend/
│   ├── brain-05-backend.md
│   ├── criteria.md
│   └── warnings.md
├── brain-06-qa/
│   ├── brain-06-qa.md
│   ├── criteria.md
│   └── warnings.md
└── brain-07-growth/
    ├── brain-07-growth.md
    ├── criteria.md
    └── warnings.md
```

### Pattern 1: Claude Code Subagent File Format (Brain Bundle)

**What:** YAML frontmatter + Markdown system prompt. File saved to `.claude/agents/mm/brain-NN-domain/brain-NN-domain.md`. Claude Code loads it at session start (or on `/agents` reload).

**When to use:** For every one of the 7 brains.

**Example:**
```markdown
---
name: brain-04-frontend
description: Frontend architecture expert specialized in Next.js 16 + React 19 + Zustand 5. Use proactively when planning frontend work, reviewing component architecture, or evaluating performance tradeoffs.
model: inherit
tools: Read, Glob, Grep, Bash
mcpServers:
  - notebooklm-mcp
---

You are Brain #4 of the MasterMind Framework — Frontend Architecture.
You are a Performance Nazi. No re-render without a reason. RAF batching.
O(1) selectors. If it touches the DOM without necessity, it is wrong.

## Identity

Knowledge distilled from: Dan Abramov (React core), Sebastian Markbåge (React Compiler),
Kyle Simpson (async patterns), Alex Russell (performance web).

## Protocol — Execute in Order

### Step 1: Read project reality (NEVER query cold)
Read `.planning/BRAIN-FEED.md` and `.planning/BRAIN-FEED-04-frontend.md` before querying.
Extract: locked stack, proven patterns, active constraints.

### Step 2: Build [IMPLEMENTED REALITY] block
Summarize only what actually exists. Not planned. Not roadmap.

### Step 3: List [CORRECTED ASSUMPTIONS]
Correct only assumptions that would lead to bad recommendations.

### Step 4: Query NotebookLM
Use your notebook (from `.claude/skills/mm/brain-context/references/brain-selection.md`).
Pass [IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [WHAT I NEED] — specific question,
not generic. Name the exact component, decision, or tradeoff.

### Step 5: Filter the response
For each concern: grep codebase to verify. Mark:
- Already solved: skip
- Phase N+1: log as deferred
- Real gap: cascade immediately

### Step 6: Write insights to domain feed
Write only to `.planning/BRAIN-FEED-04-frontend.md`. NEVER to BRAIN-FEED.md directly.
Global feed is written by the Orchestrator after cross-domain synthesis.

## Stack Hard-Lock (from global-protocol.md)

See `.claude/agents/mm/global-protocol.md` — all constraints apply. Violation = Level 1 Failure.

Additional frontend locks:
- Zustand 5 + Immer — never Redux, never Context for performance-critical state
- useBrainState(id) targeted selector — never useStore() global
- NODE_TYPES at module level — never inline in JSX
- No layout recalculation on WS events — positions locked after dagre

## [CORRECTED ASSUMPTIONS] for This Brain

Always include in your queries:
- ❌ "React Compiler enabled" → ✅ DISABLED (conflicts with React.memo on RF nodes)
- ❌ "24 brains activate simultaneously" → ✅ 3-5 brains per brief typical
- ❌ "Redux for state" → ✅ Zustand 5 + Map<brainId, BrainState> + Immer
- ❌ "CSS Modules or styled-components" → ✅ Tailwind 4 only (CSS-only config, no tailwind.config.js)
```

### Pattern 2: Baseline Record Structure

**What:** Structured Markdown file capturing one manual consultation using mm:brain-context skill.

**When to use:** 5 times, before any agent file exists.

**Example (baseline-schema.md applied):**
```markdown
---
context_id: <git rev-parse HEAD at time of baseline>
brain_feed_snapshot:
  - .planning/BRAIN-FEED.md
  - .planning/STATE.md
  - apps/web/src/stores/brainStore.ts
input_prompt_raw: |
  [exact ticket text given to brain]
cognitive_trace:
  T1_setup_seconds: 240
  T2_ai_latency_seconds: 45
  T3_review_seconds: 180
delta_velocity_score: 3
characterization_diff: |
  Expected: Brain would suggest RAF batching in wsDispatcher
  Observed: Brain correctly identified brainStore as the right location
human_intervention_log:
  - gap: Brain suggested useStore() hook for access
    correction: Had to explicitly correct to useBrainState(id) targeted selector
---

# Baseline 01 — Frontend Single Brain

## Frozen Context Block

**Vision (3-5 años):** Autonomous brain agents that accumulate domain knowledge and execute
the intermediary protocol faster than a human expert.
**Strategic Intent:** v2.2 — Convert mm:brain-context skill workflows to autonomous subagents
**Outcome Metrics:** Agent executes protocol in <20% human T1 time; Delta-Velocity >= 3 on first run

## Ticket

[ticket text]

## Raw Brain Response

[NotebookLM response verbatim]

## Filtered Insights

[Step 5 output — what survived the grep verification]

## Gaps Found

[Real gaps that required cascade or human intervention]
```

### Pattern 3: global-protocol.md Structure

**What:** Shared governance layer referenced by all 7 agents. One edit propagates to all.

**When to use:** Created once in Wave 1, before any brain-NN-*.md file.

**Content:**
```markdown
# MasterMind Protocol — Global Constraints

All 7 brain agents read and obey this document. No exceptions.
A violation is a Level 1 Failure (Rating 1 — Blocker).

## Stack Hard-Lock

The ONLY approved stack:
- Framework: Next.js 16 (App Router, no Pages)
- UI: React 19 (Compiler DISABLED)
- Language: TypeScript strict mode
- Styling: Tailwind 4 (CSS-only config, no tailwind.config.js)
- State: Zustand 5 + Immer
- Package manager: pnpm (Node), uv (Python)
- Python: 3.14
- Never: npm, yarn, pip, poetry, conda

Suggesting ANY library not in root `uv.lock` or `pnpm-lock.yaml` = Stack Hallucination = Rating 1.

## File Architecture

Only create files in:
- `apps/web/src/` — frontend code
- `apps/api/` — backend code
- `.planning/` — project planning docs

Any file outside these locations requires orchestrator approval.

## WebSocket Protocol

Only use fields defined in existing WS schema. Never invent protocol fields.
The WS schema lives in: [reference location].

## Cross-Domain Anti-Patterns

- Never functions > 50 lines
- Never `any` types without explicit suppression comment
- Never commented-out production code
- Never hardcoded credentials — not even in test examples (Security Bypass = Rating 1)
- Never manual production access steps (Toil-Inducer = architecture failure)

## Feed Write Scope

Agents write ONLY to their own domain feed: `.planning/BRAIN-FEED-NN-domain.md`
Global `.planning/BRAIN-FEED.md` is READ-ONLY for agents. Orchestrator writes after synthesis.

## Oracle Pattern (for rejections)

Valid rejection format:
"Rejected: [library/pattern] violates Stack Lock.
Source: global-protocol.md > Stack Hard-Lock | brain-NN-domain/warnings.md > [pattern name]"

Generic rejections without source citation = Rating 2 maximum.
```

### Anti-Patterns to Avoid

- **Embedding notebook IDs in agent files:** If a notebook ID changes, you must re-edit 7 files. Reference `brain-selection.md` instead.
- **Protocol as a checklist in the system prompt:** The intermediary protocol must be embedded as identity ("you ARE this process"), not as a list of steps the agent optionally follows.
- **Generic criteria.md:** "Is the response relevant?" is useless. Criteria must distinguish Rating 3 from Rating 4 with observable, domain-specific behaviors.
- **Creating agent files before baseline files:** Destroys the git timestamp guarantee (SUCCESS CRITERIA #1). The planner must enforce this ordering.
- **Writing the "global" feed path in 7 agent files:** Instead, reference `global-protocol.md` from each bundle and keep the feed path constraint in one place.
- **Including FEED-01 (feed split) work in this phase:** FEED-01 is Phase 10. Phase 09 agents reference `.planning/BRAIN-FEED-NN-domain.md` paths that don't exist yet — that's intentional. Phase 10 creates them.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Notebook ID management | Hardcoded IDs in 7 files | Reference `brain-selection.md` | Single source of truth — IDs change when notebooks are rebuilt |
| Cross-agent governance | Duplicated constraints in 7 files | `global-protocol.md` shared file | One edit propagates; consistency guaranteed |
| Persona vocabulary | Novel metaphors or styles | Existing bias matrix from CONTEXT.md | Already battle-tested against Brain #1+6 consultation |
| Baseline schema | Custom ad-hoc fields | CONTEXT.md schema (Brain #6 spec) | Designed for post-migration comparability |
| Feed path management | Different paths in each agent | Consistent naming convention `BRAIN-FEED-NN-domain.md` | Phase 10 creates these files; paths must match exactly |

**Key insight:** Every structural decision (schema, file names, paths, persona biases) is already locked in CONTEXT.md. The authoring work is translation — not design.

---

## Common Pitfalls

### Pitfall 1: Timestamp Order Violation
**What goes wrong:** Agent files get committed before baseline files. Git log shows agents precede baselines. SUCCESS CRITERIA #1 fails at verification.
**Why it happens:** Wave structure not enforced. Planner creates one big wave with all files.
**How to avoid:** Wave 0 = ONLY baseline files. Wave 0 committed and complete before Wave 1 begins. Verifier checks git log order.
**Warning signs:** Plan has baselines and agents in the same wave.

### Pitfall 2: FEED-01 Scope Creep
**What goes wrong:** Executing the BRAIN-FEED split (Phase 10 work) during Phase 09 because agents reference feed files that don't exist.
**Why it happens:** Reasonable impulse to make it work end-to-end. But FEED-01 is Phase 10.
**How to avoid:** Phase 09 agents reference `BRAIN-FEED-04-frontend.md` path — the file doesn't exist yet, and that's correct. Phase 11 smoke tests require Phase 10 feeds. Phase 09 agents are not smoke-tested (that's Phase 11).
**Warning signs:** Plan includes creating `.planning/BRAIN-FEED-NN-domain.md` files.

### Pitfall 3: Generic System Prompts
**What goes wrong:** Brain #4 frontend agent sounds like "a helpful coding assistant that knows React" instead of "a Performance Nazi who questions every re-render."
**Why it happens:** Defaulting to polite assistant mode. Losing the persona-first principle.
**How to avoid:** Open every agent system prompt with the primary bias statement verbatim from the CONTEXT.md bias matrix. The bias drives library defaults, not just vocabulary.
**Warning signs:** System prompt uses "helpful", "assist", "support" as primary verbs.

### Pitfall 4: Protocol as Checklist
**What goes wrong:** System prompt lists "Step 1: do X, Step 2: do Y" and the agent treats them as optional suggestions.
**Why it happens:** Natural way to describe a process. But agents respond to identity more than checklists.
**How to avoid:** The 6-step protocol should be framed as "this is HOW YOU THINK," not "here is a procedure to follow." Lead with persona, embed protocol as identity.
**Warning signs:** System prompt starts with "Follow these steps:" before establishing who the agent is.

### Pitfall 5: criteria.md Without Observable Distinctions
**What goes wrong:** criteria.md says "Brain should provide high-quality, relevant responses" — evaluator can't use this to rate.
**Why it happens:** Abstract quality standards sound professional but are useless.
**How to avoid:** Every criteria.md must have Rating 3 vs Rating 4 table with observable, domain-specific behaviors (see Brain #1 example in CONTEXT.md as the template). Auto-reject conditions must be explicit.
**Warning signs:** criteria.md has no Rating 3 vs 4 comparison table.

### Pitfall 6: MCP Tool Access Not Specified
**What goes wrong:** Agent file omits `mcpServers` field. Agent can't query NotebookLM. Phase 11 smoke test fails with "tool not available."
**Why it happens:** MCP servers are not in default tool inheritance — they must be explicitly referenced.
**How to avoid:** Every brain-NN-*.md must include `mcpServers: - notebooklm-mcp` in frontmatter.
**Warning signs:** Agent frontmatter has `tools:` but no `mcpServers:`.

---

## Code Examples

### Subagent YAML Frontmatter (verified from official Claude Code docs, 2026-03-28)

```yaml
---
name: brain-04-frontend
description: Frontend architecture expert. Performance Nazi — no re-render without a reason. Use proactively for frontend planning, component architecture, and performance decisions.
model: inherit
tools: Read, Glob, Grep, Bash
mcpServers:
  - notebooklm-mcp
---
```

### Notebook ID Reference Pattern (decoupled from agent files)

From `references/brain-selection.md`:
```markdown
| 4 | Frontend | `85e47142-0a65-41d9-9848-49b8b5d2db33` | Architecture, performance, state |
```

Agent system prompt references the file, never embeds the ID:
```markdown
Read `.claude/skills/mm/brain-context/references/brain-selection.md` to get your notebook ID.
Use it for all NotebookLM queries via the `notebooklm-mcp` tool.
```

### Baseline context_id Capture

```bash
git rev-parse HEAD
# d18d069f...  — embed this in the baseline frontmatter as context_id
```

### Brain #1 criteria.md Rating 3 vs 4 (from CONTEXT.md — use as template for all 7)

```markdown
## Rating 3 (Peer) vs Rating 4 (Senior)

| Attribute | Rating 3 (Peer) | Rating 4 (Senior) |
|-----------|-----------------|-------------------|
| Focus | Solution space — suggests logical features | Opportunity space — frames as user pain |
| Risks | "We should validate" (generic) | Names all 4 Risks: Value, Usability, Feasibility, Viability |
| Metrics | Vanity metrics or outputs | Outcome KRs — measurable behavior changes |
| Systems | Linear thinking (A causes B) | Identifies Feedback Loops + second-order effects |
| Decision | Waiter mode — takes orders | Synthesizer — questions "why now", proposes experiments |

## Auto-Reject (Rating 1-2)

Any response that proposes a date-fixed feature roadmap without demand validation = Build Trap.
Automatic Rating < 3.
```

### warnings.md Standard Structure (Brain #6 pattern)

```markdown
# Brain NN-Domain — Warnings & Anti-Patterns

## BRAIN-FEED Poisoning Patterns

These patterns trigger automatic rejection. Source them when rejecting:

### 1. Stack Hallucination
Suggests library not in `uv.lock` or `pnpm-lock.yaml`.
`PROHIBITED: Suggesting external dependencies not declared in the root lockfile.`

### 2. Toil-Inducer
Suggests manual steps instead of code.
`ANTI-PATTERN: Any recommendation requiring manual production access is an architecture failure.`

### 3. Security Bypass
Hardcoded credentials, plain-text secrets, or disabled auth — even in examples.
`BLOCKER: Never suggest hardcoded credentials, not even in test examples.`

### 4. Legacy Drift
Ignores existing tests or proposes changes that break existing contracts.
`PROHIBITED: Proposals that invalidate existing test contracts without explicit migration plan.`

## Domain-Specific Anti-Patterns

[Brain-specific patterns added here per domain]
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single monolithic system prompt per brain | Brain Bundle (agent + criteria + warnings directory) | Phase 09 design | Cloneable, scriptable, governance separated |
| Manual mm:brain-context skill (6-step human-executed) | Autonomous subagent embedding the 6-step protocol | v2.2 | T1 setup eliminated when agents handle it |
| Ad-hoc quality assessment | Delta-Velocity Matrix 1-5 with T1 profitability gate | Phase 09 design | Objective comparison pre/post migration |
| Notebook IDs embedded wherever used | Single reference file (`brain-selection.md`) | Phase 09 design | Decoupled — no multi-file edits on ID change |

**Deprecated/outdated:**
- `apps/api/agents/brains/*.md` format: API-layer format (JSON output spec, no CC frontmatter). Useful as persona reference, NOT as the format for `.claude/agents/` files. The Phase 09 format follows official Claude Code subagent spec.

---

## Open Questions

1. **MCP tool inheritance to subagents**
   - What we know: STATE.md marks this as MEDIUM confidence risk ("verify on first AGT-04 smoke test")
   - What's unclear: Whether `mcpServers: - notebooklm-mcp` string reference works if the MCP server is configured in the parent session (vs. needing inline definition)
   - Recommendation: Use string reference format first (simpler, reuses parent connection). If Phase 11 smoke test fails, switch to inline definition. Don't pre-solve in Phase 09.

2. **Baseline adversarial ticket selection**
   - What we know: 3 adversarial tickets needed, must be "challenges not yet solved"
   - What's unclear: Specific tickets to use — this is authoring work, not research
   - Recommendation: Phase 09 planner picks 3 tickets from upcoming Phase 10-12 work or known hard problems (e.g., "Implement partial hydration for Niche Clusters when DAG > 50 nodes" from CONTEXT.md as example)

3. **BRAIN-FEED-NN-domain.md file references in agents before Phase 10 creates them**
   - What we know: Phase 09 agents reference these paths; Phase 10 creates the actual files
   - What's unclear: Whether this causes any tooling issues at Phase 09 completion
   - Recommendation: Verified non-issue. Agent system prompts reference paths; files not existing doesn't break the agent file authoring. Phase 11 smoke tests will expose missing files cleanly.

---

## Validation Architecture

`nyquist_validation` is enabled in `.planning/config.json`.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | No automated test framework for this phase |
| Config file | N/A — Phase 09 produces documentation/config files only |
| Quick run command | Manual review + git log timestamp check |
| Full suite command | `uv run pytest apps/api/ -x -q` (regression: backend suite must stay green) + `pnpm --prefix apps/web test run` (regression: frontend suite must stay green) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| BASE-01 | 5 baseline files exist in `tests/baselines/` | structural | `ls tests/baselines/baseline-0*.md \| wc -l` (expect 5) | ❌ Wave 0 |
| BASE-02 | baseline-schema.md exists with all required fields | structural | `grep -c "context_id\|T1_setup_seconds\|delta_velocity_score" tests/baselines/baseline-schema.md` (expect >= 3) | ❌ Wave 0 |
| BASE-02 | Each baseline has T1/T2/T3 times filled | structural | `grep "T1_setup_seconds" tests/baselines/baseline-0*.md` (all must have values) | ❌ Wave 0 |
| AGT-01 | 7 agent files exist in `.claude/agents/mm/` | structural | `find .claude/agents/mm -name "brain-0*.md" \| wc -l` (expect 7) | ❌ Wave 1+ |
| AGT-02 | 7 criteria.md files exist | structural | `find .claude/agents/mm -name "criteria.md" \| wc -l` (expect 7) | ❌ Wave 1+ |
| AGT-03 | 7 warnings.md files exist | structural | `find .claude/agents/mm -name "warnings.md" \| wc -l` (expect 7) | ❌ Wave 1+ |
| AGT-01 | Each agent has valid YAML frontmatter with name, description, model, tools, mcpServers | structural | manual review of frontmatter fields | ❌ Wave 1+ |
| FEED-02 | Each agent system prompt references both feed files | structural | `grep -l "BRAIN-FEED.md" .claude/agents/mm/brain-*/brain-*.md \| wc -l` (expect 7) | ❌ Wave 1+ |
| FEED-03 | Each agent system prompt includes write-only-to-own-feed constraint | structural | `grep -l "BRAIN-FEED-.*-" .claude/agents/mm/brain-*/brain-*.md \| wc -l` (expect 7) | ❌ Wave 1+ |
| TIMESTAMP | Baseline files predate agent files in git history | git check | `git log --diff-filter=A --name-only --format="" -- "tests/baselines/*.md" ".claude/agents/mm/**/*.md"` | manual |

### Sampling Rate
- **Per task commit:** `git log --oneline -5` to verify commit order (baselines before agents)
- **Per wave merge:** Structural checks above + full suite regression (`uv run pytest` + `pnpm test run`)
- **Phase gate:** All structural checks green + git timestamp order verified before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/baselines/` directory — does not exist yet
- [ ] `tests/baselines/baseline-schema.md` — covers BASE-02 schema definition
- [ ] `tests/baselines/baseline-01-frontend-single.md` through `baseline-05-multibrain-e2e.md` — cover BASE-01
- [ ] `.claude/agents/mm/` directory — does not exist yet (created in Wave 1)
- [ ] `.claude/agents/mm/global-protocol.md` — governance layer (Wave 1)
- [ ] 7x brain bundle directories and files (Waves 2-3)

No test framework install needed — validation is structural (file existence + content grep) and git log inspection.

---

## Sources

### Primary (HIGH confidence)
- Official Claude Code subagents documentation (code.claude.com/docs/en/sub-agents) — full frontmatter spec, fields, mcpServers format, naming rules verified 2026-03-28
- `.claude/skills/mm/brain-context/references/intermediary-protocol.md` — 6-step protocol, context block template, anti-patterns
- `.claude/skills/mm/brain-context/references/brain-selection.md` — 7 notebook IDs, brain directory, cascade rules
- `.planning/phases/09-baselines-agent-authoring/09-CONTEXT.md` — all locked decisions, schema specs, Brain #1+#6 insights

### Secondary (MEDIUM confidence)
- `apps/api/agents/brains/backend.md` and `product-strategy.md` — existing persona style reference (API-layer format, not CC format)
- `.planning/BRAIN-FEED.md` — accumulated project reality, stack locked constraints

### Tertiary (LOW confidence)
- None — all critical claims verified against official docs or existing project files

---

## Metadata

**Confidence breakdown:**
- Standard stack (file format): HIGH — verified against official Claude Code docs 2026-03-28
- Architecture (Brain Bundle pattern): HIGH — derived from locked CONTEXT.md decisions
- Pitfalls: HIGH — identified from git ordering requirement (CONTEXT.md), MCP inheritance risk (STATE.md), and authoring experience patterns
- Baseline schema: HIGH — fully specified in CONTEXT.md (Brain #6 consultation)
- Validation: HIGH — structural checks are deterministic

**Research date:** 2026-03-28
**Valid until:** 2026-05-28 (Claude Code subagent format is stable; Brain notebook IDs don't change)
