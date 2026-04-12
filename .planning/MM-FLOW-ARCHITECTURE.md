# MM-Flow v2: Workflow Architecture for MasterMind Platform

**Status:** READY FOR PHASE A IMPLEMENTATION
**Created:** 2026-04-12
**Last Updated:** 2026-04-12
**Phase A Start:** Monday, April 15, 2026

---

## Executive Summary

MM-Flow is a **platform-agnostic, multi-project workflow system** that combines:
- **GSD strengths:** State-as-filesystem, goal-backward verification, manager orchestration (REMOVED — replaced by PostgreSQL)
- **Paperclip patterns:** Decoupled API, React Query, minimal context
- **OpenClaw routing:** Binding-based dispatch, plugin architecture
- **MasterMind additions:**
  - Brain expert consultation per phase
  - Cross-phase contracts
  - Automated verification gates
  - **Multi-tenant PostgreSQL** (org/project/workspace isolation)
  - **Smart multi-backend scheduler** (Claude → OpenRouter → z.ai auto-switcheo)

**Purpose:** Enable robust, brain-aware development for multiple projects (MasterMind, Paperclip-clone v3.0, and 2+ future projects) with explicit state tracking, expert routing, verification, and intelligent token management across 3 LLM backends.

---

## Multi-Tenant Architecture

**Projects using same PostgreSQL:**
- `mastermind` (current)
- `prosell-sass` (Paperclip-clone v3.0)
- `project-3` (ideas)
- `project-4` (ideas)

**Database isolation:**
- Each row has `organization_id + project_id + workspace_id`
- PostgreSQL RLS (Row-Level Security) enforces isolation at DB level
- Queries always filtered by: `WHERE organization_id = ? AND project_id = ?`
- **Cross-project data leakage: impossible**

**CLI context management:**
```bash
$ mm-flow context set --org acme-corp --project mastermind
$ mm-flow execute-phase 19
# Uses organization_id + project_id from ~/.mm-flow/.context.json
```

---

## 4 Pillars of MM-Flow

### Pillar 1: Temporal State (PostgreSQL + improved)

**Files:**
- `.planning/STATE.md` — Structured YAML schema (not freeform narrative)
- `.planning/BRAIN-OUTPUTS.md` — Cross-phase decisions and contracts
- `.planning/BRAIN-FEED.md` — Learnings captured by brains during execution
- Git commit hooks auto-update STATE.md on phase transitions

**Schema (STATE.md):**
```yaml
---
milestone: v3.0
current_phase: 19
status: PLANNING_READY  # DISCUSSION_DONE, PLANNING_READY, EXECUTION_WAVE_1, VERIFICATION_READY, COMPLETE

last_action:
  actor: "Brain #1 (Product)"
  what: "Approved Phase 19 strategy"
  timestamp: 2026-04-12T14:30:00Z
  next_step: "Planning phase (Brain #8-14 consultation)"

phase_status:
  18: COMPLETE
  19: PLANNING_READY
  20: BLOCKED_ON_19

execution_waves:
  wave_1: { status: DONE, completed_at: 2026-04-12T10:00:00Z }
  wave_2: { status: IN_PROGRESS, tasks_done: 18, tasks_total: 20 }
  wave_3: { status: PENDING }

blockers: []  # Auto-filled by verification gates
---
```

**Persistence Layer:**
- **PostgreSQL** (primary): STATE.md saved as JSON in `mm_flow_state.state_data`
- Git hooks: `post-commit` updates PostgreSQL (not filesystem)
- State machine: Detects transitions via DB queries
- **Fallback:** PostgreSQL backups + RLS isolation = safer than filesystem

