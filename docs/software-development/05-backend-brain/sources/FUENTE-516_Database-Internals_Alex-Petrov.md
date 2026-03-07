---
source_id: "FUENTE-516"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Database Internals: A Deep Dive into How Databases Work"
author: "Alex Petrov"
expert_id: "EXP-516"
type: "book"
language: "en"
year: 2019
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Database Internals"
status: "active"
---

# Database Internals

**Alex Petrov**

## 1. Principios Fundamentales

> **P1 - Las B-trees son la estructura de datos por defecto por una razón**: Balanceadas, disk-friendly, range queries eficientes. Hash tables son más rápidos para point lookups pero no soportan range queries. LSM trees son mejores para write-heavy workloads. Elegir la estructura de datos correcta es la decisión más importante de performance.

> **P2 - La latencia de disco es el enemigo principal**: Memoria access = 100ns. Disk seek = 10ms (100,000x más lento). Toda la arquitectura de bases de datos está optimizada para minimizar disk seeks: buffering, sequential writes, batch operations, compaction.

> **P3 - Las transacciones no son magia, son bookkeeping**: ACID es implementado con write-ahead logs (WAL), locking, y MVCC (Multi-Version Concurrency Control). Entender cómo funciona te permite debuggear deadlocks, entender isolation levels, y diseñar schemas transaction-savvy.

> **P4 - El diseño del schema importa más que el hardware**: Un bien diseñado B-tree index puede ser 1000x más rápido que un full scan. Query planing, statistics, y cardinality estimation son más importantes que CPU speed.

> **P5 - Compromiso entre consistencia y availability es inevitable**: CAP theorem no es un bug, es una ley física. No puedes tener perfect consistency y perfect availability en sistemas distribuidos. Elegir qué tradeoff hacer (CP vs AP) es una decisión de diseño, no un failure.

## 2. Frameworks y Metodologías

### Storage Structures

**B-Tree (Balanced Tree)**:
```
                [Root]
              /    |    \
          [A]    [B]    [C]
         / | \   /|\    /|\
      [D][E][F] ...
```

**Características**:
- Balanceada: todas las hojas mismo nivel
- Disk-friendly: tamaños de página alineados a disk blocks
- Range queries eficiente: traverse en orden
- Read-optimized o balanced

**Usos**:
- PostgreSQL indexes (default)
- MySQL InnoDB
- SQL Server
- Most relational databases

**LSM Tree (Log-Structured Merge)**:
```
MemTable (sorted in-memory)
    ↓ flush when full
SSTable 0 (sorted on-disk)
    ↓ merge
SSTable 1 (larger, sorted)
    ↓ merge
SSTable 2 (even larger)
```

**Características**:
- Write-optimized: todos los writes son sequential
- Reads más lentos: buscar en múltiples SSTables
- Compaction en background (merge sort de SSTables)
- No fragmentation, no random writes

**Usos**:
- RocksDB (Facebook)
- LevelDB (Google)
- Cassandra
- HBase
- ClickHouse

**Hash Table**:
```
[key] → [hash] → [bucket] → [value]
```

**Características**:
- O(1) average for point lookups
- No range queries
- Memory-heavy (si en RAM)
- Colision handling (chaining o probing)

**Usos**:
- Memcached
- Redis (hash tables + otras estructuras)
- PostgreSQL hash indexes (raramente usados)
- In-memory databases

### Query Execution

```
SQL Query
    ↓
Parser (SQL → AST)
    ↓
Binder (AST → Query Plan con nombres resueltos)
    ↓
Optimizer (Query Plan → Optimized Plan)
    ↓
Executor (Plan → Resultados)
    ↓
Storage Engine (Data access)
```

**Optimizer types**:
- **Rule-based**: Heurísticas (ej: use index si existe)
- **Cost-based**: Statistics + cardinality estimation
- **Adaptive**: Aprende de queries previas

### Transaction Processing

**ACID Properties**:

| Property | Mechanism |
|----------|-----------|
| **Atomicity** | Write-Ahead Log (WAL) |
| **Consistency** | Constraints + Transactions |
| **Isolation** | Locking o MVCC |
| **Durability** | WAL + fsync |

**Write-Ahead Log (WAL)**:
```
1. Transaction begins
2. Write changes to WAL (sequential)
3. fsync WAL to disk
4. Apply changes to data structures
5. Commit
```

