# Session: Skills 2.0 + Global Installer

**Date:** 2026-03-25
**Outcome:** mm:brain-context upgraded to Skills 2.0 + installer now global by default. Committed (0b84ea7).

## Work Completed

### mm:brain-context → Skills 2.0
File: `.claude/skills/mm/brain-context/SKILL.md`

New frontmatter fields added:
- `argument-hint: [1|2|3|feed]` — autocomplete en el menú
- `disable-model-invocation: true` — no se auto-activa, solo invocación explícita
- `effort: high` — reserva compute para consultas NotebookLM
- `allowed-tools: Read, Bash, Grep, Glob`

Workflow paths updated to use `${CLAUDE_SKILL_DIR}`:
- `${CLAUDE_SKILL_DIR}/workflows/moment-1.md` (era `workflows/moment-1.md`)
- Idem para moment-2, moment-3, update-brain-feed, references/*

### Installer → Global por defecto
File: `apps/api/mastermind_cli/commands/install.py`

**Antes:** `mm install init` copiaba a `.claude/` del proyecto actual
**Ahora:** `mm install init` instala en `~/.claude/` (global, todos los proyectos)
- `mm install init --local` → comportamiento anterior (proyecto actual)
- Skills 2.0 se instalan con symlink de directorio completo → `~/.claude/skills/mm/brain-context/`
- Slash commands → `~/.claude/commands/mm/*.md`
- Hooks → `~/.claude/hooks/mm/`
- `.mastermind/config.yaml` + `.mastermind-active` siempre en el proyecto actual

## Context: Por qué se hizo
Usuario quiere usar el framework en otro proyecto. Descubrimos:
- mm:ask-* tenían / porque viven en `.claude/commands/mm/` (slash commands)
- mm:brain-context NO tenía / porque vive en `.claude/skills/mm/` (skill con subdirectorios)
- La skill no se instalaba en otros proyectos — el installer solo copiaba commands/hooks
- Solución: installer global, igual que GSD (`~/.claude/commands/gsd/`) y SC

## Git State
- Branch: master
- Commit: 0b84ea7 — feat(framework): skills 2.0 brain-context + global installer
- Remote: ~210 commits ahead of origin/master (PUSH PENDIENTE)
- Tag v2.1: local only (PUSH PENDIENTE)

## Pending Next Session
1. `git push origin master && git push origin v2.1`
2. Probar `mm install init` en el otro proyecto (verificar que ~/.claude/skills/mm/ y ~/.claude/commands/mm/ se crean correctamente)
3. `/gsd:new-milestone v2.2` — Brain Agents
4. Documentar 5 tech debt items en PROJECT.md (ver session/2026-03-25-post-v2.1-debt-audit)
