# Pitfalls Research

**Domain:** Claude Code subagent migration — manual skill workflows to autonomous brain agents
**Researched:** 2026-03-27
**Confidence:** HIGH (derived from: codebase analysis, real skill/workflow code, existing brain consultation patterns, Claude Code agent format inspection from production plugin agents)

> This file replaces the v2.1 PITFALLS.md for v2.2 scope. The v2.1 pitfalls (React Flow CSS, Magic UI, JWT, WS) remain valid for `apps/web/` and are documented in `.planning/research/PITFALLS-v2.1.md` (archived). This file covers **only v2.2 Brain Agents pitfalls**: Claude Code subagent migration, BRAIN-FEED partitioning, and measurement anti-patterns.

---

## Critical Pitfalls

### Pitfall 1: System Prompt Embeds Workflow Steps Instead of Internalized Behavior

**What goes wrong:**
The brain agent's system prompt reads like the old `mm:brain-context` skill — a numbered list of steps ("Step 1: Read BRAIN-FEED.md. Step 2: Build context block. Step 3: Query NotebookLM..."). The agent treats it as a checklist to follow mechanically. When the orchestrator dispatches the agent with a specific question, the agent spends half its context budget executing the protocol overhead rather than delivering domain expertise. The consultation quality is the same as the old skill, but now it's harder to maintain (split across 7 files instead of one skill).

**Why it happens:**
The v2.1 skill was procedure-first — it documented HOW to execute a consultation. The v2.2 migration copies those procedures into agent files without converting them into internalized behavior. The key insight from PROJECT.md: "the intermediary protocol becomes built-in behavior, not a workflow to read and follow." A workflow step says "read BRAIN-FEED.md." Internalized behavior means the agent understands WHY it reads BRAIN-FEED.md (to avoid recommending what already exists) and does it automatically as context-loading, not as a step to check off.

**How to avoid:**
Write agent system prompts as expert personas with embedded knowledge, not procedures. Instead of "Step 1: Read BRAIN-FEED.md before querying," write: "You never query your brain without first loading the project reality. Knowing what already exists is not optional — it is how you avoid wasting the team's time with recommendations the codebase already implements." The behavior is the same; the framing is identity-level, not procedure-level. Test by dispatching the agent with no explicit instructions about the protocol — if it reads BRAIN-FEED.md first without being told, the behavior is internalized.

**Warning signs:**
- Agent system prompt has numbered "Step N:" sections mirroring `moment-1.md` or `moment-2.md` workflows
- Agent returns responses that rehash what's already in BRAIN-FEED.md
- Consultation time increases after migration (agent is running through protocol overhead)
- Two agents dispatched with the same question return near-identical protocol traces

**Phase to address:** AGT group — Pitfall must be addressed in AGT-01 (brain subagent files) before AGT-04 (smoke test). Validate with AGT-04 smoke test: dispatch agent cold, verify it reads feeds before querying NotebookLM without explicit instruction.

---

### Pitfall 2: BRAIN-FEED Partition Pollutes Shared Context on Migration Day

**What goes wrong:**
The current monolithic `BRAIN-FEED.md` contains patterns that look general but are actually domain-specific. When you split it into 7 per-brain files (`BRAIN-FEED-01-product.md`, `BRAIN-FEED-04-frontend.md`, etc.), patterns get copied into multiple domain files "just to be safe." The Frontend brain now carries Product Strategy patterns it will echo back as recommendations. The Product brain carries Frontend implementation details it will use to constrain product thinking. Within 2-3 consultation cycles, each domain feed has grown with cross-domain pollution, defeating the purpose of the split.

**Why it happens:**
The split is mechanical: someone reads the monolith, can't decide which domain owns a pattern, and copies it to 2-3 feeds. No ownership rule is enforced. FEED-03 (agents write only to their own feed) prevents future pollution but doesn't address the initial migration.

