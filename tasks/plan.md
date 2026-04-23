# MasterMind Framework v3.0 Completion — Plan de Implementacion

**Generated:** 2026-04-20
**Based on:** SPEC.md
**Patron:** Horizontal slicing (Phase A, B, C, D...)
**Cada phase = entregable completo y testeable**

---

## Dependency Graph

```
PHASE A: Cleanup GSD (sin dependencias, primero para workspace limpio)
  A1. Eliminar wrappers    |
  A2. Eliminar skills      |
  A3. Eliminar markers     |
                            |
PHASE B: /mm:init + PostgreSQL (despues de A para workspace limpio)
  B1. db_client.py         | ← NUEVO: modulo PostgreSQL compartido
  B2. init-handler.py      | ← USA db_client
  B3. init.md              |
  B4. Validar init         |
                            |
PHASE C: /mm:review (depende de A + B1 para db_client)
  C1. review-handler.py    | ← USA db_client
  C2. review.md            |
  C3. review skill         |
  C4. code-reviewer agent  | ← ESCRIBE en PostgreSQL
  C5. Validar review       |
                            |
PHASE D: /mm:ship (depende de A + B1 para db_client)
  D1. ship-handler.py      | ← USA db_client
  D2. ship.md              |
  D3. ship skill           |
  D4. ship-executor agent  | ← ESCRIBE en PostgreSQL
  D5. Validar ship         |
                            |
PHASE E: End-to-End (depende de A + B + C + D)
  E1. Flujo completo       |
  E2. Commit final         |
```

---

## PHASE A — Cleanup GSD Dependencies

**Objetivo:** Eliminar toda dependencia de GSD. Workspace limpio con solo comandos MasterMind autonomos.

### A1: Eliminar GSD Wrapper Commands

**Que:** Borrar los 5 archivos `.md` que son wrappers de GSD.

**Archivos:**
- `.claude/commands/mm/new-milestone.md`
- `.claude/commands/mm/plan-phase.md`
- `.claude/commands/mm/execute-phase.md`
- `.claude/commands/mm/complete-phase.md`
- `.claude/commands/mm/verify-task.md`

**Acceptance:**
- [x] Los 5 archivos no existen
- [x] `/mm:discover` sigue apareciendo en autocomplete de Claude Code
- [x] `/mm:complete-task` sigue apareciendo en autocomplete
- [x] `/mm:safe-commit` sigue apareciendo en autocomplete

### A2: Eliminar Skills Huerfanos

**Que:** Borrar skills que solo servian a los wrappers GSD eliminados.

**Archivos:**
- `.claude/skills/mm/plan-phase/` (directorio completo: SKILL.md, README.md)
- `.claude/skills/mm/verify-task/` (directorio completo: SKILL.md, assets/, references/)

**Acceptance:**
- [x] Los 2 directorios no existen
- [x] Skills restantes: brain-context, brain-persistence, discover, mastermind-consultant, safe-commit
- [x] Ningun archivo existente referencia a `plan-phase` skill o `verify-task` skill

### A3: Limpiar Agent Markers Huerfanos

**Que:** Borrar archivos `.agent-*-running` huerfanos en `.planning/`.

**Archivos:**
- `.planning/.agent-B2-running`
- `.planning/.agent-D1-running`
- `.planning/.agent-D2-running`

**Acceptance:**
- [x] Los 3 archivos no existen
- [x] No hay otros `.agent-*-running` huerfanos
- [x] Directorio `.planning/` solo contiene directorios y archivos utiles

---

## PHASE B — `/mm:init` Command + PostgreSQL Integration

**Objetivo:** Comando que instala MasterMind Framework en cualquier proyecto. Verifica PostgreSQL, registra proyecto en DB, copia archivos. Handler-only (sin skill ni agent).

### B1: Crear `db_client.py` (Modulo Compartido)

**Que:** Modulo Python de conexion PostgreSQL compartido por todos los handlers.

