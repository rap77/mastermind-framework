# MasterMind Framework - Testing Suite

> **Propósito:** Validar el framework completo con briefs de prueba que cubren diferentes escenarios y flujos de los 7 cerebros.

## Estructura de Tests

| Test | Tipo | Flujo Esperado | Veredicto Esperado |
|------|------|----------------|-------------------|
| 01 | Bad Brief | validation_only | **REJECT** |
| 02 | Borderline Brief | validation_only | **CONDITIONAL** |
| 03 | Good Brief | validation_only | **APPROVE** |
| 04 | Full Product | full_product | **APPROVE** (todos los cerebros) |
| 05 | Optimization | optimization | **APPROVE** (con métricas) |

## Cómo Usar

### Manual (con NotebookLM MCP)

```python
# 1. Seleccionar test brief
test_brief = read_file("tests/test-briefs/test-01-bad-brief.md")

# 2. Enviar al Orquestador
orchestrator_input = {
    "brief": test_brief,
    "flow_type": "validation_only"
}

# 3. El Orquestador debe:
#    - Detectar flujo: validation_only
#    - Invocar Brain #1 (Product Strategy)
#    - Enviar output a Brain #7 (Evaluator)
#    - Retornar veredicto esperado

# 4. Verificar veredicto
assert evaluation.veredict == expected_veredict
assert evaluation.score >= min_expected_score
```

### Con CLI (futuro)

```bash
# Ejecutar suite completa
mastermind test suite --all

# Ejecutar test específico
mastermind test brief --id 01

# Ver reporte de resultados
mastermind test report --last
```

## Matriz de Evaluación

### Brain #7 (Evaluator) - Scoring

| Score | Veredicto | Acción |
|-------|-----------|--------|
| 80-100 | APPROVE | Continuar al siguiente cerebro o entregar |
| 60-79 | CONDITIONAL | Aplicar notas y continuar/re-trabajar |
| 0-59 | REJECT | Devolver al cerebro origen con feedback |

### Criterios por Test

#### Test 01: Bad Brief (REJECT esperado)
- Métricas vanity en vez de accionables
- Confirmation bias evidente
- Sin análisis de fallo
- Problema mal definido
- Audiencia genérica
- Evidencia insuficiente

#### Test 02: Borderline Brief (CONDITIONAL esperado)
- Problema definido pero sin profundidad
- Alguna evidencia pero insuficiente
- Métricas mezcladas (vanity + accionables)
- Análisis de competencia básico
- Timeline sin baseline histórico

#### Test 03: Good Brief (APPROVE esperado)
- Problema claro y específico
- Evidencia de demanda real (entrevistas, datos)
- Métricas accionables con baseline
- Análisis de fallo (pre-mortem)
- Competencia analizada correctamente
- Timeline realista

#### Test 04: Full Product (APPROVE esperado)
- Requiere todos los cerebros #1-#6
- Cada cerebro debe producir output válido
- Brain #7 debe aprobar cada etapa
- Outputs deben ser consistentes entre cerebros

#### Test 05: Optimization (APPROVE esperado)
- Producto existente con métricas reales
- Brain #7 analiza métricas
- Brain #1 propone estrategia optimizada
- Métricas de mejora claras

## Reporte de Resultados

### Formato Esperado

```yaml
test_report:
  test_id: "TEST-01"
  brief_name: "Bad Brief - InstaEverything"
  flow_type: "validation_only"
  brains_invoked: [1, 7]
  evaluations:
    TASK-001:
      brain: 1
      output_quality: 0.45
      veredict: "REJECT"
      feedback: ["confirmation bias detectado", "métricas vanity", "sin pre-mortem"]
  expected_veredict: "REJECT"
  actual_veredict: "REJECT"
  passed: true
  notes: "Brain #7 detectó correctamente los defectos del brief"
```

## Precedents Generados

Durante las pruebas, documentar nuevos precedents cuando:
- Un cerebro comete un error repetido
- Dos cerebros tienen outputs conflictivos
- Brain #7 identifica un patrón de fallo

Los precedents se guardan en: `tests/precedents/`

---

## Próximos Pasos

1. **Ejecutar tests manualmente** con NotebookLM MCP
2. **Documentar resultados** en `test-results/`
3. **Crear precedents** para patrones identificados
4. **Refinar system prompts** según los hallazgos
5. **Automatizar** ejecución vía CLI

---

**Versión:** 1.0.0
**Fecha:** 2026-02-28
**Estado:** Ready for testing