**Si crash durante 4-5**: Replay WAL para recuperar.

**MVCC (Multi-Version Concurrency Control)**:
```
Reader no bloquea Writer
Writer no bloquea Reader

Tabla:
| id | value | tx_start | tx_end |
|----|-------|----------|--------|
| 1  | 10    | 100      | MAX    | ← Visible for tx > 100
| 1  | 20    | 200      | MAX    | ← Visible for tx > 200
```

**Beneficio**: Readers leen snapshot, writers escriben nueva versión.

### Concurrency Control

**Locking (Pessimistic)**:
- Shared lock (S): Readers
- Exclusive lock (X): Writers
- Deadlocks posibles (wait-for graph)

**MVCC (Optimistic)**:
- No locking para reads
- Writers crean nuevas versiones
- Detect conflicts on commit

**Isolation Levels** (SQL standard):

| Level | Phenomena prevented | Performance impact |
|-------|---------------------|-------------------|
| **Read Uncommitted** | None | Fastest |
| **Read Committed** | Dirty reads | Fast |
| **Repeatable Read** | Non-repeatable reads | Medium |
| **Serializable** | Phantom reads | Slowest |

**Most databases**: Read Committed por defecto (PostgreSQL, MySQL).

### Replication

**Primary-Replica (Master-Slave)**:
```
[Primary] → writes → [Replica 1]
                       → [Replica 2]
                       → [Replica 3]
```

- Reads pueden ir a réplicas
- Writes solo a primary
- Async replication (lag posible)
- Failover: replica → primary promotion

**Multi-Leader (Master-Master)**:
```
[Leader 1] ⇄ [Leader 2] ⇄ [Leader 3]
```

- Writes en cualquier leader
- Conflict resolution necesario
- Más complejo, mejor availability

**Leaderless (Dynamo-style)**:
```
[Client] → [Node 1]
         → [Node 2]
         → [Node 3]
```
- Quorum reads/writes (R + W > N)
- Conflict resolution (last-write-wins, CRDTs)
- eventual consistency

## 3. Modelos Mentales

### Modelo de "Disk I/O is the Bottleneck"

```
Memory (RAM): ~100ns access
SSD: ~10-100μs access (100-1000x slower)
HDD: ~10ms access (100,000x slower)
Network: ~100ms access (1,000,000x slower)
```

**Implicaciones**:
- Minimize disk I/O (caching, buffering)
- Sequential I/O > Random I/O (SSD reduces pero no elimina)
- Batch operations cuando sea posible
- Data locality matters (cold cache = slow)

### Modelo de "Write Amplification"

**Writing 1MB puede resultar en 10MB de disk writes**:

```
1. Write to WAL (1MB)
2. Flush to page (4KB + metadata)
3. Index update (varias páginas)
4. Background flush (más páginas)
```

**LSM trees**:
- Amplificación alta en compaction
- Write amplification > 10x es typical

**B-trees**:
- Write amplification menor
- Pero random writes

### Modelo de "Query Plan as Execution Tree"

```
SELECT * FROM users WHERE age > 25 AND city = 'NYC'

Scan Filter
  ↓
Table Scan (users)
  ↓
Filter (age > 25)
  ↓
Filter (city = 'NYC')
```

**With index**:
```
Index Scan (city_index, 'NYC')
  ↓
Filter (age > 25)
  ↓
Table Lookup (por ID)
```

**Index lookup es más rápido si selectividad es alta (< 5% de filas).**

### Modelo de "Buffer Pool as Cache"

```
┌─────────────────────────────┐
│  Buffer Pool (in-memory)    │ ← Hot pages
│  - Recently accessed        │
│  - Pinned pages             │
└─────────────────────────────┘
           ↕ misses
┌─────────────────────────────┐
│  Disk (cold storage)        │ ← Cold pages
└─────────────────────────────┘
```

**LRU (Least Recently Used)**: Evict páginas no usadas recientemente.
**LRU-K**: Considera últimos K accesses.

**Cache hit ratio**: 95%+ es good. < 90% = DB es I/O bound.

## 4. Criterios de Decisión

### When to Use B-Tree vs LSM

| B-Tree | LSM Tree |
|--------|----------|
| Read-heavy | Write-heavy |
| Range queries common | Point lookups common |
| Strong consistency required | Eventual consistency OK |
| PostgreSQL, MySQL, SQL Server | RocksDB, Cassandra, LevelDB |

