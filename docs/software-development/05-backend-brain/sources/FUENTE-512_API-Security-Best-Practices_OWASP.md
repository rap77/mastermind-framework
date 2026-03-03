---
source_id: "FUENTE-512"
brain: "brain-software-05-backend"
niche: "software-development"
title: "API Security Best Practices - OWASP Guidelines"
author: "OWASP Foundation"
expert_id: "EXP-512"
type: "documentation"
language: "en"
year: 2023
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

# API Security Best Practices

## 1. Principios Fundamentales

> **P1: Never trust client input** - Toda input del cliente debe ser validada, sanitizada y verificada.

> **P2: Defense in depth** - Múltiples capas de seguridad; si una capa falla, otra debe proteger.

> **P3: Principle of least privilege** - Cada usuario/app debe tener el mínimo de permisos necesario.

> **P4: Security by design** - La seguridad debe estar diseñada desde el inicio, no agregada después.

## 2. Frameworks y Metodologías

### OWASP API Security Top 10 (2023)

1. **Broken Object Level Authorization**
   - Verificar ownership del recurso en cada request
   - No confiar en IDs secuenciales o predecibles
   - Implementar proper access control checks

2. **Broken Authentication**
   - Implementar proper token expiration
   - Revoke tokens en logout
   - Rate limiting en auth endpoints

3. **Broken Object Property Level Authorization**
   - Validar cada propiedad individualmente
   - No exponer campos sensibles (admin, internal)

4. **Unrestricted Resource Consumption**
   - Rate limiting por usuario/IP
   - Query result limits (pagination)
   - Timeout protections

5. **Broken Function Level Authorization**
   - Proper role/permission checks
   - No confiar en UI ocultar funcionalidad

6. **Unrestricted Access to Sensitive Business Flows**
   - Validar cada step en workflows críticos
   - Detectar y prevenir automatización maliciosa

7. **Server-Side Request Forgery (SSRF)**
   - Validar y sanitizar URLs
   - Block access a internal resources
   - Network segmentation

8. **Security Misconfiguration**
   - Remove default credentials
   - Disable verbose error messages
   - Keep dependencies updated

9. **Improper Inventory Management**
   - Document all APIs (including shadow APIs)
   - Deprecate old versions properly
   - Monitor for unused/unknown endpoints

10. **Unsafe Consumption of APIs**
    - Validate responses from upstream APIs
    - Proper error handling
    - Don't trust external APIs blindly

### Authentication & Authorization

**JWT Best Practices:**
```yaml
structure:
  header:
    alg: "RS256"  # Asymmetric over HMAC
  payload:
    iss: "api.example.com"
    sub: "user_id"
    exp: "expiration"
    iat: "issued_at"
    jti: "unique_id"
```

- Use strong algorithms (RS256, ES256)
- Short expiration (15-30 min para access tokens)
- Refresh tokens con rotación
- Validate signature en cada request
- Implement token revocation (blocklist)

**OAuth 2.0 Flows:**
| Flow | Use Case | Security Level |
|------|----------|----------------|
| Authorization Code | Server-side apps | High |
| PKCE | Mobile/native apps | High |
| Client Credentials | Machine-to-machine | Medium |
| Implicit | **DEPRECATED** | Low - evitar |

## 3. Modelos Mentales

**API Gateway como Security Boundary**
- Centralized authentication
- Rate limiting
- Input validation
- SSL termination
- WAF integration

**Zero Trust Architecture**
- Nunca confiar, siempre verificar
- Cada request: autenticar, autorizar, auditar
- Micro-segmentación de red
- Assume breach mindset

**Threat Modeling por Endpoint**
Para cada endpoint, preguntar:
1. ¿Qué puede salir mal?
2. ¿Cómo puede un attacker abusar de esto?
3. ¿Qué controles mitigan cada amenaza?

## 4. Criterios de Decisión

### Authentication Strategy

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Public API | API Keys + OAuth | API keys para identificación, OAuth para user data |
| Mobile App | OAuth + PKCE | Prevenir token interception |
| Web App | Session cookies + CSRF | Session cookies HttpOnly, Secure |
| Microservices | mTLS | Mutually authenticated TLS entre services |
| Internal tools | SSO | Centralized identity provider |

### Rate Limiting Strategy

```yaml
per_user:
  default: "100 requests/hour"
  authenticated: "1000 requests/hour"
  premium: "10000 requests/hour"

per_ip:
  unauthenticated: "10 requests/minute"

per_endpoint:
  expensive_operations: "10 requests/hour"
  search: "60 requests/minute"
```

### API Versioning for Security

- **Header-based versioning**: `Accept: application/vnd.api.v2+json`
- **Path-based versioning**: `/api/v2/resource`
- Maintain backwards compatibility cuando sea posible
- Sunset policies: 6+ months notice antes de deprecate

## 5. Anti-patrones

❌ **API Key en URL** - Nunca pases API keys en query params; usas headers (`Authorization: Bearer <key>`).

❌ **Returning sensitive data por error** - Verificar que responses no incluyan passwords, tokens, internal IDs.

❌ **Verbose error messages** - Error details ayudan a attackers; retorna mensajes genéricos en producción.

❌ **CORS mal configurado** - No uses `*` en producción; especifica origins permitidos.

❌ **SQL injection** - Siempre usa parameterized queries/prepared statements; nunca concatenes strings.

❌ **Hardcoded secrets** - Nunca hardcodees API keys, passwords; usa environment variables o secret management.

❌ **Ignoring HTTPS** - HTTPS es mandatory; nunca uses HTTP en producción.

❌ **Trusting client-side validation** - Client validation es UX, no security; siempre valida en server.

## Implementation Checklist

### Authentication
- [ ] Strong passwords policy (min 12 chars, complexity)
- [ ] MFA disponible para sensitive operations
- [ ] Proper session management (timeout, revoke)
- [ ] Secure password storage (bcrypt, Argon2)
- [ ] Account lockout después de failed attempts

### Authorization
- [ ] Role-based access control (RBAC)
- [ ] Resource-level permissions
- [ ] Admin panel acceso restringido
- [ ] Audit logging para sensitive actions

### Data Protection
- [ ] HTTPS everywhere (HSTS enabled)
- [ ] Sensitive data encrypted at rest
- [ ] Sensitive data encrypted in transit (TLS 1.3)
- [ ] PII data properly identified y protected
- [ ] GDPR/privacy compliance

### Input Validation
- [ ] Type checking en todos los inputs
- [ ] Length limits (min/max)
- [ ] Whitelist sobre blacklist
- [ ] SQL injection prevention (prepared statements)
- [ ] XSS prevention (output encoding)

### API Security Headers
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer
Permissions-Policy: geolocation=(), microphone=()
```

## Testing Security

- **SAST**: Static analysis (SonarQube, Semgrep)
- **DAST**: Dynamic testing (OWASP ZAP, Burp Suite)
- **Dependency scanning**: SCA (Snyk, Dependabot)
- **Penetration testing**: Anual o después de cambios mayores
- **Security audits**: Por expertos externos periódicamente

## Referencias

- **OWASP API Security Top 10**: https://owasp.org/www-project-api-security/
- **OWASP ASVS**: Application Security Verification Standard
- **RFC 6749**: OAuth 2.0 Framework
- **RFC 7519**: JSON Web Token (JWT)
