# MasterMind v3.0 — PRP: Plataforma de Orquestación de Agentes con Knowledge Distillation

> **Condensado de:** Panorama Competitivo LATAM + Análisis Paperclip (7 brains) + PRP AAF v2.0 + Infraestructura MasterMind existente
> **Fecha:** 2026-04-04 (actualizado con fork strategy + backend split)
> **Veredicto Brain #7:** COMPLEMENTARIO — MasterMind = orquestación + expertise, Paperclip = solo orquestación
> **Decisión clave:** Fork Paperclip UI + Backend split Rust(65%)/Python(35%)

---

## 1. Visión

**MasterMind evoluciona de "framework de consulta de cerebros" a "plataforma de orquestación de agentes empresariales con conocimiento destilado de expertos mundiales."**

### Propuesta de Valor

```
Paperclip orquesta agentes        → "Cómo ejecutar agentes"
MasterMind orquesta + enseña      → "Qué deben saber los agentes"
```

**Diferenciador competitivo:** Ningún competidor en LATAM tiene **knowledge distillation** de expertos mundiales (Cagan, Torres, Norman, Abramov, etc.) embebido en sus agentes. Este es el moat.

### Target Persona

**Primario:** Pymes LATAM que necesitan automatizar procesos con IA pero no saben por dónde empezar
**Secundario:** Agencias digitales que ofrecen servicios de automatización
**Casos de uso estrella:** Atención multicanal (WhatsApp + IG + email), diagnóstico de procesos, desarrollo de software asistido por agentes

### Posicionamiento

"La plataforma de agentes empresariales que PIENSA como un experto, no solo ejecuta como un bot."

---

## 2. Stack Tecnológico — Fork + Split + Evolución

### Estrategia: COPY Paperclip UI + BUILD Rust/Python Backend

```
Paperclip UI (FORK/COPY)     → Frontend React 19 + Tailwind 4 + shadcn/ui
Rust Backend (BUILD) 65%     → Control Plane + Real-time Hub + Adapter Registry
Python Backend (EXISTENTE) 35% → 7 Brain Agents + Knowledge Distillation + AI
gRPC + Protobuf (CONECTAR)   → Type sync entre los 3 lenguajes
```

### ✅ FORK de Paperclip UI (copiar y rebrandear)

| Componente | Fuente | Motivo |
|-----------|--------|--------|
| **Layout.tsx** | Paperclip `ui/src/components/` | Three-column responsive con CompanyRail |
| **ActiveAgentsPanel.tsx** | Paperclip | Real-time agent monitoring con ping animation |
| **AgentConfigForm.tsx** | Paperclip | Progressive form con dirty tracking (simplificar) |
| **BillerSpendCard.tsx** | Paperclip | Cost tracking con QuotaBar |
| **KanbanBoard.tsx** | Paperclip | Drag-and-drop issue management (@dnd-kit) |
| **CommandPalette.tsx** | Paperclip | Cmd+K quick actions (Radix Command) |
| **CompanyRail.tsx** | Paperclip | Multi-tenant sidebar switcher |
| **OnboardingWizard.tsx** | Paperclip | Progressive setup flow |
| **OrgChart.tsx** | Paperclip | SVG org visualization |
| **RunTranscript** | Paperclip | Multi-density transcript streaming |
| **Sidebar.tsx** | Paperclip | Hierarchical navigation con live indicators |
| **DesignGuide.tsx** | Paperclip | Design system reference |

**Rebrand a MasterMind:** Colores, logos, brain agent knowledge display, LATAM focus.
**Ver auditoría completa:** `docs/nuevo giro/PAPERCLIP-UX-AUDIT.md`

### ✅ MANTENER (ya construido en MasterMind)

| Componente | Estado | Ubicación |
|-----------|--------|-----------|
| **FastAPI Backend** | ✅ Producción | apps/api/ |
| **Next.js 16 Frontend** | ✅ 4 pantallas | apps/web/ |
| **7 Brain Agents** | ✅ Con memoria | .claude/agents/mm/ |
| **brain_router.py** | ✅ 23 tests | orchestrator/ |
| **task_runner.py** | ✅ Background tasks | api/services/ |
| **brain_memory.py CLI** | ✅ Query/Log | tools/ |
| **experience_records** | ✅ SQLite | mastermind.db |
| **WebSocket Infrastructure** | ✅ Zustand + RAF batching | apps/web/src/ |
| **JWT Auth** | ✅ Con refresh rotation | apps/api/ |
| **Docker Compose** | ✅ api:8001 + web:3000 | docker-compose.yml |
| **CI/CD** | ✅ 3-tier pipeline | .github/ |