**How to avoid:**
Define a migration ownership rule before splitting: every entry in the current BRAIN-FEED.md gets assigned to exactly ONE domain. If a pattern is cross-domain (e.g., "JWT verified at Server Components + Route Handlers"), it goes to the global feed only, never to a domain feed. If a pattern is clearly domain-specific (e.g., "NODE_TYPES at module level prevents infinite re-render"), it goes to the domain feed only. Create a migration checklist: for each entry, one owner. No copies. The global feed should contain only cross-cutting concerns that every brain needs. A domain feed that grows beyond 2 pages before any new consultation is a sign the split was too generous.

**Warning signs:**
- A pattern appears in both global and a domain feed
- Two domain feeds contain the same architectural decision
- Global BRAIN-FEED.md retains all its v2.1 content after the split (nothing was moved, only copied)
- Domain feed for Frontend contains Product Strategy patterns (e.g., OKR framework, discovery cadence)

**Phase to address:** FEED group — FEED-01 must include the migration ownership rule as an acceptance criterion, not just "8 feed files exist." Verify during FEED-01: each entry appears in exactly one file. Spot-check 5 entries post-migration.

---

### Pitfall 3: Agent Without Evaluation Criteria Passes Everything

**What goes wrong:**
A brain agent without `evaluation-criteria.md` has no definition of what a "good response" looks like. When the agent queries NotebookLM and gets a response about, say, continuous discovery frameworks, it has no basis to filter. Two failure modes emerge simultaneously: (a) the agent passes through all 8 NotebookLM recommendations, including generic ones that don't apply to this codebase, filling BRAIN-FEED with noise; (b) or the agent applies its own implicit criteria, which varies by consultation and cannot be measured or improved. Either way, BRAIN-FEED degrades rather than improves over time.

**Why it happens:**
The v2.1 skill used the intermediary protocol's Step 5 (filter the response) as a shared filtering standard. But the step is vague: "for each concern raised: verify in code. Mark solved / deferred / real gap." Each brain agent needs a domain-specific rubric. Brain #1 (Product Strategy) should evaluate recommendations against discovery maturity. Brain #4 (Frontend) should evaluate against performance constraints and existing architectural invariants. Without this, filtering is vibes-based.

**How to avoid:**
For each brain, define 4-6 criteria that distinguish a useful recommendation from a generic one. Evaluation criteria should be specific enough to apply without judgment: "Reject any recommendation that suggests a feature already present in the Implemented Features table of BRAIN-FEED.md." "Reject any recommendation that requires a library not in the current stack unless the agent can verify it solves a proven gap." "Accept recommendations that reference a specific codebase constraint with a path or component name." Write the criteria before writing the agent system prompt — they shape what expertise the agent applies.

**Warning signs:**
- BRAIN-FEED domain sections grow by more than 3 entries per consultation (too permissive)
- BRAIN-FEED domain sections grow by 0 entries per consultation (too restrictive)
- Two consultations on the same topic return contradictory BRAIN-FEED entries
- Agent output includes recommendations the BRAIN-FEED already documents as rejected anti-patterns

**Phase to address:** AGT-02 — Evaluation criteria files are a prerequisite for AGT-04 smoke test. Do not attempt end-to-end testing without evaluation criteria in place. The criteria are the oracle for the smoke test.

---

### Pitfall 4: No Baseline = No Way to Validate Agent Improvement

**What goes wrong:**
You migrate from `mm:brain-context` skill to autonomous agents. The agents feel faster and return more structured output. You declare the migration a success. Six weeks later, a critical architectural decision contradicts a pattern the brain consultations should have caught — one that the v2.1 manual workflow had actually flagged correctly but the agent missed. You have no data to understand what happened. Was the agent worse on this domain? Did it miss it because the context was different? You don't know because you never measured the baseline.

**Why it happens:**
Teams skip baselines because they feel like overhead before the "real work" starts. The intuition is: agents will clearly be better (faster, parallel, more consistent) so why measure? The problem is that speed and consistency are not the same as quality. An agent that returns a response in 10 seconds consistently is worse than a slower workflow that surfaces the right gap if it misses the gap every time.

**How to avoid:**
Before migrating the first brain to agent format, run 5 real consultations using the current `mm:brain-context` skill workflow. Not synthetic tests. Real consultations on real upcoming phase planning questions. For each: record time elapsed, number of recommendations filtered, number of real gaps identified, number of re-consultations needed, and a 1-5 quality rating applied 24 hours later (not immediately — recency bias). Document using the metric schema from BASE-02. After v2.2 ships, run the same 5 questions through the agent equivalents. Compare. The baseline is not bureaucracy — it is the only way to know if the migration worked.

