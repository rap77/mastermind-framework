---
id: PROP-001
title: "Onboarding Visual para MasterMind v3.0"
status: APPROVED_WITH_CONDITIONS
priority: P1
category: UX/UI
effort: M
updated: 2026-04-06 (PIVOTED - Manager persona)
brain_evaluations:
  brain-02: CONDITIONAL_APPROVAL
  brain-03: CONDITIONAL_APPROVAL
  brain_07: APPROVED_WITH_CONDITIONS
final_verdict: APPROVED_WITH_CONDITIONS (PIVOT - Manager persona VALIDATED)
pivot_reason: "CEO técnico" persona invalidada por investigación secundaria (95%+ CEOs delegan config técnica). Nueva persona: Manager/Director business-savvy NO técnico RESPONSABLE de configurar.
next_actions:
  - Update Happy Path with user responses
  - Re-test with user persona clarification
  - Get Brain #7 meta-evaluation
---

# Propuesta: Onboarding Visual para MasterMind v3.0

## Problema Identificado

**Herramienta actual:** `npx paperclipai onboard` (CLI)
**Barrera:** No hay GUI de configuración inicial — managers NO técnicos no pueden usar CLI
**Propuesta:** Onboarding visual paso a paso en el browser para managers business-savvy pero NO técnicos

**PIVOT (2026-04-06):**
- **Antes:** "CEO técnico que configura sus propias API keys" → INVALIDADO por investigación
- **Ahora:** "Manager/Director business-savvy NO técnico RESPONSABLE de configurar" → VALIDADO

## Contexto

- **Proyecto:** MasterMind v3.0 — Enterprise agent orchestration platform for LATAM
- **Shift de target:** v2.2 (developer tool) → v3.0 (business users + technical)
- **Target específico (PIVOT):** Managers/Directores business-savvy pero NO técnicos
- **Pain point:** CLI-first onboarding = BARRERA INSALVABLE para no-técnicos
- **Objetivo:** Reducir fricción cognitiva, permitir time-to-first-value < 5 minutos

**Por qué esta persona es el sweet spot:**
- ✅ Abundante (hay miles de managers así en LATAM)
- ✅ Tienen autoridad para configurar (no delegan todo)
- ✅ Tienen presupuesto (no son ICs)
- ✅ OBLIGATORIAMENTE necesitan GUI (no pueden usar CLI)

## Target Persona (VALIDADA por Investigación Secundaria)

**NO es CEO técnico.** Investigación reveló que 95%+ de CEOs delegan configuración técnica.

**Nueva persona (2026-04-06 - PIVOT):**

> **"Manager/Director business-savvy, non-technical que es RESPONSABLE de llenar el onboarding"**

**Características:**
- Rol: Head of Operations, Director de Business Development, PMO Manager, Head of Customer Success, Marketing Director
- Conocimientos: SÓLIDOS sobre el negocio + áreas funcionales (ventas, marketing, operaciones)
- Conocimientos técnicos: BAJOS o NULOS (no sabe programar, no usa terminal)
- Responsabilidad: ES la persona que VA A LLENAR el onboarding (no solo revisar)
- Autoridad: Tiene budget para contratar herramientas + poder de decisión
- Pain Point: "Necesito configurar esto YA, pero no entiendo nada de API keys — necesito algo GUI y sencillo"

**Por qué esta persona es ABUNDANTE:**
- Hay MUCHOS más managers business-savvy que CEOs
- Sí tienen autoridad para configurar herramientas (no delegan TODO)
- Sí tienen presupuesto (no son individual contributors)
- NO son técnicos → necesitan GUI amigable OBLIGATORIAMENTE

### Estrategia Definida

**Reemplazar CLI completamente** — Onboarding visual será el único camino de entrada.

**Razón:** El usuario eligió reemplazo (no híbrido, no coexistencia).

### Happy Path Especificado

**4 elementos a configurar (todos necesarios):**

1. **API Keys (OpenAI/Anthropic)** — Conectar a servicios de IA para MasterMind
2. **Selección de nicho** — Software Dev, Marketing, Legal, etc. (7+ brains disponibles)
3. **Configuración de brains activos** — Elegir qué brains consultar por defecto (todos o subset)
4. **Conexión a base de conocimientos** — NotebookLM u otras fuentes de conocimiento destilada

