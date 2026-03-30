# Phase 12: Parallel Dispatch + Command Update — Context

**Gathered:** 2026-03-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire orchestrator parallel dispatch for all 7 domain brain agents via the Agent tool, dispatch Brain #7 after domain agents complete, and update the full mm:ask-* command suite to use Agent dispatch instead of manual MCP workflows.

**What this phase delivers:**
- mm:brain-context dispatches all 7 domain brains simultaneously in a single orchestrator message
- Brain #7 receives domain outputs and evaluates, then returns synthesis + Delta-Velocity score to user
- SYNC tag resolution (Context Proxy) happens inline before dispatch — no scripts, no temp files
- All mm:ask-*.md command files updated to Agent dispatch (ask-all.md + 7 individual ask-*.md)

**What this phase does NOT include:**
- Writing to global BRAIN-FEED.md automatically — global remains READ-ONLY for all agents
- Selective brain dispatch by phase/moment — always all 7
- New brain agents or new feeds — architecture is Phase 10's two-level split, unchanged

</domain>

<decisions>
## Implementation Decisions

### Dispatch Scope — Always All 7

- **Always dispatch all 7 domain brains in parallel.** No conditional selection based on moment or phase.
- Rationale: Phase 10 purified each feed to < 20 entries — overhead is negligible. Cero condicionales en el orquestador.
- When a brain has no impact on the query (e.g., Backend brain receives a CSS question), its purified domain feed allows it to return a structured "No impact" response quickly.
- Consistency benefit: Brain #7 always receives the same 7-entry structure — enabling reliable Delta-Velocity trend tracking.
- Single orchestrator message = all 7 parallel dispatch calls in one Claude Code response (DISP-01 requirement).

### Context Proxy (SYNC Tags) — Inline Injection

- **The orchestrator resolves SYNC tags inline before dispatch.** Pure skill logic, no external scripts.
- Mechanism: Before building each agent's dispatch prompt, the orchestrator reads the agent's domain feed, detects `[SYNC: BF-NN-ID]` tags, opens the owner feed, extracts the referenced section, and injects the content directly into the dispatch prompt.
- Only the referenced fragment is injected — not the full owner feed. Tokens stay minimal.
- Source files on disk remain 100% isolated — no enriched files, no temp files. Phase 10 isolation intact.
- The SYNC pointer stays in the domain feed as documentation; the resolved content travels in the prompt.

### Brain #7 Output — Human-in-the-Loop Gate

- **Brain #7 returns: synthesis + Delta-Velocity score + alerts. Output is volatile (in-session only).**
- Brain #7 does NOT write to BRAIN-FEED.md (global). Global stays READ-ONLY for all agents — no exceptions.
- Output structure from Brain #7:
  1. **Global Rating** (0-100) — health of the dispatch
  2. **Brain Alerts** — list of Rating 1 or 2 violations (corrupt brain identification)
  3. **Consolidated View** — technical/strategic synthesis of the 6 domain outputs
  4. **Delta-Velocity** — efficiency metric vs. baseline (Phase 09 baselines = reference)
- If Brain #7 detects cross-domain patterns worth persisting → it flags them for human review. User or orchestrator (on explicit command) promotes to global feed. Never automatic.

### Command Update Scope — Full Sweep

- **All mm:ask-*.md commands updated to Agent dispatch.** No hybrid, no legacy coexistence.
- Files to update:
  - `.claude/commands/mm/brain-context.md` (or `mm:brain-context` SKILL.md Momentos 1/2/3)
  - `.claude/commands/mm/ask-all.md`
  - `.claude/commands/mm/ask-product.md`
  - `.claude/commands/mm/ask-ux.md`
  - `.claude/commands/mm/ask-design.md`
  - `.claude/commands/mm/ask-frontend.md`
  - `.claude/commands/mm/ask-backend.md`
  - `.claude/commands/mm/ask-qa.md`
  - `.claude/commands/mm/ask-growth.md`
- Post-update architecture:
  - `mm:brain-context` — full orchestration (Moments 1/2/3), dispatches all 7 + Brain #7
  - `ask-all.md` — convenience alias for full parallel dispatch (without Moment context)
  - `ask-[domain].md` — single brain dispatch with full Agent protocol (no manual MCP)
- No mcp__notebooklm-mcp__notebook_query steps in any command post-Phase 12.

### Claude's Discretion

- Exact SYNC tag regex parsing implementation
- How to handle SYNC tags with missing owner sections (fallback behavior)
- Order in which domain outputs are passed to Brain #7
- Exact format of Brain #7 audit report output
- Whether ask-[domain].md also does SYNC resolution (or only the full dispatch commands do)

</decisions>

<specifics>
## Specific Ideas

- "Full-Spectrum Dispatch" — the 7-brain parallel dispatch is atomic. Either all fire or none fire. No partial dispatch.
- "Just-in-Time Hydration" — SYNC tags resolved at dispatch time, not at feed-write time. Content travels in the prompt, never in intermediate files.
- "Human-in-the-Loop Gate" — Brain #7 is a consultant, not a writer. Rafael is the only one with write authority over global BRAIN-FEED.md.
- "Full-Sweep Consistency" — all mm:ask-* commands use the same Agent dispatch engine. No behavioral surprises across commands.
- verify_feed_isolation.sh (Phase 11 sentinel) should be run as a regression test after the first real parallel dispatch — confirms no agent wrote to global or sibling feeds.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.claude/agents/mm/brain-NN-domain/brain-NN-domain.md` — 7 agent files, `subagent_type = brain-NN-domain`, `model: inherit`
- `.planning/BRAIN-FEED-NN-domain.md` — 7 domain feeds with SYNC tags planted (Phase 10)
- `.planning/BRAIN-FEED.md` — global feed, 19 entries, READ-ONLY
- `tests/smoke/verify_feed_isolation.sh` — sentinel script from Phase 11, reusable as regression test
- `.claude/commands/mm/` — 19 command files including all ask-*.md files to update

### Established Patterns
- Agent dispatch format: `subagent_type = brain-NN-domain` (decided Phase 09)
- `model: inherit` for all brain agents (decided Phase 09)
- SYNC tag format: `[SYNC: BF-NN-ID]` (decided Phase 10)
- Brain #7 dispatched AFTER domain agents — never in parallel (decided Phase 09, confirmed Phase 11)

### Integration Points
- `mm:brain-context` SKILL.md (Moment 1/2/3 workflows) — these contain manual MCP steps to replace
- `.claude/commands/mm/ask-all.md` — currently sequential MCP, becomes parallel Agent dispatch
- 7 individual `ask-*.md` files — currently single MCP call, become single Agent dispatch with full protocol

</code_context>

<deferred>
## Deferred Ideas

- **SYNC tag auto-pruning** — detecting stale SYNC references when owner sections are renamed/removed. v3.0.
- **24-brain expansion** — Marketing niche brains using the same dispatch architecture. v3.x.
- **Persistent Delta-Velocity tracking** — storing Brain #7 scores across sessions for trend analysis. v3.0.
- **Dispatch parallelization metrics** — token counting per dispatch via tiktoken to validate context efficiency. v3.0.

</deferred>

---

*Phase: 12-parallel-dispatch-command-update*
*Context gathered: 2026-03-30*
