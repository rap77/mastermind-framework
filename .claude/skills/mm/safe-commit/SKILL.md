---
name: mm-safe-commit
description: >
  Pre-commit cognitive barrier that enforces GGA validation and Brain #6 testing standards.
  NEVER allows --no-verify. Auto-corrects errors before commit. Integrates with Brain #6 QA.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0.0"
---

# Safe Commit — Barrera Cognitiva Pre-Commit

**Misión:** Nunca más dejar pasar un `--no-verify`. Esta skill es una barrera cognitiva REACTIVA que detecta intentos de commit y valida TODO antes de permitirlo.

## ¿Cuándo Usar?

Esta skill es REACTIVA — se activa automáticamente cuando detectás:

- Voy a ejecutar `git commit` (cualquier variante)
- El usuario dice "commit this", "make commit", "stage + commit", "commiteá esto"
- Acabo de editar archivos y el contexto sugiere que debería commitear
- Veo `--no-verify` en cualquier comando git

**No esperés a que el usuario lo pida.** Si vas a commitear, usá esta skill.

## Reglas Críticas — NO Negociables

### ❌ NUNCA permitas `--no-verify`

Si detectás `--no-verify` en un comando git:

```bash
# DETENER Y EXPLICAR
```

"Esperá, loco. ¿Por qué `--no-verify`? Te explico por qué es PELIGROSO:

- GGA valida seguridad (no commiteás secrets sin querer)
- GGA valida ARIA (accessibility no es opcional)
- GGA valida performance (no mandás código lento a prod)
- El hook está en `.pre-commit-config.yaml` en el ROOT por diseño

Si el hook falla, arreglá el error. No lo salteés."

### ✅ Tests deben pasar (0 fallas toleradas)

Lee los comandos de test desde `.mastermind/config.yaml` del proyecto. Si no existe, usá las convenciones del stack detectado:
- Python → `uv run pytest`
- Node.js/Next.js → `pnpm test run` o `pnpm --prefix <app-dir> test run`

**Cero fallas pre-existentes** — Brain #6 no acepta "ya venía fallando".

Si algún test falla, lo arreglás ANTES de commitear. No es opcional.

### ✅ Formato de commit convencional

```
type(scope): description

[opcional body]

[opcional footer]
```

Types permitidos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

**NUNCA** agregues "Co-Authored-By: AI" — eso es atribución automática de GGA.

### ✅ GGA hook configurado

Verificar que `.pre-commit-config.yaml` existe en el ROOT del repo.

```bash
# Si no existe, explicarle por qué es necesario
ls -la "$(git rev-parse --show-toplevel)/.pre-commit-config.yaml"
```

## Checklist Pre-Commit

Antes de ejecutar `git commit`, validar:

1. **Detectar `--no-verify`** → BLOQUEAR con explicación
2. **Ejecutar tests** → Backend + frontend deben pasar
3. **Verificar GGA** → Hook configurado en ROOT
4. **Validar mensaje** → Formato convencional correcto
5. **Verificar atribución** → Sin "Co-Authored-By"

## Integración con Brain #6 (QA/DevOps)

Brain #6 es el Reliability Fundamentalist. Antes de commitear:

```python
# Consultar Brain #6 para validar estrategia de testing
mcp__notebooklm-mcp__notebook_query(
    notebook_id="BRAIN_06_QA_DEVOPS",
    query="""
    Project: {project_name} (from .mastermind/config.yaml)
    Context: Pre-commit validation
    Stack: {stack} (from .mastermind/config.yaml)

    Questions:
    - ¿Esta change tiene test coverage adecuado?
    - ¿Hay tests que pueden fallar en CI por dependencias externas?
    - ¿El mensaje de commit sigue convencional commits?
    - ¿Hay algún riesgo de introducir regressions?

    Constraints:
    - Test commands: read from .mastermind/config.yaml or infer from stack
    - pnpm NO npm, uv NO pip
    - Hooks desde ROOT, no desde subdirectorios
    """
)
```

**Correcciones de Brain #6 que siempre respetás:**
- ✅ pnpm no npm
- ✅ uv no pip
- ✅ Tests desde el subdirectorio correcto (leer de `.mastermind/config.yaml`)
- ✅ Hooks desde ROOT del repo (`git rev-parse --show-toplevel`)
- ✅ Cero tolerancia a fallas pre-existentes

## Flujo de Auto-Correción

Si algo falla en el checklist:

### Tests fallan
```bash
# Corregir ANTES de commitear
cd apps/api && uv run pytest  # Ver qué falla
# Arreglar los tests que rompiste
# Volver a ejecutar hasta que pase todo
```

