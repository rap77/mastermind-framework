# CONCERNS.md - Technical Debt & Concerns

**MasterMind Framework** - Known issues, technical debt, areas for improvement

## High Priority Concerns

### 1. NotebookLM Integration Fragility

**Issue:** MCP dependency on external `nlm` CLI tool and Chrome profile

**Impact:** High - breaks core functionality if authentication fails

**Symptoms:**
- Timeout errors when MCP server unreachable
- Authentication failures on token expiry
- No graceful fallback to offline mode

**Mitigation:**
- Add timeout handling with exponential backoff
- Implement cached responses for common queries
- Consider alternative knowledge backends (ChromaDB, Qdrant)

**Status:** Partially mitigated (mock mode exists)

---

### 2. Sequential Brain Execution

**Issue:** Brains execute sequentially, not in parallel

**Impact:** Medium - slow performance for multi-brain flows

**Symptoms:**
- Full product flow (M1→M7) takes 5-10 minutes
- No parallelization of independent brains

**Mitigation:**
- Identify independent brains (e.g., M2 and M3 can run parallel)
- Use `asyncio` for concurrent MCP calls
- Add progress indicators for long flows

**Status:** Not started - architectural change required

---

### 3. Limited Error Recovery

**Issue:** Orchestrator fails on first brain error, no partial results

**Impact:** Medium - lost work when brain fails mid-flow

**Symptoms:**
- Brain #3 fails → entire orchestration fails
- No way to retry single brain
- No checkpoint/resume mechanism

**Mitigation:**
- Implement checkpoint system
- Allow brain-level retry (max 3)
- Save partial results for recovery

**Status:** `continue-plan` command exists, but not automatic

---

## Medium Priority Concerns

### 4. YAML Validation Incomplete

**Issue:** Source files have inconsistent YAML frontmatter

**Impact:** Medium - some sources fail to load

**Symptoms:**
- Missing required fields (version, last_updated)
- Incorrect syntax (quotes, lists)
- 122 sources need YAML updates (tracked in TECHNICAL-DEBT.md)

**Mitigation:**
- Add `mm source validate --fix` command
- Auto-fix common YAML errors
- Add pre-commit hook for YAML validation

**Status:** Manual fixes ongoing, automation planned

---

### 5. No Type Safety in MCP Integration

**Issue:** MCP calls return unstructured dicts, no type validation

**Impact:** Low-Medium - runtime errors from unexpected data

**Symptoms:**
- Key errors when accessing missing fields
- Type errors when MCP returns unexpected types
- No IDE autocomplete for MCP results

**Mitigation:**
- Create Pydantic models for MCP responses
- Add type validation wrapper
- Use TypedDict for partial safety

**Status:** Not started

---

### 6. Memory Management Unbounded

**Issue:** Interview logs grow indefinitely, no cleanup

**Impact:** Medium - disk space, performance degradation

**Symptoms:**
- `logs/interviews/` grows without limit
- Slow interview similarity searches
- No retention policy enforcement

**Mitigation:**
- Implement hot/warm/cold retention policy
- Auto-archive old interviews (> 30 days)
- Add `mm eval cleanup` command

**Status:** `scripts/cleanup_interviews.py` exists (manual)

---

### 7. Test Coverage Incomplete

**Issue:** Only ~40% code coverage, critical paths untested

**Impact:** Medium - regressions possible

**Missing tests:**
- Flow detector (0% coverage)
- Brain executor (0% coverage)
- Evaluator (0% coverage)
- MCP integration (no integration tests)

**Mitigation:**
- Add unit tests for flow detector
- Add integration tests for MCP
- Target 70% overall coverage

**Status:** In progress

---

## Low Priority Concerns

### 8. Hard-coded Nicho Logic

**Issue:** Nicho-specific code scattered throughout codebase

**Impact:** Low - hard to add new nichos

**Symptoms:**
- Marketing-specific logic in coordinator
- No abstraction for nicho differences
- 7 vs 16 brain numbers hard-coded

**Mitigation:**
- Create Nicho base class
- Use configuration-driven brain routing
- Generalize orchestrator for N nichos

**Status:** Not started (acceptable for 2 nichos)

---

### 9. No Metrics/Telemetry

**Issue:** No usage tracking, performance monitoring

**Impact:** Low - can't detect issues proactively

