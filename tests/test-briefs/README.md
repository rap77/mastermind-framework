# MasterMind Framework - Testing Suite

> **Propósito:** Validar el framework completo con briefs de prueba que cubren diferentes escenarios y flujos de los cerebros.

## Estructura de Tests

### Nicho Software Development (Brain #1-#7)

| Test | Tipo | Flujo Esperado | Veredicto Esperado |
|------|------|----------------|-------------------|
| 01 | Bad Brief | validation_only | **REJECT** |
| 02 | Borderline Brief | validation_only | **CONDITIONAL** |
| 03 | Good Brief | validation_only | **APPROVE** |
| 04 | Full Product | full_product | **APPROVE** (todos los cerebros) |
| 05 | Optimization | optimization | **APPROVE** (con métricas) |

### Nicho Marketing Digital (Brain M1-M16)

| Test | Tipo | Cerebros Involucrados | Veredicto Esperado |
|------|------|----------------------|-------------------|
| MARKETING-01 | Brand Awareness (App Launch) | M1, M2, M3, M4, M9, M15, M16 | **APPROVE** con recomendaciones |
| MARKETING-02 | B2B Lead Gen (SaaS) | M1, M3, M5, M6, M9, M11, M12, M13, M16 | **APPROVE** con gaps identificados |
| MARKETING-03 | Ecommerce CRO (Fashion) | M1, M2, M3, M6, M7, M8, M11, M12, M16 | **APPROVE** con optimización prioritaria |
| MARKETING-04 | B2B Retention (SaaS) | M1, M9, M10, M11, M13, M15, M16 | **APPROVE** con retention-first mindset |

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

### Marketing Digital Tests

#### Test MARKETING-01: Brand Awareness (APPROVE esperado)
- App de fitness para millennials
- Estrategia multi-channel con $15k budget
- Pre-lanzamiento + community building
- Métricas de awareness + conversión

#### Test MARKETING-02: B2B Lead Gen (APPROVE esperado)
- SaaS B2B project management
- Goal: 200 → 500 leads/mes
- Funnel optimization + lead scoring
- Multi-touch attribution

#### Test MARKETING-03: Ecommerce CRO (APPROVE esperado)
- Moda sustentable ecommerce
- Conversión 0.8% → 1.5% target
- Funnel leak identification
- Retention focus (70% churn)

#### Test MARKETING-04: B2B Retention (APPROVE esperado)
- SaaS email marketing automation
- Churn 5% → 3% monthly
- Health scoring + lifecycle emails
- Onboarding optimization

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

**Versión:** 1.3.0
**Fecha:** 2026-03-12
**Estado:** Ready for Marketing Digital testing
**Nuevos:** 4 tests E2E para Marketing Digital (M1-M16)
