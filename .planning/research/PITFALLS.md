# Pitfalls Research

**Domain:** Framework Refactoring (Sequential → Parallel + Type Safety + Web UI)
**Researched:** 2026-03-13
**Confidence:** MEDIUM (WebSearch unavailable, drawing from Python ecosystem knowledge + existing concerns)

## Critical Pitfalls

### Pitfall 1: False Parallelism — The Threading Trap

**What goes wrong:**
You add `asyncio` or threading to speed up brain execution, but Python's GIL and I/O-bound nature mean you see zero performance improvement. Or worse, performance degrades due to context switching overhead.

**Why it happens:**
- Brain execution is primarily I/O-bound (MCP calls to NotebookLM)
- Developers confuse CPU parallelism (multiprocessing) with I/O concurrency (asyncio)
- Threading in Python doesn't bypass the GIL for CPU-bound work
- `asyncio` requires *all* blocking operations to be async — mixing sync and async kills benefits

**How to avoid:**
1. **Profile before parallelizing** — Use `cProfile` to confirm I/O vs CPU bottleneck
2. **Use `asyncio` for I/O-bound** — MCP calls, network requests, file I/O
3. **Use `multiprocessing` only for CPU-bound** — Rare in this framework
4. **Make async all the way down** — MCP client must be async, not just wrapper
5. **Benchmark real workloads** — Test with actual multi-brain flows, not synthetic tests

**Warning signs:**
- Adding threads/async doesn't improve latency
- CPU usage at 100% on single core despite parallel code
- Context switching overhead visible in profiler (> 20% time in `switch`)

**Phase to address:**
Phase 1 (Parallel Execution Foundation) — Before writing any parallel code, must:
- Profile current sequential execution
- Identify I/O vs CPU boundaries
- Create performance baseline

**Recovery strategy:**
HIGH cost if wrong choice made. Requires rewriting orchestration layer:
- If threading used incorrectly → migrate to `asyncio`
- If `asyncio` used with sync MCP → rewrite MCP client to be async
- If multiprocessing used unnecessarily → remove complexity, use `asyncio`

---

### Pitfall 2: The Dependency Graph Blind Spot

**What goes wrong:**
You parallelize brains that appear independent but actually share state or have hidden dependencies. Race conditions cause non-deterministic failures — works in dev, fails in production.

**Why it happens:**
- Current sequential execution masks dependency violations
- Brains share `orchestrator.state` dict implicitly
- Brain #7 (Evaluator) assumes sequential execution order
- No explicit dependency declaration — dependencies are emergent from execution order

**How to avoid:**
1. **Explicit dependency declaration** — Each brain declares `dependencies: List[BrainID]`
2. **Dependency graph validation** — Topological sort before execution
3. **State isolation** — Each brain gets isolated input/output, no shared mutable state
4. **Deterministic execution** — Same inputs → same outputs, same execution order
5. **Parallelism only at leaf nodes** — Only brains with no dependencies run in parallel

**Warning signs:**
- Flaky tests that pass/fail randomly
- Different results on same input
- Failures that disappear when adding debug prints (Heisenbugs)
- Brain #7 rejects valid outputs intermittently

**Phase to address:**
Phase 1 (Parallel Execution Foundation) — Must implement:
- Dependency graph system
- State isolation layer
- Deterministic execution tests

**Recovery strategy:**
MEDIUM cost. Requires:
- Auditing all brain-to-brain communication
- Adding explicit dependency declarations
- Implementing state isolation
- Writing deterministic execution tests

---

### Pitfall 3: The Type Safety Half-Migration

**What goes wrong:**
You add type hints to core modules but leave MCP integration and brain system untyped. Or you use `mypy --strict` but sprinkle `# type: ignore` everywhere. Result: False confidence, runtime errors still happen.

**Why it happens:**
- `mypy` strict mode is aggressive — requires 100% coverage or massive `# type: ignore`
- MCP returns `dict[str, Any]` — hard to type without wrapper models
- Existing codebase has 40% coverage, 0% in critical paths
- Gradual typing requires discipline to maintain type boundary hygiene

