# PRP-005: Cerebro #7 - Evaluador Crítico con Evaluator Skill

**Status:** Ready to Implement
**Priority:** High
**Estimated Time:** 3-4 hours
**Dependencies:** PRP-003 (system prompts), PRP-004 (NotebookLM integration - opcional para fase inicial)

---

## Executive Summary

Implementar el Cerebro #7 (Evaluador Crítico / Growth & Data) con su skill de evaluación completa. Este cerebro evalúa en tiempo real todos los outputs de los cerebros 1-6, detectando sesgos cognitivos, verificando calidad, y aprobando/rechazando propuestas.

El entregable incluye:
- Evaluator Skill completa con 8 archivos
- System prompt del Cerebro #7
- Comando CLI `compile-radar` para generar fuentes consolidadas
- Test de verificación con brief defectuoso

---

## Context from Clarification Session

### Decisiones Arquitectónicas

| # | Decisión | Impacto |
|---|-----------|---------|
| 1 | Cerebro #7 es meta-cerebro, no crea, evalúa | Su conocimiento es sobre criterios de evaluación, no dominio específico |
| 2 | Evaluator Skill es separada del cerebro | Skill puede usarse standalone, cerebro la usa como herramienta |
| 3 | FUENTE-709 y FUENTE-710 son generadas | Se regeneran cada vez que un cerebro actualiza sus criterios |
| 4 | 4 veredictos: APPROVE, CONDITIONAL, REJECT, ESCALATE | Permite iteración sin bloqueo indefinido |
| 5 | Bias catalog basado en ciencia (Kahneman, Munger, Tetlock) | Detección de sesgos con base en investigación |

### Expertos del Cerebro #7

| Experto | Aporte | Fuentes |
|---------|--------|---------|
| Charlie Munger | Inversión del problema, modelos mentales | Poor Charlie's Almanack |
| Daniel Kahneman | Sesgos cognitivos, Sistema 1/2 | Thinking, Fast and Slow |
| Philip Tetlock | Calibración de predicciones, superforecasting | Superforecasting |
| Alex Hormozi | Propuesta de valor, pricing | $100M Offers |
| Sean Ellis | Growth frameworks, north star metric | Hacking Growth |
| Andrew Chen | Network effects, cold start | The Cold Start Problem |
| Rolf Dobelli | Sesgos cognitivos prácticos | Art of Thinking Clearly |
| Lenny Rachitsky | Benchmarks de industria SaaS | Newsletter compilations |

---

## External Resources

### Documentación Principal
- **docs/design/11-Cerebro-07-Evaluador-Critico.md** - Especificación completa del cerebro (LEER ANTES DE EMPEZAR)

### Prompt Engineering
- https://docs.anthropic.com/claude/docs/prompt-engineering - Prompt structure
- https://docs.anthropic.com/claude/docs/system-prompts - System prompts best practices

### YAML & Validation
- https://pyyaml.org/wiki/PyYAMLDocumentation - YAML parsing in Python
- https://click.palletsprojects.com/ - CLI framework (ya usado en mastermind-cli)

### Benchmarks de Industria
- https://www.lennyrachitsky.com/p/how-should-startups-measure-success - Lenny's benchmarks
- https://www.growthhackers.com/articles/growth-hacking-sean-ellis - Sean Ellis PMF test

### Bias Research
- https://en.wikipedia.org/wiki/List_of_cognitive_biases - Bias reference
- https://www.goodjudgment.com/ - Superforecasting research

---

## Implementation Blueprint

### Pseudocode - Evaluator Skill Structure