**Multi-Backend Token Tracking:**
```sql
CREATE TABLE backend_capabilities (
  backend VARCHAR,           -- 'claude', 'openrouter', 'z_ai'
  token_limit INTEGER,       -- Discovered via testing
  cycles_per_day INTEGER,    -- claude:1, openrouter:1, z_ai:5+
  reset_times JSON,          -- z_ai resets 5 times/day (~every 4h48m)
  discovered_at TIMESTAMP
);

-- Example:
-- claude     | 100000  | 1 | ["00:00"]              | 2026-04-15
-- openrouter | 128000  | 1 | ["00:00"]              | 2026-04-15
-- z_ai       | 200000  | 5 | ["00:00","04:48",...] | 2026-04-15
```

**No manual updates; STATE is always DB truth + human-readable.**

---

### Pillar 2: Expert Routing (MasterMind new)

**Brain Router (by phase + context):**

```python
MM_PHASE_MAP = {
  "DISCUSSION": [Brain#1, Brain#2, Brain#3, Brain#7],        # Product + UX + UI + Critic
  "PLANNING": [Brain#4, Brain#5, Brain#6, Brain#7],          # Frontend + Backend + QA + Critic
  "EXECUTION_WAVE": [Brain#7],                                # Critic validates wave
  "VERIFICATION": [Brain#7 + automated_checks],               # Critic says yes/no

  # Marketing brains (Phase 19+)
  "MARKETING_DISCUSSION": [Brain#8, Brain#9, Brain#10, Brain#7],  # Persona + Copy + CTR + Critic
  "MARKETING_PLANNING": [Brain#11-14, Brain#7],               # Campaign + Channels + Budget + Critic
}
```

**Flow:**
1. Phase starts → orchestrator checks config for required brains
2. Brain router spawns consultations **in parallel** (not sequential)
3. Each brain returns analysis (decision, recommendation, confidence)
4. Orchestrator synthesizes → BRAIN-OUTPUTS.md
5. Brain #7 (Evaluator) decides: **APPROVED** (confidence > 80%) or **ITERATE** (max 1 retry)

**Integration:**
- Brain consultation is **non-blocking** for phases < VERIFICATION
- VERIFICATION phase **blocks** until Brain #7 approves or escalates to user

---

### Pillar 3: Verification Gates (GSD goal-backward + new)

**Pre-Execution Contracts:**

Before executing a phase, validate **what must be true** (from dependent phases):

```yaml
# .planning/phases/19-marketing-foundation/CONTRACTS.yaml
depends_on:
  - phase: 18
    contracts:
      - "MultiChannelEvent must include .platform field"
      - "WebSocket API v2.0 endpoint must exist and be tested"
      - "Cross-channel session isolation must be enforced"
```

**Automated Checks (per phase):**
```python
VERIFICATION_CHECKLIST = {
  "spec_coverage": lambda spec, impl: coverage(spec, impl) > 95%,
  "tests_passing": lambda: run_tests() == "PASS",
  "security_clear": lambda: security_scan() == "CLEAR",
  "contracts_met": lambda: all_dependent_contracts_validated(),
  "brain_7_approval": lambda: brain_7.approve() == True,
}
```

**Execution:**
- **Post-wave verification:** Before Wave 2 starts, validate Wave 1 against checklist
- **Post-phase verification:** Before declaring phase COMPLETE, validate goal achievement
- **Cross-phase validation:** If Phase 19 depends on Phase 18 output, verify contracts before Phase 19 planning

**Escalation:**
- If check fails: automatic **1 retry** (fix + re-run check)
- If still fails: **escalate to user** (manual review required)
- Document failure in STATE.md `blockers` field

---

### Pillar 4: Audit Trail & Governance (NEW)

**Purpose:** Capture and persist complete development history for governance, compliance, and continuous improvement.

**What we track:**
- **Phase Executions:** Every phase run with duration, tokens, backend, output, git commit
- **Decisions:** All technical/product/process decisions with rationale, alternatives, confidence, impact
- **Verification Gates:** Brain #7 quality gates (tests, security, performance, contracts) with results
- **Artifacts:** Generated plans, specs, tests, docs with file paths and git links
- **Dev Sessions:** Development sessions with task completion, commits, discoveries, blockers
- **Phase Metrics:** Niche-specific KPIs (software: test coverage, uptime; SaaS: deployment rate; hardware: yield)
- **Audit Log:** Immutable log of all actions (for compliance)
- **Brain Feedback:** Insights, risk flags, opportunities from brain agents (synced from Engram)

