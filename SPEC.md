# MasterMind Framework v3.0 Completion — Specification

**Generated:** 2026-04-20
**Mode:** Framework Completion (plug-and-play)
**Session:** discover-new-20260420-075407

---

## 1. Problem Statement

MasterMind Framework tiene 7 cerebros funcionales, `/mm:discover` genera specs+planes, y `/mm:complete-task` ejecuta tareas. Pero el framework NO es plug-and-play: no se puede instalar en otro proyecto, no tiene flujo de review integrado, no tiene ship automatizado, y depende de GSD (comandos wrapper que delegan a `/gsd:*`).

**Problemas concretos:**

1. **Sin `/mm:init`:** No existe forma de instalar MasterMind en un proyecto nuevo. Cada proyecto necesita copia manual de `.claude/commands/mm/`, `.claude/skills/mm/`, `.claude/agents/mm/`. Friction alto.

2. **Sin `/mm:review`:** No hay code review con brains. El flujo completo es discover -> complete-task, pero falta un punto de verificacion intermedio donde los cerebros evaluem codigo antes de commit.

3. **Sin `/mm:ship`:** No existe comando para tag+archive. El usuario tiene que hacer manualmente: verificar tests, crear tag semantico, archivar artefactos. Propenso a errores.

4. **Dependencia GSD:** Cinco comandos (`new-milestone`, `plan-phase`, `execute-phase`, `complete-phase`, `verify-task`) son wrappers que delegan a `/gsd:*`. Si el usuario no tiene GSD instalado, esos comandos fallan. El framework pierde independencia.

5. **Artefactos GSD innecesarios:** Skills como `plan-phase/` y `verify-task/` solo existen para servir a los wrappers GSD. Si eliminamos los wrappers, esos skills quedan huerfanos.

---

## 2. Solution Overview

Hacer MasterMind Framework plug-and-play con **5 comandos autonomos** y **cero dependencias externas**:

| Comando | Que hace | Estado |
|---------|----------|--------|
| `/mm:init` | Instala MasterMind en cualquier proyecto | **NUEVO** |
| `/mm:discover` | Idea -> SPEC.md + plan.md + todo.md | EXISTE (no tocar) |
| `/mm:complete-task` | Ejecuta 1 tarea: build -> test -> review -> commit | EXISTE (no tocar) |
| `/mm:review` | Code review con brains | **NUEVO** |
| `/mm:ship` | Tag + archive + cleanup | **NUEVO** |

**Que se ELIMINA (GSD wrappers):**
- `/mm:new-milestone` (delega a `gsd:new-milestone`)
- `/mm:plan-phase` (delega a `gsd:plan-phase`)
- `/mm:execute-phase` (delega a `gsd:execute-phase`)
- `/mm:complete-phase` (delega a `gsd:execute-phase` + BRAIN-FEED update)
- `/mm:verify-task` (lee artefactos GSD)

**Que se LIMPIA:**
- Skill `plan-phase/` (solo sirve al wrapper deprecado)
- Skill `verify-task/` (solo lee artefactos GSD)
- Archivos `.agent-*-running` huerfanos en `.planning/`

---

## 3. Architecture

### 3.1 Patron de Comandos

Todos los comandos siguen el patron ya probado con `/mm:discover`:

```
command.md (interfaz) -> handler.py (logica) -> skill (protocolo) -> agent (ejecucion)
```

**Niveles de complejidad:**

| Comando | handler.py | skill | agent | PostgreSQL |
|---------|-----------|-------|-------|------------|
| `/mm:init` | SI | NO (handler-only) | NO | SI (verifica + registra) |
| `/mm:review` | SI | SI | SI (code-reviewer) | SI (brain decisions) |
| `/mm:ship` | SI | SI | SI (ship-executor) | SI (archive metadata) |

**Justificacion:**
- `/mm:init` es mecanico (copiar archivos, crear config) PERO tambien verifica PostgreSQL y registra el proyecto en la DB central. No necesita skill ni agent.
- `/mm:review` necesita brains consultando codigo. Skill para protocolo, agent para ejecucion en background. Escribe decisiones en PostgreSQL.
- `/mm:ship` necesita validacion multi-step (tests, tag, archive). Skill para protocolo, agent para ejecucion. Escribe metadata en PostgreSQL.

