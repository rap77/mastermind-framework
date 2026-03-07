---
source_id: "FUENTE-617"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "Kubernetes: Up and Running: Deploying and Managing Cloud-Native Applications"
author: "Brendan Burns, Joe Beda, Kelsey Hightower"
expert_id: "EXP-617"
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
      - "Initial distillation from Kubernetes Up and Running"
status: "active"
---

# Kubernetes: Up and Running

**Brendan Burns, Joe Beda, Kelsey Hightower**

## 1. Principios Fundamentales

> **P1 - Kubernetes es un platform for platforms**: No es un PaaS (Platform as a Service) completo. Es un conjunto de primitives para construir plataformas. Si esperas que Kubernetes sea Heroku, te decepcionarás. Si esperas building blocks para crear tu Heroku interno, Kubernetes es para ti.

> **P2 - Declarativo sobre imperativo**: No le dices a Kubernetes "iniciar 3 contenedores". Le declaras "quiero 3 réplicas de este pod". Kubernetes se asegura de que el estado actual coincida con el deseado. Esta convergencia continua es la clave del self-healing.

> **P3 - Labels y selectors son el glue de Kubernetes**: Todos los objetos en Kubernetes están conectados vía labels. Services find pods via labels. ConfigMaps are mounted via labels. Entender labels/selectors es entender Kubernetes.

> **P4 - Los pods son efímeros, no pets**: Los pods mueren. Kubernetes los recrea. No confíes en identidad de pod. Usa services para descubrir pods dinámicamente. Si attachas data a pod (no a persistent volumes), perderás data.

> **P5 - Controllers son el loop de reconciliación**: Cada controller (Deployment, StatefulSet, DaemonSet) corre un loop: "observa estado actual → compara con deseado → actúa para converger". Entender este pattern es entender extensibilidad de Kubernetes (CRDs).

## 2. Frameworks y Metodologías

### Kubernetes Architecture

```
┌─────────────────────────────────────┐
│  Control Plane (Master Node)        │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ API Server   │  │ Scheduler   │ │
│  └──────┬───────┘  └─────────────┘ │
│         │              ┌─────────────┐ │
│         │              │Controller Mgr│ │
│         ↓              └─────────────┘ │
│  ┌────────────────────────────────┐ │
│  │         etcd                   │ │ ← Cluster state
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
                ↕
┌─────────────────────────────────────┐
│  Worker Nodes                       │
│  ┌─────────┐  ┌─────────┐          │
│  │ kubelet │  │kube-proxy│          │
│  └────┬────┘  └────┬────┘          │
│       ↓           ↓                 │
│  ┌─────────┐  ┌─────────┐          │
│  │Pods     │  │Pods     │          │
│  └─────────┘  └─────────┘          │
└─────────────────────────────────────┘
```

**Components**:
- **API Server**: Frontend, valida config, state machine
- **etcd**: Distributed KV store (cluster state)
- **Scheduler**: Assigns pods to nodes
- **Controller Manager**: Runs controllers (deployment, replicaset, etc)
- **kubelet**: Agent on worker nodes, manages pods
- **kube-proxy**: Network proxy, service routing

### Pod: The Atomic Unit

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.19
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

**Key concepts**:
- **Containers in pod**: Share network namespace, storage
- **Restart policy**: Always, OnFailure, Never
- **Resource requests**: Guaranteed minimum
- **Resource limits**: Maximum allowed (OOM kill if exceeded)

### Controllers: Deployment, StatefulSet, DaemonSet

**Deployment** (stateless apps):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:  # Pod template
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.19
```

**StatefulSet** (stateful apps):
- Stable network identity (pod-0, pod-1, pod-2)
- Stable persistent storage
- Ordered, graceful deployment and scaling
- Use for databases, queues, etc.

**DaemonSet** (one pod per node):
- System agents (logging, monitoring)
- Storage daemons (glusterd, ceph)
- Network plugins (calico, weave)

### Service: Discovery and Load Balancing

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx  # ← Match pods via labels
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP  # ClusterIP, NodePort, LoadBalancer
```

**Service types**:
- **ClusterIP**: Cluster-internal only (default)
- **NodePort**: Expose on node IP + port (30000-32767)
- **LoadBalancer**: Cloud provider load balancer
- **ExternalName**: DNS alias (not a proxy)

### ConfigMaps and Secrets

**ConfigMap** (non-sensitive data):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "postgres://localhost:5432/mydb"
  log_level: "info"
```

**Secret** (sensitive data):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  password: cGFzc3dvcmQ=  # base64 encoded
```

**Usage in pod**:
```yaml
envFrom:
  - configMapRef:
      name: app-config
  - secretRef:
      name: app-secret
```

### Namespaces: Multi-Tenancy

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: development
```

**Use cases**:
- Separate environments (dev, staging, prod)
- Team isolation
- Resource quotas per namespace
- Network policies between namespaces

### Resource Quotas and Limits

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
  namespace: development
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
```

**Limits per pod** (via LimitRange):
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
  - default:
      memory: "512Mi"
      cpu: "500m"
    defaultRequest:
      memory: "256Mi"
      cpu: "250m"
