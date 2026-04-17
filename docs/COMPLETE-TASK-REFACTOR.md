# Plan: `/mm:complete-task` — Perfect Execution

## Context

Skills build/test/review YA EXISTEN globalmente en `~/.claude/skills/` — son compartidas.
Solo necesito refinar el flujo del comando.

**Objetivo:** Ejecución perfecta con task-executor funcional y flujo directo.

## Estado Actual

| Componente | Estado |
|------------|--------|
| Python handler | ✅ Funciona pero usa temp files innecesarios |
| task-executor agent | ✅ Existe pero necesita mejoras (retry, checkpoint) |
| Skills /build, /test, /review | ✅ Globales en ~/.claude/skills/ |
| Command .md | ⚠️ Funciona pero complejo |

## Arquitectura Nueva

```
/mm:complete-task D1
    ↓
Python Handler (refactored) — sin temp files, output estructurado
    ↓
Genera task-progress.json
    ↓
Lanza task-executor agent (directamente)
    ↓
task-executor ejecuta: /build → /test → /review → code-reviewer → /mm:safe-commit
    ↓
Checkpoint después de cada subtarea
    ↓
Notificación a sesión principal
```

## Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `.claude/commands/mm/complete-task-handler.py` | Eliminar temp files, output estructurado |
| `.claude/commands/mm/complete-task.md` | Simplificar, invocar task-executor directamente |
| `.claude/agents/mm/task-executor/task-executor.md` | Agregar retry, checkpoint granular, progreso |

---

## Fase 1: Refactor Python Handler

### 1.1 Eliminar temp files

**Antes:**
```python
with tempfile.NamedTemporaryFile(...) as f:
    json.dump(payload, f)
print(f"Payload path: {payload_path}")
```

**Después:**
- Generar estado en `.planning/task-progress.json`
- Output estructurado machine-parseable
- No más archivos temporales

### 1.2 Output estructurado

```
[mm] INFO: Task D1 initialized
[mm] TASK: D1
[mm] TITLE: All Screens Theme-Aware
[mm] SUBTASK: D1.1 pending (Command Center colors)
[mm] SUBTASK: D1.2 pending (Nexus colors)
...
[mm] GIT: 0/7 subtasks have commits
[mm] PENDING: 7 subtasks to execute
[mm] LAUNCH: task-executor
```

### 1.3 Mejorar detección git

Usar `git log --grep` en lugar de regex frágil para detectar commits existentes.

---

## Fase 2: Mejorar Task Executor Agent

### 2.1 Auto-Retry

```
Si falla fase:
  1. Log error
  2. Retry 3 veces (30s, 60s, 120s)
  3. Si sigue fallando → marcar "failed", continuar siguiente
```

### 2.2 Checkpoint Granular

Después de cada subtarea:
1. `task-progress.json` — status: "completed"
2. `mem_save` a Engram
3. Commit git (via /mm:safe-commit)

### 2.3 Progreso en Tiempo Real

```
[subtask] D1.1: build started...
[subtask] D1.1: tests (700/700) ✅
[subtask] D1.1: review (1 suggestion)
[subtask] D1.1: code-reviewer (0 critical) ✅
[subtask] D1.1: committed ✅
[checkpoint] D1.1 saved
[subtask] D1.2: build started...
```

### 2.4 Context Budget Check

```
Si context > 75%:
  1. Guardar checkpoint completo
  2. Commit: "checkpoint: D1.X context limit, resuming next session"
  3. Exit gracefully
```

---

## Fase 3: Simplificar Command .md

Command más simple que:
- Muestra usage examples
- Explica el flujo
- Enlace a task-executor agent
- Muestra cómo monitorear

---

## Verificación

### Test 1: Python handler
```bash
python3 .claude/commands/mm/complete-task-handler.py D1
# Output estructurado sin temp files
```

### Test 2: End-to-end
```bash
/mm:complete-task D1
# Verificar:
# - task-executor agent se lanza
# - skills se invocan (build → test → review → code-reviewer)
# - safe-commit valida antes de commit
# - checkpoint guardado en Engram
# - task-progress.json actualizado
```

### Test 3: Resume
```bash
# Simular context limit
/mm:complete-task D1 --continue
# Continuar desde checkpoint
```

---

## Success Criteria

1. ✅ Python handler sin temp files, output estructurado
2. ✅ task-executor con retry, checkpoint granular, progreso
3. ✅ Command.md simple y directo
4. ✅ Integration con /mm:safe-commit
5. ✅ Resume funciona desde checkpoint
6. ✅ Tests pasan post-refactor

---

## Implementación

### Día 1: Python Handler
- [ ] Eliminar tempfile dependency
- [ ] Output estructurado con prefijo `[mm]`
- [ ] Mejorar detección git con `git log --grep`
- [ ] Testear sin errores

### Día 2: Task Executor Agent
- [ ] Agregar auto-retry con exponential backoff
- [ ] Agregar checkpoint granular post-subtask
- [ ] Agregar notificaciones de progreso
- [ ] Agregar context budget check (75%)
- [ ] Integrar /mm:safe-commit

### Día 3: Command .md + Testing
- [ ] Simplificar command.md
- [ ] End-to-end test completo
- [ ] Test resume functionality
- [ ] Commit cambios
