---
proposal_id: "PROP-005"
title: "Integraciones Nativas via MCP con UI de Configuración"
status: "DEFERRED"
created_at: "2026-04-06"
last_updated: "2026-04-06"
brain_evaluations:
  - brain: "Brain #1 (Product Strategy)"
    verdict: "DEFERRED"
    confidence: 85%
  - brain: "Brain #4 (Frontend Architecture)"
    verdict: "TECHNICAL READY"
    confidence: 80%
  - brain: "Brain #5 (Backend Architecture)"
    verdict: "SECURITY HEAVY"
    confidence: 85%
  - brain: "Brain #7 (Growth/Data - Meta-evaluator)"
    verdict: "DEFERRED"
    confidence: 85%
---

# PROP-005: Integraciones Nativas via MCP con UI de Configuración

**Estado:** 🔴 **DEFERRED** — Prematuro sin validar demanda para usuarios no técnicos

**Confianza:** 85%

---

## Resumen Ejecutivo

**Problema identificado:** Para conectar un agente a Slack, Gmail, Notion, etc. tienes que hacerlo tú mismo (configuración manual en settings.json)

**Solución propuesta:** Integraciones nativas via MCP con UI de configuración

**Valor declarado:** UX simplificada — el usuario configura integraciones sin tocar archivos

---

## Evaluación de Brains

### Brain #1 (Product Strategy) — DEFERRED 🔴 (85% confianza)

#### ✅ Lo Bueno
- Feature real para v3.1+ si el pivot a SaaS multi-tenant se concreta
- Para usuarios no técnicos, configurar MCP sin tocar código es core capability

#### ⚠️ Lo Que Falta
- **Evidencia ANY de problema hoy** — Builder YA SABE configurar MCP manualmente
- **No hay friction reportada** — El usuario actual (técnico) no tiene pain con settings.json
- **External users NO validados** — Marketplace es CONDITIONAL (3 interviews + 1 LOI)

#### 🚨 Peligros
- **Build Trap puro** — Medir éxito por "UI shipped" no "platform capability mejorada"
- **Opportunity cost real** — Robar tiempo de Phase 15 (Rust Control Plane) que es critical path para v3.0

#### 💭 Sugerencias
1. **DEFER hasta Marketplace active** — 3 entrevistas + 1 LOI
2. **Fake Door Test de 2 días** — Wireframe + landing page antes de comprometer 3 semanas
3. **Alternativa CLI helper** — `npx mastermind mcp add --server notebooklm` (1 día vs 2-3 semanas)

---

### Brain #4 (Frontend Architecture) — TECHNICAL READY 🟢 (80% confianza)

#### ✅ Lo Bueno
- **Stack alineado:** Sheet, Card, Zustand, Server Actions, TanStack Query
- **APIKeyManager es template perfecto** — Patrón de tabs + query reutilizable
- **Server Actions = OAuth Seguro** — Patrón ya establecido en codebase

#### ⚠️ Lo Que Falta
- **Página de integraciones** — Hoy solo existe Command Center, Nexus, Strategy Vault, Engine Room
- **useMCPStore** — Falta store con `Map<string, IntegrationState>`
- **OAuth callback handler** — Falta `/api/integrations/callback/[provider]/route.ts`

#### 🚨 Peligros
- **Layout Shift (CLS)** con 10+ integraciones — Skeleton screens obligatorios
- **Throttling de Status Updates** — Si MCP envía updates cada 100ms, INP muere
- **React.memo OBLIGATORIO** — Compiler desactivado, re-renders masivos sin memo
- **Memory Leaks** en WS subscriptions si cleanup se olvida

#### 💭 Sugerencias
1. **Vertical Slice primero** — 1 integración fake (Slack) antes de 10 reales
2. **Copiar patrón APIKeyManager** — Tabs structure + TanStack Query con staleTime corto
3. **Usar Sheet no Dialog** — Permite ver lista mientras configuras
4. **Performance observables** — CLS < 0.1, INP < 200ms, 1 card update = 1 re-render

---

