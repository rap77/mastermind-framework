# Phase 09: Baselines + Agent Authoring - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Capture 5 pre-migration baseline consultations (manual mm:brain-context skill) and author all 7 brain subagents as Brain Bundles with embedded intermediary protocol, domain-specific evaluation criteria, anti-patterns, and a shared global protocol file. No dispatch wiring — that's Phase 12.

</domain>

<decisions>
## Implementation Decisions

### Baseline Structure (BASE-01)

- **5 baselines = Integrated Mix (3 single-brain + 2 multi-brain)**
  - 3 single-brain: test individual specialist identity (Frontend, Backend, QA — the "Critical Specialists")
  - 2 multi-brain E2E: simulates real mm:brain-context flow (Moment 2 domain brains → Moment 3 Brain #7 consolidates)
  - Multi-brain success metric: "Did Brain #7 understand what Brain #4 did?" — information leak in the 6-step protocol

- **Ticket sources: Hybrid 70/30**
  - 2 retrospective tickets (30%) from Phase 07/08 history — WS system or Edge rendering. Purpose: regression test, known ground truth for calibration
  - 3 adversarial ad-hoc tickets (70%) — new challenges not yet solved (e.g., "Implement partial hydration for Niche Clusters when DAG > 50 nodes"). Purpose: validate agent reasoning under unknown territory

- **Evaluation: Zero-shot only** — no feedback-loop chains in Phase 09

### Quality Rating Schema (BASE-02) — Delta-Velocity Matrix

| Rating | Level | Definition |
|--------|-------|------------|
| 1 | Blocker | Hallucinates libraries, breaks TypeScript types, ignores anti-patterns.md. Unusable. |
| 2 | Junior | Works but generic (ChatGPT-basic). Doesn't use existing Zustand stores or React Flow architecture. Full refactor needed. |
| 3 | Peer | Correct, respects stack and context, integrates with NexusCanvas. PR-ready with minor tweaks. |
| 4 | Senior | Detects optimization not in the ticket (e.g., critical useMemo or unasked WS error handling). Improves codebase. |
| 5 | Architect | Proposes game-changing solution (e.g., Dynamic DAG optimization reducing DOM load 40%). Unlocks next roadmap phase. |

Target: rating ≥ 3 = system is stable. Rating 4-5 = system is profitable.

### Time Measurement Schema (BASE-02) — Cognitive Load Split

| Phase | Steps | What it measures |
|-------|-------|-----------------|
| T1: Setup & Context | Steps 1-3 (read BRAIN-FEED, build [IMPLEMENTED REALITY], [CORRECTED ASSUMPTIONS]) | Friction in context gathering — candidate for scripting |
| T2: AI Execution | Step 4 (NotebookLM query + wait) | Model latency |
| T3: Refinement & Cascade | Steps 5-6 (filter, cascade gaps, write CONTEXT.md) | Prompt precision and protocol complexity |

Diagnostic: if T1 is high → need collection script. If T3 is high → cascade protocol is too manual.

### Agent File Structure — Brain Bundle Pattern

Each brain is a self-contained directory:

```
.claude/agents/mm/
├── global-protocol.md              ← shared across all 7 agents
├── brain-01-product/
│   ├── brain-01-product.md         ← Claude Code agent file (YAML frontmatter + system prompt)
│   ├── criteria.md                 ← domain-specific evaluation criteria
│   └── warnings.md                 ← anti-patterns (domain-specific rejections)
├── brain-04-frontend/
│   ├── brain-04-frontend.md
│   ├── criteria.md
│   └── warnings.md
└── ... (7 bundles total)
```

Brain Bundle rationale: clone brain → copy folder. Future scripts iterate `for brain_dir in agents_path`. Editor shows clean tree.

### Global Protocol File (.claude/agents/mm/global-protocol.md)

Shared constraints all 7 agents read — the "MasterMind Protocol":
- **Stack Hard-Lock**: Only project-approved tools (Next.js 16, Zustand 5, Tailwind 4, Python 3.14, uv, pnpm). Any suggestion outside = Level 1 Failure (hallucination)
- **No invented WS fields**: Only fields defined in existing schema — prohibit inventing WebSocket protocol fields
- **File architecture**: Prohibit creating files outside `src/` or `.planning/` without orchestrator approval
- **Cross-domain anti-patterns**: Never functions > 50 lines, never `any` types ignored, no commented-out code

Domain-specific criteria stay in each brain's `criteria.md` (< 500 words inline for speed).

### Agent Persona Design — Technical Bias Matrix

Agents are **specialized experts with technical bias**, not friendly assistants. Each has a defining technical obsession:

| Brain | Domain | Persona Archetype | Primary Bias |
|-------|--------|-------------------|--------------|
| #1 | Product Strategy | Discovery Ruthless | "Does this solve a real user pain? Show me the evidence." |
| #2 | UX Research | Flow Absolutist | "If the user can't find it in 3 clicks, it doesn't exist." |
| #3 | UI Design | Minimalist Nazi | "Remove it. Less is always more. Framer-Motion only when it adds meaning." |
| #4 | Frontend | Performance Nazi | "RAF batching. O(1) selectors. No re-render without a reason." |
| #5 | Backend | Type-Safety Zealot | "Pydantic v2, strict mode, no `dict[str, Any]`. Ever." |
| #6 | QA/DevOps | Reliability Fundamentalist | "If it doesn't have a test, it doesn't exist in production." |
| #7 | Growth/Data (Evaluator) | Systems Thinker | "What are the second-order effects? Show me the metrics." |

The persona drives default library choices, not just vocabulary. Brain #4 defaults to Zustand + Immer, never Redux. Brain #5 defaults to asyncio.TaskGroup, never Celery.

### Baseline File Location

`tests/baselines/` — baselines are **Intelligence Integration Tests**, not planning documents or user-facing docs. Located in `tests/` to signal they're part of the quality pipeline.

```
tests/
└── baselines/
    ├── baseline-schema.md           ← schema definition (Delta-Velocity + Cognitive Split)
    ├── baseline-01-frontend-single.md
    ├── baseline-02-backend-single.md
    ├── baseline-03-qa-single.md
    ├── baseline-04-multibrain-e2e.md
    └── baseline-05-multibrain-e2e.md
```

### Notebook IDs

Agents read notebook IDs from `.claude/skills/mm/brain-context/references/brain-selection.md` — NOT embedded in agent files. Rationale: decoupled, no re-edit of 7 bundles if IDs change. (Decided: 2026-03-27)

</decisions>

<specifics>
## Specific Ideas

- "El agente de Frontend debería ser un 'Performance Nazi'" — persona with strong technical bias, not a polite assistant
- "Si un cerebro saca constantemente 3, el sistema es estable. Si saca 4 o 5, el sistema es rentable" — the target for post-migration comparison
- Retrospective tickets from Phase 07/08 serve as "seniority calibration" — compare agent output against code we already wrote
- Ad-hoc adversarial tickets can become real work for Phase 10+ if the agent output is good (bonus)
- `tests/baselines/` signals quality pipeline, not documentation
- "MasterMind Protocol" global file acts as governance layer — one edit propagates to all 7 agents

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.claude/skills/mm/brain-context/references/intermediary-protocol.md` — the 6-step protocol IS the agent behavior spec. Every agent embeds this as identity, not as a checklist to follow.
- `.claude/skills/mm/brain-context/references/brain-selection.md` — notebook IDs + cascade rules. Agents read this to get their own notebook ID.
- `.planning/BRAIN-FEED.md` — current monolithic feed. Agents read this (global feed) before querying. Split happens in Phase 10.
- `.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/` — Claude Code agent file format spec (YAML frontmatter: name, description, model, color, tools)

### Established Patterns
- Claude Code agent `name` field must be `brain-NN-domain` format (lowercase-hyphens, 3-50 chars) — used as `subagent_type` in Task() dispatch
- `model: inherit` for all brain agents — run at orchestrator's model level
- Agent system prompts: persona-first, protocol-embedded, not step-list-based

### Integration Points
- `mm:brain-context` command (`.claude/commands/mm/brain-context.md`) — will be updated in Phase 12 to dispatch these agents. Phase 09 creates the agents; Phase 12 wires the dispatch.
- `tests/` directory — baselines live here as intelligence integration tests

</code_context>

<deferred>
## Deferred Ideas

- Script to auto-collect context files by NicheID (T1 friction reduction) — noted for future automation phase
- Brain #04-Beta cloning via Bundle copy — enabled by structure, no immediate action
- CLI iteration over brain_dirs for automated loading — v3.0 automation

</deferred>

---

*Phase: 09-baselines-agent-authoring*
*Context gathered: 2026-03-27*