### 3.1.1 PostgreSQL — Fuente Unica de Verdad

Todos los proyectos comparten la MISMA base de datos PostgreSQL del framework MasterMind. Esto permite:

- **Contexto persistente**: Las decisiones de los cerebros no se pierden entre sesiones
- **Aprendizaje acumulativo**: `experience_records` acumula conocimiento de todas las ejecuciones
- **Auditoria completa**: `brain_consultations`, `decisions`, `audit_log` trazan todo
- **Sesion continua**: `dev_sessions` + `context_checkpoints` permiten restaurar estado

**Tablas clave (ya existen en PostgreSQL):**

| Tabla | Uso en el framework |
|-------|---------------------|
| `projects` | Registro de proyectos instalados via `/mm:init` |
| `brain_consultations` | Cada consulta a un cerebro (input, output, confidence) |
| `brain_feedback` | Aprendizajes y retroalimentacion de agentes |
| `decisions` | Decisiones tecnicas/arquitectonicas tomadas |
| `experience_records` | Historial de ejecucion con resultados |
| `dev_sessions` | Sesiones de desarrollo con estado |
| `context_checkpoints` | Snapshots de contexto antes de cambios |
| `backend_sessions` | Tracking de tokens y providers por sesion |
| `artifacts` | Documentos generados (SPEC, planes, reviews) |

**Conexion PostgreSQL:**

- Host: `localhost:5433` (docker) / `postgres:5432` (container)
- DB: `mastermind_bd`
- El handler base incluye un modulo `db_client.py` con conexion centralizada
- Todos los handlers nuevos importan y usan `db_client` para escribir

### 3.2 Estructura de Handlers

Los handlers Python siguen el formato de `discover-handler.py`:

```python
#!/usr/bin/env python3
"""MasterMind <command> Handler."""
import argparse, json, sys
from pathlib import Path

def main():
    # Parse args
    # Read context
    # Generate payload (JSON)
    # Output: MODE, TASK, PAYLOAD, LAUNCH

if __name__ == "__main__":
    main()
```

**Output contract (machine-parseable):**
- `MODE: <mode>` — modo de operacion
- `TASK: <agent-type>` — tipo de agent a lanzar
- `PAYLOAD: {json}` — payload para el agent
- `LAUNCH: <agent-name>` — nombre del agent
- `ERROR: <message>` — error, mostrar al usuario
- `STATUS: <message>` — estado sin agent

### 3.3 Configuracion del Proyecto (`.mastermind/config.yaml`)

Nuevo archivo que `/mm:init` crea en el proyecto destino:

```yaml
mastermind:
  version: "3.0"
  installed: "2026-04-20"
  project:
    name: "my-project"
    stack:
      frontend: "nextjs"
      backend: "fastapi"
      runtime_python: "uv"
      runtime_node: "pnpm"
    testing:
      frontend_cmd: "pnpm --prefix apps/web test run"
      backend_cmd: "cd apps/api && uv run pytest"
    brains:
      active: [1, 4, 5, 7]  # Product, Backend, Frontend, Growth
    git:
      main_branch: "main"
      tag_prefix: "v"
      conventional_commits: true
```

---

## 4. Commands Detail

### 4.1 `/mm:init` — Instalar MasterMind en Cualquier Proyecto

**Interfaz:**
```bash
/mm:init                          # Instalar en proyecto actual
/mm:init --target ~/my-project    # Instalar en proyecto destino
/mm:init --check                  # Verificar instalacion existente
```

**Flujo:**
1. **Verifica PostgreSQL** — docker compose ps, ping a `localhost:5433`, schema existe
2. **Verifica Rust Control Plane** — ping a `localhost:3001` (opcional, advertir si no esta)
3. **Verifica provider disponible** — check `backend_sessions` para saber si Claude/Z.ai tienen tokens
4. Handler lee el proyecto destino (README, CLAUDE.md, package.json, pyproject.toml)
5. Detecta stack automaticamente (Next.js, FastAPI, etc.)
6. Copia archivos de MasterMind:
   - `.claude/commands/mm/` (solo los 5 comandos finales + handlers)
   - `.claude/skills/mm/` (brain-context, brain-persistence, discover, safe-commit, review, ship)
   - `.claude/agents/mm/` (7 brains + discover-planner + rediscovery-auditor + task-executor)
   - `.claude/commands/mm/db_client.py` (modulo de conexion PostgreSQL)
