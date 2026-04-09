# BRAIN-FEED-02 — UX Research Domain Feed

> Written by Brain #2 (UX Research). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-03-28

---

## Strategic Anchors — v2.2 Foundation Facts

- War Room = IDE, not SaaS dashboard. Interaction model: developer-as-composer orchestrating agents, not consumer browsing a product.
- 4-panel layout locked (Command Center, The Nexus, Strategy Vault, Engine Room) — no panel additions without Phase N+1 PRD.
- ICE Scoring ≥ 15 for animations — proven in Phase 06. Below threshold = over-engineering.
- Efficiency > Learnability: Expert speed (Time-on-task) > new user success. No "onboarding tours" — those are SaaS patterns, not IDE patterns.
- High Information Density: Use Chunking (Miller's Law) to organize data, NOT "minimalism" that removes necessary context.
- Engine Status Feedback (H1): Every uv/pnpm action needs immediate visual feedback (loading states, mini-consolas) — close the Gulf of Evaluation.

---

## Migrated Patterns — from BRAIN-FEED.md Phase 00-09

- ICE Scoring prevents over-engineering — only implement animations with ICE ≥ 15 [Phase 06 — UX decision framework owner]

---

## SYNC Cross-References

[none — Brain #2 UX is the owner of ICE Scoring, not a consumer]

---

## 2026-03-29 — Brain Navigation Request (15-tab system rejected)

### Verified Insights

- **15-tab brain navigation = Hick's Law violation.** 15 equal-weight choices create scanning mode on every context switch. Decision time grows logarithmically — directly contradicts the keyboard-first, expert-speed mandate.
- **Tabs are the wrong affordance for brain context.** Tabs signify equivalent pages in horizontal relationship. In War Room, a brain is a DATA CONTEXT flowing into the 4 existing panels — not a destination. Using tabs misrepresents the affordance (Norman: Conceptual Model mismatch).
- **Command Center BentoGrid already IS the brain navigator.** Jakob's Law: users expect a central hub for selection (BentoGrid) + specialized views for execution (4 panels). Adding 15 tabs duplicates the BentoGrid role, creates H4 Consistency violation, and breaks the conceptual model.
- **Mapping conflict: 15 tabs vs. 24 brains.** If the BentoGrid shows 24, why are only 15 tab-worthy? This creates a Gulf of Execution — user doesn't know how to reach the other 9. This is a direct Norman signifier failure.
- **Correct pattern for expert brain-switching: Command Palette (Cmd+K).** Fuzzy search over brain name/niche. Zero scanning, keyboard-first, instantaneous. This is VS Code's Cmd+P pattern applied to the War Room context.
- **Secondary pattern if persistent nav is genuinely needed: MRU working set (<5 items).** Show only recently-used brains in a pinned strip — not all 15/24. Respects Miller's 4±1 working memory constraint.

### Deferred Items

- 📅 Command Palette (Cmd+K) for brain/niche search — Phase 12 candidate. Requires: fuzzy search over brains API response already in TanStack Query cache, no new API needed.
- 📅 MRU pinned-brain strip (<5 items) in global header — Phase 12 candidate, only if observational data shows users repeatedly switching between same 2-3 brains mid-session.

---

## 2026-03-31 — Autonomous Agent Architecture Evaluation (v3.0 direction)

### Verified Insights

- **Mental Model Shift: "Invoke → Await" to "Trigger → Observe Chain".** This is a Norman conceptual model change, not just a feature addition. The War Room UI must expose the reasoning path — not just that Brain #4 is running, but *why* (Brain #1 detected frontend_implications). Without this, the Gulf of Evaluation widens: user sees motion but cannot close the feedback loop.

- **HybridFlowEdge already handles the brain_routing signal — no new component needed.** Edge state machine (idle/active/complete/error) reads from brainStore on every render. When brain_routing WebSocket event updates source brain status to 'active', edges in the Nexus animate automatically. ICE check: this is orientation (user understands which branch is executing live) — ICE >= 15 confirmed. NOT decoration.

- **brain_routing is a new WS event type — wsStore.subscribe() already supports arbitrary event types.** The routing signal surfaces in The Nexus only (DAG is the correct affordance for directional flow). Command Center BrainTiles show individual brain status (already works). No new subscriber architecture needed, only new event type registration.

- **Strategy Vault owns brain experiences (GET /api/experiences/{brain_id}).** It already owns execution history (GET /api/executions/history). Mental model: Vault = "what the system knows and has done." Adding experiences is additive, not a panel redesign. Progressive disclosure: BrainTile hover/click can surface a memory count badge, but the full experience log belongs in the Vault.

- **Focus Mode anxiety management for multi-minute chains.** Current isFocusMode activates on task start, deactivates on complete. With chained agents, "complete" may not arrive for 2-5 minutes. Missing feedback pattern: a Chain Progress indicator showing "Brain 2 of 4 — Frontend Analysis" uses the Zeigarnik Effect (incomplete task stays salient) and prevents anxiety from silence. This is NOT an animation — it is functional status text.

- **Routing transparency rule: label the WHY, not just the WHAT.** When brain_routing fires, the system must surface "Brain #4 dispatched — frontend_implications detected in Brain #1 output." This text belongs in the Engine Room LiveLogPanel (already has live log infrastructure). The Nexus shows it visually; the Engine Room shows it textually. Two-channel feedback = expert confidence.

### Deferred Items

- 📅 Chain Progress bar/breadcrumb (Zeigarnik pattern) in Command Center header — Phase 12/v3.0 candidate. Required state: orchestratorStore extended with chainSteps: Step[] where Step = {brainId, label, status}. No backend contract change needed if brain_routing events include step sequence.
- 📅 BrainTile memory count badge (progressive disclosure for experiences) — Phase 12/v3.0 candidate. Source: GET /api/experiences/{brain_id} count field. Max 1 API call per brain on hover (TanStack Query cache, staleTime 30s covers session).
- 📅 "Routing reason" label on Nexus edges — show the implication type (frontend/backend/ux) on the animated edge — Phase 12/v3.0 candidate. Requires: React Flow edge data prop + HybridFlowEdge extended to render an SVG foreignObject label.

## 2026-04-06 — Onboarding Visual Proposal Evaluation (Paperclip CLI → GUI)

### Verified Insights

- **CLI-based onboarding es REAL problem para non-technical users.** Evidencia: Paperclip UX_RESEARCH_ANALYSIS.json encontró "Curva de aprendizaje alta" (CRITICAL) + "CLI-first perception" (HIGH). Usuario no-técnico ve `npx paperclipai onboard --yes` sin affordances/signifiers — Golfo de Ejecución sin puente (Norman).

- **Reconocimiento > Recuerdo para business users.** CLI depende de memoria de trabajo (recuerda flags, sintaxis); GUI depende de reconocimiento (inputs visuales, botones, estados). Miller's Law: 7±2 chunks. Un comando CLI con múltiples flags rompe este límite si el usuario no entiende la sintaxis, generando "Mistakes" (errores de modelo mental) no "Slips".

- **Onboarding visual NO rompe War Room si aplica Heurística H7.** H7 (Nielsen): Flexibilidad y eficiencia. Visual onboarding para nuevo usuario business + CLI disponible como acelerador para developer. No es reemplazo, es camino paralelo de entrada.

- **Respetar estética War Room en onboarding.** Status Dashboard de alta densidad (no "Welcome"), luces de estado (mapeo natural verde/rojo), logs estilo terminal DENTRO del GUI. Zero happy talk — ir directo a la utilidad (Krug: "Users don't read, they scan").

- **Happy Path debe ser end-to-end, no solo setup.** 5 pasos: (1) Welcome + business goal, (2) System Readiness Check (auto), (3) Knowledge Mapping (upload doc o contexto), (4) First Consultation (Brain #1), (5) Dashboard Handoff (Strategy Vault). Miller's Law: 5 pasos (7±2 chunks). Zeigarnik Effect: First consultation incomplete → urge a completar.

- **Progressive Disclosure en The Nexus para first-run users.** Mostrar SOLO brains relevantes para el problema del usuario (ej: "mejorar UX" → brains #1, #2, #3). "Explore all brains" button para ver otros 21. H5: Prevención de errores — no abrumar con choices irrelevantes.

### Deferred Items

- 📅 **Dual onboarding paths por persona** — Phase 15/v3.0.1. Landing pregunta: "developer or business leader?" → Developer skip to Command Center (CLI: `npx mastermind-cli configure`), Business leader entra en visual onboarding (5-step flow). Requiere: landing page redesign + persona detection logic.

- 📅 **Engine Room como System Readiness dashboard** — Phase 15/v3.0.1. Extender Engine Room con "First Run Mode" que muestre status lights de dependencias + "Fix automatically" button. Ventajas: zero nuevo código, usuario aprende Engine Room desde inicio, consistencia (setup + monitoreo mismo panel).

- 📅 **Paper prototype + Figma validation** — Phase 14.5 (pre-build). Plan: (1) Paper prototype con 5 usuarios LATAM (>80% completion), (2) Figma clickable con 10 usuarios (time-to-first-success < 5 min), (3) A/B test Visual vs. CLI (2x completion rate target), (4) SUS survey (>68 target). SI CUALQUIER fase falla → iterar o pivotar antes de código.

- 📅 **Guided Tour dismissible para War Room panels** — Phase 15/v3.0.1. Post-onboarding: Tooltips para Command Center, Nexus, Vault, Engine Room. Dismissible después de primera interacción. Progressive disclosure: explicar panel cuando usuario lo necesita.

### Decisions Logged

- **Onboarding visual = CONDITIONAL APPROVAL.** Válido y alineado con v3.0 shift, PERO requiere: (1) Definir "non-technical user persona" con 3+ entrevistas LATAM, (2) Especificar flujo completo 5 pasos (inputs/validaciones), (3) Validar con paper prototype (5 usuarios, >80% completion), (4) Definir métricas: time-to-first-success, error rate, SUS score. Una vez cumplidas → APPROVED con PRIORIDAD MEDIA (no blocking para MVP v3.0).

- **No reemplazar CLI, agregar camino paralelo.** CLI sigue funcional para usuarios técnicos. Onboarding visual es entrada alternativa para business users. Respeta H7 (flexibilidad) sin alienar audiencia existente.

---

## 2026-04-08 — Phase 17 UI Evolution Patterns Analysis

### Verified Insights

#### 1. Multi-tenant Company Switching — Always-visible CompanyRail APPROVED

**Cognitive Load Assessment (Miller's Law):**
- CompanyRail debe limitarse a **7 ± 2 tenants visibles** para evitar sobrecarga de memoria de trabajo
- Superar este umbral requiere "chunking" (agrupación por entorno: dev/staging/prod)
- Hick's Law: más opciones = tiempo logarítmico de decisión. Alt + [1-9] shortcuts eliminan escaneo visual

**Mental Model Alignment (Jakob's Law):**
- Alineación con Slack/Discord: cambio de contexto = acción de nivel superior constante, no modal transitorio
- El usuario experto espera visibilidad perenne del contexto actual (affordance: "¿dónde estoy?" siempre visible)

**Interaction Pattern:**
- `Alt + [1, 2, 5-11]` para cambio directo (keyboard-first, expert speed)
- Click en avatar del rail para switch manual (mouse fallback)
- Collapse/expand con botón en header (ya existe en CompanyRail.tsx)

**Feedback Specification (Nielsen H1):**
- **100ms:** Cambio de estado visual en CompanyRail (borde activo, fondo destacado)
- **<1s:** Re-renderizado completo de DAGs en The Nexus (mantener fluidez percibida)
- **10s:** Timeout con mensaje de error si el cambio de tenant falla

**Recovery Path:**
- Botón "Back to previous tenant" (`Cmd + [`) visible en el header tras el cambio
- Undo snackbar (Nielsen H3) si el usuario activa el tenant equivocado accidentalmente

**War Room Context:**
- Afecta a toda **ThreeColumnLayout** — re-inyecta contexto de Zustand en las 4 pantallas
- CompanyRail.tsx ya existe (62 lines, placeholder en Plan 17-01) — extender con lógica multi-tenant

**Grep Verification:**
- ✅ CompanyRail.tsx existe — collapsible, placeholder listo para extender
- ✅ layoutStore.ts existe — Zustand + Immer + persist, patrón establecido
- ✅ Alt key shortcuts — NO existe aún, agregar en Plan 17-02

#### 2. Mobile Interaction Patterns — Bottom Nav + Swipe APPROVED

**Cognitive Load Assessment (Hick's Law):**
- Bottom nav debe tener **máximo 5 opciones** para minimizar tiempo de decisión en contextos móviles
- Más de 5 = escaneo visual en cada tap, rompiendo la heuristic de eficiencia

**Mental Model Alignment (Norman's Seven Stages of Action):**
- **Bottom Nav = "¿Dónde estoy?"** (affordance de ubicación, navegación principal)
- **Swipe = "¿Qué puedo hacer aquí?"** (affordance de acción sobre el elemento visible)
- Separación clara: navegación (tap) vs ejecución (swipe) — dos canales distintos, reducen Gulf of Execution

**Interaction Pattern:**
- Swipe a la derecha en un agente para "Quick Deploy" (acelerador para expertos, Nielsen H7)
- Tap en Bottom Nav para cambio de pantalla (Command Center, Nexus, Vault, Engine Room)
- Long-press para menú contextual (acción secundaria, progressive disclosure)

**Feedback Specification:**
- **100ms:** Vibración háptica en swipe exitoso (confirmación inmediata)
- **>1s:** Indicador de progreso si la acción toma más de 1 segundo (Nielsen H2)
- **Error:** Shake animation + toast message si el swipe falla (recoverability)

**Recovery Path:**
- "Undo" snackbar (Nielsen H3) tras swipe accidental con 5s timeout
- Swipe reverso (derecha→izquierda) para cancelar la acción

**War Room Context:**
- Afecta a la vista colapsada de **Command Center** (mobile <768px)
- ThreeColumnLayout ya tiene mobile breakpoints (single column) — agregar Bottom Nav y swipe gestures

**Grep Verification:**
- ✅ ThreeColumnLayout.tsx existe — mobile breakpoints implementados
- ❌ Bottom Nav — NO existe, agregar en Plan 17-03
- ❌ Swipe gestures — NO existe, agregar en Plan 17-03

#### 3. Real-time Monitoring UX — ActiveAgentsPanel APPROVED

**Cognitive Load Assessment (Vigilance Decrement):**
- **Efecto Von Restorff:** Solo agentes en estado `ERROR` o `CRITICAL` rompen la cuadrícula visual
- Los estados `idle` y `active` se funden en el fondo (opacity reducida) para evitar fatiga de atención
- Alert fatigue gestionada agrupando ráfagas de >10 eventos en un solo "Batch Alert" cada 10s

**Mental Model Alignment (Natural Mapping):**
- Rojo = Peligro/Error (mapeo universal, affordance sin aprendizaje)
- Verde = Activo/Completado (semaforización estándar)
- Gris = Idle (no requiere atención)
- Animación "pulse" solo en `active` (orientación, no decoración)

**Interaction Pattern:**
- Click en badge para filtrar el log de WebSocket por ese brain específico
- `Cmd + Click` para "Focus Mode" en un cerebro específico (aislar su actividad)
- Hover para ver timestamp y último evento (progressive disclosure)

**Feedback Specification:**
- **60fps:** RAF batching garantiza movimiento orgánico durante brain burst (24 eventos simultáneos)
- **100ms:** Cambio de color en badge cuando el estado cambia (WS event → DOM update)
- **>1s:** Si un brain está en `active` por >10s, mostrar indicador "stuck" (possible error)

**Recovery Path:**
- Botón "Clear all warnings" en el panel lateral para resetear estado visual
- Click en "Dismiss" en cada alerta individual para eliminarla sin afectar otros brains

**War Room Context:**
- Localizado exclusivamente en **ActiveAgentsPanel** dentro del **Engine Room**
- brainStore.ts ya usa RAF batching (líneas 44-50) — patrón probado, 60fps mantenido
- BrainTile.tsx ya tiene status-based styling (idle/active/complete/error) — extender para filtering

**Grep Verification:**
- ✅ brainStore.ts existe — RAF batching implementado (líneas 44-50)
- ✅ BrainTile.tsx existe — status-based styling (animate-pulse, border colors)
- ❌ ActiveAgentsPanel — NO existe, crear en Plan 17-02
- ❌ WebSocket log filtering — NO existe, agregar en Plan 17-02

#### 4. Command Palette Discoverability — Persistent Search Signifier APPROVED

**Cognitive Load Assessment (Gulf of Execution):**
- Input de búsqueda en AppSidebar con placeholder "Search commands... (Cmd+K)" como **signifier**
- Reduce el Golfo de Ejecución al hacer evidente la acción posible sin necesidad de descubrir el shortcut
- Usuario experto: `Cmd + K` (memoria muscular). Usuario novato: click en input (descubrimiento visual)

**Mental Model Alignment (Jakob's Law):**
- Convención estándar de IDEs (VS Code Cmd+Shift+P, Raycast Cmd+K)
- El experto ya domina el patrón — zero aprendizaje, solo aplicación al contexto War Room
- Modal flotante = affordance de "acción global" (no atada a ningún panel específico)

**Interaction Pattern:**
- `Cmd + K` (primary) — keyboard-first, expert speed
- Click en input de búsqueda en AppSidebar (secondary) — mouse fallback
- `Esc` para cerrar instantáneamente (Nielsen H3: user control and freedom)

**Feedback Specification:**
- **<100ms:** Despliegue del modal (sin animaciones decorativas, solo fade-in rápido)
- **Real-time:** Filtrado de resultados conforme se escribe (tan pronto como haya 2 caracteres)
- **Empty state:** Mensaje "No commands found" + sugerencias alternativas

**Recovery Path:**
- `Esc` para cerrar y volver al foco anterior (undo sin confirmación)
- `Backspace` completo para limpiar el input y empezar de nuevo

**War Room Context:**
- Global — el Palette debe flotar sobre cualquier pantalla de producción
- Debe incluir: brains (fuzzy search por nombre/niche), comandos de sistema (focus mode, settings), navegación (ir a panel)
- Fuente de datos: TanStack Query cache (GET /api/brains ya está cacheado, staleTime 30s)

**Grep Verification:**
- ❌ Command Palette — NO existe (solo test file en lib/__tests__/commands.test.ts)
- ✅ AppSidebar.tsx existe — tiene espacio para input de búsqueda (líneas 107)
- ✅ TanStack Query cache — ya existe para brains, no requiere nueva API

#### 5. Onboarding Flow Design — Quick Setup (Manifest Injection) APPROVED

**Cognitive Load Assessment (Expert User Model):**
- **Zero "Happy Talk"** — eliminar frases obvias ("Welcome to War Room!") que aumentan fricción
- Usuario es el creador: su modelo mental ya coincide con el sistema
- Onboarding debe ser una **herramienta de configuración**, no de aprendizaje

**Mental Model Alignment (Recognition over Recall):**
- **Drag & Drop** de archivo `.env` o `.json` de configuración = reconocimiento (ve el archivo, lo arrastra)
- CLI alternativa = recuerdo (debe recordar flags y sintaxis) — menos eficiente para first-time setup
- Config validation inmediata = error prevention (Nielsen H5)

**Interaction Pattern:**
- Drag & Drop de archivo de configuración directamente en **Command Center**
- Alternativa: "Paste config" textarea para copiar/pegar desde clipboard
- Botón "Load example config" para ver un template válido (progressive disclosure)

**Feedback Specification:**
- **1s:** Validación de esquema con indicadores visuales (líneas específicas marcadas en rojo)
- **<100ms:** Toast message "Config loaded successfully" con botón "Continue to Dashboard"
- **Error:** Signifiers rojos en líneas específicas + mensaje de error técnico (no "Something went wrong")

**Recovery Path:**
- Enlace a "Example Config" (template válido)
- Botón "Reset to defaults" para volver a configuración inicial
- "Discard changes" si el usuario quiere cancelar y volver al estado anterior

**War Room Context:**
- Pantalla de inicio de **Command Center** cuando no hay contexto detectado (primera visita)
- No es un wizard multi-step — es single-step config injection (respeta expert efficiency)
- Después de config exitosa → redirect al dashboard normal (no onboarding tour)

**Grep Verification:**
- ✅ CommandCenterWrapper.tsx existe — puede detectar "first visit" state
- ❌ Config upload/validation — NO existe, agregar en Plan 17-03 (o Phase 18 si baja prioridad)

#### 6. Accessibility Requirements (WCAG AA) — Focus Visible + ARIA Live APPROVED

**Cognitive Load Assessment (Binary Threshold):**
- **Foco visible** es crítico o no lo es — no hay "parcialmente visible" (binario: se ve o no se ve)
- Para usuarios de teclado, el foco es LA affordance primaria de "¿dónde estoy?"
- Hick's Law no aplica aquí — es un requisito baseline, no una decisión de diseño

**Mental Model Alignment (Keyboard-First Expectation):**
- El usuario experto espera que el teclado sea ciudadano de primera clase
- Navegación por `Tab` debe seguir el orden lógico de **ThreeColumnLayout** (CompanyRail → Sidebar → Main Content)
- `Enter/Space` para ejecutar la acción enfocada (botón, link, tile)

**Interaction Pattern:**
- `Tab` y `Shift + Tab` para navegación hacia adelante/atrás
- `Enter/Space` para ejecución (activar botón, expandir sidebar, etc.)
- `?` shortcut global para mostrar mapa de accesibilidad y atajos

**Feedback Specification:**
- **Foco visible:** Borde de 2px en color de contraste (shadcn/ui ya tiene `ring-2 ring-offset-2`)
- **ARIA Live Regions:** `aria-live="polite"` para actualizaciones de estado de agentes (brain status changes)
- **Screen reader announcements:** Cambios de estado en BrainTile (idle → active → complete) deben anunciarse

**Recovery Path:**
- Shortcut `?` siempre accesible para mostrar ayuda contextual
- "Skip to main content" link al inicio del documento (para evitar tabular por toda la navegación)

**War Room Context:**
- Implementado transversalmente mediante **shadcn/ui** (componentes base ya tienen focus visible)
- **Tailwind 4** utilities (`focus-visible:ring-2`) aplicadas a todos los elementos interactivos
- ARIA labels agregados en CompanyRail, AppSidebar, BrainTile, y cualquier componente con estado

**Grep Verification:**
- ✅ shadcn/ui components — ya tienen focus-visible styling
- ✅ globals.css — tiene focus-visible rules (líneas con `focus-visible:`)
- ❌ ARIA Live Regions — NO existe para WebSocket updates, agregar en Plan 17-02
- ❌ Skip to main content link — NO existe, agregar en Plan 17-02

### Codebase Verification Summary

| Pattern | Exists | Missing | Plan Reference |
|---------|--------|---------|----------------|
| CompanyRail multi-tenant | ✅ placeholder | ❌ Alt shortcuts, tenant switch logic | 17-02 |
| Mobile Bottom Nav | ✅ breakpoints | ❌ Bottom Nav component, swipe gestures | 17-03 |
| ActiveAgentsPanel | ✅ brainStore RAF | ❌ Panel component, log filtering | 17-02 |
| Command Palette | ❌ | ❌ Todo (cmdk integration, fuzzy search) | 17-03 |
| Onboarding Config Upload | ✅ CommandCenter | ❌ Drag & drop, validation UI | 17-03 or 18 |
| ARIA Live Regions | ✅ focus-visible | ❌ aria-live for WS updates | 17-02 |

### Deferred Items

- 📅 **Command Palette (Cmd+K) implementation** — Plan 17-03 candidate. Requiere: cmdk library (o custom implementation), integración con TanStack Query cache para brains, fuzzy search por nombre/niche.
- 📅 **Mobile Bottom Nav + Swipe gestures** — Plan 17-03 candidate. Requiere: BottomNav component (5 items max), react-use-gesture library para swipe, undo snackbar.
- 📅 **ActiveAgentsPanel con filtering** — Plan 17-02 candidate. Requiere: nuevo componente en Engine Room, integración con brainStore para filtering, WebSocket log filtering por brain ID.
- 📅 **Onboarding Config Upload** — Plan 17-03 or Phase 18 candidate. Prioridad media (expertos pueden usar CLI). Requiere: Drag & drop zone, YAML/JSON validation, example config template.

### Decisions Logged

- **CompanyRail always-visible APPROVED.** Alineado con expert user model (Slack/Discord pattern). Limitar a 7±2 tenants visibles (Miller's Law). Alt + [1-9] shortcuts para keyboard-first efficiency.
- **Bottom Nav + Swipe APPROVED for mobile.** Bottom Nav para navegación (5 items max, Hick's Law), Swipe para ejecución de comandos (acelerador para expertos). Separación clara de affordances (Nav vs Action).
- **ActiveAgentsPanel con Von Restorff effect APPROVED.** Solo ERROR/CRITICAL rompen la cuadrícula visual. Alert fatigue gestionada con Batch Alert (>10 events grouped). RAF batching mantiene 60fps (ya probado).
- **Command Palette (Cmd+K) APPROVED.** Signifier persistente en AppSidebar ("Search commands... (Cmd+K)"). Dos canales: keyboard (expert) + click (discoverability). Fuzzy search sobre cache existente (no new API).
- **Quick Setup Onboarding APPROVED.** Drag & Drop de config file (manifest injection), no wizard multi-step. Zero happy talk, direct utility. Config validation inmediata con signifiers rojos.
- **Accessibility (WCAG AA) APPROVED as baseline.** Focus visible (shadcn/ui ya lo tiene), ARIA Live Regions para WebSocket updates, `?` shortcut para help map. No es "feature", es requisito baseline.