**Warning signs:**
- BASE-01 is created the same day as AGT-04 smoke test (consultation was synthetic, not real)
- Baselines document only what went right (confirmation bias — record struggles too)
- Quality ratings are applied immediately after consultation (should be 24h later)
- Baseline format differs from the metric schema (makes comparison impossible)

**Phase to address:** BASE group — BASE-01 and BASE-02 must complete before any AGT group work begins. This is the hardest sequencing rule to enforce because it feels like delay. The sequencing is not optional.

---

### Pitfall 5: Parallel Dispatch Races to a Single BRAIN-FEED Write

**What goes wrong:**
The orchestrator dispatches 3 brain agents in parallel (e.g., Brain #2, #3, #4 for a frontend-heavy phase). Each agent reads `BRAIN-FEED-NN-domain.md`, queries NotebookLM, filters the response, and then writes new patterns back to its own domain file. Since each writes to a different file (`BRAIN-FEED-02-ux.md`, `BRAIN-FEED-03-ui.md`, `BRAIN-FEED-04-frontend.md`), there is no file-level race. But each agent also writes a cross-domain insight to the global `BRAIN-FEED.md`. Two agents writing to the same global file at the same time results in one overwriting the other's additions — no error, silent data loss. The third agent reads a stale global feed that is missing patterns the first agent just wrote.

**Why it happens:**
FEED-03 says "each agent writes only to its own domain feed." But in practice, agents make judgment calls about what's "cross-domain enough" for the global feed. Without an explicit rule that agents NEVER write to `BRAIN-FEED.md` (only the orchestrator does), agents will attempt global writes. Claude Code's Agent tool does not synchronize writes across parallel subagents — there is no lock mechanism.

**How to avoid:**
Make the write boundary absolute in every agent system prompt: "You write only to your domain feed (`BRAIN-FEED-NN-domain.md`). You never write to `BRAIN-FEED.md`. If you identify a cross-domain pattern during consultation, include it in a `cross-domain-insights` section of your return value. The orchestrator collects all cross-domain insights and writes them to the global feed after all agents complete." This turns the global feed write into a sequential, orchestrator-controlled operation. No race condition possible.

**Warning signs:**
- Multiple domain agents have write instructions that include `BRAIN-FEED.md` (not just their domain file)
- Global BRAIN-FEED.md grows during parallel dispatch (should only grow in post-dispatch synthesis)
- Two consecutive parallel dispatches produce different global feed states for the same input
- An agent's domain feed contains entries that reference patterns from another brain's domain

**Phase to address:** FEED-03 and DISP-01 — both must be addressed together. FEED-03 defines the write boundary; DISP-01 implements the parallel dispatch. If DISP-01 is built without FEED-03 in place, the race condition ships.

---

### Pitfall 6: Agent Context Window Exhaustion From Feed Over-Loading

**What goes wrong:**
An agent system prompt instructs it to "read BRAIN-FEED.md (global) + BRAIN-FEED-NN-domain.md (own domain) before querying." After 3 months of operation, the global feed is 8,000 words and the domain feed is 4,000 words. The agent loads both, builds a context block from relevant code, and then queries NotebookLM. By the time it writes the query, 60% of its context window is consumed by feed content. The NotebookLM response is returned but the agent truncates its filtering step — it doesn't have enough context budget left to systematically verify each recommendation against the codebase.

**Why it happens:**
BRAIN-FEED files are "living documents" that grow over time. The v2.1 update-brain-feed workflow has a compaction rule ("Don't dump everything. Ask: will a brain give a better answer because of this entry?") but this rule is applied per-entry at write time, not as periodic garbage collection. Feeds accumulate redundant, outdated, or overly-specific entries that bloat total size without improving consultation quality.

**How to avoid:**
Enforce a feed size budget at write time, not as periodic cleanup. Each domain feed has a maximum of 50 bullet-point entries (approximately 2,000 words). When the feed reaches 45 entries, the agent's write instruction triggers a compaction step before adding new entries: review the oldest 20 entries, remove any that describe patterns now visible in the codebase (self-documenting code doesn't need a feed entry), merge entries that express the same invariant. The global feed has a stricter limit: 30 entries max. This is not about trimming for trimming's sake — it's about keeping the context budget available for actual analysis.

