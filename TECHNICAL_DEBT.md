# Technical Debt — MasterMind Framework v2.1

This document tracks known technical limitations and planned improvements.

## Priority: High

### None at this time

## Priority: Medium

### TD-001: In-Memory Rate Limiter
**Location:** `apps/web/src/app/api/auth/token/route.ts:4-24`

**Issue:**
- Rate limiter uses `Map<string, ...>` for storage
- Does not scale across multiple server instances
- Rate limit resets on server restart
- Attackers can bypass by reconnecting or hitting different instances

**Impact:**
- Production vulnerability when deploying multiple Next.js instances
- DoS risk for `/api/auth/token` endpoint

**Plan:**
- Migrate to Redis-backed rate limiter before multi-instance deployment
- For v2.1 (single instance): Accept as limitation

**Target:** Phase 08 (Engine Room) or v2.2

---

### TD-002: Empty Test Scaffolds
**Location:** 13 test files in `apps/web/src/**/__tests__/`

**Issue:**
- All test files contain placeholder tests only
- No actual assertions for auth flow, WS connection, store updates
- False confidence in test coverage

**Impact:**
- No safety net for refactoring
- Regression risk when modifying auth/WS/store code

**Plan:**
- Implement real TDD tests for critical paths (auth, WS pipeline, stores)
- OR remove placeholder test files entirely

**Target:** Phase 06 (Command Center)

---

## Priority: Low

### TD-003: TypeScript Strict Mode Verification
**Location:** `apps/web/tsconfig.json`

**Issue:**
- Cannot verify if `strict: true` is enabled
- Strict mode catches more bugs at compile time

**Impact:**
- Medium — potential type safety gaps

**Plan:**
- Verify and enable `"strict": true` in tsconfig.json
- Fix any resulting type errors

**Target:** Phase 06

---

### TD-004: WS URL Environment Variable Naming
**Location:** `apps/web/src/stores/wsStore.ts:34`

**Issue:**
- Inconsistent naming: `API_URL` vs `NEXT_PUBLIC_WS_URL` vs `localhost:8000` fallback
- Confusing for developers

**Impact:**
- Low — works, but confusing

**Plan:**
- Standardize on `NEXT_PUBLIC_API_URL` and derive WS URL from it

**Target:** Phase 06

---

### TD-005: Missing JSDoc Comments
**Location:** All store files, auth utilities

**Issue:**
- No JSDoc comments on exported functions
- IDE hover shows types but no usage examples

**Impact:**
- Low — type information available, but missing documentation

**Plan:**
- Add JSDoc to public APIs

**Target:** Phase 08 (UX Polish)

---

### TD-006: Hardcoded Test Brain IDs
**Location:** `apps/web/src/app/(protected)/page.tsx:6`

**Issue:**
- Test page hardcoded for 24 brains, not configurable

**Impact:**
- Low — this is a test page, not production code

**Plan:**
- Accept as-is for Phase 05
- Consider environment variable in Phase 06

**Target:** Phase 06 or later

---

## Resolved Issues

### ✅ Debug Logging in Production (Fixed 2026-03-19)
**Previous Issue:** 20 console.log statements exposing JWT payloads
**Resolution:** All debug logs removed from production code
**Commit:** Pending

---

### ✅ Missing Error Boundaries (Fixed 2026-03-19)
**Previous Issue:** No user-facing error handling for WS/React errors
**Resolution:** ErrorBoundary component added, wsStore enhanced with error state and auto-reconnect
**Commit:** Pending

---

## Summary

| ID | Priority | Issue | Status | Target |
|----|----------|-------|--------|--------|
| TD-001 | Medium | In-memory rate limiter | Open | Phase 08/v2.2 |
| TD-002 | Medium | Empty test scaffolds | Open | Phase 06 |
| TD-003 | Low | TS strict mode verification | Open | Phase 06 |
| TD-004 | Low | WS URL env var naming | Open | Phase 06 |
| TD-005 | Low | Missing JSDoc comments | Open | Phase 08 |
| TD-006 | Low | Hardcoded test brain IDs | Open | Phase 06 |

**Last updated:** 2026-03-19
