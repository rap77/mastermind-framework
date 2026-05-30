# Discover Objective Template

Template usado por `/mm:discover` para crear packages de objectives.

## Instrucciones

1. **Revisar canonical docs existentes** — antes de generar, buscar en `docs/canonical/` cualquier doc relacionado con el objetivo. Si existe uno (ej: `docs/canonical/48-MM-CLI-DESIGN.md`), usarlo como base para requirements y design.

2. **Revisar el BRIEF del usuario** — el brief de entrada es la fuente primaria. No inventar features fuera del scope mencionado.

3. **Si NO hay canonical doc existente**, usar este template tal cual.

4. **Si HAY canonical doc existente**:
   - Copiar la sección `## Purpose`, `## Scope`, `## Non-negotiables` al requirements.md
   - Copiar la sección `## Arquitectura`, `## Commands`, `## Comandos en detalle` al design.md
   - Extraer las tasks del canonical doc si tiene sección de tasks
   - Mantener los archivos del canonical doc como `docs/canonical/XX-*.md` — NO moverlos

5. **Siempre incluir dual interface** — todo command nuevo debe documentar CLI + slash command + mismo handler.

---

## requirements.md template

```markdown
# Requirements — {{objective_slug}}

## Problem / Purpose

[1-3 oraciones: qué problema resuelve este objetivo. Basado en el brief del usuario.]

## Stakeholders / Users

- **Primary:** [quién usa esto directamente]
- **Secondary:** [quién se beneficia indirectamente]

## Dual Interface

Todo command existe en CLI y slash command, mismo handler subyacente:

| CLI | Slash Command | Handler |
|-----|---------------|---------|
| `mm <command>` | `/mm:<command>` | `*-handler.py` |

[Si hay commands nuevos, listarlos con su handler]

## Scope

### In Scope

- [Feature o capability principal]
- [Features secundarios]

### Out of Scope

- [Lo que NO se va a hacer]
- [Lo que está fuera del objetivo]

## Non-negotiables

- [Regla inquebrantable 1]
- [Regla inquebrantable 2]

## Acceptance Criteria

- [ ] [Criterio medible 1]
- [ ] [Criterio medible 2]
- [ ] [Criterio medible 3]
```

---

## design.md template

```markdown
# Design — {{objective_slug}}

## Arquitectura

[Descripción de la arquitectura. Si hay un canonical doc existente, usar esa sección. Si no, describir:

- Componentes principales
- Conexiones entre componentes
- Capas si aplica (ej: CLI → handler → service)]

## Dual Interface

```
┌─────────────────────────────────────┐
│           CLI (terminal)             │
│  mm <command> [args]                 │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│         Python Handler                │
│  .mm-flow/commands/mm/<name>.py    │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│        Slash Command (Claude Code)   │
│  /mm:<command> [args]               │
└─────────────────────────────────────┘
```

[Si hay components nuevos, documentarlos aquí]

## Technical Approach

- [Decisión técnica 1 con justificación]
- [Decisión técnica 2 con justificación]

## Dependencies

- [Dependencia 1: qué es, por qué se necesita]
- [Dependencia 2]

## Validation Strategy

- [Cómo se valida que el código funciona]
- [Comandos de validación específicos]
```

---

## tasks.md template

```markdown
# Tasks — {{objective_slug}}

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

---

## T1: [Nombre de la primera task]

### Purpose

[1-2 oraciones: qué resuelve esta task]

### Depends On
None (T1 siempre empieza sin dependencies)

### Files / Areas Touched

- `path/to/file1.py`
- `path/to/file2.md`

### Validation Commands

```bash
# Comando para verificar que la task está bien
[comando de validación]
```

### Acceptance Criteria

- [ ] [Criterio 1]
- [ ] [Criterio 2]

---

## T2: [Nombre de la segunda task]

### Purpose

[1-2 oraciones]

### Depends On
T1

### Files / Areas Touched

- [Archivos afectados]

### Validation Commands

```bash
[comando]
```

### Acceptance Criteria

- [ ] [Criterio 1]

---

## T3: [Nombre de la tercera task]

### Purpose

[1-2 oraciones]

### Depends On
T2

### Files / Areas Touched

- [Archivos]

### Validation Commands

```bash
[comando]
```

### Acceptance Criteria

- [ ] [Criterio 1]

---

## T4: Close continuity loop

### Purpose

Refresh handoff y validation paraarchivar el objective.

### Depends On
T3

### Files / Areas Touched

- `HANDOFF-CURRENT.md`
- `execution-state.json`

### Validation Commands

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective {{objective_slug}}
```

### Acceptance Criteria

- [ ] HANDOFF-CURRENT.md actualizado con siguiente objective recomendado
- [ ] `discover-contract-check` pasa
- [ ] Objective listo para archivar
```

---

## Canonical Doc Reference (para enrichment)

Cuando generes un objective, revisá estos lugares por canonical docs existentes:

1. `docs/canonical/*.md` — buscar docs con contenido relacionado
2. `docs/canonical/XX-*.md` — cualquier doc numerado
3. `docs/canonical/project-adapter/` — si es sobre project setup

Si encontrás un canonical doc relevante:
- NO mover ni eliminar el canonical doc
- Copiar la información relevante al objective
- El canonical doc sigue siendo el source of truth a largo plazo
- El objective es la extracción ejecutable del canonical doc

---

## Dual Interface Checklist

Para cada command en el objective, verificar:

- [ ] CLI command existe (`mm <command>`)
- [ ] Slash command existe (`/mm:<command>`)
- [ ] Handler existe (`.mm-flow/commands/mm/*-handler.py`)
- [ ] Mismo handler para ambas interfaces
- [ ] Flags consistentes (`--json`, `--verbose`, etc.)

## Códigos de salida estándar

| Code | Significado |
|------|-------------|
| `0` | Success |
| `1` | Error genérico |
| `2` | Objective no encontrado |
| `3` | Validación fallida |
| `4` | Task bloqueada o incompleta |
