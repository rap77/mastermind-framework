---
source_id: "FUENTE-612"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "CI/CD Patterns and Best Practices"
author: "Jez Humble, Martin Fowler"
expert_id: "EXP-612"
type: "article"
language: "en"
year: 2021
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

# CI/CD Patterns and Best Practices

## 1. Principios Fundamentales

> **P1: Build Feedback Loop** - El objetivo principal de CI es reducir el tiempo entre commits y feedback, permitiendo correcciones rápidas.

> **P2: Automate Everything** - Toda tarea manual repetible debe ser automatizada: build, test, deploy, rollback.

> **P3: Deploy Frequently** - Despliegues pequeños y frecuentes reducen el riesgo y facilitan rollbacks.

> **P4: Keep the Pipeline Green** - Un build roto debe tener prioridad máxima sobre todo otro trabajo.

## 2. Frameworks y Metodologías

### Continuous Integration (CI)

**Practices:**
1. **Maintain a Single Source Repository** - Todo el código en un repo
2. **Automate the Build** - Build automatizado y reproducible
3. **Make Self-Testing** - Tests automatizados como parte del build
4. **Everyone Commits Every Day** - Commits frecuentes reducen integration conflicts
5. **Every Commit Should Build** - Main branch debe siempre ser deployable
6. **Fast Feedback** - Build debe completar en minutos, no horas
7. **Test in a Clone of Production** - Test en environment idéntico a producción
8. **Make it Easy to Get the Latest Deliverables** - Artifacts accesibles fácilmente
9. **Everyone Can See What's Happening** - Build status visible (radiators)

### Continuous Delivery (CD)

**Pipeline Stages:**
```yaml
stages:
  build:
    - compile
    - unit_tests
    - package

  test:
    - integration_tests
    - contract_tests
    - security_scan
    - performance_tests

  staging:
    - deploy_to_staging
    - smoke_tests
    - exploratory_testing

  production:
    - deploy_to_production
    - smoke_tests
    - monitor
```

### Deployment Patterns

**Blue-Green Deployment:**
- Two identical production environments
- Deploy to inactive environment
- Test thoroughly
- Switch traffic via router/load balancer
- Instant rollback by switching back

**Canary Deployment:**
- Deploy new version to small subset of users
- Monitor metrics closely
- Gradually increase traffic if healthy
- Rollback instantáneo si hay problemas

**Rolling Deployment:**
- Replace instances gradually (e.g., 25% at a time)
- Health checks before proceeding
- Slower than blue-green but lower infra cost

## 3. Modelos Mentales

**Deployment Pipeline**
El pipeline es la manifestación del proceso de build-deploy-test-release. Cada stage debe agregar confidence.

**Trunk-Based Development**
- Feature flags en lugar de long-lived branches
- Todos commitean a main/trunk
- Short-lived branches (< 1 día)
- Elimina merge hell y integration conflicts

**Infrastructure as Code (IaC)**
- Infrastructure versionada como código
- Changes pasan por same pipeline que app code
- Reproducible environments (dev, staging, prod)
- Terraform, CloudFormation, Pulumi

**GitOps**
- Git como source of truth para infrastructure y deployments
- Pull requests para changes
- Automated sync from git to target environment
- ArgoCD, Flux para Kubernetes

## 4. Criterios de Decisión

### CI/CD Tools Selection

| Tool | Strengths | Weaknesses | Best For |
|------|-----------|------------|----------|
| GitHub Actions | Integración nativa, marketplace | Limited runners for large orgs | Open source, small-medium teams |
| GitLab CI/CD | Built-in, all-in-one | Learning curve | All-in-one Git platform |
| CircleCI | Fast, easy config | Pricing scales quickly | Speed-first teams |
| Jenkins | Highly customizable | Maintenance overhead | Complex, custom pipelines |
| Azure DevOps | Enterprise features | Azure-centric | Microsoft stack |

### Branching Strategies

**Trunk-Based Development:**
- Pros: Simplest, fast integration, no merge conflicts
- Cons: Requires feature flags, disciplined team
- Best: CI/CD mature teams, continuous deployment

**GitHub Flow:**
- Pros: Simple, clean history
- Cons: No explicit staging environment
- Best: SaaS with web-based deployment

**GitLab Flow:**
- Pros: Explicit staging, production branches
- Cons: More complex
- Best: Environments with explicit approval gates

### When to Use Feature Flags
✅ A/B testing
✅ Canaries
✅ Killing features without deployment
✅ Hiding incomplete features
✅ Gradual rollouts

❌ Don't use to avoid testing
❌ Don't leave flags indefinitely (technical debt)

## 5. Anti-patrones

❌ **Long-lived branches** - Branches que viven días/semans crean merge hell y delayed integration pain.

❌ **Skipping tests on main** - Tests en branches pero no en main derrota el propósito de CI.

❌ **Broken windows** - Permitir que el build permanezca roto normaliza mala calidad.

❌ **Manual deployments** - Deployment manual es error-prone, not repeatable, not auditable.

❌ **Testing in production only** - Staging/QA environments necesarios para catching bugs antes de usuarios.

❌ **Infrastructure drift** - Cuando dev/staging/prod no son idénticos, bugs emergen sorpresivamente.

## Metrics and KPIs

**DORA Metrics (High Performers):**
- **Deployment Frequency**: On-demand (multiple per day)
- **Lead Time for Changes**: < 1 hour
- **Time to Restore Service**: < 1 hour
- **Change Failure Rate**: < 15%

**Pipeline Health:**
- Build success rate: > 95%
- Average build time: < 10 minutes
- Test coverage: > 80% (line coverage)
- Flaky test rate: < 2%

**Deployment Metrics:**
- Deployment frequency: deployments per week/day
- Lead time: commit → production time
- MTTR: Mean Time To Restore after failure
- Change failure rate: deployments that require hotfix/rollback

## Security in CI/CD

**DevSecOps Integration:**
- **SAST**: Static Application Security Testing en cada commit
- **SCA**: Software Composition Analysis (dependency vulnerabilities)
- **Container Scanning**: Scan images antes de deploy
- **Secrets Scanning**: Never commit secrets, use vault/env vars
- **Policy as Code**: OPA, Rego para enforce policies

## References

- **Continuous Delivery** (Jez Humble, David Farley)
- **Accelerate** (Nicole Forsgren, Jez Humble, Gene Kim)
- **The Phoenix Project** (Gene Kim, Kevin Behr, George Spafford)
- **Site Reliability Engineering** (Google SRE team)
- **DORA Reports**: https://dora.dev
