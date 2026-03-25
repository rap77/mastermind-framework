---
name: mm-brain-context
description: Injects expert brain knowledge into GSD workflow at 3 critical moments. Use before creating ROADMAP.md (Moment 1), before /gsd:plan-phase (Moment 2), and after PLAN.md is created (Moment 3). Each moment follows the intermediary protocol — read codebase first, build context block, query with reality, cascade insights.
argument-hint: [1|2|3|feed]
disable-model-invocation: true
effort: high
allowed-tools: Read, Bash, Grep, Glob
---

<essential_principles>
**Core principle:** Brains answer WHAT and WHY. GSD answers HOW and WHEN.

**You are the intermediary between the brains and the codebase.** Brains have 86+ books of expert knowledge but ZERO access to your code. You have both. The quality of every brain response depends entirely on the context you give it.

**The Intermediary Protocol applies to ALL 3 moments:**

1. **Read before querying** — read relevant code, SUMMARY.md files, STATE.md, and BRAIN-FEED.md before writing a single query
2. **Build a context block** — structure what exists vs. what the plan proposes vs. what might be wrong assumptions
3. **Query with delta** — pass `[IMPLEMENTED REALITY]` + corrections of wrong assumptions the brain might make
4. **Filter the response** — for each concern raised: grep/read code to verify if already solved, if Phase N+1, or if a real gap
5. **Cascade real gaps** — insights that affect implementation go to domain brains in parallel, immediately, not as todos
6. **Synthesize into artifacts** — concrete changes to CONTEXT.md, PLAN.md, or ROADMAP.md — not documentation

**BRAIN-FEED.md is the project memory for brains.** A living document at `.planning/BRAIN-FEED.md` that accumulates implemented patterns, architectural decisions, and codebase reality across phases. Always read it before querying. Always update it after a phase completes. See `workflows/update-brain-feed.md`.
</essential_principles>

<intake>
Which moment?

1. **Moment 1** — About to create ROADMAP.md (before `/gsd:new-milestone`)
2. **Moment 2** — About to plan a phase (before `/gsd:plan-phase N`)
3. **Moment 3** — PLAN.md exists, needs Brain-07 validation before execute
4. **Update BRAIN-FEED** — Phase just completed, update project brain feed

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
|----------|----------|
| 1, "moment 1", "roadmap", "milestone" | `${CLAUDE_SKILL_DIR}/workflows/moment-1.md` |
| 2, "moment 2", "plan phase", "context" | `${CLAUDE_SKILL_DIR}/workflows/moment-2.md` |
| 3, "moment 3", "validate", "brain-07", "plan" | `${CLAUDE_SKILL_DIR}/workflows/moment-3.md` |
| 4, "brain-feed", "update", "post-phase" | `${CLAUDE_SKILL_DIR}/workflows/update-brain-feed.md` |

**After reading the workflow, follow it exactly.**
</routing>

<reference_index>
**Intermediary Protocol:** `${CLAUDE_SKILL_DIR}/references/intermediary-protocol.md` — how to build context blocks, filter responses, cascade insights
**Brain Selection:** `${CLAUDE_SKILL_DIR}/references/brain-selection.md` — which brain for which domain, notebook IDs, context chains
</reference_index>

<workflows_index>
| Workflow | Purpose |
|----------|---------|
| moment-1.md | Before ROADMAP — brains with project reality inform phase structure |
| moment-2.md | Before plan-phase — domain brain with codebase context informs CONTEXT.md, cascade to related brains |
| moment-3.md | After PLAN.md — Brain-07 validates with full code context, domain brains implement gaps |
| update-brain-feed.md | Post-phase — distill new patterns into BRAIN-FEED.md for future queries |
</workflows_index>

<anti_patterns>
<pitfall name="querying-without-code-context">
❌ Querying a brain with only plan text or milestone brief
✅ Read BRAIN-FEED.md + relevant code first. Brain gets `[IMPLEMENTED REALITY]` block.
</pitfall>

<pitfall name="accepting-first-response">
❌ Taking any brain response at face value without filtering against codebase
✅ For each concern raised: verify in code. Mark ✅ solved / 📅 deferred / 🔴 real gap.
</pitfall>

<pitfall name="insights-as-todos">
❌ Noting Brain-07 insights as todos to address later
✅ Real gaps → consult domain brains in parallel immediately → update artifacts now
</pitfall>

<pitfall name="skipping-brain-feed">
❌ Each consultation starts from zero context
✅ Always pass BRAIN-FEED.md content. It is the accumulated project reality.
</pitfall>

<pitfall name="wrong-assumptions-uncorrected">
❌ Brain assumes "24 brains activate simultaneously" when actually 3-5 per brief
✅ Explicitly correct wrong assumptions in the query with code evidence
</pitfall>
</anti_patterns>
