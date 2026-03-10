---
source_id: "FUENTE-515"
brain: "brain-software-05-backend"
niche: "software-development"
title: "RESTful Web APIs: Developer's Guide to the Serverless Web"
author: "Leonard Richardson, Mike Amundsen, Sam Ruby"
expert_id: "EXP-515"
type: "book"
language: "en"
year: 2013
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from RESTful Web APIs"
status: "active"
---

# RESTful Web APIs

**Leonard Richardson, Mike Amundsen, Sam Ruby**

## 1. Principios Fundamentales

> **P1 - REST es arquitectura, no protocolo**: HTTP es el protocolo, REST es el estilo arquitectónico. No porque uses HTTP significa que tu API es RESTful. REST tiene constraints: client-server, stateless, cacheable, uniform interface, layered system, code-on-demand.

> **P2 - Los recursos son la abstracción clave**: En REST, todo es un recurso. Un recurso es cualquier cosa con identidad: un documento, una colección, un concepto, un proceso. Los recursos se identifican con URIs, se manipulan con representaciones.

> **P3 - Los verbos HTTP tienen significado semántico**: GET es leer, POST es crear, PUT es reemplazar, PATCH es modificar parcialmente, DELETE es eliminar. Usar los verbos correctamente no es ser pedante, es enable caching, proxies, y herramientas.

> **P4 - Stateless es escalabilidad**: El servidor no guarda estado del cliente entre requests. Cada request contiene toda la información necesaria. Esto permite load balancing horizontal, caching, y fault tolerance sin shared state.

> **P5 - Hypermedia is the engine of application state (HATEOAS)**: Un cliente RESTful no necesita hardcodear URLs. El servidor le dice qué puede hacer next via links en la respuesta. Esto evita breaking changes cuando URLs cambian.

## 2. Frameworks y Metodologías

### The Richardson Maturity Model

**Level 0: The Swamp of POX**
- Un endpoint, un método (POST todo)
- XML o JSON sobre HTTP
- No es RESTful, es RPC sobre HTTP

**Level 1: Resources**
- Múltiples endpoints, diferentes recursos
- `/users`, `/orders`, `/products`
- Todavía usa solo POST para todo

**Level 2: HTTP Verbs**
- Usa verbos HTTP correctamente
- GET para leer, POST para crear, PUT/PATCH/DELETE
- La mayoría de las "REST APIs" están aquí

**Level 3: Hypermedia Controls**
- Respuestas incluyen links a recursos relacionados
- El cliente descubre qué puede hacer next
- Verdadero REST, HATEOAS

### Resource Modeling

**Nouns, not verbs**
```
❌ /getUsers
❌ /createUser
❌ /updateUser
❌ /deleteUser

✅ GET    /users       (list)
✅ POST   /users       (create)
✅ GET    /users/123   (read)
✅ PUT    /users/123   (replace)
✅ PATCH  /users/123   (modify)
✅ DELETE /users/123   (delete)
```

**Resource Hierarchies**
```
/users                    → Colección de usuarios
/users/123                → Usuario específico
/users/123/orders         → Órdenes de ese usuario
/users/123/orders/456     → Orden específica de ese usuario
```

**Query Parameters for Filtering**
```
GET /users?role=admin&active=true
GET /orders?status=shipped&since=2024-01-01
GET /products?category=electronics&price_lt=100
```

### HTTP Verbs Semantics

| Verb | Safe? | Idempotent? | Semántica | Response on success |
|------|-------|-------------|-----------|---------------------|
| **GET** | ✅ Yes | ✅ Yes | Leer recurso | 200 + representation |
| **POST** | ❌ No | ❌ No | Crear sub-recurso | 201 + Location header |
| **PUT** | ❌ No | ✅ Yes | Reemplazar recurso | 200/204 |
| **PATCH** | ❌ No | ❌ No | Modificar parcialmente | 200/204 |
| **DELETE** | ❌ No | ✅ Yes | Eliminar recurso | 200/204 |

**Safe**: No modifica estado del servidor (cacheable)
**Idempotent**: Múltiples llamadas = mismo efecto que una

### Status Codes

