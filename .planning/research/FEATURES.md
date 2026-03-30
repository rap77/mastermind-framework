# Feature Research: v2.2 Brain Agents

**Domain:** Claude Code subagent specialization — autonomous brain consultation system
**Researched:** 2026-03-27
**Confidence:** HIGH (based on mm:brain-context skill source, REQUIREMENTS.md, PROJECT.md, and direct analysis of the existing manual workflow that agents will replace)

---

## Context: What v2.1 Built (Do Not Re-Build)

The `mm:brain-context` skill and its 4 workflows are the **manual baseline** v2.2 automates. Every agent system prompt is a direct evolution of the workflow it replaces:

| Manual Workflow | What It Does | Becomes |
|----------------|-------------|---------|
| `moment-1.md` | Read reality → build context block → query Brain #1 + #7 → filter → synthesize into ROADMAP input | DISP-01: orchestrator dispatches Brain-01 + Brain-07 agents in parallel |
| `moment-2.md` | Select domain brains → build [IMPLEMENTED REALITY] → query all in parallel → filter → write CONTEXT.md | DISP-02: mm:brain-context dispatches domain brain agents via Agent tool |
| `moment-3.md` | Build full context → query Brain #7 → filter → cascade real gaps → iterate max 3 → update PLAN.md | Brain-07 agent validates plan natively, 3-iteration loop built in |
| `update-brain-feed.md` | Read phase artifacts → extract patterns → distill into BRAIN-FEED.md | Agent writes own domain feed after consultation; no external trigger needed |

**Key insight from PROJECT.md:** "Brains (NotebookLM) are static knowledge — they never learn. The 'learning' happens in the intermediary (Claude) via accumulated BRAIN-FEED context." The agent IS the intermediary. The skill workflow becomes the agent's native behavior.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features that, if missing, make the agent system feel broken or indistinguishable from the manual workflow.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Embedded intermediary protocol in each agent system prompt | Without it, agents query NotebookLM cold — same failure mode the skill's `querying-without-code-context` pitfall documents | MEDIUM | 6 steps: read BRAIN-FEED → build [IMPLEMENTED REALITY] → build [CORRECTED ASSUMPTIONS] → query with delta → filter each concern → cascade real gaps. Not optional shorthand |
| Read BRAIN-FEED.md (global) before querying | The skill enforces this as step 1 with explicit anti-pattern: "Each consultation starts from zero context = WRONG". Without this, the agent starts blind every time | LOW | Each agent system prompt must include explicit read instruction for `.planning/BRAIN-FEED.md` before any query |
| Read domain BRAIN-FEED-NN.md before querying | The per-brain split is the entire point of FEED-01. If agents skip their domain feed, accumulated domain expertise is inaccessible | LOW | Separate from global feed — agent reads both, not one |
| Write only to own domain feed after consultation | Without this boundary, agents contaminate each other's domain knowledge. A Frontend agent writing to the Backend feed is BRAIN-FEED poisoning | LOW | Agents must NOT touch `.planning/BRAIN-FEED.md` (global) or other domains' feeds |
| Codebase verification before returning insights | The skill step 5 "FILTER the response" is non-negotiable. An agent that returns unverified NotebookLM output is worse than useless — it pollutes planning with hallucinated gaps | HIGH | Agent must grep/read code for every concern before marking it ✅ / 📅 / 🔴 |
| Domain-specific [CORRECTED ASSUMPTIONS] | Brain #4 (Frontend) makes predictably wrong assumptions about React Compiler, inline NODE_TYPES, etc. Brain #5 (Backend) makes wrong assumptions about FastAPI setup. Each agent needs pre-baked corrections from the domain's known error patterns | MEDIUM | Not generic. Each agent's system prompt lists the 3-5 assumptions its specific brain reliably gets wrong |
| Smoke test end-to-end for each agent (AGT-04) | If an agent can't complete the 6-step protocol against a real phase, it's not done. "Files exist" is not acceptance | MEDIUM | One real consultation per agent, not a format check |

### Differentiators (What Makes Agents Better Than the Manual Skill)

