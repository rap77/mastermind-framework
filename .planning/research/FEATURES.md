# Feature Landscape

**Domain:** Enterprise Agent Orchestration Platform with Knowledge Distillation
**Researched:** 2026-04-04
**Overall confidence:** MEDIUM (WebSearch limit reached — relying on project docs + technical standards)

---

## Executive Summary

MasterMind v3.0 introduce **6 features empresariales críticas** que lo diferencian de competidores LATAM. El **moat competitivo** es el **Knowledge Distillation Engine** — ningún competidor tiene expertise destilada de expertos mundiales (Cagan, Torres, Norman, etc.) embebida en agentes.

Las features se dividen en:
- **3 Table Stakes** (esperadas en plataformas empresariales)
- **2 Differentiators** (valor único vs competidores)
- **1 Anti-Feature** (explícitamente NO construir)

**Dependencies on existing system:**
- Auth/JAT → migrar a Rust Control Plane
- 7 Brain Agents → conectar via gRPC
- WebSocket infra → reemplazar con Rust Hub
- React Flow DAG → ampliar con Canvas
- experience_records → evolucionar a Event Store

---

## Table Stakes

Features que los usuarios esperan en una plataforma empresarial. Si faltan, el producto se siente incompleto.

### 1. Rust Control Plane — Auth + RBAC + Execution Engine

**Why Expected:**
- Plataformas empresariales requieren **multi-tenant con aislamiento**
- Control de acceso granular (RBAC) es estándar en SaaS
- Performance predecible bajo carga (miles de usuarios)
- Auditoría de acciones (compliance)

**Complexity:** HIGH

**Core Capabilities:**
| Capability | Description | Notes |
|------------|-------------|-------|
| **JWT Auth + Refresh** | Migrar FastAPI JWT → Rust middleware | Ya existe en Python, migrar lógica |
| **RBAC** | Role-based access control por organización | Paperclip usa `company_id` pattern |
| **User Management** | CRUD usuarios, asignación de roles | Standard en plataformas multi-tenant |
| **Execution Engine** | State management, process spawning | Inspirado en `heartbeat.ts` de Paperclip |
| **Budget Enforcement** | Límites de tokens/costos por sesión | Prevenir sorpresas en facturación |
| **Adapter Registry** | Dynamic routing a adapters (WhatsApp, IG, email) | Trait pattern en Rust |

**Anti-Patterns to Avoid:**
- ❌ Global state sin locks → race conditions
- ❌ Blocking operations en async runtime → bloquear todo el servidor
- ❌ Hardcoded secrets → usar environment variables

**Expected Behavior:**
```
Usuario login → JWT (30min) + Refresh (24h)
    ↓
Request → Rust middleware verifica JWT
    ↓
RBAC check → user.permissions vs resource.required_permissions
    ↓
Execution → Python Agent Runtime via gRPC
    ↓
Response → Budget enforcement (tokens gastados < quota)
    ↓
Audit log → activity_log inmutable (Event Store)
```

**Dependencies on Existing System:**
- ✅ `apps/api/` tiene JWT + refresh rotation → migrar a Rust
- ✅ `api_keys_v2` table → modelo para RBAC
- ✅ `experience_records` → evolucionar a `activity_log`
- ⚠️ Requires PostgreSQL migration (SQLite → PostgreSQL)

**Confidence:** HIGH (patrón validado en Paperclip + estándares enterprise)

---

### 2. Real-time Hub — WebSocket Server

**Why Expected:**
- Dashboard en tiempo real es **table stakes** en plataformas de orquestación
- Monitoreo de agentes requiere updates en vivo (no polling)
- Colaboración multi-usuario necesita broadcast de eventos
- Paperclip tiene `ActiveAgentsPanel` con ping animation → usuarios esperan esto

**Complexity:** HIGH

**Core Capabilities:**
| Capability | Description | Notes |
|------------|-------------|-------|
| **WebSocket Server** | Tokio-tungstenite para miles de conexiones | Zero GC pauses vs Node.js |
| **Event Broadcasting** | Redis pub/sub para cross-service events | brain_started, brain_completed, brain_failed |
| **Connection Pooling** | Manejo eficiente de miles de conexiones concurrentes | Rust ownership model ayuda |
| **Heartbeat Protocol** | Ping/pong para detectar conexiones muertas | Re-connect automático |
| **Per-client Filtering** | Cada cliente recibe solo sus eventos relevantes | company_id filtering |

**Anti-Patterns to Avoid:**
- ❌ Unbounded message queues → memory leak
- ❌ Blocking sends en WebSocket → bloquear other clients
- ❌ No backpressure → crash del servidor

