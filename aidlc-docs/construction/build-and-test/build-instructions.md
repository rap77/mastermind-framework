# Build Instructions — UOW-5 verification-review-recovery-v1

## Prerequisites

- **Build Tool**: `uv` + Python 3.14
- **Dependencies**: `apps/api/pyproject.toml` resolved, local venv usable by `uv run`
- **Environment Variables**:
  - `UV_CACHE_DIR=/tmp/uv-cache` recomendado en este entorno
- **System Requirements**:
  - acceso de escritura a `/tmp`
  - repo en estado consistente

## Build Steps

### 1. Enter API Workspace

```bash
cd apps/api
```

### 2. Prepare Temporary UV Cache

```bash
export UV_CACHE_DIR=/tmp/uv-cache
mkdir -p "$UV_CACHE_DIR"
```

### 3. Resolve Runtime Environment

```bash
uv sync --all-groups
```

### 4. Verify Python Package Imports

```bash
uv run python -c "from mastermind_cli.orchestrator.runtime_contracts import LoopSelector, CapabilityRegistry, HarnessRegistry, VerificationHarness, ReviewHarness, RecoveryHarness"
```

### 5. Verify Focused Slice Files Parse

```bash
uv run python -m compileall mastermind_cli/orchestrator/runtime_contracts mastermind_cli/orchestrator/stateless_coordinator.py
```

## Verify Build Success

- **Expected Output**:
  - `uv sync` sin errores
  - imports exitosos
  - `compileall` sin fallos
- **Build Artifacts**:
  - entorno resuelto en `apps/api/.venv`
  - bytecode temporal de Python si aplica
- **Common Warnings**:
  - warning de `tool.uv.dev-dependencies` deprecated es tolerable si no bloquea

## Troubleshooting

### UV Lock / Temp File Error
- **Cause**: cache default no escribible
- **Solution**:
  1. `export UV_CACHE_DIR=/tmp/uv-cache`
  2. reintentar el comando

### Missing Test Runner or Dev Dependency
- **Cause**: entorno no sincronizado
- **Solution**:
  1. `cd apps/api`
  2. `uv sync --all-groups`
  3. reintentar