```python
# Estructura de archivos a crear
skill_structure = {
    "skills/evaluator/": {
        "SKILL.md": "System prompt del evaluador",
        "protocol.md": "Protocolo de evaluación en 5 pasos",
        "bias-catalog.yaml": "10 sesgos con signals y questions",
        "benchmarks.yaml": "Métricas SaaS/Marketplace/Mobile",
        "evaluation-matrices/product-brief.yaml": "Matrix para outputs de Cerebro #1",
        "templates/evaluation-report.yaml": "Template de reporte",
        "templates/escalation-report.yaml": "Template para escalaciones",
    },
    "agents/brains/": {
        "growth-data.md": "System prompt del Cerebro #7"
    },
    "tools/mastermind-cli/mastermind_cli/commands/": {
        "brain.py": "Agregar comando compile-radar"
    }
}

# Comando compile-radar pseudocode
def compile_radar(brain_id="07"):
    """Genera FUENTE-709 y FUENTE-710 desde cerebros 1-6"""
    # 1. Buscar evaluation-criteria.md en cada cerebro 1-6
    evaluation_criteria = []
    for brain_id in ["01", "02", "03", "04", "05", "06"]:
        criteria_file = find_brain_file(brain_id, "evaluation-criteria.md")
        if criteria_file:
            evaluation_criteria.append(read(criteria_file))

    # 2. Compilar checklist consolidado
    fuente_709 = generate_consolidated_checklist(evaluation_criteria)
    write("07-growth-data-brain/sources/FUENTE-709-checklist-evaluacion.md", fuente_709)

    # 3. Buscar anti-patrones en cada cerebro 1-6
    anti_patterns = []
    for brain_id in ["01", "02", "03", "04", "05", "06"]:
        anti_pattern_file = find_brain_file(brain_id, "anti-patrones.md")
        if anti_pattern_file:
            anti_patterns.append(read(anti_pattern_file))

    # 4. Compilar anti-patrones consolidados
    fuente_710 = generate_consolidated_anti_patterns(anti_patterns)
    write("07-growth-data-brain/sources/FUENTE-710-antipatrones-consolidados.md", fuente_710)

    print("✓ FUENTE-709 y FUENTE-710 generadas")
```

### Pseudocode - Evaluation Flow

```python
# Flujo de evaluación (lógica del SKILL.md)
def evaluate_output(source_brain, output):
    """Evalúa un output usando la skill del evaluador"""

    # Paso 1: Intake
    output_type = identify_output_type(output)  # product-brief, ux-report, etc.
    matrix = load_evaluation_matrix(output_type)
    if not matrix:
        return ESCALATE("No existe matrix para este tipo de output")

    # Paso 2: Evaluación
    results = {
        "passed_checks": [],
        "failed_checks": [],
        "biases_detected": [],
        "benchmark_comparisons": []
    }

    for category in ["completeness", "quality", "intellectual_honesty", "commercial_viability"]:
        for check in matrix[category]:
            evidence = find_evidence(output, check)
            if not evidence:
                results["failed_checks"].append({
                    "id": check.id,
                    "check": check.description,
                    "fix_instruction": generate_fix_instruction(check)
                })
            else:
                results["passed_checks"].append({
                    "id": check.id,
                    "justification": evidence
                })

    # Detectar sesgos
    for bias in bias_catalog:
        signal = detect_bias_signal(output, bias)
        if signal:
            results["biases_detected"].append({
                "bias_id": bias.id,
                "name": bias.name,
                "evidence": signal
            })

    # Comparar métricas vs benchmarks
    for metric in extract_metrics(output):
        benchmark = get_benchmark(metric)
        if benchmark:
            results["benchmark_comparisons"].append({
                "metric": metric.name,
                "output_value": metric.value,
                "benchmark": benchmark,
                "status": compare(metric.value, benchmark)
            })

    # Paso 3: Scoring
    score = calculate_score(results, matrix)

    # Paso 4: Veredicto
    if score >= 80:
        verdict = "APPROVE"
    elif score >= 60:
        verdict = "CONDITIONAL"
    else:
        verdict = "REJECT"

    # Generar reporte
    report = generate_evaluation_report(
        evaluation_id=generate_id(),
        source_brain=source_brain,
        verdict=verdict,
        score=score,
        results=results
    )

    # Paso 5: Registro
    save_report("logs/evaluations/", report)

    return report
```

---

## Tasks (in Order)

