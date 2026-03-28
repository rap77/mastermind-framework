---
schema_version: "1.0"
context_id: "bcfb93803e7ca5ca1c6b99c554fd190c77196f5a"
brain_id: 6
ticket_type: adversarial

brain_feed_snapshot:
  - .planning/BRAIN-FEED.md
  - .planning/STATE.md
  - apps/api/tests/
  - apps/web/src/__tests__/

input_prompt_raw: |
  We're adding 7 new Claude Code subagents to .claude/agents/mm/. Define the integration test
  strategy for verifying that each agent: (1) reads both BRAIN-FEED files before querying,
  (2) writes ONLY to its own domain feed, (3) rejects Stack Hallucination suggestions.
  No e2e tests that require live NotebookLM calls — tests must be runnable offline.

cognitive_trace:
  T1_setup_seconds: 225
  T2_ai_latency_seconds: 52
  T3_review_seconds: 190

delta_velocity_score: 3

characterization_diff: |
  Expected: Brain might suggest Selenium or browser automation for testing Claude Code agents, or propose live integration tests requiring actual NotebookLM API calls. Risk of suggesting mocking the entire agent behavior (defeating the test purpose).
  Observed: Brain correctly identified that Claude Code subagents are tested via subprocess invocation, not browser. Proposed pytest-mock for MCP tool interception at the protocol layer. Correctly addressed offline constraint. Did not suggest live API calls.

human_intervention_log:
  - gap: "Brain proposed using pytest-mock to intercept MCP calls but did not specify the fixture structure for simulating NotebookLM tool responses"
    correction: "Human had to define the MCP fixture shape: mock_notebooklm_query returns dict with keys 'insights', 'gaps', 'confidence' — matching actual NotebookLM MCP response schema"
  - gap: "Test for 'writes only to its own domain feed' was specified as file-system assertion (check file content after run) but lacked setup for feed file isolation"
    correction: "Added tmpdir fixture scoping so each test gets a fresh BRAIN-FEED.md copy — prevents cross-test contamination"
---

# Baseline 03 — QA Single-Brain (Adversarial: Agent Integration Test Strategy)

## Frozen Context Block

**Vision (3-5 años):** Autonomous brain agents that accumulate domain knowledge and execute the intermediary protocol faster than a human expert.
**Strategic Intent:** v2.2 — Convert mm:brain-context skill workflows to autonomous subagents
**Outcome Metrics:** Agent executes protocol in <20% human T1 time; Delta-Velocity >= 3 on first run

---

## Ticket

We're adding 7 new Claude Code subagents to `.claude/agents/mm/`. Define the integration test strategy for verifying that each agent: (1) reads both BRAIN-FEED files before querying, (2) writes ONLY to its own domain feed, (3) rejects Stack Hallucination suggestions. No e2e tests that require live NotebookLM calls — tests must be runnable offline.

---

## Brain(s) Consulted

Brain #6 — QA/DevOps (Reliability Fundamentalist)
Notebook: `74cd3a81-1350-4927-af14-c0c4fca41a8e`

---

## Raw Brain Response (Summary)

SIMULATED: Brain #6 response on agent integration test strategy:

**Testing approach: Characterization Tests + MCP Interception**

The three behaviors (BRAIN-FEED read, domain-scoped write, hallucination rejection) map to distinct test layers:

**Layer 1 — BRAIN-FEED Read Verification (Behavior 1)**
Strategy: Intercept the file system read calls during agent invocation. Use `pytest` with `unittest.mock.patch` on `builtins.open` scoped to `.planning/BRAIN-FEED.md` and `.planning/BRAIN-FEED-domain.md`. Assert that both files were opened with `'r'` mode before any MCP tool call occurs.

```python
def test_agent_reads_brain_feed_before_query(mock_open_files, agent_runner):
    with patch("builtins.open", side_effect=track_open) as mock_open:
        agent_runner.invoke("brain-04-frontend", ticket="test ticket")
    assert ".planning/BRAIN-FEED.md" in opened_files
    assert ".planning/BRAIN-FEED-04-frontend.md" in opened_files
```

