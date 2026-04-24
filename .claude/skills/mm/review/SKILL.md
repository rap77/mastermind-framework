---
name: mm-review
description: >
  Code review skill for MasterMind: executes 5-axis review (correctness, readability,
  architecture, security, performance) consulting Brain #6 (QA) and Brain #7 (Growth).
  Generates report with CRITICAL/WARNING/SUGGESTION severity levels.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0.0"
---

# mm-review — Code Review Skill

**Misión:** Ejecutar code review completo en 5 ejes consultando los cerebros especializados de MasterMind para generar reportes accionables con severidad clara.

## ¿Cuándo Usar?

Esta skill es **PROACTIVA** — se activa cuando:

**Antes de Commit:**
- El usuario indica que terminó una feature ("terminé", "listo", "ya está")
- Se detectan cambios en git (`git status` muestra archivos modificados)
- El usuario pregunta "¿qué te parece?", "¿está bien?", "¿revisás?"
- Antes de ejecutar `/mm:safe-commit`

**Post-Implementation:**
- Después de `/mm:complete-task` completa una tarea
- Después de implementar una feature compleja
- El usuario solicita revisión explícita ("review", "revisame esto")
- Se detectan patrones sospechosos en el código (hardcoded values, missing error handling)

**No esperés a que el usuario lo pida explícitamente.** Si detectás alguno de estos indicios, activá la skill.

---

## Protocolo de Review (5 Ejes)

### Eje 1: Correctness
**Pregunta clave:** ¿El código hace lo que debe hacer?

**Criterios:**
- Lógica correcta sin bugs obvios
- Manejo de edge cases (null, undefined, empty arrays)
- Validación de inputs
- Error handling completo
- Tests cubren casos críticos

**Brain #6 (QA):**
```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="BRAIN_06_QA_DEVOPS",
    query=f"""
Code Context:
{diff}

Files Changed:
{files_list}

QA Questions:
1. What edge cases are NOT covered?
2. What's missing in error handling?
3. What test scenarios should be added?
4. Are there race conditions or concurrency issues?
5. What's the risk level of potential bugs?

Answer with:
- Missing edge cases (priority: HIGH/MEDIUM/LOW)
- Test coverage gaps
- Error handling anti-patterns
"""
)
```

### Eje 2: Readability
**Pregunta clave:** ¿El código es fácil de entender?

**Criterios:**
- Nombres descriptivos (variables, funciones, clases)
- Comentarios en lo NO obvio
- Funciones pequeñas (< 50 líneas)
- Complejidad ciclomática < 10
- Sin "magia" (números hardcoded, strings sin explicación)

**Brain #7 (Growth):**
```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="BRAIN_07_GROWTH",
    query=f"""
Code Context:
{diff}

Readability Questions:
1. What's confusing or hard to understand?
2. What variable/function names are misleading?
3. What needs comments (that isn't obvious)?
4. Where's the complexity too high?
5. What patterns reduce long-term maintainability?

Answer with:
- Confusing sections (line numbers)
- Naming suggestions
- Complexity hotspots
"""
)
```

### Eje 3: Architecture
**Pregunta clave:** ¿El código sigue buenas prácticas de arquitectura?