### Task 0: Verificar Fuentes del Cerebro #7 (5 min)
- [ ] Verificar que las 10 fuentes existen en `docs/software-development/07-growth-data-brain/sources/`
- [ ] Validar YAML front matter de cada fuente
- [ ] **NOTA:** Las fuentes YA están creadas (FUENTE-701 a FUENTE-710)
- [ ] Fuentes externas (8): Munger, Kahneman, Tetlock, Hormozi, Ellis, Chen, Dobelli, Lenny
- [ ] Fuentes internas (2): FUENTE-709 (checklist), FUENTE-710 (anti-patrones)

**Fuentes existentes:**
```
FUENTE-701 - Poor Charlie's Almanack (Munger) ✅
FUENTE-702 - Thinking Fast and Slow (Kahneman) ✅
FUENTE-703 - Superforecasting (Tetlock) ✅
FUENTE-704 - $100M Offers (Hormozi) ✅
FUENTE-705 - Hacking Growth (Ellis) ✅
FUENTE-706 - Cold Start Problem (Chen) ✅
FUENTE-707 - Art of Thinking Clearly (Dobelli) ✅
FUENTE-708 - Lenny's Newsletter Benchmarks ✅
FUENTE-709 - Checklist Evaluación por Cerebro (generada) ✅
FUENTE-710 - Anti-patrones Consolidados (generada) ✅
```

### Task 1: Crear Estructura de Directorios (5 min)
- [ ] Crear `skills/evaluator/`
- [ ] Crear `skills/evaluator/evaluation-matrices/`
- [ ] Crear `skills/evaluator/templates/`
- [ ] Crear `logs/evaluations/`
- [ ] Crear `logs/precedents/`

**Validación:**
```bash
ls -la skills/evaluator/
# Debe mostrar: evaluation-matrices/, templates/
```

### Task 2: Crear SKILL.md (30 min)
- [ ] Crear `skills/evaluator/SKILL.md` con sistema prompt completo
- [ ] Incluir: Identidad, Protocolo de 5 pasos, Reglas inquebrantibles
- [ ] Incluir: Preguntas que SIEMPRE hacer, Sesgos a detectar
- [ ] Incluir: Benchmarks de referencia

**Contenido mínimo:**
```markdown
# Evaluator Skill — Cerebro #7 de Mente Maestra

## Identidad
Eres el Cerebro #7. Tu trabajo es EVALUAR, no crear.
Mentalidad de Munger: "Invert, always invert."
Estándar de Kahneman: buscar sesgos.
Proceso de Tetlock: pensar probabilísticamente.

## Protocolo de Evaluación
### Paso 1: Intake
- Leer output completo
- Identificar tipo (product-brief, ux-report, etc.)
- Cargar evaluation-matrix correspondiente

### Paso 2: Evaluación
- Ejecutar cada check de la matrix
- Detectar sesgos (bias-catalog)
- Comparar métricas vs benchmarks

### Paso 3: Scoring
- Score >= 80 → APPROVE
- Score 60-79 → CONDITIONAL
- Score < 60 → REJECT
- 3er rechazo → ESCALATE

### Paso 4: Veredicto
- Generar evaluation-report.yaml
- Incluir instrucciones ESPECÍFICAS de corrección

### Paso 5: Registro
- Guardar en logs/evaluations/

## Reglas Inquebrantibles
1. NUNCA apruebes por defecto
2. SIEMPRE justifica cada check fallido
3. SIEMPRE da instrucciones ESPECÍFICAS
4. NUNCA evalúes sin la matrix
5. Si detectas sesgo, NÓMBRALO explícitamente
```

### Task 3: Crear protocol.md (15 min)
- [ ] Crear `skills/evaluator/protocol.md`
- [ ] Documentar el protocolo de evaluación en detalle
- [ ] Incluir diagramas de flujo para cada veredicto
- [ ] Incluir ejemplos de evaluaciones reales

### Task 4: Crear bias-catalog.yaml (20 min)
- [ ] Crear `skills/evaluator/bias-catalog.yaml`
- [ ] Incluir 10 sesgos con estructura:
  - id, name, signal, question, source