**Layer 2 — Domain-Scoped Write Verification (Behavior 2)**
Strategy: File-system assertion after agent run. Agent is invoked with a test ticket; post-run, verify that only the agent's domain feed was modified, not the global feed or other domain feeds.

```python
def test_agent_writes_only_to_own_domain_feed(tmpdir, agent_runner):
    # Setup: copy BRAIN-FEED files to tmpdir, point agent to tmpdir
    assert modified_files == {f".planning/BRAIN-FEED-{brain_id}.md"}
```

**Layer 3 — Stack Hallucination Rejection (Behavior 3)**
Strategy: Adversarial prompt injection. Feed the agent a ticket that includes a suggestion to use an unlocked library (e.g., "use react-virtualized for node rendering"). Assert that the agent response contains the rejection pattern from the Oracle Pattern spec:
```
Rejected: [library] violates Stack Lock.
Source: global-protocol.md > Stack Hard-Lock
```

**MCP Interception for offline testing:**
Use `pytest-mock` to intercept `mcp.call_tool("notebooklm_query", ...)` at the protocol layer. Return a structured mock response without live API call.

---

## Filtered Insights

**Survived grep verification (Step 5):**
- pytest + unittest.mock.patch for file system interception: CONFIRMED — existing test infrastructure in `apps/api/tests/`
- Characterization test pattern: CONFIRMED — aligns with Brain #6 knowledge base (Feathers, Working Effectively with Legacy Code)
- File-system assertion for write scope: CONFIRMED — viable, no live deps
- Adversarial prompt injection for hallucination rejection: CONFIRMED — aligns with oracle pattern spec

**Rejected:**
- pytest-mock fixture without concrete response shape: Brain left the mock response schema underspecified. Human defined it as `{'insights': list[str], 'gaps': list[str], 'confidence': float}`.
- No tmpdir scoping for feed file isolation: Brain's test setup shared BRAIN-FEED files across tests. Human added `tmpdir` fixture to prevent cross-test contamination.

---

## Gaps Found

1. **MCP fixture response shape unspecified** — Brain proposed pytest-mock for MCP interception but did not define what the mock response should look like. The actual NotebookLM MCP response schema has specific keys (`insights`, `gaps`, `confidence`). Human had to derive the fixture shape from the existing MCP tool documentation. This is the primary T3 overhead — 60 additional seconds spent defining mock shape.

2. **Feed isolation not addressed** — Brain's file-system assertion tests shared BRAIN-FEED.md state across runs. Without `tmpdir` scoping, tests contaminate each other when run in parallel (`pytest -n auto`). Human added fixture isolation pattern.

3. **No assertion ordering guarantee** — Brain did not specify that BRAIN-FEED read must precede the MCP call (not just that both happen). The ordering assertion requires a more explicit mock spy pattern. Human left this as a deferred test improvement — current tests verify presence, not ordering.

---

## T1 Analysis

`T1_setup_seconds: 225` — Within the 300-second profitability threshold.

Steps during T1:
- Read `.planning/BRAIN-FEED.md` (65s) — identify existing test infrastructure and patterns
- Review `apps/api/tests/` structure (60s) — understand pytest fixtures, conftest.py patterns, existing mock usage
- Build `[IMPLEMENTED REALITY]` block (55s) — document test suite structure, mock patterns, offline test conventions
- Build `[CORRECTED ASSUMPTIONS]` block (45s) — confirm no live API calls in existing test suite, pytest-mock available

**Flag:** Not agent-unprofitable. T1 < 300s.

---

## Adversarial Validation Notes

Ground truth for adversarial ticket = adherence to system principles. Brain #6 passed on:
- No suggestion of live NotebookLM calls (correctly respected offline constraint)
- No browser/Selenium suggestion (correctly identified CLI-invoked agent architecture)
- Characterization test pattern correctly applied (working with unknown agent behavior, not prescribing it)

Brain scored 3 (Peer) — correct strategy but required human to fill in 2 fixture-level specifications. A Rating 4 response would have included the MCP mock response shape and the tmpdir isolation pattern without prompting.
