# MasterMind Framework v3.0 Completion — Checklist

**Generated:** 2026-04-20
**Based on:** tasks/plan.md

---

## PHASE A — Cleanup GSD Dependencies

### A1: Eliminar GSD Wrapper Commands ✅
- [x] Borrar `.claude/commands/mm/new-milestone.md`
- [x] Borrar `.claude/commands/mm/plan-phase.md`
- [x] Borrar `.claude/commands/mm/execute-phase.md`
- [x] Borrar `.claude/commands/mm/complete-phase.md`
- [x] Borrar `.claude/commands/mm/verify-task.md`
- [x] Verificar: `/mm:discover` aparece en autocomplete
- [x] Verificar: `/mm:complete-task` aparece en autocomplete
- [x] Verificar: `/mm:safe-commit` aparece en autocomplete

### A2: Eliminar Skills Huerfanos ✅
- [x] Borrar directorio `.claude/skills/mm/plan-phase/` (SKILL.md + README.md)
- [x] Borrar directorio `.claude/skills/mm/verify-task/` (SKILL.md + assets/ + references/)
- [x] Verificar: skills restantes = brain-context, brain-persistence, discover, mastermind-consultant, safe-commit
- [x] Verificar: sin referencias a `plan-phase` o `verify-task` en archivos existentes

### A3: Limpiar Agent Markers Huerfanos ✅
- [x] Borrar `.planning/.agent-B2-running`
- [x] Borrar `.planning/.agent-D1-running`
- [x] Borrar `.planning/.agent-D2-running`
- [x] Verificar: no hay otros `.agent-*-running` huerfanos en `.planning/`

---

## PHASE B — `/mm:init` Command

### B1: Crear init-handler.py ✅
- [x] Crear `.claude/commands/mm/init-handler.py`
- [x] Implementar flag `--target <path>` (default: CWD)
- [x] Implementar flag `--check` (verificar instalacion)
- [x] Implementar flag `--force` (sobreescribir)
- [x] Implementar deteccion de stack (package.json, pyproject.toml, CLAUDE.md)
- [x] Implementar copia de `.claude/commands/mm/` (solo init, discover, complete-task, review, ship + handlers)
- [x] Implementar copia de `.claude/skills/mm/` (brain-context, brain-persistence, discover, safe-commit, review, ship)
- [x] Implementar copia de `.claude/agents/mm/` (7 brains + discover-planner + rediscovery-auditor + task-executor)
- [x] Implementar creacion de `.mastermind/config.yaml` con stack detectado
- [x] Output: `STATUS: installed|not-installed` o `ERROR: <reason>`
- [x] Proteccion: no sobreescribir sin `--force`
- [x] Proteccion: advertir si target == mastermind source
- [x] Handler ejecuta sin errores: `python3 init-handler.py --target /tmp/test-project`

### B2: Crear init.md ✅
- [x] Crear `.claude/commands/mm/init.md`
- [x] YAML front matter: name `mm:init`, description, argument-hint
- [x] Usage con ejemplos (sin flags, --target, --check, --force)
- [x] Protocol section: Step 1 ejecutar handler, Step 2 parsear output, Step 3 notificar
- [x] Sigue formato de `discover.md`
- [x] `/mm:init` aparece en autocomplete de Claude Code

### B3: Validar /mm:init End-to-End
- [x] Crear directorio vacio `/tmp/test-project`
- [x] Ejecutar `python3 init-handler.py --target /tmp/test-project`
- [x] Verificar: `/tmp/test-project/.mastermind/config.yaml` existe
- [x] Verificar: `/tmp/test-project/.claude/commands/mm/` tiene los 5 comandos + handlers
- [x] Verificar: `/tmp/test-project/.claude/skills/mm/` tiene skills
- [x] Verificar: `/tmp/test-project/.claude/agents/mm/` tiene brains + agents
- [x] Ejecutar `python3 init-handler.py --check --target /tmp/test-project` → `STATUS: installed`
- [x] Ejecutar `python3 init-handler.py --target /tmp/test-project` (sin --force) → advierte
- [x] Ejecutar `python3 init-handler.py --target /tmp/test-project --force` → sobreescribe
- [x] En mastermind: `python3 init-handler.py --check` → `STATUS: installed`

---

## PHASE C — `/mm:review` Command