**How to avoid:**
1. **Pydantic models at boundaries** — MCP responses, CLI inputs, brain outputs
2. **Accept `Any` at external boundaries, strict internally** — Type MCP responses immediately
3. **Enable `mypy` strict mode incrementally** — Start with `mypy strict` on new code only
4. **Create TypedDict for partial safety** — Better than `Any`, less work than Pydantic
5. **Set CI to fail on new `# type: ignore`** — Prevent accumulating technical debt

**Warning signs:**
- `# type: ignore` appears in code review
- `mypy` runs take > 30 seconds (indicates complexity)
- New code added without type hints
- Runtime type errors in supposedly type-safe code

**Phase to address:**
Phase 2 (Type Safety Foundation) — Must:
- Create Pydantic models for all data structures
- Type MCP integration layer (highest risk)
- Enable `mypy` strict on new code only
- Add `# type: ignore` gate in CI

**Recovery strategy:**
MEDIUM cost if partial migration. Requires:
- Removing `# type: ignore` annotations
- Adding proper Pydantic models
- Retyping untyped modules

---

### Pitfall 4: The Authentication State Schism

**What goes wrong:**
CLI uses local config file for auth, web UI uses session cookies. User authenticates in CLI, then opens web UI and has to authenticate again. Or worse — web UI can't access CLI's NotebookLM tokens.

**Why it happens:**
- CLI tools traditionally use `~/.config/` for auth state
- Web apps use browser cookies/session storage
- No unified auth layer designed
- NotebookLM MCP tokens stored in CLI config, not accessible to web backend

**How to avoid:**
1. **Unified auth service** — Both CLI and UI call same auth API
2. **Shared credential store** — Database or encrypted file, not CLI config
3. **CLI becomes UI client** — CLI authenticates via web backend, not locally
4. **Session tokens, not API keys** — Use short-lived JWTs, not long-lived API keys
5. **OAuth flow unification** — Both interfaces use same OAuth redirect handler

**Warning signs:**
- Users report "I logged in on CLI but web says unauthorized"
- Auth logic duplicated between CLI and UI code
- Token refresh logic exists in two places
- Different token lifetimes between interfaces

**Phase to address:**
Phase 3 (Web UI Foundation) — Must:
- Design unified auth service before UI implementation
- Refactor CLI to use shared auth (breaking change)
- Migrate existing auth tokens to shared store

**Recovery strategy:**
HIGH cost. Requires:
- Redesigning auth architecture
- Migrating user tokens (breaking change for existing users)
- Rewriting CLI auth flow
- Implementing token migration script

---

### Pitfall 5: The Multi-Orchestrator Race

**What goes wrong:**
Web UI allows multiple users to run orchestrations simultaneously. Two users run product strategy flows at the same time — Brain #7's evaluation gets mixed up, User A sees User B's results.

**Why it happens:**
- Current orchestrator uses global state (module-level variables)
- No request context or session isolation
- Brain #7's `current_task` is a singleton
- MCP client is shared across all requests
- No concurrency control on shared resources (NotebookLM rate limits)

**How to avoid:**
1. **Per-request orchestrator instances** — No global state
2. **Session-scoped execution context** — All state tied to session ID
3. **Database-backed orchestration** — Progress stored in DB, not memory
4. **MCP client pooling** — Connection pool with rate limiting
5. **Idempotent operations** — Retries don't create duplicate work

**Warning signs:**
- Integration tests fail when run in parallel
- User sees another user's results
- NotebookLM rate limit errors under load
- "Task not found" errors for valid task IDs

**Phase to address:**
Phase 3 (Web UI Foundation) — Before going multi-user:
- Audit all global state in orchestrator
- Implement session isolation
- Add multi-user integration tests

**Recovery strategy:**
HIGH cost. Requires:
- Refactoring orchestrator to be stateless
- Implementing session management
- Adding database for orchestration state
- Rewriting Brain #7 to handle concurrent evaluations

---

### Pitfall 6: The MCP Integration Bottleneck

**What goes wrong:**
Parallel execution sends 10 simultaneous requests to NotebookLM via MCP. MCP server rate-limits or crashes. Or worse — requests get interleaved, responses go to wrong brains.

**Why it happens:**
- MCP protocol designed for single-request flows
- No request/response correlation mechanism
- MCP server not designed for concurrent requests
- No backpressure handling in orchestrator

