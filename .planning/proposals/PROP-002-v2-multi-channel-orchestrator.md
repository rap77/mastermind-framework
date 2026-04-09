---
id: PROP-002-v2
title: "Multi-Channel Orchestrator Interface — WhatsApp, Planning & Migrations"
status: CONDITIONAL_APPROVAL
priority: P2
category: Feature
effort: L
updated: 2026-04-06
replaces: PROP-002
brain_evaluations:
  brain-01: CONDITIONAL_APPROVAL
  brain-02: CONDITIONAL_APPROVAL
  brain-03: NOT_APPLICABLE
  brain-04: CONDITIONAL_APPROVAL
  brain-05: CONDITIONAL_APPROVAL
  brain_07: CONDITIONAL_APPROVAL
final_verdict: CONDITIONAL_APPROVAL
consensus: 5/5 brains agree — Concierge MVP FIRST, then separate into 3 proposals
confidence: 65%
next_steps: "See Brain #7 evaluation at end of file"
---

# Propuesta: Multi-Channel Orchestrator Interface — WhatsApp, Planning & Migrations

## Problema Identificado

**Paperclip actual NO tiene chat con el Orquestador** — Solo inbox (tickets) o comandos directos.

**Casos de uso reales:**

### Caso 1: CEO pidiendo reporte financiero URGENTE

```
Contexto: Reunión con gerencia/inversores en 15 minutos
Canal: WhatsApp (mobile, asíncrono)
Input: "Necesito reporte de gastos del mes"
Output: Reporte generado y enviado

¿Por qué inbox/tickets NO sirven?
- Inbox: Requiere abrir dashboard, no es mobile-first
- Tickets: Demasiado lento para "dame el dato YA"
```

### Caso 2: Implementador migrando desde N8N

```
Contexto: Cliente quiere migrar flujos existentes de N8N a MasterMind
Input: Compartir JSON/flujo de N8N al agente
Output: Análisis + recomendación de agentes a crear para replicar workflow

¿Por qué es valioso?
- Reduce weeks de análisis manual a minutos
- Caso de uso REAL de onboarding (migrar desde herramientas existentes)
```

### Caso 3: Planning — "Quiero hacer X, ¿qué agentes necesito?"

```
Contexto: User quiere automatizar un proceso pero no sabe cómo
Input: "Quiero automatizar facturación electrónica"
Output: Agente recomienda qué agentes crear, qué hace cada uno

¿Por qué es valioso?
- Reduce barrera de entrada para nuevos usuarios
- El Orquestador conoce TODAS las capacidades del sistema
```

## Contexto

- **Proyecto:** MasterMind v3.0 — Enterprise agent orchestration platform with Knowledge Distillation
- **Stack:** Next.js 16 + React 19 + Python FastAPI + Rust Control Plane
- **UI:** War Room — 4 screens (Command Center, Nexus, Strategy Vault, Engine Room)
- **Target:** Business users + technical users
- **Referencia:** Paperclip (clon) — Paperclip NO tiene esta funcionalidad

## Características Clave

### 1. Multi-Canal (No solo WhatsApp)

```
Phase 1 (v3.0):
├── WhatsApp Business API (primario)
│   ├── Mobile-first
│   ├── Asíncrono
│   └── Auth: phone number → user mapping
│
└── Dashboard Chat (secundario)
    ├── Embedded en War Room
    └── Para usuarios que YA están en el dashboard

Phase 2+ (v3.1+):
├── Email gateway
├── Telegram
└── SMS (para alertas críticas)
```

**Nota:** No TODO el mundo tiene acceso desde WhatsApp. Solo usuarios autorizados.

### 2. Tres Chat-Only Superpowers

Estas cosas SOLO el chat puede hacer (Command+K, dashboards NO sirven):

| Superpower | Qué hace | Por qué es chat-only |
|------------|----------|---------------------|
| **Reportes Ejecutivos** | "Envíame gastos del mes" / "¿Cuál es el total de ventas?" | Mobile, asíncrono, fuera del dashboard |
| **Análisis de Migración** | Compartir JSON de N8N → agente analiza y recomienda agentes | Input complejo (archivo) + síntesis experta |
| **Planning Asistido** | "Quiero automatizar X" → agente recomienda arquitectura | Requiere diálogo (preguntas/respuestas) |

### 3. Role-Based Security (Confidencialidad)

```
CEO:
✅ Puede ver: Finanzas, KPIs ejecutivos, todo
❌ No puede ver: Logs técnicos, configuración

Manager:
✅ Puede ver: KPIs de su área, tareas
❌ No puede ver: Finanzas completas, otros áreas

Technical:
✅ Puede ver: Logs, configuración, métricas técnicas
❌ No puede ver: Información financiera sensible
```