### C1: Crear review-handler.py ✅ REVIEWED & APPROVED
- [x] Crear `.claude/commands/mm/review-handler.py`
- [x] Sin flags: generar `git diff` (uncommitted)
- [x] Flag `--staged`: generar `git diff --staged`
- [x] Flag `--branch <name>`: generar `git diff <name>...HEAD`
- [x] Flag `--files <paths>`: leer archivos directamente
- [x] Flag `--last-commit`: generar `git diff HEAD~1..HEAD`
- [x] Truncar diff a 500 lineas por defecto
- [x] Detectar lenguaje de archivos modificados
- [x] Output: `MODE`, `SCOPE`, `FILES`, `LINES`, `LAUNCH: code-reviewer`, `PAYLOAD`
- [x] Handler ejecuta sin errores: `python3 review-handler.py`
- [x] `--staged` genera diff correcto
- [x] `--last-commit` genera diff del ultimo commit
- [x] **Code review completado:** `.planning/REVIEWS/2026-04-23-review-handler-C1.md`
- [x] **Veredict:** ✅ APPROVE — Production-ready
- [x] **Todos los acceptance criteria verificados**

### C2: Crear review.md ✅ VERIFIED
- [x] Crear `.claude/commands/mm/review.md`
- [x] YAML front matter: name `mm:review`, description, argument-hint
- [x] Usage con 5 modos (default, --staged, --branch, --files, --last-commit)
- [x] Protocol: handler -> parse -> launch code-reviewer agent -> notify
- [x] Brain integration: Brain #6 + Brain #7
- [x] `/mm:review` aparece en autocomplete

### C3: Crear review/SKILL.md ✅ VERIFIED
- [x] Crear directorio `.claude/skills/mm/review/`
- [x] Crear `.claude/skills/mm/review/SKILL.md`
- [x] Seccion "Cuando Usar" (proactivo: antes de commit, post-implementation)
- [x] Protocolo de review: 5 ejes (correctness, readability, architecture, security, performance)
- [x] Brain #6: QA standards, testing strategy, edge cases
- [x] Brain #7: Systems thinking, impact analysis, risk assessment
- [x] Formato de reporte: `.planning/REVIEWS/<timestamp>-review.md`
- [x] Criterios de severidad: CRITICAL / WARNING / SUGGESTION
- [x] Sigue formato de `discover/SKILL.md`

### C4: Crear code-reviewer Agent
- [ ] Crear directorio `.claude/agents/mm/code-reviewer/`
- [ ] Crear `.claude/agents/mm/code-reviewer/code-reviewer.md`
- [ ] Recibe payload con diff + contexto
- [ ] Consulta Brain #6 para QA standards
- [ ] Consulta Brain #7 para systems evaluation
- [ ] Genera reporte con 5 secciones (correctness, readability, architecture, security, performance)
- [ ] Guarda reporte en `.planning/REVIEWS/<timestamp>-review.md`
- [ ] Sigue formato de `task-executor.md`

### C5: Validar /mm:review
- [ ] Hacer un cambio pequeno en cualquier archivo (sin commitear)
- [ ] Ejecutar `python3 review-handler.py` → genera payload con diff
- [ ] Verificar que payload incluye archivos modificados y diff
- [ ] `/mm:review --staged` solo genera diff de staged changes
- [ ] `/mm:review --last-commit` genera diff del ultimo commit
- [ ] Reporte se guarda en `.planning/REVIEWS/`

---

## PHASE D — `/mm:ship` Command

### D1: Crear ship-handler.py
- [ ] Crear `.claude/commands/mm/ship-handler.py`
- [ ] Flag `--verify`: solo verificar, no crear tag (dry-run)
- [ ] Flag `--tag vX.Y.Z`: tag explicito
- [ ] Flag `--patch`: incrementar patch (default)
- [ ] Flag `--minor`: incrementar minor
- [ ] Flag `--major`: incrementar major
- [ ] Flag `--archive`: solo archivar artefactos
- [ ] Flag `--cleanup`: solo limpiar archivos temporales
- [ ] Verificar: no hay cambios uncommitted (`git diff --quiet`)
- [ ] Verificar: SPEC.md existe
- [ ] Leer ultimo tag de git (`git describe --tags --abbrev=0`)
- [ ] Generar changelog desde ultimo tag (`git log vX.Y.Z..HEAD --oneline`)
- [ ] Calcular siguiente version (patch/minor/major)
- [ ] Output: `MODE`, `CURRENT_TAG`, `NEXT_TAG`, `CHANGELOG`, `PRECONDITIONS`, `LAUNCH`, `PAYLOAD`
- [ ] Handler ejecuta sin errores: `python3 ship-handler.py --verify`

