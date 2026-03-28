# Baseline Schema — Delta-Velocity + Cognitive Load Split

**Purpose:** This file defines the measurement contract for all pre-migration baseline consultations. It is not a planning document. It lives in `tests/` because baselines are Intelligence Integration Tests — part of the quality pipeline, not documentation. Every field defined here is the control surface for post-migration comparison (Phase 11 agent runs vs Phase 09 manual runs).

---

## Schema Definition

All baseline records use the following YAML frontmatter structure. Every field is mandatory. Do not rename fields — post-migration comparison tooling depends on exact key names.

```yaml
---
schema_version: "1.0"
context_id: <git rev-parse HEAD>        # Exact commit hash at time of baseline — enables exact reproduction post-migration
brain_id: <int | list[int]>             # Brain number(s) consulted (1-7)
brain_ids: <list[int]>                  # Alias for multi-brain baselines — list all brains in dispatch order
ticket_type: <retrospective | adversarial>
# retrospective: known ground truth from Phase 07/08 history — calibration test
# adversarial: new challenge not yet solved — adherence-to-principles test

brain_feed_snapshot:
  - .planning/BRAIN-FEED.md             # Files given to brain as context (snapshot list — paths relative to repo root)
  - .planning/STATE.md
  - <relevant code file>

input_prompt_raw: |
  <exact prompt or instruction given to the brain — verbatim, no paraphrase>

cognitive_trace:
  T1_setup_seconds: <int>               # Context gathering time (Steps 1-3: read BRAIN-FEED, build [IMPLEMENTED REALITY], [CORRECTED ASSUMPTIONS])
  T2_ai_latency_seconds: <int>          # Model response wait (Step 4: NotebookLM query + response)
  T3_review_seconds: <int>              # Human validation + filtering time (Steps 5-6: filter insights, cascade gaps, write output)

delta_velocity_score: <1-5>             # See Delta-Velocity Matrix below

characterization_diff: |
  Expected: <what the brain was expected to say based on domain knowledge>
  Observed: <what the brain actually said — or would say in simulated baseline>

human_intervention_log:
  - gap: <description of what the brain got wrong or left incomplete>
    correction: <what the human had to add, change, or reject>
---
```

---

## Delta-Velocity Matrix

The rating scale used to evaluate brain output quality. A score is assigned AFTER human review (T3). Ratings are calibrated against the existing codebase — not abstract standards.

| Rating | Level | Definition |
|--------|-------|------------|
| 1 | Blocker | Hallucinates libraries not in lockfile, breaks TypeScript strict mode, ignores anti-patterns.md. Output is unusable — requires full rewrite. |
| 2 | Junior | Works but generic (ChatGPT-basic quality). Doesn't use existing Zustand stores, ignores React Flow architecture, misses NexusCanvas integration. Full refactor needed before PR. |
| 3 | Peer | Correct, respects stack and context, integrates with NexusCanvas. PR-ready with minor tweaks. This is the stability floor — system is stable when consistently scoring 3. |
| 4 | Senior | Detects optimization not in the ticket (e.g., critical useMemo not requested, WS error handling the ticket didn't mention). Improves the codebase beyond the ask. System is profitable when scoring 4+. |
| 5 | Architect | Proposes game-changing solution (e.g., Dynamic DAG optimization reducing DOM load 40%). Unlocks next roadmap phase or fundamentally improves the architecture. |

**Baseline target:** Manual skill should consistently score 3. Post-migration target: agents score >= 3 on first zero-shot run.

---

## Cognitive Load Split

Each consultation time is split into three phases mapping to the 6-step intermediary protocol:

| Phase | Protocol Steps | What it Measures | Automation Candidate |
|-------|---------------|------------------|----------------------|
| T1: Setup & Context | Steps 1-3: read BRAIN-FEED, build [IMPLEMENTED REALITY] block, build [CORRECTED ASSUMPTIONS] block | Friction in context gathering. High T1 = scripting opportunity. | Yes — T1 friction is the primary automation target for Phase 10 |
| T2: AI Execution | Step 4: NotebookLM query + response wait | Model latency. Not controllable by protocol design. | No |
| T3: Refinement & Cascade | Steps 5-6: grep verification, cascade gaps to domain context, write CONTEXT.md section | Prompt precision and protocol complexity. High T3 = cascade protocol too manual. | Partially — oracle pattern reduces T3 in Phase 11 |

**Diagnostic rules:**
- T1 high → collection script needed (Phase 10 automation target)
- T3 high → cascade protocol too manual, reduce with oracle pattern

---

## T1 Profitability Threshold

**T1 < 300 seconds (5 minutes) = agent is profitable.**

Rationale: If context setup takes longer than 5 minutes manually, an autonomous agent that reads BRAIN-FEED automatically will recoup the time. If T1 < 300s, the manual skill is fast enough that agent latency overhead must be below 60 seconds to break even.

**Flagging rule:** Any baseline where `T1_setup_seconds > 300` is flagged as **"agent-unprofitable" candidate** — these are the highest-priority automation targets in Phase 10.

```
T1 ≤ 300s: Standard baseline — agent must match or beat on first run
T1 > 300s: Agent-unprofitable flag — automation of context collection is mandatory, not optional
```

---

## Frozen Context Block Template

Every baseline includes a Frozen Context Block BEFORE the ticket query. This block is the control variable — only the ticket changes between baselines. The product context must remain identical across all 5 baselines.

```markdown
## Frozen Context Block

**Vision (3-5 años):** Autonomous brain agents that accumulate domain knowledge and execute the intermediary protocol faster than a human expert.
**Strategic Intent:** v2.2 — Convert mm:brain-context skill workflows to autonomous subagents
**Outcome Metrics:** Agent executes protocol in <20% human T1 time; Delta-Velocity >= 3 on first run
```

This block is embedded verbatim in every baseline record. Do not paraphrase. The consistency is intentional — if it changes between baselines, the comparison is invalid.

---

## Ticket Mix Specification

**5 baselines = 2 retrospective + 3 adversarial**

| Type | Count | Purpose | Ground Truth |
|------|-------|---------|--------------|
| Retrospective | 2 (baselines 01, 04) | Precision test — known ground truth from Phase 07/08 history. Calibrates what Rating 3 looks like. | Known correct answer in the codebase |
| Adversarial | 3 (baselines 02, 03, 05) | Resilience test — new challenges not yet solved. Tests adherence to system principles under unknown territory. | Adherence to: Stack Hard-Lock, Pydantic v2 strict, no unlocked libraries |

**Adversarial validity rule:** A rejection is valid only if the brain cites the specific source of the constraint (Oracle Pattern):
```
Rejected: [Specific library/pattern] violates Stack Lock.
Source: global-protocol.md > Stack Hard-Lock | brain-NN-domain/warnings.md > [pattern name]
```
Generic rejections without citation = Rating 2 max.

---

## Post-Migration Usage

After Phase 11 (Smoke Tests) completes:
1. Run the same 5 tickets through the dispatched brain agents
2. Record T1/T2/T3 and delta_velocity_score in identically structured files at `tests/baselines/agent-run-NN-*.md`
3. Compare manual (Phase 09) vs agent (Phase 11) using identical ticket text
4. Success criteria: agent T1 < 20% of manual T1; agent delta_velocity_score >= manual delta_velocity_score

The `context_id` field in both sets must match the same codebase state for the comparison to be valid.