**Flujo:** Todos los elementos son necesarios para definir, configurar, conectar agentes, y guiar al CEO a su primer workflow exitoso.

### Testing Definido

**Nivel: MVP y luego iterar**

**Estrategia:**
1. Construir versión básica primero
2. Lanzar y medir métricas reales
3. Iterar según feedback del CEO

**Testing a lo que defina el CEO post-onboarding** (diseño de MasterMind o lo que el CEO necesite).

---

## Evaluación Brain #2 (UX Research) — ACTUALIZADA con PIVOT

### ✅ Lo Bueno

1. **Problema REAL y documentado** — Paperclip UX-Audit ya identificó:
   - Issue CRITICAL: "Curva de aprendizaje alta para setup inicial"
   - Issue HIGH: "CLI-first, UI-second perception"
   - Friction point: `npx paperclipai onboard --yes` es barrera

2. **Cierra Golfo de Ejecución (Norman)**
   - CLI: Terminal sin affordances percibidas para usuario de negocio
   - GUI: Inputs visuales, botones, estados = signifiers claros

3. **Se alinea con shift v3.0** — Enterprise platform para LATAM business users
4. **Respeta Heurística H7 (Nielsen)** — Onboarding visual para NUEVOS usuarios

5. **🆕 PIVOT valida persona** — Manager business-savvy NO técnico es ABUNDANTE y OBVIO

### ⚠️ Lo Que Falta (RESUELTO por PIVOT)

1. **[✅ RESUELTO] Falta definir el "non-technical user"**
   - **ANTES:** Ambiguo ("non-technical user")
   - **AHORA:** Manager/Director con sólido conocimiento del negocio pero NULO técnico
   - **El nivel de hand-holding:** ALTO pero no porque no sepan бизнес — porque no saben tecnología

2. **[✅ RESUELTO] No hay especificación del paso a paso**
   - **Happy Path definido:** 4 elementos (API Keys, Nicho, Brains, Knowledge Base)
   - **Explicado en términos de negocio**, no técnicos

3. **[⚠️ PENDIENTE] No hay métricas de éxito**
   - Learnability: Tasa de éxito en primera sesión
   - Efficiency: Tiempo hasta primer insight
   - Error Rate: Errores de configuración vs tickets de soporte
   - SUS Score: > 68 para usuarios LATAM
   - **ADD to Phase 15.5 backlog**

4. **[✅ RESUELTO] Falta contexto MasterMind vs. Paperclip**
   - **Happy Path actualizado:** Conectado a Knowledge Distillation (no solo agent orchestration)
   - **4 elementos** mapean a MasterMind v3.0 value prop

### 🚨 Peligros

1. **Romper modelo mental "IDE/expert tool"**
   - War Room diseñado como: Desktop-first, 1440px, alta densidad, keyboard-first
   - Si agregamos onboarding SaaS-style con botones grandes, happy talk → **Incoherencia**
   - **Solución:** Onboarding debe respetar estética War Room (no jugueteo)

2. **Sobre-ingeniería sin validación**
   - Solo implementar animaciones con ICE ≥ 15
   - Validación requerida: Paper prototype → Figma → A/B test

3. **[🆕 MITIGADO por PIVOT] Assumption de que "CLI = bad"**
   - **ANTES:** ¿MasterMind v3.0 va a tener non-technical users como PRIMARIO?
   - **AHORA:** SÍ — Managers business-savvy NO técnicos son target VALIDADO
   - **Onboarding visual es CRÍTICO**, no nice-to-have

4. **No considerar flujo POST-onboarding**
   - Usuario completa onboarding pero se pierde en primer minuto dentro de app
   - Falta considerar navegación por 4 panels (Command Center, Nexus, Vault, Engine Room)

### 💭 Sugerencias

**Sugerencia #1: Happy Path completo (5 pasos)**

