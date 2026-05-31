---
name: mm:context-to-canonical
description: Generate a canonical document draft from an existing project's context.
argument-hint: "[--type project-adapter] [--target PATH] [--output PATH]"
---

# /mm:context-to-canonical

Scan an existing project, collect its real context (README, CLAUDE.md, docs, stack, git log), and generate a populated canonical document draft — not a blank template, actual content synthesized from what the project already has.

## Supported document types

- `project-adapter` (default) — fills `PROJECT-ADAPTER-TEMPLATE.md` with the project's real context
- `objective` — fills `OBJECTIVE-SPEC-TEMPLATE.md` from project context + stated intent; output is picked up by `/mm:discover --roadmap --existing`

## Usage

```bash
# Project profile (default)
python3 .mm-flow/commands/mm/context-to-canonical-handler.py
python3 .mm-flow/commands/mm/context-to-canonical-handler.py --type project-adapter

# New objective spec — creates docs/canonical/objective-specs/<slug>.md
python3 .mm-flow/commands/mm/context-to-canonical-handler.py --type objective --name "Add OAuth login"
python3 .mm-flow/commands/mm/context-to-canonical-handler.py --type objective --name "Fix N+1 query in task list" --intent bugfix
python3 .mm-flow/commands/mm/context-to-canonical-handler.py --type objective --name "Migrate to Postgres" --intent capability

# Custom target / output
python3 .mm-flow/commands/mm/context-to-canonical-handler.py --target /path/to/project --output /path/to/output.md
```

If your runtime exposes slash commands, `/mm:context-to-canonical` can be a thin
wrapper over the same handler.

## Default behavior

By default, the handler writes the document directly. This is the
model-agnostic path and works the same from Claude Code, Codex, or any shell.

## Full flow for new objectives

```
1. /mm:context-to-canonical --type objective --name "Add X"
   → creates docs/canonical/objective-specs/add-x.md

2. /mm:discover --roadmap --existing
   → reads the new spec (Tier 1 source), adds it to the roadmap

3. /mm:activate-next-objective
   → activates the objective for planning and execution
```

## Optional payload mode

If you want an LLM to rewrite or enrich the draft instead of writing it
directly, use:

```bash
python3 .claude/commands/mm/context-to-canonical-handler.py --payload-only [options]
```

That mode emits:
- `PAYLOAD: {...}`
- `LAUNCH: canonical-writer`

Any model runtime can then use `.mm-flow/agents/mm/canonical-writer/canonical-writer.md`
as the generic writing protocol.

## What the agent produces

A populated canonical document at `docs/canonical/project-adapter/<project-slug>.md`
(or the `--output` path) with every section filled from real project context.
