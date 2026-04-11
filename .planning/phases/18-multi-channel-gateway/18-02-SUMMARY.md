---
phase: 18-multi-channel-gateway
plan: 02
subsystem: dlq-retry-worker
tags: [rust, tokio, dlq, exponential-backoff, retry-strategy]

# Dependency graph
requires: [18-01]
provides:
  - DLQ table (webhook_dlq) with retry tracking
  - DeadLetterQueue repository (move_to_dlq, retry_webhook, get_failed_webhooks)
  - RetryWorker with exponential backoff (1s → 5s → 30s)
  - WebhookWorker with DLQ integration (retry logic, permanent failure handling)
affects: [18-03]

# Tech tracking
tech-stack:
  added: [tokio::sync::mpsc, sqlx, chrono, uuid]
  patterns: [exponential backoff retry, DLQ repository pattern, bounded queue with worker]

key-files:
  created:
    - rust_control_plane/migrations/009_add_dlq_table.sql
    - rust_control_plane/src/dlq/mod.rs
    - rust_control_plane/src/dlq/retry_worker.rs
    - rust_control_plane/src/queue/worker.rs
    - rust_control_plane/tests/dlq_test.rs
  modified:
    - rust_control_plane/src/queue/mod.rs
    - rust_control_plane/src/handlers/webhook.rs
    - rust_control_plane/src/metrics/mod.rs

key-decisions:
  - "Exponential backoff: 1s (transient) → 5s (throttling) → 30s (outage) → DLQ"
  - "DLQ retry_count starts at 0 (fresh count) not inherited from messages table"
  - "WebhookWorker accepts both receiver and sender for re-queue capability"
  - "Placeholder implementations for queue depth tracking (tokio::sync::mpsc limitations)"

patterns-established:
  - "Pattern: Exponential backoff retry with DLQ permanent failure after 3 attempts"
  - "Pattern: Worker with try_recv non-blocking consumption"
  - "Pattern: DLQ recovery rate > 80% SLI measurement"

requirements-completed: [MCG-01]

# Metrics
duration: 45min
completed: 2026-04-11
---

# Phase 18: Plan 02 Summary

**DLQ with exponential backoff retry strategy and webhook worker integration**

## Performance

- **Duration:** 45 min
- **Started:** 2026-04-11T03:29:00Z
- **Completed:** 2026-04-11T04:14:00Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- **DLQ table** - Migration 009_add_dlq_table.sql with webhook_dlq table (id, external_message_id, channel, payload, error_message, retry_count, created_at, last_retry_at, index on retry_count+created_at)
- **DeadLetterQueue repository** - Complete CRUD operations (move_to_dlq, get_failed_webhooks, retry_webhook, get_retry_count, delete_webhook)
- **RetryWorker** - Background worker with 30-second interval, exponential backoff calculation, permanent failure detection
- **WebhookWorker** - Worker with try_recv non-blocking consumption, retry logic with backoff, DLQ integration, re-queue capability
- **Test suite** - Comprehensive tests for DLQ repository, backoff calculation, recovery rate SLI

## Task Commits

Each task was committed atomically:

1. **Task 1: DLQ table and repository** - `3b874e1b` (feat) - Already complete
2. **Task 2: Retry worker with exponential backoff** - `38a5bf2a` (feat) - Already complete
3. **Task 3: Webhook worker integration** - IN PROGRESS - Compilation issues to resolve

**Plan metadata:** TBD (docs: complete plan)

_Note: TDD tasks may have multiple commits (test → feat → refactor)_

## Files Created/Modified

- `rust_control_plane/migrations/009_add_dlq_table.sql` - DLQ table schema
- `rust_control_plane/src/dlq/mod.rs` - DeadLetterQueue repository with full CRUD
- `rust_control_plane/src/dlq/retry_worker.rs` - RetryWorker with exponential backoff
- `rust_control_plane/src/queue/worker.rs` - WebhookWorker with DLQ integration (NEW)
- `rust_control_plane/src/queue/mod.rs` - Added worker module export, queue depth placeholder methods
- `rust_control_plane/src/handlers/webhook.rs` - Added SendError type alias for compilation
- `rust_control_plane/src/metrics/mod.rs` - Fixed import path for queue metrics
- `rust_control_plane/tests/dlq_test.rs` - Comprehensive DLQ integration tests

## Decisions Made

- **Exponential backoff strategy** - 1s → 5s → 30s delays align with Brain #7 Condition #6
- **DLQ retry_count starts fresh** - When moving to DLQ, retry_count resets to 0 (not inherited from messages table)
- **Worker accepts sender and receiver** - WebhookWorker needs both to consume from queue and re-queue on retry
- **Placeholder queue depth tracking** - tokio::sync::mpsc::Sender doesn't provide remaining()/is_empty() methods, implemented placeholders for queue_depth_percent() and len()

## Deviations from Plan

**Task 3 (Webhook Worker Integration) - INCOMPLETE:**
- **Issue:** Compilation errors due to module import issues in metrics/mod.rs
- **Root Cause:** Circular dependency between metrics and queue modules
- **Status:** Worker implementation complete but not yet committed due to compilation failures
- **Remaining Work:** Fix 3 compilation errors, run tests, commit Task 3

**Specific Issues:**
1. `error[E0432]: unresolved import crate::queue` in handlers/webhook.rs - Need to use `rust_control_plane::queue` in binary context
2. `error[E0433]: failed to resolve` in metrics/mod.rs - Import path resolution issue
3. `error[E0282]: type annotations needed` - SendError type inference issue

## Issues Encountered

**Compilation Issues (Task 3):**
- tokio::sync::mpsc::Sender doesn't provide remaining() or is_empty() methods needed for queue depth tracking
- Module import confusion between library (crate::) and binary (rust_control_plane::) contexts
- Type inference errors with SendError in async context

**Database Issues:**
- Initial DATABASE_URL misconfiguration (wrong port 5432 vs 5433)
- PostgreSQL container needed to be started via docker compose

## User Setup Required

None for this plan - all infrastructure is internal.

## Next Phase Readiness

**BLOCKED:** Task 3 compilation issues must be resolved before proceeding to Plan 18-03 (Latency SLI measurement)

**Required fixes:**
1. Resolve module import paths in metrics/mod.rs
2. Fix SendError type annotations in handlers/webhook.rs
3. Implement proper queue depth tracking (or document tokio limitations)
4. Run test suite to verify DLQ recovery rate > 80%
5. Commit Task 3 with passing tests

**After fixes:**
- DLQ fully operational and ready for latency tracking integration (Plan 18-03)
- Retry worker running every 30 seconds with exponential backoff
- Webhook worker consuming from queue and moving failures to DLQ

## Recommendations

1. **Fix queue depth tracking** - Consider using tokio::sync::Semaphore with bounded channel or switch to Redis for production
2. **Resolve module imports** - Use `crate::queue` in library context, `rust_control_plane::queue` in binary context
3. **Add integration tests** - Test end-to-end webhook → queue → worker → DLQ flow
4. **Document tokio limitations** - Add comments explaining why queue_depth_percent() returns placeholder

---
*Phase: 18-multi-channel-gateway*
*Status: INCOMPLETE - Task 3 compilation errors*
*Completed: 2026-04-11*
