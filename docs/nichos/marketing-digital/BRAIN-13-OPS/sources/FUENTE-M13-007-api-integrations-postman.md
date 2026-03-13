---
source_id: "FUENTE-M13-007"
brain: "brain-marketing-13-ops"
niche: "marketing-digital"
title: "API Integrations for Marketing: From REST to Webhooks and Event-Driven Architectures"
author: "Postman API Team"
expert_id: "EXP-M13-007"
type: "guide"
language: "en"
year: 2023
isbn: null
url: "https://blog.postman.com/marketing-api-integrations/"
skills_covered: ["H3", "H5", "H7"]
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

habilidad_primaria: "Integraciones API para marketing operations: REST, webhooks, event-driven"
habilidad_secundaria: "API design, rate limiting, error handling, webhooks, authentication"
capa: 4
capa_nombre: "Criterios de Decisión"
relevancia: "ALTA — Postman es el estándar para trabajar con APIs. Su guía de integraciones para marketing operations documenta los patrones de integración más comunes entre herramientas MarTech (HubSpot, Salesforce, Stripe, etc.)"
---

# FUENTE-M13-007: API Integrations for Marketing (Postman API Team)

## Tesis Central

> **"La mayoría de las integraciones fallan por falta de understanding de los patrones básicos de APIs. Una integración que funciona en el 80% de los casos pero falla misteriosamente en el 20% restante es peor que no tener integración. Los patrones de retry, rate limiting, y error handling son la diferencia entre una integración frágil y una robusta."**

---

## 1. Principios Fundamentales

### Los 4 tipos de integraciones MarTech

Postman clasifica las integraciones por complejidad:

1. **REST APIs (más común)**
   - Client hace requests HTTP a endpoints del servidor
   - GET (leer), POST (crear), PUT/PATCH (actualizar), DELETE
   - Sincrónico: el cliente espera respuesta

2. **Webhooks (event-driven)**
   - El server envía data al cliente cuando ocurre un evento
   - Asincrónico: el cliente recibe notificaciones push
   - Ejemplo: "New lead en HubSpot → webhook → POST a tu servidor"

3. **GraphQL (queries flexibles)**
   - Cliente pide exactamente los datos que necesita
   - Un endpoint, múltiples queries
   - Ejemplo: Shopify, GitHub, Yelp APIs

4. **Batch/Bulk APIs**
   - Procesar múltiples records en un solo request
   - Ejemplo: HubSpot Batch API, Salesforce Bulk API

*Fuente: Postman, "MarTech Integration Patterns" (2023)*

### Authentication Patterns

Los tipos de auth en APIs de marketing:

1. **API Key (más simple)**
   - Header: `Authorization: Api-Key YOUR_KEY`
   - Ejemplo: SendGrid, Mailgun

2. **Bearer Token / OAuth2**
   - Header: `Authorization: Bearer YOUR_TOKEN`
   - Token expira, necesita refresh
   - Ejemplo: HubSpot, Salesforce

3. **HMAC Signature**
   - Firma criptográfica del request
   - Para validación de integridad
   - Ejemplo: Shopify webhooks

4. **Basic Auth (legacy)**
   - Header: `Authorization: Basic BASE64(USER:PASS)`
   - Cada vez menos usado por seguridad

*Fuente: Postman, "Authentication Guide" (2023)*

---

## 2. Frameworks y Metodologías

### Framework: Error Handling Patterns

Las APIs fallan. Una integración robusta maneja:

**1. Retries con exponential backoff:**
```javascript
retry {
  attempt = 1
  while (attempt <= max_retries) {
    try: call API
    success: return result
    catch (error):
      if (error is rate_limit or server_error):
        wait(2^attempt seconds) // 2s, 4s, 8s, 16s
        attempt++
      else:
        throw // no reintentar errores de cliente
  }
}
```

**2. Dead letter queue:**
- Requests que fallaron después de todos los retries
- Guardar para revisión manual o reprocesamiento

**3. Circuit breaker:**
- Si la API falla consistentemente, parar temporalmente
- Evita DDOS involuntario al vendor

*Fuente: Postman, "Error Handling" (2023)*

### Framework: Webhook Reliability

Los webhooks son notoriamente no confiables. Patrón para hacerlos robustos:

**Lado que recibe webhook (tu servidor):**
1. Recibir webhook → retornar 200 OK INMEDIATAMENTE (no procesar)
2. Guardar payload en DB con status = pending
3. Procesar async (background job)
4. Si falla procesamiento, reintentar según lógica de retry

**Lado que envía webhook (HubStripe, etc.):**
1. Enviar webhook con timeout de 5-10 segundos
2. Si no recibe 200, reintentar según política (typical: 3 reintentos en 15 minutos)
3. Si todos fallan, marcar como fallido y alertar

*Fuente: Postman, "Webhook Best Practices" (2023)*

### Framework: Rate Limiting Strategies

Todas las APIs tienen límites. Estrategias para manejar:

1. **Token bucket (más común)**
   - X requests por segundo, se recarga con el tiempo
   - HubSpot: 100 requests / 10 segundos

2. **Retry-After header**
   - Cuando la API responde con 429 (too many requests)
   - Header: `Retry-After: 60` → esperar 60 segundos

3. **Throttling client-side**
   - Cola local con workers que procesan a ritmo controlado
   - Usa Redis para coordinar si hay múltiples instancias

**Regla:** Nunca hacer requests ilimitados a una API externa.

*Fuente: Postman, "Rate Limiting" (2023)*

---

## 3. Modelos Mentales

### "La integración más simple es la que no se necesita"

Antes de integrar, preguntar: ¿Hay una forma de lograr el objetivo sin integración? A veces la respuesta sí (export/import manual, reporte compartido, proceso simple).

*Fuente: Postman, "Integration Philosophy" (2023)*

### "El sync eventual es inevitable"

Eventualmente, dos sistemas sincronizados divergirán. Uno tiene un dato, el otro tiene otro dato viejo. La estrategia de "source of truth" y reconciliation periódica es necesaria en cualquier integración compleja.

*Fuente: Postman, "Data Synchronization" (2023)*

---

## 4. Criterios de Decisión

### Build vs. Buy en integraciones

| Criterion | Buy (middleware) | Build (custom integration) |
|-----------|------------------|----------------------------|
| **Commodity integration** | Zapier, Make, Segment | No reinventar |
| **Complex logic** | Build | El middleware no soporta |
| **Data volume** | Build | Middleware tiene límites |
| **Speed to value** | Buy | Build toma más tiempo |
| **Control** | Build | Middleware es black box |

**Regla:** Start con buy (Zapier), move to build cuando scale lo justifica.

*Fuente: Postman, "Build vs Buy" (2023)*

---

## 5. Anti-patrones

### Anti-patrón: Ignorar paginación en APIs

Muchas APIs devuelven datos paginados (ej: HubSpot contacts, 100 por página). Si el código solo lee la primera página, pierde el 80%+ de los datos. Siempre iterar sobre todas las páginas.

*Fuente: Postman, "Pagination Pitfalls" (2023)*

### Anti-patrón: Hardcoded API keys en código

Las API keys deben estar en environment variables, no en el código. Si el código con hardcoded keys se comitea a GitHub, las keys están comprometidas.

*Fuente: Postman, "Security Best Practices" (2023)*

### Anti-patrón: No monitorear integraciones

Una integración que falla silenciosamente es peor que no tener integración. Logs, alertas (Slack/email cuando falla), y dashboards de health de integración son obligatorios.

*Fuente: Postman, "Monitoring Integrations" (2023)*