### Brain #5 (Backend Architecture) — SECURITY HEAVY 🔒 (85% confianza)

#### ✅ Lo Bueno
- **Patrón MCP ya existe** — Tipos Pydantic en `mastermind_cli/types/mcp.py`
- **Auth robusto** — JWT + API keys con hash SHA-256 + bcrypt
- **Almacenamiento de credenciales probado** — Tabla `api_keys` demuestra patrón correcto

#### ⚠️ Lo Que Falta
- **Endpoints CRUD** — `POST /api/integrations`, `GET`, `PUT`, `DELETE`, `/test`
- **Tabla mcp_integrations** — SQLite para almacenar config + OAuth tokens
- **OAuth flow handlers** — 3 endpoints por proveedor (authorize, callback, disconnect)
- **Cifrado de tokens** — Fernet encryption para access/refresh tokens

#### 🚨 Peligros
- **AUTH BYPASS RIESGO** — Todos endpoints DEBEN requerir JWT (`Depends(get_current_user)`)
- **OAuth CSRF Attack** — Sin `state` parameter, app es vulnerable
- **Token Leakage en logs** — Nunca loguear `oauth_token`, `api_key` en plaintext
- **IDOR en endpoints** — Sin `WHERE user_id = ?`, Usuario A accede a integraciones de Usuario B
- **SQL Injection** en server_config JSON si construyes SQL dinámico

#### 💭 Sugerencias
1. **Phase 1: Custom Servers (sin OAuth)** — Solo command + args (como serena, context7)
2. **Phase 2: OAuth Gmail** — Un proveedor antes de generalizar a Notion/Slack
3. **Type Contracts Pydantic v2 strict** — `model_config = ConfigDict(strict=True)`
4. **Service Layer** — `services/mcp_connector.py` con `test_connection()`, `refresh_oauth_token()`

---

### Brain #7 (Growth/Data - Meta-evaluator) — DEFERRED 🔴 (85% confianza)

#### Veredicto Final

**DEFERRED** — Optimizar para usuario que NO existe es Build Trap puro. La UI no crea demanda, la demanda valida la UI.

#### Tensiones Identificadas

**TENSIÓN 1: Builder vs. Future User**
- Brain #1 optimiza: Builder technical (usuario actual, YA existe)
- Brain #4+#5 optimizan: Future SME non-technical (usuario hipotético, NO validado)
- **GANADOR:** Brain #1 — Sin external users validados, construir UI es prematuro

**TENSIÓN 2: Security vs. Speed**
- Brain #5 dice: OAuth CSRF requiere threat modeling + security review (semanas)
- Brain #1 dice: Phase 15 no puede esperar (roadmap crítico)
- **GANADOR:** Brain #5 — Security no es negotiable en plataforma Enterprise

**TENSIÓN 3: Technical Debt vs. Opportunity Cost**
- Brain #4+#5 dicen: MCP UI es deuda técnica manejable
- Brain #1 dice: Opportunity cost de Phase 15 es inaceptable
- **GANADOR:** Brain #1 — Deuda técnica se puede pagar después. Opportunity cost NO se recupera.

#### Second-Order Effects

**1. Feature Factory Trap**
Implementar UI sin validar demanda = síntoma de "Feature Shipping" en lugar de "Systems Thinking". Genera deuda técnica sin retorno claro en Product-Market Fit.

**2. Cascade Failure — Efecto Lollapalooza**
Convergencia de: (1) implementación apresurada Frontend (CLS/memory leaks), (2) riesgos OAuth CSRF, (3) presión Phase 15. Si OAuth CSRF attack ocurre → brecha de seguridad catastrófica → confianza LATAM destruida.

**3. Systemic Inertia — Atomic Network Dilución**
Pivot v3.0 = Enterprise LATAM. Atomic Network inicial = Builders técnicos. Optimizar para no-técnicos prematuramente diluye propuesta de valor para segmento que genera tracción inicial.

#### Systemic Metrics