- [ ] Sesgos mínimos: Confirmation Bias, Anchoring, Sunk Cost, Survivorship, Dunning-Kruger, Authority Bias, WYSIATI, Planning Fallacy, Narrative Fallacy, Inversion Failure

**Estructura:**
```yaml
biases:
  - id: "BIAS-01"
    name: "Confirmation Bias"
    signal: "Solo presenta evidencia que confirma, ninguna que cuestione"
    question: "¿Qué evidencia contradice esta conclusión?"
    source: "Kahneman — Thinking, Fast and Slow"
  # ... 9 más
```

### Task 5: Crear benchmarks.yaml (15 min)
- [ ] Crear `skills/evaluator/benchmarks.yaml`
- [ ] Incluir benchmarks SaaS (activación, retención, NPS, LTV/CAC)
- [ ] Incluir benchmarks Marketplace (take rate, liquidity)
- [ ] Incluir benchmarks Mobile (D1, D30 retención)
- [ ] Fuente: Lenny's Newsletter + Sean Ellis

**Validación:**
```bash
python3 -c "import yaml; yaml.safe_load(open('skills/evaluator/benchmarks.yaml'))"
# No debe dar error
```

### Task 6: Crear evaluation-matrices/product-brief.yaml (30 min)
- [ ] Crear `skills/evaluator/evaluation-matrices/product-brief.yaml`
- [ ] Incluir 4 categorías: completeness, quality, intellectual_honesty, commercial_viability
- [ ] Mínimo 15 checks con weights
- [ ] Cada check debe tener: id, description, weight, fail_action
- [ ] Alguns checks deben tener bias_check asociado

**Estructura:**
```yaml
matrix_id: "MATRIX-product-brief"
applies_to: "01-product-strategy"
output_type: "product-brief"

checks:
  completeness:
    - id: "C1"
      check: "¿Define claramente el problema?"
      weight: 10
      fail_action: "REJECT"
    # ... más checks

  quality:
    - id: "Q1"
      check: "¿El problema está validado con evidencia?"
      weight: 9
      fail_action: "REDIRECT"
      bias_check: "BIAS-01"
    # ... más checks

  # ... intellectual_honesty, commercial_viability

scoring:
  total_possible: 138
  approve_threshold: 80
  conditional_threshold: 60
```

### Task 7: Crear Templates (20 min)
- [ ] Crear `skills/evaluator/templates/evaluation-report.yaml`
- [ ] Crear `skills/evaluator/templates/escalation-report.yaml`
- [ ] Incluir todos los campos: evaluation_id, timestamp, verdict, scores, passed/failed checks, biases_detected, redirect_instructions

### Task 8: Crear System Prompt del Cerebro #7 (20 min)
- [ ] Crear `agents/brains/growth-data.md`
- [ ] Basarse en `agents/brains/product-strategy.md` como referencia
- [ ] Incluir: Identidad, Conocimiento (6 expertos), Frameworks, Proceso, Reglas
- [ ] Importante: El cerebro USA la skill, no la es

**Contenido clave:**
```markdown
# Role: Critical Evaluator / Growth & Data Brain

You are Brain #7 of the MasterMind Framework.

## Your Identity
You are a meta-cognitive evaluator with expertise in:
- Critical thinking (Munger, Kahneman, Tetlock)
- Growth frameworks (Ellis, Chen)
- Commercial viability (Hormozi)

## Your Purpose
You evaluate EVERY output from brains 1-6. You do NOT create - you EVALUATE.
Your mindset: "Invert, always invert" (Munger).
You find weaknesses. If you find none, you approve.

## Your Knowledge
You have access to:
- skills/evaluator/SKILL.md (your evaluation protocol)
- skills/evaluator/bias-catalog.yaml (10 cognitive biases)
- skills/evaluator/benchmarks.yaml (industry metrics)
- skills/evaluator/evaluation-matrices/* (evaluation criteria by output type)

## Your Process
1. Receive output from another brain
2. Identify output type
3. Load corresponding evaluation matrix
4. Execute evaluation (5-step protocol)
5. Generate verdict: APPROVE / CONDITIONAL / REJECT / ESCALATE
```

