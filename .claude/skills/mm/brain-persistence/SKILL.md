# MasterMind Brain Context Persistence Protocol

**Purpose:** Ensure brain consultation outputs are NEVER lost between sessions.

**Problem:** Brain outputs generated during sessions were lost because:
1. Files were created in .planning/phases/ but not committed to git
2. Only session summaries were saved to Serena memory
3. Full brain outputs exist only in NotebookLM (not in codebase)

**Solution:** Triple persistence strategy

---

## Persistence Protocol

### Layer 1: File System (Immediate)

**When:** After each brain consultation completes

**What to save:**
```
.planning/phases/{PHASE}/
├── BRAIN-{BRAIN_ID}-CONTEXT.md       # Full brain output
├── BRAIN-{BRAIN_ID}-SUMMARY.md       # Key insights (1-2 pages)
└── BRAIN-{BRAIN_ID}-RAW.md           # Raw NotebookLM output
```

**How:**
```bash
# Immediately after brain returns output
cat > .planning/phases/06-command-center/BRAIN-02-UX-CONTEXT.md << 'EOF'
# brain-02 Output
[Full brain response here]
EOF
```

### Layer 2: Git Commit (After Momento 2)

**When:** After all technical brains consulted (Momento 2 complete)

**What to commit:**
```bash
git add .planning/phases/06-command-center/BRAIN-*-CONTEXT.md
git add .planning/phases/06-command-center/BRAIN-*-SUMMARY.md
git commit -m "docs(phase-06): add brain consultation outputs (Momento 2)"
```

### Layer 3: Serena Memory (Checkpoint)

**When:** After Momento 3 (brain-07 evaluation)

**What to save:**
```bash
# Save checkpoint memory
mcp__serena__write_memory(
  memory_name="session/2026-03-20-phase06-momento2-complete",
  content="# Session checkpoint\n\n## Brains Consulted\n- brain-02: BRAIN-02-UX-CONTEXT.md\n- brain-04: BRAIN-04-FRONTEND-CONTEXT.md\n- brain-05: BRAIN-05-BACKEND-CONTEXT.md\n- brain-06: BRAIN-06-QA-CONTEXT.md\n\n## Key Decisions\n[Summarize key decisions]"
)
```

---

## File Naming Convention

```
BRAIN-{XX}-{DOMAIN}-{TYPE}.md

Where:
- XX: brain number (02, 04, 05, 06, 07)
- DOMAIN: ux, frontend, backend, qa, growth
- TYPE: CONTEXT (full), SUMMARY (key insights), EVALUATION (brain-07)
```

Examples:
- BRAIN-02-UX-CONTEXT.md
- BRAIN-04-FRONTEND-CONTEXT.md
- BRAIN-05-BACKEND-CONTEXT.md
- BRAIN-06-QA-CONTEXT.md
- BRAIN-07-EVALUATION.md

---

## Recovery Checklist

If brain outputs are lost:

1. **Check Serena memories:** `mcp__serena__list_memories topic=session`
2. **Check git commits:** `git log --all --grep="brain" --name-only`
3. **Check NotebookLM:** All brains are persistent notebooks
4. **Reconstruct from memory:** Use session summaries as source

---

## Momento Workflow

```
Momento 1: discuss-phase
  → Creates 06-CONTEXT.md
  → Commit immediately

Momento 2: Brain Consultation
  → Consult 4 technical brains
  → Save each output to BRAIN-XX-CONTEXT.md
  → Create BRAIN-XX-SUMMARY.md (key insights)
  → Git commit all files
  → Save Serena memory checkpoint

Momento 3: Brain-07 Evaluation
  → brain-07 evaluates CONTEXT + all BRAIN-XX files
  → Save BRAIN-07-EVALUATION.md
  → If REJECT → iterate
  → If APPROVE → proceed to plan-phase
  → Git commit + Serena memory
```

---

## Prevention Rules

**RULE 1:** Never `/clear` after brain consultation without:
- [ ] Files saved to .planning/phases/
- [ ] Git commit completed
- [ ] Serena memory saved

**RULE 2:** Brain outputs must be saved in 3 places:
- [ ] File system (immediate)
- [ ] Git (after Momento 2)
- [ ] Serena memory (checkpoint)

**RULE 3:** Each brain consultation must produce:
- [ ] BRAIN-XX-CONTEXT.md (full output)
- [ ] BRAIN-XX-SUMMARY.md (1-2 page summary)
- [ ] BRAIN-XX-RAW.md (optional, raw NotebookLM)

---

## Implementation

Add to CLAUDE.md or project-specific instructions:

```markdown
## Brain Consultation Protocol

When consulting brains for phase planning:

1. **Save immediately:** Each brain output → BRAIN-XX-CONTEXT.md
2. **Git commit:** After Momento 2, commit all BRAIN-* files
3. **Serena memory:** Save checkpoint with list of files
4. **Never /clear** until all 3 layers complete

This ensures brain outputs are never lost between sessions.
```

---

*Protocol created: 2026-03-20*
*Reason: Session 2026-03-20-phase06 lost brain outputs*