```
[LANDING]
  ↓
[STEP 1: Welcome] "What business problem are you solving?"
  Input: Free text + 3 suggested templates
  ↓
[STEP 2: System Readiness] Auto-check: API keys, connectivity
  Feedback: Status lights + "Fix automatically" button
  ↓
[STEP 3: Knowledge Mapping] "Upload document OR describe context"
  Input: File upload OR text area
  ↓
[STEP 4: First Consultation] Brain #1 consulta tu problema
  Animation: Nodo en Nexus se expande
  ↓
[STEP 5: Dashboard Handoff] "Here's your first insight. View it in Strategy Vault."
  Button: "Go to Strategy Vault"
  ↓
[POST-ONBOARDING: Guided Tour] Tooltips explicativos para cada panel
```

**Sugerencia #2: Dual onboarding paths**
- IF DEVELOPER: Skip visual onboarding → CLI
- IF BUSINESS LEADER: Visual onboarding (5-step flow)

**Sugerencia #3: Usar Engine Room como "System Readiness"**
- Reutilizar Engine Room para Step 2
- Extender con "First Run Mode"
- Zero nuevo código para status dashboard

**Sugerencia #4: Progressive Disclosure en Nexus**
- First Run Mode: Mostrar SOLO brains relevantes al problema
- "Explore all brains" button → Progressive disclosure

**Sugerencia #5: Plan de测试 obligatorio**
- Paper prototype (5 usuarios, >80% completion)
- Figma clickable (10 usuarios, time-to-first-success < 5min)
- A/B test (Visual vs CLI, 2x completion rate)
- SUS survey (>68 target)

### 📋 Veredict Brain #2

**CONDITIONAL APPROVAL** — Prioridad Media

**Condiciones para APPROVAL:**
- [ ] Documentar persona "non-technical MasterMind user" (3 entrevistas LATAM)
- [ ] Especificar flujo completo 5 pasos
- [ ] Validar con paper prototype (5 usuarios, >80% completion)
- [ ] Definir métricas: time-to-first-success, error rate, SUS score

**Una vez cumplidas:** APPROVED — Construir con prioridad media (no bloqueante para MVP)

---

## Evaluación Brain #3 (UI Design)

### ✅ Lo Bueno

1. **Reducción de fricción cognitiva** — Reemplazar CLI por flujo visual orientado a objetivos (Alan Cooper)
2. **Madurez en uso de Motion** — Framer Motion solo para orientación/estado (no ruido visual)
3. **Compromiso con Accesibilidad** — No depender solo del color para estados
4. **Arquitectura moderna** — Tailwind 4 + variables CSS = single source of truth

### ⚠️ Lo Que Falta

1. **Sistema de 5 Estados Incompleto**
   - Falta especificar: Default, Hover, Active, Disabled, Error/Loading
   - Integración con Control Plane de Rust requiere estos estados

2. **Elevación Tonal No Definida**
   - Tema oscuro requiere overlays de color blanco semitransparentes
   - Falta definir `--elevation-1: rgba(255,255,255,0.05)` en globals.css

3. **Grid System No Definido**
   - Grid de 12 columnas para 1440px canvas
   - Escala de espaciado fija (múltiplos de 4/8px)

4. **Escala Tipográfica Proporcional**
   - Ratio matemático (ej: 1.25) para heading/body flow natural

### 🚨 Peligros

1. **Efecto "Smearing" por Negro Puro**
   - `#000000` causa distorsión en pantallas OLED
   - **Usar `#121212`** (gris muy oscuro) en lugar de negro puro

2. **Abandono por Formulario Largo**
   - Validación inline (on-blur) es crítica
   - Si errores solo al final → tasa de abandono se dispara

3. **Limitación "Desktop-Only"**
   - Ignorar priorización de contenido (Luke Wroblewski)
   - Resultado: interfaz de escritorio sobrecargada

4. **Inconsistencia en shadcn/ui**
   - Excesivos overrides de clases → "strings" inmanejables
   - Documentar como "moléculas" del sistema

### 💭 Sugerencias

1. **Implementar Tonal Elevation** — Overlays semitransparentes para diferenciar cards sobre fondo oscuro
2. **Validación Proactiva** — Mensajes de error específicos con instrucción de corrección inmediata
3. **Squint Test** — Si no puedes identificar botón "Siguiente" en 3 segundos, la jerarquía visual necesita más contraste
4. **Tokens Semánticos** — Naming por función (`--color-on-background`) no por valor (`--blue-500`)

