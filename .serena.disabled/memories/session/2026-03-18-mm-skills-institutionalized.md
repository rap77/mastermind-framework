# Session 2026-03-18 — mm Skills Institutionalized + Brain Context GSD Flow

## Lo que se hizo

### Skills mm creadas (commit b047e20)

#### Nueva: `.claude/skills/mm/brain-context/SKILL.md`
- Flujo brain+GSD institucionalizado en 3 momentos:
  - **Momento 1** (pre-roadmap): Correr brains relevantes → `.planning/research/BRAIN-0X-CONTEXT.md`
  - **Momento 2** (pre-plan-phase): Brain del dominio → `CONTEXT.md` de la fase
  - **Momento 3** (post-plan, pre-execute): brain-07 valida PLAN.md via MCP directo
- Setup portable: detecta CLI dinámicamente, lee IDs del config del proyecto (no hardcodeado)
- Tabla de selección de brains por dominio de fase
- Common mistakes: siempre --use-mcp, siempre cd apps/api, no saltear Momento 3

#### Refactorizada: `.claude/skills/mm/mastermind-consultant/SKILL.md`
- Era: `mastermind-consultant.md` (flat file, 238 líneas, no-spec)
- Ahora: `mm/mastermind-consultant/SKILL.md` (52 líneas, spec-compliant)
- Fix typo notebook_id brain-07: b4d4 → b4d5
- Eliminado: triggers: YAML, Overview, When This Skill Activates, Memory References, Troubleshooting, Version
- Conservado: tabla IDs, Quick Selection, Standard Flows, ejemplo de query

#### CLAUDE.md del proyecto actualizado
- Tabla mm Brain Context con los 3 momentos como recordatorio permanente

### Patrón de institucionalización decidido
- Skill = portable knowledge (no CLAUDE.md global)
- CLAUDE.md del proyecto = reminder table (se agrega vía Setup de la skill)
- mm doctor --claude = verificación de salud (a implementar en CLI)
- La skill detecta su propio setup en repos externos

## Estado al cerrar

### Commits de sesión
- b047e20: feat(skills): add mm namespace skills + refactor mastermind-consultant
- 611a0fa: wip: 00-milestone-planning paused at task 2/3

### Pending: Momento 1
```bash
cd apps/api
uv run mm orchestrate run \
  "War Room Frontend: 4 pantallas..." \
  --brains brain-02-ux-research,brain-03-ui-design,brain-04-frontend \
  --use-mcp
```
→ outputs → `.planning/research/BRAIN-0X-CONTEXT.md`
→ gsd-roadmapper crea ROADMAP.md leyendo esos archivos

## Próxima sesión
/clear → /gsd:resume-work → Momento 1 (brains) → ROADMAP.md v2.1