### Task 9: Implementar comando compile-radar en CLI (30 min)
- [ ] Editar `tools/mastermind-cli/mastermind_cli/commands/brain.py`
- [ ] Agregar comando `compile-radar` que:
  1. Lee evaluation-criteria.md de cerebros 1-6
  2. Compila en FUENTE-709-checklist-evaluacion.md
  3. Lee anti-patrones de cerebros 1-6
  4. Compila en FUENTE-710-antipatrones-consolidados.md
  5. Deposita en `07-growth-data-brain/sources/`

**Implementación:**
```python
@brain.command("compile-radar")
@click.argument("brain_id", default="07")
def brain_compile_radar(brain_id: str):
    """Compile evaluation criteria and anti-patterns from all brains."""
    if brain_id != "07":
        console.print("[yellow]compile-radar only applies to brain 07[/yellow]")
        return

    project_root = get_project_root()
    software_dev = project_root / "docs" / "software-development"
    output_dir = software_dev / "07-growth-data-brain" / "sources"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Compilar evaluation criteria
    console.print("[cyan]Compiling evaluation criteria...[/cyan]")
    criteria_sections = []

    for brain_num in range(1, 7):
        brain_id = f"0{brain_num}"
        brain_path = software_dev / f"{brain_id}-product-strategy-brain" if brain_num == 1 else software_dev / f"{brain_id}-*-brain"
        criteria_file = list(brain_path.glob("evaluation-criteria.md"))

        if criteria_file:
            content = criteria_file[0].read_text()
            criteria_sections.append(f"## From {brain_id}\n\n{content}\n")

    fuente_709 = "# FUENTE-709: Checklist de Evaluación por Cerebro\n\n"
    fuente_709 += "\n".join(criteria_sections)

    (output_dir / "FUENTE-709-checklist-evaluacion.md").write_text(fuente_709)
    console.print("[green]✓ FUENTE-709 created[/green]")

    # Compilar anti-patrones
    console.print("[cyan]Compiling anti-patterns...[/cyan]")
    anti_pattern_sections = []

    for brain_num in range(1, 7):
        brain_id = f"0{brain_num}"
        brain_path = software_dev / f"{brain_id}-product-strategy-brain" if brain_num == 1 else software_dev / f"{brain_id}-*-brain"
        anti_file = list(brain_path.glob("anti-patrones.md"))

        if anti_file:
            content = anti_file[0].read_text()
            anti_pattern_sections.append(f"## From {brain_id}\n\n{content}\n")

    fuente_710 = "# FUENTE-710: Anti-patrones Consolidados\n\n"
    fuente_710 += "\n".join(anti_pattern_sections)

    (output_dir / "FUENTE-710-antipatrones-consolidados.md").write_text(fuente_710)
    console.print("[green]✓ FUENTE-710 created[/green]")

    console.print(f"\n[green]✓ Radar compiled for brain {brain_id}[/green]")
```

### Task 10: Crear Test Brief Defectuoso (15 min)
- [ ] Crear `tests/fixtures/product-brief-defectuoso.md`
- [ ] Brief debe tener defectos intencionales:
  - Sin métricas de éxito
  - Confirmation bias evidente
  - Sin análisis de fallo
  - Métricas vanity en vez de accionables

### Task 11: Ejecutar Test de Verificación (15 min)
- [ ] Ejecutar evaluación del brief defectuoso
- [ ] Verificar que se genera evaluation-report.yaml
- [ ] Verificar que detecta los 3 defectos
- [ ] Verificar que veredicto es REJECT o CONDITIONAL
- [ ] Verificar que da instrucciones específicas de corrección

**Test manual:**
```bash
# Simular evaluación
python3 -c "
import yaml
from pathlib import Path

# Cargar brief defectuoso
brief = Path('tests/fixtures/product-brief-defectuoso.md').read_text()

# Simular evaluación (manual por ahora)
print('Evaluating brief...')
print('Expected: REJECT or CONDITIONAL')
print('Expected to detect: No metrics, confirmation bias, no failure analysis')
"
```

