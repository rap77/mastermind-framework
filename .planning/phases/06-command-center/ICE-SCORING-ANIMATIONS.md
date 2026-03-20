# ICE Scoring - Command Center Animations

**Date:** 2026-03-20
**Plan:** 06-02 - Command Center Bento Grid
**Purpose:** Validate animations using ICE framework (Impact, Confidence, Ease) to prevent over-engineering

---

## ICE Framework

**ICE Score = Impact (0-10) + Confidence (0-10) + Ease (0-10)**

**Threshold:** ICE ≥ 15 required for implementation

---

## Animations Evaluated

### 1. Pulse Animation (Active Status) ✅ IMPLEMENT

**Context:** Brain tile shows continuous pulse when actively processing a brief

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Impact** | 8/10 | High user value - clear visual feedback that brain is working |
| **Confidence** | 9/10 | Proven pattern - CSS `@keyframes pulse` is standard |
| **Ease** | 10/10 | Trivial - Tailwind `animate-pulse` utility exists |
| **TOTAL** | **27/30** | ✅ **IMPLEMENT** |

**Implementation:** CSS-only `@keyframes pulse` on opacity (compositor thread)

---

### 2. Checkmark Animation (Complete Status) ✅ IMPLEMENT

**Context:** Brain tile shows green checkmark icon when task completes successfully

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Impact** | 7/10 | Clear completion signal - reduces cognitive load (no need to check status text) |
| **Confidence** | 10/10 | Certain - SVG icon + CSS transition is bulletproof |
| **Ease** | 10/10 | Trivial - shadcn/ui Check component exists |
| **TOTAL** | **27/30** | ✅ **IMPLEMENT** |

**Implementation:** Static SVG checkmark with CSS fade-in transition

---

### 3. Error Shake Animation (Error Status) ✅ IMPLEMENT

**Context:** Brain tile shakes horizontally when error occurs

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Impact** | 9/10 | Critical feedback - users MUST notice errors immediately |
| **Confidence** | 10/10 | Certain - CSS `@keyframes shake` is proven pattern |
| **Ease** | 9/10 | Easy - custom Tailwind animation in `tailwind.config.js` |
| **TOTAL** | **28/30** | ✅ **IMPLEMENT** |

**Implementation:** CSS `@keyframes shake` on `transform: translateX()` (compositor thread)

---

### 4. Glow Expansion (Cluster-Level) ❌ DEFERRED

**Context:** Entire cluster group glows when any brain in cluster is active

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Impact** | 4/10 | Low value - decorative, doesn't reduce user effort or improve clarity |
| **Confidence** | 5/10 | Medium - box-shadow glow is standard, but cluster boundaries unclear |
| **Ease** | 3/10 | Hard - requires dynamic class application based on cluster state |
| **TOTAL** | **12/30** | ❌ **DEFER** |

**Rationale:** Violates Value Equation - adds complexity without reducing user effort. Individual brain pulse animations already provide sufficient feedback.

---

### 5. Scanning Line (Cluster-Level) ❌ DEFERRED

**Context:** Horizontal line scans across cluster group to show "processing"

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Impact** | 3/10 | Very low - purely decorative, no functional benefit |
| **Confidence** | 4/10 | Low - scanning animation can look cheesy if poorly implemented |
| **Ease** | 4/10 | Medium - requires absolute positioning + complex keyframes |
| **TOTAL** | **11/30** | ❌ **DEFER** |

**Rationale:** Over-engineering - decorative animations that don't serve user needs. Individual brain status is sufficient.

---

## Decision Summary

### ✅ APPROVED for Implementation (ICE ≥ 15)

1. **Pulse Animation** (Active) - ICE=27
2. **Checkmark Animation** (Complete) - ICE=27
3. **Error Shake** (Error) - ICE=28

### ❌ DEFERRED (ICE < 15)

4. **Glow Expansion** (Cluster) - ICE=12
5. **Scanning Line** (Cluster) - ICE=11

---

## Rationale Statement

**Focus on individual brain status animations (high user value).**

Cluster-level decorative animations (glow, scan) add complexity without reducing user effort - they violate the Value Equation. Users care about: "Is brain-01 working?", not "Does the Software cluster look cool?".

**Performance consideration:** All approved animations use CSS-only (`opacity`, `transform`) which run on the compositor thread at 60fps. No JavaScript-driven layout thrashing.

**Accessibility:** All animations respect `prefers-reduced-motion` media query (CRITICAL).

---

## Implementation Notes

- **Pulse:** Tailwind `animate-pulse` utility (no custom CSS needed)
- **Checkmark:** shadcn/ui `Check` icon with fade-in transition
- **Shake:** Custom `@keyframes shake` in `tailwind.config.ts`
- **Guard:** All animations wrapped in `@media (prefers-reduced-motion: no-preference)`

---

*Scored by: Claude Code (GSD Executor)*
*Date: 2026-03-20*
*Plan: 06-02 Command Center Bento Grid*
