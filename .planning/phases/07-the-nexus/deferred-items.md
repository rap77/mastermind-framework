# Deferred Items — Phase 07 The Nexus

Items discovered during execution that are out of scope and deferred.

## Pre-existing Test Failures (not introduced by this phase)

### 1. test_cors_configuration
- **File:** `apps/api/tests/api/test_app.py::test_cors_configuration`
- **Status:** FAILING before Phase 07 work started (verified via git stash)
- **Issue:** CORS preflight OPTIONS request returns 400 — `access-control-allow-origin` header absent
- **Owner:** Pre-existing — not Phase 07 scope

### 2. test_get_brain
- **File:** `apps/api/tests/unit/test_brain_registry.py::test_get_brain`
- **Status:** FAILING before Phase 07 work started (verified via git stash)
- **Issue:** `assert 'idle' == 'active'` — brain registry default state mismatch
- **Owner:** Pre-existing — not Phase 07 scope
