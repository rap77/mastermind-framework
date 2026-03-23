# Update BRAIN-FEED — Post-Phase Distillation

**When:** After a phase completes (SUMMARY.md files exist, UAT passing). Before `/gsd:execute-phase N+1`.

**Goal:** Extract the patterns, decisions, and anti-patterns discovered during execution and distill them into `.planning/BRAIN-FEED.md`. This is what makes Brain queries progressively better over time — each phase teaches the brains something new about your codebase.

---

## Step 1 — Read Phase Artifacts

```bash
# Read SUMMARY files for the completed phase
ls .planning/phases/NN-name/*-SUMMARY.md | xargs cat

# Read key new files created in this phase
# (check files_modified in SUMMARY.md)

# Read verification report if it exists
cat .planning/phases/NN-name/VERIFICATION.md 2>/dev/null
```

---

## Step 2 — Extract New Patterns

Ask yourself for each artifact:

**New architectural invariants?**
> "NODE_TYPES must be at module level" — this is an invariant that must never be violated.

**New proven patterns?**
> "RAF batching in the store (not in the handler) — proven at Phase 05, 60fps maintained"

**New libraries now available?**
> "DOMPurify now installed — use for all user-generated HTML sanitization"

**Anti-patterns discovered?**
> "useBrainStore() causes cascade re-renders — use useBrainState(id) instead"

**New endpoints or stores available?**
> "GET /api/brains — returns BrainConfig[], JWT required, paginated (page/page_size)"

---

## Step 3 — Update BRAIN-FEED.md

Edit `.planning/BRAIN-FEED.md`:

### Add to "Implemented Features" table

```markdown
| [Feature] | [Location] | [Notes] |
```

### Add to "Architecture Patterns" if new invariant

```markdown
### [Category]
- [Pattern description] — [why it matters / what breaks without it]
```

### Add new Phase Learnings section

```markdown
### Phase [N] — [Name]
Key discoveries:
- [Pattern 1]: [why it matters]
- [Pattern 2]: [what it replaces or prevents]
- [Anti-pattern found]: [what we tried, why it failed, what we use instead]
```

### Update "Active Constraints" if new hard limits emerged

```markdown
- **[New constraint]** — [reason from this phase]
```

### Update "Anti-patterns" table if new failures documented

---

## Step 4 — Verify Completeness

Before marking done, check:

- [ ] New libraries (added in this phase) appear in Stack table
- [ ] New proven patterns appear in Architecture Patterns
- [ ] New endpoints/stores appear in Implemented Features
- [ ] New anti-patterns documented with reason
- [ ] "Last updated" date updated at top of file

---

## Compact Distillation Rule

Don't dump everything. Ask: **"Will a brain give a better answer because of this entry?"**

| Include | Skip |
|---------|------|
| Invariants that must never be violated | Obvious things (use TypeScript types) |
| Patterns that would be reinvented | Configuration details already in code |
| Anti-patterns with failure mode | Decisions already visible in files_modified |
| New libraries and their usage | Implementation details |
| Constraints that limit brain suggestions | Solved bugs (these live in git) |

---

## Example Addition (Phase 06 → BRAIN-FEED)

```markdown
### Phase 06 — Command Center
Key discoveries:
- ICE Scoring (Impact × Confidence × Effort) prevents animation over-engineering
  Only implement animations with ICE ≥ 15. Pulse=17, Checkmark=17, Shake=18 ✅
  Glow=6, Scan=5 ✗ DEFERRED
- CLUSTER_CONFIGS data-driven array — add niches without touching BentoGrid code
- TanStack Query staleTime: 30s for brain config — it's stable, don't refetch on focus
- websocket-metrics.ts with WS_SLOS — define guardrail metrics before implementing WS features
```

---

## Done When

- [ ] BRAIN-FEED.md "Last updated" reflects this phase
- [ ] New patterns distilled (not copy-pasted — distilled)
- [ ] Next brain query will be meaningfully better because of this update
