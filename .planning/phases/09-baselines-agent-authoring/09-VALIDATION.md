---
phase: 09
slug: baselines-agent-authoring
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-28
---

# Phase 09 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | No automated test framework — Phase 09 produces documentation/config files only |
| **Config file** | N/A |
| **Quick run command** | Structural checks (file existence + content grep) |
| **Full suite command** | `uv run pytest apps/api/ -x -q` + `pnpm --prefix apps/web test run` (regression only) |
| **Estimated runtime** | ~5 seconds (structural) + ~120 seconds (full regression) |

---

## Sampling Rate

- **After every task commit:** Structural check for that task's output file (grep/ls)
- **After every plan wave:** All structural checks above + full regression suite
- **Before `/gsd:verify-work`:** All structural checks green + git timestamp order verified
- **Max feedback latency:** ~5 seconds (structural), ~120 seconds (regression)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 09-W0-schema | W0 | 0 | BASE-02 | structural | `grep -c "context_id\|T1_setup_seconds\|delta_velocity_score" tests/baselines/baseline-schema.md` (expect >= 3) | ❌ W0 | ⬜ pending |
| 09-W0-b1 | W0 | 0 | BASE-01 | structural | `ls tests/baselines/baseline-01*.md` | ❌ W0 | ⬜ pending |
| 09-W0-b2 | W0 | 0 | BASE-01 | structural | `ls tests/baselines/baseline-02*.md` | ❌ W0 | ⬜ pending |
| 09-W0-b3 | W0 | 0 | BASE-01 | structural | `ls tests/baselines/baseline-03*.md` | ❌ W0 | ⬜ pending |
| 09-W0-b4 | W0 | 0 | BASE-01 | structural | `ls tests/baselines/baseline-04*.md` | ❌ W0 | ⬜ pending |
| 09-W0-b5 | W0 | 0 | BASE-01 | structural | `ls tests/baselines/baseline-05*.md` | ❌ W0 | ⬜ pending |
| 09-W0-count | W0 | 0 | BASE-01 | structural | `ls tests/baselines/baseline-0*.md \| wc -l` (expect 5) | ❌ W0 | ⬜ pending |
| 09-W1-protocol | W1 | 1 | AGT-01 | structural | `ls .claude/agents/mm/global-protocol.md` | ❌ W1 | ⬜ pending |
| 09-W1-agents | W1+ | 1 | AGT-01 | structural | `find .claude/agents/mm -name "brain-0*.md" \| wc -l` (expect 7) | ❌ W1 | ⬜ pending |
| 09-W1-criteria | W1+ | 1 | AGT-02 | structural | `find .claude/agents/mm -name "criteria.md" \| wc -l` (expect 7) | ❌ W1 | ⬜ pending |
| 09-W1-warnings | W1+ | 1 | AGT-03 | structural | `find .claude/agents/mm -name "warnings.md" \| wc -l` (expect 7) | ❌ W1 | ⬜ pending |
| 09-W1-feed2 | W1+ | 1 | FEED-02 | structural | `grep -l "BRAIN-FEED.md" .claude/agents/mm/brain-*/brain-*.md \| wc -l` (expect 7) | ❌ W1 | ⬜ pending |
| 09-W1-feed3 | W1+ | 1 | FEED-03 | structural | `grep -l "BRAIN-FEED-.*-" .claude/agents/mm/brain-*/brain-*.md \| wc -l` (expect 7) | ❌ W1 | ⬜ pending |
| 09-timestamp | ALL | gate | BASE-01 | git | `git log --diff-filter=A --name-only --format="" -- "tests/baselines/*.md" ".claude/agents/mm/**/*.md"` (baselines first) | manual | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/baselines/` directory — does not exist yet
- [ ] `tests/baselines/baseline-schema.md` — schema spec covering BASE-02 (all required fields)
- [ ] `tests/baselines/baseline-01-frontend-single.md` — BASE-01 baseline #1
- [ ] `tests/baselines/baseline-02-backend-api.md` — BASE-01 baseline #2
- [ ] `tests/baselines/baseline-03-frontend-adversarial.md` — BASE-01 baseline #3
- [ ] `tests/baselines/baseline-04-backend-adversarial.md` — BASE-01 baseline #4
- [ ] `tests/baselines/baseline-05-multibrain-e2e.md` — BASE-01 baseline #5

*These 6 files must be committed BEFORE any `.claude/agents/mm/` file — git timestamp is the compliance proof.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Baseline files predate agent files in git history | BASE-01 | Git timestamp is ground truth — cannot automate ordering check without custom script | Run `git log --diff-filter=A --name-only --format="%ai %s" -- "tests/baselines/*.md" ".claude/agents/mm/**/*.md"` and verify baseline dates < agent dates |
| Each agent frontmatter has valid `name`, `description`, `model: inherit`, `tools`, `mcpServers` | AGT-01 | YAML parsing requires human judgment on field completeness | Open each brain-NN.md and verify frontmatter fields against spec |
| Each brain's criteria.md has domain-specific (not generic) quality gate | AGT-02 | Content quality is subjective — requires human review | Compare Rating 3 vs Rating 4 descriptions in criteria.md against CONTEXT.md spec |
| Each brain's warnings.md has rejection cases from real poisoning examples | AGT-03 | Content quality requires human review | Verify all 4 warning patterns (Stack Hallucination, Toil-Inducer, Security Bypass, Legacy Drift) appear |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s (structural), < 120s (regression)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
