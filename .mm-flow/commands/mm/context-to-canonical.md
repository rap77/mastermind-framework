---
name: mm:context-to-canonical
description: Generate a filled canonical document from an existing project's context.
argument-hint: "[--type project-adapter] [--target PATH] [--output PATH]"
---

# /mm:context-to-canonical

Scan an existing project, collect its real context (README, CLAUDE.md, docs, stack, git log), and generate a populated canonical document — not a blank template, actual content synthesized from what the project already has.

## Supported document types

- `project-adapter` (default) — fills `PROJECT-ADAPTER-TEMPLATE.md` with the project's real context

## Usage

```bash
/mm:context-to-canonical
/mm:context-to-canonical --type project-adapter
/mm:context-to-canonical --target /path/to/project
/mm:context-to-canonical --target /path/to/project --output /path/to/output.md
```

## Protocol (For Assistant)

When user executes `/mm:context-to-canonical [options]`:

### Step 1: Run the handler

```bash
python3 .claude/commands/mm/context-to-canonical-handler.py [options]
```

Run from the **project root** where MasterMind is installed.

### Step 2: Parse handler output

Look for:
- `PAYLOAD: {...}` — JSON payload for the agent
- `LAUNCH: canonical-writer` — launch the canonical-writer agent
- `ERROR: ...` — show to user and stop

### Step 3: Launch canonical-writer agent

If `LAUNCH: canonical-writer` is present:

```
Agent(
  subagent_type="claude",
  prompt="""
## Canonical Writer Task

{parsed_payload_json}

Read the project context in the payload and write the canonical document.
Follow the canonical-writer agent protocol exactly.
""",
  run_in_background=false
)
```

Run **foreground** — the output file path is needed before reporting to user.

### Step 4: Report to user

```
✅ Canonical document generated
📄 {output_path}
```

## What the agent produces

A fully populated canonical document at `docs/canonical/project-adapter/<project-slug>.md` (or the `--output` path) with every section filled from real project context — not placeholder text.