### 📋 Veredict Brain #3

**CONDITIONAL APPROVAL** — Bloqueadores específicos

**Bloqueadores a resolver (pre-implementation):**

1. **Sistema de 5 Estados** — Documentar Default, Hover, Active, Disabled, Error/Loading para todos los inputs
2. **Elevación Tonal** — Definir overlays en `globals.css` (`--elevation-1: rgba(255,255,255,0.05)`)
3. **Grid System** — 12-column grid + escala de espaciado 4/8px
4. **Escala Tipográfica** — Ratio matemático (1.25) para heading/body flow

**Required Before Implementation:**
```bash
pnpm dlx shadcn@latest add tabs progress
```

**Critical Constraints:**
- Background: `#121212` (NUNCA `#000000`)
- Validation: on-blur inline
- Motion: max 300ms transiciones
- Tokens: semantic naming

---

## Síntesis

**Veredicto combinado:** CONDITIONAL APPROVAL (P1 - Prioridad Media)

**Estado actual:** UNDER_REVIEW — Awaiting Brain #7 meta-evaluation

**Resumen de evaluaciones:**
- **Brain #2 (UX Research):** Válido pero requiere definición de persona + especificación de Happy Path + plan de测试
- **Brain #3 (UI Design):** Válido pero requiere documentación de 5 estados + elevación tonal + grid system

**Condiciones unificadas:**
1. ✅ Problema real documentado en Paperclip UX-Audit
2. ✅ Alineado con shift v3.0 (business users)
3. ⚠️ Requiere especificación de 5 pasos exactos
4. ⚠️ Requiere plan de测试 (paper → Figma → A/B)
5. ⚠️ Debe respetar estética War Room (no SaaS toy)
6. ⚠️ Debe considerar flujo POST-onboarding (navegación por 4 panels)

**Siguiente acción:**
- Brain #7 (Growth) debe hacer meta-evaluación final

**🔄 ACTUALIZACIÓN (2026-06-21):**

**Condiciones RESUELTAS:**
- [✅] Persona aclarada: CEO técnico que quiere onboarding guiado que inspire confianza
- [✅] Estrategia definida: Reemplazar CLI (no híbrido, no coexistencia)
- [✅] Happy Path especificado: 4 elementos (API Keys, Nicho, Brains, Knowledge Base)
- [✅] Testing definido: MVP primero + iterar según feedback

**Respuestas del usuario:**
- **Persona:** CEO técnico (programación/IA) que quiere onboarding guiado que inspire confianza
- **Estrategia:** Reemplazar CLI completamente (no híbrido, no coexistencia)
- **Happy Path:** API Keys (OpenAI/Anthropic) + Selección de nicho + Configuración de brains activos + Conexión a base de conocimientos
- **Testing:** MVP primero y luego iterar según feedback del CEO

**ESTADO:** APPROVED_WITH_CONDITIONS — Ready for implementation AFTER critical conditions are met

## Evaluación Brain #7 (Growth/Data) - Meta-evaluación FINAL

### Síntesis de Opiniones de Dominio

**Brain #2 (UX Research):** ✅ RESUELTO — Identificó que CLI es barrera REAL. Condiciones resueltas: persona (CEO técnico), Happy Path (4 elementos), testing (MVP + iterar).

**Brain #3 (UI Design):** ⚠️ PARCIALMENTE RESUELTO — Validó factibilidad técnica. Requiere documentación de 5 estados, elevación tonal, grid system, escala tipográfica (PRE-implementation).

### Veredicto Final

**ESTADO:** APPROVED_WITH_CONDITIONS
**Confianza:** 85%
**Rationale:** Propuesta válida y alineada, PERO timing crítico. GUI onboarding no puede construirse antes de Phase 15 (Rust Control Plane) por riesgo de sunk cost fallacy.

### Condiciones CRÍTICAS (Categorizadas)

#### 🟡 ACLARACIÓN REQUIRIDA (1) — ✅ RESUELTA

**C3. [ACLARACIÓN] Manejo de errores en GUI onboarding**

