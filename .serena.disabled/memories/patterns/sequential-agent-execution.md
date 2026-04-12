# Pattern: Sequential Agent Execution for Large Phases

**Pattern:** When executing phases with 3+ plans, use sequential agent spawning instead of parallel.

**Why:** Parallel agent spawning (3+ agents simultaneously) triggers Claude API 429 rate limits. Sequential execution (one agent at a time) avoids this.

**Evidence:** Phase 18 Wave 2 - attempted to spawn 3 agents in parallel (18-04, 18-05, 18-06). All 3 returned 429 error simultaneously. Limit reset after ~7 hours. Switched to sequential execution - all 3 plans completed successfully.

**How to Apply:**
- For phases with 1-2 plans: parallel execution is fine
- For phases with 3+ plans: execute sequentially OR spawn in smaller batches (2 at a time)
- Use `run_in_background: true` for long-running agents
- Monitor for 429 errors and switch to sequential if encountered

**Trade-offs:** Sequential is slower but more reliable. Parallel is faster but risks rate limits.
