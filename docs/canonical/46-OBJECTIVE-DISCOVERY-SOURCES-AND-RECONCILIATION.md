# 46. Objective Discovery Sources and Reconciliation

## Purpose

This document defines how `/mm:discover --roadmap --existing` should derive the MVP objective roadmap for an existing project.

The key principle is:

> the roadmap must not come only from code scanning, and it must not come only from stale planning documents.

It must be produced by reconciling:

1. **declared intent**
2. **active planning state**
3. **decision history**
4. **actual implementation state**

---

## High-Level Rule

The discovery pipeline should treat **intent** and **reality** as separate inputs.

- **Intent** tells us what the project is trying to become.
- **Reality** tells us what has already been implemented, partially implemented, abandoned, or left inconsistent.

The roadmap is the result of reconciling both.

---

## Source Priority

### Tier 1 — Explicit Intent Sources (highest trust)

These sources define what the project says it wants to be.

Examples:
- `PROJECT.md`
- `README.md`
- `docs/PRD/**`
- `docs/canonical/**`
- `.planning/SOURCE-OF-TRUTH.md`
- current handoff files
- active objective specs

These should be treated as the strongest signals for objective discovery.

### Tier 2 — Planning State Sources (medium-high trust)

These sources define what work is already structured.

Examples:
- `.planning/changes/**`
- `.planning/archive/**`
- `.planning/HANDOFF-*`
- `.planning/task-progress.json`

These help determine:
- what is active
- what is blocked
- what was completed
- what was partially completed

### Tier 3 — Decision Sources (medium trust)

These sources define obligations implied by earlier decisions.

Examples:
- `docs/canonical/decision-records/**`
- ADR-like docs
- meta-brain recommendations already accepted

These are especially important when a design decision introduced required follow-up work that has not yet been completed.

### Tier 4 — Codebase Reality Sources (validation / gap detection)

These sources define what the codebase actually contains.

Examples:
- backend modules
- frontend routes/pages/components
- tests
- migrations
- websocket/events contracts
- generated schemas
- service boundaries

These should be used to:
- validate whether declared objectives are real or stale
- detect partially implemented objectives
- discover technical gaps that are necessary for MVP completion

### Rule

Tier 4 must **not** be the only source of objective generation.

---

## Objective Discovery Pipeline

## Step 1 — Collect candidate objectives from explicit intent

Extract candidate objectives from the highest-trust sources.

Examples:
- `project-state-mvp`
- `project-state-realtime`
- `window-scheduler`
- `engineering-doctrine-layer`
- `collaboration-rbac`

Each candidate should carry metadata:
- `source`
- `source_path`
- `confidence`
- `description`
- `mvp_relevance`

---

## Step 2 — Collect candidates from planning state

Use planning artifacts to determine whether a candidate objective is:
- already active
- already completed
- partially complete
- stale
- duplicated

This step helps distinguish roadmap ideas from already-managed workstreams.

---

## Step 3 — Collect implied objectives from decision history

Some objectives are not written as roadmap items, but are required by accepted decisions.

Example:
- decision says “backend is authority for model access”
- implied objective might be `agent-service-boundary-hardening`

These should be captured as derived candidates.

---

## Step 4 — Scan implementation reality

Now scan the codebase to determine:
- whether the objective already exists in some form
- whether it is partial
- whether implementation drift exists
- whether missing infrastructure makes the objective mandatory for MVP

This step is especially valuable for:
- half-built workstreams
- duplicated experiments
- dead branches of implementation
- “it exists in docs but not in code” situations

---

## Step 5 — Reconcile candidates

Merge duplicate or overlapping candidates.

For each resulting objective, determine:
- canonical objective name
- why it exists
- main supporting evidence
- dependency order
- status
- MVP priority

### Recommended statuses

- `done`
- `active`
- `planned`
- `missing-but-required`
- `stale`
- `deferred`

---

## Step 6 — Produce the roadmap

Write:

```text
.planning/roadmap/objectives.md
.planning/roadmap/dependency-graph.md
```

Each objective should include at least:
- ID
- objective name
- summary
- why it matters
- status
- dependencies
- MVP inclusion (`yes/no`)
- evidence sources

---

## Objective Validity Rules

An objective is valid for the roadmap if at least one of the following is true:

1. it is explicitly declared in trusted project docs
2. it is clearly implied by an accepted architectural/product decision
3. it exists as a partial implementation that must be completed for MVP coherence
4. it closes a real MVP gap discovered by reconciling intent and implementation

An objective should not be added just because:
- a file name looks interesting
- there is a random TODO in code
- a branch of code exists with no product or architectural relevance

---

## Trust Model

## High trust
- project docs
- canonical docs
- source-of-truth docs
- current structured planning package

## Medium trust
- archived planning artifacts
- handoffs
- decision records

## Lower trust
- code scan alone
- orphan files
- test names without planning support

### Important rule

Code scan alone should detect **gaps**, not define the product roadmap by itself.

---

## Recommended Internal Modules for `/mm:discover`

### `objective_sources.py`

Suggested responsibilities:
- `collect_from_project_docs()`
- `collect_from_canonical_docs()`
- `collect_from_planning_state()`
- `collect_from_decision_records()`
- `collect_from_codebase_scan()`

### `objective_reconciler.py`

Suggested responsibilities:
- merge duplicates
- assign confidence
- determine current status
- infer MVP relevance
- infer dependencies

### `roadmap_writer.py`

Suggested responsibilities:
- write `objectives.md`
- write `dependency-graph.md`
- optionally write a machine-readable `objectives.json`

---

## Why This Matters

Without explicit reconciliation, discovery fails in one of two ways:

### Failure mode A — document-only fantasy

The roadmap reflects what old docs promised, but not what the codebase actually is.

### Failure mode B — code-only archaeology

The roadmap reflects whatever files happen to exist, but loses the product and architectural intent.

The system must avoid both.

---

## Recommended Output Shape

Example objective entry:

```markdown
## O3 — project-state-realtime

**Summary:** Add real-time event streaming for the Project State dashboard.
**Status:** planned
**MVP:** yes
**Depends on:** project-state-mvp, websocket-event-contract
**Why it matters:** improves observability and operational continuity.
**Evidence:** docs/canonical/33-DASHBOARD-REALTIME-EVENTS.md, existing `/project-state` dashboard, backend event contract docs.
```

---

## Summary

`/mm:discover --roadmap --existing` should build the roadmap by:

1. collecting explicit intent
2. collecting planning state
3. collecting implied work from decisions
4. scanning implementation reality
5. reconciling all of the above
6. producing a ranked and dependency-aware roadmap

This keeps roadmap generation grounded, auditable, and resilient across models.
