---
source_id: "FUENTE-517"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Database Design and Relational Theory: Normal Forms and All That Jazz"
author: "C.J. Date"
expert_id: "EXP-517"
type: "book"
language: "en"
year: 2012
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Database Design and Relational Theory"
status: "active"
---

# Database Design and Relational Theory

**C.J. Date**

## 1. Principios Fundamentales

> **P1 - La normalización no es una regla arbitraria, es una ley matemática**: Las formas normales (1NF, 2NF, 3NF, BCNF) no son "best practices" que alguien inventó. Son derivaciones lógicas de la teoría relacional que garantizan integridad de datos y eliminan anomalías. Romper las reglas tiene consecuencias predecibles.

> **P2 - Una cosa, un lugar: el principio de atomicidad**: Cada atributo en una relación debe representar un valor atómico e indivisible. Si un atributo contiene múltiples valores (una lista, una estructura anidada), viola 1NF y el diseño es defectuoso.

> **P3 - La clave primaria es la identidad de la tupla**: Cada tupla debe ser identificable únicamente por su clave primaria. Si no puedes identificar una tupla unívocamente, no puedes actualizarla ni eliminarla sin riesgo de afectar otras tuplas. Esto es la base de la integridad referencial.

> **P4 - Las dependencias funcionales son las relaciones causales de los datos**: Si A determina B (A → B), entonces dado un valor de A, el valor de B está fijo. Entender las dependencias funcionales de tu schema es el primer paso para diseñar bases de datos correctas.

> **P5 - La denormalización tiene un coste, no es una optimización gratis**: Denormalizar para performance (ej: duplicar datos) introduce anomalías de actualización y requiere triggers o application logic para mantener sincronía. La regla default es normalizar; denormalizar solo cuando hay un problema de performance medible y la solución es denormalización.

## 2. Frameworks y Metodologías

### The Normal Forms

**First Normal Form (1NF)**:
- Cada atributo es atómico (indivisible)
- Cada tupla es única (clave primaria)
- El orden de tuplas no es significativo

**Violation**:
```
❌ Orders (order_id, customer_id, items[])
   items = [item1, item2, item3]  ← No atómico
```

**Correct**:
```
✅ Orders (order_id, customer_id)
   OrderItems (order_id, item_id, quantity)
```

**Second Normal Form (2NF)**:
- Está en 1NF
- Todo atributo no-clave depende completamente de la clave primaria

**Violation**:
```
❌ OrderItems (order_id, item_id, quantity, order_date)
   order_date depende de order_id, no de (order_id, item_id)
```

**Correct**:
```
✅ OrderItems (order_id, item_id, quantity)
   Orders (order_id, order_date)
```

**Third Normal Form (3NF)**:
- Está en 2NF
- No hay dependencias transitivas (A → B → C, donde B no es clave)

**Violation**:
```
❌ Orders (order_id, customer_id, customer_name)
   order_id → customer_id → customer_name (transitiva)
```

**Correct**:
```
✅ Orders (order_id, customer_id)
   Customers (customer_id, customer_name)
```

**Boyce-Codd Normal Form (BCNF)**:
- Versión más estricta de 3NF
- Todo determinante es una clave candidata

**Rara vez necesaria en la práctica**, pero importante entenderla.

### Functional Dependencies

**Definition**: A → B significa que dado un valor de A, el valor de B está determinado.

**Types**:
- **Trivial**: A → A (siempre verdadero)
- **Non-trivial**: A → B where B no es subset de A
- **Multivalued**: A →→ B (one A maps to multiple B values)

**Finding functional dependencies**:
1. Examina business rules
2. "Un customer tiene una dirección" → customer_id → address
3. "Una orden tiene un customer" → order_id → customer_id
4. "Un item tiene un precio" → item_id → price

### The ACID Properties

| Property | Database Implementation |
|----------|------------------------|
| **Atomicity** | Transactions all-or-nothing |
| **Consistency** | Constraints enforced (FK, unique) |
| **Isolation** | Concurrent transactions don't interfere |
| **Durability** | Committed data survives failures |

**SQL Transaction**:
```sql
BEGIN TRANSACTION;

-- Multiple operations
INSERT INTO orders (...) VALUES (...);
INSERT INTO order_items (...) VALUES (...);

COMMIT;  -- ← All or nothing
```

### Keys and Indexes

**Primary Key**: Único identificador de tupla
```sql
PRIMARY KEY (order_id)
```

**Foreign Key**: Referencia a otra tupla
```sql
FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
```

**Unique Key**: Valor único, pero no es primary key
```sql
UNIQUE (email)
```

**Index**: Estructura de búsqueda (B-tree, hash)
```sql
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

**Trade-off**: Índices mejoran reads, penalizan writes.

### Referential Integrity

**Cascade Rules**:
- **CASCADE**: Si parent se borra, borrar children
- **RESTRICT**: No permitir borrar parent si children existen
- **SET NULL**: Set foreign key a NULL si parent se borra
- **SET DEFAULT**: Set foreign key a default value

**Example**:
```sql
FOREIGN KEY (customer_id)
  REFERENCES customers(customer_id)
  ON DELETE RESTRICT
  ON UPDATE CASCADE