**Expected Behavior:**
```
Frontend conecta → WebSocket handshake (JWT auth)
    ↓
Suscribe a eventos → company_id, brain_ids
    ↓
Backend evento → Redis pub/sub (brain_completed)
    ↓
WebSocket Hub → Broadcast a clientes suscriptos
    ↓
Frontend → Zustand + RAF batching (ya existe)
    ↓
UI update → 60fps incluso con 24+ brain events concurrentes
```

**Dependencies on Existing System:**
- ✅ `apps/web/src/stores/brainStore.ts` → Zustand + RAF batching ya implementado
- ✅ `WebSocket Infrastructure (WS-01 through WS-03)` → patrones probados
- ⚠️ Requiere Redis pub/sub (nueva dependencia)
- ⚠️ Migrar WebSocket server Python → Rust Tokio

**Confidence:** HIGH (existente en v2.2, escalar a Rust es well-trodden path)

---

### 3. Multi-channel Gateway — WhatsApp + Instagram + Email

**Why Expected:**
- Pymes LATAM usan **WhatsApp como canal principal** de comunicación
- Instagram DM es crítico para negocios visuales (ecommerce, marketing)
- Email sigue siendo estándar para comunicación formal
- Competidores (Agentify) ya tienen WhatsApp → feature parity

**Complexity:** HIGH

**Core Capabilities:**
| Capability | Description | Notes |
|------------|-------------|-------|
| **WhatsApp Business API** | Webhook receiver + mensajería bidireccional | Meta approval requerido |
| **Instagram DM** | Graph API integration | Mismo backend que WhatsApp (Meta) |
| **Email Gateway** | IMAP/SMTP integration (lettre + imap crates) | Parsing + routing |
| **Unified Inbox** | Bandeja única para todos los canales | Threaded conversations |
| **Channel Router** | Brain #8 decide qué canal usar | WhatsApp para urgente, email para formal |
| **Template Management** | Plantillas de respuesta por canal | WhatsApp templates requieren aprobación Meta |

**Anti-Patterns to Avoid:**
- ❌ Hardcoded API keys → rotación segura
- ❌ No rate limiting → bloqueo por Meta
- ❌ Ignorar webhooks verificados → security vulnerability
- ❌ No reintentos en fallos → mala experiencia

**Expected Behavior:**
```
Cliente mensaje → WhatsApp webhook
    ↓
Rust Gateway → Verificar signature (security)
    ↓
Channel Router → Brain #8: ¿Responder por WhatsApp o email?
    ↓
Brain Agent → Procesa consulta con knowledge
    ↓
Response → Rust Gateway → WhatsApp API
    ↓
Cliente → Recibe respuesta en mismo canal
    ↓
Escalación → Si Brain #7 rechaza, humano toma control
```

**Dependencies on Existing System:**
- ✅ `brain_router.py` → extender para channel routing
- ✅ 7 Brain Agents → knowledge ya disponible
- ⚠️ Requires new brain-08-channel-router agent
- ⚠️ Requires Meta developer account + app approval

**Confidence:** MEDIUM (WhatsApp API es bien documentado, pero Meta approval es external risk)

---

## Differentiators

Features que **no se esperan** pero agregan valor único vs competidores.

### 4. Knowledge Distillation Engine — Learning Loop

**Value Proposition:**
- **MOAT COMPETITIVO:** Ningún competidor LATAM tiene expertise destilada
- Agentes mejoran con cada interacción (no son estáticos)
- Brain #7 evalúa outputs → feedback → ajuste automático
- Delta-Velocity tracking: medir mejora vs baseline

**Complexity:** HIGH

**Core Capabilities:**
| Capability | Description | Notes |
|------------|-------------|-------|
| **Experience Logging** | Cada brain operation → experience_record | Ya existe en v2.2 |
| **Pattern Extraction** | Análisis de patrones recurrentes | NLP para agrupar similares |
| **Brain #7 Evaluation** | Meta-cerebro valida outputs | Barrier pattern después de domain agents |
| **Feedback Loop** | Human corrections → anti-patterns → brain memory | Continuous learning |
| **Delta-Velocity** | Métrica de mejora vs baseline | Comparar sesión N vs sesión 1 |
| **Template Generation** | Interacciones exitosas → plantillas reusables | Brain #1 sugiere templates |

**Why It's Unique:**
```
Paperclip:    Agentes vacíos → ejecutan sin knowledge
Agentify:     Bots genéricos → sin especialización
MasterMind:   7 cerebros con expertise Cagan, Torres, Norman, etc.
              + learning loop → mejoran con el tiempo
```

