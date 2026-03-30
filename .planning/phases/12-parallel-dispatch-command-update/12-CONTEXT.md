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

## Expert Brain Synthesis

### QA/DevOps — Acceptance Criteria (Brain #6)

**Parallel dispatch verification (behavioral, not unit tests):**
- Claude Code UI must show multiple concurrent agent "thinking" indicators — not sequential. Observable as simultaneous execution.
- `Tiempo Total ≈ Max(T_brain_1..6) + T_brain_7` — if total time equals sum of all 7, dispatch is NOT parallel. This is the timing acceptance criterion.
- Error independence: if one domain agent fails/times out, others must continue. Brain #7 receives successful results + explicit failure notification.
- Domain agent outputs must appear as independent tool responses in orchestrator history, ready for Brain #7 consumption.

**verify_feed_isolation.sh gaps for Phase 12 (must add before plan is complete):**
- Current script only checks write isolation ✅ — sufficient for Phase 11 single-agent dispatch
- Phase 12 needs 2 new checks:
  1. **Barrier order validation**: verify Brain #7 prompt is sent AFTER all domain agent responses appear in context. Log check: #7 never fires before 1-6 return.
  2. **Cross-talk isolation**: verify each agent's dispatch prompt contains ONLY its own domain feed SYNC fragments — not fragments from other agents' feeds. Brain #4 must NOT receive SYNC content meant for Brain #1.

**SYNC resolution characterization test:**
- Introduce a deliberate change to `BF-05-WS-AUTH` (break the auth contract)
- WITHOUT SYNC injection: Brain #4 returns "No impact" (it only sees its own feed)
- WITH SYNC injection (correct): Brain #4 detects the desync and raises an alert, citing the injected BF-05 fragment
- Acceptance criterion: Brain #4 cites the BF-05 fragment explicitly. No citation = SYNC injection failed.

**Safe delivery sequence (incremental, not atomic):**
1. Update `mm:brain-context` dispatch logic first — test SYNC resolution with a single agent
2. Implement Brain #7 barrier — validate it receives domain outputs and fires after
3. Update `ask-*.md` files atomically (once core logic is validated)
4. Run updated `verify_feed_isolation.sh` (with new barrier + cross-talk checks)

### Product Strategy — T1 & Risk (Brain #1)

**T1 projection post-Phase 12:** ~90-110s
- Slowest domain brain ≈ 60s + Brain #7 synthesis ≈ 30-40s
- vs pre-migration baseline: 210-270s (sequential MCP calls)
- Triples profitability margin before 300s threshold

**Delta-Velocity range expected: 3.5-4.5**
- Rating 3: parallel dispatch works, T1 maintained, files updated
- Rating 4: T1 < 120s AND Brain #7 report is self-contained — user doesn't need to open individual agent files to understand the synthesis

**Critical risk: "Trap of the Average" in Brain #7**
- Risk: Brain #7 reconciles contradictions between domain agents → produces mediocre consensus
- Signal: user has to mentally "de-conflict" the Brain #7 report themselves → system failed its synthesis job
- Mitigation: Brain #7 system prompt needs explicit constraint: "Do NOT reconcile contradictions. Name the conflict. Pick the strongest expert position. Mediocre synthesis is worse than no synthesis."
- Action item for plan: audit `brain-07-growth.md` — add anti-mediocre synthesis guard if not already present

**"Always 7" latency risk:**
- Real trade-off: loses "early-stop efficiency" — even for simple questions, always waits for slowest brain
- Non-linear degradation if slowest agent hits a latency spike or loops
- Accepted trade-off (user decision): coverage + Brain #7 consistency outweigh early-stop flexibility at v2.2 scale

### Non-Negotiables for Plan
- SYNC cross-talk isolation MUST be explicit in orchestrator logic — each agent gets only its own SYNC fragments
- Brain #7 anti-mediocre constraint must be verified before Phase 12 is marked complete
- verify_feed_isolation.sh must be extended with barrier + cross-talk checks (not recreated — extended)
- T1 < 120s is the Phase 12 success metric for Delta-Velocity Rating 4

---

*Phase: 12-parallel-dispatch-command-update*
*Context gathered: 2026-03-30*
*Brain consultation: Brain #6 QA (conversation: e4411abc) + Brain #1 Product (conversation: 8b6903e0)*