7. Crea `.mastermind/config.yaml` con settings detectados + conexion DB
8. **Registra proyecto en PostgreSQL** — INSERT en tabla `projects`
9. Valida que todo este en su lugar
10. Opcionalmente inicializa git hooks (GGA)

**Archivos nuevos:**
- `.claude/commands/mm/init.md` — command interface
- `.claude/commands/mm/init-handler.py` — handler logica
- `.claude/commands/mm/db_client.py` — modulo de conexion PostgreSQL (compartido por todos los handlers)

**No necesita skill ni agent.** Todo es file operations mecanicas + verificacion de servicios.

---

### 4.2 `/mm:review` — Code Review con Brains

**Interfaz:**
```bash
/mm:review                        # Review de cambios uncommitted
/mm:review --staged               # Review solo staged changes
/mm:review --branch main          # Review diff vs branch
/mm:review --files src/app.ts     # Review archivos especificos
/mm:review --last-commit          # Review ultimo commit
```

**Flujo:**
1. Handler detecta scope del review (git diff, staged, branch diff, archivos)
2. Genera payload con diff/code + contexto del proyecto
3. Lanza agent `code-reviewer` que consulta Brain #6 (QA) y Brain #7 (Growth)
4. Agent genera reporte con:
   - Correctness: logica correcta, edge cases
   - Readability: nombres, estructura, complejidad
   - Architecture: patrones, dependencias, coupling
   - Security: vulnerabilidades, input validation
   - Performance: N+1, memory leaks, bundle size
5. **Escribe en PostgreSQL:**
   - `brain_consultations` — cada consulta a Brain #6 y #7 (input, output, confidence)
   - `brain_feedback` — aprendizajes del review
   - `artifacts` — referencia al archivo de reporte generado
6. Reporte se guarda en `.planning/REVIEWS/<timestamp>-review.md`

**Archivos nuevos:**
- `.claude/commands/mm/review.md` — command interface
- `.claude/commands/mm/review-handler.py` — handler logica
- `.claude/skills/mm/review/SKILL.md` — skill protocolo
- `.claude/agents/mm/code-reviewer/code-reviewer.md` — agent ejecucion

---

### 4.3 `/mm:ship` — Tag + Archive + Cleanup

**Interfaz:**
```bash
/mm:ship                          # Ship completo: verify -> tag -> archive
/mm:ship --verify                 # Solo verificar (dry-run)
/mm:ship --tag v1.0.0             # Crear tag especifico
/mm:ship --archive                # Solo archivar artefactos
/mm:ship --cleanup                # Limpiar artefactos temporales
```

**Flujo:**
1. Handler verifica pre-condiciones:
   - Todos los tests pasan (frontend + backend)
   - No hay cambios uncommitted
   - `SPEC.md` y `tasks/todo.md` existen
2. Lee version actual de git tags
3. Genera payload con estado del proyecto
4. Lanza agent `ship-executor` que:
   - Ejecuta suite completa de tests
   - Genera changelog desde ultimo tag
   - Crea git tag semantico (patch/minor/major)
   - Mueve `tasks/` a `.planning/archive/<version>/`
   - Limpia artefactos temporales (`.agent-*-running`, `task-progress.json` viejos)
   - Actualiza `.mastermind/config.yaml` con version
5. **Escribe en PostgreSQL:**
   - `decisions` — registro del ship (version, tests result, changelog)
   - `artifacts` — referencia al archive generado
   - `dev_sessions` — actualiza estado de sesion a `completed`
6. Muestra resumen del ship

**Archivos nuevos:**
- `.claude/commands/mm/ship.md` — command interface
- `.claude/commands/mm/ship-handler.py` — handler logica
- `.claude/skills/mm/ship/SKILL.md` — skill protocolo
- `.claude/agents/mm/ship-executor/ship-executor.md` — agent ejecucion

---

### 4.4 `/mm:discover` — Sin Cambios

Ya funciona. No se toca. Genera SPEC.md + plan.md + todo.md.

