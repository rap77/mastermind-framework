---
name: HANDOFF-2026-03-13-PHASE3-DISCUSSION-PARTIAL
description: Partial Phase 3 discussion progress - Auth & Dashboard decisions captured
type: project
---

# Handoff - Phase 3 Discussion Partial

**Fecha:** 2026-03-13
**Estado:** Discusión parcial (2 de 5 áreas completadas)
**Next:** Continuar con Real-time Updates, Observability, Mobile

---

## Decisiones Capturadas

### 1. Autenticación & Sesiones ✅

**Mecanismo Híbrido:**
- **Web UI**: JWT (Access + Refresh tokens con rotación)
  - Access token: 30 min
  - Refresh token: 24h con "Remember me"
  - Refresh Token Rotation para revocación segura
- **CLI**: API Keys (Personal Access Tokens)
  - Token de larga duración desde dashboard
  - `Authorization: Bearer <token>` header
  - Configurar WSL2 una sola vez con `mm auth login --key=...`

**Storage: Encrypted DB Store (Vault Pattern)**
- Todo en SQLite: `users` table + `api_keys` table
- Campos sensibles encriptados en reposo (ENV_VAR clave maestra)
- Relaciones SQL: users ↔ api_keys ↔ executions
- Consistente con Phase 2 (SQLite para task state)
- CRUD total en Web UI

**User Management: Single → Multi Evolution**
- Phase 3: Admin user por defecto (primer arranque pide crearlo)
- Sin RBAC, password recovery, email validation por ahora
- Foco 100% en Dashboard + WebSockets perfectos
- Multi-user UI para Phase 4

**Session Timeout: Hybrid Context-Aware**
- **CLI**: API Key persistente (no expira, protegido por Linux user)
- **Web UI**: 1 hora inactividad + Silent Refresh durante ejecución brains
- Pestaña cerrada → sesión muere en 30 min

---

### 2. Dashboard Layout & UI ✅

**Layout: Hybrid Command Center (IDE Style)**
- **Sidebar izquierdo**: Navegación rápida entre flujos (colapsable)
- **Bento Grid central**: KPIs + Grafo DAG protagonista
- **Panel inferior**: Logs en tiempo real del brain seleccionado

**Organización de tarjetas Bento Grid:**
- **60%**: Grafo DAG interactivo (23 nodos)
- **20%**: Métricas de Salud (fallos, latencia)
- **20%**: Proveedores (rate limiting Claude/NotebookLM)
- **Drawer inferior**: Terminal embebida con stream de pensamiento

**Visualización de Brains: Layered Sankey / Dependency Tree**
- Estilo CI/CD (GitHub Actions, Jenkins)
- Brains organizados en stages verticales (orden topológico)
- Conexiones fluyen izquierda → derecha
- Camino crítico visible instantáneamente

**Estados en tiempo real (nodos):**
- 🔳 **Gris (Pending)**: Esperando dependencias
- 🔵 **Azul Animado (Running)**: Procesando (spinner/progress bar)
- 🟢 **Verde (Completed)**: Éxito (hover = resumen output)
- 🔴 **Rojo (Failed)**: Error (nodo palpita + link al log)
- 🟡 **Amarillo (Skipped)**: Blast radius (dependencia falló)

**Librería de grafo:** React Flow o Svelte Flow

**Theme: System-Adaptive (Fluid)**
- Detección automática de preferencia OS/navegador
- Acentos dinámicos por estado:
  - Gris azulado en reposo
  - Verde esmeralda cuando todo va bien
  - Rojo neón si hay fallo crítico

**Paleta "Cyber-Modern":**
- Fondos profundos (#0F172A)
- Bordes sutiles + "glow" suave
- Tipografía: **JetBrains Mono** o **Geist Mono**

**Densidad: Semantic Density (Contextual)**
- **Grafo DAG**: Spacious (entender conexiones)
- **Logs + Tabla Estados**: Compact (máximo dato visible)
- **Zoom-dependent density**:
  - Alejado: solo colores
  - Acercado: IDs, tiempos, estados detallados

**Dashboard "Single Screen":**
- 23 brains + métricas en una sola pantalla (no scroll)
- Fuentes 12-13px legibles
- Padding reducido en tablas SQLite
- Pydantic output_data en visor colapsable compacto

---

## Áreas Pendientes (Sesión Siguiente)

### 3. Real-time Updates ⏳
**Dilemas definidos:**
- Tecnología de transporte: SSE vs WebSockets vs Polling
- Frecuencia de actualización: Event-based vs Stream-based vs Throttled

**Preferencia del usuario:** SSE (más ligero, HTTP nativo, unidireccional)

### 4. Observability & Debugger UI ⏳
**Requisitos del usuario:**
- Logs de cada brain en tiempo real
- Inspección del estado de SQLite desde la UI
- Visualización interactiva del grafo (DAG) con nodos que cambian de color
- Mostrar camino crítico y cuellos de botella (Topological Sort de Phase 2)

### 5. Mobile Responsiveness ⏳
**Por definir:** Responsive CSS vs separate mobile UI, touch interactions, portrait vs landscape

---

## Resumen de Progreso

**Áreas completadas:** 2/5 (40%)
**Decisiones capturadas:** 10 decisiones clave
**Tiempo de discusión:** ~30-40 min

**Siguiente comando:**
```bash
/clear
/sc:load
/gsd:discuss-phase 3
```

---

**Notas para el planner:**
- El usuario tiene visión técnica muy clara
- Prefiere enfoques híbridos y context-aware
- Valora herramientas profesionales (GitHub Actions, VS Code, Linear como referencias)
- Foco en densidad de información para power users
- Consistencia arquitectónica (SQLite, Pydantic) es prioridad
