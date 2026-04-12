# Estandarización de Nichos - 2026-03-10

## Cambios Realizados

### 1. Estructura de Directorios ✅

**Antes:**
```
docs/
├── software-development/
│   ├── 01-product-strategy-brain/
│   └── ...
└── nichos/
    └── marketing-digital/
        └── sources/
            ├── BRAIN-01-STRATEGY/
            └── ...
```

**Después (estándar):**
```
docs/nichos/
├── software-development/
│   ├── BRAIN-01-PRODUCT-STRATEGY/
│   ├── BRAIN-02-UX-RESEARCH/
│   └── ...
└── marketing-digital/
    ├── BRAIN-01-STRATEGY/
    ├── BRAIN-02-BRAND/
    └── ...
```

### 2. Renombramientos

**Software:**
- `01-product-strategy-brain` → `BRAIN-01-PRODUCT-STRATEGY`
- `02-ux-research-brain` → `BRAIN-02-UX-RESEARCH`
- `03-ui-design-brain` → `BRAIN-03-UI-DESIGN`
- `04-frontend-brain` → `BRAIN-04-FRONTEND`
- `05-backend-brain` → `BRAIN-05-BACKEND`
- `06-qa-devops-brain` → `BRAIN-06-QA-DEVOPS`
- `07-growth-data-brain` → `BRAIN-07-GROWTH-DATA`

**Marketing:**
- `BRAIN-03` → `BRAIN-03-CONTENT`
- `BRAIN-04` → `BRAIN-04-SOCIAL-ORGANIC`
- `BRAIN-05` → `BRAIN-05-SOCIAL-PAID`
- `BRAIN-06` → `BRAIN-06-SEARCH-PPC`
- `BRAIN-07` → `BRAIN-07-SEO-TECHNICAL`
- `BRAIN-08` → `BRAIN-08-SEO-CONTENT`
- `BRAIN-09` → `BRAIN-09-EMAIL`
- `BRAIN-10` → `BRAIN-10-RETENTION`
- `BRAIN-11` → `BRAIN-11-ANALYTICS`
- `BRAIN-12` → `BRAIN-12-CRO`
- `BRAIN-13` → `BRAIN-13-OPS`
- `BRAIN-14` → `BRAIN-14-INFLUENCER`
- `BRAIN-15` → `BRAIN-15-COMMUNITY`
- `BRAIN-16` → `BRAIN-16-GROWTH-PARTNER`

### 3. Archivos Creados

- `docs/nichos/TEMPLATE-UNIVERSAL.md` - Template estándar para nichos
- `docs/nichos/marketing-digital/BRAIN-01-STRATEGY/notebook-config.json`
- `docs/nichos/marketing-digital/BRAIN-02-BRAND/notebook-config.json`
- `TECHNICAL-DEBT.md` - Deuda técnica documentada

### 4. Formato Estándar de Fuentes

**Campos obligatorios (v1.1):**
- `habilidad_primaria`: Una frase describiendo la habilidad principal
- `habilidad_secundaria`: Habilidades secundarias
- `capa`: 1-5
- `capa_nombre`: Base Conceptual|Framework Operativo|Modelo Mental|Criterio de Decisión|Mecanismo de Retroalimentación
- `relevancia`: [CRÍTICA|ALTA|MEDIA|BAJA] — Justificación

**Marketing:** ✅ Ya tiene estos campos
**Software:** ⏳ Pendiente (deuda técnica, 122 fuentes)

## Deuda Técnica

**Actualizar 122 fuentes de software** con campos extra.
Guardado en `TECHNICAL-DEBT.md`.
Prioridad: Media.
Hacer después de completar marketing PRP-002/003.

## Estado Actual

| Nicho | Estructura | Formato YAML | Fuentes |
|-------|-----------|--------------|---------|
| Software Development | ✅ Estándar | ⏳ Pendiente | 122 |
| Marketing Digital | ✅ Estándar | ✅ Completo | 15 (M1✅ M2⏳ M3-M8⏳) |

## Próximos Pasos

1. Completar marketing PRP-002 (M2: 5 fuentes faltantes, M3-M8)
2. marketing PRP-003 (M9-M16 + CLI multi-nicho)
3. Volver a deuda técnica: actualizar 122 fuentes de software
