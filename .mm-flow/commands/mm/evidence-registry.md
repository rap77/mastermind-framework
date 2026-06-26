---
name: mm:evidence-registry
description: Manage the versioned evidence registry for canonical docs and external sources.
argument-hint: "<command> [options]"
---

# /mm:evidence-registry

Manage evidence versions, deltas, and readiness.

## Usage

```bash
python3 .mm-flow/commands/mm/evidence-registry.py register \
  --source-type doc \
  --name "Launch Plan" \
  --uri docs/launch-plan.md \
  --version-ref docs/launch-plan.md \
  --version-hash <sha256> \
  --summary "Canonical launch plan"

python3 .mm-flow/commands/mm/evidence-registry.py readiness --id ev-0001
python3 .mm-flow/commands/mm/evidence-registry.py delta --from-id ev-0001 --to-id ev-0002 \
  --delta-type decision --summary "Updated with user feedback"
python3 .mm-flow/commands/mm/evidence-registry.py list-deltas
python3 .mm-flow/commands/mm/evidence-registry.py list-deltas --source-id canonical:prd:launch-plan
python3 .mm-flow/commands/mm/evidence-registry.py list-deltas --delta-type decision --decision superseded
```

## Commands

| Command | Description |
|---|---|
| `register` | Register a new evidence version |
| `list` | List evidence versions |
| `list-deltas` | List evidence deltas |
| `readiness` | Compute readiness for a version |
| `delta` | Record a delta between two versions |

## Notes

- `register` records canonical docs created by `new-canonical`
- `register` auto-records a delta when the same source is registered again with a new hash
- `readiness` is deterministic from confidence, coverage, gaps, and contradictions
- `delta` preserves version-to-version lineage
- `list-deltas` supports source/type/decision filters
