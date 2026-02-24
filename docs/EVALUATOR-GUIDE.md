# Evaluator Skill — Guía de Uso

Guía para usar el Cerebro #7 (Evaluador Crítico) del framework Mente Maestra.

---

## Overview

El **Cerebro #7** es un meta-cerebro que evalúa TODOS los outputs de los cerebros 1-6. No crea contenido — encuentra debilidades.

### Arquitectura

```
Usuario ──► Brief ──► Cerebro #1 ──► Product Brief
                                    │
                                    ▼
                             Cerebro #7 (Evaluador)
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                 APPROVE      CONDITIONAL       REJECT
                    │               │               │
                    ▼               ▼               ▼
              Siguiente fase   Revisar y       Rehacer desde
                               re-submitir     cero
```

---

## Componentes del Evaluador

### 1. SKILL.md

System prompt principal del evaluador. Define:
- Identidad (Munger, Kahneman, Tetlock)
- Protocolo de 5 pasos
- Reglas inquebrantibles
- Preguntas que SIEMPRE hacer

**Ubicación:** `skills/evaluator/SKILL.md`

### 2. bias-catalog.yaml

10 sesgos cognitivos que detectar:

| ID | Sesgo | Signal |
|----|-------|--------|
| BIAS-01 | Confirmation Bias | Solo evidencia confirmatoria |
| BIAS-02 | Anchoring | Primer número como verdad |
| BIAS-03 | Sunk Cost | "Ya invertimos tanto" |
| BIAS-04 | Survivorship | Solo casos de éxito |
| BIAS-05 | Dunning-Kruger | Certeza sin data |
| BIAS-06 | Authority Bias | "Lo dice el experto" |
| BIAS-07 | WYSIATI | Conclusión sin info completa |
| BIAS-08 | Planning Fallacy | Estimaciones optimistas |
| BIAS-09 | Narrative Fallacy | Explicación post-hoc |
| BIAS-10 | Inversion Failure | Sin análisis de fallo |

**Ubicación:** `skills/evaluator/bias-catalog.yaml`

### 3. benchmarks.yaml

Benchmarks de industria para comparar métricas:

| Categoría | Métricas Clave |
|-----------|----------------|
| SaaS | D7/D30 retention, LTV/CAC, NPS, PMF survey |
| Marketplace | Take rate, liquidity, match rate |
| Mobile | D1/D30 retention, session duration |
| B2B | Sales cycle, deal size, NRR |

**Ubicación:** `skills/evaluator/benchmarks.yaml`

### 4. evaluation-matrices/

Matrices de evaluación por tipo de output:

```
evaluation-matrices/
├── product-brief.yaml      # Para outputs del Cerebro #1
├── ux-research-report.yaml # Para outputs del Cerebro #2 (futuro)
├── ui-design-spec.yaml     # Para outputs del Cerebro #3 (futuro)
└── ...
```

Cada matrix tiene 4 categorías:
- **Completeness**: ¿Tiene todo lo que debe tener?
- **Quality**: ¿Es bueno lo que tiene?
- **Intellectual Honesty**: ¿Hay humo?
- **Commercial Viability**: ¿Alguien pagaría?

**Ubicación:** `skills/evaluator/evaluation-matrices/`

### 5. templates/

Templates para reportes:

- `evaluation-report.yaml` — Reporte estándar de evaluación
- `escalation-report.yaml` — Para escalar al humano

**Ubicación:** `skills/evaluator/templates/`

---

## Uso del CLI

### Comando: compile-radar

Genera FUENTE-709 y FUENTE-710 desde los cerebros 1-6:

```bash
mastermind brain compile-radar --brain 07
# o
mm brain compile-radar 07
```

Este comando:
1. Lee `evaluation-criteria.md` de cada cerebro 1-6
2. Compila en `FUENTE-709-checklist-evaluacion.md`
3. Lee `anti-patrones.md` de cada cerebro 1-6
4. Compila en `FUENTE-710-antipatrones-consolidados.md`
5. Deposita en `docs/software-development/07-growth-data-brain/sources/`