**Funcionalidad:**
- Conexion centralizada a `localhost:5433` / `mastermind_bd`
- Funciones helper: `save_brain_consultation()`, `save_decision()`, `save_artifact()`, `save_experience()`
- Registro de proyectos: `register_project()`, `get_project()`
- Session tracking: `save_session_state()`, `get_session_state()`
- Provider check: `get_provider_status()`, `is_provider_available()`
- Manejo de errores graceful (si PostgreSQL no esta, los handlers funcionan sin DB)

**Acceptance:**
- [x] Modulo importa sin errores: `from db_client import MasterMindDB`
- [x] Conexion a PostgreSQL funciona: `MasterMindDB().ping()` retorna True
- [x] `register_project(name="test", path="/tmp/test")` inserta en tabla `projects`
- [x] `save_brain_consultation()` inserta en tabla `brain_consultations`
- [x] Si PostgreSQL no esta disponible, no crashea (graceful degradation)

### B2: Crear `init-handler.py`

**Que:** Python handler que verifica servicios, detecta stack y copia archivos de MasterMind al proyecto destino.

**Funcionalidad:**
- `--target <path>` — Directorio destino (default: CWD)
- `--check` — Verificar instalacion existente
- `--force` — Sobreescribir si ya existe `.mastermind/`
- **Verificar PostgreSQL** — docker compose ps + ping localhost:5433
- **Verificar Rust Control Plane** — ping localhost:3001 (opcional, advertir si no esta)
- **Verificar provider disponible** — check `backend_sessions` para tokens disponibles
- Detectar stack: leer `package.json`, `pyproject.toml`, `CLAUDE.md`
- Copiar `.claude/commands/mm/` (solo init, discover, complete-task, review, ship + handlers + db_client.py)
- Copiar `.claude/skills/mm/` (brain-context, brain-persistence, discover, safe-commit, review, ship)
- Copiar `.claude/agents/mm/` (7 brains + discover-planner + rediscovery-auditor + task-executor)
- Crear `.mastermind/config.yaml` con stack detectado + conexion DB
- **Registrar proyecto en PostgreSQL** — INSERT en tabla `projects`
- Output: `STATUS: installed` o `ERROR: <reason>`

**Acceptance:**
- [x] Handler ejecuta sin errores con `python3 init-handler.py --target /tmp/test-project`
- [x] Verifica PostgreSQL antes de continuar (falla si no esta)
- [x] Crea `.mastermind/config.yaml` con stack detectado + DB connection info
- [x] Crea `.claude/commands/mm/` con los 5 comandos + handlers + db_client.py
- [x] Registra proyecto en tabla `projects` de PostgreSQL
- [x] `--check` retorna `STATUS: installed` en proyecto ya instalado
- [x] `--check` retorna `STATUS: not-installed` en proyecto vacio
- [x] Proteccion: no sobreescribir sin `--force`
- [x] Advierte si Rust Control Plane no esta disponible (no bloquea)

### B3: Crear `init.md`

**Que:** Slash command interface siguiendo el patron de `discover.md`.

**Estructura:**
- YAML front matter: name, description, argument-hint
- Usage con ejemplos
- Protocol (For Assistant): Step 1 ejecutar handler, Step 2 parsear output, Step 3 notificar
- Flags: --target, --check, --force
- Nota sobre PostgreSQL como prerequisito

**Acceptance:**
- [x] `/mm:init` aparece en autocomplete de Claude Code
- [x] Sigue el mismo formato que `discover.md`
- [x] Protocol section sigue el patron: handler -> parse -> notify
- [x] Documenta que PostgreSQL es prerequisito

### B4: Validar `/mm:init` End-to-End

**Que:** Probar init en directorio vacio y en proyecto existente.

**Acceptance:**
- [x] En `/tmp/test-project` vacio: `/mm:init --target /tmp/test-project` crea estructura completa
- [x] Proyecto aparece en tabla `projects` de PostgreSQL
- [x] `.mastermind/config.yaml` tiene `db.host: localhost`, `db.port: 5433`
- [x] En proyecto existente (mastermind): `/mm:init --check` retorna installed
- [x] Sin `--force`: `/mm:init --target /tmp/test-project` (ya instalado) advierte sin sobreescribir
- [x] Con `--force`: sobreescribe correctamente

---

## PHASE C — `/mm:review` Command

