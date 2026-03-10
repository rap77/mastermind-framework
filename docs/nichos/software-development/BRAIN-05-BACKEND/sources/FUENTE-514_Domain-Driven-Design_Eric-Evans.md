---
source_id: "FUENTE-514"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Domain-Driven Design: Tackling Complexity in the Heart of Software"
author: "Eric Evans"
expert_id: "EXP-514"
type: "book"
language: "en"
year: 2003
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from DDD book"
status: "active"
---

# Domain-Driven Design

**Eric Evans**

## 1. Principios Fundamentales

> **P1 - El dominio es el corazón del software**: La complejidad del software está en el dominio, no en la tecnología. Si no entiendes el dominio, estás construyendo cáscara sin sustancia.

> **P2 - El lenguaje ubicuo es la llave**: Developers y domain experts deben hablar el mismo lenguaje. El código debe leerse como el lenguaje del dominio. Si hay traducción mental entre "lo que dice el negocio" y "lo que dice el código", hay un problema.

> **P3 - Los modelos no son diagramas, son código**: Un modelo UML que no se ejecuta es fantasía. El modelo vivo es el código. Los diagramas pueden ayudar, pero el modelo real es el que corre.

> **P4 - Los bounded contexts son fronteras necesarias**: No intentes modelar el todo. Divide el dominio en contexts con límites claros. Dentro de cada bounded context, el modelo es consistente. Entre contexts, hay traducción.

> **P5 - El diseño evolutivo es la única constante**: El modelo no se descubre en un taller y se implementa. El modelo emerge del diálogo continuo entre developers, domain experts, y el código que se ejecuta.

## 2. Frameworks y Metodologías

### Strategic DDD

**Bounded Context** (BC):
- Frontera donde un modelo particular se aplica
- Dentro del BC: términos consistentes, reglas consistentes
- Entre BCs: integración mediante anticorruption layer

**Core Domain**:
- La parte del dominio que es diferencial competitiva
- Recursos aquí: mejores developers, mayor inversión
- Ejemplo: En Amazon, recomendaciones es core. Checkout es supporting (commodity).

**Supporting Domains**:
- Necesarios pero no diferenciadores
- Buy/build/outsource decisions aplican aquí
- Ejemplo: Autenticación, facturación, reporting

**Generic Domains**:
- Soluciones commodity que todos tienen
- SaaS, open source, libraries
- Ejemplo: User management, file storage

### Tactical DDD (Building Blocks)

**1. Entity**
```typescript
// Tiene identidad, no igualdad por valor
class User {
  id: UserId;  // Identificador único
  name: string;
  email: Email;

  equals(other: User): boolean {
    return this.id.equals(other.id);  // Igualdad por ID
  }
}
```

**2. Value Object**
```typescript
// Sin identidad, igualdad por valor
class Email {
  value: string;

  constructor(value: string) {
    if (!this.isValid(value)) throw new InvalidEmailError(value);
    this.value = value;
  }

  isValid(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  equals(other: Email): boolean {
    return this.value === other.value;  // Igualdad por valor
  }
}
```

**3. Aggregate**
```typescript
// Consistency boundary. Una raíz, muchas entidades.
class Order {
  // Aggregate Root
  id: OrderId;
  items: OrderItem[];
  status: OrderStatus;
  customerId: CustomerId;

  addItem(product: Product, quantity: number): void {
    // Invariant: cannot add items to shipped order
    if (this.status !== OrderStatus.DRAFT) {
      throw new InvalidOperationError("Cannot modify shipped order");
    }
    this.items.push(new OrderItem(product, quantity));
  }

  ship(): void {
    // Invariant: cannot ship empty order
    if (this.items.length === 0) {
      throw new InvalidOperationError("Cannot ship empty order");
    }
    this.status = OrderStatus.SHIPPED;
  }
}
```

**4. Repository**
```typescript
// Colección-like interface para aggregates
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
  findByCustomer(customerId: CustomerId): Promise<Order[]>;
}
```

**5. Domain Service**
```typescript
// Operación que no pertenece naturalmente a una entidad
class DomainTransferService {
  transfer(from: Account, to: Account, amount: Money): void {
    // Business rule que involucra múltiples aggregates
    from.withdraw(amount);
    to.deposit(amount);
    // Event publication, audit, etc.
  }
}
```

