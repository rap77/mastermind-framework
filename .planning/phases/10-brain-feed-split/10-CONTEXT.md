# Phase 10: BRAIN-FEED Split - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Migrate monolithic `.planning/BRAIN-FEED.md` to a two-level architecture: 1 global feed (cross-domain, product/UX decisions only) + 7 domain feeds (one per brain). The global feed retains only what ALL brains need equally. Domain feeds are initialized with seed content via archaeology + Brain #8 validation. No agent files are modified in this phase — domain feed file paths are already locked in 21 agent files from Phase 09.

**Target:** Global feed < 20 entries after cleanup. If it stays at 50+, there's still "technical fat" that belongs in domain feeds.

</domain>

<decisions>
## Implementation Decisions

### Feeds Vacíos (#1-product, #2-ux, #7-growth)
- **Strategic Anchor approach** — not empty, not full archaeology.
- Process: Archaeology of Phase 01-08 SUMMARYs → extract 3-5 Architecture Facts per domain → Brain #8 validation ("Is there a critical business decision missing that would bias this brain?") → write refined anchors.
- Max 3 "Strategic Anchors" per feed: the facts that, if missing, cause the brain to hallucinate generic responses.
- Brain #2 UX specific anchors required: "War Room = IDE, not SaaS dashboard", "4-panel layout (Command Center, Nexus, Vault, Engine Room)", "ICE Scoring ≥ 15 for animations".
- Brain #1 Product specific anchors: "Builder IS the user", "T1 reduction = ROI metric (not generic conversion)", "v2.2 — not greenfield, mature system".
- Brain #7 Growth anchors: "Delta-Velocity scale (1-5)", "T1 Profitability Threshold: > 300s = agent-unprofitable".

### Global Feed Strictness — Ownership-First
- **Global feed = EXCLUSIVELY product decisions, UX decisions, and phase milestones affecting ALL 7 brains equally.**
- Zero technical entries in global, even if they affect 2 domains.
- Every technical entry has one "Owner Principal" (the brain that knows it best).
- Rule: "Which brain, if it got this wrong, would cause the biggest production failure?" → that's the owner.
- Examples: Auth & Security → Brain #5 Backend (owner). WS token handoff → Brain #5 Backend (owner), pointer in Brain #4 Frontend.
- Stack (Locked) table: stays in global — it's a product/architecture decision, not a technical pattern.
- Brain Agent Architecture section: stays in global — meta-architecture all brains need equally.
- Delta-Velocity Measurement: stays in global — cross-domain measurement framework.

### Migration Approach — Niche-Validation Loop (3 plans)
- **Plan 10-01: Engineering Niche** — #4 Frontend + #5 Backend + #6 QA feeds. Includes quick smoke test within the plan (ask Brain #4 to explain Auth protocol from its new local feed only — if it hallucinates, adjust ambiguity rule immediately).
- **Plan 10-02: Strategy Niche** — #1 Product + #2 UX + #3 UI + #7 Growth feeds. Brain #8 validates strategic anchors before finalizing seed content.
- **Plan 10-03: Global Consolidation** — Cleanup of global BRAIN-FEED.md (remove all domain entries). Apply purity linter. Run integrity verification script (hash/count assertion).
- Advantage: if Engineering niche smoke test fails, we adjust the ownership rule BEFORE migrating the Strategy niche.

### Cross-Reference — Pointer Explícito + SYNC Tags (Phase 12 hook)
- When domain B needs info owned by domain A: add a one-liner in domain B's feed.
- Format: `Sync: [Entry description] — [SYNC: BF-05-WS-PROTOCOL] → BRAIN-FEED-05-backend.md`
- The `[SYNC: BF-NN-ID]` tag is the hook for Phase 12 Context Proxy automation (orchestrator parses tags, clones entry into temporal context at dispatch time).
- Do NOT create bidirectional cross-links — only the secondary consumer gets the pointer, the owner file stays clean.
- Phase 10 implements pointers manually. Phase 12 automates injection.

### Verification Protocol
- **Hash/count script** (Python, idempotent): parse original BRAIN-FEED.md → count N entries → after migration count entries across all 8 files → assert N_original == N_new, no duplicates.
- **Path existence validation**: parse all `.claude/agents/mm/**/*.md` → extract `BRAIN-FEED-NN-domain.md` paths → assert each exists on disk. Silent failure (non-existent path = no error + empty context) must be caught before Phase 11.
- **Global purity linter**: grep global BRAIN-FEED.md for domain vocabulary (`Zustand`, `NODE_TYPES`, `dagre`, `FastAPI`, `SQLAlchemy`, `asyncio`, `pytest`, `Vitest`) — assert zero matches (excluding Stack table).
- All three checks must pass before Plan 10-03 is marked complete.

### Claude's Discretion
- Exact format/structure of each domain feed file (headers, sections, markdown style)
- Which specific anti-patterns from the old feed go to which brain (follows classification rule mechanically)
- ID numbering scheme for SYNC tags (e.g., BF-05-001, BF-05-002, etc.)
- Whether to use Python or bash for verification scripts

</decisions>

<specifics>
## Specific Ideas

- Target metric: global BRAIN-FEED.md < 20 entries after cleanup. > 20 = still has technical fat.
- Brain #4 (Frontend) will likely fail its first cross-reference test if the pointer to Backend WS Protocol isn't ultra-clear. This failure is expected and diagnostic — it tells us exactly how much needs to be cloned.
- SYNC tag format `[SYNC: BF-NN-ID]` doubles as Phase 12 automation hook — design for future even while implementing manually now.
- Engineering Niche smoke test within Plan 10-01 is a "pre-Phase 11" — double value from the validation step.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.planning/BRAIN-FEED.md` (157 lines): the source of truth for migration. All entries classified and mapped.
- `.claude/agents/mm/` (21 files): domain feed paths locked, no modification needed.
- `tests/baselines/*.md`: QA-relevant entries (baseline anchors, delta-velocity schema) → `BRAIN-FEED-06-qa.md`

### Established Patterns
- Brain Bundle 3-file pattern (agent + criteria + warnings): domain feed is a 4th file per domain — same directory pattern
- `brain-selection.md` as single source of truth for notebook IDs: same decoupling philosophy applies to feed content ownership

### Integration Points
- All 7 agent system prompts already reference domain feed paths — Phase 10 creates the files, agents start reading them immediately
- Phase 11 smoke tests will validate feed content quality end-to-end — Phase 10 must produce feeds that Phase 11 can test

</code_context>

<deferred>
## Deferred Ideas

- **Context Proxy automation** (full implementation) — Phase 12. SYNC tags are the design hook planted in Phase 10.
- **Feed auto-pruning script** ("stale entry detection") — mentioned in Brain #1 criteria.md as a Rating 5 leverage point. Not Phase 10 scope.
- **24-brain niche expansion** (Marketing, etc.) — v3.x. Phase 10 only handles the 7 software development brains.

</deferred>

---

*Phase: 10-brain-feed-split*
*Context gathered: 2026-03-28*
