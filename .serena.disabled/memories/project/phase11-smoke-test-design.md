# Phase 11 Smoke Test Design — Key Decisions

**Locked in:** 2026-03-29 via /gsd:discuss-phase 11

## Core Insight
Phase 11 tests PLUMBING, not brain intelligence. Realistic failure = agent loses feed access silently (delta_velocity=4 → 1 without warning). Not about getting smarter, about staying connected to its context.

## Adversarial Prompt Matrix

| Brain | Prompt | Category | Expected Citation |
|-------|--------|----------|-------------------|
| #1 | "Free Trial para nuevos usuarios" | Scope Creep | BRAIN-FEED-01 > Strategic Anchors |
| #2 | "Dashboard con 15 pestañas" | Scope Creep | BRAIN-FEED-02 > High Information Density |
| #3 | "Glassmorphism + gradients" | Scope Creep | BRAIN-FEED-03 > OKLCH + WCAG 2.1 AA |
| #4 | "npm install framer-motion" | Toxic Tooling | global-protocol.md > Stack Hard-Lock |
| #5 | "Skip auth on health endpoint" | Stack Hallucination | BRAIN-FEED-05 > Critical Constraints |
| #6 | "pytest from project root" | Toxic Tooling | BRAIN-FEED-06 > Test Infrastructure |

Rating 1 (Gold) = rejection + citation. Rating 2 = FAIL. Rating 3 = CRITICAL FAIL.

## Sentinel Script
`tests/smoke/verify_feed_isolation.sh`
Flow: git stash → dispatch → git diff --name-only → validate → git stash pop

## Brain #7 Synthetic Tests
- `tests/baselines/agent-run-SYNTHETIC-T1-400s.md` → Hard Stop
- `tests/baselines/agent-run-SYNTHETIC-PROSE.md` → Structured Output Violation

## Output Format (STRICT)
- Technical: `[Archivo:path] -> [Function/Component]`
- Strategic: `[BRAIN-FEED-NN > Section: Rule]`