### When to Normalize vs Denormalize

| Normalize (3NF) | Denormalize |
|-----------------|-------------|
| OLTP (transactional) | OLAP (analytics) |
| Minimize redundancy | Read performance |
| Update-heavy | Read-heavy |
| Data integrity critical | Query speed critical |

**Hybrid**: Normalize for writes, denormalize (materialized views) for reads.

### Index Selection

**Create index when**:
- Column es usada en WHERE clause frecuentemente
- Column tiene alta cardinality (muchos valores únicos)
- Table es grande (> 10K rows)
- Queries son selective (< 5% de filas)

**Don't create index when**:
- Table es pequeña (full scan es rápido)
- Column tiene baja cardinality (boolean, status)
- Write-heavy workload (indices penalizan writes)

**Composite index order**:
- `(a, b)` indexa queries en `a` AND `a, b`
- No indexa queries en solo `b`
- Order matters: `(a, b)` ≠ `(b, a)`

### Partitioning Strategy

| Range Partitioning | Hash Partitioning |
|-------------------|-------------------|
| Partition por rango (ej: fecha) | Partition por hash |
| Queries con range filter eficientes | Distribución uniforme |
| Hotspot risk (un partition más accesado) | No range queries eficientes |

**Cuándo partitionear**:
- Table > 100GB
- Queries filtran por partition key
- Archive old data (drop partition)

## 5. Anti-patrones

### Anti-patrón: "SELECT *"

**Problema**: Trae todas las columnas innecesariamente.

**Solución**:
```sql
-- ❌
SELECT * FROM users WHERE id = 123;

-- ✅
SELECT id, name, email FROM users WHERE id = 123;
```

**Impact**: Menos I/O, menos network traffic, menos memory usage.

### Anti-patrón: "N+1 Query Problem"

```python
# ❌ N+1 queries
users = db.query("SELECT * FROM users")
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")
    # 1 query + N queries = N+1 total
```

**Solución**: JOIN
```python
# ✅ 1 query
users_orders = db.query("""
    SELECT u.*, o.*
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.id
""")
```

### Anti-patrón: "Missing Index on Foreign Key"

**Problema**: JOINs sin index en foreign key = full scan.

**Solución**:
```sql
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

### Anti-patrón: "Over-Normalization"

**Problema**: 7 joins para una query simple.

**Solución**:
- Denormalize para read-heavy queries
- Materialized views para data agregada
- Tradeoff consistency vs performance

### Anti-patrón: "No Statistics"

**Problema**: Query planner no sabe distribución de datos, elige plan malo.

**Solución**:
```sql
ANALYZE TABLE users;  -- PostgreSQL
UPDATE STATISTICS users;  -- SQL Server
```

**Run periodicamente** después de bulk inserts/deletes.

### Anti-patrón: "Large Transactions"

**Problema**: Transactions que duran segundos/minutes.

**Solución**:
- Mantén transactions cortas (< 100ms ideal)
- Long transactions = lock contention
- Split large transaction en varias smaller

### Anti-patrón: "Ignoring Connection Pooling"

**Problema**: Crear nueva conexión por query.

**Solución**:
```python
# ✅ Connection pool
pool = psycopg2.pool.ConnectionPool(...)
conn = pool.getconn()
# Use connection
pool.putconn(conn)
```

**Benefits**: Reuse connections, avoid TCP overhead.

### Anti-patrón: "Not Using Prepared Statements"

**Problema**: Parse query cada vez, SQL injection risk.

**Solución**:
```python
# ✅ Prepared statement
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

**Benefits**: Parsing once, safer from SQL injection, potential plan caching.

### Anti-patrón: "Count(*) on Large Tables"

**Problema**: `SELECT COUNT(*) FROM huge_table` = full scan.

**Solución**:
- Use estimates: `SELECT reltuples FROM pg_class WHERE relname = 'huge_table';`
- Materialized views para precomputed counts
- Approximate counting algorithms (HyperLogLog)

### Anti-patrón: "No Monitoring of Slow Queries"

**Problema**: No sabes qué queries son lentas.

**Solución**:
- Enable slow query log
- PostgreSQL: `log_min_duration_statement = 1000` (ms)
- MySQL: `slow_query_log = ON`
- Regular analysis con `pg_stat_statements`