**Expected Behavior:**
```
Usuario brief → Brain Agents (paralelo)
    ↓
Brain #1 (Product Strategy) → NotebookLM (Cagan knowledge)
    ↓
Brain #4 (Frontend) → grep codebase + patterns aprendidos
    ↓
Brain #7 (Evaluator) → ¿Output válido?
    ↓
Si YES → Experience Logger → PATRÓN GUARDADO
    ↓
Si NO → Anti-pattern detectado → Brain memory actualizada
    ↓
Delta-Velocity → ¿Mejoró vs baseline?
    ↓
Template Generation → Si patrón repetido 5x → plantilla
```

**Dependencies on Existing System:**
- ✅ `experience_records` table → SQLite, migrar a PostgreSQL
- ✅ `brain_memory.py` CLI → query/log ya implementado
- ✅ `BRAIN-FEED` two-level architecture → global + domain feeds
- ✅ 7 Brain Agents con memoria → ya operacionales
- ⚠️ Requires NLP library para pattern extraction (spaCy/LangChain)

**Confidence:** HIGH (infraestructura existe, escalar a analytics es evolution)

---

### 5. Template Marketplace — Pre-built Agent Configurations

**Value Proposition:**
- **Time-to-value:** Usuarios arrancan con configuraciones probadas
- **Verticalización:** Templates por industria (Software Dev Agency, Marketing, Customer Support)
- **Community contribution:** Usuarios pueden compartir templates
- **Revenue stream:** Marketplace premium en el futuro

**Complexity:** MEDIUM

**Core Capabilities:**
| Capability | Description | Notes |
|------------|-------------|-------|
| **Template Gallery** | UI estilo Clipmart (Paperclip marketplace) | Categorías por vertical |
| **One-click Deploy** | Template → nueva compañía con agentes pre-configurados | Fast onboarding |
| **Version Control** | Templates con versionado semántico | Changelog por template |
| **Import/Export** | YAML de configuración de compañía | Portable entre instalaciones |
| **Rating System** | Usuarios califican templates | Social proof |
| **Usage Analytics** | Qué templates se usan más | Data-driven improvements |

**Why It's Unique:**
```
Competidor:    Marketplace de workflows vacíos
MasterMind:    Templates con 7 cerebros pre-cargados con knowledge
               + patterns aprendidos de casos reales
```

**Expected Behavior:**
```
Usuario nuevo → Browse Template Gallery
    ↓
Selecciona "Software Dev Agency" template
    ↓
One-click deploy → Nueva compañía creada
    ↓
Pre-configured:
    - 7 Brain Agents activos
    - Channels: WhatsApp + Email configurados
    - Playbooks: Cagan discovery, Norman UX review, etc.
    - Baselines: 5 pre-migration baselines cargados
    ↓
Usuario modifica → Customiza para su needs
    ↓
Export → Comparte template con comunidad
```

**Dependencies on Existing System:**
- ✅ 7 Brain Agents → base de templates
- ✅ `BRAIN-FEED` → knowledge por dominio
- ✅ Company configuration pattern → de Paperclip
- ⚠️ Requires marketplace UI (Clipmart-style)
- ⚠️ Requires template versioning system

**Confidence:** MEDIUM (requiere investigación con usuarios LATAM — CONDITIONAL en PRP)

---

## Anti-Features

Features explícitamente **NO construir** en v3.0.

### Anti-Feature 1: Machine Learning Auto-Improvement

**Why Avoid:**
- R&D heavy — incertidumbre tecnológica
- Requiere dataset de entrenamiento grande
- ROI incierto — learning loop manual es suficiente para v3.0
- Competidores tampoco lo tienen → no es table stakes

**Instead:**
- **Learning Loop manual:** Human corrections → brain memory
- **Delta-Velocity tracking:** Medir mejora vs baseline (ya diseñado)
- **Template Generation:** Basado en patrones, no en ML

**Future:** v4.0+ cuando se tenga dataset suficiente + validación de ROI

---

### Anti-Feature 2: Full RAG System with Vector DB

**Why Avoid:**
- PostgreSQL + pgvector es suficiente para v3.0
- ChromaDB/Qdrant agregan complejidad operacional
- 7 cerebros = knowledge acotado por dominio → no requiere vector DB global
- Costo operacional vs beneficio no justifica para v3.0

**Instead:**
- **RAG per agent:** Cada brain tiene su propio conocimiento (NotebookLM)
- **Project BRAIN-FEED:** Memoria por proyecto (no vector DB)
- **PostgreSQL + pgvector:** Para embeddings cuando scale (v3.1+)

**Future:** v3.1+ cuando scale requiera optimización de retrieval

---

### Anti-Feature 3: Mobile Apps

**Why Avoid:**
- Web-first es suficiente para LATAM (WhatsApp ya es mobile)
- Desarrollo mobile nativo es expensive (iOS + Android)
- React Native add complexity → velocidad de desarrollo
- Pymes usan desktop en oficina