Features that create measurable improvement over the `mm:brain-context` skill workflow. If an agent can't demonstrably beat the manual workflow on at least one dimension, there was no point shipping v2.2.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Parallel dispatch from orchestrator (DISP-01) | Manual workflow runs brains sequentially — Brain #2 then #3 then #4 takes ~15 min. Parallel dispatch runs all domain brains simultaneously. Time savings compounds per phase | MEDIUM | Orchestrator uses Claude's Agent tool with multiple parallel invocations. Brain #7 still runs last (it validates the others) |
| Accumulated domain expertise per brain (FEED-01 + FEED-02) | Manual BRAIN-FEED is flat and global — all 7 brains read the same context soup. Per-brain feeds let Brain #4 (Frontend) accumulate React patterns across 10 phases without Backend noise polluting it | MEDIUM | Quality of context blocks improves phase over phase. The "first consultation = ground truth" problem disappears after 3-4 phases |
| evaluation-criteria.md per domain (AGT-02) | Manual filtering depends entirely on the operator's judgment: "is this a real gap or generic advice?". With explicit criteria, the agent filters consistently. Brain #3 (UI) knows exactly what a "good visual design recommendation" looks like vs. generic theory | MEDIUM | 7 files — one per domain. Defines specific quality gates: "must reference specific CSS tokens, not principles", "must reference specific Lucide icon names", etc. |
| anti-patterns.md per domain (AGT-03) | Manual BRAIN-FEED has an anti-patterns section but it's codebase-focused (tried and rejected). Per-brain anti-patterns are domain knowledge: what types of NotebookLM responses should NEVER enter the BRAIN-FEED | MEDIUM | Manual curation only in v2.2. Agent reads anti-patterns.md before writing to BRAIN-FEED. Prevents poisoning at the source |
| Baseline measurement (BASE-01 + BASE-02) | Without baselines, "agents are better" is a belief, not a fact. 5 documented consultations create the comparison point for time, gap quality, and re-consultation count | LOW | 5 consultations documented before migration. Metric schema: time-per-consultation, gap-count, re-consultation-count, quality-rating 1-5 |
| BRAIN-FEED self-update after each consultation | Manual workflow: operator runs `mm:brain-context feed` explicitly post-phase. Agent workflow: agent updates domain feed automatically as part of every consultation. Nothing falls through the cracks | LOW | Write instruction is built into agent system prompt at step 6 |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Auto-pruning BRAIN-FEED entries (removing stale ones) | "The feed will grow forever" / "Old patterns become outdated" | v2.2 has no validation mechanism to know what's stale vs. intentionally kept. Wrong pruning removes hard-won invariants like "React Compiler: DISABLED". Over-engineering for a problem that doesn't exist yet in v2.2 scope | Manual curation (AGT-03 anti-patterns.md). Operator decides what to remove. Auto-pruning is a v2.3 problem after observing feed growth in practice |
| YAML inter-agent coordination protocol | "Agents should communicate structured data with each other" | Adds coordination overhead before validating whether agents even produce better results than manual workflow. The value is in better consultations, not in a prettier handoff format | Agents write to BRAIN-FEED files that other agents and the orchestrator read directly. No YAML wrapper. v2.3 after v2.2 validates the baseline |
| Brain agent managing its own vector store | "Each brain should have persistent RAG, not just BRAIN-FEED" | v3.0 feature requiring ChromaDB/Qdrant + embeddings infrastructure. Building this in v2.2 is 3 months of infrastructure work before any agent consultation improvement is validated | BRAIN-FEED.md files are the persistence layer. Markdown files are portable and transparent. RAG comes after BRAIN-FEED pattern is proven across 10+ phases |
| One mega-agent that calls all 7 brains | "Why dispatch 7 agents when 1 can do it all?" | Defeats the specialization purpose. Domain agents carry domain-specific [CORRECTED ASSUMPTIONS] and evaluation-criteria that are mutually contradictory. Frontend and Backend agents correct opposite assumptions. A merged agent dilutes all of them | Orchestrator dispatches specialized agents in parallel. Specialization is the entire design rationale |
| Agents replacing the operator entirely | "Full automation — agent decides which brains to consult" | mm:brain-context has 3 explicit moments. Moment selection (which brains, for which phase, at which moment) requires human judgment about the development context. Agents are the execution layer, not the routing layer | Operator triggers dispatch (DISP-02 updates mm:brain-context to use agents). Agents execute the consultation protocol; humans decide when and for what |
| Streaming agent outputs to the War Room frontend | "Watch agents think in real-time in the UI" | The War Room is for brain execution (NotebookLM queries), not for GSD workflow agents. Conflates two different agent paradigms. Adds frontend complexity for no user value | CONTEXT.md files are the output artifact. Operator reads them before planning. No UI plumbing needed in v2.2 |

