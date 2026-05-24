# DR-007 — Rust Control Plane Consolidation

## Decision

MasterMind adopts `rust_control_plane` as the single canonical Rust control plane and removes `apps/control-plane` to avoid architectural confusion, duplicate evolution, and split ownership.

## Rationale

A comparative review showed that `rust_control_plane` is substantially more complete and better aligned with production-grade control-plane responsibilities:

- auth and middleware
- websocket hub
- queueing and DLQ
- event sourcing
- observability and metrics
- migrations and PostgreSQL support
- integration and load tests

By contrast, `apps/control-plane` remained largely a spike with:

- mock gRPC client
- placeholder proto types
- mock-header auth
- limited repository depth
- much narrower test coverage

## Operational consequence

Going forward:

- all Rust control-plane development happens in `rust_control_plane`
- `docker-compose` and proto generation point to `rust_control_plane`
- `apps/control-plane` is removed from the repo

## Follow-up work

Before extending the canonical Rust base further, MasterMind should harden `rust_control_plane` by:

1. fixing refresh-token lookup/rotation semantics
2. restoring or redefining gRPC worker integration
3. cleaning migration numbering and placeholders
4. clarifying Python vs Rust responsibility boundaries

## Key Learnings:

1. Keeping two Rust control planes alive would create more confusion than optionality.
2. `rust_control_plane` is the clearly superior base on completeness and operational design.
3. Consolidation should happen before further runtime expansion.