**Objetivo:** Code review con brains. Handler + skill + agent.

### C1: Crear `review-handler.py`

**Que:** Python handler que detecta scope del review y genera payload para agent. Escribe en PostgreSQL.

**Funcionalidad:**
- Sin flags: `git diff` (uncommitted changes)
- `--staged`: `git diff --staged`
- `--branch <name>`: `git diff <name>...HEAD`
- `--files <paths>`: Leer archivos directamente
- `--last-commit`: `git diff HEAD~1..HEAD`
- Truncar diff a 500 lineas (configurable)
- Detectar lenguaje de los archivos modificados
- Generar payload con diff + contexto
- **Guardar en PostgreSQL:** `artifacts` con referencia al review pendiente

**Output:**
```
MODE: review
SCOPE: uncommitted|staged|branch|files|last-commit
FILES: [lista de archivos modificados]
LINES: N lines changed
DB: connected|unavailable
LAUNCH: code-reviewer
PAYLOAD: {json}
```

**Acceptance:**
- [ ] Handler ejecuta sin errores con `python3 review-handler.py`
- [ ] `--staged` genera diff correcto de staged changes
- [ ] `--last-commit` genera diff del ultimo commit
- [ ] Payload incluye lista de archivos y diff truncado

### C2: Crear `review.md`

**Que:** Slash command interface.

**Estructura:**
- YAML front matter
- Usage: `/mm:review`, `/mm:review --staged`, `/mm:review --branch main`, etc.
- Protocol: handler -> parse -> launch agent -> notify
- Brain integration: Brain #6 (QA) + Brain #7 (Growth)

**Acceptance:**
- [ ] `/mm:review` aparece en autocomplete
- [ ] Sigue patron de `discover.md`
- [ ] Documenta los 5 modos de review

### C3: Crear `review/SKILL.md`

**Que:** Skill protocolo para review. Define como consultar brains durante review.

**Contenido:**
- Cuando usar (proactivo: antes de commit, post-implementation)
- Protocolo de review: 5 ejes (correctness, readability, architecture, security, performance)
- Brain #6: QA standards, testing strategy, edge cases
- Brain #7: Systems thinking, impact analysis, risk assessment
- Formato de reporte: `.planning/REVIEWS/<timestamp>-review.md`
- Criterios de severidad: CRITICAL / WARNING / SUGGESTION

**Acceptance:**
- [ ] SKILL.md sigue formato de `discover/SKILL.md`
- [ ] Define 5 ejes de review con criterios claros
- [ ] Incluye formato de reporte

### C4: Crear `code-reviewer` Agent

**Que:** Agent que ejecuta code review consultando brains.

**Directorio:** `.claude/agents/mm/code-reviewer/code-reviewer.md`

**Funcionalidad:**
- Recibe payload con diff + contexto
- Consulta Brain #6 para QA standards
- Consulta Brain #7 para systems evaluation
- **Escribe en PostgreSQL:**
  - `brain_consultations` — cada consulta a Brain #6 y #7 (input, output, confidence)
  - `brain_feedback` — aprendizajes del review
  - `artifacts` — referencia al reporte generado
- Genera reporte en `.planning/REVIEWS/<timestamp>-review.md`
- Reporte: 5 secciones con CRITICAL / WARNING / SUGGESTION

**Acceptance:**
- [ ] Agent file sigue formato de `task-executor.md`
- [ ] Consulta Brain #6 y Brain #7
- [ ] Genera reporte con 5 secciones
- [ ] Guarda en `.planning/REVIEWS/`

### C5: Validar `/mm:review`

**Que:** Probar review con cambios reales.

**Acceptance:**
- [ ] `/mm:review` en proyecto con cambios uncommitted genera reporte
- [ ] Reporte tiene 5 secciones (correctness, readability, architecture, security, performance)
- [ ] `/mm:review --staged` solo reviewea staged changes
- [ ] `/mm:review --last-commit` reviewea ultimo commit
- [ ] Reporte se guarda en `.planning/REVIEWS/`

---

## PHASE D — `/mm:ship` Command

**Objetivo:** Tag + archive + cleanup. Handler + skill + agent.

### D1: Crear `ship-handler.py`

