# Memory - MasterMind Framework

## Git Rules

### CRITICAL: NUNCA usar `--no-verify`
- **El usuario lo prohibió explícitamente**
- Si GGA hook tarda mucho, esperar a que termine
- Si hay problemas con el hook, investigar y solucionar - NO saltearlo
- **Exit code 1 no siempre significa hook falló** - podría ser interrupción de herramienta
- Esta es una regla fija, sin excepciones

## Project Notes

- Nombre del repo: **mastermind-framework**
- URL: https://github.com/rap77/mastermind-framework
- Branch principal: `master`
- Stack: Python 3.14 (uv), Node.js (nvm), Claude Code

## Progreso (2026-03-02)

### Framework Completion: 98% ✅

### ✅ Completado Esta Sesión
- **MCP Integration** (notebooklm_client, evaluator, mcp_wrapper)
- **Iteration Loop** (max 3, escalation on 3rd rejection)
- **Tests** (10/10 passing: 6 unit + 4 e2e)
- **CLI Orchestration** (validation_only flow working)

### PRPs Completados ✅
- **PRP-000**: Initial Setup & Project Structure
- **PRP-001**: mastermind-cli Implementation
- **PRP-002**: YAML Versioning en Fichas
- **PRP-006**: Framework Core - Product Strategy Brain
- **PRP-008**: CLI Orchestrate Command
- **MCP Integration**: NotebookLM + Evaluator + Iteration Loop

### CLI Implementado
```bash
# Ubicación: tools/mastermind-cli/
# Comandos:
mastermind source {new,update,validate,status,list,export}
mastermind brain {status,validate,package}
mastermind orchestrate <brief> --flow <type> --dry-run
mastermind framework {status,release}
mastermind info

# Alias: mm
```

### Cerebros Activos (7/7 en NotebookLM)
| Cerebro | NotebookLM ID | Estado |
|---------|---------------|--------|
| #1 Product Strategy | f276ccb3-0bce-4069-8b55-eae8693dbe75 | **Activo** |
| #2 UX Research | ea006ece-00a9-4d5c-91f5-012b8b712936 | **Activo** |
| #3 UI Design | 8d544475-6860-4cd7-9037-8549325493dd | **Activo** |
| #4 Frontend | 85e47142-0a65-41d9-9848-49b8b5d2db33 | **Activo** |
| #5 Backend | c6befbbc-b7dd-4ad0-a677-314750684208 | **Activo** |
| #6 QA/DevOps | 74cd3a81-1350-4927-af14-c0c4fca41a8e | **Activo** |
| #7 Growth/Data | d8de74d6-7028-44ed-b4d4-784d6a9256e6 | **Activo** |

### Testing Suite Completa (5/5 tests)
**Fecha:** 2026-02-28
**Archivo:** tests/test-results/test-suite-2026-02-28.md
**Resultados:**
- Test-01 (Bad Brief): 9/100 REJECT ✅
- Test-02 (Borderline): 68/100 CONDITIONAL ✅
- Test-03 (Good Brief): 88/100 APPROVE ✅
- Test-04 (Full Flow): 84/100 CONDITIONAL ✅
- Test-05 (Optimization): 82/100 CONDITIONAL ✅
**Accuracy:** 100% | **Confidence avg:** 87.6%
**Status:** ✅ READY FOR PRODUCTION

### Tests Unitarios (6/6)
**Fecha:** 2026-03-02
**Archivo:** tools/mastermind-cli/tests/test_orchestration.py
**Resultados:**
- Test: List Active Brains ✅
- Test: NotebookLM Client ✅
- Test: Evaluator Matrix Loading ✅
- Test: Evaluator Simple Output ✅
- Test: Evaluator Weak Output ✅
- Test: MCP Wrapper ✅

### Tests End-to-End (4/4)
**Fecha:** 2026-03-02
**Archivo:** tools/mastermind-cli/tests/test_orchestration_e2e.py
**Resultados:**
- Test: Dry Run Mode ✅
- Test: Validation Flow - Good Brief ✅
- Test: Validation Flow - Weak Brief ✅
- Test: Iteration Loop ✅

### Próximo Paso: Complete Sources (3% restante)

**Prioridad:** Media
**Objetivo:** Cargar 18 fuentes restantes para alcanzar 100/100

**Distribución actual:**
- Brain #1: 10/10 ✅
- Brain #2: ~10/20
- Brain #3: ~10/20
- Brain #4: ~10/20
- Brain #5: ~10/20
- Brain #6: ~10/20
- Brain #7: 12/12 ✅

## Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `CLAUDE.md` | Guía del proyecto para Claude Code |
| `AGENTS.md` | Reglas de code review para GGA |
| `docs/CLI-REFERENCE.md` | Documentación del CLI |
| `docs/design/00-PRD-MasterMind-Framework.md` | PRD principal |
| `tools/mastermind-cli/` | CLI implementado |

## currentDate
Today's date is 2026-03-02.