### Task 11A: NotebookLM Setup para Cerebro #7 (20 min - OPCIONAL)
- [ ] Crear notebook: `[CEREBRO] Growth & Data - Software Development`
- [ ] Usar MCP: `mcp__notebooklm-mcp__notebook_create` con título correcto
- [ ] Exportar fuentes sin YAML: usar `tools/export_sources_notebooklm.py` adaptado
- [ ] Cargar las 10 fuentes (FUENTE-701 a FUENTE-710)
- [ ] Ejecutar 3 consultas de prueba:
  1. "¿Qué es la inversión del problema según Munger?"
  2. "¿Cuáles son los 3 sesgos más comunes según Kahneman?"
  3. "¿Qué benchmarks considera Lenny para SaaS B2C?"
- [ ] Actualizar `docs/software-development/07-growth-data-brain/notebook-config.json`

**NOTA:** Esta tarea es OPCIONAL para la fase inicial. La skill del evaluador funciona sin NotebookLM. Se puede agregar en un PRP futuro.

### Task 12: Documentación y Git (10 min)
- [ ] Actualizar `agents/brains/growth-data.md` si es necesario
- [ ] Crear `docs/EVALUATOR-GUIDE.md` con guía de uso
- [ ] Git commit: `feat(evaluator): implement Cerebro #7 with evaluator skill`

---

## Validation Gates

```bash
# 1. Verificar estructura de archivos creada
ls -la skills/evaluator/
# Debe mostrar: SKILL.md, protocol.md, bias-catalog.yaml, benchmarks.yaml, evaluation-matrices/, templates/

# 2. Validar YAML syntax
python3 -c "import yaml; yaml.safe_load(open('skills/evaluator/bias-catalog.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('skills/evaluator/benchmarks.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('skills/evaluator/evaluation-matrices/product-brief.yaml'))"
# No debe dar error

# 3. Verificar system prompt creado
ls -la agents/brains/growth-data.md
# Debe existir

# 4. Verificar comando compile-radar
mastermind brain compile-radar --brain 07
# Debe crear FUENTE-709 y FUENTE-710

# 5. Verificar fuentes generadas
ls -la docs/software-development/07-growth-data-brain/sources/
# Debe mostrar FUENTE-709 y FUENTE-710

# 6. Ejecutar test (manual por ahora)
cat tests/fixtures/product-brief-defectuoso.md
# Verificar que tiene defectos intencionales

# 7. Verificar directorio de logs
ls -la logs/evaluations/
ls -la logs/precedents/
# Deben existir
```

---

## Definition of Done