### 🔀 Backend Split — Rust (65%) + Python (35%)

**RUST — Performance-critical, state management, infrastructure:**

| Módulo | Función |
|--------|---------|
| Auth + JWT + RBAC | Seguridad, access control |
| WebSocket Real-time Hub | Miles conexiones concurrentes |
| Execution Engine | State management, process spawning |
| Budget + Cost Tracking | Cálculos financieros tiempo real |
| Adapter Registry | Multi-channel routing (WhatsApp, IG, email) |
| Scheduler / Cron | Timing precision |
| Plugin Loader | Process isolation |
| PostgreSQL + pgvector | Via SQLx |

**PYTHON — AI/ML, knowledge processing:**

| Módulo | Función |
|--------|---------|
| 7 Brain Agents + Memory | LangChain, NotebookLM, experience logging |
| Knowledge Distillation Engine | Autoaprendizaje, delta-velocity tracking |
| Feedback Analysis | Procesamiento de conocimiento, anti-patterns |
| Skills Registry | Gestión de conocimiento por dominio |
| Routines / Workflows | Automatización AI |
| Document Manager | Procesamiento de contenido |

### 🔄 RESTRUCTURAR (evaluado módulo por módulo)

| Componente Paperclip | Destino | Motivo |
|---------------------|---------|--------|
| **heartbeat.ts** (140K) | → Rust | Core execution engine, real-time performance |
| **workspace-runtime.ts** (76K) | → Rust | Process lifecycle, port management |
| **agents.ts** (routes 84K + services 24K) | → Rust | Agent state management, auth |
| **access.ts** (routes 96K) | → Rust | Security-critical access control |
| **live-events.ts** + **realtime/** | → Rust | WebSocket hub, thousands concurrent connections |
| **budgets.ts** + **costs.ts** | → Rust | Real-time financial calculations |
| **cron.ts** (12K) | → Rust | Timing precision, scheduler |
| **execution-workspaces.ts** (28K) | → Rust | Process spawning, state management |
| **adapter-utils/** | → Rust | Multi-provider adapter traits |
| **company-skills.ts** (84K) | → Python | AI/ML skill management |
| **feedback.ts** (72K) | → Python | Knowledge processing, AI training data |
| **issues.ts** (routes 68K + services 76K) | → Python | AI task management |
| **routines.ts** (54K) | → Python | AI workflow automation |
| **documents.ts** (20K) | → Python | Knowledge document management |
| **company-portability.ts** (168K) | → Python | Data transformation, export/import |

### Backend Split — Rust 65% / Python 35%

**RUST (performance-critical, state management, infrastructure):**
- Auth + JWT + RBAC → Seguridad y performance
- WebSocket Real-time Hub → Miles de conexiones concurrentes
- Execution Engine → State management, process spawning
- Budget + Cost Tracking → Cálculos financieros tiempo real
- Adapter Registry → Multi-channel routing
- Scheduler / Cron → Timing precision
- Plugin Loader → Process isolation
- PostgreSQL + pgvector via SQLx

**PYTHON (AI/ML, data processing, knowledge):**
- 7 Brain Agents + Memory → LangChain, NotebookLM, knowledge distillation
- Knowledge Distillation Engine → Autoaprendizaje
- Feedback Analysis → Procesamiento de conocimiento
- Skills Registry → Gestión de conocimiento por dominio
- Routines / Workflows → Automatización AI
- Document Manager → Procesamiento de contenido

### 🆕 CREAR

| Componente | Tecnología | Motivo |
|-----------|-----------|--------|
| **Control Plane** | **Rust (Axum + Tokio)** | Orquestador misión crítica, WebSockets, sandboxing |
| **Adapter Registry** | **Rust** | Multi-provider (WhatsApp, Instagram, Odoo, etc.) |
| **Event Store** | **PostgreSQL** + Rust | Audit trail + analytics + learning |
| **Orchestration Canvas** | React Flow v12 (ya instalado) | Visual DAG de agentes |
| **Multi-channel Gateway** | **Rust (Axum)** + webhooks | WhatsApp Business API, Instagram, email |
| **Cost Tracking** | **Rust** + dashboard | Tokens/costos por agente |
| **Template Marketplace** | **Rust API** + UI | Plantillas de "compañías" predefinidas |
| **gRPC + Protobuf** | Rust + Python + TypeScript | Type sync entre los 3 lenguajes |

### 🏗️ Arquitectura de 3 Servicios

| Servicio | Tecnología | Responsabilidad |
|----------|-----------|-----------------|
| **Control Plane** | **Rust** (Axum + Tokio) | Empresas, proyectos, DB, dashboard, org chart, auth |
| **Agent Runtime** | **Python** (FastAPI existente) | IA, autoaprendizaje, LangChain, 7 brain agents, knowledge distillation |
| **Real-time Hub** | **Rust** (Tokio) | WebSockets, eventos, Run Transcript en vivo, broadcast |

### 🔗 Type Sync — El `@paperclipai/shared` Mejorado

```
Protobuf definitions (UNA vez)
    ↓ auto-genera
├── Rust types     (tonic + prost)
├── Python types   (betterproto)
└── TypeScript types (protoc-gen-es)
```

Un cambio en un campo → error en compilación en los 3 lenguajes. Fin de la inconsistencia.

---

## 3. Architecture — "El Cerebro de la Empresa"

```
┌─────────────────────────────────────────────────────────────┐
│                    MasterMind v3.0                            │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │   RUST CORE      │  │  PYTHON AI       │  │  NEXT.js    │ │
│  │   (Axum + Tokio) │  │  (FastAPI)       │  │  Frontend   │ │
│  │                  │  │                  │  │             │ │
│  │  ▸ Control Plane │  │  ▸ 7 Brains      │  │  ▸ Canvas   │ │
│  │  ▸ Real-time Hub │  │  ▸ Knowledge     │  │  ▸ Dashboard│ │
│  │  ▸ WebSockets    │  │  ▸ LangChain     │  │  ▸ ReactFlow│ │
│  │  ▸ Adapter Reg.  │  │  ▸ AutoGen       │  │  ▸ Monitor  │ │
│  │  ▸ Sandboxing    │  │  ▸ Auto-learn    │  │             │ │
│  └────────┬─────────┘  └────────┬─────────┘  └─────┬──────┘ │
│           │                     │                    │        │
│           └──────────┬──────────┘────────────────────┘        │
│                      │                                        │
│             ┌────────┴────────┐                               │
│             │ gRPC + Protobuf │ ← Type Sync (el shared)       │
│             └────────┬────────┘                               │
│                      │                                        │
│  ┌────────────┐  ┌───┴─────────┐  ┌──────────────┐          │
│  │ PostgreSQL │  │  Redis      │  │  Adapter     │          │
│  │ + pgvector │  │  Events Bus │  │  Registry    │          │
│  │ RLS multi- │  │             │  │  WhatsApp    │          │
│  │ tenant     │  │             │  │  Instagram   │          │
│  └────────────┘  └─────────────┘  │  Email       │          │
│                                    │  Odoo/Notion │          │
│                                    └──────────────┘          │
└─────────────────────────────────────────────────────────────┘
         │                    │
    ┌────┴────┐          ┌───┴────┐
    │ WhatsApp│          │ Odoo   │
    │ Insta   │          │ Notion │
    │ Email   │          │ Custom │
    └─────────┘          └────────┘
```

---

## 4. Fases de Implementación

### Fase 0 — Fork Paperclip UI (1-2 semanas)

**Objetivo:** Copiar frontend funcional de Paperclip y rebrand a MasterMind

**Tareas:**
1. **Fork `ui/` directory**
   - Copiar `/home/rpadron/proy/paperclip/ui/` → MasterMind monorepo
   - Eliminar dependencias Paperclip-specific (heartbeat references, codex panel)
   - Integrar con Next.js 16 existente en `apps/web/`

2. **Rebrand a MasterMind**
   - Colores: OKLCH + cyan (MasterMind) vs slate (Paperclip)
   - Logo + iconografía
   - Textos: inglés/español (LATAM focus)
   - Company Pattern Icons → Brain Agent icons (7 cerebros)

3. **Adaptar API calls**
   - Paperclip llama a `/api/*` → apuntar a nuestro Rust + Python backend
   - TanStack Query hooks → nuevos endpoints MasterMind
   - WebSocket connection → Rust Real-time Hub

4. **Testing de UI**
   - Verificar 10 patrones UX funcionan (ver PAPERCLIP-UX-AUDIT.md)
   - Responsive testing (mobile + desktop)
   - Accesibility basics

**Patrones copiados:** Layout, Sidebar, CompanyRail, AgentConfigForm, ActiveAgentsPanel, MetricCard, KanbanBoard, CommandPalette, LiveRunWidget, OnboardingWizard

### Fase 0 — Fork Paperclip UI (1-2 semanas)

**Objetivo:** Copiar frontend funcional de Paperclip, rebrand a MasterMind

**Tareas:**
1. **Fork UI completa**
   - Copiar `paperclip/ui/` → `apps/web-v3/`
   - React 19 + Tailwind 4 + shadcn/ui + Radix + TanStack Query 5
   - 41 páginas + 94 componentes = base sólida

2. **Rebrand MasterMind**
   - Colores → MasterMind palette
   - Logo → MasterMind branding
   - Agentes vacíos → Brain agents con knowledge indicators

3. **Adaptar routing**
   - Company prefix → Workspace prefix
   - Issues → Tasks (brain tasks)
   - Agents → Brain Agents

4. **Conectar APIs**
   - Reemplazar Paperclip API calls → Rust/Python endpoints
   - Protobuf types en vez de @paperclipai/shared

**Patrones UX copiados (ver PAPERCLIP-UX-AUDIT.md):**
Three-column layout, Real-time monitoring, Company-as-context, Agent config form, Cost dashboard, Kanban, Command palette, Run transcript, Onboarding wizard, Org chart

**Cerebros involucrados:**
- Brain #3 (UI Design): Design system rebrand
- Brain #4 (Frontend): Adaptar componentes + conectar APIs

### Fase 1 — Foundation Upgrade: Rust Control Plane (3-4 semanas)

**Objetivo:** Migrar SQLite → PostgreSQL + Rust Control Plane + gRPC type sync

**Tareas:**
1. **Rust Control Plane (Axum + Tokio)**
   - Bootstrapping del servicio Rust con Axum
   - Definir Protobuf contracts para Rust ↔ Python ↔ TypeScript
   - gRPC server (tonic) en Rust + gRPC client en Python (betterproto)
   - Migrar auth (JWT existente) → Rust middleware

2. **PostgreSQL migration**
   - Migrar mastermind.db → PostgreSQL
   - experience_records → Event Store
   - SQLx (Rust) + SQLAlchemy/Alembic (Python)
   - pgvector para embeddings futuros

3. **Adapter Pattern en Rust**
   - Copiar patrón de Paperclip (server/src/adapters/) pero en Rust
   - Trait: `BrainAdapter` con `execute()`, `query_knowledge()`, `log_experience()`
   - Registry dinámico de adapters (HashMap-based)
   - Integrar brain_router.py → Adapter Registry via gRPC

4. **Event Sourcing**
   - Tabla `activity_log` inmutable
   - Cada brain operation = evento
   - Consultas por brain_id, timestamp, type

**Cerebros involucrados:**
- Brain #5 (Backend): Diseñar schemas + migraciones + Protobuf contracts
- Brain #6 (QA): Tests de migración + rollback + gRPC integration tests

### Fase 2 — Orchestration Canvas + Rust Real-time Hub (2-3 semanas)

**Objetivo:** Dashboard visual de orquestación de agentes + Rust WebSocket hub

**Tareas:**
1. **Rust Real-time Hub (Tokio)**
   - WebSocket server con Tokio-tungstenite
   - Miles de conexiones concurrentes sin GC pauses
   - Eventos: brain_started, brain_completed, brain_routed, brain_failed
   - Redis pub/sub para cross-service broadcast

2. **React Flow Canvas** (ya instalado @xyflow/react v12)
   - Nodos = Brain agents con estado en tiempo real
   - Edges = Routing rules (brain-to-brain communication)
   - Animaciones de flujo (inspirado en n8n)
   - Tipos TypeScript auto-generados desde Protobuf

3. **Real-time updates**
   - Zustand + RAF batching (ya funciona)
   - Consumir eventos desde Rust WebSocket hub
   - Ping animation para brains activos (copiar ActiveAgentsPanel de Paperclip)

3. **Cost Dashboard**
   - MetricCard por brain (tokens, costos, duración)
   - Timeline de actividad (ActivityRow pattern de Paperclip)
   - Budget enforcement por sesión

**Cerebros involucrados:**
- Brain #3 (UI Design): Design system OKLCH + zero-radius
- Brain #4 (Frontend): React Flow + code splitting + TanStack Query
- Brain #2 (UX Research): Flujos de usuario del canvas

### Fase 3 — Multi-Channel Gateway (3-4 semanas)

**Objetivo:** Conectar WhatsApp + Instagram + email al orquestador Rust

**Tareas:**
1. **WhatsApp Business API**
   - Webhook receiver en Rust (Axum)
   - Adapter para mensajería bidireccional
   - Cola de mensajes con Tokio channels (zero-copy)

2. **Instagram DM + Facebook Messenger**
   - Meta Graph API integration en Rust
   - Adapter trait para multi-canal
   - Personalización de tono por canal

3. **Email Gateway**
   - IMAP/SMTP integration en Rust (lettre + imap crates)
   - Adapter para parsing + routing
   - Templates de respuesta

4. **Unified Inbox**
   - Bandeja única para todos los canales
   - Contexto compartido entre canales
   - Escalamiento a humano cuando sea necesario

**Cerebros involucrados:**
- Brain #5 (Backend): Rust API design + webhooks + Adapter traits
- Brain #1 (Product): Validar casos de uso con clientes reales
- Brain #6 (QA): Testing multi-canal

### Fase 4 — Knowledge Distillation Engine (3-4 semanas)

**Objetivo:** Los cerebros aprenden de cada interacción y mejoran

**Tareas:**
1. **Experience Analytics**
   - Dashboard de patrones recurrentes
   - Insights por brain (qué funciona, qué no)
   - Correlation analysis entre brains

2. **Auto-learning loop**
   - Brain #7 evalúa outputs → feedback → ajuste
   - Human corrections → anti-patterns → brain memory
   - Delta-Velocity tracking (mejora vs baseline)

3. **Template Generation**
   - De interacciones exitosas → plantillas reusables
   - Brain #1 sugiere templates basados en patrones
   - Marketplace de templates por industria

**Cerebros involucrados:**
- Brain #7 (Growth): Diseñar métricas + loops
- Brain #1 (Product): Priorizar templates por valor de negocio
- Todos los brains: Contribuir knowledge a sus dominios

### Fase 5 — Template Marketplace + Enterprise (4-6 semanas)

**Objetivo:** Escalar a múltiples verticales con plantillas predefinidas

**Tareas:**
1. **Clipmart-style marketplace**
   - Plantillas de "compañías" por vertical
   - Software Dev Agency, Marketing Agency, Customer Support
   - Import/export de configuraciones

2. **Multi-tenant**
   - Aislamiento por company_id (Paperclip pattern)
   - RBAC por organización
   - Billing + usage tracking

3. **Enterprise integrations**
   - Odoo adapter
   - Notion adapter
   - Custom webhook adapter
   - API para integraciones propias

**Cerebros involucrados:**
- Brain #1 (Product): Go-to-market strategy
- Brain #7 (Growth): Pricing + funnels
- Brain #5 (Backend): Rust multi-tenant architecture + gRPC services
- Brain #6 (QA): Rust load testing + security audit

---

## 5. Cómo Participan los Cerebros en Desarrollo

### En Cada Fase

```
Fase N:
  1. Brain #1 evalúa el product value de la fase
  2. Brain #5 + #4 diseñan la arquitectura
  3. Brain #3 define el UI design system
  4. Brain #2 valida los flujos de usuario
  5. Brain #6 define testing strategy
  7. Brain #7 evalúa el output final → APPROVE/REJECT/ITERATE
```

### Conocimiento Nuevo Requerido

| Brain | Conocimiento Nuevo | Fuente |
|-------|-------------------|--------|
| **#1 Product** | Go-to-market LATAM, pricing SaaS | Torres (Continuous Discovery), Cagan (Inspired) |
| **#2 UX** | Multi-channel UX patterns, WhatsApp UX | Norman (Design of Everyday Things), Krug (Don't Make Me Think) |
| **#3 UI** | OKLCH design system, React Flow patterns | Frost (Atomic Design), Vignelli (Grid Systems) |
| **#4 Frontend** | Code splitting, TanStack Query, React Flow | Abramov (React patterns), Osborne (React Flow) |
| **#5 Backend** | Rust (Axum + Tokio), gRPC, Adapter Pattern, Event Sourcing, Multi-tenant | Fowler (Patterns of Enterprise Architecture), Evans (DDD) |
| **#6 QA** | Multi-channel testing, E2E with Playwright | Beck (TDD), Rainsberger (Integrated Tests) |
| **#7 Growth** | SaaS metrics, LATAM growth strategy | Balfour (Reforge), Kohani (Hacking Growth) |

### Agentes Nuevos Potenciales

| Agente | Propósito | Prioridad |
|--------|-----------|-----------|
| **brain-08-channel-router** | Enruta mensajes al canal óptimo (WhatsApp vs email vs IG) | Fase 3 |
| **brain-09-customer-success** | Gestiona relación con clientes, NPS, churn prevention | Fase 4 |
| **brain-10-compliance** | Cumplimiento regulatorio LATAM (protección de datos) | Fase 5 |

---

## 6. Competitividad — Por Qué MasterMind Gana

### vs Agentify (competidor directo LATAM)

| Aspecto | Agentify | MasterMind v3.0 |
|---------|----------|-----------------|
| **Multi-agente** | ❌ Un bot | ✅ 7+ agentes especializados |
| **Knowledge** | ❌ Genérico | ✅ Expertise destilada (Cagan, Norman, etc.) |
| **Diagnóstico** | ❌ Solo atención | ✅ Diagnóstico + rediseño de procesos |
| **Canvas visual** | ❌ No | ✅ React Flow DAG |
| **Open-source** | ❌ Propietario | ✅ MIT (core) |
| **WhatsApp nativo** | ✅ Sí | 🔄 Fase 3 |
| **LATAM focus** | ✅ Uruguay | ✅ Regional |

### vs Paperclip (open-source)

| Aspecto | Paperclip | MasterMind v3.0 |
|---------|-----------|-----------------|
| **Agent knowledge** | ❌ Agentes vacíos | ✅ Knowledge distillation |
| **Multi-canal** | ❌ No | ✅ WhatsApp + IG + email |
| **LATAM** | ❌ No | ✅ Nativo |
| **Business model** | ❌ Ninguno | ✅ SaaS + marketplace |
| **Testing** | ❌ 11% coverage | ✅ 80%+ target |
| **Code splitting** | ❌ Zero | ✅ Lazy loading desde día 1 |

---

## 7. Métricas de Éxito

### KPIs por Fase

| Fase | KPI | Target |
|------|-----|--------|
| 1 | PostgreSQL migration sin data loss | 100% |
| 2 | Canvas render time | < 100ms |
| 2 | Code splitting coverage | 100% lazy routes |
| 3 | WhatsApp response time | < 3s |
| 3 | Multi-channel uptime | 99.9% |
| 4 | Experience records por sesión | >= 5 |
| 4 | Auto-learning improvement | Delta-Velocity > 1.0 |
| 5 | Templates disponibles | >= 10 |
| 5 | Paying customers | >= 5 |

### North Star Metric

**Reducción de tiempo en tareas repetitivas: 30%+**

---

## 8. Riesgos y Mitigaciones

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| **WhatsApp API approval** | ALTO | Empezar con sandbox Meta, documentación temprana |
| **Token costs** | MEDIO | Budget enforcement por sesión, alerts en 80% |
| **Multi-tenant isolation** | MEDIO | Aprender de Paperclip company_id pattern |
| **Scope creep** | ALTO | Fases estrictas, Brain #7 gate entre fases |
| **LATAM adoption** | MEDIO | Focus en nichos con ROI claro (agencias, dev shops) |

---

## 9. Próximos Pasos Inmediatos

1. **Aprobar este PRP** — ¿Estás de acuerdo con la dirección?
2. **Fork Paperclip UI** — Copiar `ui/` → `apps/web-v3/` → Rebrand MasterMind
3. **Bootstrapping Rust** — Axum + Tokio + tonic (gRPC) + SQLx
4. **Fase 1 kickoff** — PostgreSQL migration + Rust Control Plane + Protobuf contracts
5. **Dispatch Brain #5** — Diseñar schemas + migraciones + gRPC service definitions
6. **Crear milestones** — `/gsd:new-milestone` para v3.0

**Referencias:**
- `docs/nuevo giro/PAPERCLIP-UX-AUDIT.md` — 10 patrones UX documentados
- `docs/nuevo giro/Panorama competitivo...` — Análisis competitivo LATAM
- `/home/rpadron/proy/paperclip/` — Código fuente Paperclip (fork candidate)
- `/home/rpadron/proy/paperclip/ui/` — 41 páginas + 94 componentes (copiar)
- `/home/rpadron/proy/paperclip/server/src/` — Backend (evaluar Rust vs Python)

---

*PRP condensado de: Panorama Competitivo LATAM + Análisis Multi-Brain Paperclip + PRP AAF v2.0 + Infraestructura MasterMind v2.2*
*Autor: MasterMind 7-Brain Analysis System*
*Fecha: 2026-04-04*
