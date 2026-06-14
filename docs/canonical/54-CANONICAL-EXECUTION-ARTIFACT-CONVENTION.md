# 54 - Canonical Execution Artifact Convention

## Goal

Define the minimum canonical convention for persisting execution detail payloads needed by Strategy Vault without relying on legacy `execution_history`.

---

## Scope

This convention covers:

- per-run `brain_outputs`
- replayable `graph_snapshot`

It does **not** attempt to solve full artifact content modeling yet.

---

## Transitional Convention

### 1. Execution output bundle

Store one artifact version per run using:

- `artifact_type = execution_output_bundle`
- `artifact_id = execution-output:{run_id}`

Metadata keys:

- `run_id`
- `task_id`
- `brain_outputs`
- `format_version = 1`

### 2. Execution graph snapshot

Until a dedicated artifact writer exists, derive the snapshot from:

- `ps_tasks.metadata.flow_config`

If that payload already contains:

- `nodes`
- `edges`

then it is sufficient for the current replay/detail contract.

---

## Why this is acceptable

- it removes dependency on `execution_history` for the richest currently available execution payload
- it keeps the migration surgical
- it leaves room for a future richer artifact body/content model

---

## Known Limits

- `brain_outputs` lives in artifact metadata for now, not a dedicated content field
- `graph_snapshot` is derived, not explicitly versioned yet
- milestone richness still depends on future telemetry/checkpoint conventions

---

## Follow-up

Future refinement should introduce:

1. explicit execution graph snapshot artifact writes
2. explicit artifact content/body support beyond metadata-only storage
3. richer milestone reconstruction from runtime telemetry

## Key Learnings:

1. A metadata-backed execution output bundle is enough to decouple Strategy Vault detail from legacy SQLite immediately.
2. Existing `flow_config` already provides a usable minimal graph snapshot source in many cases.
3. This convention is transitional but canonical enough to move read paths off `execution_history`.
