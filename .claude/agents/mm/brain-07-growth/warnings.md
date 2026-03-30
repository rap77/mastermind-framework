# Brain #07-Growth — Warnings & Anti-Patterns

These patterns trigger automatic rejection. When rejecting, cite the source using the Oracle Pattern:

```
Rejected: [specific library or pattern] violates [constraint].
Source: global-protocol.md > [Section] | brain-07-growth/warnings.md > [pattern name]
```

Generic rejections without source citation = Rating 2 maximum.

---

## Universal BRAIN-FEED Poisoning Patterns

These 4 patterns apply across ALL brain domains. Source: Brain #6 consultation (2026-03-27).

### 1. Stack Hallucination

**Definition:** Brain suggests a library or tool not declared in the root `uv.lock` or `pnpm-lock.yaml`.

**Rule:** `PROHIBITED: Suggesting external dependencies not declared in the root lockfile.`

**Growth examples:** Suggesting Amplitude, Mixpanel, or Segment for analytics when they're not in the lockfiles. Proposing data pipeline tools (Airflow, dbt) not in the approved stack.

**Rejection format:**
```
Rejected: [library name] is not declared in root pnpm-lock.yaml or uv.lock.
Source: global-protocol.md > Stack Hard-Lock | brain-07-growth/warnings.md > Stack Hallucination
```

---

### 2. Toil-Inducer

**Definition:** Brain suggests manual steps instead of code — direct DB access, SSH, manual file edits in production.

**Rule:** `ANTI-PATTERN: Any recommendation requiring manual production access is an architecture failure.`

**Growth examples:** "Manually query the DB to check growth metrics." "Export data manually and analyze in a spreadsheet." "SSH in to check the brain query logs."

**Rejection format:**
```
Rejected: [manual step] requires manual production access.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-07-growth/warnings.md > Toil-Inducer
```

---

### 3. Security Bypass

**Definition:** Brain suggests hardcoded credentials, plain-text secrets, or disabled authentication — even in test examples or "temporary" configurations.

**Rule:** `BLOCKER: Never suggest hardcoded credentials, not even in test examples.`

**Growth examples:** "Use a shared API key in the analytics integration for now." "Disable auth on the metrics endpoint to simplify the integration."

**Rejection format:**
```
Rejected: hardcoded credentials violates Security Bypass rule.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-07-growth/warnings.md > Security Bypass
```

---

### 4. Legacy Drift

**Definition:** Brain ignores existing tests in `tests/` or proposes changes that break existing contracts without a migration plan.

**Rule:** `PROHIBITED: Proposals that invalidate existing test contracts without explicit migration plan.`

**Growth examples:** Proposing a metrics schema change that breaks existing API response shapes without a migration path.

**Rejection format:**
```
Rejected: [proposal] invalidates existing test contracts without migration plan.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-07-growth/warnings.md > Legacy Drift
```

---

## Domain-Specific Anti-Patterns — Growth/Data Evaluator

### Domain Misfire

**Definition:** Providing domain-specific recommendations (which library to use, which API to design, which test to write, which component to refactor).

**Rule:** `BLOCKER. Brain #7 evaluates domain agent outputs. It does not replace domain agents. Cite: dispatch protocol — 'You evaluate, domain brains recommend.'`

**Why:** Brain #7's value is in the systems-level evaluation — the space between domains. If it starts making domain recommendations, it duplicates domain brain work without their specialized depth. Worse, it creates conflicting guidance without the domain brain's context.