**Database Schema (docker/postgres/mm-flow-audit.sql):**
- 8 audit tables (phase_executions, decisions, dev_sessions, verification_gates, artifacts, phase_metrics, audit_log, brain_feedback)
- 1 config table (niche_metrics_config — extensible per niche)
- 2 views (phase_execution_timeline, session_summary)
- All tables have RLS policies for org/project isolation

**API Endpoints (apps/api/routers/audit.py):**
- `GET /api/audit/projects/{project_id}/timeline` — Full development timeline
- `GET /api/audit/projects/{project_id}/phase/{phase_num}/details` — Phase details with decisions, gates, artifacts
- `POST /api/audit/projects/{project_id}/phase/{phase_num}/decision` — Record decision
- `GET /api/audit/projects/{project_id}/decisions` — List decisions with filtering
- `GET /api/audit/projects/{project_id}/phase/{phase_num}/gates` — Verification gates
- `GET /api/audit/projects/{project_id}/sessions` — Development sessions
- `GET /api/audit/projects/{project_id}/metrics` — Phase metrics by niche
- `GET /api/audit/projects/{project_id}/artifacts` — Track plans, specs, tests, docs
- `GET /api/audit/projects/{project_id}/audit-log` — Immutable audit trail (compliance)
- `GET /api/audit/projects/{project_id}/summary` — Executive summary (health, progress)
- `GET /api/audit/projects/{project_id}/brain-feedback` — Brain insights and feedback

**Engram ↔ PostgreSQL Sync (apps/api/services/engram_sync.py):**
- EngramSyncService: Query Engram for decisions (type=decision) and brain feedback, upsert to PostgreSQL
- PhaseExecutionRecorder: Record phase execution at completion with metadata
- Automatic linkage: decisions linked to phase_executions by timestamp + phase_number
- Handles missing/partial data gracefully
- Reference tracking: engram_link field connects DB records to Engram observations

**Integration with State Machine:**
- `record_phase_execution()` called after phase completion
- Captures backend, tokens, git commit, output summary
- Returns phase_execution_id for linking decisions/gates
- Audit log entries auto-created for all phase transitions

**Niche-Specific Metrics:**
- **Software:** test_coverage (%), code_review_time (hours), cyclomatic_complexity (score), security_vulnerabilities (count)
- **SaaS:** deployment_success_rate (%), uptime (%), mrr_impact ($)
- **Hardware:** manufacturing_yield (%), defect_rate (ppm), time_to_production (weeks)
- Extensible: add new niches via niche_metrics_config table

**Example: Phase 18 Execution Flow**

```
Phase 18 starts:
  ├─ state_machine.record_phase_execution(
  │    phase=18, status='in_progress', backend='claude'
  │  )
  │  └─ Creates phase_executions row, audit_log entry
  │
Phase 18 executes:
  ├─ Brain #1 makes product decision
  │  └─ Decision recorded: decision_type='product', title='Async messaging strategy'
  │
  ├─ Brain #7 evaluates output
  │  └─ Verification gate recorded: gate_type='brain_7_approval', status='passed'
  │
  ├─ Tests run: 95% coverage (recorded as phase_metric)
  ├─ Security scan: 0 vulnerabilities (recorded as verification_gate)
  ├─ Plans generated (recorded as artifact: plan_spec.md)
  │
Phase 18 completes:
  ├─ state_machine.record_phase_execution(
  │    phase=18, status='completed',
  │    backend='claude', tokens_consumed=45000,
  │    git_commit_hash='abc123...',
  │    output_summary='Phase 18 Wave 3 complete'
  │  )
  │  └─ Updates phase_executions, creates audit_log entry
  │
End of session:
  ├─ engram_sync.sync_decisions_to_db(org_id, project_id, phase=18)
  │  └─ Queries Engram for decisions made during Phase 18
  │  └─ Links each decision to phase_execution_id
  │  └─ Upserts into decisions table with engram_link reference
  │
Timeline view now shows:
  - Phase 18 started (09:00)
  - Product decision: 'Async messaging strategy' (10:15, confidence: 85%)
  - Verification gate: 'brain_7_approval' passed (11:30)
  - Phase 18 completed (14:00, 45K tokens, commit abc123)
```