**Implementación:**
- Auth: Phone number → user mapping en WhatsApp
- Filtro: Respuesta del agente depende del rol del usuario
- Auditoría: Todas las queries logueadas (compliance)

### 4. Migraciones desde N8N (Modular)

```
Phase 1 (v3.0):
└── MVP: Análisis de flujos simples N8N
    ├── Input: JSON exportado de N8N
    ├── Output: Lista de agentes a crear
    └── Agente: "n8n-migration-analyst" (especializado)

Phase 2+ (v3.1+):
└── Migraciones completas
    ├── N8N specialist agents
    ├── Zapier specialist agents
    └── Make (Integromat) specialist agents
```

**Nota:** Cada herramienta de automatización tiene sus propios agentes especializados.

## Diferenciación vs Paperclip

| Feature | Paperclip | MasterMind v3.0 |
|---------|----------|-----------------|
| Comunicación con Orquestador | Inbox (tickets) SOLO | Multi-canal (WhatsApp, dashboard chat) |
| Mobile-first | ❌ No | ✅ Sí (WhatsApp) |
| Asíncrono | ❌ No (solo sync en dashboard) | ✅ Sí |
| Reportes ejecutivos | ❌ No | ✅ Sí |
| Análisis de migración | ❌ No | ✅ Sí (N8N, Zapier, Make) |
| Planning asistido | ❌ No | ✅ Sí |

## Auth Strategy

### WhatsApp (Phase 1)

```
1. Usuario registra phone number en su perfil
2. Sistema envía mensaje de verificación
3. Phone number mapeado a user_id
4. Mensajes de WhatsApp → autenticados por phone number
5. Respuestas filtradas por rol del usuario
```

### Dashboard Chat (Phase 1)

```
1. Usuario ya autenticado (JWT)
2. Chat hereda auth de la sesión
3. Respuestas filtradas por rol del usuario
```

## Scope MVP (v3.0)

### Incluye

✅ WhatsApp Business API integration
✅ 3 superpowers:
   - Reportes ejecutivos (financieros, KPIs)
   - Planning asistido ("Quiero hacer X")
   - Análisis básico de migración N8N
✅ Role-based security (3 roles: CEO, Manager, Technical)
✅ Auth: Phone number → user mapping
✅ Dashboard chat (embedded en War Room)

### No incluye (Phase 2+)

❌ Migraciones completas desde N8N (solo análisis básico en MVP)
❌ Zapier/Make specialist agents (Phase 2+)
❌ Email gateway (Phase 2+)
❌ Telegram (Phase 2+)
❌ SMS alerts (Phase 2+)

## Input/Output Examples

### Ejemplo 1: Reporte financiero

```
Input (WhatsApp):
"Envíame reporte de gastos del mes"

Output (WhatsApp):
"📊 Reporte de Gastos — Abril 2026

Total: $15,430
├── Marketing: $5,200 (33.7%)
├── Infraestructura: $4,100 (26.6%)
├── Salarios: $4,500 (29.2%)
└── Otros: $1,630 (10.5%)

📈 vs mes anterior: +8.2%
⚠️ Alerta: Marketing está 15% sobre presupuesto

[Ver dashboard completo → link]"
```

### Ejemplo 2: Migración N8N

```
Input (WhatsApp):
[Archivo JSON exportado de N8N]

Output (WhatsApp):
"🔍 Análisis de Flujo N8N

He detectado 3 nodos principales:
1. Webhook (trigger) → Agent: webhook-receiver
2. HTTP Request → Agent: api-client
3. Code (JavaScript) → Agent: script-executor

Recomendación:
├── Crear 3 agentes especializados
├── Conectar en DAG: webhook → api-client → script-executor
└── ¿Querés que los cree ahora? (responde 'sí' para ejecutar)

[Ver diagrama → link]"
```

### Ejemplo 3: Planning

```
Input (WhatsApp):
"Quiero automatizar facturación electrónica"

Output (WhatsApp):
"🎯 Plan de Automatización — Facturación Electrónica

Para esto necesito crear 3 agentes:

1. **invoice-generator**
   └── Genera facturas en formato AFIP

2. **email-sender**
   └── Envía facturas a clientes por email

3. **webhook-receiver**
   └── Recibe notificaciones de pago

Conexión:
webhook-receiver → invoice-generator → email-sender

¿Querés que los cree ahora? (responde 'sí' para ejecutar)

[Ver documentación → link]"
```