### 4.5 `/mm:complete-task` — Sin Cambios

Ya funciona. No se toca. Ejecuta subtareas: build -> test -> review -> commit.

---

## 5. File Structure

### 5.1 Archivos Existentes (NO TOCAR)

```
.claude/commands/mm/
  discover.md              # Comando discover
  discover-handler.py      # Handler discover
  complete-task.md         # Comando complete-task
  complete-task-handler.py # Handler complete-task

.claude/skills/mm/
  discover/SKILL.md        # Skill discover
  brain-context/           # Skill brain-context
  brain-persistence/       # Skill brain-persistence
  mastermind-consultant/   # Skill mastermind-consultant
  safe-commit/             # Skill safe-commit (SE MANTIENE)

.claude/agents/mm/
  discover-planner/        # Agent discover (nuevo proyecto)
  rediscovery-auditor/     # Agent rediscovery (proyecto existente)
  task-executor/           # Agent task executor
  brain-01-product/        # Brain #1
  brain-02-ux/             # Brain #2
  brain-03-ui/             # Brain #3
  brain-04-frontend/       # Brain #4
  brain-05-backend/        # Brain #5
  brain-06-qa/             # Brain #6
  brain-07-growth/         # Brain #7
  global-protocol.md       # Protocolo global
```

### 5.2 Archivos Nuevos (CREAR)

```
.claude/commands/mm/
  init.md                  # Comando init
  init-handler.py          # Handler init (handler-only, sin skill/agent)
  review.md                # Comando review
  review-handler.py        # Handler review
  ship.md                  # Comando ship
  ship-handler.py          # Handler ship

.claude/skills/mm/
  review/SKILL.md          # Skill review protocol
  ship/SKILL.md            # Skill ship protocol

.claude/agents/mm/
  code-reviewer/           # Agent code-reviewer
    code-reviewer.md
  ship-executor/           # Agent ship-executor
    ship-executor.md

.mastermind/
  config.yaml              # Config del proyecto (creado por /mm:init)
```

### 5.3 Archivos a Eliminar (GSD Wrappers + Skills Huerfanos)

```
.claude/commands/mm/
  new-milestone.md         # Wrapper: delega a /gsd:new-milestone
  plan-phase.md            # Wrapper: delega a /gsd:plan-phase (DEPRECATED)
  execute-phase.md         # Wrapper: delega a /gsd:execute-phase
  complete-phase.md        # Wrapper: delega a /mm:execute-phase + BRAIN-FEED
  verify-task.md           # Lee artefactos GSD

.claude/skills/mm/
  plan-phase/              # Skill solo para wrapper plan-phase
    SKILL.md
    README.md
  verify-task/             # Skill solo para verify-task
    SKILL.md
    assets/
    references/

.planning/
  .agent-B2-running        # Agent marker huerfano
  .agent-D1-running        # Agent marker huerfano
  .agent-D2-running        # Agent marker huerfano
```

---

## 6. Success Criteria

### 6.1 `/mm:init`

- [ ] Ejecutar `/mm:init --target /tmp/test-project` crea `.claude/commands/mm/` en el destino
- [ ] El destino tiene `.mastermind/config.yaml` con stack detectado
- [ ] `/mm:init --check` en un proyecto ya instalado retorna success sin errores
- [ ] Handler detecta stack automaticamente (Next.js, FastAPI, etc.)
- [ ] Solo copia los 5 comandos finales (init, discover, complete-task, review, ship)

### 6.2 `/mm:review`

- [ ] `/mm:review` genera reporte en `.planning/REVIEWS/<timestamp>-review.md`
- [ ] Reporte tiene 5 secciones: correctness, readability, architecture, security, performance
- [ ] Consulta Brain #6 y Brain #7 durante review
- [ ] `/mm:review --staged` solo reviewea staged changes
- [ ] `/mm:review --last-commit` reviewea ultimo commit

### 6.3 `/mm:ship`

- [ ] `/mm:ship --verify` ejecuta tests y reporta estado sin crear tag
- [ ] `/mm:ship` crea git tag semantico (patch por defecto)
- [ ] Archiva `tasks/` a `.planning/archive/<version>/`
- [ ] Limpia archivos `.agent-*-running` huerfanos
- [ ] Falla si tests no pasan (0 failures requerido)