**How to avoid:**
1. **Semaphore limiting** — Max N concurrent MCP requests
2. **Request correlation IDs** — Track which response belongs to which request
3. **MCP connection pooling** — Separate connections per "session"
4. **Circuit breaker** — Stop sending requests if MCP fails repeatedly
5. **Response queue matching** — Match responses to requests via ID

**Warning signs:**
- MCP timeout errors increase with parallelism
- Brains receive wrong knowledge (misrouted responses)
- `nlm` process crashes under load
- Requests hang indefinitely

**Phase to address:**
Phase 1 (Parallel Execution Foundation) — Must:
- Benchmark MCP under concurrent load
- Implement semaphore limiting
- Add request correlation

**Recovery strategy:**
MEDIUM cost. Requires:
- Implementing MCP connection pooling
- Adding semaphore limiting
- Rewriting MCP client to handle concurrency

---

### Pitfall 7: The Backward Compatibility Breaking Point

**What goes wrong:**
v2.0 introduces type-safe Pydantic models for brain communication. Existing v1.x brains (23 brains across 2 niches) break because they return raw dicts, not Pydantic models. Users can't upgrade without rewriting all their brains.

**Why it happens:**
- No deprecation path designed
- Breaking changes introduced without migration guide
- Type safety enforced at boundary (all or nothing)
- No compatibility shim provided

**How to avoid:**
1. **Deprecation cycle** — Support old format for N versions, warn loudly
2. **Adapter pattern** — Convert v1 brains to v2 format automatically
3. **Feature flags** — Allow users to opt into v2 behavior
4. **Migration script** — Auto-convert existing brains to new format
5. **Separate v1/v2 execution paths** — Run old brains in compatibility mode

**Warning signs:**
- Existing brains fail after upgrade
- No migration path documented
- Users forced to rewrite brains immediately
- Breaking changes in minor/patch versions

**Phase to address:**
Phase 2 (Type Safety Foundation) — Must:
- Design compatibility layer before enforcing types
- Create brain format migration script
- Document deprecation timeline

**Recovery strategy:**
MEDIUM cost. Requires:
- Implementing compatibility shim
- Writing migration tooling
- Maintaining dual code paths (v1/v2)

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `# type: ignore` on MCP responses | Unblocks type migration | Hides real errors, false confidence | Only in Phase 1, must be tracked |
| Global state in orchestrator | Faster development, less code | Impossible multi-user support | CLI-only (v1.x), never in v2.0 |
| Sequential execution | Simple debugging, predictable | 5-10 min flows, can't scale | MVP only, Phase 0 target |
| Mixing sync/async in MCP | Works with existing MCP client | No performance benefit, complexity | Never — pure async required |
| CLI-only auth | Fast to implement | UI must re-implement, duplicate code | Acceptable for CLI-only v1.x |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| **NotebookLM MCP** | Treating as synchronous, blocking main thread | All MCP calls must be async, use asyncio |
| **Brain execution** | Assuming independent, running all in parallel | Build dependency graph, parallelize leaves only |
| **Type system** | Using `Any` at boundaries, no validation | Pydantic models at all boundaries, validate early |
| **Web UI backend** | Calling orchestrator directly (global state) | Per-request orchestrator instances, session-scoped |
| **Auth system** | Separate CLI/web auth implementations | Unified auth service, CLI uses web backend |
| **Multi-user sessions** | Storing state in memory (module vars) | Database-backed session state |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| **False parallelism** | No latency improvement, high CPU | Profile first, use asyncio for I/O | Immediately — measurable in Phase 1 |
| **GIL contention** | Single core at 100%, slow execution | Avoid threading for CPU work | At 5+ concurrent brain executions |
| **MCP bottleneck** | Timeouts increase with concurrency | Semaphore limiting (max 3-5 concurrent) | At 3+ simultaneous brain queries |
| **Memory leaks** | Growing memory, slow GC | Explicit cleanup, connection pooling | After 100+ orchestrations |
| **DB contention** | Slow queries, locks | Connection pooling, optimistic concurrency | At 10+ concurrent users |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| **Token leakage in logs** | NotebookLM tokens exposed to anyone with logs | Redact tokens from logs, use secret scanning |
| **Session hijacking** | User A accesses User B's orchestration results | Strict session ID validation, CSRF tokens |
| **Auth bypass in CLI** | CLI bypasses web auth, accesses everything | CLI must authenticate via web backend |
| **MCP injection** | Malicious brief injects commands into MCP | Sanitize all user inputs, validate schemas |
| **Rate limit abuse** | User floods system with orchestrations | Per-user rate limiting, quota enforcement |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| **Silent failures in parallel** | Brain fails but user sees "complete" | Aggregate all errors, show at end |
| **Unpredictable execution order** | Can't follow which brain is running | Visual progress shows topological order |
| **Lost context on errors** | User restarts from beginning | Checkpoint/resume from last success |
| **Type error gibberish** | `mypy` errors confuse non-technical users | Friendly error messages, show what to fix |
| **Auth friction CLI→Web** | Login twice, confusing session | Single sign-on, shared session state |