## Open Questions

1. **WhatsApp Business API provider:** Twilio? Meta directamente? Otro?
2. **Rate limiting:** ¿Cuántos mensajes por minuto/hora?
3. **Cost structure:** WhatsApp Business API tiene costo por mensaje
4. **File upload limits:** JSON de N8N puede ser grande — ¿Cómo manejar?
5. **Error handling:** ¿Qué pasa si el usuario envía algo que el agente no entiende?

## Success Metrics

### Phase 1 (v3.0)

| Métrica | Target | ¿Cómo medir? |
|---------|--------|--------------|
| **Adopción** | 60%+ usuarios registran phone number | DB query |
| **Uso semanal** | 3+ mensajes/semana activo | Message logs |
| **Response time** | P90 < 10 segundos | Timestamps |
| **Satisfacción** | 4.0+/5.0 | Post-interaction survey |
| **Error rate** | <5% mensajes fallidos | Error logs |

### Phase 2+ (v3.1+)

| Métrica | Target | ¿Cómo medir? |
|---------|--------|--------------|
| **Migraciones completadas** | 10+ flujos N8N migrados | Migration logs |
| **N8N specialist agents creados** | 5+ agentes especializados | Agent registry |
| **Time to migrate** | <1 hora por flujo (vs weeks manual) | Timestamps |

## Dependencies

| Dependencia | Estado | Nota |
|-------------|--------|------|
| Rust Control Plane | ⏸️ Phase 15 | Orquestador corre en Rust |
| PostgreSQL | ⏸️ Phase 15 | Para persistencia de mensajes |
| WhatsApp Business API | ❌ No iniciado | Requiere setup |
| N8N specialist agents | ❌ No iniciado | Phase 2+ |

## Technical Considerations

### WhatsApp Business API

```
Provider options:
1. Twilio — Más fácil, pero más caro
2. Meta direct — Más barato, pero más complejo
3. Otros (MessageBird, etc.)

Recomendación: Empezar con Twilio (velocidad), migrar a Meta direct en scale.
```

### Async Message Queue

```
WhatsApp → API Gateway → Queue (Redis/RabbitMQ) → Orquestador
                                   ↓
                              Response Queue → WhatsApp
```

### Phone Number Verification

```
1. Usuario ingresa phone number en perfil
2. Sistema envía código de verificación vía SMS/WhatsApp
3. Usuario ingresa código
4. Phone number verificado y mapeado a user_id
```

---

**Propuesta creada:** 2026-04-06
**Creado por:** Rafael Padrón (via /mm:propose)
**Estado:** UNDER_REVIEW — Brain #1 evaluó, awaitingBrains #2-#7
**Replaces:** PROP-002 (diferido por solution-talk)

---

## Evaluación Brain #1 (Product Strategy)

### ✅ Lo Bueno

1. **Mejor evidencia que PROP-002** — 3 casos específicos con contexto (mejor granularidad que "quiero consultar al CEO")
2. **Migration Analysis es un chat-only superpower REAL** — Compartir JSON de N8N + síntesis experta NO lo puede hacer Command+K
3. **Diferenciación vs Paperclip clara** — Paperclip solo tiene inbox/tickets, MasterMind agrega multi-canal + 3 superpowers
4. **Alineado con Knowledge Distillation** — Chat como interfaz de síntesis cross-brain (si se implementa bien)

### ⚠️ Lo Que Falta

1. **Evidencia de frecuencia/severity** — ¿Cuántas veces pasa el Caso 1 (reporte urgente)? ¿1 vez/mes? ¿1 vez/semana? Sin FREQUENCY, no se puede priorizar vs otros features

2. **Claridad de Target Persona** — 3 casos = 3 personas POTENCIALMENTE diferentes:
   - Caso 1: ¿CEO? ¿Asistente? ¿CFO?
   - Caso 2: ¿DevOps? ¿Consultor? ¿Implementador?
   - Caso 3: ¿Manager? ¿Dev? ¿Architect?
   - **PROP-001 validó que target v3.0 es Manager NO técnico** — ¿Se alinean estos casos con esa persona?

3. **Validación LATAM** — No hubo entrevistas The Mom Test para validar que estos 3 casos son REALES para LATAM business users

4. **Business Case** — WhatsApp Business API tiene COSTO por mensaje:
   - ¿Quién paga? ¿User? ¿MasterMind absorbe?
   - Proposal NO menciona pricing model o cost structure
   - Sin esto, no se puede evaluar Viability Risk

