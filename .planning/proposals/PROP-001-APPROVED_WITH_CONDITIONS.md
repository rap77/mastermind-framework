---
id: PROP-001
title: "Onboarding Visual para MasterMind v3.0"
status: DRAFT
priority: P1
category: UX/UI
effort: M
updated: 2026-06-21 04:50
brain_evaluations:
  brain-02: CONDITIONAL_APPROVAL
  brain-03: CONDITIONAL_APPROVAL
  brain_07: APPROVED_WITH_CONDITIONS
final_verdict: APPROVED_WITH_CONDITIONS
next_actions:
  - Update Happy Path with user responses
  - Re-test with user persona clarification
  - Get Brain #7 meta-evaluation
---

# Propuesta: Onboarding Visual para MasterMind v3.0

## Problema Identificado

**Herramienta actual:** `npx paperclipai onboard` (CLI)
**Barrera:** No hay GUI de configuración inicial — usuarios no-técnicos no pueden usarlo
**Propuesta:** Onboarding visual paso a paso en el browser

## Contexto

- **Proyecto:** MasterMind v3.0 — Enterprise agent orchestration platform for LATAM
- **Shift de target:** v2.2 (developer tool) → v3.0 (business users + technical)
- **Pain point:** CLI-first onboarding = barrera enorme para usuarios no-técnicos
- **Objetivo:** Reducir fricción cognitiva, permitir time-to-first-value < 5 minutos

## Clarificaciones del Usuario (2026-06-21)

### Target Persona Aclarado

**NO es un "non-technical user" tradicional.** El usuario aclaró:

> *"Todo junto, no todos los CEOs no solo en LATAM sino también en el resto del mundo son técnicos en Programación o en IA. La idea sería que el onboarding sea guiado inspire confianza y sea de una manera, clara limpia, bien explicada, contestando cualquier duda del ceo."*

**Revelación clave:** Ya existe un agente encargado de este trabajo:
- Recibe al CEO
- Extrae ideas/flujo a automatizar
- **Genera formularios DINÁMICOS** (no fijos)
- Hace preguntas aclaratorias para llevarlo de la mano
- Propone crear los agentes necesarios para su primer equipo

**Implicación:** El onboarding NO es para "no-técnicos", es para **CEO técnicos que quieren onboarding guiado que inspire confianza**. El problema es UX, no falta de capacidad técnica.

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

## Evaluación Brain #2 (UX Research)

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

### ⚠️ Lo Que Falta

1. **Falta definir el "non-technical user"**
   - ¿CEO que nunca tocó terminal?
   - ¿Marketing manager que usa Gmail pero no sabe qué es API key?
   - **El nivel de hand-holding cambia drásticamente según el punto de partida**

2. **No hay especificación del paso a paso**
   - ¿Cuántos pasos? (Miller's Law: 7±2 chunks máximo)
   - ¿Qué info se captura en cada paso?
   - ¿Cuál es el "primer éxito"?

3. **No hay métricas de éxito**
   - Learnability: Tasa de éxito en primera sesión
   - Efficiency: Tiempo hasta primer insight
   - Error Rate: Errores de configuración vs tickets de soporte
   - SUS Score: > 68 para usuarios LATAM

4. **Falta contexto MasterMind vs. Paperclip**
   - Paperclip: Orquestar agentes (crear company, agents, goals)
   - MasterMind v3.0: Knowledge distillation (consultar expertos destilados)
   - **El onboarding debe ser diferente:**
     - ¿Selección de nicho?
     - ¿Configuración de brains activos?
     - ¿Conexión de API keys?

### 🚨 Peligros

1. **Romper modelo mental "IDE/expert tool"**
   - War Room diseñado como: Desktop-first, 1440px, alta densidad, keyboard-first
   - Si agregamos onboarding SaaS-style con botones grandes, happy talk → **Incoherencia**
   - **Solución:** Onboarding debe respetar estética War Room (no jugueteo)

2. **Sobre-ingeniería sin validación**
   - Solo implementar animaciones con ICE ≥ 15
   - Validación requerida: Paper prototype → Figma → A/B test

3. **Assumption de que "CLI = bad"**
   - ¿MasterMind v3.0 va a tener non-technical users como PRIMARIO?
   - Si SÍ → Onboarding visual es CRÍTICO
   - Si NO → Onboarding visual es NICE-TO-HAVE

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

### Condiciones CRÍTICAS (BLOCKERs)

1. **[BLOCKER] Phase 15 debe ser planificada Y estimada PRIMERO**
   - Estado actual: Phase 15 NO existe en `.planning/phases/`
   - No se puede construir GUI sin conocer contratos de API

2. **[BLOCKER] Validación de persona requerida ANTES de código**
   - Conduct 3 entrevistas Mom Test con CEOs LATAM
   - Validar que "CEO técnico que quiere onboarding guiado" es real

3. **[CONDITION] Definir escape hatch para reemplazo de CLI**
   - Opción A: Comando de emergencia `npx mastermind-cli onboard --emergency`
   - Opción B: Edición directa de config `~/.mastermind/config.yaml`

4. **[CONDITION] Instrumentar métricas de abandono ANTES del launch**
   - Tracking de funnel (step 1 → step 2 → step 3 → step 4 → complete)

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