**Warning signs:**
- BRAIN-FEED.md exceeds 3,000 words
- Any domain BRAIN-FEED file exceeds 2,000 words
- Agent output quality degrades over time without apparent reason (context exhaustion)
- Agent filter step ("for each concern: verify in code") contains fewer verifications than recommended count

**Phase to address:** FEED group — FEED-01 must set initial size budgets as acceptance criteria. Add to AGT-01 system prompt templates: the feed size enforcement rule.

---

### Pitfall 7: BRAIN-FEED Poisoning via Unverified Patterns

**What goes wrong:**
Brain #4 (Frontend) consults NotebookLM about state management patterns. NotebookLM recommends "use Redux Toolkit for complex state." The agent lacks evaluation-criteria.md or the criteria don't explicitly cover stack lock-in. The agent adds this to `BRAIN-FEED-04-frontend.md`. In the next consultation, the agent reads this as an established project pattern and begins recommending Redux Toolkit for new state requirements — even though the project uses Zustand 5 with Immer, proven across 4 phases. The poisoned feed entry overrides actual codebase reality.

**Why it happens:**
This is the specific risk Brain #7 identified before v2.2: "wrong pattern in feed = 'expertise' envenenado." The root cause is two-fold: (a) evaluation-criteria.md doesn't exist yet when the agent writes its first entry, or (b) the criteria exist but don't include a "verify against codebase before writing" gate.

**How to avoid:**
Evaluation criteria must include a mandatory pre-write verification rule: "Before writing any pattern to the domain feed, verify it is not contradicted by the locked stack in the global BRAIN-FEED.md. If the pattern requires a different library than what's in the stack, the pattern is rejected — not added with a note, rejected." Anti-patterns.md for each brain serves as the explicit rejection list. A pattern that matches an entry in anti-patterns.md cannot enter the domain feed under any circumstances. The agent's write gate is: (1) not already in feed, (2) not in anti-patterns, (3) not contradicted by stack in global feed.

**Warning signs:**
- Domain feed contains a library recommendation that contradicts the stack table in global BRAIN-FEED.md
- A pattern is added to the domain feed before the agent has read the codebase to verify it
- Two consecutive consultations on the same feature suggest different approaches (feed was poisoned then corrected)
- Anti-patterns.md file doesn't exist (no rejection list means no protection)

**Phase to address:** AGT-02 (evaluation-criteria) and AGT-03 (anti-patterns) — these two files are the poison prevention mechanism. AGT-01 (agent files) must reference both explicitly in the write gate. Creating AGT-01 without AGT-02 and AGT-03 produces an unprotected write path.

---

### Pitfall 8: Smoke Test Passes Syntactically But Not Semantically

**What goes wrong:**
AGT-04 acceptance criterion is "each agent can be dispatched, reads its feeds, queries its NotebookLM brain, filters for codebase reality, and returns verified insights." The smoke test dispatches each agent, observes it reads the feed files, sees a NotebookLM query in the transcript, and marks the test passed. What it doesn't check: did the filter step actually reject any recommendations? Did the agent verify even one recommendation against the codebase by reading code? Did it try to write a recommendation that anti-patterns.md should have blocked? A syntactic smoke test can pass while the agent's quality gate is effectively absent.

**Why it happens:**
Smoke tests are optimized to check happy-path completeness, not quality-gate enforcement. The intermediary protocol's value comes from the filter step (Step 5) and the cascade rule (Step 6). Both require active exercise of rejection — which only happens when the brain returns a recommendation that conflicts with codebase reality. A smoke test that uses an easy question ("What are best practices for product discovery?") will never trigger a filter rejection because the brain's generic advice won't conflict with anything in a typical BRAIN-FEED.

