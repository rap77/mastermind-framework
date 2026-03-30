# Phase 12: Parallel Dispatch + Command Update — Research

**Researched:** 2026-03-30
**Domain:** Claude Code Agent dispatch, slash command authoring, SYNC tag resolution
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Dispatch Scope:** Always dispatch all 7 domain brains in parallel — no conditional selection. Single orchestrator message = all 7 parallel dispatch calls in one Claude Code response.
- **Context Proxy (SYNC Tags):** Orchestrator resolves SYNC tags inline before dispatch. Pure skill logic, no external scripts, no temp files. Only the referenced fragment is injected — not the full owner feed.
- **Brain #7 Output:** Volatile (in-session only). Does NOT write to BRAIN-FEED.md. Output structure: Global Rating (0-100) + Brain Alerts + Consolidated View + Delta-Velocity. Cross-domain patterns flagged for human review, never promoted automatically.
- **Command Update Scope:** All mm:ask-*.md commands updated to Agent dispatch. No hybrid, no legacy coexistence. No mcp__notebooklm-mcp__notebook_query steps in any command post-Phase 12.
- **Files to update:** `.claude/skills/mm/brain-context/workflows/moment-2.md`, `.claude/skills/mm/brain-context/workflows/moment-3.md`, and all 9 `ask-*.md` command files.

### Claude's Discretion

- Exact SYNC tag regex parsing implementation
- How to handle SYNC tags with missing owner sections (fallback behavior)
- Order in which domain outputs are passed to Brain #7
- Exact format of Brain #7 audit report output
- Whether ask-[domain].md also does SYNC resolution (or only the full dispatch commands do)

### Deferred Ideas (OUT OF SCOPE)

- SYNC tag auto-pruning (v3.0)
- 24-brain expansion (v3.x)
- Persistent Delta-Velocity tracking across sessions (v3.0)
- Dispatch parallelization metrics via tiktoken (v3.0)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DISP-01 | Orchestrator dispatches brain agents in parallel (not sequential skill steps) | Agent tool parallel dispatch pattern — all 7 calls in one orchestrator message |
| DISP-02 | mm:brain-context command uses Agent tool dispatch, not manual MCP steps | Command file rewrite pattern — replace mcp__notebooklm-mcp__notebook_query with subagent dispatch |
</phase_requirements>

---

## Summary

Phase 12 replaces the manual, sequential MCP workflow in `mm:brain-context` and all `ask-*.md` commands with parallel Agent tool dispatch. The core technical challenge is not the Agent dispatch itself (the pattern is established from Phase 09) — it is the **orchestration layer** that governs dispatch ordering, SYNC tag resolution, and Brain #7 barrier enforcement.

The existing infrastructure is 90% ready. Seven brain agent files exist at `.claude/agents/mm/brain-NN-domain/brain-NN-domain.md`, each with `subagent_type = brain-NN-domain` and `model: inherit`. The SYNC tag format `[SYNC: BF-NN-ID]` is planted in BRAIN-FEED-04 (4 tags pointing to backend feed sections). The sentinel script `verify_feed_isolation.sh` exists and passes Phase 11. What is missing: the orchestration logic in the command/skill files that ties it all together.