| SLI/OKR | Qué mide | Target | ¿Qué indica si falla? |
|---------|----------|--------|----------------------|
| **SLI-1: Activation Rate** | Time to first successful MCP connection | <1 día | Supuesto de "no fricción" es FALSO |
| **SLI-2: Support Ticket Rate** | Tickets configuración MCP/month | Incremento sostenido | Producto superó capacidad técnica base actual |
| **SLI-3: Fake Door CTR** | CTR botón "Configurar vía UI" (deshabilitado) | >20% | Invalida asunción de no demanda latente |
| **OKR: Market Validation** | 3 entrevistas Mom Test + 1 LOI | Completado | Demanda real validada |

---

## Condiciones CRÍTICAS para Re-evaluación

### Condición #1: Market Validation (BLOCKER estratégico)
- 3 entrevistas Mom Test con LATAM SMEs
- Pregunta basada en COMPORTAMIENTOS PASADOS: "¿Cómo configuraste tu último server?", no "¿Te gustaría una UI?"
- 1 LOI (Letter of Intent) o piloto pagado confirmado

### Condición #2: Marketplace Active (BLOCKER estratégico)
- Marketplace (original roadmap Phase 6) activado
- Validado que hay external users demandando integraciones

### Condición #3: Phase 15 Complete (BLOCKER técnico)
- Rust Control Plane completo o en milestone estable
- v3.0 critical path antes de features nice-to-have

### Condición #4: Métricas de Control (BLOCKER de evidencia)
- SLI-1/2/3 indican demanda latente real
- Fake Door Test con CTR >20%

---

## Roadmap Sugerido

| Fase | Qué | Cuándo | Condición | Duración |
|------|-----|--------|-----------|----------|
| **NOW** | Phase 15 (Rust Control Plane) | Inmediato | v3.0 critical path | 3-4 semanas |
| **v3.0** | CLI helper (`npx mcp add`) | Si alguien reporta pain | "Hate editing JSON" | 1 día |
| **v3.1** | MCP Configuration UI | Después de condiciones | 3 interviews + 1 LOI + Marketplace | 2-3 semanas |
| **v3.1+** | OAuth (Gmail, Notion) | Solo después de MCP UI validada | Custom servers funcionando | 1-2 semanas |

---

## Alternativa Sugerida: CLI Helper

Si el problema es "hate editing JSON" (no reportado aún):

```bash
npx mastermind mcp add --server notebooklm --url "..." --args "..."
npx mastermind mcp list
npx mastermind mcp remove <server-id>
```

**Costo:** 1 día vs 2-3 semanas para full UI

**Ventajas:**
- No requiere OAuth complexity
- No requiere UI development
- Satisface a usuarios técnicos (Builder actual)
- Fácil de iterar

---

## Archivos Clave Existentes

- `apps/web/src/components/engine-room/KeyCreateDialog.tsx` — Patrón de form + Server Actions
- `apps/api/mastermind_cli/routes/auth.py` — JWT + API keys (patrón de auth)
- `apps/api/mastermind_cli/models.py` — `api_keys` table (patrón de almacenamiento)
- `components/ui/sheet.tsx` — Sheet component para configuración

---

## Cascade Risk

**Si OAuth CSRF attack ocurre:**
- Gmail/Notion tokens comprometidos → acceso a datos empresariales → liability legal → confianza LATAM destruida → v3.0 pivot muerto

**Si MCP config UI tiene bugs:**
- Configuración inválida → brains fallan silenciosamente → UX degrada → soporte aumenta → tiempo de Phase 15 robado

**Si Phase 15 se retrasa por MCP UI:**
- v3.0 enterprise platform se retrasa → first-mover advantage en LATAM perdido → competidores ocupan nicho

---

## Next Action

**Opción A:** Continuar con Phase 15 (Rust Control Plane) — Critical path para v3.0

**Opción B:** Fake Door Test (2 días) — Wireframe + landing page para medir demanda latente

**Opción C:** CLI helper (1 día) — Si alguien reporta "hate editing JSON"

---

*Created: 2026-04-06*
*Status: DEFERRED — Prematuro sin validar demanda para usuarios no técnicos*
*Next review: After Marketplace active + 3 interviews + 1 LOI*
