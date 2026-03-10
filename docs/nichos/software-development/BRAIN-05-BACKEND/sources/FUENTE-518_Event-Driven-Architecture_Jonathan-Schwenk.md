---
source_id: "FUENTE-518"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Event-Driven Architecture: Designing Highly Scalable and Loosely Coupled Systems"
author: "Jonathan Schwenk, others"
expert_id: "EXP-518"
type: "article"
language: "en"
year: 2022
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from EDA best practices"
status: "active"
---

# Event-Driven Architecture

**Jonathan Schwenk, others**

## 1. Principios Fundamentales

> **P1 - Los eventos son hechos, no comandos**: Un evento es "algo que pasó" (OrderPlaced), no "haz esto" (PlaceOrder). Esta distinción es crucial. Los eventos son inmutables y almacenable. Los comandos son intenciones que pueden fallar. Diseñar con events, no commands.

> **P2 - El acoplamiento loose es la meta, no el side effect**: EDA desacopla productores de consumers. El productor no sabe quién consume el evento ni cuántos consumers hay. Este desacoplamiento permite escalar consumers independientemente, agregar nuevos consumers sin cambiar productores.

> **P3 - Los consumidores son idempotentes por diseño**: Un evento puede ser entregado múltiples veces (at-least-once delivery). El consumidor debe manejar duplicados gracefully. Idempotency (mismo evento procesado dos veces = mismo resultado que una vez) es no opcional.

> **P4 - El ordering de eventos es un problema difícil, no trivial**: "Event B occurred after Event A" no está garantizado en sistemas distribuidos. Si ordering es crítico, usa un secuencia ID o timestamp lógico. No asumas que los eventos llegarán en orden.

> **P5 - La saga pattern compensa la falta de ACID distribuido**: En EDA, no hay transacciones distribuidas. Una saga es una secuencia de transactions locales donde cada una compensa la anterior si algo falla. El eventual consistency es el tradeoff.

## 2. Frameworks y Metodologías

### Event Architecture Patterns

**1. Event Notification**
```
Producer → Event Bus → Consumer
```
Producer no espera respuesta. Fire-and-forget.

**2. Event-Carried State Transfer**
```
Producer → Event (with full state) → Consumer
```
Consumer tiene toda la data en el evento, no necesita hacer fetch al producer.

**3. Event Sourcing**
```
Event Store ← All events
    ↓
Project to Current State
```
El estado es derivado de eventos. No hay "update", solo "append event".

### Message Brokers

| Technology | Use Case | Trade-offs |
|-------------|----------|------------|
| **Kafka** | Event streaming, log storage | High throughput, complexity |
| **RabbitMQ** | Work queues, routing | Mature, many features |
| **AWS SNS/SQS** | Cloud-native, managed | Vendor lock-in |
| **Redis Streams** | Simple pub/sub, lightweight | Limited features, simple |

### Event Types

**Domain Events** (business events):
```typescript
{
  eventType: "OrderPlaced",
  eventId: "ord-123",
  timestamp: "2024-03-03T10:00:00Z",
  data: {
    orderId: "ord-123",
    customerId: "cust-456",
    items: [...],
    total: 99.99
  }
}
```

**Integration Events** (system boundaries):
```typescript
{
  eventType: "PaymentCompleted",
  eventId: "pay-789",
  timestamp: "2024-03-03T10:05:00Z",
  data: {
    paymentId: "pay-789",
    orderId: "ord-123",
    amount: 99.99,
    status: "COMPLETED"
  }
}
```

### Consumer Strategies

**Competing Consumers**:
```
┌──────────────┐
│  Event Queue │
└───────┬──────┘
        │
   ┌────┴────┐
   ↓    ↓    ↓
 C1   C2   C3
```
Cada evento va a un consumer. Load balancing.

**Fan-Out** (Publish-Subscribe):
```
┌──────────────┐
│   Exchange   │
└───┬────┬────┬┘
    ↓    ↓    ↓
  Q1   Q2   Q3
    ↓    ↓    ↓
   C1   C2   C3
```
Cada evento va a multiple queues/consumers.

### Saga Pattern

**Choreography** (decentralized):
```
OrderService → OrderCreated event
    ↓
PaymentService → OrderPaid event
    ↓
ShippingService → OrderShipped event
```
Cada service escucha y reacciona. No orquestador central.

**Orchestration** (centralized):
```
OrderOrchestrator
    ↓ commands
    ↓
    ↓
    ↓
Compensating actions if any step fails
```
Orquestador coordena, maneja failure scenarios.

## 3. Modelos Mentales

