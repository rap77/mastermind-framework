# Brain #06-QA — Warnings & Anti-Patterns

These patterns trigger automatic rejection. When rejecting, cite the source using the Oracle Pattern:

```
Rejected: [specific library or pattern] violates [constraint].
Source: global-protocol.md > [Section] | brain-06-qa/warnings.md > [pattern name]
```

Generic rejections without source citation = Rating 2 maximum.

---

## Universal BRAIN-FEED Poisoning Patterns

These 4 patterns apply across ALL brain domains. Source: Brain #6 consultation (2026-03-27).
Brain #6 was the source of these patterns — they are embedded here as primary reference.

### 1. Stack Hallucination

**Definition:** Brain suggests a library or tool not declared in the root `uv.lock` or `pnpm-lock.yaml`.

**Rule:** `PROHIBITED: Suggesting external dependencies not declared in the root lockfile.`

**QA examples:** Suggesting Jest when Vitest is the test runner in `pnpm-lock.yaml`. Proposing coverage tools not in lockfiles. Recommending `nox` for Python test automation when `pytest` + `uv` is the stack.

**Rejection format:**
```
Rejected: [library name] is not declared in root pnpm-lock.yaml or uv.lock.
Source: global-protocol.md > Stack Hard-Lock | brain-06-qa/warnings.md > Stack Hallucination
```

---

### 2. Toil-Inducer

**Definition:** Brain suggests manual steps instead of code — direct DB access, SSH, manual file edits in production.

**Rule:** `ANTI-PATTERN: Any recommendation requiring manual production access is an architecture failure.`

**QA examples:** "Manually check the logs to verify the fix worked." "SSH in and look at the queue depth." "Edit the test fixture manually before running the suite."

**Rejection format:**
```
Rejected: [manual step] requires manual production access.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-06-qa/warnings.md > Toil-Inducer
```

---

### 3. Security Bypass

**Definition:** Brain suggests hardcoded credentials, plain-text secrets, or disabled authentication — even in test examples or "temporary" configurations.

**Rule:** `BLOCKER: Never suggest hardcoded credentials, not even in test examples.`

**QA examples:** Using `api_key="test-hardcoded-key"` in pytest fixtures. "Disable auth in the test environment to simplify the integration test." Setting `JWT_SECRET=insecure` in test config files.

**Rejection format:**
```
Rejected: hardcoded credentials violates Security Bypass rule.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-06-qa/warnings.md > Security Bypass
```

---

### 4. Legacy Drift

**Definition:** Brain ignores existing tests in `tests/` or proposes changes that break existing contracts without a migration plan.

**Rule:** `PROHIBITED: Proposals that invalidate existing test contracts without explicit migration plan.`

**QA examples:** Proposing API schema changes without updating the existing API test fixtures. Changing test utilities in `tests/conftest.py` without verifying all test files that import them.

**Rejection format:**
```
Rejected: [proposal] invalidates existing test contracts without migration plan.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-06-qa/warnings.md > Legacy Drift
```

---

## Domain-Specific Anti-Patterns — QA/DevOps

### Coverage Theater

**Definition:** Adding tests that only test happy paths and assert what the code already does (tautological tests). Tests that pass by definition, not by verification.

**Rule:** `ANTI-PATTERN. Characterization tests must cover the failure modes, not just the success path.`

**Why:** A test that only verifies the happy path gives false confidence. The failures — timeouts, concurrent access, partial data — are where production systems actually break. Feathers: "Tests that don't test the seams aren't protecting the refactor."

**Examples:**
- Unit test that asserts `result == expected` where `expected` is set to whatever the function currently returns
- Test that only calls the happy path and asserts `status_code == 200`
- Test suite with 100% line coverage but zero error path coverage

**Correction pattern:** For every happy path test, add at minimum: one timeout/latency scenario + one input validation failure + one concurrent access scenario.

---

### Pre-Existing Failure Tolerance

**Definition:** Suggesting a fix that leaves other tests failing as "pre-existing issues" or "known failures."

**Rule:** `BLOCKER. Zero failures is the baseline. Always. Cite: project rules — 'Suite must be in 0 failures before closing a phase.'`

**Why:** Pre-existing failures mask new failures. A suite with 5 "known" failures normalizes failure. The moment the suite goes from 5 to 6 failures, the team doesn't notice because 5 failures was already "normal." Zero tolerance is the only defensible policy.

**Examples:**
- "These 3 tests have been failing since the DB migration — we can ignore them for now."
- "The fixture is broken but it doesn't affect this feature."
- Closing a phase with any test marked `xfail`, `skip`, or failing without a documented justification and fix date.

**Rejection format:**
```
Rejected: leaving tests failing = Pre-Existing Failure Tolerance violation.
Source: brain-06-qa/warnings.md > Pre-Existing Failure Tolerance | project rules
```

---

### npm Reference

**Definition:** Suggesting `npm test`, `npm install`, or any npm command for this project.

**Rule:** `PROHIBITED = Stack Hallucination. pnpm only for Node.js, uv for Python.`

**Why:** The project uses pnpm lockfile. Running `npm install` creates a parallel `node_modules` that conflicts with pnpm's symlink structure. The correct commands are `pnpm --prefix apps/web test run` (frontend) and `cd apps/api && uv run pytest` (backend).

**Rejection format:**
```
Rejected: npm violates pnpm-only Node.js package management rule.
Source: global-protocol.md > Stack Hard-Lock | brain-06-qa/warnings.md > npm Reference
```

---

### Live MCP Test

**Definition:** Designing a test that requires a live NotebookLM MCP call to pass.

**Rule:** `PROHIBITED. All tests must pass offline. Mock the MCP tool in tests.`

**Why:** Tests with live network dependencies are flaky by definition. A NotebookLM API timeout means your test suite fails in CI. The MCP tool must be mockable — and the test must verify the behavior of the code under test, not the behavior of an external API.

**Examples:**
- Integration test that calls `mcp__notebooklm-mcp__notebook_query` directly
- Test that requires a real notebook to exist and respond
- Fixture that sets up a real MCP connection to seed test data

**Correction pattern:** Mock the MCP tool at the boundary. Test that the brain sends the correct query format (contract test) separately from testing NotebookLM's response (which is their responsibility, not ours).

**Rejection format:**
```
Rejected: test requires live NotebookLM connection — violates offline test requirement.
Source: brain-06-qa/warnings.md > Live MCP Test
```