### GGA falla
```bash
# Ver qué validación falló
pre-commit run --all-files
# Arreglar errores de formato, ARIA, performance
# Volver a ejecutar hasta que pase
```

### Formato incorrecto
```
❌ "Updated feature X"
✅ "feat(product): add X validation"

❌ "Fix bug"
✅ "fix(auth): resolve JWT expiration edge case"
```

### Atribución AI
```
❌ "Co-Authored-By: Claude Code <noreply@anthropic.com>"
✅ (nada — GGA lo agrega automáticamente)
```

## Comandos

| Comando | Qué hace |
|---------|----------|
| `/mm:safe-commit` | Valida TODO y commitea cambios staged |
| `/mm:safe-commit --check` | Solo checkea, no commitea (dry-run) |
| `/mm:safe-commit --fix` | Auto-corrige issues y luego commitea |

## Mensajes de Error — Explicaciones Claras

### Por qué `--no-verify` es peligroso

```
Lo loco, te explico por qué NUNCA usar --no-verify:

1. Seguridad: GGA detecta secrets en el código antes de que lleguen al repo
2. ARIA: Validamos accessibility en cada commit — no es algo "para después"
3. Performance: GGA rechaza código lento antes de que entre a master
4. Consistencia: Todos los commits pasan por las mismas validaciones

Si el hook falla, es porque algo está mal. Arreglá el problema, no salteás la barrera.
```

### Qué tests deben pasar

```
Lee .mastermind/config.yaml para saber qué tests correr en este proyecto.
Si no hay config, inferí desde el stack (Python → uv run pytest, Node → pnpm test run).

Si rompiste tests, arreglás lo que rompiste. No es opcional.

Brain #6 dice: "Untested code is not a feature. It is a liability with a delayed activation date."
```

### Cómo arreglar issues comunes

```
Tests fallan en backend:
  cd apps/api && uv run pytest  # Ver qué rompiste
  # Arreglar los tests
  # Volver a ejecutar hasta que pase todo

Tests fallan en frontend:
  pnpm --prefix apps/web test run
  # Arreglar los tests
  # Volver a ejecutar

GGA falla:
  pre-commit run --all-files
  # Arreglar errores de formato/ARIA/performance
  # Volver a ejecutar

Formato de commit incorrecto:
  feat(scope): description
  # Type: feat, fix, docs, style, refactor, perf, test, chore
  # Scope: módulo afectado (auth, product, etc.)
  # Description: imperativo, en inglés, sin mayúscula al final
```

## Protocolo de Memoria

Después de la primera vez que uses esta skill, guardala en memoria:

```python
mcp__plugin_engram_engram__mem_save(
    title="Safe commit skill activated -- --no-verify blocked",
    type="pattern",
    content="""
    **What**: Activated mm-safe-commit skill to block --no-verify attempts
    **Why**: User documented rule 4x but I kept ignoring it. Cognitive barrier needed.
    **Where**: .claude/skills/mm/safe-commit/SKILL.md
    **Learned**: --no-verify bypasses GGA (security, ARIA, performance). Never allow it.
    """,
    project="mastermind"
)
```

## Ejemplo de Uso

```bash
# Usuario dice "commiteá esto"
# → Activar skill automáticamente

# 1. Detectar: ¿Hay --no-verify? No → OK
# 2. Tests backend (según .mastermind/config.yaml o stack detectado) → passing ✅
# 3. Tests frontend (según .mastermind/config.yaml o stack detectado) → passing ✅
# 4. GGA: pre-commit run --all-files → passing ✅
# 5. Mensaje: feat(qa): add safe-commit skill → OK ✅
# 6. Commit: git commit -m "feat(qa): add safe-commit skill"
```

```bash
# Usuario dice "commiteá esto con --no-verify"
# → ACTIVAR BARRERA COGNITIVA

"¡PARÁ! ¿Por qué --no-verify? Te explico por qué es peligroso..."

# Esperar a que el usuario entienda o corrija el comando
```

## Referencias del Proyecto

- **Brain #6 QA/DevOps**: `.claude/agents/mm/brain-06-qa/brain-06-qa.md`
- **GGA Hook**: `.pre-commit-config.yaml` (en ROOT del repo)
- **Test Commands**: leer de `.mastermind/config.yaml` → campo `test_commands` (si existe), o inferir desde `stack`
- **Package Managers**: uv (Python), pnpm (Node.js)
- **Config**: `.mastermind/config.yaml` — fuente de verdad para stack y comandos del proyecto

---

**Remember:** This is a COGNITIVE BARRIER, not just a tool. It stops you from making mistakes before they happen.