5. **Secuencia con Phase 15** — Depende de Rust Control Plane que NO existe aún:
   - ¿Por qué no se siguió el patrón de PROP-001? (validación ANTES de código)
   - Si Phase 15 cambia de scope → WhatsApp integration puede romperse (sunk cost)

6. **Outcome vs Output** — Proposal lista features (Output), NO business impact (Outcome):
   - ¿Outcome es "reducir time-to-insight"? ¿"Aumentar confianza en decisiones"?
   - Sin Outcome claro, NO se puede medir éxito

### 🚨 Peligros

1. **Build Trap 2.0 Confirmado** — Output (WhatsApp chat) sin Outcome (business impact medido). Exactamente el mismo error que PROP-002, pero con mejor empaquetado.

2. **Value Risk:** Baja frecuencia de uso para Effort L (Large)
   - Caso 1 (Executive Reports): Frecuencia ? (si es baja → ROI bajo)
   - Caso 2 (Migration): One-time use durante onboarding → ¿Vale la pena feature completo?
   - Caso 3 (Planning): ¿Cuántas veces un Manager NO técnico crea workflows?
   - **Si ninguno es HIGH FREQUENCY, ROI de WhatsApp integration es BAJO**

3. **"Chat-Only Superpowers" sobre-exagerados**
   - Caso 1: Es **MOBILE-only**, no chat-only (email alerts también sirven)
   - Caso 2: ✅ Verdaderamente chat-only (migration analysis requiere input complejo)
   - Caso 3: Borderline — docs/templates pueden resolverlo
   - **Solo 1 de 3 es realmente chat-only**

4. **Viability Risk: Scope Explosion**
   - 3 casos = 3 implementaciones diferentes
   - WhatsApp API + RBAC + Async Queue + Phone Verification
   - **Effort L parece SUB-estimado**

5. **Alternativas NO evaluadas**
   - Command+K mejorado (costo bajo, valor alto para devs)
   - Email alerts para reportes urgentes (costo muy bajo, valor medium)
   - Migration CLI tool standalone (costo medio, valor high)
   - **¿Por qué no probar alternativas ANTES de WhatsApp?**

6. **No se aprendió de PROP-002** — Concierge MVP fue DEFERRED en PROP-002, pero PROP-002-v2 NO menciona concierge test. Saltó directo de learning a build.

### 💭 Sugerencias

**Sugerencia #1: Separar los 3 casos en 3 propuestas independientes**

```
PROP-002-A: Executive Reports (WhatsApp/Email)
PROP-002-B: Migration Analysis (N8N → Agents)
PROP-002-C: Assisted Planning ("Quiero hacer X")
```

**Por qué:** Cada caso tiene diferente target, frecuencia y complejidad. Juntos = scope explosion.

**Sugerencia #2: Concierge MVP ANTES de código (OBLIGATORIO)**

**Phase 0 (1 semana):**
- Crear canal Slack/Discord `#orchestrator-chat-beta`
- Usuarios pueden enviar: (a) pedidos de reporte, (b) JSONs de N8N, (c) "quiero automatizar X"
- Responder MANUALMENTE usando Command Center + Command+K
- Medir: Frecuencia, Tipo de requests, TTV vs dashboard

**Métricas de Go/No-Go:**
- **SLI-1:** ≥10 requests/semana de ALGUNO de los 3 casos
- **SLI-2:** ≥60% de requests son de UN SOLO caso (priorizar ese)
- **OKR-1 (40% PMF Test):** "¿Qué tan decepcionado estarías si elimináramos este canal?"

**Sugerencia #3: Priorizar Caso 2 (Migration Analysis) PRIMERO**

**Por qué:**
- Es el único chat-only superpower REAL
- Alta intención durante onboarding (users traen flujos de N8N)
- Value prop claro: "weeks de análisis → minutes"

**Implementation:**
- **Phase 1:** CLI tool standalone (sin WhatsApp)
- **Phase 2:** Integrar en War Room (dashboard chat)
- **Phase 3:** WhatsApp integration (SOLO si Phase 1/2 validan demanda)

**Sugerencia #4: Executive Reports → Email alerts PRIMERO**

**Por qué:**
- Email es asíncrono, mobile-friendly, MÁS BARATO que WhatsApp
- Validar si "urgencia" es REAL o perceived
- Si email alerts no se usan → WhatsApp TAMPOCO se usará

**Sugerencia #5: Definir Target Persona CLARAMENTE**

**Preguntas para resolver:**
- ¿Manager NO técnico (PROP-001) es el target de los 3 casos?
- ¿O son 3 targets diferentes?
- **Si es Manager NO técnico:** Caso 2 (Migration N8N) probablemente NO aplica (no usa N8N)

