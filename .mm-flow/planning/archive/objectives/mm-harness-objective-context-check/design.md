# Design — mm-harness-objective-context-check

## Architecture / Boundaries

This objective adds the **validation gate** between intake and discovery.

### 1. Upstream input

Produced by the previous harness objective:

- canonical markdown under `docs/canonical/objective-specs/<slug>.md`
- sidecar report `docs/canonical/objective-specs/<slug>.json`

### 2. New gate

Source of truth:
- `.mm-flow/commands/mm/objective-context-check-handler.py` *(new)*

Responsibility:
- resolve the target objective canonical
- load markdown + intake report
- evaluate readiness before `discover`
- print structured status and actionable reasons

### 3. Downstream consumer

- `discover`

Responsibility:
- still materializes packages
- but now has a formal upstream readiness gate available

## Technical Approach

### Step 1 — target resolution

The handler should accept either:

- `--objective <slug>`
- `--path <path-to-objective-md>`

Resolution rules:

- if `--path` is given, use it directly
- else resolve:
  - `docs/canonical/objective-specs/<slug>.md`
  - sidecar JSON at the same basename

### Step 2 — deterministic checks

The first implementation should validate at least:

- canonical markdown file exists
- sidecar JSON exists
- JSON parses successfully
- required report keys exist:
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
- markdown still contains the objective marker:
  - `<!-- mm:objective-spec ... -->`

### Step 3 — readiness decision

Suggested first-pass policy:

- `FAILED`
  - required files missing
  - malformed JSON
  - missing required keys
  - wrong `doc_type`

- `NEEDS_INPUT`
  - `questions_unanswered` non-empty
  - severe context gaps remain
  - confidence too low for packaging

- `PASSED`
  - files and keys are valid
  - no outstanding required questions
  - gaps are acceptable for packaging

### Step 4 — output contract

The command should print:

- `STATUS: PASSED|FAILED|NEEDS_INPUT`
- resolved canonical path
- resolved report path
- summarized gaps/reasons
- suggested next command:
  - `discover --roadmap --existing`
  - or “answer interview questions first”

## Dependencies

- `.mm-flow/commands/mm/context-to-canonical-handler.py`
- objective spec markdown convention
- intake report JSON contract from the archived intake objective

## Validation Strategy

Concrete validations for this objective should include:

```bash
python3 .mm-flow/commands/mm/objective-context-check-handler.py --help
python3 .mm-flow/commands/mm/objective-context-check-handler.py --objective add-oauth-login
python3 -m unittest tests.unit.test_mm_discover_workflow
```

Need at least one test each for:

- `PASSED`
- `FAILED`
- `NEEDS_INPUT`

## Important Tradeoffs

- **Strictness vs usefulness:** too strict blocks useful discovery; too lax adds no value
- **Deterministic checks vs semantic judging:** start with deterministic contract validation first
- **Slug resolution vs explicit path:** both matter because humans and automation use different entrypoints
- **Standalone gate vs discover coupling:** keep the first implementation standalone; integrate more deeply later if needed

## Files / Areas Likely Touched

- `.mm-flow/commands/mm/objective-context-check-handler.py` *(new)*
- `.mm-flow/commands/mm/objective-context-check.md` *(new)*
- `.mm-flow/README.md`
- tests for readiness decision cases