```

## 3. Modelos Mentales

### Modelo de "Information Principle"

**Relational model principle**: All information in a relational database is represented explicitly at the logical level in exactly one way: by values in column positions within rows of tables.

**Implication**:
- No hidden pointers (como en bases de datos jerárquicas)
- No duplicate information en múltiples lugares
- No "implicit order" (las filas no tienen orden inherente)

### Modelo de "Closure de Dependencias"

**Algoritmo para encontrar la closure de un conjunto de atributos**:
1. Empieza con el conjunto de atributos dado
2. Agrega atributos que pueden ser derivados vía dependencias funcionales
3. Repetir hasta que no se pueden agregar más

**Example**:
```
Dependencias: A → B, B → C, C → D
Closure(A) = {A, B, C, D}
```

### Modelo de "Lossless Join Decomposition"

**Decomposición**: Dividir una tabla en múltiples tablas más pequeñas
**Lossless**: La reconstrucción (JOIN) produce exactamente la tabla original

**Criterio** (Heath's theorem):
- Si R → S (R determina S), entonces (R, S) es una descomposición lossless de R ∪ S

**Implicación**: Las formas normales garantizan que la descomposición es lossless.

### Modelo de "Anomalías de Actualización"

**Anomalía de actualización**: Debes actualizar múltiples filas para cambiar un hecho
**Anomalía de inserción**: No puedes insertar un hecho sin insertar otro no relacionado
**Anomalía de borrado**: Borrar un hecho borra otro no relacionado

**Solución**: Normalización elimina todas las anomalías.

## 4. Criterios de Decisión

### When to Normalize

| ✅ Always normalize | ⚠️ Consider denormalizing |
|---------------------|-------------------------|
| OLTP (transactional) systems | OLAP (analytical) systems |
| Data integrity is critical | Read performance is critical |
| Frequent writes | Read-heavy, write-light |
- Unknown query patterns | Known query patterns |

### When to Use Composite Keys vs Surrogate Keys

| Composite Key | Surrogate Key |
|---------------|---------------|
| Natural business meaning | Artificial (auto-increment) |
| Multiple columns (order_id, item_id) | Single column (id) |
| Enforces business rules | Simpler joins |
| Can change (business logic change) | Never changes |

**Rule**: Use surrogate keys for simplicity, composite keys when business rules require it.

### Index Selection

**Create index when**:
- Column usado en WHERE clause frecuentemente
- Column usado en JOIN conditions
- Column tiene alta cardinalidad (muchos valores únicos)

**Don't create index when**:
- Table es pequeña (full scan es rápido)
- Column tiene baja cardinalidad (boolean, status)
- Write-heavy workload (índices penalizan writes)

### Many-to-Many Relationships

**Requirement**: Junction table

```
Students (student_id, name)
Courses (course_id, title)
Enrollments (student_id, course_id, grade)
                              ↑
                        Junction table (composite PK)
```

**Nunca** store comma-separated values:
```
❌ Courses (course_id, student_ids)  -- student_ids = "1,2,3"
```

## 5. Anti-patrones

### Anti-patrón: "Violating 1NF" (Storing Lists)

```
❌ Orders (order_id, items)
   items = "[{\"id\": 1, \"qty\": 2}, {\"id\": 2, \"qty\": 1}]"
```

**Solución**:
```
✅ Orders (order_id)
   OrderItems (order_id, item_id, quantity)
```

### Anti-patrón: "Violating 2NF" (Partial Dependencies)

```
❌ OrderItems (order_id, item_id, quantity, customer_name)
   customer_name depende de order_id, no de (order_id, item_id)
```

**Solución**:
```
✅ OrderItems (order_id, item_id, quantity)
   Orders (order_id, customer_id)
   Customers (customer_id, customer_name)
```

### Anti-patrón: "Violating 3NF" (Transitive Dependencies)

```
❌ Orders (order_id, customer_id, customer_name, customer_address)
   order_id → customer_id → customer_name, customer_address
```

**Solución**:
```
✅ Orders (order_id, customer_id)
   Customers (customer_id, customer_name, customer_address)
```

### Anti-patrón: "No Foreign Keys" (Data Orphaning)

```
❌ OrderItems (order_id, item_id)
   -- No foreign key to Orders
```

**Solución**:
```
✅ OrderItems (order_id, item_id,
   FOREIGN KEY (order_id) REFERENCES orders(order_id))
```

### Anti-patrón: "Generic Data Models" (EAV)

```
❌ Attributes (entity_id, attribute_name, attribute_value)
   -- Para cada entidad, store attributes como filas
```

**Problema**: Pierdes todas las garantías de SQL, queries son horribles.

**Solución**: Diseñar schema específico al dominio.

### Anti-patrón: "Ignoring NULLs"

```
❌ Products (id, name, description, optional_field1, optional_field2, ...)
   -- Muchos NULLs para atributos opcionales
```

**Solución**:
- Separa en tablas específicas
- ProductCore, ProductExtended, etc.
- O usa JSONB para attributes verdaderamente variables

### Anti-patrón: "Over-Normalization"

```
❌ Separando todo en tablas minúsculas
   Customers (customer_id)
   CustomerNames (customer_id, name)
   CustomerAddresses (customer_id, address)
   CustomerPhones (customer_id, phone)
```

**Problema**: Joins excesivos, complexity sin beneficio.

**Solución**: Mantén relacionado junto.

### Anti-patrón: "Magic Numbers"

```
❌ Orders (status)
   -- status = 1, 2, 3 (qué significa?)
```

**Solución**:
```
✅ Orders (status_id)
   OrderStatuses (status_id, status_name, description)
   -- status_id = 1 → "Pending"
```

### Anti-patrón: "No Constraints"

**Problema**: Dejando validity a application code.

**Solución**:
```sql
-- Constraints en database
CHECK (price >= 0)
CHECK (quantity > 0)
CHECK (email LIKE '%_@_%_.__%')
```

**Database es la última línea de defensa.**
