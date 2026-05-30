# Brain #01-Product — Warnings & Anti-Patterns

These patterns trigger automatic rejection. When rejecting, cite the source using the Oracle Pattern:

```
Rejected: [specific library or pattern] violates [constraint].
Source: global-protocol.md > [Section] | brain-01-product/warnings.md > [pattern name]
```

Generic rejections without source citation = Rating 2 maximum.

---

## Universal BRAIN-FEED Poisoning Patterns

These 4 patterns apply across ALL brain domains. Source: Brain #6 consultation (2026-03-27).

### 1. Stack Hallucination

**Definition:** Brain suggests a library or tool not declared in the root `uv.lock` or `pnpm-lock.yaml`.

**Rule:** `PROHIBITED: Suggesting external dependencies not declared in the root lockfile.`

**Examples:** Suggesting Amplitude, Mixpanel, or LaunchDarkly without verifying they're in `pnpm-lock.yaml`. Proposing a Python analytics library not in `uv.lock`.

**Rejection format:**
```
Rejected: [library name] is not declared in root pnpm-lock.yaml or uv.lock.
Source: global-protocol.md > Stack Hard-Lock | brain-01-product/warnings.md > Stack Hallucination
```

---

### 2. Toil-Inducer

**Definition:** Brain suggests manual steps instead of code — direct DB access, SSH, manual file edits in production.

**Rule:** `ANTI-PATTERN: Any recommendation requiring manual production access is an architecture failure.`

**Examples:** "Manually update the user's plan tier in the database." "SSH into the server and restart the process." "Manually edit the BRAIN-FEED.md to remove stale entries."

**Rejection format:**
```
Rejected: [manual step] requires manual production access.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-01-product/warnings.md > Toil-Inducer
```

---

### 3. Security Bypass

**Definition:** Brain suggests hardcoded credentials, plain-text secrets, or disabled authentication — even in test examples or "temporary" configurations.

**Rule:** `BLOCKER: Never suggest hardcoded credentials, not even in test examples.`

**Examples:** "For now, hardcode the API key to test the flow." "Disable auth temporarily to debug the issue." "Use a test credential: api_key='sk-test-123'."

**Rejection format:**
```
Rejected: hardcoded credentials violates Security Bypass rule.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-01-product/warnings.md > Security Bypass
```

---

### 4. Legacy Drift

**Definition:** Brain ignores existing tests in `tests/` or proposes changes that break existing contracts without a migration plan.

**Rule:** `PROHIBITED: Proposals that invalidate existing test contracts without explicit migration plan.`

**Examples:** Suggesting an API contract change without addressing existing API tests. Proposing a schema change that breaks the 575-test suite without a migration path.

**Rejection format:**
```
Rejected: [proposal] invalidates existing test contracts without migration plan.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-01-product/warnings.md > Legacy Drift
```

---

## Domain-Specific Anti-Patterns — Product Strategy

### Build Trap

**Definition:** Proposing a feature delivery roadmap without validating user demand. Optimizing for outputs (features shipped) instead of outcomes (behavior changes).

**Rule:** `PROHIBITED: Automatically triggers Rating 1-2.`

**Why:** The Build Trap is the most fundamental product strategy failure. A date-fixed feature roadmap signals the team is a feature factory, not an empowered product team. Cite: Torres/continuous-discovery — "Build Trap = optimizing for outputs, not outcomes."

**Examples:**
- "Here's what we should build in Q2: Feature A in week 1, Feature B in week 2..."
- "If we ship X, Y, and Z by March, we'll have a complete product."
- Proposing backlog items without evidence of user pain behind them.

**Rejection format:**
```
Rejected: feature roadmap without demand validation = Build Trap.
Source: brain-01-product/warnings.md > Build Trap | Torres/continuous-discovery
```

---

### Vanity Metric Proposal

**Definition:** Citing page views, downloads, MAU (Monthly Active Users), or activity metrics as success metrics without linking them to a measurable outcome (behavior change).

**Rule:** `ANTI-PATTERN: Requires outcome KR reformulation before acceptance.`

**Why:** Vanity metrics look good but don't tell you if the product is actually solving the problem. "10,000 signups" means nothing if 9,900 churn in week 1.

**Examples:**
- "Success metric: 1,000 monthly users."
- "We'll know it's working when brain query volume increases."
- Tracking usage without measuring whether the usage achieved the intended behavior change.

**Reformulation pattern:** "What behavior change would 1,000 users accomplish? What would they do differently because of this feature?" — that's the real metric.

---

### Solution Space Anchoring

**Definition:** Jumping to a solution before defining the opportunity (user pain + context + desired outcome).

**Rule:** `ANTI-PATTERN: Opportunity framing must precede solution framing.`

**Why:** Solutions proposed without opportunity framing anchor the conversation to a specific implementation, killing the exploration of alternatives. The solution might solve the wrong problem.

**Examples:**
- "We should add a dashboard to show brain usage metrics." (solution-first, no pain stated)
- "The fix is to add caching here." (without stating what the user experience problem is)
- Responding to "what should we build next?" with a feature list instead of a problem map.

**Correction pattern:** "What user pain is this dashboard solving? Who experiences that pain and when? What would they do differently if the pain were gone?" — force opportunity space first.

---

### Stakeholder Theater

**Definition:** Reframing a business requirement or stakeholder demand as a user need to give it false legitimacy.

**Rule:** `BLOCKER for Rating >= 3. Cite: Cagan/SVPG — "The biggest risk is building the wrong product."`

**Why:** This is the most insidious pattern because it sounds user-centric but isn't. "The CEO wants X" becomes "users need X" without evidence. This corrupts the discovery process and leads to building what executives imagine, not what users actually need.

**Examples:**
- "Our investors want a mobile app, so our users clearly need mobile." (business requirement → fake user need)
- "Since the team voted for this feature, users must want it." (internal consensus → fake user evidence)
- Quoting internal stakeholders as evidence of user pain without actual user research.

**Detection pattern:** Ask "is there direct evidence from users, or is this someone else's assumption?" If there's no user quote, observation, or behavior data, it's stakeholder theater.
