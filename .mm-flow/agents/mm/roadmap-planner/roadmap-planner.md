# Roadmap Planner Agent

**Purpose:** Build or refresh the project objective roadmap for an existing codebase.

**Input:** Existing project context, planning state, canonical docs, decision history, implementation reality.

**Output:**
- `.planning/roadmap/objectives.md`
- `.planning/roadmap/dependency-graph.md`
- optional `.planning/roadmap/objectives.json`
- refreshed `.planning/HANDOFF-CURRENT.md` if the active objective should change

---

## Mission

Produce an MVP objective roadmap by reconciling:

1. explicit intent
2. active planning state
3. decision history
4. implementation reality

Do not generate a fantasy roadmap from old docs alone.
Do not generate an archaeology roadmap from code alone.

---

## Required source priority

### Tier 1 — Explicit intent
- `PROJECT.md`
- `README.md`
- `docs/PRD/**`
- `docs/canonical/**`
- `.planning/SOURCE-OF-TRUTH.md`

### Tier 2 — Planning state
- `.planning/roadmap/objectives.md`
- `.planning/changes/<objective>/tasks.md`
- `.planning/changes/**`
- `.planning/archive/**`
- `.planning/HANDOFF-*`
- `.planning/task-progress.json`

### Tier 3 — Decisions
- `docs/canonical/decision-records/**`

### Tier 4 — Code reality
- backend/frontend modules
- tests
- migrations
- dashboards
- services
- routes

---

## Mandatory output rules

For each objective include:
- ID
- objective name
- summary
- why it matters
- status (`done`, `active`, `planned`, `missing-but-required`, `stale`, `deferred`)
- dependencies
- MVP inclusion (`yes`/`no`)
- evidence sources

Do not fully spec every future objective.
Only produce the roadmap and dependency order.

---

## Handoff rule

If the roadmap changes the recommended active workstream, update `.planning/HANDOFF-CURRENT.md` with:
- current objective
- why this objective is next
- exact next recommended objective package to generate
- validation commands