**Sugerencia #6: Definir Business Case (WhatsApp API costs)**

**Research requerido:**
- WhatsApp Business API pricing (Twilio vs Meta direct)
- Costo por mensaje × frecuencia esperada = Monthly operational cost
- ¿Pricing puede absorberlo? ¿O se cobra premium?

**Sugerencia #7: Secuencia correcta con Phase 15**

```
Phase 14.5: Concierge MVP (1 semana)
Phase 15: Rust Control Plane (3-4 semanas)
Phase 15.5: Migration Analysis CLI (2 semanas)
Phase 16: Executive Reports Email (1 semana)
Phase 17: WhatsApp integration (SOLO si 14.5/15.5/16 validan)
```

**Por qué:** No construir WhatsApp ANTES de (a) validar demanda, (b) tener backend estable.

### 📋 Veredict Brain #1

**ESTADO:** **CONDITIONAL_APPROVAL** 🔶

**Confianza:** 70%

**Rationale:** PROP-002-v2 es MEJOR que PROP-002 (más específico), pero aún tiene **Build Trap 2.0 risk**. Los 3 casos tienen diferente target, frecuencia y complejidad — juntos causan scope explosion. Solo Caso 2 (Migration Analysis) es un chat-only superpower REAL.

**Condiciones CRÍTICAS para APPROVAL:**

1. **[BLOCKER] Concierge MVP (1 semana) ANTES de cualquier código**
   - Canal Slack/Discord para recibir requests de los 3 casos
   - Medir frecuencia, tipo, TTV vs dashboard
   - ≥10 requests/semana + ≥40% "muy decepcionado" = Go

2. **[BLOCKER] Separar en 3 propuestas independientes**
   - PROP-002-A (Executive Reports)
   - PROP-002-B (Migration Analysis) ← PRIORIDAD
   - PROP-002-C (Assisted Planning)

3. **[BLOCKER] Definir Target Persona CLARAMENTE**
   - ¿Manager NO técnico (PROP-001) es el target?
   - Si SÍ → Caso 2 (N8N) probablemente NO aplica
   - 3 entrevistas The Mom Test con LATAM users

4. **[CONDITION] Business Case para WhatsApp API**
   - Research pricing (Twilio/Meta direct)
   - Cost structure vs pricing model
   - Si no es viable → Email alerts como alternativa

5. **[CONDITION] Secuencia con Phase 15**
   - NO construir WhatsApp ANTES de Rust Control Plane
   - Migration Analysis CLI standalone PRIMERO (sin WhatsApp)
   - Email alerts para Executive Reports PRIMERO

**Si NO se cumplen condiciones:** REJECTED → Ahorrar semanas de desarrollo que no generan valor.

**Recomendación de prioridad (si pasan condiciones):**
1. **Phase 1:** PROP-002-B (Migration Analysis) — CLI standalone
2. **Phase 2:** PROP-002-A (Executive Reports) — Email alerts
3. **Phase 3:** PROP-002-C (Assisted Planning) — Templates
4. **Phase 4:** WhatsApp integration — SOLO si Phase 1-3 validan demanda alta

---

## Evaluación Brain #2 (UX Research)

### ✅ Lo Bueno

1. **Jakob's Law aplicado correctamente** — WhatsApp tiene ~2B usuarios globales. En LATAM es EL canal de comunicación móvil. Curva de aprendizaje = CERO.
2. **Gulf of Evaluation reducido (en teoría)** — "¿Qué está pasando?" → respuesta en lenguaje natural PUEDE ser más rápido que escanear 4 pantallas
3. **Mobile-first alignment con LATAM** — WhatsApp Business = asíncrono, no requiere estar frente al PC
4. **Role-based filtering como affordance** — Comunica permiso sin romper el modelo mental
5. **3 superpoderes claros** — Executive Reports, Migration Analysis, Assisted Planning son tareas específicas donde chat TIENE ventaja

### ⚠️ Lo Que Falta

1. **Modelo mental del Orquestador NO definido** — ¿Es pasivo? ¿Tiene iniciativa? ¿Tiene personalidad?
2. **Expectation management INEXISTENTE** — Necesita first-run message con capacidades y límites
3. **Descubribilidad = CERO** — ¿Cómo sé que EXISTE el chat de WhatsApp? QR code? Email?
4. **Manejo de ambigüedad NO especificado** — "Dame el reporte" → ¿Cuál reporte?
5. **Validación LATAM — CRITICAL GAP** — The Mom Test es OBLIGATORIO antes de aprobar
6. **Integración con Command+K NO especificada** — ¿Compite? ¿Se integra?
7. **Error handling en lenguaje natural** — ¿Qué pasa si WhatsApp API falla?