The primary authoring surface is the slash command markdown files — these are the only files that control Claude Code dispatch behavior. The `ask-all.md` and individual `ask-*.md` files currently contain manual MCP steps; they must become Agent dispatch instructions. The `moment-2.md` and `moment-3.md` workflows (which are the `mm:brain-context` skill's brain) must be rewritten to use parallel Agent dispatch with explicit ordering: domain agents first, Brain #7 barrier second.

**Primary recommendation:** Author the orchestration logic as explicit, step-by-step instructions in the command/skill markdown files. Claude Code follows slash command prose exactly — use numbered phases (Phase A: Parallel Domain Dispatch / Phase B: Brain #7 Evaluation) to enforce the barrier order. SYNC resolution is a pre-dispatch step: read source section, inject inline into agent prompt text.

---

## Standard Stack

### Core
| Component | Location | Purpose | Status |
|-----------|----------|---------|--------|
| Brain agent files | `.claude/agents/mm/brain-NN-domain/brain-NN-domain.md` | Subagent system prompts with NotebookLM access | READY — 7 files exist |
| BRAIN-FEED domain files | `.planning/BRAIN-FEED-NN-domain.md` | Agent context feeds, contain SYNC tags | READY — 7 files exist |
| BRAIN-FEED global | `.planning/BRAIN-FEED.md` | Read-only global feed (19 entries) | READY — frozen |
| verify_feed_isolation.sh | `tests/smoke/verify_feed_isolation.sh` | Post-dispatch feed isolation sentinel | READY — needs 2 new checks |
| mm:brain-context SKILL.md | `.claude/skills/mm/brain-context/SKILL.md` | Skill entry point — routes to workflows | ROUTES ONLY — not the behavior |
| moment-2.md workflow | `.claude/skills/mm/brain-context/workflows/moment-2.md` | Currently: manual MCP | REWRITE REQUIRED |
| moment-3.md workflow | `.claude/skills/mm/brain-context/workflows/moment-3.md` | Currently: manual MCP for Brain #7 | REWRITE REQUIRED |
| ask-all.md | `.claude/commands/mm/ask-all.md` | Full 7-brain dispatch | REWRITE REQUIRED |
| ask-[domain].md (x7) | `.claude/commands/mm/ask-*.md` | Single brain dispatch | REWRITE REQUIRED |

### Supporting
| Component | Purpose | Note |
|-----------|---------|------|
| global-protocol.md | Governs all agents — stack hard-lock, feed write rules | READ-ONLY — do not touch |
| brain-selection.md | Notebook IDs, dispatch sequences | READ-ONLY for Phase 12 — informational only |
| brain-07-growth.md | Brain #7 already has dispatch constraint ("dispatched AFTER domain brains") | Already enforces barrier in its system prompt |

---

## Architecture Patterns

### Current State (Pre-Phase 12)

All command files follow the same manual MCP pattern:

```markdown
# ask-product.md (current)
<process>
1. Identify question
2. Build query
3. Read notebook_id from config.yaml — query brain via mcp__notebooklm-mcp__notebook_query
4. Present response
</process>
```

```markdown
# ask-all.md (current)
<process>
1. Query all 7 brains SEQUENTIALLY via MCP
4. Synthesize
</process>
```

The `moment-2.md` workflow (step 5) reads: "Use MCP directly for speed." This is what must be replaced.

### Target State (Post-Phase 12)

**Pattern 1: Parallel Domain Dispatch (ask-all.md + moment-2.md)**

The orchestrating command instructs Claude Code to dispatch all 7 brain agents simultaneously in a single message. Claude Code's Agent tool supports launching multiple agents in one response when instructed explicitly.

```markdown
## Phase A — Pre-Dispatch: SYNC Resolution

For each domain brain that has SYNC tags in its feed:
1. Read the brain's domain feed to detect `[SYNC: BF-NN-ID]` tags
2. For each tag found, read the OWNER feed (identified by NN in the tag)
3. Extract ONLY the referenced section (not the full owner feed)
4. Inject the extracted content into that brain's dispatch prompt inline

Example — Brain #4 Frontend has 4 SYNC tags pointing to Brain #5 Backend:
- [SYNC: BF-05-001] → read BRAIN-FEED-05-backend.md > Auth & Security section
- [SYNC: BF-05-002] → same owner, different section
- Inject extracted text directly into Brain #4's prompt: "INJECTED CROSS-DOMAIN CONTEXT: [text]"

Cross-talk rule: Brain #4's prompt gets BF-05 fragments ONLY. Brain #1's prompt gets NO fragments
from any other feed unless it has SYNC tags. Each agent prompt is isolated.

## Phase B — Parallel Domain Dispatch

Dispatch all 7 brain agents SIMULTANEOUSLY in a single orchestrator message.
Use the Task() tool (Agent dispatch) for each brain, all in the same response.

Agents: brain-01-product, brain-02-ux, brain-03-ui, brain-04-frontend,
        brain-05-backend, brain-06-qa, brain-07-growth

DO NOT dispatch sequentially. All 7 in one message = parallel execution.
Wait for all 7 to return before proceeding.

## Phase C — Brain #7 Barrier (after all domain agents return)

Only after all 6 domain agents have returned their outputs:
Dispatch brain-07-growth with the 6 domain agent outputs as context.
Brain #7 receives: [Brain #1 output] + [Brain #2 output] + ... + [Brain #6 output]
```

**Pattern 2: Single Brain Dispatch (ask-[domain].md)**

```markdown
## Process

1. Read `.planning/BRAIN-FEED.md` (global — READ ONLY)
2. Read `.planning/BRAIN-FEED-04-frontend.md` (domain feed)
3. Detect any [SYNC: BF-NN-ID] tags in domain feed — resolve each inline (read owner section, inject)
4. Dispatch brain-04-frontend agent via Task() with:
   - The user's question
   - IMPLEMENTED REALITY block (from feeds)
   - Any resolved SYNC fragments as inline context
5. Present agent output
```

**Pattern 3: Brain #7 Output Structure**

Brain #7 already has its output format specified in `brain-07-growth.md`. The command must request this structure explicitly:

```markdown
Brain #7 must return:
1. Global Rating (0-100) — health of this dispatch
2. Brain Alerts — any Rating 1 or 2 violations by domain agents
3. Consolidated View — technical/strategic synthesis of all 6 domain outputs
4. Delta-Velocity — efficiency vs Phase 09 baselines (target: 3.5-4.5)
5. Human-review flags — cross-domain patterns worth adding to global feed (flagged, NOT written)
```

### Anti-Patterns to Avoid

- **Sequential dispatch across messages:** Dispatching Brain #1, waiting for response, then Brain #2 in the next message. This is the pre-Phase 12 behavior. All 6 domain brains must be in one message.
- **Brain #7 in the domain wave:** Brain #7 dispatched alongside Brain #1-#6. Its system prompt enforces this ("If you receive a query without domain brain outputs: do not proceed"), but the command must also enforce ordering.
- **SYNC injection leaking cross-domain:** Brain #4's prompt must only receive BF-05 fragments (its SYNC pointers). Not fragments from Brain #1's feed or Brain #2's feed.
- **Owner feed full injection:** Injecting the entire BRAIN-FEED-05-backend.md into Brain #4's prompt defeats the point of domain isolation. Only the referenced section.
- **mcp__notebooklm-mcp__notebook_query in commands:** Any remaining manual MCP steps in command files = DISP-02 violation.
- **Temp files for SYNC resolution:** Resolution happens in orchestrator memory, not on disk.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Brain agent files | New agent definitions | Existing `.claude/agents/mm/brain-NN-domain/brain-NN-domain.md` files | Already validated in Phase 11, smoke-tested |
| Agent dispatch format | Custom invocation syntax | Standard Claude Code `Task()` / Agent tool with `subagent_type = brain-NN-domain` | The format is established — `model: inherit` decided in Phase 09 |
| Brain #7 output format | Custom evaluator format | Brain #7's existing output format (5-section: Domain Summary + Second-Order Effects + Systemic Metric + Cascade Risk + Verdict) | Already defined in `brain-07-growth.md` |
| Feed isolation testing | New test framework | Extend `verify_feed_isolation.sh` — add barrier + cross-talk checks | Phase 11 script already handles write isolation; extend, never recreate |
| Global feed governance | New write-guard | `global-protocol.md` already defines the rule | One document governs all 7 agents — editing it propagates everywhere |

**Key insight:** Phase 12 is a command/skill authoring phase, not a code-writing phase. The implementation layer (agent files, feeds, sentinel) is done. The missing layer is the orchestration instructions in the markdown command files.

---

## Common Pitfalls

### Pitfall 1: "Parallel" meaning concurrent across messages
**What goes wrong:** Developer writes `ask-all.md` to dispatch Brain #1, get response, then Brain #2 — treating "parallel" as "eventual consistency." Total time = sum of all 7 agents.
**Why it happens:** The default mental model for agent orchestration is sequential.
**How to avoid:** All 7 domain brain dispatches must be in a single Claude Code orchestrator response. The acceptance criterion (from Brain #6 QA) is observable: `Tiempo Total ≈ Max(T_brain_1..6) + T_brain_7`. If total time equals sum, dispatch failed.
**Warning signs:** The Claude Code UI shows one "thinking" indicator at a time rather than multiple simultaneous ones.

### Pitfall 2: SYNC cross-talk contamination
**What goes wrong:** Brain #4's dispatch prompt receives SYNC fragments from Brain #1's feed (or vice versa), or the full BRAIN-FEED-05-backend.md is passed to Brain #4 instead of just the referenced sections.
**Why it happens:** Lazy implementation injects all resolved SYNC content into all agent prompts.
**How to avoid:** Build a per-agent SYNC fragment map: `{ brain_id → [resolved fragments for that brain only] }`. Inject only matching fragments into each agent's prompt. Zero cross-agent leakage.
**Warning signs:** Brain #4 cites Backend security rules it had no SYNC pointer to. Brain #6 QA's Phase 12 cross-talk isolation check fails.

### Pitfall 3: Brain #7 "Trap of the Average" (mediocre synthesis)
**What goes wrong:** Brain #7 reconciles contradictions between domain agents, producing a mediocre consensus that is neither useful nor actionable. User must mentally de-conflict the report.
**Why it happens:** Without explicit constraint, LLM behavior defaults to consensus-seeking.
**How to avoid:** Brain #7's dispatch prompt must include the anti-mediocre constraint verbatim: "Do NOT reconcile contradictions. Name the conflict. Pick the strongest expert position. Mediocre synthesis is worse than no synthesis." Audit `brain-07-growth.md` — add this constraint if not present.
**Warning signs:** Brain #7 report contains phrases like "balancing both perspectives" or "it depends on context" without naming a specific winner.

### Pitfall 4: SYNC tag regex fragility
**What goes wrong:** A SYNC tag like `[SYNC: BF-05-001]` fails to parse due to whitespace variation or tag appearing inside a code block.
**Why it happens:** Regex without anchoring.
**How to avoid:** The regex pattern `\[SYNC:\s+BF-(\d{2})-(\w+)\]` handles whitespace. Add a fallback: if the owner section ID is not found, log a warning and proceed without injection (graceful degradation, not hard failure). Never block dispatch due to a missing SYNC target.
**Warning signs:** Brain #4 returns "No impact" on a question where BF-05 context would clearly have changed the answer.

### Pitfall 5: verify_feed_isolation.sh not extended before testing
**What goes wrong:** Running parallel dispatch before extending the sentinel script means the barrier order and cross-talk isolation checks are not verified.
**Why it happens:** Assuming Phase 11's script covers Phase 12's requirements.
**How to avoid:** Extend the script with the 2 new checks (barrier order validation + cross-talk isolation) before the first real parallel dispatch. The script takes 2 new optional parameters — extend without breaking the existing interface.
**Warning signs:** Parallel dispatch completes but nobody verified Brain #7 fired after domain agents.

---

## Code Examples

### SYNC Tag Detection and Resolution (inline logic)

```python
# Conceptual pseudocode for the orchestrator to follow
# Source: derived from CONTEXT.md decisions (inline injection, no temp files)

import re

SYNC_PATTERN = re.compile(r'\[SYNC:\s+BF-(\d{2})-(\w+)\]')

def resolve_sync_tags(domain_feed_content: str, all_feeds: dict[str, str]) -> list[str]:
    """
    Returns list of (tag, resolved_content) for injection.
    Falls back to empty string if owner section not found.
    """
    injections = []
    for match in SYNC_PATTERN.finditer(domain_feed_content):
        owner_id = match.group(1)   # e.g., "05"
        section_id = match.group(2) # e.g., "001"
        owner_feed_key = f"BRAIN-FEED-{owner_id}"
        owner_content = all_feeds.get(owner_feed_key, "")
        # Extract the section heading that contains the section_id reference
        # Section reference is in the SYNC tag's descriptive text
        # Fallback: if not found, return empty (graceful degradation)
        injections.append(f"[INJECTED FROM {owner_feed_key}]: {extracted_section}")
    return injections
```

In practice, the orchestrator does this as prose in the command file — it reads the owner feed section and includes it verbatim inline in the agent prompt.

### Parallel Dispatch Instruction (command file prose)

```markdown
## Phase B — Dispatch (in a single orchestrator message)

Dispatch these 6 brain agents simultaneously using the Task tool:
- `brain-01-product` — prompt: [context block] + [user question] + [product-specific WHAT I NEED]
- `brain-02-ux` — prompt: [context block] + [user question] + [ux-specific WHAT I NEED]
- `brain-03-ui` — prompt: [context block] + [user question] + [ui-specific WHAT I NEED]
- `brain-04-frontend` — prompt: [context block] + [user question] + [INJECTED: BF-05 fragments] + [frontend-specific WHAT I NEED]
- `brain-05-backend` — prompt: [context block] + [user question] + [backend-specific WHAT I NEED]
- `brain-06-qa` — prompt: [context block] + [user question] + [qa-specific WHAT I NEED]

All 6 in one message. Wait for all to return.
```

### Brain #7 Barrier Instruction (command file prose)

```markdown
## Phase C — Brain #7 Evaluation (only after Phases A and B complete)

After ALL 6 domain agents have returned:

Dispatch `brain-07-growth` with this prompt:
"""
[CROSS-DOMAIN CONTEXT]
Brain #1 Product output: [paste brain-01 return]
Brain #2 UX output: [paste brain-02 return]
Brain #3 UI output: [paste brain-03 return]
Brain #4 Frontend output: [paste brain-04 return]
Brain #5 Backend output: [paste brain-05 return]
Brain #6 QA output: [paste brain-06 return]

[ANTI-MEDIOCRE CONSTRAINT]
Do NOT reconcile contradictions. Name the conflict. Pick the strongest expert position.
Mediocre synthesis is worse than no synthesis.

[WHAT I NEED]
Evaluate these 6 domain outputs. Return:
1. Global Rating (0-100)
2. Brain Alerts (Rating 1 or 2 violations)
3. Consolidated View (synthesis — name conflicts, don't smooth them)
4. Delta-Velocity vs Phase 09 baselines
5. Human-review flags (cross-domain patterns for global feed — flag only, do NOT write)
"""
```

### Extended verify_feed_isolation.sh Checks

```bash
# New Check A: Barrier order validation
# After parallel dispatch, check git log timestamps or orchestrator history
# to confirm Brain #7's dispatch prompt appears AFTER all 6 domain agent responses.
# Implementation: this is observational (Claude Code UI) + manual verification.
# Automated proxy: check that brain-07 output file (if any) has a later mtime than domain outputs.

# New Check B: Cross-talk isolation
# After dispatch, verify each agent's domain feed was only written by its owner.
# Check that Brain #4's feed contains no Backend-specific technical content
# that could only have arrived via a BF-05 fragment (indirect test).
# Direct test: inject a deliberate change to BF-05-WS-AUTH section.
# Without SYNC: Brain #4 returns "No impact" (only sees own feed).
# With correct SYNC: Brain #4 cites the BF-05 fragment explicitly.
```

---

## State of the Art

| Old Approach | Current Approach | Impact on Phase 12 |
|--------------|-----------------|-------------------|
| Manual MCP in command files | Agent dispatch via Task() | Command files become orchestration scripts, not MCP callers |
| Sequential brain consultation | Parallel dispatch in one message | T1 drops from 210-270s to ~90-110s |
| Brain #7 consulted when user chose Moment 3 | Brain #7 dispatched automatically after domain agents | Evaluation becomes systemic, not optional |
| SYNC tags unresolved (planted in Phase 10, never automated) | SYNC tags resolved inline at dispatch time | Cross-domain context flows without violating feed isolation |
| 9 command files with different MCP approaches | 9 command files with consistent Agent dispatch engine | "Full-Sweep Consistency" — no behavioral surprises |

**Deprecated/outdated after Phase 12:**
- `mcp__notebooklm-mcp__notebook_query` steps in command files: replaced by Agent dispatch
- `config.yaml` notebook_id reads in command files: agent files contain the NotebookLM access directly
- Sequential consultation in `ask-all.md` step 3: replaced by single-message parallel dispatch

---

## Open Questions

1. **Does moment-1.md also need updating?**
   - What we know: CONTEXT.md says "update all mm:ask-*.md files" and `moment-2.md` + `moment-3.md`. Moment 1 (before ROADMAP) currently uses Brain #1 + #7 in parallel.
   - What's unclear: Is Moment 1's MCP workflow also replaced, or only Moments 2 and 3?
   - Recommendation: Read moment-1.md during planning. Given "Full-Sweep Consistency" principle, include it. But CONTEXT.md's explicit file list does not name it — confirm with user or include as low-risk addition.

2. **SYNC fallback behavior for missing owner sections**
   - What we know: CONTEXT.md marks this as Claude's Discretion.
   - What's unclear: Should a missing SYNC target hard-fail, warn and continue, or silently skip?
   - Recommendation: Graceful degradation — log a visible warning in the orchestrator output, proceed without injection. Never block dispatch. This matches the Phase 10 SYNC tag design intent (optional enrichment, not hard dependency).

3. **Anti-mediocre constraint presence in brain-07-growth.md**
   - What we know: CONTEXT.md (Brain #1 analysis) identifies this as a critical risk. Current `brain-07-growth.md` has extensive output format requirements but does not explicitly say "Do NOT reconcile contradictions."
   - What's unclear: Is the constraint implicit in "You are not a domain specialist" persona, or must it be explicit?
   - Recommendation: Add it explicitly to brain-07-growth.md as a named constraint. The difference between implicit ("I evaluate") and explicit ("Do NOT reconcile") is measurable in output quality.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | bash (verify_feed_isolation.sh) + manual observation |
| Config file | `tests/smoke/verify_feed_isolation.sh` (existing, extend) |
| Quick run command | `bash tests/smoke/verify_feed_isolation.sh brain-04-frontend BRAIN-FEED-04-frontend.md` |
| Full suite command | Run all 7 single-agent verifications + 1 parallel dispatch verification |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DISP-01 | All 7 dispatched in one orchestrator message — T1 ≈ Max(T1..6) + T7, not sum | Manual observation | Claude Code UI shows simultaneous "thinking" indicators | N/A — behavioral |
| DISP-01 | Brain #7 fires AFTER domain agents (barrier) | Behavioral + sentinel | Extended `verify_feed_isolation.sh` barrier check | ❌ Wave 0 — extend script |
| DISP-01 | Each agent prompt contains ONLY its own SYNC fragments (no cross-talk) | Behavioral sentinel | SYNC characterization test (deliberate BF-05 change + Brain #4 citation check) | ❌ Wave 0 — new test |
| DISP-02 | No mcp__notebooklm-mcp__notebook_query in any ask-*.md file | Static file check | `grep -r "notebooklm-mcp__notebook_query" .claude/commands/mm/` returns zero matches | ❌ Wave 0 — add to verification |
| DISP-02 | No mcp__ steps in moment-2.md and moment-3.md | Static file check | `grep "mcp__" .claude/skills/mm/brain-context/workflows/moment-2.md` returns zero matches | ❌ Wave 0 — add to verification |

### Sampling Rate
- **Per task commit:** Static check — `grep -r "mcp__notebooklm" .claude/commands/mm/` confirms zero MCP steps
- **Per wave merge:** Full behavioral test — single-agent dispatch with isolation check
- **Phase gate:** Parallel dispatch + Brain #7 barrier validated before marking Phase 12 complete

### Wave 0 Gaps
- [ ] `tests/smoke/verify_feed_isolation.sh` — extend with barrier order check (new flag `--check-barrier`)
- [ ] `tests/smoke/verify_feed_isolation.sh` — extend with cross-talk isolation check (new flag `--check-crosstalk`)
- [ ] SYNC characterization test documented in `tests/smoke/README.md` or inline in the extended script
- [ ] Static grep check for MCP elimination verification (can be a 3-line shell script or part of the extended sentinel)

---

## Sources

### Primary (HIGH confidence)
- Direct file inspection: `.claude/agents/mm/brain-NN-domain/brain-NN-domain.md` (all 7 agents) — dispatch format, model:inherit pattern, tool declarations
- Direct file inspection: `.claude/skills/mm/brain-context/workflows/moment-2.md` — current MCP workflow being replaced
- Direct file inspection: `.claude/skills/mm/brain-context/workflows/moment-3.md` — current Brain #7 workflow being replaced
- Direct file inspection: `.claude/commands/mm/ask-*.md` (all 9 files) — current command structure
- Direct file inspection: `.planning/BRAIN-FEED-04-frontend.md` — 4 SYNC tags confirmed (BF-05-001 thru BF-05-004)
- Direct file inspection: `tests/smoke/verify_feed_isolation.sh` — sentinel script structure, exit codes, existing checks
- Direct file inspection: `.planning/phases/12-parallel-dispatch-command-update/12-CONTEXT.md` — all locked decisions

### Secondary (MEDIUM confidence)
- `.planning/STATE.md` — established decisions from Phase 09-11 (model:inherit, brain agent naming format, Brain #7 barrier rule)
- `brain-07-growth.md` dispatch constraint: "Always dispatched AFTER domain brains" — confirmed present in system prompt

### Tertiary (LOW confidence — needs validation)
- Anti-mediocre constraint gap in brain-07-growth.md: identified by reading the file, confirmed absent. Needs planner decision on whether to add it in Phase 12 or treat as separate task.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all files inspected directly, no external dependencies
- Architecture patterns: HIGH — dispatch format established in Phase 09, SYNC tags from Phase 10, both verified in Phase 11
- Pitfalls: HIGH (behavioral) / MEDIUM (SYNC regex) — behavioral pitfalls from CONTEXT.md Brain consultations; SYNC regex from direct tag inspection
- Validation architecture: HIGH — script exists and was read; gaps identified precisely

**Research date:** 2026-03-30
**Valid until:** Phase 12 execution — no external dependencies to go stale; all sources are in-repo
