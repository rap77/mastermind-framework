---
source_id: "FUENTE-615"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "GitOps in Practice: Operating Kubernetes Clusters and Cloud Native Infrastructure"
author: "David Kim, Hideto Saito, Scott Z. Nichols, Jason Dobies"
expert_id: "EXP-615"
type: "article"
language: "en"
year: 2023
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from GitOps best practices"
status: "active"
---

# GitOps in Practice

**David Kim, Hideto Saito, Scott Z. Nichols, Jason Dobies**

## 1. Principios Fundamentales

> **P1 - Git como source of truth para infraestructura**: La configuración del cluster, deployments, y environments son código declarativo en Git. Si no está en Git, no existe. La realidad del cluster es solo una manifestación del estado en Git.

> **P2 - Declarativo sobre imperativo**: No dices "hacer X, luego Y". Describes "quiero que el sistema se vea así". El sistema converge automáticamente hacia ese estado deseado. Immutability over mutability.

> **P3 - Desired state = Actual state**: El estado del cluster siempre debería coincidir con lo que está en Git. Si hay drift, se detecta y se corrige automáticamente. No hay configuraciones "ad-hoc" en servidores.

> **P4 - Acceso indirecto al cluster**: Developers nunca hacen `kubectl apply` directamente. Los cambios se hacen vía PRs a Git. Un agent en el cluster aplica los cambios aprobados. Separación de duties: developers propose, operators approve, system applies.

> **P5 - La auditorabilidad está built-in**: Cada cambio tiene un git commit, un autor, un review history. ¿Quién desplegó qué cuándo? `git log` lo sabe. La compliance no es post-facto, es inherente al modelo.

## 2. Frameworks y Metodologías

### The GitOps Workflow

```
1. Developer crea PR con cambios de infraestructura
2. PR review + approvals (automated + human)
3. Merge a main branch
4. GitOps operator detecta cambio
5. Operator aplica cambios al cluster
6. Operator verifica que converge al estado deseado
7. Alerta si hay drift o error
```

### GitOps vs Traditional CI/CD

| Aspecto | Traditional CI/CD | GitOps |
|---------|-------------------|--------|
| **Source of truth** | Kubectl commands, scripts | Git repository |
| **Apply method** | Imperative (kubectl apply) | Declarative (yaml in Git) |
| **Drift detection** | Manual or custom | Built-in (operator) |
| **Rollback** | Manual rollback | Git revert |
| **Audit trail** | CI logs | Git history |
| **Who can deploy** | Anyone with cluster access | Anyone with Git access |
| **Compliance** | Post-hoc review | Pre-merge review |

### The GitOps Toolchain

**Core Components**:

1. **Git Repository**: Contiene manifests (Kubernetes yaml, Helm charts, Terraform)
2. **GitOps Operator**: Corre en cluster, aplica cambios desde Git
3. **CI Pipeline**: Tests + builds + push de artifacts
4. **CD Pipeline**: GitOps operator watching Git

**Tools**:
- **ArgoCD**: Declarative, GitOps continuous delivery
- **Flux**: GitOps operator from CNCF
- **Tekton**: CI/CD pipelines para Kubernetes
- **Helm**: Package manager (compatible con GitOps)
- **Kustomize**: Configuration customization

### ArgoCD Architecture

```
┌─────────────┐
│  Git Repo   │ ← Source of truth
│  (manifests)│
└──────┬──────┘
       │ watch & pull
       ↓
┌─────────────┐
│  ArgoCD     │ ← GitOps operator
│  Controller │
└──────┬──────┘
       │ reconcile
       ↓
┌─────────────┐
│  Kubernetes │ ← Target cluster
│  Cluster    │
└─────────────┘
       ↑
       │ drift detection
       └───────┘
```

**Key concepts**:
- **Application**: Un deployable unit (microservice, cronjob, configmap)
- **Project**: Agrupa aplicaciones, comparte policies
- **Source**: Git repo con manifests
- **Destination**: Cluster + namespace donde deployar
- **Sync**: Estado sincronizado con Git
- **Health**: Health checks de aplicación

### Manifest Strategies

**Strategy 1: Plain YAML**
```
repo/
└── apps/
    ├── deployment.yaml
    ├── service.yaml
    └── ingress.yaml
```
**Pros**: Simple, transparente
**Cons**: Duplicación entre environments

**Strategy 2: Kustomize**
```
repo/
└── apps/
    ├── base/
    │   ├── deployment.yaml
    │   └── service.yaml
    └── overlays/
        ├── dev/
        │   └── kustomization.yaml
        └── prod/
            └── kustomization.yaml
```
**Pros**: Dry (base) + patches (overlays)
**Cons**: Complexity aumenta con tamaño

**Strategy 3: Helm Charts**
```
repo/
└── apps/
    └── myapp/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
            ├── deployment.yaml
            └── service.yaml
```
**Pros**: Paquetizados, reutilizables
**Cons**: Helm learning curve, debugging

### GitOps for Multi-Environment

```
repo/
├── environments/
│   ├── dev/
│   │   ├── app1.yaml
│   │   └── app2.yaml
│   ├── staging/
│   │   ├── app1.yaml
│   │   └── app2.yaml
│   └── prod/
│       ├── app1.yaml
│       └── app2.yaml
└── apps/  # Shared base configs
    └── common/
        └── base-config.yaml
```

**Promotion workflow**: dev → staging → prod via PR promotion or automated promotion.

### Secret Management in GitOps

**Problem**: Secrets can't be in plaintext in Git.

**Solution Options**:

1. **Sealed Secrets** (Bitnami)
   - Encrypt secret for cluster public key
   - Commit sealed secret to Git
   - Controller decrypts in cluster

2. **External Secrets Operator**
   - Secrets stored externally (Vault, AWS Secrets Manager)
   - Operator syncs to cluster
   - Git references secret by name

3. **Mozilla SOPS**
   - Encrypt secrets with GPG/AWS KMS
   - Commit encrypted file to Git
   - Decrypt in pipeline or via admission controller

## 3. Modelos Mentales

### Modelo de "Declarative State Management"

**Imperative** (script):
```bash
kubectl create deployment nginx --image=nginx:1.19
kubectl scale deployment nginx --replicas=3
kubectl expose deployment nginx --port=80
# Cada comando es una mutación
```

**Declarative** (GitOps):
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 3  # Desired state
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.19
```
**Beneficio**: El operator converge automáticamente al estado deseado.

### Modelo de "Infrastructure as Code"

**Traditional**:
- Server configurado manualmente
- "Snowflake servers": cada uno único
- Configuration drift: servers se divergen
- No reproducible

**GitOps / IaC**:
- Infraestructura es código versionado
- "Cattle servers": reemplazables, idénticos
- No drift: estado declarado en Git
- Fully reproducible: `git clone` → `terraform apply`

### Modelo de "Separation of Concerns"

| Role | Responsibilities |
|------|------------------|
| **Developer** | Escribe código, crea PR de infra |
| **Reviewer** | Approva cambios (code + infra) |
| **GitOps Operator** | Aplica cambios, detecta drift |
| **Platform Team** | Configura GitOps operator, policies |

**Beneficio**: Developers deploy sin acceso directo a cluster.

## 4. Criterios de Decisión

### When to Use GitOps

| ✅ GitOps ideal para | ❌ GitOps NO ideal para |
|----------------------|------------------------|
| Kubernetes deployments | Simple VM deployments |
| Multi-cluster management | One-off infrastructure |
| Teams needing self-service | Heavy legacy systems |
| Compliance/audit requirements | Highly dynamic infra (serverless) |
| Declarative infrastructure | Imperative workflows (scripts) |

### GitOps Operator Selection

| Tool | Best For | Trade-offs |
|------|----------|------------|
| **ArgoCD** | Complex multi-cluster apps | Steeper learning curve |
| **Flux** | Simple setups, CD purists | Less feature-rich than ArgoCD |
| **Rudder** | Multi-cloud (K8s + non-K8s) | Newer, less battle-tested |

### Sync Policy: Auto vs Manual

| Auto-Sync | Manual Sync |
|-----------|-------------|
| Merge → deployed immediately | Merge → waiting for approval → sync |
| Faster deployment | Controlled rollout |
| Risk of bad merge reaching prod | Human gate |
| Best for dev/test environments | Best for production |

**Hybrid**: Auto-sync for dev, manual for prod.

### Handling Secrets

| Approach | Pros | Cons |
|----------|------|------|
| **Sealed Secrets** | Kubernetes-native | Requires public key setup |
| **External Secrets** | Centralized secret management | External dependency |
| **SOPS** | Git-friendly encryption | Key management overhead |
| **HashiCorp Vault** | Enterprise-grade | Complex setup |

**Decision**: Start simple (Sealed Secrets), escalate if needed.

### Self-Service for Developers

**Without GitOps**:
- Developer creates ticket to ops
- Ops team deploys manually
- Days/weeks of waiting

**With GitOps**:
- Developer updates YAML in dev folder
- Creates PR, auto-deploys to dev
- Promotes to prod via PR
- Hours instead of weeks

## 5. Anti-patrones

### Anti-patrón: "GitOps Only for Apps"

**Problema**: Usar GitOps para aplicaciones pero no para infraestructura cluster.

**Solución**:
- GitOps para todo: apps + cluster config + monitoring
- Cluster management también en Git (Cluster API, crossplane)

### Anti-patrón: "Large PRs with Many Changes"

**Problema**: PRs monolíticos que tocan 50+ files.

**Solución**:
- Small, focused PRs
- One concern per PR
- Easier review, faster rollback

### Anti-patrón: "Ignoring Drift Detection"

**Problema**: Drift warnings ignorados hasta que algo rompe.

**Solución**:
- Auto-sync or alert on drift
- Don't allow manual cluster changes
- Make Git the only path to production

### Anti-patrón: "Not All Environments in Git"

**Problema**: Prod es GitOps, dev es "kubectl apply manual".

**Solución**:
- Todos los siguen el mismo modelo
- Diferencia es en policies, no en approach

### Anti-patrón: "No Rollback Strategy"

**Problema**: Deployment falla, no hay rollback plan.

**Solución**:
- Git revert = rollback instantáneo
- O mantener versiones anteriores tagged
- ArgoCD "history" feature para rollback

### Anti-patrón: "Approval Bottlenecks"

**Problema**: PRs esperando aprobación por días.

**Solución**:
- Automated approvals for low-risk changes
- Required approvals only for prod/promotions
- CODEOWNERS file para auto-assign reviewers

### Anti-patrón: "Storing Secrets in Plaintext"

**Problema**: Secrets commiteados en plaintext.

**Solución**:
- Implement secret encryption (Sealed Secrets, SOPS)
- Pre-commit hooks para detectar secrets
- GitHooks para bloquear commits con secrets

### Anti-patrón: "GitOps for Everything"

**Problema**: Usar GitOps para workflows que no encajan.

**Solución**:
- GitOps es para infraestructura declarativa
- No todos los problemas son clavos
- Scripting todavía tiene su lugar