---

## Feature Dependencies

```
[BRAIN-FEED split (FEED-01)]
    └──required by──> [Per-brain feed reads (FEED-02)]
                          └──required by──> [Agent system prompts (AGT-01)]
                                                └──required by──> [Parallel dispatch (DISP-01)]

[evaluation-criteria.md per brain (AGT-02)]
    └──required by──> [Agent filtering step — consistent quality gate]
                          └──required by──> [Anti-BRAIN-FEED-poisoning]

[anti-patterns.md per brain (AGT-03)]
    └──required by──> [Agent BRAIN-FEED write step — prevents poisoning at source]

[5 manual baselines (BASE-01)]
    └──required by──> [Metric schema (BASE-02)]
                          └──required by──> [Post-migration comparison]

[AGT-01 through AGT-04 (all 7 agents functional)]
    └──required by──> [DISP-01 — orchestrator dispatch]
                          └──required by──> [DISP-02 — mm:brain-context update]

[FEED-03 (write isolation)]
    └──prevents──> [Cross-domain BRAIN-FEED contamination]
```

### Dependency Notes

- **FEED-01 must come before AGT-01:** Agent system prompts need the feed file paths to exist. Writing agents that reference `BRAIN-FEED-04-frontend.md` before the file structure is created = broken agents from day one.
- **BASE-01 must come before full agent migration:** You cannot compare agent quality to manual quality without the manual baseline. Sequence: document 5 consultations manually → define metric schema → migrate to agents → measure.
- **AGT-02 and AGT-03 are independent but both block AGT-04:** Smoke tests (AGT-04) validate the full consultation loop including filtering (AGT-02) and feed write behavior (AGT-03). Can't smoke test without the criteria files.
- **DISP-02 depends on DISP-01:** mm:brain-context command update assumes parallel dispatch infrastructure is proven working. Update the command last, not first.
- **Brain-07 agent is a special dependency:** Brain-07 (Evaluator) validates the outputs of the other 6 agents. Its system prompt must include the 3-iteration loop from moment-3.md. It always runs after domain agents, not in parallel. This ordering constraint belongs in the orchestrator dispatch logic.

---

## MVP Definition

### Launch With (v2.2 — all 11 requirements)

v2.2 is a tightly scoped milestone. All 11 requirements are load-bearing. There is no "minimum" smaller than the full spec — partial agent migration leaves you with a hybrid manual/agent system that's harder to maintain than either pure approach.

- [ ] **FEED-01** — BRAIN-FEED split (global + 7 per-brain files). Existing content migrated. Required before any agents work.
- [ ] **AGT-01** — 7 `.claude/agents/brain-NN-*.md` files with embedded intermediary protocol. The 6-step protocol is native behavior, not a workflow to follow.
- [ ] **AGT-02** — 7 `evaluation-criteria.md` files. One per brain domain. Defines what filters each agent applies before writing to its feed.
- [ ] **AGT-03** — 7 `anti-patterns.md` files. One per brain domain. Prevents known failure modes from entering BRAIN-FEED.
- [ ] **FEED-02** — Both feed reads in every agent system prompt (global + domain). Must be step 1 of the 6-step protocol.
- [ ] **FEED-03** — Write isolation enforced. Each agent writes only to its domain feed. Explicit in system prompt.
- [ ] **BASE-01** — 5 documented manual consultation baselines. Time-box: do 5 real consultations in the next phase cycle, document them with the metric schema.
- [ ] **BASE-02** — Metric schema defined and applied to BASE-01 baselines. Four metrics: time/consultation, gap-count, re-consultations, quality-rating 1-5.
- [ ] **AGT-04** — Smoke test: each agent dispatched, reads feeds, queries its NotebookLM brain, filters, returns verified insights. Manual end-to-end per agent.
- [ ] **DISP-01** — Orchestrator dispatches brain agents in parallel using Agent tool. Brain-07 last.
- [ ] **DISP-02** — mm:brain-context slash command updated to dispatch agents instead of running manual MCP workflows.

### Add After Validation (v2.2.x)

