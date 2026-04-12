# MasterMind Framework - Code Conventions

## Git Conventions

### Commit Format
- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- NEVER add "Co-Authored-By" or AI attribution
- Format: `type(scope): description`

### Semantic Versioning
- Use git tags for versioning: `git tag v0.1.0 -m "description"`

## Source Files (Fichas de Fuentes)

### YAML Front Matter (Required)

```yaml
---
source_id: "FUENTE-XXX"
brain: "brain-software-01-product-strategy"
niche: "software-development"
title: "Title"
author: "Author Name"
expert_id: "EXP-XXX"
type: "book|video|article"
language: "en|es"
year: YYYY
distillation_date: "YYYY-MM-DD"
distillation_quality: "complete|partial|pending"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "YYYY-MM-DD"
changelog:
  - version: "1.0.0"
    date: "YYYY-MM-DD"
    changes:
      - "Change description"
status: "active|draft|deprecated"
---
```

### Required Content Sections

1. `### 1. Principios Fundamentales` - Min 3 principles with `> **P** format
2. `### 2. Frameworks y Metodologías`
3. `### 3. Modelos Mentales`
4. `### 4. Criterios de Decisión`
5. `### 5. Anti-patrones`

## System Prompts (Agents)

### Structure

- Written in English (better LLM performance)
- Include bilingual instruction: "Respond in the same language as the user's input"
- Define JSON output format for automation
- Add Markdown content field for humans

### Agent Files

- `agents/{role}/system-prompt.md` - Main behavior definition
- `agents/{role}/config.yaml` - Configuration (flows, criteria, etc.)

## Language

- Documentation: Spanish
- Code: English
- Comments: English (code), Spanish (documentation)