**Instead:**
- **Responsive web:** Mobile-optimized UI (copiar Paperclave responsive patterns)
- **PWA:** Progressive Web App para instalación en móvil
- **WhatsApp Native:** Usuarios ya usan WhatsApp app

**Future:** v4.0+ si demanda de usuarios lo justifica

---

## Feature Dependencies

```
Rust Control Plane (VS)
    ↓ Required for
Real-time Hub (RTU) + Multi-channel Gateway (MCG)

Knowledge Distillation (KD)
    ↓ Extends
7 Brain Agents (EXISTING) → Experience Records (EXISTING)

Template Marketplace (CONDITIONAL)
    ↓ Requires
Knowledge Distillation (patterns → templates) + Multi-channel (playbooks)

Orchestration Canvas (UIE)
    ↓ Extends
React Flow DAG (EXISTENTE in Nexus)
```

**Dependency Graph:**
```
VS (Rust Control Plane) → RTU (Real-time Hub) + MCG (Multi-channel)
KD (Knowledge Distillation) → TEMPLATE (Marketplace)
UIE (Canvas) → Standalone (extends existing Nexus)
```

---

## MVP Recommendation

**Phase 0 (Fork Paperclip UI):** 1-2 weeks
- Table stakes UX patterns
- Foundation for Rust backend

**Phase 1 (Foundation):** 3-4 weeks
1. **Rust Control Plane** — Auth + RBAC + PostgreSQL migration
2. **gRPC Bridge** — Type sync Rust ↔ Python ↔ TypeScript
3. **Adapter Registry** — Foundation for multi-channel

**Phase 2 (Real-time):** 2-3 weeks
1. **Real-time Hub** — WebSocket server Rust
2. **Orchestration Canvas** — React Flow enhanced (extends Nexus)

**Phase 3 (Multi-channel):** 3-4 weeks
1. **WhatsApp Gateway** — Webhook receiver
2. **Instagram + Email** — Multi-channel adapter

**Phase 4 (Knowledge):** 3-4 weeks
1. **Knowledge Distillation Engine** — Learning loop
2. **Delta-Velocity Tracking** — Metrics dashboard

**Phase 5 (Marketplace):** CONDITIONAL on 3 LATAM SME interviews + 1 LOI
1. **Template Gallery** — Clipmart-style UI
2. **One-click Deploy** — Templates por vertical

**Defer:**
- **Machine Learning Auto-Improvement** — v4.0+ (R&D)
- **Full RAG with Vector DB** — v3.1+ (scale trigger)
- **Mobile Apps** — v4.0+ (demand trigger)

---

## Complexity Assessment

| Feature | Complexity | Risk | Notes |
|---------|-----------|------|-------|
| Rust Control Plane | HIGH | MEDIO | Nuevo lenguaje para equipo Python |
| Real-time Hub | HIGH | MEDIO | Scaling a miles de conexiones |
| Multi-channel Gateway | HIGH | ALTO | Meta API approval es external dependency |
| Knowledge Distillation | HIGH | BAJO | Infraestructura existe, escalar es evolution |
| Template Marketplace | MEDIUM | MEDIO | Requiere validación con usuarios |
| Orchestration Canvas | MEDIUM | BAJO | Extiende Nexus existente |

**Highest Risk Items:**
1. **Meta API Approval** (WhatsApp/Instagram) — External dependency, timeline uncertain
2. **Rust Learning Curve** — Equipo Python debe aprender Rust
3. **PostgreSQL Migration** — Data loss risk si migration falla

**Mitigation:**
- Meta: Empezar con sandbox, documentación temprana
- Rust: Vertical slice first (Fase VS), escape hatch si velocity < 0.5x
- PostgreSQL: Migration con rollback plan + testing extensivo

---

## Sources

### Project Documentation (HIGH confidence)
- `.planning/PROJECT.md` — Existing system capabilities
- `docs/nuevo giro/PRP MasterMind v3.0.md` — Feature specifications
- `docs/nuevo giro/PAPERCLIP-UX-AUDIT.md` — 10 UX patterns to replicate
- `/home/rpadron/proy/paperclip/` — Source code analysis (competitive intelligence)

### Technical Standards (MEDIUM confidence)
- Rust Axum + Tokio — Async web framework standard
- gRPC + Protobuf — Type-safe microservices communication
- PostgreSQL + pgvector — Vector storage in relational DB
- React Flow v12 — Visual DAG library (already installed)

### External Sources (LOW confidence — WebSearch limit reached)
- **Note:** WebSearch unavailable due to weekly limit (resets 2026-04-13)
- Findings based on project docs + technical standards only
- **Recommendation:** Validate with LATAM SME interviews before Phase 5 (Marketplace)

---

*Research completed: 2026-04-04*
*Confidence: MEDIUM (WebSearch limit — project docs + technical standards only)*
*Next: STACK.md research for technology recommendations*