- [ ] **Drift detection** — Detect when BRAIN-FEED entries reference code paths that no longer exist. Trigger: operator notices stale entries during manual review.
- [ ] **BRAIN-FEED compaction** — When feed grows past a threshold (e.g., 100 entries), distill into summary entries. Trigger: agent consultation time noticeably increases due to feed length.

### Future Consideration (v2.3+)

- [ ] **YAML inter-agent coordination** — Structured handoff format between agents and orchestrator. Defer until agent consultation quality is validated.
- [ ] **Auto-pruning BRAIN-FEED** — Automatic removal of stale entries. Requires observing feed evolution across 10+ phases first.
- [ ] **Cross-brain learning** — Agents learn from each other's successful patterns via shared project BRAIN-FEED. Requires understanding which patterns are domain-specific vs. universal.
- [ ] **RAG per agent** — Each agent manages its own vector store partition (ChromaDB/Qdrant). v3.0 after BRAIN-FEED.md pattern is proven across multiple project cycles.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| FEED-01 — BRAIN-FEED split | HIGH (enables everything else) | LOW | P1 |
| AGT-01 — 7 agent system prompts | HIGH (core capability) | HIGH | P1 |
| FEED-02 — Both feeds read in agents | HIGH (prevents zero-context queries) | LOW | P1 |
| FEED-03 — Write isolation | HIGH (prevents BRAIN-FEED poisoning) | LOW | P1 |
| AGT-02 — evaluation-criteria.md x7 | HIGH (filters noise from feed) | MEDIUM | P1 |
| AGT-03 — anti-patterns.md x7 | HIGH (prevents poisoning at source) | MEDIUM | P1 |
| AGT-04 — Smoke tests x7 | HIGH (validates agents actually work) | MEDIUM | P1 |
| DISP-01 — Parallel dispatch | HIGH (the core time savings) | MEDIUM | P1 |
| DISP-02 — mm:brain-context update | MEDIUM (operator interface improvement) | LOW | P1 |
| BASE-01 — 5 manual baselines | MEDIUM (measurement foundation) | LOW | P1 |
| BASE-02 — Metric schema | MEDIUM (comparison framework) | LOW | P1 |
| Auto-pruning BRAIN-FEED | LOW (v2.2 feeds are small) | HIGH | P3 |
| YAML inter-agent protocol | LOW (file reads are sufficient) | HIGH | P3 |

**Priority key:**
- P1: Must have for v2.2 launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

---

## Agent System Prompt — Required Behavior Patterns

This section documents what MUST be in every brain agent's system prompt (AGT-01). These are not suggestions — they are the behavior patterns from the manual skill that made consultation quality high.

### Pattern 1: Read Before Query (Table Stakes)

Every agent must read in this exact order before querying NotebookLM:
1. `.planning/BRAIN-FEED.md` (global project reality)
2. `.planning/BRAIN-FEED-NN-domain.md` (own domain accumulated patterns)
3. Relevant code files for the current phase domain

What happens without this: agent queries with zero context → brain gives generic advice → all 5 anti-patterns from the skill trigger simultaneously. This is the most important behavior pattern.

### Pattern 2: [IMPLEMENTED REALITY] Block Construction

The query to NotebookLM must contain a structured block summarizing what actually exists in the codebase. Not what's planned. Not what's in the ROADMAP. Only implemented reality.

From intermediary-protocol.md: "Include only what's actually implemented. Not what's planned." Agents that include planned features in [IMPLEMENTED REALITY] get recommendations that treat planned features as constraints — causing the brain to avoid suggesting things the codebase doesn't actually have.

### Pattern 3: [CORRECTED ASSUMPTIONS] Per Domain

Each domain brain makes predictably wrong assumptions. These must be pre-baked into the agent system prompt, not computed at query time. Examples by domain:

- **Brain #4 Frontend:** React Compiler available? NO — DISABLED. NODE_TYPES inline? NO — module-level always. dagre recalculates on WS updates? NO — runs once.
- **Brain #5 Backend:** Redis/Celery required for async? NO — asyncio.TaskGroup sufficient. PostgreSQL required? NO — SQLite WAL mode.
- **Brain #7 Evaluator:** 24 brains activate simultaneously? NO — 3-5 per brief typically.

### Pattern 4: Filter Before Writing to BRAIN-FEED

