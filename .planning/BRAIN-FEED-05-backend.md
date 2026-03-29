# BRAIN-FEED-05 — Backend Domain Feed

> Written by Brain #5 (Backend). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-03-28

---

## Critical Constraints (Non-Negotiable)

- uv only, never pip or poetry
- pytest runs from apps/api/ only: `cd apps/api && uv run pytest` — running from project root fails with ModuleNotFoundError: mastermind_cli
- JWT in httpOnly cookies only — never in client bundle, never in localStorage
- WS auth via /api/auth/token handoff pattern — server reads cookie, returns short-lived token to client

---

## Auth & Security

- JWT verified at Server Components + Route Handlers (not only `proxy.ts`) — CVE-2025-29927 mitigation
- httpOnly cookie storage — XSS defense (not localStorage)
- WS token handoff via `/api/auth/token` endpoint — server-side cookie read, token not in client bundle
- DOMPurify + `html.escape` backend — defense in depth for XSS

---

## API Design

- TanStack Query Eager Loading — single query fetches all 24 brains (N+1 prevention)
- Pagination from day one: `page`, `page_size` (default 24, max 100) — Margin of Safety
- SQLAlchemy `selectinload` for one-to-many relationships — N+1 prevention (NOT yet implemented — required pattern for future endpoints)
- IDOR protection pattern: `WHERE id = :id AND user_id = :current_user_id` on all user-scoped queries

---

## Anti-patterns (Backend)

- `jwt.verify()` from jsonwebtoken → use `jose` library (Edge Runtime compatible)
- `localStorage` for JWT → use httpOnly cookie (XSS attack vector)

---

## SYNC Cross-References

Sync: pytest infrastructure ownership — [SYNC: BF-06-001] → BRAIN-FEED-06-qa.md > Test Infrastructure. Brain #6 QA owns the full test command spec. Owner: Brain #6 QA.
