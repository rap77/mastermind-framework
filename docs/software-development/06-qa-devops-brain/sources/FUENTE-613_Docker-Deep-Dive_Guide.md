---
source_id: "FUENTE-613"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "Docker Deep Dive - Production-Ready Containers"
author: "Docker Inc., CNCF"
expert_id: "EXP-613"
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

# Docker Deep Dive - Production-Ready Containers

## 1. Principios Fundamentales

> **P1: Containers son inmutables** - Una vez creada, una imagen no debe cambiar; deploy nuevas imágenes para cambios.

> **P2: Un proceso por contenedor** - Cada contenedor debe correr un único proceso; no corras multiples servicios en uno.

> **P3: Stateless containers** - Los contenedores deben ser stateless; persiste datos en volumes o servicios externos.

> **P4: Build small images** - Imágenes más pequeñas = más rápidas de pull/build, menor attack surface.

## 2. Frameworks y Metodologías

### Dockerfile Best Practices

**Multi-stage builds:**
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**Layer caching optimization:**
```dockerfile
# MAL: Copia todo y luego instala dependencies
COPY . .
RUN npm install

# BIEN: Instala dependencies primero (cache layer)
COPY package*.json ./
RUN npm install
COPY . .
```

**Non-root user:**
```dockerfile
# Crear usuario no-root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
USER nodejs
```

### Docker Compose para Local Development

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      target: development
    volumes:
      - .:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: app_dev

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 3. Modelos Mentales

**Container como unidad de deploy**
- Cada servicio = un container
- Containers son ephemeral (pueden morir en cualquier momento)
- Orchestration (Kubernetes) maneja lifecycle

**Layers como caché inteligente**
- Cada Dockerfile instruction = una layer
- Layers unchanged se reusen del cache
- Ordenar instructions de más a menos likely-to-change

**Volumes para persistencia**
- Containers son stateless por diseño
- Data persiste en volumes (mapped o named)
- Backup strategy para volumes

**Networks para comunicación**
- Containers en mismo network pueden comunicarse
- Service discovery por nombre de service
- Isolate servicios en diferentes networks

## 4. Criterios de Decisión

### Base Image Selection

| Image | Size | Use Case | Trade-off |
|-------|------|----------|-----------|
| Alpine | ~5MB | Production, constrained environments | Minimal, potential compatibility issues |
| Debian/Ubuntu | ~100MB | General purpose | Balance, más tools |
| Distroless | ~50MB | Security-focused, production | Harder debugging |
| scratch | 0MB | Static binaries, Go/Rust | Absolute minimum |

**Recomendación:** Alpine para development, Distroless para production (cuando sea posible).

### Volume Types

| Type | Use Case | Persistence |
|------|----------|-------------|
| Bind mount | Local development code | Host machine |
| Named volume | Database data | Docker-managed |
| Tmpfs mount | Temporary files | Memory only, lost on stop |

### Network Drivers

| Driver | Use Case | Characteristics |
|--------|----------|-----------------|
| bridge | Default, local containers | Isolated host, containers communicate |
| host | Host networking | Best performance, no isolation |
| overlay | Swarm clusters | Multi-host communication |
| none | Disabled networking | Complete isolation |

## 5. Anti-patrones

❌ **Corrar como root** - Siempre usa non-root user en containers; reduce attack surface.

❌ **Secrets en Dockerfile/ENV** - Usas Docker secrets or vaults; secrets en imágenes son visibles (`docker history`).

❌ **Latest tag** - Usa versiones específicas (`node:20-alpine`, no `node:latest`); latest cambia inesperadamente.

❌ **Grandes imágenes** - Usa multi-stage builds, Alpine, .dockerignore para reducir tamaño.

❌ **Monolithic containers** - Un container = un proceso; múltiples procesos rompen benefits de containers.

❌ **Ignorar healthchecks** - Define HEALTHCHECK en Dockerfile; orchestra necesita saber si el container está vivo.

❌ **Committing containers** - Nunca uses `docker commit`; usa Dockerfiles reproducibles.

❌ **Orphaned volumes** - Limpia volumes no usadas (`docker volume prune`); consumen disk space.

## Production Checklist

### Image Hardening
- [ ] Non-root user (USER instruction)
- [ ] Read-only filesystem (`--read-only` flag)
- [ ] Drop capabilities (`--cap-drop`)
- [ ] Security scanning (Trivy, Snyk)
- [ ] Minimal base image
- [ ] No secrets en imagen
- [ ] Updated base image (patch vulnerabilities)

### Resource Limits
```yaml
resources:
  limits:
    cpus: '0.50'
    memory: 512M
  reservations:
    cpus: '0.25'
    memory: 256M
```

### Healthcheck
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1
```

### Logging Configuration
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

## Docker Security Best Practices

**Image Scanning:**
```bash
# Scan image for vulnerabilities
trivy image myapp:latest

# Scan during CI/CD
docker scan myapp:latest
```

**Run-time security:**
```bash
# Drop all capabilities except needed
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE myapp

# Read-only root filesystem
docker run --read-only --tmpfs /tmp myapp

# No new privileges
docker run --security-opt=no-new-privileges myapp
```

**User namespace remapping:**
```json
{
  "userns-remap": "default"
}
```

## Docker en CI/CD

**Caching layers:**
```yaml
# GitHub Actions example
- name: Build Docker image
  run: |
    docker build -t myapp:${{ github.sha }} .
  # Caches layers automáticamente
```

**Push to registry:**
```bash
docker tag myapp:${SHA} registry.example.com/myapp:${SHA}
docker push registry.example.com/myapp:${SHA}
```

## Troubleshooting

**Debug containers:**
```bash
# Enter running container
docker exec -it <container> sh

# View logs
docker logs -f <container>

# Inspect filesystem
docker export <container> | tar tf -
```

**Common issues:**
- **Permission denied**: Non-root user permission issues
- **Out of space**: Prune images, containers, volumes
- **Network issues**: Check firewall, DNS
- **Slow builds**: Optimize Dockerfile caching

## Referencias

- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **Docker Security**: https://docs.docker.com/engine/security/
- **Dockerfile Reference**: https://docs.docker.com/engine/reference/builder/
- **Docker Compose**: https://docs.docker.com/compose/
