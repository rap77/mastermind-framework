# Rust Control Plane Hardening Plan

## 1. Propósito

Definir la fase corta de endurecimiento necesaria antes de extender o normalizar estructuralmente el control plane Rust canónico.

---

## 2. Tesis central

> Antes de expandir o reubicar el control plane Rust, hay que corregir sus defectos críticos y cerrar los placeholders que afectarían confiabilidad operativa.

---

## 3. Objetivos del hardening

- corregir autenticación/refresh flow
- restaurar o redefinir integración con worker
- limpiar migraciones problemáticas
- cerrar placeholders críticos
- dejar responsabilidades Python vs Rust mejor definidas

---

## 4. Trabajo prioritario

### A. Refresh token flow

Corregir lookup/rotation para no depender de re-hashear bcrypt como si fuera comparable por igualdad.

### B. gRPC / worker integration

Resolver la integración hoy deshabilitada o redefinir un boundary alternativo claro.

### C. Migration hygiene

- ordenar numbering
- revisar dualidades como `003_*`
- validar consistencia de migración de datos

### D. Placeholder handlers

Priorizar cierre de:
- logout placeholder
- DLQ placeholders relevantes
- puntos donde el worker está simulado

### E. Responsibility map

Formalizar qué queda en:
- Python
- Rust

---

## 5. Criterio de salida

El hardening se considera suficiente cuando:

- auth refresh funciona correctamente
- worker boundary no está roto ni ambiguo
- migrations tienen orden confiable
- placeholders críticos ya no afectan el flujo principal
- el servicio puede crecer sin deuda estructural inmediata

---

## 6. Lo que NO incluye

- mover todavía el repo a `apps/control-plane`
- extender todo el runtime multi-provider
- reescribir el producto en Rust

---

## 7. Próximo paso después del hardening

1. normalización de path en monorepo
2. luego extensión del control plane

## Key Learnings:

1. El control plane elegido es correcto, pero aún necesita una fase de estabilización.
2. Hardening primero evita arrastrar defectos al resto de la arquitectura.
3. La normalización del monorepo debe venir después, no antes.
