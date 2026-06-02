# Design — mm-harness-context-intake-and-canonicalization

## Architecture / Boundaries

This objective touches the **intake boundary** of the harness, not the execution
boundary.

### 1. Intake command

Source of truth:
- `.mm-flow/commands/mm/context-to-canonical-handler.py`

Responsibility:
- inspect repository context
- accept explicit user intent
- optionally ask structured questions
- produce canonical outputs

### 2. Structured output contract

Produced artifacts:
- markdown canonical doc
- machine-readable intake report (JSON)

Responsibility:
- let downstream tools understand what is known vs inferred
- give `discover` and the future `objective-context-check` a stable upstream
  contract

### 3. Future validation gate

Not implemented here, but explicitly prepared for:
- `objective-context-check`

Responsibility:
- evaluate whether the canonical objective is specific enough to materialize into
  an execution package

## Technical Approach

### Step 1 — define the input contract

`context-to-canonical` should support a normalized intake shape covering:

- `type`
- `name`
- `intent`
- `target`
- optional user-supplied context
- optional suspected paths / focus areas
- optional constraints

At minimum, T2 should make the command emit and consume that structure clearly.

### Step 2 — define the output contract

Canonical generation should produce:

1. markdown output for humans
2. a JSON report with fields such as:
   - `schema_version`
   - `doc_type`
   - `intent`
   - `context_sources`
   - `evidence`
   - `assumptions`
   - `gaps_detected`
   - `questions_asked`
   - `questions_unanswered`
   - `confidence`
   - `generated_files`

### Step 3 — structured interview fallback

When the repo context is insufficient, the intake layer should not guess
silently. It should support a structured interview path that can ask targeted
questions for:

- feature work
- bugfixes
- refactors
- harness/capability work

### Step 4 — code-aware context gathering

For objective generation, the command should inspect repo evidence before
writing a canonical spec:

- nearby modules
- canonical docs
- existing planning packages
- active architectural boundaries

This should remain lightweight and additive; it should not become a full
discovery replacement.

## Dependencies

- existing `context-to-canonical-handler.py`
- canonical asset templates already bundled in `.mm-flow/assets/canonical/`
- existing `discover` flow as downstream consumer

## Validation Strategy

Required checks for this objective should become concrete:

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 .mm-flow/commands/mm/context-to-canonical-handler.py --help
python3 .mm-flow/commands/mm/context-to-canonical-handler.py --type objective --name "Add OAuth login" --payload-only
```

If JSON report output is introduced in T2, add a validation that verifies:
- report file exists
- expected keys are present

## Important Tradeoffs

- **Interview richness vs simplicity:** enough structure to fill gaps, but not so
  much that the command becomes a wizard for every case
- **Code-aware audit vs discovery overlap:** gather enough evidence to improve
  canonical quality without duplicating `discover`
- **Markdown readability vs JSON structure:** both are needed because humans and
  tools consume different surfaces
- **Immediate implementation vs future gate prep:** this objective should improve
  the intake layer and reserve a clean contract for `objective-context-check`,
  not implement every downstream behavior at once

## Files / Areas Likely Touched

- `.mm-flow/commands/mm/context-to-canonical-handler.py`
- `.mm-flow/commands/mm/context-to-canonical.md`
- `.mm-flow/assets/canonical/**` (only if templates/examples need alignment)
- `.mm-flow/README.md`
- tests around canonical generation / objective packaging