**Que:** Python handler que verifica pre-condiciones y genera payload para agent.

**Funcionalidad:**
- `--verify`: Solo verificar, no crear tag (dry-run)
- `--tag vX.Y.Z`: Tag explicito
- `--patch`: Incrementar patch (default)
- `--minor`: Incrementar minor
- `--major`: Incrementar major
- `--archive`: Solo archivar artefactos
- `--cleanup`: Solo limpiar archivos temporales
- Verificar: tests pasan, no hay uncommitted, SPEC.md existe
- Leer ultimo tag de git
- Generar changelog desde ultimo tag (git log)

**Output:**
```
MODE: ship|verify|archive|cleanup
CURRENT_TAG: vX.Y.Z
NEXT_TAG: vX.Y.Z+1
CHANGELOG: [N commits since last tag]
PRECONDITIONS: pass|fail
LAUNCH: ship-executor
PAYLOAD: {json}
```

**Acceptance:**
- [ ] Handler detecta ultimo tag correctamente
- [ ] `--verify` ejecuta checks sin crear tag
- [ ] Genera changelog desde ultimo tag
- [ ] Falla si hay cambios uncommitted
- [ ] `--patch` incrementa patch, `--minor` minor, `--major` major

### D2: Crear `ship.md`

**Que:** Slash command interface.

**Acceptance:**
- [ ] `/mm:ship` aparece en autocomplete
- [ ] Documenta flags: --verify, --tag, --patch, --minor, --major, --archive, --cleanup

### D3: Crear `ship/SKILL.md`

**Que:** Skill protocolo para ship.

**Contenido:**
- Cuando usar: al completar milestone/version
- Pre-condiciones: tests pass, no uncommitted, SPEC exists
- Flujo: verify -> tag -> archive -> cleanup
- Formato de changelog
- Formato de archive: `.planning/archive/<version>/`

**Acceptance:**
- [ ] Sigue formato de `discover/SKILL.md`
- [ ] Define flujo completo con pre-condiciones

### D4: Crear `ship-executor` Agent

**Que:** Agent que ejecuta el ship (verify, tag, archive, cleanup).

**Directorio:** `.claude/agents/mm/ship-executor/ship-executor.md`

**Funcionalidad:**
- Ejecutar tests (frontend + backend)
- Crear git tag
- Mover `tasks/` a `.planning/archive/<version>/`
- Limpiar `.agent-*-running`, `task-progress.json` viejos
- Actualizar `.mastermind/config.yaml` con version
- **Escribir en PostgreSQL:**
  - `decisions` — registro del ship (version, tests result, changelog)
  - `artifacts` — referencia al archive generado
  - `dev_sessions` — actualiza estado a `completed`
- Mostrar resumen del ship

**Acceptance:**
- [ ] Agent sigue formato de `task-executor.md`
- [ ] Ejecuta tests antes de crear tag
- [ ] Crea tag semantico
- [ ] Archiva `tasks/` correctamente
- [ ] Limpia archivos temporales

### D5: Validar `/mm:ship`

**Que:** Probar ship con `--verify` (dry-run, no crea tag real).

**Acceptance:**
- [ ] `/mm:ship --verify` ejecuta checks y reporta estado
- [ ] Reporta tests pasando/fallando
- [ ] Reporta cambios uncommitted
- [ ] Sugiere proximo tag basado en ultimo tag
- [ ] `/mm:ship --cleanup` elimina archivos `.agent-*-running`

---

## PHASE E — End-to-End Validation

**Objetivo:** Validar flujo completo de los 5 comandos.

### E1: Flujo Completo en Proyecto de Prueba

**Que:** Ejecutar el flujo completo en un proyecto temporal.

**Flujo:**
1. Crear proyecto temporal: `/tmp/mm-test-project`
2. `/mm:init --target /tmp/mm-test-project`
3. `/mm:discover "Test app de TODO"`
4. `/mm:complete-task A1`
5. `/mm:review --last-commit`
6. `/mm:ship --verify`

**Acceptance:**
- [ ] Init crea estructura completa
- [ ] Discover genera SPEC + plan + todo
- [ ] Complete-task ejecuta subtarea
- [ ] Review genera reporte con 5 secciones
- [ ] Ship --verify reporta estado correcto
- [ ] Cero errores en flujo completo