**Compliance & Audit:**
- Immutable audit_log table (no updates, only appends)
- All actions tracked with actor, timestamp, entity links
- Useful for: audits, root cause analysis, compliance reporting
- Time series: query timeline view for phase-over-phase trends

**Cross-Session Wisdom (Engram ↔ PostgreSQL):**
1. Brain makes decision during phase → stored in Engram via mem_save()
2. Phase completes → engram_sync queries Engram for decisions
3. Decisions upserted to PostgreSQL with engram_link tracking
4. Next session: Brain can query both systems for complete context

---

## Pillar 5: Smart Multi-Backend Manager (NEW)

**Problem:** Claude exhausts in 2h, manually switching to OpenRouter/z.ai loses context and is error-prone.

**Solution:** Automatic backend selection based on **"most available credits RIGHT NOW"** + intelligent fallback.

### Backend Priorities & Reset Cycles

```python
BACKENDS = {
    "claude": {
        "token_limit": 100_000,
        "priority": 1,
        "cycles_per_day": 1,
        "reset_time": "00:00 UTC"
    },
    "openrouter": {
        "token_limit": 128_000,
        "priority": 2,
        "cycles_per_day": 1,
        "reset_time": "00:00 UTC"
    },
    "z_ai": {
        "token_limit": 200_000,
        "priority": 3,           # Fallback, but BEST capacity
        "cycles_per_day": 5,     # MULTIPLE resets = THE ADVANTAGE
        "reset_times": ["00:00", "04:48", "09:36", "14:24", "19:12"]  # Every ~4h48m
    }
}
```

### Auto-Switcheo Flow

```
Phase 19 Wave 1 (2h in, on Claude):
  ├─ Token monitor: Claude at 95% (95,000 / 100,000) ⚠️
  ├─ Query all backends:
  │  ├─ Claude: 5,000 tokens left ❌ (depleted)
  │  ├─ OpenRouter: 80,000 tokens left ✅ (good)
  │  └─ z.ai: 190,000 tokens left ✅ (BEST!)
  │
  ├─ Decision: "z.ai has most credits available"
  │
  ├─ Action: Switch to z.ai
  │  ├─ Save mm_flow_state to PostgreSQL
  │  ├─ Save context checkpoint to PostgreSQL
  │  ├─ Close Claude session
  │  └─ Resume on z.ai (NO WAIT TIME!)
  │
  └─ Result: Phase 19 Wave 1 completes on z.ai seamlessly
```

### If All Backends Depleted

```
All backends at 90%+ capacity:
  ├─ Query reset times:
  │  ├─ Claude resets tomorrow 00:00 (24h wait)
  │  ├─ OpenRouter resets tomorrow 00:00 (24h wait)
  │  └─ z.ai resets in 4.8 hours! ✅ (SOONEST)
  │
  ├─ Auto-pause execution
  ├─ Wait for z.ai reset (4.8h << 24h wait)
  ├─ Resume automatically when credits available
  │
  └─ User impact: Pause for ~5 hours, not 24 hours
```

### Fallback Strategy

**Preference order:**
1. **Claude** (preferred, lowest latency)
2. **OpenRouter** (if Claude depleted)
3. **z.ai** (fallback, but highest capacity)
4. **Wait for reset** (if all depleted, soonest reset)

**Multi-Project Isolation:**
- Project A's tokens tracked independently from Project B
- Each project has its own `backend_sessions` table entries
- Token limits discovered per-backend (global, shared discovery)

---

## File Structure