**How to avoid:**
Design smoke test prompts specifically to trigger filter rejections. Use a question where NotebookLM will likely suggest something the codebase already implements or explicitly rejected. For Brain #4 (Frontend): "What state management approach should we use for real-time brain status updates across 24 concurrent tiles?" NotebookLM will recommend Redux, MobX, or Context API. The agent's filter should reject all three (Zustand 5 + Immer + RAF batching is in both the stack lock and BRAIN-FEED). A smoke test that passes AGT-04 correctly shows at least one rejection in the filter log per agent.

**Warning signs:**
- Smoke test transcript shows 0 rejected recommendations (agent passed everything through)
- Smoke test prompt is generic ("give me best practices for X domain")
- All 7 smoke tests complete in under 2 minutes (agents aren't doing actual codebase verification)
- Agent returns the same recommendations that anti-patterns.md explicitly lists

**Phase to address:** AGT-04 — redesign the smoke test prompt design to be adversarial. One question per agent that should trigger at least one rejection. Document the expected rejections before running the test.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Copy skill workflow steps verbatim into agent system prompt | Fast migration | Agent behaves as a slow skill, not an autonomous agent. No quality improvement | Never — reframe as internalized behavior |
| Skip evaluation-criteria.md for "simple" brains | Faster delivery | No filter standard. Feed degrades with unverified entries | Never — criteria are the quality gate |
| Use the same anti-patterns.md template for all 7 brains | Saves time upfront | Domain-specific anti-patterns missed (e.g., Frontend brain won't know Product anti-patterns) | Never — each brain needs domain-specific rejections |
| Write baselines after migration, not before | Avoids delay | Can't distinguish improvement from degradation — baselines after are meaningless | Never — before-only, no exceptions |
| Allow agents to write to global BRAIN-FEED.md | Simpler agent instructions | Silent write race condition in parallel dispatch | Never — orchestrator-controlled global writes only |
| Skip feed size budgets until feeds "feel too long" | Less cognitive overhead | Gradual context window exhaustion. Quality degrades invisibly over 2-3 months | Acceptable if team commits to manual quarterly compaction |
| Dispatch agents sequentially in DISP-01 to avoid race conditions | Eliminates write race at the cost of parallelism | Misses the key value of v2.2 (parallel domain expertise). Equivalent to the old skill pattern | Acceptable as a temporary step before FEED-03 write boundaries are validated |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| **mm:brain-context → agent dispatch** | Update `mm:brain-context` to call agents in parallel but forget to update the Moment routing logic | Verify all 4 moment workflows (moment-1.md, moment-2.md, moment-3.md, update-brain-feed.md) are updated for DISP-02, not just the main SKILL.md |
| **Agent tool dispatch + NotebookLM MCP** | Agent dispatched with Agent tool tries to invoke `mcp__notebooklm-mcp__notebook_query` but NotebookLM MCP tool is not in the agent's allowed-tools list | Explicitly include NotebookLM MCP tools in agent file front matter. Tool access does not inherit from the parent invocation. |
| **BRAIN-FEED split + existing skill** | Old `mm:brain-context` skill still references `BRAIN-FEED.md` as the single file. After split, skill reads global-only and misses domain patterns | Update skill's intermediary protocol references after FEED-01 split completes. The skill is decommissioned by DISP-02 but must remain functional until DISP-02 completes. |
| **Agent system prompt file path** | Agent expects feeds at `.planning/BRAIN-FEED-NN.md` but actual path uses domain suffix `.planning/BRAIN-FEED-01-product.md` | Standardize and lock the naming convention in FEED-01 before writing any agent system prompts. Path in system prompt cannot be refactored without editing all 7 agent files. |
| **Parallel dispatch + orchestrator context** | Orchestrator dispatches agents in parallel but passes a stale copy of the project context to each | Ensure agents read fresh context from files (not from orchestrator's passed summary). Agents should independently read their feeds from disk, not rely on orchestrator-provided content. |
| **evaluation-criteria.md location** | Criteria files stored alongside agent files in `.claude/agents/` but agent system prompt references wrong relative path | Establish file structure convention (suggest `.claude/agents/criteria/brain-NN-evaluation.md`) before creating any criteria files. |
| **AGT-04 smoke test isolation** | Running all 7 smoke tests sequentially causes each agent to read domain feeds written by the previous agent's test — contaminated test state | Each smoke test should run against a clean feed snapshot. Either use isolated test feeds or clear domain feed additions after each smoke test. |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| **Feed over-loading per consultation** | Consultation takes 3x longer than baseline; agent context budget exhausted before filtering step | Feed size budgets enforced at write time (50 entries max per domain feed) | When any domain feed exceeds ~2,000 words |
| **Sequential agent dispatch masquerading as parallel** | `mm:brain-context` updated to "dispatch agents" but the dispatch loop is actually awaited serially | Use Agent tool with truly parallel invocation. Time multiple agents to verify they start within 1s of each other. | Immediately visible if timed, invisible if not measured |
| **NotebookLM cold-start penalty in smoke tests** | All 7 smoke tests run against cold NotebookLM sessions. First query per notebook is 2-3x slower than warm | Account for this in baseline measurements. Do not penalize agents for cold-start latency. | In every test run since notebooks don't stay warm indefinitely |
| **Anti-patterns.md growing into a knowledge base** | anti-patterns.md file grows beyond 30 entries as team adds every rejected pattern ever seen | anti-patterns.md is a rejection list, not a learning log. Cap at 20 entries per brain. Archive to a separate file if needed. | When more than 5 agents reference anti-patterns that are 6+ months old |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| **API keys or notebook IDs in agent system prompts** | Notebook IDs (e.g., `f276ccb3-...`) in `.claude/agents/brain-01-product.md` are readable by anyone with repo access. Low severity today (these are NotebookLM IDs, not API keys), but establishes a bad pattern | Store notebook IDs in `.claude/skills/mm/brain-context/references/brain-selection.md` (already exists). Agent system prompts reference brain ID numbers only — the mapping lives in the reference file. |
| **Agent allowed-tools without Write restriction** | A brain agent with unrestricted Write access could accidentally modify source files if a confused recommendation lands in a Bash command | Restrict brain agent `tools` front matter to `Read, Grep, Glob, Bash (read-only), Write` where Write is scoped to `.planning/` only. This matches the skill's `allowed-tools: Read, Bash, Grep, Glob` pattern. |
| **BRAIN-FEED committed with internal project context** | If BRAIN-FEED.md contains client-specific data (feature names, business logic) and the repo is later made public | Use generic, architectural language in BRAIN-FEED entries. No business domain names, no client-specific logic. This is about patterns, not content. |

---

## "Looks Done But Isn't" Checklist

- [ ] **AGT-01:** Agent files exist and have correct front matter — verify each agent's `tools` includes NotebookLM MCP, not just file-reading tools
- [ ] **AGT-02:** evaluation-criteria.md exists per brain — verify the criteria include at least one explicit rejection rule that references the locked stack
- [ ] **AGT-03:** anti-patterns.md exists per brain — verify entries include patterns specific to that domain (not copies of the global anti-patterns list)
- [ ] **FEED-01:** All 8 feed files exist — verify each entry in the old monolith appears in exactly ONE file (one-owner rule), not copied across multiple
- [ ] **FEED-02:** Agent reads both feeds before querying — verify in smoke test transcript that both `BRAIN-FEED.md` and `BRAIN-FEED-NN-domain.md` are read before the NotebookLM query appears
- [ ] **FEED-03:** Agents write only to domain feed — dispatch 2 agents in parallel and verify `BRAIN-FEED.md` (global) is NOT modified by either
- [ ] **BASE-01:** 5 baselines documented — verify baselines predate any AGT group work (timestamps prove before-migration)
- [ ] **BASE-02:** Metric schema applied — verify each baseline has all 4 metrics (time, gap-count, re-consultations, quality-rating) filled, quality-rating recorded 24h after consultation
- [ ] **DISP-01:** Parallel dispatch implemented — verify via timing that 3 dispatched agents start within 1s of each other (not sequential)
- [ ] **DISP-02:** mm:brain-context updated — verify all 4 moment workflows are updated, not just the main SKILL.md routing table

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| **Workflow-as-steps system prompt** | MEDIUM | Rewrite all 7 agent system prompts. Convert procedure to identity-level behavior. Re-run AGT-04 smoke test. |
| **BRAIN-FEED polluted on migration day** | MEDIUM | Restore BRAIN-FEED.md to last clean state from git. Re-apply the one-owner migration rule. Takes ~2-4 hours for 7 domain files. |
| **Missing evaluation-criteria per agent** | LOW | Write criteria files. Requires 1-2h domain research per brain. No code changes required. |
| **No baseline before migration** | HIGH (unrecoverable) | Cannot recreate pre-migration baselines after the fact. Retrospective reconstruction is not the same measurement. Accept the gap and start measuring from now. Document what's known about the old workflow performance from memory. |
| **Global feed write race condition** | LOW (if caught early) | Remove global write instructions from agent system prompts. Add cross-domain-insights section to agent return value schema. Update orchestrator to handle synthesis. |
| **Feed size exceeds context budget** | MEDIUM | Manual compaction: read each feed, remove entries that are now documented in code, merge redundant entries. Implement size budget enforcement. Takes ~1h per feed. |
| **Poisoned BRAIN-FEED entry** | LOW-MEDIUM | Identify poisoned entries (look for library recommendations that contradict locked stack). Remove them. Add them to anti-patterns.md. Run smoke test to verify agent now rejects the pattern. |
| **Smoke test passes without filter rejection** | LOW | Redesign smoke test prompts to be adversarial. No code changes needed — just better test questions. |

---

## Pitfall-to-Phase Mapping

| Pitfall | Requirement Group | Prevention | Verification |
|---------|--------------------|------------|--------------|
| Workflow-as-steps system prompt | AGT-01 | Agent identity-level framing, not procedure steps | AGT-04 smoke test: agent reads feeds without explicit instruction |
| BRAIN-FEED pollution on migration | FEED-01 | One-owner migration rule before split | Each entry appears in exactly 1 file |
| Missing evaluation criteria | AGT-02 | criteria files before agent files are finalized | Criteria includes at least 1 rejection rule referencing locked stack |
| No baseline before migration | BASE-01, BASE-02 | Baseline before AGT group starts | File timestamps predate first AGT file |
| Parallel write race to global feed | FEED-03, DISP-01 | Write boundary absolute in all 7 agent prompts | Parallel dispatch test: global feed unchanged |
| Context window exhaustion | FEED-01 | Size budget as acceptance criterion in FEED-01 | No feed file > 2,000 words |
| BRAIN-FEED poisoning | AGT-02, AGT-03 | Evaluation criteria + anti-patterns as write gate | Smoke test triggers known rejection correctly |
| Smoke test semantic failure | AGT-04 | Adversarial smoke test prompt design | Each agent transcript shows ≥1 rejected recommendation |

---

## Sources

- **Codebase — `.claude/skills/mm/brain-context/SKILL.md`** — existing skill structure being replaced (HIGH confidence)
- **Codebase — `.claude/skills/mm/brain-context/references/intermediary-protocol.md`** — 6-step protocol that agents must internalize (HIGH confidence)
- **Codebase — `.planning/BRAIN-FEED.md`** — current monolith structure, sizing reference (HIGH confidence)
- **Codebase — `.planning/REQUIREMENTS.md`** — AGT/FEED/BASE/DISP requirement groups (HIGH confidence)
- **Codebase — `.planning/PROJECT.md`** — "intermediary protocol becomes built-in behavior, not a workflow to read and follow" (HIGH confidence — explicit decision)
- **Claude Code agent format — `/home/rpadron/.claude/plugins/marketplaces/claude-plugins-official/`** — production agent files, tool restrictions, system prompt patterns (HIGH confidence)
- **Brain #7 pre-v2.2 consultation output** — BRAIN-FEED poisoning risk identified as top gap before requirements approval (HIGH confidence — documented in REQUIREMENTS.md AGT-03 rationale)
- **Training knowledge — Claude Code subagent behavior** — context window constraints, parallel Agent tool dispatch, lack of cross-agent write synchronization (MEDIUM confidence — verify tool access inheritance empirically during AGT-04)

---
*Pitfalls research for: MasterMind Framework v2.2 — Brain Agents migration*
*Researched: 2026-03-27*