**Criterios:**
- Separación de responsabilidades (SRP)
- DRY (Don't Repeat Yourself)
- Inversión de dependencias
- Patrones apropiados (Factory, Strategy, etc.)
- Modularidad y bajo acoplamiento

**Brain #7 (Growth):**
```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="BRAIN_07_GROWTH",
    query=f"""
Code Context:
{diff}

Architecture Questions:
1. Does this follow SOLID principles?
2. What patterns should be applied?
3. What's coupled too tightly?
4. Where's the abstraction wrong?
5. What's the long-term impact on codebase?

Answer with:
- Architecture violations (specific principle)
- Pattern suggestions
- Refactoring opportunities (high impact)
"""
)
```

### Eje 4: Security
**Pregunta clave:** ¿El código tiene vulnerabilidades?

**Criterios:**
- Sin inyección SQL/Command
- Validación de entrada sanitizada
- Auth/authorization correctos
- Sin data sensible en logs
- Headers de seguridad (CORS, CSP)

**Brain #6 (QA):**
```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="BRAIN_06_QA_DEVOPS",
    query=f"""
Code Context:
{diff}

Security Questions:
1. What OWASP Top 10 vulnerabilities exist?
2. Is user input properly sanitized?
3. Are auth checks missing or bypassable?
4. What's exposed that shouldn't be?
5. What's the attack surface?

Answer with:
- Security issues (severity: CRITICAL/HIGH/MEDIUM/LOW)
- OWASP category
- Exploit scenario
- Fix recommendation
"""
)
```

### Eje 5: Performance
**Pregunta clave:** ¿El código es eficiente?

**Criterios:**
- Sin queries N+1
- Uso apropiado de índices
- Sin memory leaks
- Complejidad algorítmica adecuada
- Caching cuando aplica

**Brain #7 (Growth):**
```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="BRAIN_07_GROWTH",
    query=f"""
Code Context:
{diff}

Performance Questions:
1. What's the algorithmic complexity (Big O)?
2. Where's the potential for optimization?
3. Are there obvious performance anti-patterns?
4. What's the impact at scale?
5. What should be cached?

Answer with:
- Performance bottlenecks
- Optimization opportunities (impact: HIGH/MEDIUM/LOW)
- Caching recommendations
"""
)
```

---

## Formato de Reporte

Generar reporte en `.planning/REVIEWS/<timestamp>-review.md`:

```markdown
# Code Review — {timestamp}

**Scope:** {mode} ({branch|files|commit})
**Files Changed:** {count}
**Lines Changed:** {additions}+, {deletions}-

**Reviewer:** Brain #6 (QA) + Brain #7 (Growth)

---

## Summary

{one-paragraph overview}

**Overall Assessment:** {PASS/NEEDS_WORK/FAIL}

---

## 1. Correctness

### CRITICAL
- [ ] {issue} — Line {n}

### WARNING
- [ ] {issue} — Line {n}

### SUGGESTION
- [ ] {improvement} — Line {n}

---

## 2. Readability

### CRITICAL
- [ ] {confusing code} — Line {n}

### WARNING
- [ ] {unclear name} — Line {n}

### SUGGESTION
- [ ] {naming suggestion} — Line {n}

---

## 3. Architecture

### CRITICAL
- [ ] {violation} — Line {n}

### WARNING
- [ ] {pattern suggestion} — Line {n}

### SUGGESTION
- [ ] {refactoring opportunity} — Line {n}

---

## 4. Security

### CRITICAL
- [ ] {vulnerability} — Line {n}

### WARNING
- [ ] {risk} — Line {n}

### SUGGESTION
- [ ] {hardening} — Line {n}

---

## 5. Performance

### CRITICAL
- [ ] {bottleneck} — Line {n}

### WARNING
- [ ] {inefficiency} — Line {n}

### SUGGESTION
- [ ] {optimization} — Line {n}

---

## Brain Consultations

### Brain #6 (QA) — {timestamp}
**Input:** {query_summary}
**Output:** {key_findings}
**Confidence:** {HIGH/MEDIUM/LOW}

### Brain #7 (Growth) — {timestamp}
**Input:** {query_summary}
**Output:** {key_findings}
**Confidence:** {HIGH/MEDIUM/LOW}

---

## Action Items

1. [ ] {CRITICAL item} — MUST fix before commit
2. [ ] {WARNING item} — SHOULD fix
3. [ ] {SUGGESTION item} — NICE to have

---

**Reviewed by:** MasterMind Code Review (Brain #6 + #7)
**Generated:** {timestamp}
**Report:** `.planning/REVIEWS/{this_file}`
```

---

## Criterios de Severidad

### CRITICAL 🔴
**Must fix BEFORE commit**
- Bugs que rompen la funcionalidad
- Vulnerabilidades de seguridad (OWASP Top 10)
- Performance issues críticos (N+1 queries sin paginación)
- Violaciones de arquitectura que causan technical debt severo

**Action:** Bloquear commit hasta corregir

### WARNING 🟡
**Should fix SOON**
- Edge cases no manejados
- Error handling incompleto
- Código confuso o difícil de mantener
- Patrones arquitecturales incorrectos
- Riesgos de seguridad moderados

**Action:** Permitir commit con TODO comment, revisar en próxima iteración

### SUGGESTION 🟢
**Nice to have**
- Mejoras de naming
- Refactoring opportunities
- Optimizaciones no críticas
- Mejoras de readability
- Best practices

**Action:** Documentar en backlog, priorizar según impacto

---

## Integración con `/mm:review`

Esta skill se activa automáticamente cuando el comando `/mm:review` se ejecuta:

```bash
# El comando ejecuta:
/mm:review              # Review uncommitted changes
/mm:review --staged     # Review staged changes
/mm: review --branch X  # Review diff vs branch
/mm:review --files a.ts b.ts  # Review specific files
/mm:review --last-commit  # Review last commit

# El comando:
1. Ejecuta review-handler.py (genera payload)
2. Lanza code-reviewer agent (esta skill)
3. Agent consulta Brain #6 y #7
4. Genera reporte en .planning/REVIEWS/
5. Muestra resumen al usuario
```

---

## Brain Protocol

**Brain #6 (QA/DevOps):**
- QA standards
- Testing strategy
- Edge cases identification
- Security vulnerabilities (OWASP)
- Error handling patterns

**Brain #7 (Growth/Data):**
- Systems thinking
- Architecture evaluation
- Impact analysis
- Risk assessment
- Performance optimization
- Long-term maintainability

---

## Memoria Protocol

Después del review, guardar aprendizajes en memoria:

```python
mcp__plugin_engram_engram__mem_save(
    title=f"Review patterns: {context}",
    type="pattern",
    content=f"""
**What**: Common issues found in review

**Why**: Patterns detected across {count} reviews

**Where**: {files_reviewed}

**Learned**:
- Common mistakes: {patterns}
- Missing test coverage: {gaps}
- Architecture violations: {violations}
- Security risks: {risks}
""",
    project="mastermind",
    topic_key="review-patterns"
)
```

---

## Ejemplos de Uso

### Review Antes de Commit

```bash
# Usuario terminó feature
> "Listo, ya está"

# Activar skill proactivamente
> "Voy a hacer un review antes de que commitees"

# Ejecutar:
/mm:review

# Output:
INFO: Reviewing 3 files (additions: 127, deletions: 45)
INFO: Consulting Brain #6 (QA)...
INFO: Consulting Brain #7 (Growth)...
INFO: Report: .planning/REVIEWS/2026-04-23-143052-review.md

✅ Overall Assessment: NEEDS_WORK

🔴 CRITICAL: 2 items
  - SQL injection vulnerability in login.ts:45
  - Missing null check in UserService.create()

🟡 WARNING: 3 items
  - Function too complex (cyclomatic: 15) in OrderProcessor.ts:120
  - No tests for edge case: empty array in filter()
  - Hardcoded API key (should be env var)

🟢 SUGGESTION: 1 item
  - Extract magic number "30000" to constant TIMEOUT_MS

⚠️  BLOCK: Fix CRITICAL items before committing
```

### Review Post-Complete-Task

```bash
# Después de /mm:complete-task C1
/mm:review --last-commit

# Output:
INFO: Reviewing commit abc1234 (C1: Crear review-handler.py)
INFO: Consulting Brain #6 (QA)...
INFO: Consulting Brain #7 (Growth)...
INFO: Report: .planning/REVIEWS/2026-04-23-150123-review.md

✅ Overall Assessment: PASS

🔴 CRITICAL: 0 items
🟡 WARNING: 1 item
  - Add docstring to verify_criterion_automatically() (line 165)

🟢 SUGGESTION: 2 items
  - Consider extracting verification logic to separate module
  - Add type hints for all functions (python 3.14)

✅ Safe to commit
```

---

## Referencias del Proyecto

- **Brain #6:** `.claude/agents/mm/brain-06-qa/`
- **Brain #7:** `.claude/agents/mm/brain-07-growth/`
- **Command:** `.claude/commands/mm/review.md`
- **Handler:** `.claude/commands/mm/review-handler.py`
- **Agent:** `.claude/agents/mm/code-reviewer/code-reviewer.md`

---

**Remember:** This skill executes comprehensive 5-axis code review using expert knowledge from Brain #6 (QA) and Brain #7 (Growth). It generates actionable reports with clear severity levels to guide developers toward better, more secure, and maintainable code.
