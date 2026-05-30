---
name: mm:new-canonical
description: Create new canonical documents (PRD, brain specs, source masters) from MasterMind templates.
argument-hint: "<type> [--name <slug>] [--title <title>]"
---

# /mm:new-canonical

Create new canonical documents from MasterMind framework templates.

## Usage

```bash
# Create a new PRD document
/mm:new-canonical prd --name "My Product" --title "My Product Vision"

/mm:new-canonical brain --name "brain-01" --title "Product Strategy Brain"
```

## Types

| Type | Description |
|------|-------------|
| `prd` | Product Requirements Document |
| `brain` | Brain specification |
| `source` | Source master document |
| `task` | Task specification |
| `objective` | Objective specification |

## Flags

| Flag | Description |
|------|-------------|
| `--name <slug>` | Slug for the document (required) |
| `--title <title>` | Human-readable title (optional, defaults to name) |
| `--output <path>` | Custom output path |

## Protocol

Execute the handler directly:

```bash
python3 .mm-flow/commands/mm/new-canonical-handler.py <type> --name <slug> --title <title>
```

---

## Examples

### Create PRD

```bash
/mm:new-canonical prd --name "v30-launch" --title "v3.0 Launch Plan"
```

### Create Brain Spec

```bash
/mm:new-canonical brain --name "brain-05-frontend" --title "Frontend Brain"
```

---

## See Also

- `/mm:extract-objectives` — Extract objectives from roadmap
- `/mm:discover` — Discover and plan
