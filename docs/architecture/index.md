# Architecture Index

This is the canonical entry point for architecture decisions and reusable runtime contracts in MasterMind.

## Canonical Sources

- `docs/decisions/ADR-001-dynamic-loop-selector.md` — why dynamic loop selection exists.
- `docs/specs/index.md` — implementation specs derived from ADRs.
- `docs/loops/README.md` — how loops are classified and selected.
- `docs/contracts/loop-envelope.md` — the standard runtime output contract.
- `docs/registry/roles.yaml` — canonical role and brain registry for loop composition.
- `docs/ORCHESTRATOR-GUIDE.md` — operator-facing orchestration behavior.

## Canonical Rules

- Architecture decisions live in ADRs.
- Runtime behavior lives in contracts and loop docs.
- Role selection is owned by the harness, not by domain brains.
- If a new loop or role is added, update the registry and the relevant tests.

## Change Policy

- Add new decisions as new ADRs.
- Supersede, do not overwrite, old decisions.
- Keep guides descriptive and contracts strict.
- Keep the registry machine-readable.
