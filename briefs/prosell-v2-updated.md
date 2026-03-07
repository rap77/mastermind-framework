# BRIEF - ProSell SaaS v2.0 - Re-evaluación

**Fecha:** 2026-03-04
**Objetivo:** Evaluación completa con MasterMind Framework (7 cerebros)
**Contexto:** Re-evaluación con investigación de mercado completa

---

## 1. DESCRIPCIÓN DEL PRODUCTO

**ProSell SaaS** es una plataforma B2B→B2C que actúa como:

> **"Revenue OS para concesionarias - Infraestructura de distribución, inteligencia y cierre"**

### NO es:
- ❌ Un marketplace más (no compite con AutoTrader, Facebook)
- ❌ Un generador de inventario

### SÍ es:
- ✅ Capa de monetización encima de marketplaces existentes
- ✅ Sales-as-a-Service especializado en automotriz
- ✅ Publicación multi-canal gestionada
- ✅ Data & market intelligence

---

## 2. MODELO DE NEGOCIO (CORREGIDO)

### Cliente B2B (Concesionarias)
**Pagan:** 2-4% comisión por venta cerrada + fee base opcional

**Valor:** Incremento de ventas usando los mismos canales

### Cliente B2C (Compradores)
**Pagan:** GRATIS

**Valor:** Mejor experiencia, respuesta rápida, transparencia

### Insight Clave de Validación B2C:
> **60% de compradores NO pagarían comisión directa**
> 3% fue percibido como "demasiado alto"

---

## 3. INVESTIGACIÓN DE MERCADO COMPLETADA

### ✅ Market Research
- **TAM:** $5.4 Trillion USD (global automotriz)
- **SAM:** $1.2T USD (marketplace digital)
- **SOM:** $1M–$3M ARR (100 dealers, 24 meses)
- **Competencia:** AutoTrader, Cars.com, CarGurus, Facebook Marketplace
- **Pricing válido:** 2-4% comisión (alineado con estándares industria)

### ✅ 50 Entrevistas B2B (Concesionarias)

| Hallazgo | Dato |
|----------|------|
| Dispuestos a probar | 68% (26% definitivamente + 42% probablemente) |
| Dolor principal | Gestión y conversión de leads (no falta de leads) |
| Leads mal gestionados | ~43% |
| Sistemas desconectados | 65-80% |
| Gasto actual/mes | $5k–$15k en marketing |

**Comentarios frecuentes:**
- "Tenemos leads, pero más del 40% de oportunidades se escapan"
- "No sabemos qué porcentaje realmente cierra"
- "Pagamos por leads de distintas fuentes, pero sin atribución clara"

### ✅ 20 Conversaciones B2C (Compradores)

| Hallazgo | Dato |
|----------|------|
| Búsqueda empieza en | Google (90%), Facebook (70%), CarGurus (65%) |
| Cómodos agendando online | 85% |
| **NO pagarían comisión** | **60%** |
| Máximo tolerable | $100–$300 fee fijo o 0-1% si hay ahorro |
| Molestia principal | No responden rápido (13/20) |

**Comentario típico:**
> "Si voy a pagar 3%, mejor negocio directamente con el dealer"

---

## 4. PROPUESTA DE VALOR

### Para Concesionarias (B2B):
1. **Publicación multi-canal** - Automatizada en FB, AutoTrader, Cars.com, CarGurus
2. **Gestión de leads** - Centralización omnicanal, scoring, respuesta <60s
3. **Sales-as-a-Service** - Seguimiento, confirmación de citas, recuperación de leads fríos
4. **Data Intelligence** - Scraping precios competidores, dynamic pricing, elasticidad

### Para Compradores (B2C):
1. Experiencia gratuita
2. Respuesta rápida
3. Confirmación de disponibilidad real
4. Transparencia de precios

---

## 5. ESTRUCTURA DE MONETIZACIÓN

### Modelo Híbrido Recomendado:

