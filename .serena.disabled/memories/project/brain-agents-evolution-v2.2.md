# Brain Agents Evolution — v2.2 Architectural Vision

**Date:** 2026-03-22
**Status:** Documented in PROJECT.md + ROADMAP.md — execution deferred to after v2.1

## Core Insight

Brains (NotebookLM) are static knowledge — they never learn. The "learning" happens in the intermediary (Claude) via accumulated BRAIN-FEED context. The quality of brain responses depends entirely on the quality of the context Claude provides.

## Evolution Path

1. **v2.1 (current):** `mm:brain-context` skill with manual workflows → Claude follows instructions
2. **v2.2 (next):** Autonomous subagents per brain → intermediary protocol is native behavior
3. **v3.0 (future):** Agents + RAG → each agent manages its own vector store

## v2.2 Key Architecture

- 7 brain subagents (`.claude/agents/brain-NN-*.md`) — system prompts derived from `mm:brain-context/workflows/`
- Two-level BRAIN-FEED: `BRAIN-FEED.md` (general) + `BRAIN-FEED-NN-*.md` (per-brain domain)
- Orchestrator dispatches agents in parallel (vs. sequential workflow following today)
- Each agent: reads domain + general feed → reads code → queries NotebookLM → filters → updates domain feed → returns insights
- Inter-agent coordination via orchestrator for cross-domain decisions

## What Already Exists (Foundation)

- `mm:brain-context/workflows/moment-{1,2,3}.md` → become agent system prompts
- `mm:brain-context/workflows/update-brain-feed.md` → becomes agent post-phase behavior
- `mm:brain-context/references/intermediary-protocol.md` → embedded in each agent
- `mm:brain-context/references/brain-selection.md` → becomes orchestrator routing logic
- `mm:brain-context/templates/BRAIN-FEED.md` → template for both general and per-brain feeds

## Where It's Documented

- `PROJECT.md` → "Deferred (v2.2)" section + "Vision Notes" section + Key Decisions table
- `ROADMAP.md` → v2.2 and v3.0 milestone stubs added
