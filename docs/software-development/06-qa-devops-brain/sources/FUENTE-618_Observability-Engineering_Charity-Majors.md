---
source_id: "FUENTE-618"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "Observability Engineering: Achieving Excellence in Production"
author: "Charity Majors, Liz Fong-Jones, George Miranda"
expert_id: "EXP-618"
type: "book"
language: "en"
year: 2020
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Observability Engineering"
status: "active"
---

# Observability Engineering

**Charity Majors, Liz Fong-Jones, George Miranda**

## 1. Principios Fundamentales

> **P1 - Logs, metrics, y traces son las tres columnas de la observabilidad**: Los logs dicen "qué pasó", los metrics dicen "cuánto pasó", los traces dicen "dónde pasó". Necesitas los tres para entender tu sistema. No es uno u otro, es los tres juntos.

> **P2 - La observabilidad debe ser everywhere, no un afterthought**: No instrumentes tu aplicación en producción cuando ya hay un problema. Observabilidad es built-in desde el inicio. Código sin observabilidad es código no maintainable.

> **P3 - El debugging de sistemas distribuidos es imposible sin distributed tracing**: En un microservicios architecture, un request atraviesa 10+ servicios. Sin tracing correlacionando el request a través de todos los servicios, debugging es nightmare.

> **P4 - Las alertas deben ser actionable, no noise**: Cada alerta debe indicar acción específica. "CPU is high" no es actionable. "API latency p99 > 500ms for Checkout flow" es actionable. Noise mata alert fatigue, que mata响应速度。

> **P5 - La observabilidad habilita el self-service debugging**: Si un usuario tiene un problema, tú deberías poder ver qué pasó sin pedir al usuario que reproduzca. Observabilidad = post-mortem analysis sin reproducción manual.

## 2. Frameworks y Metodologías

### The Three Pillars

**1. Structured Logging**
```json
{
  "timestamp": "2024-03-03T10:00:00Z",
  "level": "info",
  "service": "orders-api",
  "trace_id": "abc123",
  "span_id": "def456",
  "user_id": "user-789",
  "message": "Order created",
  "order_id": "ord-123",
  "total": 99.99
}
```

**Best practices**:
- Machine parseable (JSON)
- Structured fields (no text parsing)
- Correlation IDs (trace_id, span_id)
- Log levels appropriately (error, warn, info, debug)

**2. Metrics**
```
Counter: Number of orders created
Gauge: Current number of active connections
Histogram: Request latency distribution
Summary: Response time percentiles (p50, p95, p99)
```

**Key metrics**:
- **RED method**: Rate (requests/sec), Errors (error rate), Duration (latency)
- **Golden signals**: Latency, Traffic, Errors, Saturation

**3. Tracing**
```
Request → Service A → Service B → Service C
    ↓         ↓          ↓          ↓
  Trace A   Span A1    Span B1    Span C1
            ↓          ↓          ↓
          Span A2    Span B2
```

**Distributed tracing**: Trace ID correlates all spans across services.

## 3. Modelos Mentales

### Modelo de "Debuggability"

```
Debuggability = Logs + Metrics + Traces + Context
```

**Without observability**: "It's broken" → Reproduce in dev → Find bug → Fix (hours/days)
**With observability**: "It's broken" → Check trace → Find exact line → Fix (minutes)

## 4. Criterios de Decisión

### Tool Selection

| Open Source | Commercial | Managed |
|-------------|-----------|---------|
| Prometheus + Grafana | Datadog | AWS CloudWatch |
| Jaeger | Honeycomb | Google Cloud Operations |

## 5. Anti-patrones

### Anti-patrón: "Unstructured Logs"
```
❌ [INFO] 2024-03-03 Order created for user 123
✅ {"level": "info", "event": "order_created", "user_id": "123"}
```
