# Session: Framework Portability Fixes

**Date:** 2026-03-26
**Outcome:** Framework instalable en proyectos externos. 3 fixes commiteados + CLI reinstalado v1.1.0.

## Fixes Commiteados

- **[407b9ae]** fix(installer): get_framework_root() walk-up strategy — detecta monorepo/editable/distribución. Antes hardcodeaba `tools/mastermind-cli` y `site-packages`.
- **[15b4e6d]** fix(commands): Brain #7 notebook_id b4d4→b4d5 en ask-growth.md
- **[1ca3d1b]** refactor(commands): todos los ask-*.md leen notebook_id de config.yaml. Single source of truth: brain_registry.py → config.yaml → commands. No más IDs hardcodeados.

## CLI
- Reinstalado: `uv tool install --editable apps/api --force` → v1.1.0 desde ~/proy/mastermind/apps/api
- Antes apuntaba a ~/.mastermind-framework (v1.0.0, desactualizado)

## Prueba en prosell-sass
- `mm install init --force` funcionó — Framework: /home/rpadron/proy/mastermind ✓
- Skills via symlink → propagación automática de futuros fixes
- Brain #7 consultado: respondió con Hormozi/Lean Analytics/Munger/Kahneman (NotebookLM real)
- Decisión para Phase 8 prosell-sass: estrategia híbrida — Wave 1 funcional bloqueante, Wave 2 UAT real, Wave 3 UI premium
- mm:brain-context 2 ejecutado parcialmente (solo Brain #2, sin CONTEXT.md) — pendiente completar

## Git State
- master ~214 commits adelante de origin/master — PUSH PENDIENTE
- Tag v2.1 local only — PUSH PENDIENTE

## Next Actions
1. git push origin master && git push origin v2.1
2. Documentar 5 tech debt items en PROJECT.md (ver session/2026-03-25-post-v2.1-debt-audit)
3. Fix brains.ts: id: 1 → id: '1' (trivial, 5 líneas)
4. /gsd:new-milestone v2.2 (Brain Agents)
5. prosell-sass: completar mm:brain-context 2 → /gsd:plan-phase 8
