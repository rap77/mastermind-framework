---
source_id: "FUENTE-M12-010"
brain: "brain-marketing-12-cro"
niche: "marketing-digital"
title: "Mobile CRO and Core Web Vitals: Speed, UX, and Conversion on Mobile"
author: "Google Web.dev Team"
expert_id: "EXP-M12-010"
type: "guide"
language: "en"
year: 2023
isbn: null
url: "https://web.dev/performance/"
skills_covered: ["H3", "H5", "H7"]
distillation_date: "2026-03-12"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-12"
changelog:
  - version: "1.0.0"
    date: "2026-03-12"
    changes:
      - "Ficha creada con destilación completa"
status: "active"

habilidad_primaria: "Mobile CRO y performance técnica como driver de conversión"
habilidad_secundaria: "Core Web Vitals, page speed, mobile UX, SEO técnico de conversión"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — La velocidad de carga y los Core Web Vitals son factores directos de conversión (y de SEO). Google documenta que cada segundo adicional de carga reduce la conversión entre 7-20%. Para LATAM con conexiones móviles más lentas, este factor es crítico."
---

# FUENTE-M12-010: Mobile CRO y Core Web Vitals (Google Web.dev)

## Tesis Central

> **"La velocidad no es solo un factor técnico — es el CRO más subestimado. Un sitio que carga en 2 segundos convierte el doble que uno que carga en 5 segundos. En LATAM, donde la conectividad móvil es más lenta, la optimización de velocidad es obligatoria para competir."**

---

## 1. Principios Fundamentales

### Core Web Vitals: Las métricas de UX que afectan conversión y SEO

Google define tres métricas de experiencia de usuario como ranking signals:

1. **LCP (Largest Contentful Paint):** Tiempo hasta que carga el elemento principal visible
   - Good: < 2.5 segundos
   - Needs improvement: 2.5-4.0 segundos
   - Poor: > 4.0 segundos

2. **INP (Interaction to Next Paint):** Responsividad a interacciones del usuario
   - Good: < 200ms
   - Needs improvement: 200-500ms
   - Poor: > 500ms

3. **CLS (Cumulative Layout Shift):** Estabilidad visual (¿el contenido se mueve mientras carga?)
   - Good: < 0.1
   - Needs improvement: 0.1-0.25
   - Poor: > 0.25

*Fuente: Google Web.dev, "Core Web Vitals" (2023)*

### El impacto de velocidad en conversión

Datos de Google/Deloitte (estudios de 2022-2023):

| Mejora de velocidad | Impacto en conversión |
|--------------------|-----------------------|
| -0.1s en mobile | +8% conversión |
| -1s en LCP | +7% conversiones en retail |
| LCP < 2.5s vs > 4s | +2x tasa de conversión |
| Cada +1s de carga | -7% conversión promedio |

*Fuente: Google, "The Business Impact of Web Performance" (2022)*

---

## 2. Frameworks y Metodologías

### Framework: Mobile CRO Audit

Checklist de optimización mobile:

**Velocidad:**
- [ ] LCP < 2.5s en mobile (medido en PageSpeed Insights)
- [ ] Imágenes en WebP/AVIF (no JPEG/PNG)
- [ ] Imágenes con lazy loading
- [ ] JS y CSS minificados
- [ ] CDN configurado

**UX Mobile:**
- [ ] Botones de CTA: mínimo 44x44px (touch target)
- [ ] Texto legible sin zoom: mínimo 16px body text
- [ ] Formularios con teclado correcto (numeric, email, tel)
- [ ] Sin popups que bloqueen el contenido en mobile
- [ ] Apple Pay / Google Pay integrado en checkout

**Conversión Mobile:**
- [ ] Checkout en máximo 2 pasos en mobile
- [ ] Sticky CTA en mobile (botón flotante)
- [ ] Autocompletado habilitado en formularios
- [ ] Número de teléfono clickeable (tel: link)

*Fuente: Google Web.dev, "Mobile Performance Checklist" (2023)*

### Framework: PageSpeed Budget

Para mantener velocidad mientras se agregan features:

```
Performance Budget:
├── Total page weight: < 500KB mobile
├── Number of requests: < 50
├── Time to Interactive: < 3.8s en 4G
├── LCP resource: < 150KB
└── JS bundle: < 200KB (parsed)
```

*Fuente: Google Web.dev, "Performance Budget" (2023)*

### Framework: Image Optimization Pipeline

Las imágenes son el mayor contribuyente al peso de página:

```
PROCESO DE OPTIMIZACIÓN:
1. Formato: JPEG→WebP (30-40% más ligero) o AVIF (50-60% más ligero)
2. Dimensiones: Servir al tamaño que se muestra (no imagen 2000px en slot de 400px)
3. Compresión: 80-85% quality en WebP es imperceptible y reduce 40-60%
4. Lazy loading: Imágenes below-the-fold se cargan solo cuando son visibles
5. Responsive images: srcset para servir imagen correcta según dispositivo
```

*Fuente: Google Web.dev, "Image Optimization" (2023)*

---

## 3. Modelos Mentales

### "3 segundos es el umbral de paciencia móvil"

El 53% de los usuarios móviles abandona un sitio que tarda más de 3 segundos en cargar (Google data). En mercados con conectividad más lenta (LATAM), este umbral es aún más crítico.

*Fuente: Google, "Mobile Speed Study" (2022)*

### "La percepción de velocidad importa tanto como la velocidad real"

Técnicas de optimización percibida:
- **Skeleton screens:** Mostrar el layout cargando antes del contenido real (parece más rápido)
- **Optimistic UI:** Actualizar la UI antes de confirmar con el servidor
- **Above-the-fold priority:** Cargar primero lo visible, diferir el resto

*Fuente: Google Web.dev, "Perceived Performance" (2023)*

---

## 4. Criterios de Decisión

### Cuándo priorizar velocidad vs. otras optimizaciones de CRO

Si el LCP > 4 segundos, la optimización de velocidad tiene mayor ROI que cualquier otro cambio de CRO. Es el cuello de botella que limita el impacto de todo lo demás.

**Prioridad:**
1. LCP > 4s → Velocidad primero
2. LCP 2.5-4s → Velocidad + copy/diseño en paralelo
3. LCP < 2.5s → Foco en copy, diseño, y testing

*Fuente: Google Web.dev, "Performance ROI" (2023)*

### Herramientas de medición

| Herramienta | Qué mide | Cuándo usar |
|-------------|---------|-------------|
| **PageSpeed Insights** | CWV en URL específica | Audit inicial |
| **Chrome UX Report** | CWV de usuarios reales | Validación con datos reales |
| **Lighthouse** | CWV + auditoria completa | During development |
| **WebPageTest** | Análisis profundo de waterfall | Debugging de performance |
| **Search Console** | CWV de todo el sitio | Monitoring continuo |

*Fuente: Google Web.dev, "Measurement Tools" (2023)*

---

## 5. Anti-patrones

### Anti-patrón: Optimizar solo en desktop

El tráfico es mayoritariamente mobile pero los equipos de desarrollo tienden a probar en desktop. El LCP en desktop puede ser 2s mientras que en mobile es 8s. Medir siempre en condiciones de red mobile real (Fast 3G throttling en Chrome DevTools).

*Fuente: Google Web.dev, "Mobile First Testing" (2023)*

### Anti-patrón: Popups en mobile que bloquean el contenido

Google penaliza en SEO las páginas con popups que cubren el contenido principal en mobile. Además, destruyen la UX y aumentan el bounce rate. Usar slides in-app o banners en lugar de modales full-screen en mobile.

*Fuente: Google, "Intrusive Interstitials" (2023)*

### Anti-patrón: Cargar scripts de terceros sin control

Cada script de terceros (chat, analytics, remarketing, A/B testing) agrega latencia. Un sitio con 10 scripts de terceros puede tener 2-3 segundos de impacto de terceros en el TTI. Auditar y eliminar scripts no esenciales.

*Fuente: Google Web.dev, "Third-party Scripts" (2023)*