**6. Domain Event**
```typescript
// Algo que pasó en el dominio, relevante para otros bounded contexts
class OrderShipped {
  orderId: OrderId;
  shippedAt: Date;
  shippingAddress: Address;
}
```

### Context Mapping

| Relationship | Description | Example |
|--------------|-------------|---------|
| **Partnership** | BCs alineados, colaboran | Sales + Marketing teams |
| **Shared Kernel** | BCs comparten modelo mínimo | Common entities like Customer |
| **Customer-Supplier** | Upstream defines, downstream consumes | Pricing → Orders |
| **Conformist** | Downstream adopta upstream model | Orders adopts Shipping model |
| **Anti-Corruption Layer** | Traduce entre modelos diferentes | External API → Internal model |
| **Open Host Service** | BC publica protocolo público | REST API para otros |
| **Published Language** | Doc de traducción entre BCs | Swagger, documentation |

### The Lifecycle of a Domain Object

```
1. AGGREGATE CREATION
   Factory creates new aggregate root
   (e.g., OrderFactory.createOrder(customerId))

2. REPOSITORY RETRIEVAL
   Repository reconstitutes aggregate from persistence
   (e.g., orderRepository.findById(orderId))

3. DOMAIN LOGIC EXECUTION
   Methods executed on aggregate root
   (e.g., order.addItem(product, quantity))

4. PERSISTENCE
   Repository saves aggregate state
   (e.g., orderRepository.save(order))

5. EVENT PUBLICATION
   Domain events emitted to other BCs
   (e.g., OrderCreated event published)
```

## 3. Modelos Mentales

### Modelo de "Ubiquitous Language"

**Without Ubiquitous Language**:
- Business: "Customer places order"
- Dev: "User creates order record"
- DBA: "Insert row into orders table"

**With Ubiquitous Language**:
- All: "Customer places Order"

**En código**:
```typescript
// NO: OrderService.createUserOrderRecord(userId, productId)
// YES: Order.place(customerId, productId)
```

### Modelo de "Strategic Distillation"

```
Todo el dominio
    ↓
Core Domain (10-20%) ← Invertir aquí
Supporting Domain (60-70%) → Automatizar, externalizar
Generic Domain (10-20%) → Comprar, no construir
```

**Regla**: Si todos tienen el mismo problema, no es tu core domain.

### Modelo de "Aggregate as Consistency Boundary"

**Dentro de un aggregate**: Consistencia transaccional
**Entre aggregates**: Consistencia eventual

**Ejemplo**:
- Order y OrderItem están en el mismo aggregate (consistencia fuerte)
- Order y Customer son aggregates diferentes (consistencia eventual)

**Why**: Distribuir transacciones mata performance. Mantén aggregates pequeños.

### Modelo de "Layered Architecture"

```
┌────────────────────────────────────┐
│  UI Layer                         │ ← Thin, delega a Application
│  (Controllers, Presenters)         │
├────────────────────────────────────┤
│  Application Layer                │ ← Orchestration, no business logic
│  (Use cases, commands)             │
├────────────────────────────────────┤
│  Domain Layer                     │ ← Core business logic
│  (Entities, Value Objects, Services)│
├────────────────────────────────────┤
│  Infrastructure Layer             │ ← External concerns
│  (DB, API, File system)            │
└────────────────────────────────────┘
```

**Dependency rule**: Outer layers depend on inner layers. Never reverse.

## 4. Criterios de Decisión

### When to Apply DDD

| ✅ DDD cuando | ❌ No usar DDD cuando |
|---------------|---------------------|
| Dominio complejo, no trivial | CRUD simple |
| Reglas de negocio significativas | Solo validaciones de formato |
- Equipo con domain knowledge | Solo technical requirements
| Largo plazo (años de evolución) | Corto plazo (throwaway prototype)
| Colaboración con domain experts | Solo developers en el proyecto

### Aggregate Sizing

| Muy pequeño | Ideal | Muy grande |
|-------------|-------|-------------|
| < 3 entidades | 3-7 entidades | > 10 entidades |
| Demasiados aggregates | Manejable | Monolith within monolith |
| Over-engineering | Balance | Performance issues |

