# Requirements — multi-channel-gateway

## Problem / Purpose
Multi-channel Gateway

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.

## T1 Boundary Decision

### What already exists
- Historical roadmap marks Phase 18 as completed, so this objective should not
  assume a greenfield build.
- The repo already contains:
  - channel send surfaces (`apps/api/routers/whatsapp.py`,
    `apps/api/routers/instagram.py`, `apps/api/routers/email.py`)
  - an internal gRPC worker bridge (`apps/api/routers/internal.py`)
  - channel enum/routing placeholder (`apps/api/routers/channel_router.py`)

### Current gap to target
- The most credible remaining gap is **inbound multi-channel normalization and
  reliability**, not outbound send helpers alone.
- The first safe slice should tighten the **backend-authoritative internal
  event contract** that receives/normalizes WhatsApp, Instagram, and Email
  payloads before broader queueing, inbox UI, or provider-specific expansion.

### Explicit non-goals for this objective slice
- No “build the whole unified inbox” restart.
- No Redis/DLQ/circuit-breaker program in the first slice.
- No provider-auth onboarding or full webhook verification matrix yet.
- No broad UI rebuild for channel operations yet.
