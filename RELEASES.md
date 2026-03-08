# Release Notes - MasterMind Framework

## v1.1.0 (2026-03-07)

### Nuevas Funcionalidades

#### Brain #8: Master Interviewer / Discovery

Octavo cerebro especializado del framework, orientado a la clarificación de briefs ambiguos y la conducción de entrevistas de descubrimiento con usuarios.

**Funcionalidades principales:**

- **Detección de ambigüedad (3 niveles):** Evalúa automáticamente si un brief es demasiado vago (word count < 15, marcadores de ambigüedad, ausencia de problema concreto)
- **Discovery Flow interactivo:** Entrevista iterativa Q→A→Domain Brain→Follow-up para clarificar requerimientos
- **Interview Planning via NotebookLM:** Genera planes de entrevista usando el conocimiento destilado de Fitzpatrick, Voss, Stanier y Torres
- **Domain Brain Routing:** Dirige outputs a los cerebros #1-7 según el dominio detectado
- **Slash Command `/mm:discovery`:** Interfaz de línea de comandos para iniciar entrevistas interactivas desde Claude Code

**Sistema de Aprendizaje (Learning System):**

- `find_similar_interviews()` — Búsqueda de entrevistas previas por similitud Jaccard
- `get_learning_stats()` — Estadísticas de entrevistas de los últimos 30 días
- Retention policy automática: almacenamiento hot/warm/cold según antigüedad
- `_conduct_interview()` usa historial de entrevistas similares para mejorar preguntas
- Script `scripts/cleanup_interviews.py` para mantenimiento periódico

**NotebookLM:**

- Notebook ID: `5330e845-29dc-4219-9d7e-c1ccb4851bb3`
- Fuentes cargadas: Fitzpatrick (Mom Test), Voss (Never Split the Difference), Stanier (The Coaching Habit), Torres (Continuous Discovery Habits)

#### Testing & Polish (PRP-016)

- 31/31 tests passing (9 discovery + 10 learning + 12 core)
- Cobertura con pytest-cov integrado
- `docs/testing/E2E-TEST-MANUAL.md` con 4 casos de prueba validados
- Fix en `test_brain_registry` para reconocer Brain #8 como activo

### Mejoras

- `mastermind_cli/orchestrator/coordinator.py` — +456 líneas: Discovery flow + Learning integration
- `mastermind_cli/orchestrator/output_formatter.py` — +150 líneas: Formateo de outputs de discovery
- `mastermind_cli/memory/interview_logger.py` — +455 líneas: Learning system completo
- `mastermind_cli/memory/models.py` — Modelos Pydantic actualizados
- `agents/brains/master-interviewer.md` — System prompt Brain #8

### Expertos Incorporados (Brain #8)

| Experto | Libro | Habilidades |
|---------|-------|-------------|
| Rob Fitzpatrick | The Mom Test | Entrevistas sin sesgo, validación de hipótesis |
| Chris Voss | Never Split the Difference | Negociación, escucha activa, preguntas calibradas |
| Michael Bungay Stanier | The Coaching Habit | Preguntas de coaching, facilitar claridad |
| Teresa Torres | Continuous Discovery Habits | Discovery continuo, árbol de oportunidades |

### Casos de Uso Validados (E2E)

| TC | Brief | Resultado |
|----|-------|-----------|
| TC-1 | "quiero una app moderna" | CRM clarificado con métricas de conversión |
| TC-2 | "agencia necesita app de campañas" | client_onboarding, Brain #5, integraciones detectadas |
| TC-3 | "SEO y content marketing" | Gap detectado, Brain #9 recomendado |
| TC-4 | "e-commerce B2B complejo" | 5 dominios cubiertos, riesgos detectados |

---

## v1.0.0 (2026-03-06)

### Estado General

Framework base con 7 cerebros especializados + Orquestador + Evaluador. Production ready para el nicho de Software Development.

### Cerebros Activos (v1.0.0)

| # | Cerebro | Fuentes |
|---|---------|---------|
| 1 | Product Strategy | Cagan, Torres, Perri, Ries, Doerr |
| 2 | UX Research | Norman, Nielsen, Krug, Young, Hall |
| 3 | UI Design | Frost, Wathan, Wroblewski, Lupton |
| 4 | Frontend | Simpson, Comeau, Osmani, Dodds |
| 5 | Backend | Jin, Martin, Kleppmann, Xu, Fowler |
| 6 | QA/DevOps | Kim, Forsgren, Humble, Majors, Crispin |
| 7 | Growth/Data | Munger, Kahneman, Tetlock, Hormozi |

### Funcionalidades (v1.0.0)

- mastermind-cli con comandos `mm source`, `mm brain`, `mm orchestrate`, `mm eval`
- Orquestador central con routing a cerebros especializados
- Cerebro #7 como evaluador crítico (meta-cerebro)
- Sistema de memoria: Evaluation Logger (hot storage)
- Instaladores universales: `install.sh` (Linux/macOS) y `install.ps1` (Windows)
- Namespace `mm:` para slash commands en Claude Code
- 122 fuentes destiladas cargadas en NotebookLM
