---
phase: 09-baselines-agent-authoring
plan: 02
subsystem: agent-authoring
tags: [brain-agents, global-protocol, subagents, claude-code, product-strategy, ux-research]
dependency_graph:
  requires:
    - 09-01 (baselines authored — git timestamp prerequisite)
  provides:
    - global-protocol.md (shared governance layer for all 7 brain agents)
    - Brain Bundle #1 — Product Strategy (3 files)
    - Brain Bundle #2 — UX Research (3 files)
  affects:
    - Phase 10 (BRAIN-FEED split — agents reference domain feed paths created there)
    - Phase 11 (smoke tests — will test these agent files)
    - Phase 12 (dispatch wiring — agents referenced by mm:brain-context command)
tech_stack:
  added: []
  patterns:
    - Claude Code subagent format (YAML frontmatter + system prompt Markdown)
    - Brain Bundle pattern (agent + criteria + warnings per domain directory)
    - Global governance file (one edit propagates to all 7 agents)
    - Oracle Pattern (citation-required rejections)
    - Delta-Velocity Matrix embedded in criteria.md
key_files:
  created:
    - .claude/agents/mm/global-protocol.md
    - .claude/agents/mm/brain-01-product/brain-01-product.md
    - .claude/agents/mm/brain-01-product/criteria.md
    - .claude/agents/mm/brain-01-product/warnings.md
    - .claude/agents/mm/brain-02-ux/brain-02-ux.md
    - .claude/agents/mm/brain-02-ux/criteria.md
    - .claude/agents/mm/brain-02-ux/warnings.md
  modified: []
decisions:
  - "global-protocol.md positioned as governance reference, not system prompt — agents read and obey it, never duplicate its constraints inline"
  - "Persona bias opens system prompt verbatim — 'You are Brain #N... You are [Archetype].' not 'Follow these steps'"
  - "6-step protocol embedded as identity using first-person framing ('Before I form any opinion, I read...') — not a step-list the agent optionally follows"
  - "[CORRECTED ASSUMPTIONS] are domain-specific per brain, not generic — Brain #1 corrects internal-tool/v2.2-evolution, Brain #2 corrects desktop-first/expert-user"
  - "No notebook IDs hardcoded in agent files — brain-selection.md referenced instead (decoupled)"
  - "No BRAIN-FEED-NN-domain.md files created — those are Phase 10 scope (references to non-existent paths are intentional)"
metrics:
  duration: "25 minutes (1469 seconds)"
  completed_date: "2026-03-28"
  tasks_completed: 2
  files_created: 7
---

# Phase 09 Plan 02: Global Protocol + Brain Bundles #1-#2 Summary

**One-liner:** Shared governance layer (global-protocol.md) + Brain Bundle pattern established with Product Strategy (Discovery Ruthless) and UX Research (Flow Absolutist) subagents — each with domain-specific Rating 3 vs 4 criteria and 4+4 anti-pattern warnings.

---

## Files Created

| File | Description |
|------|-------------|
| `.claude/agents/mm/global-protocol.md` | Shared governance layer — Stack Hard-Lock, File Architecture, WS Protocol, Cross-Domain Anti-Patterns, Feed Write Scope, Oracle Pattern, Delta-Velocity scale |
| `.claude/agents/mm/brain-01-product/brain-01-product.md` | Brain #1 Product Strategy subagent — Discovery Ruthless persona, 6-step protocol as identity, domain [CORRECTED ASSUMPTIONS] |
| `.claude/agents/mm/brain-01-product/criteria.md` | Brain #1 quality gate — Rating 3 vs 4 table (Focus/Risks/Metrics/Systems/Decision), Build Trap auto-reject, Rating 5 threshold |
| `.claude/agents/mm/brain-01-product/warnings.md` | Brain #1 anti-patterns — 4 universal patterns + Build Trap/Vanity Metrics/Solution Anchoring/Stakeholder Theater |
| `.claude/agents/mm/brain-02-ux/brain-02-ux.md` | Brain #2 UX Research subagent — Flow Absolutist persona, 6-step protocol, War Room desktop-first corrected assumptions |
| `.claude/agents/mm/brain-02-ux/criteria.md` | Brain #2 quality gate — Rating 3 vs 4 (Cognitive Load/Navigation/Feedback/Error Recovery/War Room Context), Complexity Theater auto-reject |
| `.claude/agents/mm/brain-02-ux/warnings.md` | Brain #2 anti-patterns — 4 universal patterns + Aesthetic Override/Animation Inflation/Mobile Contamination/Generic Persona |

---

## Decisions Made During Authoring