### D2: Crear ship.md
- [ ] Crear `.claude/commands/mm/ship.md`
- [ ] YAML front matter: name `mm:ship`, description, argument-hint
- [ ] Usage con flags: --verify, --tag, --patch, --minor, --major, --archive, --cleanup
- [ ] Protocol: handler -> parse -> launch ship-executor agent -> notify
- [ ] `/mm:ship` aparece en autocomplete

### D3: Crear ship/SKILL.md
- [ ] Crear directorio `.claude/skills/mm/ship/`
- [ ] Crear `.claude/skills/mm/ship/SKILL.md`
- [ ] Seccion "Cuando Usar" (al completar milestone/version)
- [ ] Pre-condiciones: tests pass, no uncommitted, SPEC exists
- [ ] Flujo: verify -> tag -> archive -> cleanup
- [ ] Formato de changelog
- [ ] Formato de archive: `.planning/archive/<version>/`
- [ ] Sigue formato de `discover/SKILL.md`

### D4: Crear ship-executor Agent
- [ ] Crear directorio `.claude/agents/mm/ship-executor/`
- [ ] Crear `.claude/agents/mm/ship-executor/ship-executor.md`
- [ ] Ejecutar tests (frontend + backend) y reportar resultado
- [ ] Crear git tag semantico
- [ ] Mover `tasks/` a `.planning/archive/<version>/`
- [ ] Limpiar `.agent-*-running` y `task-progress.json` viejos
- [ ] Actualizar `.mastermind/config.yaml` con version
- [ ] Mostrar resumen del ship
- [ ] Sigue formato de `task-executor.md`

### D5: Validar /mm:ship
- [ ] Ejecutar `python3 ship-handler.py --verify` → reporta estado
- [ ] Verificar: reporta ultimo tag correctamente
- [ ] Verificar: reporta si hay uncommitted changes
- [ ] Verificar: sugiere proximo tag (patch por defecto)
- [ ] Ejecutar `python3 ship-handler.py --cleanup` → elimina `.agent-*-running`
- [ ] Sin crear tag real (usar --verify para pruebas)

---

## PHASE E — End-to-End Validation

### E1: Flujo Completo en Proyecto de Prueba
- [ ] Crear proyecto temporal: `mkdir -p /tmp/mm-test-project && cd /tmp/mm-test-project && git init`
- [ ] Paso 1: `/mm:init --target /tmp/mm-test-project` → estructura creada
- [ ] Paso 2: `/mm:discover "App de TODO simple"` → SPEC + plan + todo generados
- [ ] Paso 3: `/mm:complete-task A1` → subtarea ejecutada
- [ ] Paso 4: `/mm:review --last-commit` → reporte con 5 secciones generado
- [ ] Paso 5: `/mm:ship --verify` → estado reportado correctamente
- [ ] Verificar: cero errores en flujo completo
- [ ] Verificar: `/mm:discover` y `/mm:complete-task` siguen funcionando post-cleanup

### E2: Commit Final
- [ ] Stage: archivos nuevos (init, review, ship commands + handlers + skills + agents)
- [ ] Stage: archivos eliminados (GSD wrappers + skills huerfanos + markers)
- [ ] Verificar: tests existentes pasan (backend + frontend)
- [ ] Commit: `feat(mm-commands): add init, review, ship commands and remove GSD wrappers`
- [ ] Verificar: `/mm:discover` funciona post-commit
- [ ] Verificar: `/mm:complete-task` funciona post-commit
- [ ] Verificar: `/mm:safe-commit` funciona post-commit

---

## Summary

| Phase | Tasks | Items | Status |
|-------|-------|-------|--------|
| A — Cleanup | 3 | 16 | ✅ |
| B — Init | 3 | 22 | ✅ |
| C — Review | 5 | 26 | 2/5 (C1 ✅, C2 ✅) |
| D — Ship | 5 | 24 | [ ] |
| E — E2E | 2 | 13 | [ ] |
| **Total** | **18** | **101** | **60/101 (60%)** |

**Archivos nuevos:** ~14
**Archivos eliminados:** ~10
**Estimacion:** 3-4 horas de trabajo