```
.planning/
├── STATE.md                              # Structured state (auto-updated)
├── ROADMAP.md                            # Phase definitions (GSD pattern)
├── REQUIREMENTS.md                       # Traceability matrix
├── MM-FLOW-ARCHITECTURE.md               # THIS FILE
├── BRAIN-OUTPUTS.md                      # Cross-phase brain decisions
├── BRAIN-FEED.md                         # Learnings captured by brains
├── config.yml                            # Brain routing rules + verify gates
│
├── phases/
│   ├── 18-multi-channel-gateway/
│   │   ├── CONTEXT.md                    # Brain #1-3 discussion output
│   │   ├── PLAN.md                       # Brain #4-6 planning output
│   │   ├── BRAIN-OUTPUTS.md              # Decisions affecting Phase 19
│   │   ├── CONTRACTS.yaml                # Pre-exec contracts for Phase 19
│   │   ├── SUMMARY.md                    # Execution proof
│   │   ├── BRAIN-FEED.md                 # Learnings from Phase 18
│   │   └── VERIFICATION.md               # Goal achievement proof
│   │
│   └── 19-marketing-foundation/
│       ├── CONTEXT.md
│       ├── PLAN.md
│       ├── CONTRACTS.yaml
│       └── ...
│
├── .mm-flow/
│   ├── brain-router.py                   # Auto-dispatch to brains
│   ├── verification-gates.py              # Auto-verify goals
│   ├── state-machine.py                  # Phase transition detection + audit trail
│   ├── token_limiter.py                  # Token tracking
│   ├── multi_backend_manager.py           # Backend selection
│   └── config.py                         # Config: NICHE_METRICS, etc.
│
└── docker/postgres/
    ├── mm-flow-schema.sql                # Multi-tenant state machine schema
    └── mm-flow-audit.sql                 # Audit trail schema (NEW)

apps/api/
├── routers/
│   └── audit.py                          # REST endpoints for timeline, metrics, gates (NEW)
│
└── services/
    └── engram_sync.py                    # Engram ↔ PostgreSQL sync (NEW)
```

---

## Brain Consultation Flow (Concrete Example)

### Phase 19: Marketing Foundation — DISCUSSION

```
User: "/mm:discuss-phase 19"
    ↓
MM-Flow reads config.yml → DISCUSSION requires [Brain#8, Brain#9, Brain#10, Brain#7]
    ↓
Brain router spawns 4 parallel consultations:

  Brain #8 (Persona):
    Input: "Phase 19 goal, requirements, Phase 18 context"
    Output: "Target persona analysis, channel fit, messaging hooks"
    Confidence: 85%

  Brain #9 (Copy):
    Input: "Phase 19 goal, target persona"
    Output: "Copy direction, tone, key messages"
    Confidence: 78%

  Brain #10 (CTR Optimization):
    Input: "Phase 19 goal, copy drafts"
    Output: "A/B testing strategy, metrics to track"
    Confidence: 90%

  Brain #7 (Evaluator):
    Input: "All 3 outputs, Phase 18 contracts"
    Output: "Feasibility assessment, risk flags"
    Confidence: 92%
    Decision: ✅ APPROVED (3/3 high-confidence + no risks)
    ↓
BRAIN-OUTPUTS.md generated:
  - Persona: "B2B DevOps Manager, AWS-heavy, values time-saving"
  - Copy direction: "Focus on automation ROI, not features"
  - A/B tests: "CTA A: 'Try Free' vs CTA B: 'See Demo'"
  - Risks: "None identified"
    ↓
STATE.md auto-updates:
  current_phase: 19
  status: PLANNING_READY
  last_action: "Brain #7 approved Phase 19 discussion"
```

---

## CEO Agent Decision

**Approach:** Brain #1 (Product Strategy) + CEO-Consultant prompt

During DISCUSSION phase, orchestrator adds a CEO-style questioning layer:

```python
CEO_CONSULTANT_PROMPT = """
You are the CEO Consultant for Phase {phase}.

Before Brain #1 finalizes the strategy, ask:
1. "Who cares about this? Why them? What's their pain?"
2. "What's the ROI? How do we measure success?"
3. "Can we simplify or pivot?"
4. "Do we scale with this? Will it break in v3.1?"
5. "What's the biggest risk if we get this wrong?"

Your analysis feeds into Brain #1. Brain #7 makes the final call.
"""
```

**Why not a separate CEO agent?**
- Brain #1 already has product strategy expertise
- CEO role is about asking hard questions, not additional domain knowledge
- Reduces agent overhead while preserving decision quality
- Scales easily (same prompt works for all phases)

**Upgrade path:** If CEO needs autonomy (sign decisions independently), create CEO agent in Phase 20+.

---

## Phase A: Scaffolding (Apr 15-18, ~4 days)

### Day 1: Multi-Tenant Database + Audit Trail Schema

- [ ] Create PostgreSQL schema (multi-tenant)
  - [x] `organizations` table
  - [x] `projects` table
  - [x] `workspaces` table
  - [x] `mm_flow_state` table (multi-tenant)
  - [x] `backend_sessions` table (per-project tracking)
  - [x] `backend_capabilities` table (discovered limits)
  - [x] `context_checkpoints` table
  - [x] RLS policies (isolation enforcement)

- [ ] Create Audit Trail schema (docker/postgres/mm-flow-audit.sql) — DONE
  - [x] `phase_executions` — track each phase run
  - [x] `decisions` — capture decisions with rationale, alternatives, confidence
  - [x] `dev_sessions` — log development sessions with tasks, commits, discoveries
  - [x] `verification_gates` — Brain #7 quality gates (test, security, performance)
  - [x] `artifacts` — generated files (plans, specs, tests, docs) with git link
  - [x] `phase_metrics` — niche-specific KPIs
  - [x] `audit_log` — immutable compliance log
  - [x] `brain_feedback` — Engram sync target for brain decisions
  - [x] `niche_metrics_config` — define metrics per niche (software, saas, hardware)
  - [x] Views: phase_execution_timeline, session_summary
  - [x] RLS policies for org isolation

- [ ] Generalize credentials (`.claude/backends.sh`)
  - [ ] Support Claude, OpenRouter, z.ai
  - [ ] Load from settings.local.json or env vars
  - [ ] Verify API keys work

**Deliverable:** PostgreSQL schemas ready (state + audit), credentials configured

### Day 2-3: MM-Flow Core + Audit Integration