**2xx: Success**
- `200 OK`: GET/PUT/PATCH success
- `201 Created`: POST created new resource
- `204 No Content`: PUT/DELETE success, no response body

**3xx: Redirection**
- `301 Moved Permanently`: Resource new permanent URL
- `304 Not Modified`: Conditional GET, resource unchanged

**4xx: Client Error**
- `400 Bad Request`: Malformed request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Authenticated but not authorized
- `404 Not Found`: Resource doesn't exist
- `409 Conflict`: Conflict with current state
- `422 Unprocessable Entity`: Semantically incorrect

**5xx: Server Error**
- `500 Internal Server Error`: Bug en servidor
- `503 Service Unavailable**: Temporarily down

### Content Negotiation

```http
GET /users/123
Accept: application/json
```

```http
200 OK
Content-Type: application/json
```

**Supported formats**:
- `application/json` (standard)
- `application/xml` (legacy)
- `text/csv` (data export)

**API version via content type**:
```
Accept: application/vnd.api+json;version=2
```

### HATEOAS (Hypermedia)

**Without HATEOAS**:
```json
{
  "id": 123,
  "name": "Alice"
}
```

**With HATEOAS**:
```json
{
  "id": 123,
  "name": "Alice",
  "_links": {
    "self": { "href": "/users/123" },
    "orders": { "href": "/users/123/orders" },
    "update": { "href": "/users/123", "method": "PUT" }
  }
}
```

**Beneficio**: Cliente descubre acciones disponibles, no hardcodea URLs.

## 3. Modelos Mentales

### Modelo de "Statelessness"

**Stateful (anti-pattern)**:
```
Request 1: POST /login {username, password}
Response: {session_id: abc123}

Request 2: GET /orders
Header: Session: abc123
→ Server busca session en memory/database
```

**Stateless (REST)**:
```
Request 1: POST /api/tokens {username, password}
Response: {token: eyJhbG...}

Request 2: GET /api/orders
Header: Authorization: Bearer eyJhbG...
→ Server valida token, no busca session
```

**Beneficio**: Cualquier server puede manejar cualquier request (load balancing trivial).

### Modelo de "Resource vs Representation"

**Resource**: La entidad abstracta (User #123)
**Representation**: La serialización de ese recurso (JSON, XML)

```
Resource: /users/123 (abstract)

Representations:
- GET /users/123 → JSON
- GET /users/123 → XML
- GET /users/123 → HTML
```

**Un recurso, múltiples representaciones.**

### Modelo de "Uniform Interface"

REST define 4 constraints de interfaz uniforme:

1. **Identification of resources**: URI
2. **Manipulation through representations**: Enviar representación para modificar
3. **Self-descriptive messages**: Media types, HTTP verbs, status codes
4. **Hypermedia as the engine of application state**: HATEOAS

**Beneficio**: Entendimiento universal. No hay APIs "propietarias" en REST real.

### Modelo de "Cacheability"

**GET es cacheable por defecto**:
```
GET /users/123
Cache-Control: max-age=300  → Cache por 5 minutos
```

**POST/PUT/PATCH/DELETE no son cacheables**:
- Modifican estado, no tienen sentido cachear

**Conditional GET**:
```
GET /users/123
If-None-Match: "abc123"  ← ETag del cliente

