# Fix: GGA + Claude Code — Sesión Anidada

**Fecha:** 2026-03-08
**Versión GGA:** 2.6.2 → 2.7.2
**Problema:** `git commit` desde Claude Code fallaba con GGA como pre-commit hook

---

## El Problema

GGA llama internamente a `claude --print` como subprocess para hacer code review.
Cuando se ejecuta desde dentro de una sesión de Claude Code, el CLI de Claude detecta
una sesión anidada y falla:

```
Error: Claude Code cannot be launched inside another Claude Code session.
Nested sessions share runtime resources and will crash all active sessions.
To bypass this check, unset the CLAUDECODE environment variable.
```

Las variables de ambiente que Claude Code inyecta al proceso:

```bash
CLAUDECODE=1
CLAUDE_CODE_ENTRYPOINT=cli
```

---

## Diagnóstico

### Paso 1 — Identificar que claude CLI falla como subprocess

```bash
timeout 10 claude -p "say OK" 2>&1
# → Error: Claude Code cannot be launched inside another Claude Code session.
```

### Paso 2 — Confirmar que unset de vars no es suficiente en el pipe

```bash
# El unset en bash -c funciona para el proceso, pero NO para ambos lados del pipe
# porque A | B crea subshells independientes
bash -c 'unset CLAUDECODE && printf "ok" | claude --print'
# → cuelga o falla según versión
```

### Paso 3 — Identificar dónde GGA llama a claude en cada versión

**GGA ≤ 2.6.x** — usaba `execute_claude()` en `lib/providers.sh`:
```bash
execute_claude() {
  printf '%s' "$prompt" | claude --print 2>&1
}
```

**GGA 2.7.x** — cambió a `execute_provider_with_timeout()` con `bash -c` inline:
```bash
execute_with_timeout "$timeout" "Claude" bash -c "printf '%s' \"\$1\" | claude --print 2>&1" -- "$prompt"
```

> **El fix en `.pre-commit-config.yaml` con `unset CLAUDECODE` estaba en el proceso
> padre, pero NO propagaba correctamente al `bash -c` inline de `execute_with_timeout`.**

---

## Solución

### Paso 1 — Actualizar GGA a la última versión

```bash
brew upgrade gga
# 2.6.2 → 2.7.2
```

### Paso 2 — Aplicar el fix en `execute_provider_with_timeout`

Archivo: `/home/linuxbrew/.linuxbrew/Cellar/gga/2.7.2/libexec/lib/providers.sh`

**Antes (línea ~801):**
```bash
claude)
  execute_with_timeout "$timeout" "Claude" bash -c "printf '%s' \"\$1\" | claude --print 2>&1" -- "$prompt"
  ;;
```

**Después:**
```bash
claude)
  execute_with_timeout "$timeout" "Claude" bash -c "unset CLAUDECODE; unset CLAUDE_CODE_ENTRYPOINT; printf '%s' \"\$1\" | claude --print 2>&1" -- "$prompt"
  ;;
```

El `unset` debe estar **dentro del mismo `bash -c`** que ejecuta el pipe, no en un proceso padre.

### Paso 3 — Revertir cambios innecesarios al `.pre-commit-config.yaml`

La entrada original es correcta y suficiente:

```yaml
- id: gga
  name: Gentleman Guardian Angel
  entry: bash -c 'unset CLAUDECODE && unset CLAUDE_CODE_ENTRYPOINT && gga run'
  language: system
  pass_filenames: false
  stages: [pre-commit]
```

### Paso 4 — Verificar

```bash
# Stagear algún archivo y commitear normalmente desde Claude Code
git add <archivo>
git commit -m "test: verificar GGA funcionando"
# → Debe mostrar GGA review y Passed
```

---

## Por qué pasa esto en cada versión

| Versión GGA | Cómo llama a claude | El `unset` en el entry funciona |
|-------------|--------------------|---------------------------------|
| ≤ 2.6.x | `execute_claude()` directamente | ✅ Sí, hereda del proceso padre |
| 2.7.x | `bash -c "... \| claude --print"` inline | ❌ No, el subshell inline no hereda |

---

## Nota sobre lentitud

A veces GGA tarda más de lo normal — esto es normal y depende de la carga de la API
de Claude. GGA 2.7.x introdujo un sistema de timeout con progress display:

- **Default:** 300 segundos
- **Configurable en `.gga`:**

```bash
# .gga
TIMEOUT=120  # segundos
```

---

## Reproducir el fix en futuras actualizaciones de GGA

Cada vez que GGA se actualice, verificar que el `bash -c` inline en
`execute_provider_with_timeout` incluya el `unset`:

```bash
grep -n "claude --print" /home/linuxbrew/.linuxbrew/Cellar/gga/$(gga --version | grep -oP '\d+\.\d+\.\d+')/libexec/lib/providers.sh
```

Si no tiene el `unset CLAUDECODE`, aplicar el patch manualmente.

> **Nota:** Este es un bug conocido reportado al repositorio de GGA.
> Seguir: https://github.com/Gentleman-Programming/gentleman-guardian-angel
