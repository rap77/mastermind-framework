---
source_id: "FUENTE-416"
brain: "brain-software-04-frontend"
niche: "software-development"
title: "Progressive Web Apps (PWA) - Complete Developer Guide"
author: "Google Developers"
expert_id: "EXP-416"
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

# Progressive Web Apps - Complete Developer Guide

## 1. Principios Fundamentales

> **P1: Progressive Enhancement** - Las PWAs deben funcionar para todos los usuarios, independientemente del navegador o capabilities del dispositivo.

> **P2: App-like Experience** - El objetivo es brindar una experiencia similar a una app nativa: inmersiva, confiable y rápida.

> **P3: Connectivity-Independent** - Las PWAs deben funcionar con o sin conectividad, usando service workers para caché inteligente.

> **P4: Installable** - Los usuarios deben poder "instalar" la PWA en sus dispositivos, agregándola al home screen.

## 2. Frameworks y Metodologías

### Los 3 Pilares de una PWA

**1. Service Worker**
- JavaScript worker que intercepta requests de red
- Habilita offline-first y caché granular
- Corre en background, independiente del DOM

**2. Manifest JSON**
```json
{
  "name": "Mi App",
  "short_name": "App",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#0066CC",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

**3. HTTPS**
- Requerido para service workers
- Necesario para seguridad y confianza del usuario
- Permitido en localhost para desarrollo

### Estrategias de Caché

| Estrategia | Descripción | Use Cases |
|------------|-------------|-----------|
| Cache First | Sirve desde caché, fallback a red | Assets estáticos |
| Network First | Intenta red, fallback a caché | API requests, HTML |
| Stale While Revalidate | Caché inmediato, actualiza en background | Content que cambia |
| Network Only | Siempre desde red, sin caché | Carrito, datos sensibles |
| Cache Only | Siempre desde caché, error si miss | Shell de app offline |

## 3. Modelos Mentales

**The App Shell Pattern**
- Separar shell (HTML/CSS/JS crítico) del contenido
- Cachear el shell inmediatamente
- Cargar contenido dinámicamente
- Resultado: carga instantánea en visitas repetidas

**Granular Caching Strategy**
- No es "todo o nada" - diferentes estrategias para diferentes recursos
- static assets: cache first, larga duración
- API responses: network first, corta duración
- HTML: network first o stale while revalidate

**Offline-First Thinking**
- Diseñar para offline desde el inicio
- Qué es lo mínimo que el usuario necesita hacer sin red?
- Proveer feedback claro del estado de conectividad
- Queue acciones para sincronizar cuando hay conexión

## 4. Criterios de Decisión

### ¿Cuándo usar PWA?

**Usa PWA si:**
- Necesitas trabajar offline o con conectividad pobre
- Quieres mejorar engagement (tiempo en app)
- Buscas instalación sin pasar por app stores
- Tu audience es principalmente mobile web
- Quieres reducir costos de desarrollo (iOS + Android + Web)

**Considera app nativa si:**
- Necesitas acceso extensivo a hardware APIs
- Tu modelo de negocio depende de app store revenue
- Requieras background processing complejo
- Tus usuarios son principalmente mobile-first y esperan app nativa

### Performance Targets para PWAs

| Métrica | Target | PWA-specific |
|---------|--------|--------------|
| First Contentful Paint | < 1.8s | App shell debe ser < 1s |
| Time to Interactive | < 3.8s | Con service worker: < 2s |
| First Input Delay | < 100ms | Igual que web estándar |
| Lighthouse PWA Score | > 90 | Mide instalación y offline |

## 5. Anti-patrones

❌ **Cachear todo sin estrategia** - Diferentes recursos necesitan diferentes estrategias de caché.

❌ **Olvidar actualizar versiones** - Implementar versioning de service worker para evitar caché obsoleto.

❌ **No manejar errores de red** - Proporcionar feedback claro cuando el usuario está offline y el contenido no está disponible.

❌ **Service worker sin cleanup** - No limpiar cachés antiguas causa llenado de almacenamiento y problemas de versioning.

❌ **Asumir que funciona en todos los browsers** - Siempre feature-detect; proporcionar fallback para browsers sin service worker support.

## Implementación Checklist

### Core Features
- [ ] Service worker registrado e instalado
- [ ] Manifest.json con campos required
- [ ] HTTPS en producción
- [ ] Al menos un icono de 192x192 y uno de 512x512
- [ ] Estrategia de caché implementada
- [ ] Offline page o fallback
- [ ] Actualización de service worker con notificación al usuario

### Enhanced Features
- [ ] Push notifications
- [ ] Background sync
- [ ] Periodic Background Sync
- [ ] App Shortcuts (iOS, Android)
- [ ] Share Target API
- [ ] File System Access API

### Testing
- [ ] Lighthouse PWA audit score > 90
- [ ] Chrome DevTools Application tab verification
- [ ] Offline functionality test (Chrome DevTools Network throttling)
- [ ] Install prompt test en navegadores soportados
- [ ] Cross-browser testing (Chrome, Edge, Safari - con caveats)

## Referencias

- **Google Developers PWA**: https://developers.google.com/web/progressive-web-apps
- **Service Worker Cookbook**: https://serviceworke.rs/
- **Workbox** (Google PWA library): https://developer.chrome.com/docs/workbox
