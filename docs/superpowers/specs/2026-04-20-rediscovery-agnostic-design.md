# Rediscovery Auditor Agnóstico — Design Spec

**Date:** 2026-04-20
**Author:** Rafael Padrón
**Status:** Approved

## Problem

El rediscovery-auditor actual asume una estructura de monorepo hardcodeada:
- `apps/web/` → pnpm test
- `apps/api/` → uv run pytest

Esto falla en proyectos con estructuras diferentes (monolitos, otros stacks).

## Solution

**Enfoque C: Híbrido Inteligente**

Detector de fingerprint → estrategias por stack → orchestrator mergea resultados.

## Architecture

### Components

```
rediscovery-auditor/
├── core/
│   ├── detector.py       # Fingerprint del proyecto
│   ├── strategies/
│   │   ├── base.py       # Interface común
│   │   ├── python.py     # Estrategia Python
│   │   ├── node.py       # Estrategia Node.js
│   │   └── rust.py       # Estrategia Rust
│   └── orchestrator.py   # Coordina estrategias
└── rediscovery-auditor.md
```

### Flow

```
1. Detector → fingerprint (stacks, estructura, herramientas)
2. Orchestrator → mapea fingerprint a estrategias
3. Cada estrategia → valida + ejecuta análisis
4. Orchestrator → mergea resultados
5. Brain #1 + #7 → rediscovery con contexto completo
```

## Component Specification

### 1. Fingerprint Detector

**Input:** Filesystem del proyecto

**Output:**
```json
{
  "type": "monolito" | "monorepo",
  "stacks": ["python", "node", "rust"],
  "structure": {
    "python": {
      "src": ["mastermind/", "routers/"],
      "tests": ["tests/"],
      "package_manager": "uv",
      "test_runner": "pytest"
    }
  }
}
```

**Detection rules:**
- `pyproject.toml` / `requirements.txt` → Python stack
- `package.json` → Node stack
- `Cargo.toml` → Rust stack
- `apps/` / `packages/` / `services/` → Monorepo pattern

### 2. Project Strategy (Base Interface)

```python
class ProjectStrategy(ABC):
    @abstractmethod
    def validate(self) -> bool:
        """Verifica que las herramientas existan"""
        pass

    @abstractmethod
    def run_tests(self) -> dict:
        """Ejecuta tests y retorna resultados"""
        pass

    @abstractmethod
    def analyze_deps(self) -> dict:
        """Analiza dependencies outdated"""
        pass

    @abstractmethod
    def analyze_code(self) -> dict:
        """Analiza estructura de código (fd + rg)"""
        pass

    @abstractmethod
    def get_coverage(self) -> float | None:
        """Retorna coverage si existe"""
        pass
```

### 3. Python Strategy

**Validation:**
- Check if `uv` or `pip` exists
- Check if `pytest` exists
- Check if `tests/` directory exists

**Test execution:**
- Try: `uv run pytest`
- Fallback: `python -m pytest`
- Parse: passing, failing, skipped

**Dependency analysis:**
- `uv pip list --outdated`
- Count outdated packages
- Flag security vulnerabilities

### 4. Node Strategy

**Validation:**
- Check if `pnpm` or `npm` or `yarn` exists
- Check if `vitest` or `jest` exists

**Test execution:**
- Try: `pnpm test -- --run`
- Fallback: `npm test -- --run`
- Parse: test results

### 5. Rust Strategy

**Validation:**
- Check if `cargo` exists

**Test execution:**
- `cargo test`
- Parse: test results

**Additional:**
- `cargo clippy` for lints
- `cargo outdated` for deps

### 6. Orchestrator

```python
class Orchestrator:
    def __init__(self, fingerprint):
        self.strategies = self._load_strategies(fingerprint)

    def execute_all(self) -> dict:
        results = {}
        for strategy in self.strategies:
            if strategy.validate():
                results[strategy.name] = {
                    "tests": strategy.run_tests(),
                    "deps": strategy.analyze_deps(),
                    "code": strategy.analyze_code(),
                    "coverage": strategy.get_coverage()
                }
            else:
                results[strategy.name] = {
                    "status": "skipped",
                    "reason": "Tooling not available"
                }
        return results
```

### 7. Rediscovery Integration

**Contexto completo a Brain #1:**
```python
full_context = {
    "fingerprint": fingerprint,
    "health": orchestrator_results,
    "files": context_files,
    "git": git_info,
    "code_analysis": code_stats
}
```

**Brain #1 recibe:**
- Project fingerprint
- Health check results por stack
- Original promise (SPEC.md)
- Current state (git log)

**Brain #7 evalúa:**
- Calidad del contexto
- Qué stack está en peor estado
- Riesgos por stack

## Error Handling

**Graceful degradation:**
- Cada operación tiene try-except
- Nunca falla fatal, siempre reporta
- Status codes: ✅ ⚠️ ❌ ⏭️

**Ejemplo:**
```python
try:
    test_results = strategy.run_tests()
except Exception as e:
    test_results = {
        "status": "error",
        "reason": str(e),
        "suggestion": "Check if test runner is installed"
    }
```

## Output Files

**HEALTH-CHECK.md:**
```markdown
# Project Health Check

## Python Stack
- ✅ Tests: 631 passing, 0 failing
- ⚠️ Coverage: 78% (target: 80%)
- ✅ Dependencies: 0 outdated

## Node Stack
- ⏭️ Skipped (no Node.js detected)
```

**GAPS.md:**
- Features promised vs delivered
- Gaps por stack
- Blockers por stack

**SPEC.md (updated):**
- Regenerado con estado actual

**tasks/plan.md (regenerated):**
- Solo lo que falta (gaps)

**tasks/todo.md (regenerated):**
- Checklist actualizado

## Implementation Plan

1. **Fase 1: Core Detector**
   - Implementar detector.py
   - Test con diferentes estructuras

2. **Fase 2: Python Strategy**
   - Implementar estrategia Python completa
   - Test con proyecto actual

3. **Fase 3: Node + Rust Strategies**
   - Implementar estrategias Node y Rust
   - Test con proyectos de ejemplo

4. **Fase 4: Orchestrator**
   - Implementar coordinador
   - Test merge de resultados

5. **Fase 5: Rediscovery Integration**
   - Integrar con Brain #1 + #7
   - Test end-to-end

## Success Criteria

- ✅ Funciona en monolito Python (proyecto actual)
- ✅ Funciona en monorepo (apps/api, apps/web, rust_control_plane)
- ✅ Detecta y analiza Node.js si existe
- ✅ Detecta y analiza Rust si existe
- ✅ Graceful degradation si herramienta no existe
- ✅ HEALTH-CHECK.md siempre se genera
- ✅ Brain #1 + #7 reciben contexto completo

## Future Extensions

- Go strategy
- Java strategy
- Plugins community (open source)
- Config file personalizable (.rediscoveryrc)