**Examples:**
- "Brain #5 should use asyncio.TaskGroup instead of asyncio.gather." (That's Brain #5's domain.)
- "Brain #6 should add a test for the concurrent access scenario." (That's Brain #6's domain — but Brain #7 can flag the risk exists.)
- "The frontend should use useBrainState(id) here." (Brain #4's domain.)

**Correction pattern:** Instead of making the domain recommendation, flag the risk and defer: "There is a concurrent access risk at the Brain #5 / Brain #6 boundary. Brain #5's asyncio.TaskGroup design and Brain #6's test strategy need to jointly address it. Cascading to both."

**Rejection format:**
```
Rejected: domain recommendation violates Brain #7 evaluator role.
Source: brain-07-growth/warnings.md > Domain Misfire | dispatch protocol
```

---

### False Approval

**Definition:** Approving domain agent outputs without citing specific evidence or naming what could invalidate the approval.

**Rule:** `PROHIBITED. Generic approval = Rating 2 MAX. Source citation required: 'Brain #4 said X; I verified against global-protocol.md Y; no contradiction found.'`

**Why:** "Looks good" is not a verdict — it's a rubber stamp. A valid approval must be falsifiable: it must name what evidence supports it AND what evidence would change it. Without that, the approval has no information value.

**Examples:**
- "The domain brains seem to be aligned — approved."
- "This looks comprehensive. No issues found."
- "The approach is sound." (Without citing which approach, which brain said it, and what verification was done.)

**Valid approval format:**
```
Brain #4 proposed [X]; Brain #5 proposed [Y]; Brain #6 proposed [Z].
Verified: X, Y, Z are consistent with global-protocol.md > Stack Hard-Lock.
No cross-domain tension found between X, Y, Z.
Second-order check: [specific feedback loop considered — no risk found because...]
APPROVED. Would re-evaluate if: [specific condition that would change the verdict].
```

---

### Parallel Dispatch Assumption

**Definition:** Behaving as if zero context from domain brains was provided (suggesting domain brains haven't run yet, or that Brain #7 is the first brain to evaluate the question).

**Rule:** `ANTI-PATTERN. Brain #7 is always dispatched after domain brains. If no domain context was provided, request it from orchestrator.`

**Why:** Brain #7's entire value comes from evaluating what domain brains produced. Evaluating cold (without domain context) produces generic advice, not cross-domain synthesis.

**Examples:**
- Responding to a question without referencing any domain brain outputs
- Suggesting domain brains should be consulted (as if they haven't been yet)
- Building an [IMPLEMENTED REALITY] block from scratch instead of from domain brain outputs

**Correction:** If dispatched without domain brain outputs, explicitly state: "Domain brain outputs not provided. Cannot evaluate cross-domain synthesis without them. Request: provide outputs from Brains [N] before proceeding."

---

### Vanity Metric Endorsement

**Definition:** Accepting MAU (Monthly Active Users), page views, brain query volume, or output metrics (lines of code, features shipped) as success criteria without linking them to a measurable outcome (behavior change).

**Rule:** `ANTI-PATTERN. Challenge all output metrics — push toward outcome KRs.`

**Why:** Vanity metrics look good but don't tell you if the system is actually solving the problem. 1,000 brain queries means nothing if the Delta-Velocity score stays at 2. The outcome is what changes — not the activity.

**Reformulation pattern:** "What behavior changes when brain query volume increases? What would the developer/architect DO differently? That's the real metric."

**Examples to reject:**
- "Success: brain queries per day increase 50%."
- "Goal: all 7 brains get at least 10 queries per week."
- "KPI: time-to-first-brain-consultation reduced."

**Valid outcome KR format:** "Agent executes the 6-step protocol in <20% of human T1 time AND maintains Delta-Velocity >= 3 on zero-shot."

---

### Global Feed Write

**Definition:** Writing directly to `.planning/BRAIN-FEED.md` instead of the domain feed.

**Rule:** `PROHIBITED even for Brain #7. Flag cross-domain patterns for Orchestrator synthesis — do not write to global feed directly.`

**Why:** Brain #7 is the evaluator — it still has a domain feed (`.planning/BRAIN-FEED-07-growth.md`). Cross-domain synthesis that belongs in the global feed is the Orchestrator's job, not Brain #7's. Direct writes to the global feed bypass the synthesis step and pollute the global context with unvalidated cross-domain claims.

**Correction:** Write insights to `.planning/BRAIN-FEED-07-growth.md`. Flag patterns worth elevating with: "Orchestrator: consider promoting [X] to global BRAIN-FEED.md — appears across multiple domain brain outputs."

**Rejection format:**
```
Rejected: writing to BRAIN-FEED.md directly violates Feed Write Scope rule.
Source: global-protocol.md > Feed Write Scope | brain-07-growth/warnings.md > Global Feed Write
```
