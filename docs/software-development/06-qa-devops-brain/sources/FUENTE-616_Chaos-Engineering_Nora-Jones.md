---
source_id: "FUENTE-616"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "Chaos Engineering: System Resilience through Controlled Experimentation"
author: "Nora Jones, Casey Rosenthal"
expert_id: "EXP-616"
type: "article"
language: "en"
year: 2020
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Chaos Engineering practices"
status: "active"
---

# Chaos Engineering

**Nora Jones, Casey Rosenthal**

## 1. Principios Fundamentales

> **P1 - Los sistemas distribuidos siempre fallan**: Es cuestión de cuándo, no de si. Network partitions, disk failures, process crashes, cascading failures — estos son eventos normales, no excepcionales. Chaos Engineering ayuda a construir sistemas que toleran fallas normales.

> **P2 - No confíes en la intuición, experimenta**: Crees que tu sistema tolera un database crash. ¿Lo probaste? ¿Recientemente? La intuición sobre resiliencia es a veces incorrecta. Los experimentos controlados son la única forma de saber.

> **P3 - El blast radius debe ser controlado**: No rompas producción en el día Black Friday. Los chaos experiments empiezan small, en controlled environments, con rollback plans. La métrica de éxito de chaos engineering no es "rompimos algo", es "aprendimos sin incidente".

> **P4 - La resiliencia se mide en outcomes, no outputs**: No importa que tu health check pase. Importa que los usuarios puedan completar sus journeys. SLA agreements son sobre user experience, no uptime de servicios.

> **P5 - La normalidad es la hipótesis, no el hecho**: "El sistema funciona normalmente" es tu hypothesis. El chaos experiment intenta disprovarla. Si el experimento falla (el sistema se rompe), aprendiste. Si el experimente pasa (el sistema tolera el caos), ganaste confianza.

## 2. Frameworks y Metodologías

### The Chaos Engineering Cycle

```
1. Define "steady state" (normalidad)
2. Hypothesize that system will tolerate chaos
3. Introduce controlled chaos (fault injection)
4. Measure against steady state
5. Learn: Did system recover? Was hypothesis correct?
6. Improve: Fix weaknesses, repeat
```

### Fault Injection Methods

**1. Process-Level Faults**
- Kill specific process/container
- CPU spike (80%+ utilization)
- Memory exhaustion (OOM kill)
- File descriptor exhaustion

**2. Network-Level Faults**
- Packet loss (random drops)
- Increased latency (add 1000ms delay)
- Network partition (isolate service)
- DNS resolution failure

**3. Infrastructure-Level Faults**
- Terminate random EC2 instance
- Detach EBS volume
- Corrupt disk block
- AZ outage simulation

**4. Application-Level Faults**
- Exception injection
- Return error from dependency
- Slow response from dependency
- Invalid data injection

### Tools for Chaos Engineering

| Tool | Type | Use Case |
|------|------|----------|
| **Chaos Monkey** (Netflix) | Random instance termination | Spontaneous failure tolerance |
| **Chaos Mesh** | Kubernetes-native chaos | K8s environments |
| **Gremlin** | SaaS chaos platform | Managed chaos experiments |
| **Litmus** | Kubernetes chaos | Cloud-native experiments |
| **Jepsen** | Distributed systems testing | Database/consistency verification |
| **Toxiproxy** | Network fault simulation | Dependency failure testing |
| **Chaos Engineering Toolkit** | AWS | Cloud provider experiments |

### Steady State Hypothesis

**Definición**: Qué significa "funcionando normalmente"?

**Malas métricas** (outputs):
```
❌ CPU < 70%
❌ Memory < 80%
❌ Process is running
```

**Buenas métricas** (outcomes):
```
✅ 100 requests/sec are processed
✅ P95 latency < 200ms
✅ Error rate < 0.1%
✅ Users can complete checkout flow
```

**SLO (Service Level Objective)**:
- 99.9% uptime (43 min/month downtime)
- P95 latency < 200ms
- Error rate < 0.1%

### Experiment Design Template

```
Experiment: Database Connection Pool Exhaustion
Hypothesis: System can handle 2x connection load

Steady State:
- 1000 req/s, P95 latency < 100ms, error rate < 0.01%

Method:
- Spike DB connections to 2x normal
- Maintain for 5 minutes
- Measure system response

Rollback Plan:
- Kill experiment immediately
- Auto-scale DB if needed
- Page on-call if SLO breaches

Expected Outcome:
- System degrades gracefully (connections queue)
- SLOs maintained or degraded within acceptable range
```

### The Four Signals of Resilience

**Latency**:
- P50, P95, P99 latency
- SLI: 95% of requests < 200ms
- Monitoring: Histograms, heatmaps

**Errors**:
- Error rate (4xx, 5xx)
- SLI: Error rate < 0.1%
- Monitoring: Error counters by type

**Traffic**:
- Requests per second
- Saturation point
- Monitoring: RPS over time

**Saturation**:
- CPU, memory, disk, network
- Queue depths
- SLI: CPU < 80%, memory < 90%