### E2: Commit Final

**Que:** Commit de todos los archivos nuevos y eliminados.

**Acceptance:**
- [ ] Commit con mensaje: `feat(mm-commands): add init, review, ship commands and remove GSD wrappers`
- [ ] Solo archivos nuevos/modificados/eliminados, nada extra
- [ ] Tests existentes pasan
- [ ] `/mm:discover` y `/mm:complete-task` funcionan post-commit

---

## Task Summary

| ID | Task | Depends On | Complexity | Files | DB | Status |
|----|------|------------|------------|-------|-----|--------|
| A1 | Eliminar wrapper commands | — | Low | 5 delete | — | [x] |
| A2 | Eliminar skills huerfanos | — | Low | 2 dirs delete | — | [x] |
| A3 | Limpiar markers huerfanos | — | Low | 3 delete | — | [x] |
| B1 | db_client.py (modulo PostgreSQL) | — | Medium | 1 new | SI | [x] |
| B2 | init-handler.py | B1 | Medium | 1 new | SI | [x] |
| B3 | init.md | B2 | Low | 1 new | — | [x] |
| B4 | Validar init | B1-B3 | Low | 0 new | SI | [x] |
| C1 | review-handler.py | A, B1 | Medium | 1 new | SI | [ ] |
| C2 | review.md | C1 | Low | 1 new | — | [ ] |
| C3 | review/SKILL.md | C1 | Medium | 1 new | — | [ ] |
| C4 | code-reviewer agent | C3 | Medium | 1 new | SI | [ ] |
| C5 | Validar review | C1-C4 | Low | 0 new | SI | [ ] |
| D1 | ship-handler.py | A, B1 | Medium | 1 new | SI | [ ] |
| D2 | ship.md | D1 | Low | 1 new | — | [ ] |
| D3 | ship/SKILL.md | D1 | Medium | 1 new | — | [ ] |
| D4 | ship-executor agent | D3 | Medium | 1 new | SI | [ ] |
| D5 | Validar ship | D1-D4 | Low | 0 new | SI | [ ] |
| E1 | Flujo E2E | All | Medium | 0 new | SI | [ ] |
| E2 | Commit final | E1 | Low | 0 new | — | [ ] |

**Total: 5 phases, 19 tasks, ~15 files nuevos, ~10 archivos eliminados**

**Parallel tracks:**
- Track 1 (cleanup): A1 + A2 + A3 (secuencial rapido)
- Track 2 (init + DB): B1 -> B2 -> B3 -> B4 (primero: db_client es prerequisito de C y D)
- Track 3 (review): C1 -> C2 -> C3 -> C4 -> C5 (despues de A + B1)
- Track 4 (ship): D1 -> D2 -> D3 -> D4 -> D5 (despues de A + B1, paralelo con C)
- Track 5 (E2E): E1 -> E2 (despues de todo)

**Recommended execution order:**
1. **A1-A3** (Cleanup) — 10 minutos, workspace limpio
2. **B1** (db_client.py) — 20 minutos, PRIMERO (C y D dependen de este)
3. **B2-B4** (Init) — 30 minutos, handler + command + validacion
4. **C1-C5 + D1-D5** (Review + Ship) — 90 minutos, pueden ir en paralelo
5. **E1-E2** (E2E) — 30 minutos, al final

---

## Risks

| Risk | Mitigation |
|------|------------|
| `/mm:init` copia archivos del propio mastermind (meta) | Detectar si target == mastermind source, advertir |
| Eliminar wrappers rompe flujo existente | Verificar no hay fases pendientes en `.planning/phases/` |
| Review con diffs grandes (>500 lineas) | Truncar por defecto, flag `--full` para completo |
| Ship asume tags semanticos | Detectar ultimo tag, sugerir `v0.1.0` si no hay |
| Safe-commit depende de GGA | Init incluye opcion para GGA, safe-commit advierte si falta |

---

*Plan basado en SPEC.md — single source of truth para implementacion.*
*Last updated: 2026-04-20*
