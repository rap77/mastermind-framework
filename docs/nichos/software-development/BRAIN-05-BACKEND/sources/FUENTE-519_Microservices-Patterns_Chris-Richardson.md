---
source_id: "FUENTE-519"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Microservices Patterns: With Examples in Java"
author: "Chris Richardson"
expert_id: "EXP-519"
type: "book"
language: "en"
year: 2018
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Microservices Patterns"
status: "active"
---

# Microservices Patterns

**Chris Richardson**

## 1. Principios Fundamentales

> **P1 - Los microservicios son sobre organisational boundaries, no tecnología**: La razón principal para microservicios es alinear arquitectura con estructura de equipos (Conway's Law). Si tu organización no está estructurada para equipos pequeños y cross-funcionales, los microservicios no traerán beneficios.

> **P2 - Cada microservicio tiene su propia base de datos**: No compartas DB entre microservicios. La shared database es el anti-patrón más común y más destructivo. Si dos servicios comparten una DB, no son microservicios, son módulos disfrazados.

> **P3 - La comunicación entre servicios es vía APIs bien definidas**: Los servicios se comunican vía HTTP/REST, gRPC, o message brokers. La API es el contract, y debe ser versionado y estable. Breaking changes deben evitarse o ser gestionadas cuidadosamente.

> **P4 - La descentralización governance es clave**: No hay "architecture team" que dicte tecnología. Cada team elige su stack (tecnología, database, framework). El rol central es definir principios y patterns comunes, no implementar.

> **P5 - La resiliencia es un requerimiento, no un afterthought**: En sistemas distribuidos, las fallas son normales. Los servicios deben diseñarse para fallas gracefully: circuit breakers, retries, timeouts, fallbacks. Un servicio failing no debe cascade fallar todo el sistema.

## 2. Frameworks y Metodologías

### Microservice Architecture

```
┌─────────────────────────────────────────────────┐
│  API Gateway                                    │
│  (Authentication, rate limiting, routing)       │
└───────┬────────────┬────────────┬──────────────┘
        ↓            ↓            ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Service A   │ │ Service B   │ │ Service C   │
│ + Database  │ │ + Database  │ │ + Database  │
└─────────────┘ └─────────────┘ └─────────────┘
        ↓            ↓            ↓
        └────────────┴────────────┘
                     ↓
            ┌──────────────┐
            │ Message Bus  │
            │ (async comms)│
            └──────────────┘
```

### Key Patterns

**1. Service Discovery**
```
Service Registry → All services register
    ↓
Client queries registry for service location
    ↓
Client calls service
```
- **Client-side discovery**: Client asks registry, calls service
- **Server-side discovery**: Client calls API gateway, gateway routes

**2. API Gateway Pattern**
```
External Client
    ↓
API Gateway (single entry point)
    ↓
    ├→ Service A
    ├→ Service B
    └→ Service C
```
**Responsibilities**:
- Authentication/authorization
- Rate limiting
- Request routing
- Response aggregation
- Protocol translation

**3. Circuit Breaker Pattern**
```
┌─────────────────────────────────────────┐
│  CLOSED (normal)                        │
│  Requests pass through                  │
│  If failures > threshold → OPEN        │
└─────────────────────────────────────────┘
              ↓ (too many failures)
┌─────────────────────────────────────────┐
│  OPEN (failing fast)                    │
│  Requests fail immediately              │
│  After timeout → HALF_OPEN              │
└─────────────────────────────────────────┘
              ↓ (timeout)
┌─────────────────────────────────────────┐
│  HALF_OPEN (testing)                    │
│  Allow one request through              │
│  Success → CLOSED, Failure → OPEN       │
└─────────────────────────────────────────┘
```

**4. Saga Pattern** (for distributed transactions)
```
Orchestration Saga:
1. Book flight
2. Book car (if flight booked)
3. Book hotel (if car booked)

If any step fails:
   Compensating actions (cancel flight, car, hotel)
```

**5. Event-Driven Architecture**
```
Service A → Event → Message Bus
                        ↓
                ┌───────┴───────┐
                ↓               ↓
            Service B      Service C
```

### Decomposition Strategies

**By Business Capability**:
- Order Service (manages orders)
- Inventory Service (manages inventory)
- Shipping Service (manages shipping)

**By Data** (DDD Bounded Contexts):
- Each service owns its data
- No shared databases
- Data accessed via API only

**By Team Structure**:
- One team per service (2-pizza team: 6-10 people)
- Team owns service end-to-end (dev, ops, support)

## 3. Modelos Mentales

### Modelo de "Distributed Monolith"

**Anti-pattern**: Microservices that communicate heavily, tightly coupled.

```
Service A → heavily calls Service B → heavily calls Service C
```

**Signs**:
- Deployment requires coordinating multiple services
- Change in one service requires changes in others
- High network latency between services

**Solution**: Re-evaluate service boundaries.

### Modelo de "CAP Theorem Trade-offs**

```
┌─────────────────────────────────────────┐
│           Consistency                   │
│                  &                      │
│              Availability                │
│              (Pick two)                 │
│              &                          │
│           Partition Tolerance            │
└─────────────────────────────────────────┘
```

**Microservices**: Choose AP (Availability + Partition tolerance), accept eventual consistency.

### Modelo de "Service Mesh"

```
┌─────────────────────────────────────────┐
│  Service Mesh (sidecar proxy)           │
│  - Service discovery                     │
│  - Load balancing                       │
│  - Circuit breaking                      │
│  - Observability                        │
└─────────────────────────────────────────┘
            ↑
        ┌───┴───┬─────────┬─────────┐
        ↓       ↓         ↓         ↓
    Service A  Service B  Service C  Service D
```

**Examples**: Istio, Linkerd, Consul Connect.

### Modelo de "Database per Service"

```
Service A     Service B     Service C
    ↓             ↓             ↓
  DB A          DB B          DB C
```

**Benefits**:
- Loose coupling
- Independent scaling
- Technology diversity (Postgres, Mongo, Redis)

**Challenges**:
- Distributed transactions (use saga)
- Data consistency (eventual)
- Cross-service queries (API composition)

## 4. Criterios de Decisión

### Monolith vs Microservices

| Monolith | Microservices |
|----------|----------------|
| Simpler deployment | Complex deployment |
| Easier debugging | Distributed tracing required |
| Technology lock-in | Technology diversity |
| Good for small teams | Good for large organizations |
| Good for simple domains | Good for complex domains |

**Rule**: Start with monolith, decompose when organization scales.

### Service Boundaries: How Big?

| Too small | Just right | Too large |
|-----------|-----------|-----------|
| < 100 LOC | 1000-5000 LOC | > 10000 LOC |
| One feature | Multiple related features | Entire business domain |
| Chatty with others | Independent with minimal comms | Monolith in disguise |

**Guideline**: One service per bounded context (DDD).

### Communication: Sync vs Async

| Synchronous (HTTP) | Asynchronous (Events) |
|---------------------|------------------------|
| Simple request/response | Decoupled producers/consumers |
| Tight coupling | Loose coupling |
| Immediate response required | Eventual consistency OK |
| Easy to debug | Complex debugging |

**Default**: Sync for reads, async for writes/notifications.

### Deployment Strategies

| Strategy | Description | When to use |
|----------|-------------|-------------|
| **Multiple Service Instances** | N instances per service | Always |
| **Blue-Green Deployment** | Switch traffic between versions | Zero downtime required |
| **Canary Deployment** | Roll out to subset of users | High risk changes |
| **Shadow Deployment** | Deploy alongside, not receiving traffic | Testing production load |

## 5. Anti-patrones

### Anti-patrón: "Shared Database"

```
❌ Service A ──┐
              ├─ Shared Database
❌ Service B ──┘
```

**Problems**:
- Tight coupling (schema changes affect both)
- Single point of failure
- Can't scale independently

**Solution**: Database per service.

### Anti-patrón: "Distributed Transactions"

```
❌ 2PC across services
```

**Problems**:
- Locks resources across services
- Slow, fragile, not scalable

**Solution**: Saga pattern with eventual consistency.

### Anti-patrón: "Fine-Grained Services"

```
❌ Service per class/module
```

**Problems**:
- Network latency overhead
- Deployment complexity
- Debugging nightmare

**Solution**: Service per bounded context, not per class.

### Anti-patrón: "Ignoring Observability"

**Problema**: No distributed tracing, logging, metrics.

**Solution**:
- Distributed tracing (OpenTelemetry, Jaeger)
- Centralized logging (ELK, Splunk)
- Metrics per service (Prometheus, Grafana)

### Anti-patrón: "Synchronous Communication Chains"

```
❌ A calls B, B calls C, C calls D
```

**Problems**:
- Latency compounds
- Failure cascades
- Unpredictable performance

**Solution**: Async events for chains, limit sync depth to 2-3 hops.

### Anti-patrón: "No Versioning of APIs"

```
❌ Breaking changes without versioning
```

**Solution**:
- Version APIs (/v1/, /v2/)
- Deprecate old versions gracefully
- Never break without notice

### Anti-patrón: "Ignoring Failure Modes"

```
❌ No retries, no circuit breakers, no fallbacks
```

**Solution**:
- Circuit breakers for external calls
- Retry with exponential backoff
- Fallback to default/cache/error
- Timeout on all external calls

### Anti-patrón: "Service Proliferation"

```
❌ Creating new service for every feature
```

**Solution**:
- Start with monolith modulaire
- Extract services when organisational boundaries emerge
- One service per team (2-pizza rule)

### Anti-patrón: "Neglecting Data Consistency"

```
❌ No strategy for eventual consistency
```

**Solution**:
- Define consistency requirements per use case
- Use sagas for distributed transactions
- Monitor consistency violations