**Missing:**
- Query latency tracking
- Error rate monitoring
- Usage analytics

**Mitigation:**
- Add structured logging
- Export metrics to JSON
- Consider telemetry service (optional)

**Status:** Not started (privacy concern?)

---

### 10. Documentation Drift

**Issue:** Some docs outdated vs code reality

**Impact:** Low - confusion for contributors

**Examples:**
- STACK-TECNOLOGICO.md mentions old patterns
- CLI-REFERENCE.md incomplete
- HANDOFF.md references old commands

**Mitigation:**
- Add doc validation to CI
- Update docs with code changes
- Use `--help` output as source of truth

**Status:** Ongoing maintenance

---

## Known Bugs

### Bug #1: GGA Hook Timeout

**Issue:** Gentleman Guardian Angel hook takes > 30s on large commits

**Workaround:** Wait for hook to complete (never use `--no-verify`)

**Status:** External tool issue, no fix planned

---

### Bug #2: MCP Connection Leak

**Issue:** Long-running CLI sessions may leak MCP connections

**Symptoms:** Too many open files error after 100+ operations

**Workaround:** Restart CLI session

**Status:** Needs investigation

---

### Bug #3: YAML Quoting Inconsistencies

**Issue:** Some source files have inconsistent quote usage in YAML

**Example:** `title: Book Title` vs `title: "Book Title"`

**Fixed:** 3 files in PRP-MARKETING-003
**Remaining:** ~120 files in software-development niche

**Status:** Tracked in TECHNICAL-DEBT.md

---

## Security Concerns

### 1. NotebookLM Tokens in Files

**Risk:** Medium - tokens may be accidentally committed

**Mitigation:**
- `.gitignore` for token files
- Pre-commit hook to scan for secrets
- Use environment variables where possible

**Status:** `.gitignore` configured, no automated scanning yet

---

### 2. Unvalidated MCP Inputs

**Risk:** Low - MCP servers trusted, but no input validation

**Mitigation:**
- Add input sanitization for user briefs
- Validate MCP response structure
- Limit query length to prevent DoS

**Status:** Not started (acceptable risk for local CLI)

---

### 3. File Path Traversal

**Risk:** Low - user controls file paths, but no validation

**Mitigation:**
- Validate file paths are within project root
- Disallow `../` in source file paths
- Use `Path.resolve().is_relative_to(project_root)`

**Status:** Not started (acceptable for CLI tool)

---

## Performance Concerns

### 1. Large Source File Parsing

**Issue:** 500-line source files slow to parse

**Impact:** Noticeable delay on `mm source validate`

**Mitigation:**
- Cache parsed YAML in `__pycache__`
- Stream large files instead of full read
- Consider binary format for metadata

**Status:** Not started (acceptable for < 1000 sources)

---

### 2. NotebookLM Query Latency

**Issue:** Queries take 5-10 seconds per brain

**Impact:** Long wait times for multi-brain flows

**Mitigation:**
- Implement response caching
- Use streaming responses (show progress)
- Parallelize independent queries

**Status:** Response streaming implemented, caching planned

---

## Dependencies Outdated

| Package | Current | Latest | Risk |
|---------|---------|--------|------|
| `click` | 8.1.0 | 9.x | Low - breaking changes |
| `pydantic` | 2.0.0 | 2.10+ | Low - new features available |
| `rich` | 13.0.0 | 13.x | Low - compatible |

**Upgrade policy:** Upgrade on minor versions, evaluate major versions

---

## Areas for Future Improvement

### Short-term (Next Sprint)

1. ✅ Add E2E tests for marketing niche
2. ⏳ Improve YAML validation
3. ⏳ Add checkpoint/resume for long flows
4. ⏳ Implement interview cleanup automation

### Medium-term (Next Quarter)

1. Parallel brain execution where possible
2. Add type hints to MCP integration
3. Improve error messages with suggestions
4. Add metrics/logging for performance

### Long-term (Next 6 Months)

1. Alternative knowledge backends (ChromaDB)
2. Multi-language support (beyond English/Spanish)
3. Web UI for brief submission
4. Real-time collaboration features

---

## Debt Tracking

**TECHNICAL-DEBT.md** tracks:
- 122 sources needing YAML updates
- Outdated documentation files
- Refactoring opportunities

**Review cycle:** Monthly during planning

**Debt reduction goal:** Reduce by 50% in 3 months