Every insight the brain returns must be verified against the codebase before it enters any feed file. The tri-state classification is non-negotiable:
- ✅ already solved → skip, do not write
- 📅 Phase N+1 → write as deferred, not as gap
- 🔴 real gap → write as insight, cascade to planning

Writing unfiltered NotebookLM output to BRAIN-FEED is the fastest path to a poisoned feed. The anti-pattern from the skill: "accepting first response without filtering against codebase."

### Pattern 5: Brain-07 Always Last, Never Parallel

Brain-07 (Evaluator/Growth) validates the outputs of other agents. It cannot run in parallel with domain agents because it needs their CONTEXT.md outputs as input. The orchestrator dispatch logic must enforce this sequencing:

```
Dispatch domain agents in parallel (Brain #1, #2, #3, #4, #5, #6)
Wait for all to complete
Dispatch Brain-07 with all CONTEXT.md outputs
```

### Pattern 6: 3-Iteration Loop for Brain-07

The Brain-07 agent system prompt must include the iteration loop from moment-3.md:
- Verdict: APPROVED → signal complete to orchestrator
- Verdict: APPROVED_WITH_CONDITIONS → fix conditions in PLAN.md, re-query (max 3 iterations)
- Verdict: REJECTED_REVISE → cascade to domain agents, re-query
- After 3 iterations without APPROVED → escalate to human

This loop must be native behavior in the Brain-07 agent system prompt. Without it, the evaluator becomes a one-shot reviewer with no mechanism to verify fixes.

---

## What Makes Brain Agents Better Than Manual Skill

The downstream consumer question: "what makes a brain agent better than a manual skill workflow?"

The manual `mm:brain-context` skill requires the operator to:
1. Know which workflow file to follow (moment-1, moment-2, moment-3, update-brain-feed)
2. Remember to read BRAIN-FEED before querying (easy to skip under time pressure)
3. Execute the 6-step protocol correctly every time (human error accumulates)
4. Decide which concerns are real gaps vs. generic advice (judgment call, inconsistent)
5. Run brains sequentially (15-30 min for 4-5 brains in moment-2)
6. Manually trigger BRAIN-FEED updates post-phase (often forgotten)

The agent system handles 2, 3, 4, 5, and 6 automatically. The operator only decides 1 (when and which brains to dispatch), which is the judgment that belongs to humans anyway.

Measurable improvements:
- **Time:** Sequential → parallel (Moment 2 drops from ~20min to ~5min for 4 brains)
- **Consistency:** Protocol is native behavior, not instructions to follow (zero skip rate)
- **BRAIN-FEED freshness:** Self-updating after every consultation (not post-phase only)
- **Filter quality:** evaluation-criteria.md makes quality judgment explicit and repeatable

---

## Sources

- `.claude/skills/mm/brain-context/SKILL.md` — Current manual skill, the baseline being automated
- `.claude/skills/mm/brain-context/workflows/moment-1.md` — Moment 1 workflow → agent Moment 1 behavior
- `.claude/skills/mm/brain-context/workflows/moment-2.md` — Moment 2 workflow → domain agent behavior
- `.claude/skills/mm/brain-context/workflows/moment-3.md` — Moment 3 workflow → Brain-07 agent behavior
- `.claude/skills/mm/brain-context/workflows/update-brain-feed.md` — Feed update → agent self-update behavior
- `.claude/skills/mm/brain-context/references/intermediary-protocol.md` — 6-step protocol to embed in agent prompts
- `.claude/skills/mm/brain-context/references/brain-selection.md` — Brain IDs, notebook IDs, cascade rules
- `.planning/REQUIREMENTS.md` — 11 requirements for v2.2 (AGT-01..04, FEED-01..03, BASE-01..02, DISP-01..02)
- `.planning/PROJECT.md` — Key insight: "intermediary protocol becomes built-in behavior, not a workflow to read and follow"
- `.planning/BRAIN-FEED.md` — Current monolithic feed, content to be migrated in FEED-01

**Confidence basis:** All findings derived directly from existing codebase artifacts (skill files, workflows, references) and approved requirements. No external verification needed — the manual workflow IS the specification for agent behavior.

---

*Feature research for: v2.2 Brain Agents — Claude Code subagent specialization*
*Researched: 2026-03-27*
*Confidence: HIGH — all claims derived from existing skill source files and approved REQUIREMENTS.md*
