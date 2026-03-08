# PRP-016: Brain #8 Testing & Polish

**Status:** Ready to Implement (after PRP-013, PRP-014, PRP-015)
**Priority:** High (ensures quality)
**Estimated Time:** 5 hours
**Dependencies:** PRP-011, PRP-012, PRP-013, PRP-014, PRP-015
**Branch:** `feature/prp-016-brain-08-testing-polish`

---

## Executive Summary

Realizar testing end-to-end completo del Cerebro #8, incluyendo tests manuales de los flujos principales, pruebas de performance, revisión de documentación y bug fixes. Esta fase es el "gate de calidad" antes del release.

**Activities:**
1. E2E tests manuales (3 casos principales)
2. Performance testing (entrevistas con 10+ preguntas)
3. Revisión de documentación
4. Bug fixes y polish

---

## Context from Brain #8 Spec

**Referencia:** `docs/software-development/08-master-interviewer-brain/spec-brain-08-master-interviewer.md` → Sección "Testing Strategy"

### Testing Strategy del Spec

**Unit Tests** (Ya implementados en PRPs anteriores):
- `test_brain_registry.py` — Test YAML registry
- `test_interview_logger.py` — Test logging system
- `test_interview_learning.py` — Test learning features

**Integration Tests** (Ya implementados en PRP-013):
- `test_discovery_flow.py` — Test flujo completo

**E2E Tests** (Esta PRP):
- Tests manuales con usuarios reales
- Verificación de output formats
- Validación de user experience

### Performance Targets del Spec

| Metric | Target |
|--------|--------|
| Single interview (10 Qs) | < 5 minutes |
| Interview plan generation | < 30 seconds |
| Similar interview retrieval | < 5 seconds |
| JSON serialization | < 1 second |

---

## Test Cases

### Test Case 1: Vague Brief → Clarified Requirements

**Input:**
```bash
/mm:discovery "quiero una app moderna"
```

**Expected Flow:**
1. Detecta ambigüedad ("moderna" es vago)
2. Brain #8 genera plan con 4-5 categorías
3. Entrevista pregunta sobre:
   - ¿Qué tipo de app? (delivery, retail, social...)
   - ¿Quiénes son los usuarios?
   - ¿Qué plataformas? (web, mobile...)
   - ¿Qué significa "moderna" para vos?
4. Después de 10-15 preguntas, genera brief clarificado

**Expected Output:**
```markdown
# Clarified Requirements

**Original:** "quiero una app moderna"

**Clarified:**
- **Industry:** [Specific industry detected]
- **Users:** [Specific user personas]
- **Platform:** [Specific platform(s)]
- **"Modern" means:** [Specific design/tech/features]

**Recommendations:**
- Brain #X suggests [Specific actionable recommendations]
```

**Validation:**
- [ ] Brief está significativamente más claro que el input
- [ ] Todas las categorías tienen al menos 1 Q&A
- [ ] Output incluye JSON + YAML + Markdown
- [ ] Duración < 5 minutos

---

### Test Case 2: Client Onboarding → Technical Spec

**Input:**
```bash
/mm:discovery "Cliente de agencia de marketing necesita app para gestionar campañas publicitarias"
```

**Expected Flow:**
1. Contexto detectado: "client_onboarding"
2. Brain #8 genera plan enfocado en business requirements
3. Entrevista cubre:
   - Users (marketing managers, clients)
   - Features (campaign creation, analytics, approvals)
   - Platforms (web dashboard + mobile)
   - Integrations (Facebook Ads, Google Ads)
   - Budget (client pricing model)
4. Recommendations de brains #1, #4, #5

**Expected Output:**
```markdown
# Discovery Interview Summary

**Session ID:** [UUID]
**Context:** client_onboarding

**Key Findings:**
- B2B SaaS for marketing agencies
- Web dashboard for managers + Mobile for field staff
- Must integrate with major ad platforms
- Real-time collaboration critical

**Technical Recommendations** (from Brain #5):
- OAuth for ad platform authentication
- WebSocket for real-time updates
- Background jobs for campaign processing
```