```

## 3. Modelos Mentales

### Modelo de "Declarative State Management"

```
Desired State (YAML)
        ↓
   Current State (observed)
        ↓
   Reconciliation loop
        ↓
   Action to converge
```

**Example**:
- Desired: 3 replicas of nginx
- Current: 2 replicas (one crashed)
- Action: Create 1 new replica

**The reconciliation loop runs continuously.**

### Modelo de "Labels as Relational Model"

```
Pods ─────[labels]────→ Services
                        ↑
                      [selector]
```

**Query via labels**:
```bash
kubectl get pods -l app=nginx
kubectl get pods -l environment=production
kubectl get pods -l app=nginx,environment=prod
```

**Dynamic coupling**: Services automatically find new pods with matching labels.

### Modelo de "Pod Lifecycle"

```
Pending → Running → Succeeded/Failed
   ↑
   ↓ (if restart)
Running
```

**Container restart policies**:
- **Always**: Restart container (default)
- **OnFailure**: Restart only on failure
- **Never**: Never restart

**Pod phases**: Pending, Running, Succeeded, Failed, Unknown.

### Modelo de "Network Model"

```
Pod IP (ephemeral)
    ↓
Service IP (stable virtual IP)
    ↓
Ingress / LoadBalancer (external)
```

**Every pod gets its own IP**:
- Pods communicate directly via pod IPs
- No NAT (network address translation) between pods
- Services provide stable IP for dynamic pods

## 4. Criterios de Decisión

### When to Use Deployment vs StatefulSet

| Deployment | StatefulSet |
|------------|-------------|
| Stateless apps | Stateful apps |
| Identical pods | Unique pods (pod-0, pod-1) |
| Ephemeral storage | Stable persistent storage |
| Scaling up/down is fine | Scaling requires care |
| Example: web servers | Example: databases, queues |

### Service Types Selection

| ClusterIP | NodePort | LoadBalancer |
|-----------|----------|--------------|
| Internal only | External access via node IP | External via cloud LB |
| Development/testing | Simple external access | Production external access |
| No cloud dependency | Manual port management | Cloud provider required |

### Resource Requests vs Limits

| Request | Limit | When to use |
|---------|-------|-------------|
| Guaranteed minimum | Maximum allowed | Production: set both |
| Scheduling decision | OOM kill threshold | Dev: requests only |

**Best practice**: Always set requests. Set limits for production.

### When to Use Namespaces

| Use namespaces for | Don't namespace |
|--------------------|----------------|
| Multiple environments | Small clusters |
| Team isolation | Single team |
| Resource quotas | Testing |
| Network policies | Learning |

### HPA (Horizontal Pod Autoscaler) vs VPA (Vertical Pod Autoscaler)

| HPA | VPA |
|-----|-----|
| Scales replicas | Scales resources (CPU/memory) |
| Based on metrics (CPU, custom) | Based on usage history |
| Automatic scaling | Recommendation or auto-apply |
| Production-ready | Beta (use with caution) |

## 5. Anti-patrones

### Anti-patrón: "Golden Images"

**Problema**: Build custom image with everything baked in.

**Solución**:
- Use base images + init containers
- ConfigMaps/Secrets for configuration
- Smaller, more flexible images

### Anti-patrón: "Privileged Containers"

**Problema**: Containers run as root, privileged mode.

**Solución**:
- Run as non-root user
- Drop capabilities
- Use security contexts

### Anti-patrón: "Impedance Mismatch"

**Problema**: Try to make Kubernetes behave like VMs.

**Solución**:
- Embrace pods as ephemeral
- Use services for discovery
- Don't SSH into pods

### Anti-patrón: "Huge Pods"

**Problema**: Multiple containers in one pod doing different things.

**Solución**:
- One concern per container
- Sidecars for logging, monitoring
- Keep pods focused

### Anti-patrón: "Ignoring Liveness and Readiness Probes"

**Problema**: No health checks, Kubernetes doesn't know if pod is healthy.

**Solución**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Anti-patrón: "No Resource Limits"

**Problema**: No limits, one pod can consume entire node resources.

**Solución**:
- Always set requests
- Set limits in production
- Prevent noisy neighbor problem

### Anti-patrón: "kubectl apply Everything"

**Problema**: Manual kubectl commands, no version control.

**Solución**:
- Declarative YAML in Git
- kubectl apply -f directory/
- GitOps for production

### Anti-patrón: "Ignoring Network Policies"

**Problema**: All pods can talk to all pods (default allow).

**Solución**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### Anti-patrón: "Updating Deployments with RollingUpdate"

**Problema**: RollingUpdate is default but not always best.

**Solución**:
- Use Recreate for databases (can't have 2 versions running)
- Use Blue-Green deployment for zero downtime
- Use Canary for gradual rollout

### Anti-patrón: "Using Latest Tag"

**Problema**: `image: nginx:latest` is unpredictable.

**Solución**:
```yaml
image: nginx:1.19.6  # Specific version
# OR
image: nginx@sha256:abc123...  # Digest (immutable)
```