- [ ] `skills/evaluator/SKILL.md` creado con protocolo de 5 pasos
- [ ] `skills/evaluator/protocol.md` documentado
- [ ] `skills/evaluator/bias-catalog.yaml` con 10 sesgos
- [ ] `skills/evaluator/benchmarks.yaml` con métricas SaaS/Marketplace/Mobile
- [ ] `skills/evaluator/evaluation-matrices/product-brief.yaml` con 15+ checks
- [ ] `skills/evaluator/templates/evaluation-report.yaml` creado
- [ ] `skills/evaluator/templates/escalation-report.yaml` creado
- [ ] `agents/brains/growth-data.md` (system prompt Cerebro #7) creado
- [ ] Comando `mastermind brain compile-radar --brain 07` implementado
- [ ] Test brief defectuoso creado y evaluación verificada
- [ ] Git commit con cambios
- [ ] `docs/EVALUATOR-GUIDE.md` creado (opcional pero recomendado)

---

## Error Handling Strategy

| Error | Acción |
|-------|--------|
| YAML syntax error en bias-catalog/benchmarks | Validar con python3 antes de continuar |
| evaluation-criteria.md no encontrado en cerebro | Warning, continuar con los que sí existen |
| Matrix no existe para output type | ESCALATE pidiendo que se cree |
| Test brief no genera evaluation report | Verificar que SKILL.md está cargado correctamente |

---

## Gotchas & Notes

1. **Cerebro #7 vs Evaluator Skill:** El cerebro USA la skill, no la es. La skill es la herramienta, el cerebro es el operador.
2. **FUENTE-709 y FUENTE-710:** Se regeneran cada vez que se ejecuta `compile-radar`. No son estáticas.
3. **NotebookLM para Cerebro #7:** Opcional para fase inicial. La skill funciona sin él. Se puede agregar en PRP futuro.
4. **Evaluation Matrices:** Solo creamos product-brief.yaml ahora. Las demás (ux-report, ui-design, etc.) se crean cuando se implementen esos cerebros.
5. **Bias Detection:** La clave está en NOMBRAAR el sesgo explícitamente (BIAS-01, BIAS-02, etc.) para que el cerebro evaluado aprenda.
6. **Benchmarks:** Los números son referenciales para SaaS B2C. Ajustar según contexto específico del proyecto.

---

## Files Created

| Archivo | Propósito |
|---------|-----------|
| `skills/evaluator/SKILL.md` | System prompt completo del evaluador |
| `skills/evaluator/protocol.md` | Protocolo de evaluación documentado |
| `skills/evaluator/bias-catalog.yaml` | 10 sesgos catalogados |
| `skills/evaluator/benchmarks.yaml` | Benchmarks de industria |
| `skills/evaluator/evaluation-matrices/product-brief.yaml` | Matrix para evaluar outputs de Cerebro #1 |
| `skills/evaluator/templates/evaluation-report.yaml` | Template de reporte de evaluación |
| `skills/evaluator/templates/escalation-report.yaml` | Template para escalaciones al humano |
| `agents/brains/growth-data.md` | System prompt del Cerebro #7 |
| `tests/fixtures/product-brief-defectuoso.md` | Test con defectos intencionales |
| `docs/EVALUATOR-GUIDE.md` | Guía de uso (opcional) |

---

## Next Steps

After this PRP:
- **PRP-006:** Implementar Orquestador que coordine Cerebro #1 + Cerebro #7
- **Testing con briefs reales:** Probar el flujo completo
- **Cerebro #2:** UX Research (cuando se necesite)

---

## Confidence Score

**8.5/10** - Alta confianza de éxito.

**Rationale:**
- docs/design/11 es extremadamente detallado
- Patrones claros en PRPs existentes
- Riesgo principal: longitud puede hacer que se pierdan detalles
- Mitigación: estructura clara de tasks en orden

**Riesgos identificados:**
- Si evaluation-criteria.md no existe en otros cerebros, compile-radar no funcionará → crear archivos vacíos o stubs
- YAML syntax errors pueden bloquear progreso → validar cada archivo
- Test manual puede no ser suficiente → considerar automatizar en PRP futuro

---

## Context for AI Agent

**Archivos clave para leer ANTES de implementar:**

1. **Especificación completa:**
   - `docs/design/11-Cerebro-07-Evaluador-Critico.md` - LEER ESTE PRIMERO

2. **Referencias de patrones:**
   - `agents/brains/product-strategy.md` - Patrón de system prompt
   - `PRPs/PRP-003-system-prompts.md` - Patrón de creación de system prompts
   - `tools/mastermind-cli/mastermind_cli/commands/brain.py` - Estructura del CLI

3. **Contexto del proyecto:**
   - `docs/design/10-Plan-Implementacion-Claude-Code.md` - FASE 4B
   - `docs/design/07-Orquestador-y-Evaluador.md` - Contexto del evaluador

**Comando para iniciar:**
```bash
cd /home/rpadron/proy/mastermind
# Verificar que estás en master branch
git branch
# Crear estructura de directorios
mkdir -p skills/evaluator/{evaluation-matrices,templates}
mkdir -p logs/{evaluations,precedents}
```

**Resultado esperado:**
Cerebro #7 completamente implementado con skill de evaluación funcional, comando compile-radar operativo, test de verificación pasando.