### Persona Authoring (system prompt opening)

The plan specified persona bias must open system prompts verbatim. Executed exactly:
- Brain #1: "You are Brain #1 of the MasterMind Framework — Product Strategy. You are Discovery Ruthless. 'Does this solve a real user pain? Show me the evidence.' You are not a feature factory. You are not a roadmap executor. You are an outcome machine."
- Brain #2: "You are Brain #2 of the MasterMind Framework — UX Research. You are a Flow Absolutist. 'If the user can't find it in 3 clicks, it doesn't exist.' You do not design pretty things. You design cognitive load reduction."

Decision: Added a third "personality sharpener" sentence after the bias statement ("You do not take orders. You question them.") to reinforce the expert identity beyond vocabulary.

### [CORRECTED ASSUMPTIONS] Specificity

Brain #1 corrected assumptions are MasterMind-specific (v2.2 not greenfield, builder IS the user, T1 reduction = ROI). Added a fifth assumption not in the plan: "Prioritize by business value → Prioritize by T1 reduction" — this is the correct domain-specific metric and prevents generic product prioritization frameworks being applied.

Brain #2 corrected assumptions added a sixth not in the plan: "Follow SaaS conventions → War Room is closer to an IDE than a SaaS dashboard." This catches a high-frequency error pattern for developer tools.

### Protocol Framing (identity vs. checklist)

The 09-RESEARCH.md pitfall #4 warned against step-list format. Solution: Section headers are first-person identity statements:
- "Before I Form Any Opinion, I Read Project Reality" (not "Step 1: Read")
- "I Only Speak of What Exists, Not What Is Planned" (not "Step 2: Build")
- "I Grep Before I Conclude" (not "Step 5: Filter")

This frames the protocol as how the agent thinks, not a procedure to optionally execute.

### global-protocol.md as Reference Document

Decision: global-protocol.md is explicitly labeled a reference document, not a system prompt. It uses table format for Cross-Domain Anti-Patterns to make the rating impact immediately scannable. Added a "Session Start Reminder" section at the end that summarizes the 7-step execution order — this is available to any brain that queries the file mid-consultation.

### Output Format Sections

Added explicit `## Output Format` sections to both agent files specifying required response structure. This is not in the plan spec but directly addresses the 09-CONTEXT.md finding that "structured output required in agent system prompts" — cascade re-run in baseline 04 (imprecise language → Brain #7 error) proves free-text prose causes information leaks.

---

## Verification Results

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| global-protocol.md sections | >= 4 | 11 | PASS |
| global-protocol.md line count | >= 80 | 159 | PASS |
| Brain Bundle file count | 6 | 6 | PASS |
| model: inherit in both agents | 2 | 2 | PASS |
| mcpServers: notebooklm-mcp | 2 | 2 | PASS |
| FEED-02: global BRAIN-FEED.md reads | 2 | 2 | PASS |
| FEED-03: domain feed write constraints | 2 | 2 | PASS |
| criteria.md with Rating 3 tables | 2 | 2 | PASS |
| warnings.md universal patterns (brain-01) | >= 4 | 9 | PASS |
| warnings.md universal patterns (brain-02) | >= 4 | 9 | PASS |
| Notebook IDs NOT in agent files | 0 | 0 | PASS |
| BRAIN-FEED-NN-domain.md files NOT created | 0 | 0 | PASS |
| Git order: baselines precede agents | TRUE | TRUE | PASS |
| Backend suite regression | 575 pass | 575 pass | PASS |
| Frontend suite regression | 407 pass | 407 pass | PASS |

---

## Deviations from Plan

None — plan executed exactly as written with additive enhancements only (Output Format sections, additional [CORRECTED ASSUMPTIONS] entries, personality sharpener sentences). All additions serve the core authoring goals without violating any plan constraints.

---

## Self-Check

**Checking created files exist:**

- FOUND: .claude/agents/mm/global-protocol.md
- FOUND: .claude/agents/mm/brain-01-product/brain-01-product.md
- FOUND: .claude/agents/mm/brain-01-product/criteria.md
- FOUND: .claude/agents/mm/brain-01-product/warnings.md
- FOUND: .claude/agents/mm/brain-02-ux/brain-02-ux.md
- FOUND: .claude/agents/mm/brain-02-ux/criteria.md
- FOUND: .claude/agents/mm/brain-02-ux/warnings.md

**Checking commits exist:**

- FOUND: 581ce44 feat(09-02): create global-protocol.md
- FOUND: 1002235 feat(09-02): create Brain Bundles #1 (Product) and #2 (UX)

## Self-Check: PASSED