**Regla empírica**: 1 aggregate = 1-3 entidades + value objects

### Entity vs Value Object

| Entity | Value Object |
|--------|--------------|
| Tiene identidad | Sin identidad |
| Igualdad por ID | Igualdad por valor |
| Mutable (generalmente) | Inmutable (idealmente) |
| Ejemplo: User, Order | Ejemplo: Email, Money, Address |

**Cuándo cambiar de Entity a VO**:
- Si no importa "cuál", solo "qué"
- Si no hay lifecycle propio
- Si puede ser shared y cached

### Repository vs DAO

| Repository | DAO (Data Access Object) |
|------------|-------------------------|
| Domain-centric | Data-centric |
| Trabaja con aggregates | Trabaja con tablas/records |
| Oculta persistencia del dominio | Expone estructura de datos |
| 1 repo por aggregate root | 1 DAO por tabla |

**DDD**: Usa Repositories para aggregates. DAOs son un anti-pattern en DDD.

### Domain Service vs Application Service

| Domain Service | Application Service |
|----------------|--------------------|
| Lógica de dominio | Orchestration |
| Pertenece al dominio | Coordina use cases |
| No tiene estado | No tiene lógica de dominio |
| Ejemplo: Transfer funds | Ejemplo: CreateOrderUseCase |

**Regla**: Si la operación es un verbo del dominio, es Domain Service. Si es un use case, es Application Service.

## 5. Anti-patrones

### Anti-patrón: "Anemic Domain Model"

**Problema**: Entidades vacías, lógica en services.

```typescript
// ❌ ANEMIC
class Order {
  id: string;
  items: OrderItem[];
  // No methods, just getters/setters
}

class OrderService {
  addItem(order: Order, item: OrderItem) {  // Lógica fuera
    order.items.push(item);
  }
}
```

**Solución**:
```typescript
// ✅ RICH DOMAIN MODEL
class Order {
  addItem(item: OrderItem) {  // Lógica dentro
    if (this.status !== OrderStatus.DRAFT) {
      throw new Error("Cannot modify shipped order");
    }
    this.items.push(item);
  }
}
```

### Anti-patrón: "Everything is an Aggregate"

**Problema**: Crear aggregates para todo, incluso entidades simples.

**Solución**:
- Entities existen solo dentro de aggregates
- No crees aggregates para trivial CRUD
- Value Objects preferidos sobre Entities cuando sea posible

### Anti-patrón: "Big Ball of Mud"

**Problema**: Sin bounded contexts, todo mezclado.

**Solución**:
- Identifica bounded contexts
- Crea anticorruption layers entre contexts
- Usa context mapping para definir relaciones

### Anti-patrón: "Database-Driven Design"

**Problema**: El modelo del dominio refleja la estructura de la DB.

**Solución**:
- Domain model ≠ Database schema
- Usa repositories para abstraer persistencia
- ORM mapea entre ambos mundos

### Anti-patrón: "No Ubiquitous Language"

**Problema**: Developers hablan "tech", domain experts hablan "business".

**Solución**:
- Crea glossary compartido
- Code uses domain terms, not tech terms
- Diagramas y docs use same language

### Anti-patrón: "Ignorando Core Domain"

**Problema**: Tratar todo el dominio igual.

**Solución**:
- Identifica tu core domain
- Invierte más recursos ahí
- Externaliza supporting/generic domains

### Anti-patrón: "Fantasy Modeling"

**Problema**: Modelar el "perfect" domain sin feedback de experts.

**Solución**:
- Modelo emerge de diálogo
- Prototipa y valida con domain experts
- El código es parte del modelado process

### Anti-patrón: "God Aggregate"

**Problema**: Aggregate con 20+ entities, miles de líneas.

**Solución**:
- Divide en múltiples aggregates
- Usa domain events para consistency eventual
- Mantén aggregates pequeños por performance

### Anti-patrón: "Service Layer as Domain Layer"

**Problema**: Toda la lógica en "Services", el dominio es DTOs.

**Solución**:
- Rich domain model, not anemic
- Behavior donde pertenece (entities/VOs)
- Services solo para operaciones que no pertenecen a entidades
