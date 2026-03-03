---
source_id: "FUENTE-511"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Microservices Patterns: With examples in Java"
author: "Chris Richardson"
expert_id: "EXP-511"
type: "book"
language: "en"
year: 2018
distillation_date: "2026-03-02"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-02"
changelog:
  - version: "1.0.0"
    date: "2026-03-02"
    changes:
      - "Destilación inicial completa"
status: "active"
---

# Microservices Patterns

## 1. Principios Fundamentales

> **P1: Database per Service** - Cada servicio debe tener su propia base de datos, eliminando shared databases.

> **P2: API Gateway Pattern** - Un único entry point para todos los clientes, simplificando la arquitectura y centralizando cross-cutting concerns.

> **P3: Asynchronous Communication** - Los servicios deben comunicarse de forma asíncrona usando eventos/mensajes siempre que sea posible.

> **P4: Definir boundaries cuidadosamente** - Los microservices no son sobre dividir todo arbitrariamente; cada servicio debe ser autónomo y enfocado en un business capability.

## 2. Frameworks y Metodologías

### Core Patterns

**1. Decomposition Patterns**
- **Decompose by Business Capability**: Identificar capabilities del negocio (ej: Order Management, Inventory, Shipping)
- **Decompose by Subdomain**: DDD - bounded contexts como límites de servicios
- **Database per Service**: Cada servicio tiene su DB propia (no shared schema)

**2. Communication Patterns**
- **API Gateway**: Single entry point, routing, rate limiting, authentication
- **Service Mesh**: Sidecar proxy para inter-service communication (Istio, Linkerd)
- **Event-Driven**: Publicar eventos para cambios de estado (Kafka, RabbitMQ)

**3. Data Management Patterns**
- **Saga Pattern**: Manejar transacciones distribuidas
  - Choreography: Eventos coordinan sin orchestrator central
  - Orchestration: Saga orchestrator coordina explícitamente
- **CQRS**: Command Query Responsibility Segregation
- **Event Sourcing**: Store events como source of truth

## 3. Modelos Mentales

**Autonomous Services**
- Cada equipo owns un service de principio a fin
- Deploy independently
- Different tech stack por servicio si hace sentido
- Failure isolation - un servicio roto no debe derrumbar todo

**CAP Trade-offs**
- **CA (Consistency + Availability)**: RDBMS con replication, xACID
- **CP (Consistency + Partition Tolerance)**: Distributed transactions, eventual consistency
- **AP (Availability + Partition Tolerance)**: Eventual consistency, DNS, DynamoDB

**The Fallacies of Distributed Computing**
1. The network is reliable
2. Latency is zero
3. Bandwidth is infinite
4. The network is secure
5. Topology doesn't change
6. There is one administrator
7. Transport cost is zero
8. The network is homogeneous

## 4. Criterios de Decisión

### Monolith vs Microservices

| Factor | Monolith | Microservices |
|--------|----------|---------------|
| Team size | < 5-10 devs | > 10 devs, multiple teams |
| Deployment frequency | Low (mensual) | High (diario/semanal) |
| Complexity | Moderate | Alta (distribuido) |
| Organizational | One team | Multi-team, autonomous squads |
| Scalability needs | Predictable | Unpredictable, bursty |

### Database per Service Anti-patterns
❌ **Shared Database**: Proporciona ACID pero pierdes autonomy
✅ **Database per Service**: Autonomy total pero necesitas Sagas para transactions

### When to Use Microservices
✅ Cuando múltiples equipos trabajando en diferentes domains
✅ Cuando necesitas escalabilidad independiente por servicio
✅ Cuando diferentes domains tienen diferentes requisitos de tech stack
✅ Cuando quieres isolación de fallos

❌ Solo por hype o sin haber evaluado trade-offs
❌ Cuando el team es pequeño y la organización no está preparada
❌ Cuando el sistema no tiene complejidad que justifique overhead

## 5. Anti-patrones

❌ **Nanoservices** - Servicios tan pequeños que overhead supera beneficios. Límite práctico: servicios que pueden ser manejados por un equipo pequeño (2-8 personas).

❌ **Shared Libraries sin disciplina** - Usar shared libraries para logic que cambia frecuentemente acopla servicios y pierdes benefits de microservices.

❌ **Synchronous communication everywhere** - Si todos los servicios se llaman sincrónicamente, no tienes isolation de fallos. Usa async events.

❌ **Distributed monolith** - Servicios que comparten tanto código/base de datos que son un monolith distribuido. Mejor un monolith real.

❌ **Ignoring operations overhead** - Microservices agregan complejidad de deployment, monitoring, debugging, testing. No es free.

## Implementation Patterns

### API Gateway Responsibilities
```yaml
routing:
  - Route requests to appropriate service
  - Version API (v1, v2)
  - Canary deployments

cross_cutting:
  - Authentication & authorization
  - Rate limiting
  - SSL termination
  - Logging & monitoring
  - Request/response transformation
```

### Saga Pattern Example
```yaml
scenario: "Place Order"

services:
  - Order Service
  - Payment Service
  - Inventory Service
  - Shipping Service

orchestration:
  step_1:
    service: Order
    action: create_order
  step_2:
    service: Payment
    action: authorize_payment
    compensating: refund_payment
  step_3:
    service: Inventory
    action: reserve_inventory
    compensating: release_inventory
  step_4:
    service: Shipping
    action: schedule_shipment
    compensating: cancel_shipment
```

### Service Mesh Benefits
- Traffic management (routing, load balancing)
- Service identity and security (mTLS)
- Observability (tracing, metrics)
- Resilience (timeouts, retries, circuit breakers)
- WITHOUT changing application code

## Testing Strategy

**Unit Tests**: Dentro de cada service

**Contract Tests**: Verificar que service A cumple con contract que service B espera (Pact)

**Consumer-Driven Contract Testing**:
- Consumer define test expectations
- Provider verifica que cumple expectations
- Evita breaking changes en producción

**Integration Tests**: Test inter-service communication con mocks o test containers

**End-to-End Tests**: Test critical user journeys, pero mantener mínimo (costosos, frágiles)

## References

- **Building Microservices** (Sam Newman)
- **Microservices Patterns** (Chris Richardson)
- **Domain-Driven Design** (Eric Evans) - Bounded Contexts
- **Release It!** (Michael Nygard) - Production patterns
---
source_id: "FUENTE-511"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Microservices Patterns: With examples in Java"
author: "Chris Richardson"
expert_id: "EXP-511"
type: "book"
language: "en"
year: 2018
distillation_date: "2026-03-02"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-02"
changelog:
  - version: "1.0.0"
    date: "2026-03-02"
    changes:
      - "Destilación inicial completa"
status: "active"
---