### 6.4 GSD Cleanup

- [ ] Eliminar 5 archivos wrapper en `.claude/commands/mm/`
- [ ] Eliminar 2 skills huerfanos (`plan-phase/`, `verify-task/`)
- [ ] Eliminar 3 agent markers huerfanos en `.planning/`
- [ ] Verificar que `/mm:discover` y `/mm:complete-task` siguen funcionando
- [ ] Verificar que `/mm:safe-commit` funciona sin cambios (no depende de GSD)

### 6.5 Flujo End-to-End

- [ ] En proyecto vacio: `/mm:init` -> `/mm:discover "idea"` -> `/mm:complete-task A1` -> `/mm:review` -> `/mm:ship`
- [ ] Cada comando se puede ejecutar independientemente
- [ ] Cero dependencias de GSD o herramientas externas
- [ ] `safe-commit` sigue funcionando como barrera cognitiva

---

## 7. Dependencies

| Dependency | Version | Uso |
|-----------|---------|-----|
| Python | 3.14 | Handlers |
| uv | latest | Python package manager |
| Node.js | via nvm | Frontend (si aplica) |
| pnpm | latest | Node.js package manager |
| Claude Code | latest | Runtime de slash commands |
| git | 2.x | Versionado, tags, diffs |

**Sin dependencias nuevas.** Todo lo que se necesita ya esta en el proyecto.

---

## 8. Risks and Mitigations

### R1: `/mm:init` copia archivos del propio MasterMind (meta-framework)

**Riesgo:** MasterMind es un framework que se instala a si mismo. Si ejecutas `/mm:init` dentro de mastermind, podria sobreescribir archivos.

**Mitigacion:** Handler detecta si el target es el propio mastermind y advierte. Si `--target` es el CWD, requiere `--force`. Si el target ya tiene `.mastermind/config.yaml`, pregunta antes de sobreescribir.

### R2: Eliminar GSD wrappers puede romper flujo existente

**Riesgo:** Si alguien esta usando `/mm:execute-phase` activamente, eliminarlo rompe su workflow.

**Mitigacion:** Verificar que no hay fases pendientes en `.planning/phases/` antes de eliminar. Documentar migracion: `/mm:execute-phase` -> `/mm:complete-task`. Los GSD wrappers originales (no `/mm:*`) siguen disponibles si el usuario tiene GSD instalado.

### R3: `/mm:review` puede ser lento con diffs grandes

**Riesgo:** Consultar brains con diffs de 1000+ lineas puede exceder context window o ser muy lento.

**Mitigacion:** Handler trunca diffs a 500 lineas por defecto. Flag `--full` para diff completo. Si el diff es > 2000 lineas, sugerir review por archivos individuales.

### R4: `/mm:ship` asume git tag semantico

**Riesgo:** Proyectos sin tags previos o con esquema de versionado diferente.

**Mitigacion:** Handler detecta ultimo tag. Si no hay tags, sugiere `v0.1.0` como primer tag. Flag `--tag vX.Y.Z` para tag explicito. Nunca auto-incrementa major sin flag explicito `--major`.

### R5: Safe-commit depende de GGA hook

**Riesgo:** `/mm:safe-commit` valida que `.pre-commit-config.yaml` existe. Proyectos sin GGA fallan.

**Mitigacion:** `/mm:init` incluye opcion para instalar GGA. `/mm:safe-commit` advierte si GGA falta pero no bloquea (solo sugiere instalar).

---

## 9. Flow Completo (Post-Implementation)

```
Proyecto vacio
    |
/mm:init                        # Instala MasterMind
    |
/mm:discover "mi idea"          # Genera SPEC + plan + todo
    |
/mm:complete-task A1            # Ejecuta tarea 1
    |
/mm:review                      # Review con brains
    |
/mm:complete-task A2            # Ejecuta tarea 2
    |
... (iterar por cada tarea)
    |
/mm:ship                        # Tag + archive + cleanup
    |
/mm:discover --existing         # Audit + re-plan para siguiente version
    |
... (loop)
```

**Independiente. Sin GSD. Sin dependencias externas. Plug-and-play.**
