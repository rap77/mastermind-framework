# Brain #06-QA — Evaluation Criteria

## Purpose

This file defines how to evaluate Brain #6 (QA/DevOps) responses against the Delta-Velocity Matrix. Use this file when rating a consultation output. The criteria are observable and domain-specific — not generic quality statements.

A response that "sounds thorough" but cannot be rated against this table is a Rating 2 at best.

---

## Rating 3 (Peer) vs Rating 4 (Senior)

| Attribute | Rating 3 (Peer) | Rating 4 (Senior) |
|-----------|-----------------|-------------------|
| **Test strategy** | Provides correct test type for the scenario (unit vs integration) | Identifies which test pyramid layer and explains WHY this specific layer — not just "add a test" |
| **Coverage** | Adds tests for the happy path | Identifies edge cases: concurrent access, timeout, partial failure scenarios — tests the failure modes, not just the success path |
| **CI/CD** | Provides correct pipeline step addition | Identifies the feedback loop bottleneck — where does the pipeline slow the team down? Proposes specific speed improvement |
| **Observability** | Adds logging to the change | Defines what makes an alert actionable vs. noise — proposes specific SLI/SLO with measurable target |
| **Legacy** | Writes tests for new code | Characterizes existing behavior before refactoring (Feathers approach — test the seam, verify behavior, then change) |

**Observable distinction:** A Rating 3 response adds the correct test. A Rating 4 response explains what to test, why that layer, and what the test would catch that currently would silently fail.

---

## Auto-Reject (Rating 1)

**Suite Failure Tolerance:**
Any proposal that leaves the test suite at < 100% green = Rating 1. No "pre-existing failures" excuse. The baseline is 570/570 + 407/407. Zero tolerance.

```
Rejected: proposal leaves existing tests failing without migration plan.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-06-qa/warnings.md > Pre-Existing Failure Tolerance
```

**Live MCP Test:**
Any proposal for a test that requires a live NotebookLM MCP call to pass = Rating < 3. Tests must be offline-runnable. Live network dependencies in tests are flaky by definition.

```
Rejected: test requires live NotebookLM connection — violates offline test requirement.
Source: brain-06-qa/criteria.md > Auto-Reject | brain-06-qa/warnings.md > Live MCP Test
```

---

## Rating 5 (Architect) Threshold

A Rating 5 response:
- Identifies a test coverage gap that would cause a silent failure under production conditions (concurrent brain queries exceeding TaskGroup limits, JWT expiry during a multi-step operation)
- Proposes a characterization test that captures the exact behavior boundary of a legacy component before refactoring, making the refactor provably safe
- Designs a test pyramid restructure that reduces test suite runtime by 30%+ without reducing coverage
- Identifies a flakiness root cause in the existing suite and provides a deterministic fix

---

## Minimum for Rating 3

A response must satisfy ALL of the following to be Rating 3:

1. Uses `pnpm --prefix apps/web test run` for frontend — not `npm test`
2. Uses `cd apps/api && uv run pytest` for backend — not `uv run pytest` from root
3. Every proposed test is runnable offline — no live MCP/NotebookLM dependency
4. Does not propose changes that would break the 570/407 suite without a migration plan
5. References `.pre-commit-config.yaml` at repo root for any pre-commit hook changes

If any of these are missing, the response is Rating 2 regardless of test quality.

---

## Evaluation Checklist

When rating a Brain #6 response, verify:

- [ ] Did the brain read BRAIN-FEED.md before responding? (Step 1 — ask to show it)
- [ ] Does the `[IMPLEMENTED REALITY]` block reflect the actual test suite counts (570/570 + 407/407)?
- [ ] Are the 5 domain-specific `[CORRECTED ASSUMPTIONS]` present? (Step 3)
- [ ] Are proposed tests offline-runnable — no live MCP dependency?
- [ ] Does the test strategy name the pyramid layer AND explain why that layer?
- [ ] Are failure modes covered — not just the happy path?
- [ ] Did the brain write to `.planning/BRAIN-FEED-06-qa.md` only? (Step 6 — Feed Write Scope)

Failing 3+ checklist items = Rating 2 regardless of content quality.
