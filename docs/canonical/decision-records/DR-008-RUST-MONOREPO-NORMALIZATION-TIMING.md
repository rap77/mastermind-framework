# DR-008 — Rust Monorepo Normalization Timing

## 1. Decision Metadata

- **Decision ID:** DR-008
- **Date:** 2026-05-23
- **Status:** Approved
- **Related project:** MasterMind
- **Related niche:** Monorepo Structure / Rust Control Plane
- **Related phase / workflow:** Post-Consolidation Cleanup

## 2. Problem Statement

Después de consolidar el código Rust en `rust_control_plane`, queda abierta una pregunta estructural:

- ¿debe moverse ya a una ruta más coherente del monorepo?
- ¿o conviene estabilizarlo primero y normalizar la estructura después?

## 3. Decision Type

- [x] Architecture
- [x] Repo Structure
- [x] Sequencing

## 4. Why This Decision Is Needed

Aunque `rust_control_plane` ya es la única base Rust canónica, su ubicación actual no es la más coherente respecto al resto del monorepo, donde las apps principales viven bajo `apps/`.

Sin embargo, moverlo demasiado pronto introduce riesgo innecesario en:

- Docker
- CI/builds
- paths de proto
- scripts
- documentación
- tooling

## 5. Options Considered

### Option A — Move immediately into `apps/control-plane`

- **Description:** reubicar ahora mismo `rust_control_plane/` a `apps/control-plane/`
- **Benefits:** coherencia inmediata del monorepo
- **Risks:** más riesgo operativo antes del hardening

### Option B — Keep current path for now, normalize after hardening

- **Description:** mantener `rust_control_plane/` como source of truth temporal y moverlo solo después de estabilizar auth, gRPC, migrations y boundaries
- **Benefits:** menor riesgo, mejor secuencia
- **Risks:** inconsistencia estructural temporal

### Option C — Keep current path permanently

- **Description:** no moverlo nunca y aceptar la incoherencia estructural
- **Benefits:** cero churn de paths
- **Risks:** deuda organizacional duradera

## 6. Participating Brains

- Platform Architecture Brain
- Product Operations Brain
- Governance & Safety Brain

## 7. Final Decision

- **Selected option:** Option B
- **Decision owner:** Platform Architecture Brain
- **Decision rationale:** el control plane Rust debe normalizarse dentro del monorepo, pero solo después del hardening de la base canónica para evitar churn prematuro.

## 8. Operational Consequence

### Ahora
- mantener `rust_control_plane/` como fuente oficial
- no moverlo todavía

### Después del hardening
- moverlo a una ruta coherente, idealmente `apps/control-plane/`
- actualizar Docker, CI, proto paths, scripts y docs de forma coordinada

## 9. Preconditions for the move

Antes de normalizar ubicación, deberían estar resueltos como mínimo:

1. fix del refresh token flow
2. definición o restauración de gRPC worker integration
3. limpieza de migrations y placeholders críticos
4. mapa claro Python vs Rust responsibilities

## 10. Reversal Conditions

Revisar esta decisión si:

- el equipo necesita coherencia extrema de paths inmediatamente por tooling
- el hardening tarda demasiado y la inconsistencia empieza a costar más que el move

## 11. Learning Capture

- **Observation:** consolidar implementación y normalizar estructura no siempre deben ocurrir al mismo tiempo.
- **Pattern:** primero eliminar duplicidad, luego estabilizar, luego normalizar ubicación.
- **Heuristic candidate:** no mover un servicio canónico a su ubicación final hasta que su boundary operativo esté razonablemente estable.

## 12. Links / Artifacts

- `docs/canonical/decision-records/DR-007-RUST-CONTROL-PLANE-CONSOLIDATION.md`
- `docs/canonical/42-REPO-INTEGRATION-PLAN.md`

## Key Learnings:

1. La base Rust correcta ya fue elegida; lo que queda pendiente es normalizar su ubicación en el monorepo.
2. Moverla antes del hardening añade más riesgo que valor.
3. La secuencia correcta es: consolidar → endurecer → normalizar.