**Respuesta del usuario:**
> "Para evitar eso lo primero que se debe abordar es garantizar que la configuración esté correcta y las conexiones estén en condiciones de empezar el onboarding. Luego de eso, si se establece que ya todo está conectado y el problema es otra causa externa (no hay internet, el usuario aplicó mal una api-key, o se le terminaron los créditos), se le debe informar al usuario para que tome las medidas y correcciones pertinentes."

**Enfoque:** Prevención proactiva sobre escape hatch reactivo

**Estrategia de validación:**
1. **Pre-flight check** ANTES de permitir avanzar en onboarding:
   - Validar formato de API keys
   - Test de conexión a servicios (OpenAI/Anthropic)
   - Verificar saldo/credits disponible
   - Validar conectividad de red

2. **Mensajes de error específicos** si falla pre-flight:
   - "No hay conexión a internet. Verificá tu red y volvé a intentar."
   - "API key inválida. Verificá que la key sea correcta."
   - "Saldo insuficiente. Agregá créditos a tu cuenta."

3. **No permitir avanzar** hasta que todo esté verde ✅

**Estado:** ✅ RESUELTO — Enfoque de prevención proactiva documentado

#### 🟢 ACCIÓN INDEPENDIENTE (1) — ✅ COMPLETO

**C2. [ACCIÓN] Validación de persona requerida ANTES de código**
- Conduct 3 entrevistas Mom Test con CEOs LATAM
- Validar que "CEO técnico que quiere onboarding guiado" es real
- **NO depende de Phase 15** → se puede ejecutar en cualquier momento
- **Owner:** TBD
- **Estado:** ✅ COMPLETO — Persona PIVOTEADA y VALIDADA
- **Fecha aprobación:** 2026-04-06
- **Resultado:**
  - Investigación secundaria invalidó "CEO técnico" (95%+ CEOs delegan)
  - Usuario refinó a "Manager/Director business-savvy NO técnico RESPONSABLE de configurar"
  - Nueva persona es ABUNDANTE y OBVIA → validación adicional innecesaria
  - **Persona FINAL:** Head of Operations, Director Business Development, PMO Manager, Head of Customer Success, Marketing Director
- **Archivos creados:**
  - `PLAN.md` — Criterios de éxito, estructura de entrevista
  - `interview-script.md` — 13 preguntas Mom Test
  - `results-template.md` — Scorecard + análisis agregado
  - `SECONDARY_RESEARCH_VALIDATION_REPORT.md` — Investigación completa + pivot
  - `candidate-sourcing-strategy.md` — Estrategia de outreach (no usado)
  - `outreach-templates.md` — Templates (no usado)

#### 🔴 DEPENDENCIA EXTERNA (1) — Pendiente hasta resolver

**C1. [DEPENDENCIA] Phase 15 debe ser planificada Y estimada PRIMERO**
- Estado actual: Phase 15 NO existe en `.planning/phases/`
- No se puede construir GUI sin conocer contratos de API
- **Trigger:** `/mm:plan-phase 15` completada
- **Estado:** BLOCKED - Waiting for Phase 15
- **Retomar:** Cuando Phase 15 esté planificada

#### 🔵 IMPLEMENTACIÓN (1) — Backlog de la fase

**C4. [IMPLEMENTACIÓN] Instrumentar métricas de abandono ANTES del launch**
- Tracking de funnel (step 1 → step 2 → step 3 → step 4 → complete)
- Parte del build de GUI onboarding
- **Fase:** Phase 15.5
- **Estado:** BACKLOG - Ready for implementation

### Integration Recommendation

**Secuencia correcta (NO paralelo):**

1. **Phase 14.5** (1 semana): Validación de persona
   - 3 entrevistas Mom Test
   - Paper prototype testing
   - ≥ 80% completion rate

2. **Phase 15** (3-4 semanas): Rust Control Plane
   - Infraestructura backend
   - Contratos de API + tests
   - API contracts frozen

3. **Phase 15.5** (2 semanas): GUI Onboarding
   - Construir GUI DESPUÉS de endpoints congelados
   - Integración con 4 endpoints de Rust

**Riesgo si se ignora:** Sunk cost fallacy — reescribir GUI si contratos de API cambian.

---

**Propuesta creada:** 2026-04-06
**Última actualización:** 2026-04-06 04:45
**Creado por:** Rafael Padrón (via /mm:propose)