### Otros comandos útiles

```bash
# Ver status del cerebro 07
mm brain status 07

# Validar fuentes del cerebro 07
mm source validate --brain 07

# Listar todas las fuentes
mm source list
```

---

## Flujo de Evaluación

### Paso 1: Intake

1. Recibir output de otro cerebro
2. Identificar tipo (product-brief, ux-report, etc.)
3. Cargar evaluation matrix correspondiente
4. Si no existe matrix → ESCALATE

### Paso 2: Evaluación

Por cada check en la matrix:
- Buscar evidencia en el output
- Si hay evidencia → PASS
- Si no hay evidencia → FAIL con instrucción específica
- Verificar contra bias-catalog
- Comparar métricas vs benchmarks

### Paso 3: Scoring

```
Score = (Puntos obtenidos × weight) / Total posible
```

| Score | Veredicto |
|-------|-----------|
| >= 80 | APPROVE |
| 60-79 | CONDITIONAL |
| < 60 | REJECT |
| 3er rechazo | ESCALATE |

### Paso 4: Veredicto

Generar evaluation-report con:
- Score numérico y por categoría
- Checks pasados con justificación
- Checks fallidos con instrucciones ESPECÍFICAS
- Sesgos detectados (nombrados explícitamente)
- Redirect instructions

### Paso 5: Registro

- Guardar en `logs/evaluations/`
- Si hay precedente → guardar en `logs/precedents/`

---

## Verificación de Implementación

Para verificar que el evaluador está correctamente implementado:

```bash
# 1. Verificar archivos creados
ls -la skills/evaluator/
# Debe mostrar: SKILL.md, protocol.md, bias-catalog.yaml, benchmarks.yaml,
#               evaluation-matrices/, templates/

# 2. Validar YAML syntax
python3 -c "import yaml; yaml.safe_load(open('skills/evaluator/bias-catalog.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('skills/evaluator/benchmarks.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('skills/evaluator/evaluation-matrices/product-brief.yaml'))"

# 3. Verificar system prompt
ls -la agents/brains/growth-data.md

# 4. Verificar comando compile-radar
mm brain compile-radar 07

# 5. Verificar fuentes generadas
ls -la docs/software-development/07-growth-data-brain/sources/
# Debe mostrar FUENTE-709 y FUENTE-710

# 6. Verificar directorio de logs
ls -la logs/evaluations/
ls -la logs/precedents/
```

---

## Test de Verificación

Existe un test brief defectuoso en `tests/fixtures/product-brief-defectuoso.md`.

Este brief tiene defectos intencionales:
- Sin métricas de éxito reales (son vanity metrics)
- Confirmation bias evidente (solo evidencia positiva)
- Sin análisis de fallo (pre-mortem)
- Problema mal definido (es una solución, no un problema)

Para probar el evaluador:
1. Leer el test brief
2. Aplicar la matrix de product-brief
3. Verificar que detecta los defectos
4. Verificar que el veredicto es REJECT o CONDITIONAL

---

## Próximos Pasos

Después de esta implementación:

1. **PRP-006:** Implementar Orquestador que coordine Cerebro #1 + Cerebro #7
2. **Testing con briefs reales:** Probar el flujo completo
3. **Cerebro #2:** UX Research (cuando se necesite)
4. **NotebookLM para Cerebro #7:** Crear notebook con las 10 fuentes (opcional)

---

## Referencias

- `docs/design/11-Cerebro-07-Evaluador-Critico.md` — Especificación completa
- `PRPs/PRP-005-brain-07-evaluator.md` — PRP de implementación
- `agents/brains/growth-data.md` — System prompt del Cerebro #7

---

**Versión:** 1.0.0
**Última actualización:** 2026-02-23
**Autor:** MasterMind Framework Team