### Modelo de "At-Least-Once Delivery"

```
Producer → Message Broker → Consumer
                ↑
                └──────┐
                 Retry on failure
```

**Guarantee**: Cada evento será entregado al menos una vez.
**Implication**: Consumers deben ser idempotent.

### Modelo de "Eventual Consistency"

```
Service A (state changed) → Event → Service B (updates)
                                      ↓
                                Temporary inconsistency
                                      ↓
                                Eventually consistent
```

**Trade-off**: Availability over consistency (CAP theorem).

### Modelo de "CQRS" (Command Query Responsibility Segregation)

```
Write Model (Commands)     Read Model (Queries)
    ↓                           ↓
Event Store              Projections → Read DB
    ↓                           ↓
Events → Projections          Queries
```

**Benefits**:
- Optimize reads y writes independently
- Scale reads y writes separately
- Complex queries sin affecting writes

### Modelo de "Versioned Events"

```typescript
// Version 1
{
  eventType: "OrderPlaced",
  version: 1,
  data: {
    orderId: "ord-123",
    customerId: "cust-456"
  }
}

// Version 2 (added field)
{
  eventType: "OrderPlaced",
  version: 2,
  data: {
    orderId: "ord-123",
    customerId: "cust-456",
    promotionCode: "SAVE10"  // New field
  }
}
```

**Consumers handle multiple versions gracefully.**

## 4. Criterios de Decisión

### When to Use EDA

| ✅ EDA ideal para | ❌ No uses EDA |
|--------------------|----------------|
| Loosely coupled services | Tightly coupled monolith |
| Asynchronous processing | Synchronous user requests |
- High scalability needs | Simple request/response |
| Event-driven workflows | Simple CRUD operations |
| Multiple consumers per event | One consumer per event |

### Message Ordering

| Ordered | Unordered |
|---------|------------|
| Kafka (per partition) | Kafka (across partitions) |
| SQS FIFO queue | SQS standard queue |
| Required for business logic | Most cases |

**If ordering needed**: Use sequence IDs or logical timestamps.

### Delivery Guarantees

| Guarantee | Use Case |
|-----------|----------|
| **At-most-once** | Duplicate acceptable, speed critical |
| **At-least-once** | No data loss, duplicates OK |
| **Exactly-once** | Critical financial data (complex to implement) |

**Most systems**: At-least-once with idempotent consumers.

### Backpressure Strategies

| Strategy | Description | When to use |
|----------|-------------|-------------|
| **Drop** | Discard messages | Non-critical events |
| **Buffer** | Queue messages temporarily | High throughput, can delay |
| **Rate limit** | Slow down producer | Consumer overload |
| **Scale up** | Add consumers | Auto-scaling infrastructure |

## 5. Anti-patrones

### Anti-patrón: "Commands as Events"

```
❌ "PlaceOrder" event
✅ "OrderPlaced" event
```

**Why**: Commands can fail, events are facts.

### Anti-patrón: "Tight Coupling via Events"

**Problema**: Consumer knows too much about producer schema.

**Solución**:
- Version events
- Anti-corruption layer
- Consumer uses only needed fields

### Anti-patrón: "Ignoring Failure Handling"

**Problema**: No compensation when saga step fails.

**Solución**:
- Define compensating transactions
- Implement saga manager
- Dead letter queue for failed events

### Anti-patrón: "Over-Engineering"

**Problema**: EDA for simple request/response.

**Solución**:
- Use direct API calls for simple sync operations
- EDA for async, multi-consumer scenarios
- Complexity should be justified

### Anti-patrón: "Ignoring Idempotency"

**Problema**: Consumer processes duplicate events multiple times.

**Solución**:
```typescript
function handleEvent(event) {
  if (alreadyProcessed(event.eventId)) {
    return;  // Idempotent
  }
  // Process event
  markAsProcessed(event.eventId);
}
```

### Anti-patrón: "Event God Object"

**Problema**: One giant event type for everything.

**Solución**:
- Specific event types (OrderPlaced, OrderPaid, OrderShipped)
- Smaller, focused events
- Version events independently

### Anti-patrón: "No Monitoring/Observability"

**Problema**: No visibility into event flow.

**Solución**:
- Trace events (correlation IDs)
- Monitor consumer lag
- Alert on dead letter queue growth
- Dashboard event throughput

### Anti-patrón: "Ignoring Schema Evolution"

**Problema**: Breaking changes in event schema break consumers.

**Solución**:
- Version events
- Add fields, never remove
- Support multiple versions in consumers
- Communicate breaking changes