- [x] `.mm-flow/` directory (exists)
  - [x] `multi_backend_manager.py` (smart backend selection)
  - [x] `backend_scheduler.py` (reset cycle detection)
  - [x] `token_limiter.py` (token discovery + tracking)
  - [x] `state_machine.py` (phase transition detection) — UPDATED with record_phase_execution()
  - [x] `brain_router.py` (parallel brain consultation)
  - [x] `verification_gates.py` (automated checks + Brain #7)

- [ ] Create Audit API (apps/api/routers/audit.py) — DONE
  - [x] `GET /api/audit/projects/{project_id}/timeline` — full timeline
  - [x] `GET /api/audit/projects/{project_id}/phase/{phase_num}/details` — phase details
  - [x] `POST /api/audit/projects/{project_id}/phase/{phase_num}/decision` — record decision
  - [x] `GET /api/audit/projects/{project_id}/decisions` — list decisions
  - [x] `GET /api/audit/projects/{project_id}/phase/{phase_num}/gates` — gates
  - [x] `GET /api/audit/projects/{project_id}/sessions` — sessions
  - [x] `GET /api/audit/projects/{project_id}/metrics` — metrics
  - [x] `GET /api/audit/projects/{project_id}/artifacts` — artifacts
  - [x] `GET /api/audit/projects/{project_id}/audit-log` — compliance log
  - [x] `GET /api/audit/projects/{project_id}/summary` — executive summary
  - [x] `GET /api/audit/projects/{project_id}/brain-feedback` — brain insights

- [ ] Create Engram Sync Service (apps/api/services/engram_sync.py) — DONE
  - [x] EngramSyncService — sync decisions from Engram to PostgreSQL
  - [x] PhaseExecutionRecorder — record phase execution to audit trail
  - [x] Brain feedback syncing
  - [x] Timestamp-based linkage to phase_executions

- [ ] Implement hooks
  - [ ] `mm-flow-context-monitor.js` (detects backend depletion)
  - [ ] `mm-flow-session-init.js` (loads from PostgreSQL on start)
  - [ ] `mm-flow-statusline.js` (shows current backend + tokens)

- [ ] Update settings.json
  - [ ] Remove GSD hooks
  - [ ] Add MM-Flow hooks
  - [ ] Backend configuration

**Deliverable:** MM-Flow core modules, hooks integrated

### Day 4: CLI + Testing

- [ ] Create CLI commands
  - [ ] `mm-flow init` (create org/project/workspace)
  - [ ] `mm-flow context set` (switch project context)
  - [ ] `mm-flow context show`
  - [ ] `mm-flow execute-phase` (uses current context)

- [ ] Test multi-tenant isolation
  - [ ] Project A cannot see Project B data
  - [ ] Backend tokens tracked per-project
  - [ ] RLS enforces org/project filtering

- [ ] Documentation
  - [ ] Update MM-FLOW-ARCHITECTURE.md (already done ✅)
  - [ ] Create SETUP.md (local dev setup)
  - [ ] Create CLI-REFERENCE.md

**Deliverable:** MM-Flow v1 ready to pilot, multi-project support, 3 backends integrated

**Output:**
- Multi-tenant PostgreSQL (mastermind + prosell-sass + future projects)
- Smart backend manager (Claude → OpenRouter → z.ai auto-switcheo)
- CLI context management
- Hooks for auto-checkpoint/resume
- Ready for Phase 18 Wave 3 piloting

**Timeline:** Monday Apr 15 - Thursday Apr 18 (4 days, parallel workstreams)

---

### FASE B: Piloting on Phase 18 (2 weeks)

**Goal:** Validate MM-Flow on real milestone execution

- **Week 1 (Apr 22-26):**
  - Integrate MM-Flow into Phase 18 Wave 3 execution
  - Run brain router during verification (read-only)
  - Capture Brain feedback in BRAIN-FEED.md
  - Monitor STATE.md auto-updates
  - Document friction points

- **Week 2 (Apr 29 - May 3):**
  - Iterate based on feedback
  - Fix STATE.md schema gaps
  - Harden verification gates
  - Finalize Phase 18 with MM-Flow
  - Commit: `feat(mm-flow): Phase 18 complete with MM-Flow v2`

**Output:**
- Phase 18 COMPLETE using MM-Flow
- MM-Flow v2 validated in production
- Learnings documented for Phase 19 scaling

**Timeline:** 2 weeks

---

### FASE C: Scale to Marketing (2-3 weeks, post v3.0)

**Goal:** Prove MM-Flow scales across niches

- **Week 1:**
  - Agentify marketing brains (8-23)
  - Extend brain router for MARKETING phases
  - Create marketing phase map in `config.yml`

- **Week 2:**
  - Execute Phase 19 (Marketing Foundation) with full MM-Flow + marketing brains
  - DISCUSSION → PLANNING → EXECUTION → VERIFICATION with all 3 pillars
  - Document learnings

- **Week 3:**
  - Finalize documentation for OSS
  - Create video walkthrough
  - GitHub discussion template for community feedback

**Output:**
- MM-Flow proven at scale (dev + marketing brains)
- Ready for open-source release
- Template for future nichos

**Timeline:** 2-3 weeks

---

## FAQ

**Q: What if a brain's recommendation conflicts with another?**
A: Brain #7 (Evaluator) mediates. Documents conflict in BRAIN-OUTPUTS.md, proposes resolution, escalates to user if unresolvable.

**Q: What if Phase N's output doesn't meet Phase N+1's contracts?**
A: Verification gate catches it before Phase N+1 planning. Phase N loops (max 1 retry) or escalates.

**Q: Does MM-Flow work for non-software nichos?**
A: Yes. Swap brain set (Phase 19 uses brains 8-23 for marketing instead of 4-6 for backend). Same flow, different expertise.

**Q: How does MM-Flow coexist with GSD?**
A: MM-Flow is a **replacement workflow** for MasterMind. GSD can stay as reference documentation or be archived. See "Transition Plan" below.

**Q: How much overhead does brain routing add?**
A: ~5-10 min per phase (parallel brain consultations). Recovers time lost to verification gaps and rework.

---

## Memory Systems: Roles & Responsibilities

**Three systems work together, each with specific role:**

| System | What It Stores | When Used | Purpose | Example |
|--------|---|---|---|---|
| **PostgreSQL** | MM-Flow execution state | Within-session | "Where are we in the phase?" | "Phase 19 Wave 2 complete, checkpoint saved" |
| **Engram** | Learnings & decisions | Cross-session wisdom | "What did we learn that matters?" | "Session 1: discovered Zustand > Redux. Session 2: Brain #3 uses that knowledge" |
| **Serena** | NOTHING (DISABLED) | ❌ | ❌ | ❌ |

### PostgreSQL: Workflow State

**Saves automatically on:**
- Phase completion
- Wave completion
- Backend switcheo
- Context checkpoint

**Loaded automatically on:**
- Session start (via `mm-flow-session-init.js` hook)
- `/mm:execute-phase --resume`
- Multi-backend recovery

### Engram: Cross-Session Learnings

**Save ONLY these:**
```python
# ✅ SAVE (Cross-session wisdom)
mem_save(title="Zustand > Redux decision", type="decision", ...)
mem_save(title="JWT Next 16 fix", type="bugfix", ...)
mem_save(title="Compound components pattern", type="pattern", ...)

# ❌ DON'T SAVE (That's PostgreSQL's job)
mem_save("Session checkpoint")  # Use /gsd:pause-work instead
mem_save("Phase 19 current status")  # That's DB state
```

**Query across sessions:**
```bash
# Session 1: Fixed JWT issue
mem_save(title="JWT Next 16 fixed", type="bugfix", ...)

# Session 2 (next day): Starting Phase 20
mem_search(query="JWT")  # Finds: "Fixed JWT verification"
# Brain #3 avoids same mistake, applies lesson immediately
```

---

## Transition Plan

### Current State
- **GSD workflow:** Removed ✅ (replaced by MM-Flow + PostgreSQL)
- **Serena memory:** Disabled ✅ (150+ memories archived)
- **MasterMind phases:** 13-18 executed with old GSD flow
- **Brain agents:** 7 dev brains + 16 marketing brains ready

### Target State (post MM-Flow Phase A)
- **MM-Flow workflow:** Primary (`.planning/.mm-flow/`)
- **PostgreSQL:** State persistence (shared multi-tenant DB)
- **Engram:** Cross-session learnings (what we learned that matters)
- **Brain agents:** Integrated into MM-Flow consultation pipeline
- **Multi-backend:** Claude → OpenRouter → z.ai auto-switcheo

### Phase A Implementation (Apr 15-18)
1. **Database:** Multi-tenant schema in PostgreSQL (already running in Docker)
2. **CLI:** Context management (`mm-flow context set`)
3. **Backend manager:** Smart selection (most available credits)
4. **Hooks:** Auto-checkpoint, auto-resume
5. **Test:** Verify isolation (Project A ≠ Project B data)

---

## Notes for Modification

- This is a **draft**. Edit freely.
- Sections marked `[EDIT ME]` need user input.
- Configuration files (`.mm-flow/config.yml`) will be created in Phase A.
- Brain consultation endpoints (API stubs) defined in Phase A.
- Implementation details (Python classes, git hook scripts) deferred to Phase A kick-off.

---

**Next:** User review + feedback → Phase A kick-off (Mon 15 April)