## 3. Modelos Mentales

### Modelo de "Failure Modes"

```
Hardware Failure ──────┐
                       ├──→ System Failure
Software Bug ──────────┤     │
Network Partition ─────┤     ↓
Configuration Error ────┤  User Impact
Human Error ────────────┤     │
                       └─────┘
```

**Chaos Engineering**:
- No previene todas las fallas
- Pero asegura que las fallas no causen user impact
- Resiliencia = tolerancia a fallas

### Modelo de "Blast Radius"

```
Small blast radius:          Large blast radius:
┌──────┐                    ┌─────────────────┐
│ Exp  │                    │        Exp      │
└──────┘                    └─────────────────┘
   ✅ Safe                      ⚠️ Risky
```

**Principle**: Start small, increase gradually.
- Test en dev → test en staging → test en production (off-peak) → test en production (on-peak)

### Modelo de "Graceful Degradation"

**Not binary** (up/down):
```
┌─────────────────────────────────┐
│ 100% functionality              │
│                                 │
│ 90%  functionality (degraded)   │ ← Degraded mode
│                                 │
│ 0%  functionality (down)        │ ← Complete failure
└─────────────────────────────────┘
```

**Degradation strategies**:
- Circuit breaker (stop calling failing dependency)
- Fallback to cache (stale data better than error)
- Feature flags (disable non-critical features)
- Load shedding (reject some requests)

### Modelo de "Mean Time to Recovery (MTTR)"

**DORA metric** (DevOps):
- **Elite**: MTTR < 1 hour
- **High**: MTTR < 1 day
- **Medium**: MTTR < 1 week
- **Low**: MTTR > 1 week

**Chaos Engineering improves MTTR**:
- Practice makes perfect
- Runbooks are tested in real conditions
- On-call knows how to respond

## 4. Criterios de Decisión

### When to Run Chaos Experiments

| ✅ Run chaos experiments | ❌ Don't run chaos experiments |
|-------------------------|------------------------------|
| Production systems with SLAs | Development (no value) |
| Before high-traffic events | During high-traffic events |
| After significant changes | Without monitoring/alerting |
| Regular cadence (weekly/monthly) | Without rollback plan |

### Severity Levels

| Level | Blast Radius | Example |
|-------|--------------|---------|
| **1** | Single service, dev | Kill a dev container |
| **2** | Single service, staging | Kill staging service |
| **3** | Single service, prod (off-peak) | Kill prod service at 3 AM |
| **4** | Multiple services, prod (off-peak) | AZ outage simulation |
| **5** | Critical path, prod (on-peak) | Only after extensive practice |

### GameDays vs Automated Chaos

| GameDay | Automated Chaos |
|---------|-----------------|
| Manual, team learning | Automated, continuous |
| Quarterly/monthly | Daily/weekly |
| Large blast radius | Small blast radius |
| Focus: team response | Focus: system resilience |

**Both are valuable.**

### Hypothesis vs Exploratory Testing

**Hypothesis-Driven**:
- "System will tolerate database latency increase of 500ms"
- Specific, measurable, falsifiable

**Exploratory**:
- "Let's see what happens when we randomly kill things"
- Discovers unknown unknowns

**Start with hypothesis, use exploration for discovery.**

## 5. Anti-patrones

### Anti-patrón: "Chaos without Monitoring"

**Problema**: Rompes algo pero no tienes visibility.

**Solución**:
- Monitoring antes de chaos
- Metrics, logs, tracing en lugar
- Si no puedes medir, no puedes hacer chaos engineering

### Anti-patrón: "Chaos without Rollback Plan"

**Problema**: Experimento rompe producción, no hay plan.

**Solución**:
- Document rollback plan antes de experimento
- Automated rollback triggers
- On-call ready to intervene

### Anti-patrón: "One-Off Chaos"

**Problema**: Haces chaos engineering una vez, nunca más.

**Solución**:
- Regular cadence (weekly/bi-weekly)
- Integrate en CI/CD
- Make chaos engineering part of culture

### Anti-patrón: "Chaos for Chaos Sake"

**Problema**: Experiments sin propósito, learning.

**Solución**:
- Always have hypothesis
- Document learnings
- Share with team

### Anti-patrón: "Only Breaking Things"

**Problema**: Chaos = breaking stuff, not learning.

**Solución**:
- Learning is the goal
- Breaking is the method
- Celebrate learning, not destruction

### Anti-patrón: "Ignoring Team Psychology"

**Problema**: Team hates chaos days, feels unsafe.

**Solución**:
- Psychological safety primero
- Blameless postmortems
- Focus on system weakness, not human error

### Anti-patrón: "Chaos without Stakeholder Buy-In"

**Problema**: Management thinks you're breaking production.

**Solución**:
- Educate on benefits
- Share success stories
- Start small, build trust

### Anti-patrón: "Testing the Wrong Things"

**Problema**: Testing systems that don't matter.

**Solución**:
- Focus on critical paths
- Test what users care about
- Prioritize by impact