## "Looks Done But Isn't" Checklist

- [ ] **Parallel execution:** Often missing dependency validation — verify topological sort catches all violations
- [ ] **Type safety:** Often missing MCP integration typing — verify all MCP responses use Pydantic models
- [ ] **Web UI:** Often missing session isolation — verify two users can run flows simultaneously without cross-talk
- [ ] **Auth unification:** Often missing CLI→backend integration — verify CLI uses web backend for auth
- [ ] **Multi-user:** Often missing database-backed state — verify orchestrator state survives server restart
- [ ] **Error recovery:** Often missing checkpoint/resume — verify failed orchestrations can be continued
- [ ] **Performance:** Often missing concurrency benchmarking — verify parallel execution is actually faster
- [ ] **Backward compatibility:** Often missing brain format migration — verify v1 brains work in v2

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| **False parallelism** | HIGH | Rewrite orchestration layer with correct concurrency model (asyncio vs multiprocessing) |
| **Dependency graph blind spot** | MEDIUM | Add explicit dependency declarations, implement state isolation, write deterministic tests |
| **Type safety half-migration** | MEDIUM | Remove `# type: ignore`, add Pydantic models, retype untyped modules |
| **Auth state schism** | HIGH | Redesign auth architecture, migrate tokens, rewrite CLI auth flow |
| **Multi-orchestrator race** | HIGH | Refactor to stateless, add session management, implement DB backing |
| **MCP bottleneck** | MEDIUM | Implement connection pooling, semaphore limiting, request correlation |
| **Backward compatibility break** | MEDIUM | Implement compatibility shim, write migration tooling, maintain dual paths |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| False parallelism | Phase 1 — Profile before implementing | Benchmark shows >2x improvement |
| Dependency graph blind spot | Phase 1 — Dependency graph system | Tests pass with all dependency permutations |
| Type safety half-migration | Phase 2 — Pydantic at boundaries | `mypy strict` passes, zero `# type: ignore` |
| Auth state schism | Phase 3 — Unified auth service | CLI and UI use same session |
| Multi-orchestrator race | Phase 3 — Session isolation | Multi-user integration tests pass |
| MCP bottleneck | Phase 1 — Semaphore limiting | No MCP errors under concurrent load |
| Backward compatibility break | Phase 2 — Migration tooling | v1 brains run without modification |

## Sources

**Note:** WebSearch was unavailable during research (quota limit reached). Findings are based on:
- Python ecosystem knowledge (asyncio, threading, GIL behavior)
- Existing concerns in CONCERNS.md (sequential execution, type safety, multi-user gaps)
- Common refactoring patterns (sequential→parallel, dynamic→static typing)
- Framework architecture principles (dependency injection, state isolation)

**Confidence level:** MEDIUM — Recommendations are grounded in established Python best practices but lack recent 2026-specific validation. Consider verification through:
- Python asyncio documentation (official)
- mypy type system documentation (official)
- FastAPI/FastStream multi-pattern examples (real-world parallel systems)
- Post-mortems of projects that attempted similar migrations (search required when WebSearch available)

**Recommended follow-up research:**
1. Search for "Python sequential to parallel refactoring war stories 2025 2026"
2. Search for "mypy strict migration large codebase experiences"
3. Search for "FastAPI multi-user session isolation patterns"
4. Search for "MCP (Model Context Protocol) concurrent request handling"

---
*Pitfalls research for: MasterMind Framework v2.0*
*Researched: 2026-03-13*