| Capa | Modelo | Pricing |
|------|--------|---------|
| Publicación gestionada | Fee mensual | $300–$800 según volumen |
| Leads gestionados | Por lead | $20–$60 por lead calificado |
| Ventas cerradas | Comisión | 2–4% sobre ventas atribuidas |

---

## 6. VALIDACIÓN TÉCNICA

### Stack Actual:
- **Frontend:** Next.js 16, React 19, Tailwind 4, Zustand, TanStack Query
- **Backend:** FastAPI (Python 3.13), SQLAlchemy, Pydantic
- **Tests:** 629/629 passing, Pyright 0 errors

### Sprints Completados:
| Sprint | Estado | Entregables |
|--------|--------|-------------|
| 1-2 (Auth) | ✅ COMPLETO | OAuth, 2FA, RBAC |
| 3-4 (Orgs) | ✅ COMPLETO | Teams, Wallet, Upload |
| 5-6 (Productos) | 🔄 EN PROGRESO | CRUD, Galería, VIN Decoder |

---

## 7. MÉTRICAS DEFINIDAS

| Métrica | Objetivo MVP |
|---------|--------------|
| OMTM (Liquidez) | % productos con cita en 30d: >20% |
| Activación B2B | 10 nuevas organizaciones/mes |
| Activación B2C | 1,000 usuarios únicos/mes |
| Citas completadas | 50/mes |
| Show-up rate | >60% |
| CAC B2C | <$50 |

---

## 8. ESTRATEGIA DE DISTRIBUCIÓN

### Uso de BigTech como CANALES (no competidores):
- **Facebook Marketplace** - Distribución de inventario
- **AutoTrader/Cars.com** - Distribución de inventario
- **CarGurus** - Fuente de data competitiva (pricing, días en inventario)

### Ventaja Defendible:
No es tráfico. Es:
1. Data agregada de múltiples plataformas
2. Algoritmo de pricing
3. Data histórica de conversión
4. Procesos optimizados de cierre

---

## 9. PREGUNTAS PARA LOS 7 CEREBROS

### Brain #1 (Product Strategy):
- ¿El modelo B2Cgratis + B2Bcomisión es viable?
- ¿La estructura de monetización híbrida está bien diseñada?
- ¿Qué missing pieces hay en la estrategia?

### Brain #2 (UX Research):
- ¿La investigación B2B/B2C es suficiente? (50 + 20)
- ¿Qué sesgos podrían existir en los datos?
- ¿Qué más validar antes de escalar?

### Brain #3 (UI Design):
- ¿UX para B2B (dealers) vs B2C (compradores)?
- ¿Flujo crítico de agendamiento de citas?

### Brain #4 (Frontend):
- ¿Stack adecuado para marketplace multi-canal?
- ¿Consideraciones de performance?

### Brain #5 (Backend):
- ¿Arquitectura para integración multi-API?
- ¿Sistema de atribución de ventas?

### Brain #6 (QA/DevOps):
- ¿Estrategia de testing para integraciones externas?
- ¿Monitoreo de APIs de terceros?

### Brain #7 (Growth/Data):
- ¿OMTM definido es correcto?
- ¿Experimento piloto (10 dealers) está bien diseñado?
- ¿Unit economics positivos?

---

## 10. ESTADO ACTUAL

- **Framework:** 122/122 fuentes (100%)
- **Desarrollo:** Sprint 5-6 en progreso
- **Tests:** 629/629 passing
- **Investigación:** ✅ Completa (Market Research + 50 B2B + 20 B2C)
- **Veredicto anterior:** CONDITIONAL 100/156 (mejorado de REJECT 18/156)

---

## 11. OBJETIVO DE RE-EVALUACIÓN

**Determinar si con la investigación completa:**
1. El proyecto está listo para APPROVE
2. Faltan elementos críticos
3. Necesita pivote estratégico
4. Debe continuar con desarrollo planificado

---

**Para el orquestador:** Ejecutar flujo `full_product` con los 7 cerebros.