**Validation:**
- [ ] Output es lo suficientemente específico para iniciar desarrollo
- [ ] Brain #5 recommendations son técnicas y accionables
- [ ] Integrations mencionadas (Facebook Ads, etc.)
- [ ] Duración < 5 minutos

---

### Test Case 3: Gap Detection → Brain Recommendation

**Input:**
```bash
/mm:discovery "Necesito implementar SEO técnico y content marketing en mi sitio web"
```

**Expected Flow:**
1. Interview procede normalmente
2. Brain #8 detecta que expertise SEO no está en cerebros #1-7
3. Al final, genera recomendación de nuevo cerebro

**Expected Output:**
```markdown
# Discovery Results

**Requirements:**
- On-page SEO optimization
- Content management system
- Blog functionality

**⚠️ Knowledge Gap Detected:**

Current brains (#1-7) focus on software development.
SEO and Content Marketing require expertise not available.

**Recommendation:**

Consider creating **Brain #9: Growth Marketing** with experts:
- Rand Fishkin (SEOmoz)
- Brian Dean (Backlinko)
- Ann Handley (Content Marketing Institute)

**Available Alternatives:**
- Brain #7 (Growth/Data) can help with analytics
- Brain #1 (Product Strategy) can help prioritize SEO features
```

**Validation:**
- [ ] Gap es detectado correctamente
- [ ] Expertos sugeridos son relevantes
- [ ] Alternativas (brains #1, #7) son mencionadas
- [ ] Output es accionable (puede crear PRP para nuevo brain)

---

## Performance Testing

### Test 4: Large Interview (10+ Questions)

**Input:**
```bash
/mm:discovery "Necesito construir un sistema completo de e-commerce B2B con inventario, payments, shipping, y analytics"
```

**Expected:**
- Generar 15-20 preguntas
- Duración total < 5 minutos
- Sin timeouts o crashes

**Validation:**
- [ ] Todas las categorías completadas
- [ ] No hay pérdidas de estado entre preguntas
- [ ] Output completo se genera

**Performance Metrics:**
| Step | Target | Actual |
|------|--------|--------|
| Interview plan generation | < 30s | ___ |
| Per question (avg) | < 15s | ___ |
| Total interview time | < 5min | ___ |
| Document generation | < 10s | ___ |

---

## Documentation Review

### Check 1: README.md

**Verify:**
- [ ] Brain #8 mencionado en lista de cerebros
- [ ] Ejemplo de uso incluido
- [ ] Link a documentación del comando

### Check 2: CLI-REFERENCE.md

**Verify:**
- [ ] Sección `/mm:discovery` completa
- [ ] Ejemplos actualizados
- [ ] Output formats documentados

### Check 3: Spec Document

**Verify:**
- [ ] `spec-brain-08-master-interviewer.md` está completo
- [ ] Todas las fases marcadas como completadas
- [ ] Timeline actualizado

### Check 4: Memory.md

**Verify:**
- [ ] Brain #8 agregado a tabla de cerebros
- [ ] Status marcado como "Active"
- [ ] Notebook ID incluido

---

## Bug Fixes & Polish

### Common Issues to Watch For

1. **Typos en output** — Revisar todos los formatters
2. **Format inconsistencies** — Verificar JSON/YAML/Markdown formatting
3. **Missing error messages** — Asegurar que todos los errores tengan mensajes claros
4. **Broken links** — Verificar links en documentación
5. **Outdated comments** — Revisar comentarios en código

### Polish Checklist

- [ ] Todos los outputs de formatters tienen emojis consistentes
- [ ] Mensajes de error son útiles y accionables
- [ ] Logs tienen timestamp y session_id
- [ ] Output files se crean en directorios correctos
- [ ] Tests tienen coverage > 80%

---

## Validation Gates

```bash
# ========== Test Case 1: Vague Brief ==========
echo "⚠️  MANUAL TEST: Run /mm:discovery 'quiero una app moderna'"
echo "   Expected: Clarified requirements output"
echo "   Validate: Output is clearer than input"

# ========== Test Case 2: Client Onboarding ==========
echo "⚠️  MANUAL TEST: Run /mm:discovery 'cliente de agencia necesita app'"
echo "   Expected: Technical spec with integrations"
echo "   Validate: Brain #5 recommendations are technical"

# ========== Test Case 3: Gap Detection ==========
echo "⚠️  MANUAL TEST: Run /mm:discovery 'necesito SEO y content marketing'"
echo "   Expected: Gap detected + brain recommendation"
echo "   Validate: Suggested experts are relevant"

# ========== Test Case 4: Performance ==========
echo "⚠️  MANUAL TEST: Run /mm:discovery with complex brief"
echo "   Expected: < 5 minutes total duration"
echo "   Validate: Time each step"

# ========== Documentation Checks ==========
# README.md
grep -q "Brain #8" README.md
echo "✅ README.md mentions Brain #8"

# CLI-REFERENCE.md
grep -q "/mm:discovery" docs/CLI-REFERENCE.md
echo "✅ CLI-REFERENCE.md documents discovery command"

# Spec
grep -q "Master Interviewer" docs/software-development/08-master-interviewer-brain/spec-brain-08-master-interviewer.md
echo "✅ Spec document exists"

# ========== All Tests ==========
uv run pytest tests/ -v --cov=mastermind_cli

# Coverage check
coverage report | grep "TOTAL"
# Expected: > 80%

echo "========== ALL VALIDATIONS PASSED (except manual tests) =========="
```

---

## Bug Tracking

Template para documentar bugs encontrados:

```markdown
### Bug #XXX: [Title]

**Description:**
[Brief description]

**Steps to Reproduce:**
1.
2.
3.

**Expected:** [What should happen]
**Actual:** [What actually happened]

**Severity:** [Critical/High/Medium/Low]

**Fix:**
[Code or description of fix]
```

---

## Quality Checklist

- [x] All necessary context included (spec, test cases)
- [x] Validation gates ejecutables (excepto tests manuales)
- [x] Test cases específicados con expected outputs
- [x] Performance targets definidos
- [x] Documentation review checklist incluido
- [x] Bug tracking template provisto
- [x] Polish considerations listadas

---

## Branch Strategy

**Create branch:** `feature/prp-016-brain-08-testing-polish`

```bash
git checkout -b feature/prp-016-brain-08-testing-polish

# Work through testing
# ... manual tests ...
# ... performance tests ...
# ... documentation review ...
# ... bug fixes ...

# Commit when done
git add README.md
git add docs/CLI-REFERENCE.md
git add .claude/projects/*/MEMORY.md
git add mastermind_cli/  # bug fixes
git commit -m "test(prp-016): e2e testing and polish for brain #8

- Manual E2E tests (3 test cases passing)
- Performance testing (interviews < 5 min)
- Documentation review and updates
- Bug fixes and polish

Test Results:
✅ Test Case 1: Vague brief → Clarified requirements
✅ Test Case 2: Client onboarding → Technical spec
✅ Test Case 3: Gap detection → Brain recommendation
✅ Test Case 4: Performance (10+ Qs < 5 min)

Documentation:
✅ README.md updated
✅ CLI-REFERENCE.md updated
✅ Spec document marked complete
✅ MEMORY.md updated

Coverage: > 80%

Refs: PRP-016, spec-brain-08"
```

---

## Success Criteria

- [ ] Los 3 test cases E2E pasan manualmente
- [ ] Performance test cumple targets (< 5 min)
- [ ] Coverage > 80%
- [ ] Todos los documentos actualizados
- [ ] Críticos bugs fijados
- [ ] No regressions en tests existentes

---

## PRP Confidence Score

**Score: 9/10**

**Justification:**
- ✅ **Well-defined test cases** — 3 escenarios principales especificados
- ✅ **Clear validation** — Expected outputs para cada test
- ✅ **Performance targets** — Métricas específicas
- ✅ **Isolated** — Testing no afecta código (solo encuentra bugs)
- ⚠️ **-1 punto** — Tests son manuales (no automatizados)

**Riesgo bajo:** Esta PRP es testing y polish. No introduce código nuevo significativo.

---

## Next Steps After Completion

Once PRP-016 is complete:

1. **Documentar bugs** encontrados y fixes aplicados
2. **Start PRP-017:** Release (git tag, release notes)
3. **Planear mejoras futuras** basadas en testing findings

---

**END OF PRP-016**