### 🚨 Peligros

1. **Adopción CERO por falta de descubribilidad** — Si nadie sabe que puede chatear, nadie lo usa
2. **Frustración por "AI que no entiende"** — Promesa de "natural language" vs realidad de "commands disfrazados"
3. **Role-based fragmentation** — Mismo query, respuestas diferentes → confusión
4. **Miller's Law violado** — 20 líneas de texto → usuario escanea, NO lee
5. **Duplicación con LiveRunWidget (Paperclip)** — Paperclip YA tiene streaming transcript
6. **WhatsApp Business API limitations** — No soporta streaming, rate limits estrictos
7. **Sunk Cost Fallacy sin validación** — Concierge MVP ANTES de código

### 💭 Sugerencias

1. **Definir personalidad del Orquestador** — "MasterMind Assistant" (NO "CEO Chat")
2. **Expectation management EXPLÍCITO** — First-run message con capacidades y límites
3. **Integrar con Command Palette (Cmd+K)** — Dashboard chat = Cmd+K modo conversacional
4. **Clarification questions obligatorias** — "¿Cuál reporte? [Sistema] [Outcome] [Templates]"
5. **3 superpoderes deben ser ÚNICOS del chat** — Prototipar sin código, medir TTV chat vs dashboard
6. **Estrategia de descubribilidad** — QR code en dashboard, email onboarding
7. **The Mom Test — 3 entrevistas LATAM** — CTO, Tech Lead, Developer senior
8. **Paper prototype validation** — 5 usuarios, >80% tasks completion
9. **Error handling en tiempo real** — "Estoy procesando...", "Hubo un error..."
10. **Concierge MVP ANTES de código** — 1 semana Slack/Discord manual

### 📋 Veredicto Brain #2

**ESTADO:** **CONDITIONAL_APPROVAL** 🔶

**Confianza:** 60%