304 Not Modified  ← Si no cambió
200 OK            ← Si cambió
```

**Beneficio**: Menos load en servidor, mejores response times.

## 4. Criterios de Decisión

### When to Use REST vs GraphQL

| REST | GraphQL |
|------|---------|
| Fixed schema, predictable queries | Flexible queries, overfetching prevention |
| Simple CRUD | Complex data relationships |
| HTTP caching built-in | Caching more complex |
| Standard tooling | Custom tooling |
| Multiple resources per endpoint | Single endpoint, graph query |
| Better for public APIs | Better for complex data fetching |

**Decision**: Default to REST. Consider GraphQL if overfetching/underfetching es un problema real.

### Collection Pagination

**Offset-based**:
```
GET /users?offset=20&limit=10
```
- Simple
- Problems: Items can be skipped/added during pagination

**Cursor-based**:
```
GET /users?cursor=abc123&limit=10
```
- More robust for real-time data
- Can't jump to arbitrary page

**Best practice**: Cursor-based for large/real-time collections.

### API Versioning Strategy

| Strategy | Example | Pros | Cons |
|----------|---------|------|------|
| **URL path** | `/v1/users` | Clear, simple | Breaks when version changes |
| **Header** | `Accept: application/vnd.api.v1+json` | No URL change | Harder to use |
| **Query param** | `/users?version=1` | Easy to test | Not cache-friendly (different URL) |

**Best practice**: URL path versioning (`/v1/`, `/v2/`).

### Error Response Format

**RFC 7807 Problem Details**:
```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request failed validation.",
  "instance": "/users/123",
  "errors": {
    "email": "Invalid email format"
  }
}
```

**Benefits**: Standardized, machine-readable, human-readable.

### Authentication: API Keys vs OAuth2

| API Keys | OAuth2 (Bearer tokens) |
|----------|------------------------|
| Simple to implement | Complex but industry standard |
| No revocation granularity | Fine-grained scopes |
| Shared secret (leak risk) | Per-token revocation |
| Good for server-to-server | Good for user-to-server |

**Decision**: API keys for internal services, OAuth2 for external/user-facing APIs.

## 5. Anti-patrones

### Anti-patrón: "RPC Style Endpoints"

```
❌ /getUsers
❌ /createUser
❌ /updateUser
❌ /deleteUser
```

**Solución**:
```
✅ GET    /users
✅ POST   /users
✅ PATCH  /users/123
✅ DELETE /users/123
```

### Anti-patrón: "Tunneling Everything Through POST"

```
❌ POST /getUsers (body: {filter: "active"})
❌ POST /deleteUser (body: {id: 123})
```

**Solución**:
```
✅ GET /users?filter=active
✅ DELETE /users/123
```

### Anti-patrón: "Ignoring Status Codes"

```
❌ Siempre retorna 200
{
  "success": false,
  "error": "User not found"
}
```

**Solución**:
```
✅ 404 Not Found
{
  "type": "https://api.example.com/errors/not-found",
  "title": "User not found"
}
```

### Anti-patrón: "Version Everything, Always"

**Problema**: `/v1/`, `/v2/`, `/v3/` sin necesidad real.

**Solución**:
- No versiones en v1 (evolución backward compatible)
- Versiones solo para breaking changes
- Deprecated old versions gradualmente

### Anti-patrón: "Returning Internal Data Structures"

**Problema**: API retorna DB schema directly.

**Solución**:
- API contract ≠ DB schema
- DTOs (Data Transfer Objects) como intermediario
- Evita leaking implementation details

### Anti-patrón: "Chatty API"

**Problema**: Cliente hace N requests para N resources.

**Solución**:
- Include related resources (expanding)
- `/users/123?include=orders,payments`
- O GraphQL para queries complejas

### Anti-patrón: "No Rate Limiting"

**Problema**: API sin rate limiting = abuse.

**Solución**:
```
RateLimit-Limit: 1000
RateLimit-Remaining: 999
RateLimit-Reset: 1625097600
```

### Anti-patrón: "Inconsistent Naming**

```
❌ /users vs /Users vs /user_profiles
```

**Solución**:
- Plural nouns for collections
- kebab-case for multi-word: `/user-profiles`
- Consistency is king

### Anti-patrón: "No Pagination for Collections"

**Problema**: `GET /users` retorna 1M+ records.

**Solución**:
- Paginar por default
- `?limit=20&offset=0` o `?cursor=xxx&limit=20`
- Document max limit

### Anti-patrón: "Returning 200 for Errors"

```
❌ 200 OK
{
  "error": true,
  "message": "Invalid input"
}
```

**Solución**:
```
✅ 400 Bad Request
{
  "type": "https://api.example.com/errors/validation",
  "title": "Invalid input",
  "errors": {...}
}
```

### Anti-patrón: "No Documentation"

**Problema**: "El código es la documentación."

**Solución**:
- OpenAPI/Swagger specification
- Interactive API documentation (Swagger UI, Redoc)
- Examples for every endpoint
