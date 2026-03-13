---
source_id: "FUENTE-M13-004"
brain: "brain-marketing-13-ops"
niche: "marketing-digital"
title: "Customer Data Platforms: How to Build a Single View of the Customer"
author: "Segment Team (Twilio)"
expert_id: "EXP-M13-004"
type: "guide"
language: "en"
year: 2023
isbn: null
url: "https://segment.com/academy/introduction-to-cdp/"
skills_covered: ["H1", "H3", "H5", "H7"]
distillation_date: "2026-03-12"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-12"
changelog:
  - version: "1.0.0"
    date: "2026-03-12"
    changes:
      - "Ficha creada con destilación completa"
status: "active"

habilidad_primaria: "CDP strategy y data warehouse para marketing: identidad unificada del cliente"
habilidad_secundaria: "Event tracking, data pipelines, identity resolution, data governance"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "CRÍTICA — Segment (Twilio) es el estándar de CDP para empresas que no pueden construir un data warehouse propio. Su enfoque de 'collect data once, send everywhere' resuelve el problema de integración de múltiples herramientas de marketing."
---

# FUENTE-M13-004: Customer Data Platforms (Segment Team)

## Tesis Central

> **"El promedio de empresa tiene datos del cliente en 15+ sistemas siloados. CRM tiene email, analytics tiene user ID, e-commerce tiene customer ID, email platform tiene otro ID. Sin una forma de unificar estas identidades, cada herramienta tiene una versión diferente del 'mismo' cliente. Un CDP resuelve esto."**

---

## 1. Principios Fundamentales

### El problema del data silo

La realidad del stack de marketing moderno:

```
SISTEMA               IDENTIFICADOR         DATO
─────────────────────────────────────────────────────
Google Analytics      Cookie (GA4)          Comportamiento web
HubSpot CRM           Email                Datos de lead
Stripe               Customer ID          Transacciones
Klaviyo              Email + subscriber_id  Email engagement
Meta Ads              Device ID + FB pixel  Ad exposure
Salesforce           Lead ID              Pipeline
```

Sin unificación: no sabés que el usuario que compró en Stripe es el mismo que visitó el sitio 10 veces y abrió 5 emails de Klaviyo.

*Fuente: Segment, "The Data Silo Problem" (2023)*

### El modelo de Segment: Collect once, send everywhere

```
FUENTE DE DATOS → SEGMENT → DESTINATIONS
├── Website           ├→ GA4
├── Mobile App        ├→ HubSpot
├── Server            ├→ Klaviyo
├── CRM               ├→ Amplitude
└── Point of Sale     └→ Data Warehouse (Snowflake)
```

Un solo evento de "purchase" enviado a Segment se replica automáticamente a todas las herramientas conectadas.

*Fuente: Segment, "Architecture" (segment.com, 2023)*

---

## 2. Frameworks y Metodologías

### Framework: Event Tracking Standard

Segment define un estándar de eventos que toda empresa debe trackear:

**Identify (Quién es):**
```javascript
analytics.identify('user_123', {
  email: 'juan@example.com',
  name: 'Juan Pérez',
  plan: 'premium',
  signup_date: '2024-01-15'
})
```

**Track (Qué hace):**
```javascript
analytics.track('Completed Purchase', {
  order_id: 'ORD-1234',
  revenue: 99.90,
  products: [{id: 'SKU-001', name: 'Product A', quantity: 1}],
  payment_method: 'credit_card'
})
```

**Page (Qué ve):**
```javascript
analytics.page('Pricing Page', {
  plan_type: 'premium',
  utm_source: 'google',
  utm_campaign: 'spring_sale'
})
```

*Fuente: Segment, "Spec" (segment.com, 2023)*

### Framework: Identity Resolution

El proceso de unificar identidades diferentes:

```
STEP 1: User lands on site → Anonymous ID (aa1b2c3d...)
STEP 2: User signs up → Identify with email
STEP 3: Link: Anonymous ID + User ID = Unified Profile
STEP 4: Merge future events to Unified Profile
```

**Beneficio:** Si un usuario anónimo visitó 10 veces y luego se registró, el CDP une el comportamiento pre- y post-registro en un solo perfil.

*Fuente: Segment, "Identity Resolution Guide" (2023)*

### Framework: Source of Truth Hierarchy

Segment recomienda tener una jerarquía de fuentes de datos:

1. **Server events** → Confiables (no manipulables por cliente)
2. **Mobile SDK** → Confiables (difíciles de falsificar)
3. **Web events** → Menos confiables (ad blockers, ITP)
4. **Third-party data** → Menos confiables (compartidos, match rate bajo)

**Regla:** Siempre que sea posible, enviar eventos desde el servidor, no solo del cliente.

*Fuente: Segment, "Data Reliability" (2023)*

---

## 3. Modelos Mentales

### "Data without schema is worthless"

Tener un CDP no es suficiente — hay que definir el schema de eventos: qué eventos se trackean, qué propiedades tienen cada uno, quiénes son los owners. Sin schema, el CDP es un data lake sin estructura.

*Fuente: Segment, "Data Governance" (2023)*

### "Pii-data requires extra protection"

Los datos personales (email, nombre, dirección) en el CDP requieren tratamiento especial: encriptación, acceso restringido, compliance con GDPR. El CDP puede ser un riesgo si no se maneja correctamente.

*Fuente: Segment, "Privacy and Security" (2023)*

---

## 4. Criterios de Decisión

### Segment vs. data warehouse propio (Snowflake, BigQuery)

| Criterion | Segment (CDP) | Data Warehouse Propio |
|-----------|---------------|----------------------|
| **Time to value** | Días/semanas | Meses |
| **Costo inicial** | Medio | Alto (engineers) |
| **Flexibilidad** | Media (schemas predefinidos) | Alta (custom SQL) |
| **Mantenimiento** | Vendor lo mantiene | Tu equipo lo mantiene |
| **Escalabilidad** | Hasta cierto punto | Ilimitada |

**Recomendación:** Usar Segment hasta llegar a cierto volumen (~100M eventos/mes), luego evaluar data warehouse propio.

*Fuente: Segment, "Build vs Buy" (2023)*

---

## 5. Anti-patrones

### Anti-patrón: Sending events without a plan

Implementar tracking de eventos sin un schema documentado lleva a datos inconsistentes: el mismo evento con diferentes nombres, propiedades con diferentes tipos, etc.

*Fuente: Segment, "Common Mistakes" (2023)*

### Anti-patrón: Ignoring data deletion requests

Under GDPR, si un usuario pide eliminar sus datos, el CDP debe poder hacerlo no solo en su propia DB sino en todos los destinations conectados. Sin esta capacidad, el CDP es un liability legal.

*Fuente: Segment, "GDPR Compliance" (2023)*

### Anti-patrón: Over-tracking events

Trackear todo que se mueve en la app genera data noise. Menos eventos, bien definidos y realmente usados, es mejor que miles de eventos que nadie consulta.

*Fuente: Segment, "Event Planning" (2023)*