**Rationale:** La propuesta v2 tiene fortalezas UX reales (Jakob's Law + WhatsApp mobile-first) pero gaps críticos de validación: target user mal definido, sin validación LATAM, descubribilidad = 0, ambigüedad no manejada.

**Condiciones para APPROVAL:**
- Concierge MVP FIRST
- Definir personalidad (Voice + Tone doc)
- 3+ chat-only superpowers con TTV validation
- Validar con 3 LATAM users
- Paper prototype validation
- Integrar con Cmd+K
- Especificar manejo de ambigüedad
- Estrategia de descubribilidad
- Error handling especificado

---

## Evaluación Brain #4 (Frontend Architecture)

### ✅ Lo Bueno

1. **Infraestructura WebSocket ya existe** — `wsStore.ts` maneja reconexión con exponential backoff
2. **React Query disponible para polling fallback** — Patrón ya usado en ExecutionDetail
3. **Zustand 5 como state manager global** — Chat history puede vivir en store dedicado
4. **Tailwind 4 + shadcn/ui = componentes reutilizables** — Input fields ya existen
5. **React 19 + Server Components = carga inicial rápida**

### ⚠️ Lo Que Falta

1. **Arquitectura de chat no especificada** — ¿Chat embebido en Command Center? ¿Nueva ruta `/chat`?
2. **Estrategia de mensajería real-time no definida** — WebSocket? SSE? Polling?
3. **File upload UX para N8N JSON no especificado** — ¿Drag-drop? ¿Progress bar? ¿Límite de tamaño?
4. **Role-based filtering: Frontend vs Backend** — ¿Quién filtra? ¿Frontend (UX) o Backend (security)?
5. **State management para chat history** — ¿Cuántos mensajes mantener? ¿Paginación?
6. **Integración con WhatsApp Business API** — ¿Es integración real? ¿O solo mención?

### 🚨 Peligros

1. **🚨 CRITICAL: WebSocket scalability no considerado** — 1 WS por tarea vs 1 WS global con multiplexing
2. **🚨 CRITICAL: N8N JSON parsing puede bloquear UI** — Web Worker requerido para archivos grandes
3. **Memory leak por chat history sin límite** — 1000 mensajes = 2MB en Zustand store
4. **Role-based filtering solo en frontend = SECURITY BUG** — Backend SIEMPRE debe filtrar
5. **Duplicación de código con 4 pantallas existentes** — Extender BriefInputModal vs crear nuevo
6. **Performance: Markdown rendering en cada mensaje** — `react-markdown` es lento

### 💭 Sugerencias

1. **Arquitectura de componentes recomendada:**
   ```
   chat/
   ├── ChatContainer.tsx        # WS connection
   ├── ChatMessageList.tsx      # react-virtuoso
   ├── ChatMessage.tsx          # Individual message
   ├── ChatInput.tsx            # Extend BriefInputModal
   ├── ChatTypingIndicator.tsx
   └── FileUpload.tsx           # N8N JSON
   ```

2. **Schema de Zustand store:**
   - Max 50 mensajes en memoria
   - Paginación para history antiguo
   - Persistencia opcional en localStorage

3. **WebSocket event protocol:**
   ```
   Client → Server: { type: 'chat:message', data: { content, taskId } }
   Server → Client: { type: 'chat:message', data: { id, role, content } }
   ```

4. **File upload con Web Worker** — Parsing en background para no bloquear UI

5. **Role-based filtering architecture:**
   - Backend: Filtrar datos por role (security)
   - Frontend: Ocultar UI elements por role (UX)

6. **Ubicación recomendada:** Nueva ruta `/war-room` con chat dockable a la derecha

### 📋 Veredicto Brain #4

**ESTADO:** **CONDITIONAL_APPROVAL** 🔶

**Confianza:** 70%

**Rationale:** POTENCIAL técnico válido, pero propuesta incompleta desde Frontend Architecture. Infraestructura WS existe, PERO falta: arquitectura de chat, file upload strategy, role-based responsibilities, WebSocket scalability.

**Condiciones para APPROVAL:**
1. Especificar ubicación del chat (wireframe de navegación)
2. Definir protocolo de mensajería WS + fallback
3. Strategy para N8N JSON (Web Worker, validation)
4. Clarificar frontend vs backend responsibilities
5. Diseñar chatStore schema
6. Extender componentes existentes (BriefInputModal)

---

## Evaluación Brain #5 (Backend Architecture)

### ✅ Lo Bueno

1. **Arquitectura de mensajes asíncrona bien pensada** — Queue desacopla webhook de procesamiento
2. **Role-based response filtering es CRÍTICO y bien definido** — Security principle of least privilege
3. **Phone number auth es simple y efectivo para MVP** — 2FA implícito
4. **Caso de uso de migración N8N es REAL y valioso** — N8N exporta JSON parsable
5. **Dashboard chat como fallback está bien diseñado**

### ⚠️ Lo Que Falta

1. **❌ Estrategia de rate limiting para WhatsApp Business API** — Límites estrictos (1,000-100,000 msgs/día)
2. **❌ Estrategia de manejo de archivos grandes** — N8N JSON puede ser 500KB+
3. **❌ Estrategia de error handling y retry logic** — WhatsApp downtime, phone invalid, message rejected
4. **❌ Estrategia de monitoreo de costos** — WhatsApp API NO es gratis (~USD 0.01-0.05/msg)
5. **❌ Estrategia de cleanup de mensajes antiguos** — 1M mensajes = ~1GB

### 🚨 Peligros

1. **🚨 HIGH: Queue buildup sin monitoreo** — Orquestador cae 2h → 10K msgs → 5h backlog
2. **🚨 HIGH: Phone number spoofing** — Atacante falsifica CEO → pide transferir fondos
3. **🚨 MEDIUM: WhatsApp API downtime sin fallback** — Meta outage → todos los msgs fallan
4. **🚨 MEDIUM: N8N JSON parsing puede fallar** — DoS por JSON malformado
5. **🚨 LOW: Costos no controlados** — Usuario spamma 1,000 msgs → factura USD 50

### 💭 Sugerencias

1. **Usar Redis (no RabbitMQ) para la queue** — Más simple, más rápido, ya lo conocés
2. **Twilio (no Meta direct) para MVP** — Setup en 1h vs 1 semana, migra fácil
3. **PostgreSQL BYTEA (no S3) para MVP** — Más simple, suficiente para 10MB
4. **Implementar observabilidad desde día 1** — OpenTelemetry metrics
5. **Feature flags para rollout gradual** — 10% usuarios antes de 100%

### 📋 Veredicto Brain #5

**ESTADO:** **CONDITIONAL_APPROVAL** 🔶

**Confianza:** 72%

**Rationale:** SOLID foundation técnico (async queue, role-based filtering), PERO faltan detalles críticos de operación (rate limiting, cost tracking, retry).

**Condiciones MUST (bloqueantes):**
- Rate limiting con Redis (token bucket)
- Retry logic con exponential backoff + DLQ
- Cost tracking por usuario + alertas
- Circuit breaker para WhatsApp downtime
- Safe JSON parsing (size/depth limits)

**Condiciones SHOULD:**
- Redis (no RabbitMQ) para queue
- Twilio (no Meta direct) para MVP
- PostgreSQL BYTEA (no S3) para N8N
- Observabilidad (OpenTelemetry)
- Feature flags para rollout

---


---

## Evaluación Brain #7 (Growth/Data) — Meta-evaluación FINAL

### Síntesis de Conflictos

**¿Por qué coinciden los 4 cerebros?**
- Todos detectan el MISMO patrón: v2 trae casos concretos PERO el problema de validación persiste
- Los 3 casos sufren de **frequency problem**:
  - Caso 1 (Executive Reports): 1x/mes — demasiado bajo para justificar infraestructura
  - Caso 2 (Migration Analysis): one-time — infraestructura permanente para uso único
  - Caso 3 (Assisted Planning): frecuencia desconocida — dangerous assumption
- Ningún caso valida DEMANDA real, solo plantea "podría ser útil" sin evidencia

### Winner Selection

**Brain #1 (Product Strategy) tiene la posición más fuerte (70% confidence)**

**¿Por qué?**
- Ataca el **ROOT CAUSE**: Build Trap 2.0 — construir solución antes de validar problema
- Su roadmap de fases es **PRAGMÁTICO**: valida incrementalmente sin construir infraestructura completa
- Los otros cerebros resuelven síntomas, PERO #1 dice "primero valida que alguien quiera esto"

### Final Veredict

## 🔶 **CONDITIONAL_APPROVAL — 65% confidence**

**Razones:**
- ✅ v2 está MEJOR que v1 (casos concretos vs vaguedad)
- ❌ Todavía falta el paso CRÍTICO: validar que alguien NECESITE esto
- ❌ Frequency problem en los 3 casos hace que WhatsApp no tenga ROI

**Es todavía solution-talk?**
- **SÍ** porque asume demanda sin evidencia
- **NO** porque ahora tenemos casos concretos
- **FALTA**: "hablamos con usuarios LATAM y confirmaron que les duele esto"

### Integration Recommendation

**PASO 1: Separar en 3 propuestas INDEPENDIENTES**
```
PROP-002-A: Executive Reports por WhatsApp
PROP-002-B: Migration Analysis Chat ← PRIORIDAD
PROP-002-C: Assisted Planning
```

**PASO 2: Priorizar PROP-002-B (Migration Analysis)**
- Único "chat-only superpower" que Command+K NO puede hacer
- Valor REAL: análisis complejo de migración

**PASO 3: Concierge MVP ANTES de construir**
1. NO implementes WhatsApp todavía
2. Haz Migration Analysis manual con 3-5 clientes LATAM
3. Mide: ¿lo usaron? ¿cuánto tiempo? ¿pagarían?
4. Si validan → recién AHORA evalúa Phase 1 (CLI)

**PASO 4: WhatsApp = Phase 4 (no Phase 1)**
- Solo después de CLI + Email + Templates validen demanda
- WhatsApp es **CHERRY on top**, no foundation

### ROI Analysis — Why WhatsApp doesn't make sense YET

| Caso | Frecuencia | Infra cost | Usage/year | ROI |
|------|-----------|-----------|-----------|-----|
| Executive Reports | 1x/mes | Alto | 12 | ❌ NEGATIVE |
| Migration Analysis | One-time | Alto | 1/cliente | ❌ NEGATIVE |
| Assisted Planning | ¿? | Alto | ¿? | ❌ UNKNOWN |

**Conclusión:** Ningún caso justifica SOLO la inversión en WhatsApp. Migration Analysis tiene el mejor potencial PERO necesita validar primero.

---

## Estado Final de PROP-002-v2

**Status:** 🔶 **CONDITIONAL_APPROVAL** — 65% confidence

**Consensus:** Los 5 cerebros coinciden en que la propuesta tiene potencial técnico PERO requiere validación ANTES de construir.

**Próximos pasos:**
1. ✅ Archivar PROP-002-v2 como "learning experience"
2. ✅ Crear PROP-002-B: "Migration Analysis Chat — Concierge MVP"
3. ✅ Ejecutar Concierge Phase: 3-5 clientes manuales
4. ✅ Si valida → seguir roadmap de Brain #1
5. ✅ Si NO valida → pivotar sin gastar recursos

**Última actualización:** 2026-04-06
**Evaluación completa:** 5/5 brains (#1, #2, #4, #5, #7)
