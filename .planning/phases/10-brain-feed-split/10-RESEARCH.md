# Phase 10: BRAIN-FEED Split - Research

**Researched:** 2026-03-28
**Domain:** Knowledge architecture migration — monolithic feed to two-level ownership model
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Feeds Vacíos (#1-product, #2-ux, #7-growth)**
- Strategic Anchor approach — not empty, not full archaeology.
- Process: Archaeology of Phase 01-08 SUMMARYs → extract 3-5 Architecture Facts per domain → Brain #8 validation ("Is there a critical business decision missing that would bias this brain?") → write refined anchors.
- Max 3 "Strategic Anchors" per feed: the facts that, if missing, cause the brain to hallucinate generic responses.
- Brain #2 UX specific anchors required: "War Room = IDE, not SaaS dashboard", "4-panel layout (Command Center, Nexus, Vault, Engine Room)", "ICE Scoring ≥ 15 for animations".
- Brain #1 Product specific anchors: "Builder IS the user", "T1 reduction = ROI metric (not generic conversion)", "v2.2 — not greenfield, mature system".
- Brain #7 Growth anchors: "Delta-Velocity scale (1-5)", "T1 Profitability Threshold: > 300s = agent-unprofitable".

**Global Feed Strictness — Ownership-First**
- Global feed = EXCLUSIVELY product decisions, UX decisions, and phase milestones affecting ALL 7 brains equally.
- Zero technical entries in global, even if they affect 2 domains.
- Every technical entry has one "Owner Principal" (the brain that knows it best).
- Rule: "Which brain, if it got this wrong, would cause the biggest production failure?" → that's the owner.
- Examples: Auth & Security → Brain #5 Backend (owner). WS token handoff → Brain #5 Backend (owner), pointer in Brain #4 Frontend.
- Stack (Locked) table: stays in global — it's a product/architecture decision, not a technical pattern.
- Brain Agent Architecture section: stays in global — meta-architecture all brains need equally.
- Delta-Velocity Measurement: stays in global — cross-domain measurement framework.

**Migration Approach — Niche-Validation Loop (3 plans)**
- Plan 10-01: Engineering Niche — #4 Frontend + #5 Backend + #6 QA feeds.
- Plan 10-02: Strategy Niche — #1 Product + #2 UX + #3 UI + #7 Growth feeds.
- Plan 10-03: Global Consolidation — Cleanup of global BRAIN-FEED.md + purity linter + integrity verification script.

**Cross-Reference — Pointer Explícito + SYNC Tags (Phase 12 hook)**
- Format: `Sync: [Entry description] — [SYNC: BF-05-WS-PROTOCOL] → BRAIN-FEED-05-backend.md`
- `[SYNC: BF-NN-ID]` tag is the hook for Phase 12 Context Proxy automation.
- Do NOT create bidirectional cross-links — only the secondary consumer gets the pointer, owner file stays clean.

**Verification Protocol**
- Hash/count script (Python, idempotent): parse by bullet points (`^- `), NOT by headers. Assert set equality: `set(original_entries) == union(all_domain_entries)`.
- Path existence validation: `pathlib.Path.glob("**/*.md")` on `.claude/agents/mm/`, regex `BRAIN-FEED-\d{2}-[\w-]+\.md`, assert `path.exists()`.
- Global purity linter: word boundaries (`\bFastAPI\b`, `\bZustand\b`) — prevents false positives in Stack table rows. Verbose fail output: line number + 2-line context. Silent pass = CI-friendly.
- All three checks must pass before Plan 10-03 is marked complete.

### Claude's Discretion
- Exact format/structure of each domain feed file (headers, sections, markdown style)
- Which specific anti-patterns from the old feed go to which brain (follows classification rule mechanically)
- ID numbering scheme for SYNC tags (e.g., BF-05-001, BF-05-002, etc.)
- Whether to use Python or bash for verification scripts

### Deferred Ideas (OUT OF SCOPE)
- Context Proxy automation (full implementation) — Phase 12. SYNC tags are the design hook planted in Phase 10.
- Feed auto-pruning script — mentioned in Brain #1 criteria.md as a Rating 5 leverage point. Not Phase 10 scope.
- 24-brain niche expansion (Marketing, etc.) — v3.x. Phase 10 only handles the 7 software development brains.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FEED-01 | BRAIN-FEED split into global + per-brain: `.planning/BRAIN-FEED.md` (general) + `.planning/BRAIN-FEED-NN-domain.md` (7 files). All existing content migrated. | Ownership-First classification rule + entry inventory below + exact filename table + verification scripts |
</phase_requirements>

---

## Summary

Phase 10 is a **content migration and file creation phase** — no application code changes, no test suite modifications, no agent file modifications. The work is entirely in `.planning/`. The monolithic `BRAIN-FEED.md` (50 bullet entries + 39 table rows across 8 sections) must be split into 8 files using an Ownership-First classification rule: every entry gets exactly one owner, the global file retains only what ALL 7 brains need equally.

The critical constraint is that 21 agent files in `.claude/agents/mm/` already hardcode domain feed filenames. Those filenames are immutable — Phase 10 creates files that match them, not the other way around. One file already exists as a Phase 09 byproduct: `BRAIN-FEED-01-product.md` (contains one real post-consultation entry, NOT migrated monolith content). This distinction matters: Phase 10 creates the *initial seed content* in domain feeds, which coexists with entries the agent may have already written.

The verification system is the load-bearing safety net: three independent checks (conservation law, path existence, global purity) must all pass before Plan 10-03 is complete. The 50 bullet entry count is the ground truth baseline for the conservation assertion.

**Primary recommendation:** Create feeds in niche order (Engineering first, Strategy second, Global cleanup last) so that if the Engineering smoke test reveals an ambiguity in the ownership rule, it can be corrected before the Strategy niche content is classified.

---

## Locked File Paths (from Agent Files — Immutable)

These filenames are hardcoded in 21 agent files. Phase 10 MUST create files with exactly these names:

| Brain | Domain Feed Path | Status |
|-------|-----------------|--------|
| #1 Product | `.planning/BRAIN-FEED-01-product.md` | EXISTS (has real content from Phase 09 consultation) |
| #2 UX | `.planning/BRAIN-FEED-02-ux.md` | MISSING — Phase 10 creates |
| #3 UI | `.planning/BRAIN-FEED-03-ui.md` | MISSING — Phase 10 creates |
| #4 Frontend | `.planning/BRAIN-FEED-04-frontend.md` | MISSING — Phase 10 creates |
| #5 Backend | `.planning/BRAIN-FEED-05-backend.md` | MISSING — Phase 10 creates |
| #6 QA | `.planning/BRAIN-FEED-06-qa.md` | MISSING — Phase 10 creates |
| #7 Growth | `.planning/BRAIN-FEED-07-growth.md` | MISSING — Phase 10 creates |
| Global | `.planning/BRAIN-FEED.md` | EXISTS (to be cleaned up in Plan 10-03) |

Each agent references the domain feed in exactly TWO places in its system prompt: Step 1 read command and Step 6 write instruction. Verified across all 7 agents — the paths are consistent within each file and across all files.

---

## Entry Inventory and Classification

The monolithic `BRAIN-FEED.md` has **50 bullet entries** (parsed by `^- ` — this is the conservation baseline for the verification script). Classification follows the Ownership-First rule.

### Section: Stack (Locked) — GLOBAL (stays)
The Stack table (12 rows) stays in global. It is a product/architecture decision affecting all 7 brains equally. It is a TABLE, not a bullet entry — exempt from the 50-entry count, not subject to migration.

### Section: Architecture Patterns

**State Management (4 bullets) → BRAIN-FEED-04-frontend.md**
- `Map<brainId, BrainState>` in Zustand — O(1) lookups, Immer for immutable updates
- `useBrainState(id)` targeted selector — prevents cascade re-renders (not `useStore()`)
- RAF batching in `brainStore` (not WS handler) — queues burst events, drains before paint
- WS is a module singleton (`wsDispatcher`) — lazy init inside `connect()` action, `typeof window` guard

Reason: Brain #4 Frontend owns these. If Brain #4 gets Zustand/RAF wrong, the entire Command Center and Nexus collapse.

**Brain Agent Architecture (7 bullets) → GLOBAL (stays)**
All 7 entries stay global — this is meta-architecture that every brain needs equally:
- Brain Bundle = 3-file directory pattern
- `model: inherit` + `mcpServers: notebooklm-mcp` required
- `global-protocol.md` is governance layer
- No notebook IDs in agent files
- `BRAIN-FEED-NN-domain.md` domain split files Phase 10 creates them *(this entry becomes outdated post-Phase 10 — planner should flag for removal in Plan 10-03)*
- Brain #7 dispatched AFTER domain brains always
- Brain #7 uses `[CROSS-DOMAIN REALITY]` block

**Delta-Velocity Measurement (5 bullets) → GLOBAL (stays)**
Cross-domain measurement framework all brains reference. Stays global per locked decision.

**React Flow (5 bullets) → BRAIN-FEED-04-frontend.md**
- `NODE_TYPES` declared at module level — prevents infinite re-render loop
- `EDGE_TYPES` same rule
- dagre layout runs once via `useState` initializer
- nodes array is layout-only — brain state comes from `brainStore` directly
- React Flow CSS in `globals.css @layer base` — Tailwind 4 silently breaks handles

Reason: Brain #4 Frontend owns all React Flow patterns.

**Auth & Security (4 bullets) → BRAIN-FEED-05-backend.md**
- JWT verified at Server Components + Route Handlers (CVE-2025-29927 mitigation)
- httpOnly cookie storage — XSS defense
- WS token handoff via `/api/auth/token` endpoint
- DOMPurify + `html.escape` backend — defense in depth

Reason: Brain #5 Backend owns auth. If Brain #5 gets JWT wrong, the app has a CVE. SYNC pointer required in Brain #4 feed for the two entries Brain #4 needs operationally (httpOnly + WS handoff).

**API (2 bullets) → BRAIN-FEED-05-backend.md**
- TanStack Query Eager Loading — single query fetches all 24 brains (N+1 prevention)
- Pagination from day one: `page`, `page_size` (default 24, max 100)

Note: TanStack Query is a frontend library but the N+1 pattern is an API design decision that Brain #5 owns. Brain #4 gets a SYNC pointer for staleTime.

### Section: Implemented Features — GLOBAL (stays as table)
The Implemented Features table stays global — it's the cross-domain "what exists" reference that all brains need to prevent re-building shipped features. It is a TABLE, not a bullet entry.

### Section: Active Constraints (9 bullets)

| Entry | Owner | Reasoning |
|-------|-------|-----------|
| React Compiler: DISABLED | BRAIN-FEED-04-frontend.md | Brain #4 Frontend — if it enables React Compiler, infinite re-render loop |
| No inline NODE_TYPES | BRAIN-FEED-04-frontend.md | Brain #4 Frontend — same React Flow constraint |
| No layout recalculation on WS events | BRAIN-FEED-04-frontend.md | Brain #4 Frontend — dagre lock |
| WS updates touch only `data` prop | BRAIN-FEED-04-frontend.md | Brain #4 Frontend — topology rule |
| No `npm` or `pip` | GLOBAL | Cross-domain — every brain recommending a dependency must know this |
| Brain #7 dispatch order | GLOBAL | Cross-domain — orchestration constraint, not a domain decision |
| No notebook IDs in agent files | GLOBAL | Cross-domain — all 7 brain agents are affected equally |
| Structured output required | GLOBAL | Cross-domain — proven by baseline 04 cascade error (50s T3 penalty) |
| `uv run pytest` from `apps/api/` | BRAIN-FEED-06-qa.md | Brain #6 QA owns test infrastructure. Brain #5 gets SYNC pointer. |

### Section: Phase Learnings

**Phase 05 learnings (4 bullets)**
| Entry | Owner |
|-------|-------|
| Vitest over Jest — ESM-native | BRAIN-FEED-06-qa.md |
| `cookies()` is async in Next.js 16 | BRAIN-FEED-04-frontend.md (frontend API concern) |
| React Flow CSS in `@layer base` | BRAIN-FEED-04-frontend.md |
| Zustand RAF batching prevents dropped frames | BRAIN-FEED-04-frontend.md |

**Phase 06 learnings (4 bullets)**
| Entry | Owner |
|-------|-------|
| ICE Scoring prevents over-engineering | BRAIN-FEED-02-ux.md (UX decision framework) |
| `CLUSTER_CONFIGS` data-driven array | BRAIN-FEED-04-frontend.md (component pattern) |
| `websocket-metrics.ts` with `WS_SLOS` | BRAIN-FEED-06-qa.md (reliability metrics) |
| TanStack Query `staleTime: 30s` | BRAIN-FEED-04-frontend.md (query config) |

**Phase 09 learnings (6 bullets)**
| Entry | Owner |
|-------|-------|
| Brain Bundle invariant (3-file pattern) | GLOBAL — all brains need to author consistently |
| `[CORRECTED ASSUMPTIONS]` twice rule | GLOBAL — authoring rule for all agents |
| Output Format section non-negotiable | GLOBAL — baseline 04 cascade proof applies cross-domain |
| Brain #7 `[CROSS-DOMAIN REALITY]` distinction | GLOBAL — evaluation architecture for all brains to understand |
| Adversarial baseline delta_velocity=4 signal | BRAIN-FEED-06-qa.md + BRAIN-FEED-07-growth.md (testing benchmark + growth metric) |
| Domain feed paths intentionally broken at Phase 09 | REMOVE from global post-Phase 10 — it's self-referential, outdated once feeds exist |

### Section: Anti-patterns (10 rows as table) — SPLIT

| Anti-pattern | Owner |
|-------------|-------|
| `useStore()` for brain state | BRAIN-FEED-04-frontend.md |
| WS reconnect on every render | BRAIN-FEED-04-frontend.md |
| `jwt.verify()` from jsonwebtoken | BRAIN-FEED-05-backend.md |
| `localStorage` for JWT | BRAIN-FEED-05-backend.md (security) + SYNC in #4 |
| Inline `NODE_TYPES` in JSX | BRAIN-FEED-04-frontend.md |
| Recalculate dagre on data update | BRAIN-FEED-04-frontend.md |
| `tailwind.config.js` | BRAIN-FEED-04-frontend.md (styling system) |
| Free-text prose in brain output | GLOBAL — cross-domain authoring rule |
| Notebook IDs hardcoded in agent files | GLOBAL — agent architecture rule |
| `BRAIN-FEED-NN-domain.md` created in Phase 09 | REMOVE — outdated post-Phase 10 |
| Brain #7 dispatched in parallel | GLOBAL — orchestration rule |
| `uv run pytest` from project root | BRAIN-FEED-06-qa.md |

---

## Architecture Patterns

### Domain Feed File Structure

Every domain feed must follow this structure (Claude's Discretion — but must be consistent for Phase 11 smoke tests to parse):

```markdown
# BRAIN-FEED-NN — [Domain Name] Domain Feed

> Written by Brain #NN ([Domain Name]). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: [date]

---

## Critical Constraints (Non-Negotiable)
[For Brain #5 Backend: uv only, pytest from apps/api/, JWT in httpOnly only, WS auth pattern]
[For other brains: their domain-specific hard locks]

---

## Migrated Patterns — from BRAIN-FEED.md Phase 00-09

[Bullet entries classified as owned by this brain]

---

## SYNC Cross-References

[Pointer entries to other domain feeds — format below]

---

## [Date] — [Context] — [Consultation record if any exists]

[Any existing real consultation entries, e.g., BRAIN-FEED-01-product.md already has one]
```

**Critical Constraints section MUST appear first for Brain #5** — the CONTEXT.md specifies "Guardrail-first feed structure" because Brain #5 without these constraints defaults to Node.js patterns or root-level Python.

### SYNC Cross-Reference Format

```markdown
## SYNC Cross-References

- `[SYNC: BF-05-001]` WS token handoff protocol — Brain #5 owns. See `BRAIN-FEED-05-backend.md` > Auth & Security.
- `[SYNC: BF-05-002]` httpOnly cookie — Brain #5 owns. Frontend must NOT attempt JS cookie read. See `BRAIN-FEED-05-backend.md`.
```

ID scheme: `BF-{ownerBrainNN}-{3-digit-sequence}`. Sequence resets per owning brain. This is Claude's Discretion — but the scheme must be consistent for Phase 12 parser.

### Required SYNC Pointers per Domain Feed

Based on CONTEXT.md brain enrichment:

**BRAIN-FEED-04-frontend.md needs 4 SYNC pointers:**
- `[SYNC: BF-05-001]` — WS token handoff protocol (`/api/auth/token` handshake)
- `[SYNC: BF-05-002]` — httpOnly cookie confirmation (Frontend must NOT read via JS)
- `[SYNC: BF-05-003]` — Zod API contracts (`apps/web/src/types/api.ts`, `login/actions.ts`)
- `[SYNC: BF-05-004]` — Error response standard (500/429 shape for frontend mapping)

**BRAIN-FEED-05-backend.md needs 1 SYNC pointer:**
- `[SYNC: BF-06-001]` — `cd apps/api && uv run pytest` (Brain #6 QA owns test infrastructure)

**BRAIN-FEED-06-qa.md needs 0 SYNC pointers** (owns both test commands and baseline infrastructure)

**BRAIN-FEED-03-ui.md likely needs 1 SYNC pointer:**
- `[SYNC: BF-02-001]` — ICE Scoring ≥ 15 rule for animations (Brain #2 UX owns the decision framework, Brain #3 UI must know the threshold)

### Strategic Anchor Structure (for #1-product, #2-ux, #7-growth)

These three feeds have NO migrated entries from the monolith (no existing entries in the global feed clearly owned by them). They need archaeology-sourced Strategic Anchors:

**BRAIN-FEED-01-product.md** (already has one real consultation entry — add Strategic Anchors as a separate section):
```markdown
## Strategic Anchors — v2.2 Foundation Facts
- Builder IS the user — no external users. Optimize for developer-architect workflow, not general consumer UX.
- T1 reduction = ROI metric — pre-migration baseline: 210-270s. Agent value = further reduction, not rescue of unprofitable flows.
- v2.2 — not greenfield: 7 brain bundles authored (Phase 09), 4 War Room screens shipped (v2.1), 575+407 test baseline established.
```

**BRAIN-FEED-02-ux.md** (empty — needs full archaeology):
```markdown
## Strategic Anchors — v2.2 Foundation Facts
- War Room = IDE, not SaaS dashboard. Interaction model: developer-as-composer orchestrating agents, not consumer browsing a product.
- 4-panel layout locked (Command Center, The Nexus, Strategy Vault, Engine Room) — no panel additions without Phase N+1 PRD.
- ICE Scoring ≥ 15 for animations — proven in Phase 06. Below threshold = over-engineering.
```

**BRAIN-FEED-07-growth.md** (empty — needs full archaeology):
```markdown
## Strategic Anchors — v2.2 Foundation Facts
- Delta-Velocity scale: 1=Wrong / 2=Junior / 3=Peer / 4=Senior / 5=Principal. Target ≥ 3 = stable. ≥ 4 = profitable.
- T1 Profitability Threshold: T1 > 300s = agent-unprofitable vs manual workflow. Pre-migration baseline: 210-270s.
- Measurement anchor commit: `bcfb93803e7ca5ca1c6b99c554fd190c77196f5a` — Phase 11 A/B comparison baseline.
```

---

## Verification Scripts

### Script 1: Hash/Count Conservation Law

Parse by bullet points (`^- `), NOT headers. Headers group multiple decisions that may split across feeds.

```python
#!/usr/bin/env python3
"""
verify_feed_conservation.py
Assert: all entries from original BRAIN-FEED.md appear in exactly one domain/global feed.
BASELINE: 50 bullet entries in original file.
"""
import re
from pathlib import Path

def count_bullets(path: Path) -> set[str]:
    lines = path.read_text().splitlines()
    return {line.strip() for line in lines if line.startswith("- ")}

planning = Path(".planning")
original = count_bullets(planning / "BRAIN-FEED.md")
EXPECTED_BASELINE = 50  # verified: grep -c "^- " .planning/BRAIN-FEED.md

domain_files = [
    "BRAIN-FEED-01-product.md",
    "BRAIN-FEED-02-ux.md",
    "BRAIN-FEED-03-ui.md",
    "BRAIN-FEED-04-frontend.md",
    "BRAIN-FEED-05-backend.md",
    "BRAIN-FEED-06-qa.md",
    "BRAIN-FEED-07-growth.md",
]

all_domain = set()
for fname in domain_files:
    entries = count_bullets(planning / fname)
    overlap = all_domain & entries
    if overlap:
        print(f"DUPLICATE in {fname}: {overlap}")
        exit(1)
    all_domain |= entries

global_entries = count_bullets(planning / "BRAIN-FEED.md")
union = all_domain | global_entries

missing = original - union
extra = union - original

if missing:
    print(f"MISSING entries (lost in migration): {missing}")
    exit(1)
if extra:
    print(f"EXTRA entries (not in original): {extra}")
    exit(1)

print(f"OK: {len(original)} entries conserved across all 8 files.")
```

Key design decisions in this script:
- `set` equality instead of count equality — catches renames/rewrites of entries
- Duplicate check runs BEFORE union — catches same entry in two domain feeds
- Does not flag SYNC pointers (they start with `Sync:` not `- `) — no false positives

### Script 2: Path Existence Validation

```python
#!/usr/bin/env python3
"""
verify_feed_paths.py
Assert: every BRAIN-FEED-NN-domain.md path referenced in agent files exists on disk.
"""
import re
from pathlib import Path

agents_root = Path(".claude/agents/mm")
pattern = re.compile(r"BRAIN-FEED-\d{2}-[\w-]+\.md")
planning = Path(".planning")

referenced = set()
for md in agents_root.glob("**/*.md"):
    for match in pattern.findall(md.read_text()):
        referenced.add(match)

missing = []
for fname in referenced:
    if not (planning / fname).exists():
        missing.append(fname)

if missing:
    print(f"MISSING feed files referenced in agents: {missing}")
    exit(1)

print(f"OK: {len(referenced)} feed file references — all paths exist.")
```

Expected result after Phase 10: 7 domain feed filenames referenced, all 7 exist.

### Script 3: Global Purity Linter

```python
#!/usr/bin/env python3
"""
verify_global_purity.py
Assert: global BRAIN-FEED.md contains zero domain-specific vocabulary
(excluding Stack table — word-boundary matching prevents false positives there).
Verbose fail: line number + 2-line context.
Silent pass = CI-friendly.
"""
import re
import sys
from pathlib import Path

DOMAIN_VOCAB = [
    r"\bZustand\b", r"\bImmer\b", r"\buseBrainState\b", r"\bRAF\b",
    r"\bNODE_TYPES\b", r"\bEDGE_TYPES\b", r"\bdagre\b",
    r"\bFastAPI\b", r"\bSQLAlchemy\b", r"\basicoio\b", r"\bpytest\b",
    r"\bpydantic\b", r"\bVitest\b", r"\buv run\b",
    r"\bTanStack\b", r"\bReact Flow\b", r"\b@xyflow\b",
]

# Stack table rows are exempt — they appear in the ## Stack (Locked) section
# Word boundaries handle the Stack table correctly for most terms (e.g., "Zustand | 5.x" still matches \bZustand\b)
# Exception: if Stack table rows need exempting, skip lines starting with "|"

feed = Path(".planning/BRAIN-FEED.md")
lines = feed.read_text().splitlines()
failures = []

for i, line in enumerate(lines):
    if line.strip().startswith("|"):  # skip table rows (Stack table exemption)
        continue
    for vocab_pattern in DOMAIN_VOCAB:
        if re.search(vocab_pattern, line, re.IGNORECASE):
            ctx_start = max(0, i - 1)
            ctx_end = min(len(lines), i + 2)
            failures.append({
                "line": i + 1,
                "match": vocab_pattern,
                "content": line,
                "context": lines[ctx_start:ctx_end],
            })
            break  # one report per line is enough

if failures:
    print(f"PURITY FAIL: {len(failures)} domain-vocabulary match(es) in global BRAIN-FEED.md\n")
    for f in failures:
        print(f"  Line {f['line']}: {f['content']}")
        print(f"  Pattern: {f['match']}")
        print(f"  Context:")
        for ctx_line in f['context']:
            print(f"    {ctx_line}")
        print()
    sys.exit(1)

# Silent pass — no output
```

---

## Architecture Patterns — Domain Feed Classification Rules

| Question | Answer → Owner |
|----------|---------------|
| If Brain #NN gets this wrong, does it cause a production runtime failure? | → Brain #NN (domain owner) |
| Does this entry affect the way all 7 brains must structure their outputs? | → GLOBAL |
| Is this an architecture/stack decision that gates ALL development? | → GLOBAL |
| Is this a "how to do X in our stack" implementation detail? | → Domain brain most likely to implement X |
| Is this a cross-domain measurement/metric framework? | → GLOBAL |

### Entries to REMOVE entirely (not migrate)
- `BRAIN-FEED-NN-domain.md` domain split files do NOT exist yet — Phase 10 creates them (line 44, Architecture section) → **outdated once Phase 10 completes, remove in Plan 10-03**
- `BRAIN-FEED-NN-domain.md` created in Phase 09 (Premature — empty files are noise) anti-pattern row → **same reason, remove in Plan 10-03**

These 2 entries are self-referential Phase 09 notes. They are NOT migrated to domain feeds. They are removed from global. This is the only case where `original_count - removed_count == new_union_count` must be adjusted — document in the verification script as a known delta.

**Revised conservation law:** `len(original) - 2 == len(global_after_cleanup) + len(all_domain_feeds)` — the 2 removed entries are legitimate deletions, not losses.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Entry deduplication across 8 files | Custom hash algorithm | Python `set()` equality | Sets handle identical strings — no hash collisions, no custom equality |
| Path discovery in agent files | Manual file reading loop | `pathlib.glob("**/*.md")` + regex | Single call discovers all 21 agent files including nested directories |
| Global purity checking | Manual grep with false positive risk | Word boundaries `\b` + skip table rows | Prevents `\bZustand\b` from matching in the Stack table row `| State | Zustand | 5.x |` |
| Feed file headers | Inventing structure from scratch | Mirror existing `BRAIN-FEED-01-product.md` header pattern | Consistency for Phase 11 parser, already established precedent |

---

## Common Pitfalls

### Pitfall 1: BRAIN-FEED-01-product.md Already Exists
**What goes wrong:** Overwriting it during migration destroys the real consultation record from Phase 09.
**Why it happens:** Phase 10 "creates domain feeds" — could be interpreted as creating all 7 from scratch.
**How to avoid:** BRAIN-FEED-01-product.md already has a real entry (2026-03-28 notification system consultation). Add Strategic Anchors as a NEW section above or below, do NOT overwrite or replace the file.
**Warning signs:** If the write operation doesn't use an append or section-add approach, it will destroy existing content.

### Pitfall 2: Conservation Count Off by 2 (Stale Entry Removal)
**What goes wrong:** The verification script reports 2 "missing" entries that were intentionally deleted.
**Why it happens:** Two anti-pattern entries are self-referential Phase 09 notes that should be removed, not migrated.
**How to avoid:** Document the 2 intentional deletions in the verification script as a known delta. Adjust assertion: `len(union) == len(original) - 2`.
**Warning signs:** Script fails with `MISSING entries: {'BRAIN-FEED-NN-domain.md domain split files...' }`.

### Pitfall 3: SYNC Pointer Format Inconsistency
**What goes wrong:** Phase 12 Context Proxy parser breaks because SYNC tags are formatted differently across feeds.
**Why it happens:** Each plan writes its own SYNC pointers without a template.
**How to avoid:** Establish the format in Plan 10-01 (Engineering), lock it, carry it forward to Plan 10-02 (Strategy). Format: `- \`[SYNC: BF-{NN}-{3-digit}]\` Description — See BRAIN-FEED-{NN}-{domain}.md`.
**Warning signs:** SYNC tags in different plans use different bracket styles, different ID formats, or missing canonical file references.

### Pitfall 4: Global Feed Retains Delta-Velocity Measurement — Is That Correct?
**What goes wrong:** Treating Delta-Velocity as a Brain #7 Growth domain entry and migrating it out of global.
**Why it happens:** Delta-Velocity = Growth domain vocabulary → seems like it belongs to Brain #7.
**How to avoid:** The locked decision is explicit: "Delta-Velocity Measurement: stays in global — cross-domain measurement framework." Brain #7 gets Strategic Anchors for the scale, but the scale itself stays in global because ALL brains are rated on it.
**Warning signs:** Purity linter triggers on "Delta-Velocity" — but Delta-Velocity is NOT in the domain vocabulary list (it's cross-domain). Do not add Delta-Velocity to the purity linter's vocabulary.

### Pitfall 5: Brain #4 Smoke Test Failure is Expected
**What goes wrong:** Engineer sees Brain #4 failing to explain Auth from its new feed and treats this as a Phase 10 bug.
**Why it happens:** CONTEXT.md explicitly states: "Brain #4 expected to fail first cross-reference smoke test if the pointer to Backend WS Protocol isn't ultra-clear. This failure is expected and diagnostic."
**How to avoid:** Plan 10-01 must include a step to run the Engineering Niche smoke test. The expected outcome is: Brain #4 reads its feed, hits the SYNC pointer for WS Auth, navigates to BRAIN-FEED-05-backend.md, and succeeds. If it fails, the SYNC pointer text was insufficient — rewrite it and document the required clarity level.
**Warning signs:** Engineer skips the smoke test step or marks it complete without running it.

### Pitfall 6: TanStack Query Entry Ownership Confusion
**What goes wrong:** `TanStack Query Eager Loading` entry migrated to BRAIN-FEED-04-frontend.md because TanStack Query is a frontend library.
**Why it happens:** Library lives in `apps/web/` → feels like a frontend concern.
**How to avoid:** The N+1 prevention pattern is an API design decision. Brain #5 Backend owns it because if Brain #5 designs the `/api/brains` endpoint without considering N+1, the frontend optimization doesn't help. BRAIN-FEED-05-backend.md gets the entry. BRAIN-FEED-04-frontend.md gets a SYNC pointer for the `staleTime: 30s` config value.

---

## Code Examples

### Running All Three Verification Scripts

```bash
# Run from project root
cd /home/rpadron/proy/mastermind

# Script placement (Claude's Discretion — but .planning/ is the logical home)
python3 .planning/verify_feed_conservation.py
python3 .planning/verify_feed_paths.py
python3 .planning/verify_global_purity.py
```

All three must exit 0 before Plan 10-03 is complete.

### Global Feed Post-Cleanup Target Structure

After Plan 10-03, `BRAIN-FEED.md` should contain ONLY:
1. Stack (Locked) table — 12 rows
2. Brain Agent Architecture — 5-6 bullets (removing the 2 stale Phase 09 self-referential entries)
3. Delta-Velocity Measurement — 5 bullets
4. Implemented Features table — as-is
5. Active Constraints — 4 bullets: `No npm/pip`, Brain #7 dispatch order, No notebook IDs, Structured output required
6. Phase Learnings — Phase 09 global entries only (Brain Bundle invariant, `[CORRECTED ASSUMPTIONS]` twice rule, Output Format non-negotiable, Brain #7 `[CROSS-DOMAIN REALITY]` distinction)
7. Anti-patterns — 3 table rows: Free-text prose, Notebook IDs hardcoded, Brain #7 parallel dispatch

**Target global bullet count after cleanup: ~16 entries** (within the < 20 target).

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python 3 scripts (no framework dependency — pure stdlib) |
| Config file | none — scripts are standalone `.planning/*.py` files |
| Quick run command | `python3 .planning/verify_feed_paths.py` |
| Full suite command | `python3 .planning/verify_feed_conservation.py && python3 .planning/verify_feed_paths.py && python3 .planning/verify_global_purity.py` |
| Existing test suites (unchanged) | `cd apps/api && uv run pytest` (575) + `pnpm --prefix apps/web test run` (407) |

**The existing 575 backend + 407 frontend test suites are NOT affected by Phase 10.** Phase 10 creates only `.planning/*.md` files and `.planning/*.py` scripts. Zero application code changes.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FEED-01 | All 8 feed files exist | path existence | `python3 .planning/verify_feed_paths.py` | ❌ Wave 0 |
| FEED-01 | No entry lost or duplicated in migration | conservation | `python3 .planning/verify_feed_conservation.py` | ❌ Wave 0 |
| FEED-01 | Global feed has zero domain vocabulary | purity | `python3 .planning/verify_global_purity.py` | ❌ Wave 0 |
| FEED-01 | Engineering smoke: Brain #4 explains Auth from its feed | manual smoke | dispatch Brain #4 with Auth question post-migration | N/A — manual |
| FEED-01 | Agent file paths match created filenames | cross-check | `python3 .planning/verify_feed_paths.py` (same script) | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python3 .planning/verify_feed_paths.py` (fastest check — path existence)
- **Per wave merge:** Full suite: `python3 .planning/verify_feed_conservation.py && python3 .planning/verify_feed_paths.py && python3 .planning/verify_global_purity.py`
- **Phase gate:** All 3 scripts green + Engineering Niche smoke test completed (even if Brain #4 required SYNC pointer rewrite) before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `.planning/verify_feed_conservation.py` — covers FEED-01 conservation law
- [ ] `.planning/verify_feed_paths.py` — covers FEED-01 path existence
- [ ] `.planning/verify_global_purity.py` — covers FEED-01 global purity

*(No framework install needed — pure Python stdlib: `re`, `pathlib`, `sys`)*

### Engineering Niche Smoke Test (Plan 10-01 internal)

This is a manual test embedded within Plan 10-01 (not a separate plan):
1. After BRAIN-FEED-04-frontend.md, BRAIN-FEED-05-backend.md, and BRAIN-FEED-06-qa.md are created
2. Ask Brain #4 a question that requires Auth knowledge: "What is the WS token handoff sequence?"
3. Expected: Brain #4 reads its feed, finds `[SYNC: BF-05-001]`, reads BRAIN-FEED-05-backend.md Auth section, returns correct `/api/auth/token` sequence
4. Failure signal: Brain #4 hallucinations (says "localStorage" or invents a custom auth endpoint) → rewrite SYNC pointer to be more explicit about what information to extract
5. This failure is diagnostic, not blocking — document what was insufficient, fix, proceed to Plan 10-02

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Monolithic BRAIN-FEED.md (all 50 entries + tables) | Two-level: global (cross-domain) + 7 domain feeds | Phase 10 (now) | Brains read 2 targeted files instead of 1 sprawling document — T1 reduction |
| Phase 09: domain feed paths broken (files don't exist) | Phase 10: files created, agents start reading domain feeds immediately | Phase 10 (now) | All 21 agent file references become valid — no more fallback to STATE.md |
| Single ownership ambiguity (Auth lives in global) | Ownership-First: Brain #5 Backend owns Auth, Brain #4 gets SYNC pointer | Phase 10 (now) | Eliminates "which feed has the answer" ambiguity in multi-brain queries |

**Obsolete/will become outdated after Phase 10:**
- Anti-pattern row: `BRAIN-FEED-NN-domain.md created in Phase 09 (Premature)` → remove from global (self-referential)
- Architecture Pattern bullet: `BRAIN-FEED-NN-domain.md domain split files do NOT exist yet` → remove from global (false after Phase 10)

---

## Open Questions

1. **BRAIN-FEED-03-ui.md seed content**
   - What we know: No entries in the monolith are clearly Brain #3 UI-owned. ICE Scoring ≥ 15 migrates from Phase 06 learnings (it's a UX rule from Brain #2, but Brain #3 needs to know it). CLUSTER_CONFIGS data-driven pattern is a component architecture decision.
   - What's unclear: Does Brain #3 UI need archaeology of Phase 07-08 (Strategy Vault, Engine Room styling) to have meaningful seed content beyond the SYNC pointer?
   - Recommendation: Give Brain #3 the ICE Scoring SYNC pointer + the CLUSTER_CONFIGS entry. If Phase 07-08 learnings are not distilled yet (BRAIN-FEED.md explicitly notes this gap), note it in the feed as `⚠️ Gap: Phase 07-08 UI learnings not yet distilled — see git history`.

2. **Conservation law with 2 intentional deletions**
   - What we know: 2 stale entries should be removed (not migrated), making the conservation count `N-2` not `N`.
   - What's unclear: Should the verification script hard-code the expected count (48) or accept a deletion manifest?
   - Recommendation: Hard-code `KNOWN_DELETIONS = 2` in the script with an explicit comment listing the deleted entries. Avoids a generic "deletion manifest" mechanism that adds complexity for a one-time operation.

3. **BRAIN-FEED-01-product.md write strategy**
   - What we know: File already exists with one real consultation entry. Strategic Anchors need to be added.
   - What's unclear: Should Strategic Anchors go before or after the existing consultation entry?
   - Recommendation: Strategic Anchors go BEFORE the consultation entries — they are "seed knowledge" that pre-dates any specific consultation. Header: `## Strategic Anchors — v2.2 Foundation Facts`. Existing entry section: `## [Date] — [Context]` (unchanged).

---

## Sources

### Primary (HIGH confidence)
- Direct file reads: `.planning/BRAIN-FEED.md` — full 158-line inventory, 50 bullet entries counted
- Direct file reads: `.claude/agents/mm/brain-{01..07}-{domain}/{brain-file}.md` — all 7 system prompts, BRAIN-FEED paths verified
- Direct file reads: `.claude/agents/mm/global-protocol.md` — Feed Write Scope section confirmed
- Direct file reads: `.planning/phases/10-brain-feed-split/10-CONTEXT.md` — all locked decisions
- Direct file reads: `.planning/REQUIREMENTS.md` — FEED-01 acceptance criteria
- Bash: `grep -c "^- " BRAIN-FEED.md` → 50 (verified baseline for conservation script)
- Bash: `grep -n "BRAIN-FEED" all 7 agent files` → exact paths with line numbers confirmed

### Secondary (MEDIUM confidence)
- Inferred from CONTEXT.md brain enrichment: SYNC pointer count and content for Brain #4 Frontend (4 pointers specified) and Brain #5 Backend (1 pointer to QA)

### Tertiary (LOW confidence)
- Brain #3 UI seed content: not explicitly specified in CONTEXT.md — inferred from classification rules and ICE Scoring entry origin

---

## Metadata

**Confidence breakdown:**
- Locked file paths: HIGH — verified directly from 21 agent files with line numbers
- Entry classification: HIGH — CONTEXT.md provides explicit ownership rules + brain enrichment section maps most entries
- Verification scripts: HIGH — logic is simple Python stdlib, no external dependencies
- Strategic Anchors content: HIGH — exact text specified in CONTEXT.md for #1, #2, #7
- Brain #3 UI seed content: MEDIUM — inferred, not explicitly specified
- SYNC pointer IDs: MEDIUM — format specified, sequence numbers are Claude's Discretion

**Research date:** 2026-03-28
**Valid until:** 2026-04-28 (30 days — stable domain, no external dependencies)
