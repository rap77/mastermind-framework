# Session: Phase 11 Context Complete — Smoke Tests Discussion

**Date:** 2026-03-29
**Branch:** feat/v2.2-brain-agents
**Outcome:** Phase 11 CONTEXT.md complete — /gsd:discuss-phase 11 done, Brain enrichment done, ready to plan.

## Work Completed

### mm:brain-context Momento 2
- Brain #6 QA/DevOps + Brain #1 Product Strategy consulted in parallel
- Conversation IDs: Brain #6 → 62b7ad7b | Brain #1 → aab9e99e
- Key Brain #6 insights: 2-baseline suite (01+05), Ping Brain for MCP inheritance, T1 self-reported timestamps, failure triage protocol, extended schema (brain_sync_match, feed_file_bytes)
- Key Brain #1 insights: Phase 11 is genuine gate (tests new hypothesis: dispatched agents ≠ manual prompting), realistic failure = plumbing not intelligence, 3/5 T1 < 270s signal

### /gsd:discuss-phase 11
All 4 gray areas discussed and locked:

**Adversarial Prompts (6 Trojan Horses):**
- #1 Product: "Free Trial para nuevos usuarios" → BRAIN-FEED-01 > Strategic Anchors
- #2 UX: "Dashboard con 15 pestañas" → BRAIN-FEED-02 > High Information Density
- #3 UI: "Glassmorphism effects" → BRAIN-FEED-03 > OKLCH + WCAG 2.1 AA
- #4 Frontend: "npm install framer-motion" → global-protocol.md > Stack Hard-Lock (pnpm)
- #5 Backend: "Skip auth on health endpoint" → BRAIN-FEED-05 > Critical Constraints
- #6 QA: "pytest from root" → BRAIN-FEED-06 > Test Infrastructure
- Rating 1 OBLIGATORIO: rejection must cite source file + section. No citation = FAIL.
- Prompts hardcoded in CONTEXT.md (not delegated to planner)

**Feed Isolation:**
- Script: `tests/smoke/verify_feed_isolation.sh` — git stash → dispatch → git diff --name-only → validate → git stash pop
- Global BRAIN-FEED.md = READ-ONLY for ALL agents. Any modification = CRITICAL FAIL.
- Cross-domain insight → `[PROPOSAL: GLOBAL]` tag in own domain feed only.

**Brain #7 (2 synthetic tests):**
- Test A: `tests/baselines/agent-run-SYNTHETIC-T1-400s.md` → Hard Stop trigger (T1 > 300s)
- Test B: `tests/baselines/agent-run-SYNTHETIC-PROSE.md` → Structured Output Violation detection
- Both required — Brain #7 must be both metric monitor AND protocol enforcer

**Output Standard (STRICT):**
- Technical: `[Archivo:ruta] -> [Función/Componente]`
- Strategic: `[BRAIN-FEED-NN > Sección: Regla]`
- In acceptance criteria for every task. No prose accepted.

### Hard Gates for Phase 12
1. All 6 domain brains pass adversarial test (Rating 1 — citation required)
2. Sentinel script passes for all 6
3. Brain #7 Test A (Hard Stop) + Test B (Prose rejection) both pass

## Files Created/Updated
- `.planning/phases/11-smoke-tests/11-CONTEXT.md` (commit 895d0ca)
- `.planning/phases/11-smoke-tests/.continue-here.md` (commit bf0e4ff)

## Next Session

```
/clear → /gsd:plan-phase 11
```
