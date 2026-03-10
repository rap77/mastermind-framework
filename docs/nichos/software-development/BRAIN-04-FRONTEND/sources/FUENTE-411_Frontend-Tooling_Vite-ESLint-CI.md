---
source_id: "FUENTE-411"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "Modern Frontend Tooling: Vite, ESLint, Prettier, Husky, CI/CD & DevTools"
author: "Evan You (Vite) + ESLint Team + Prettier Team + Google DevTools Team"
expert_id: "EXP-411"
type: "documentation"
language: "en"
year: 2024
isbn: "N/A"
url: "https://vitejs.dev + https://eslint.org + https://prettier.io + https://typicode.github.io/husky"
skills_covered: ["H1", "H6", "H7", "H10"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "1.0.0"
    date: "2026-02-26"
    changes:
      - "Ficha creada — gap de tooling ausente en versión inicial; las fuentes anteriores asumen el build system sin enseñarlo"
status: "active"

habilidad_primaria: "Frontend Tooling Moderno — Build, Linting, Formatting, CI/CD"
habilidad_secundaria: "Developer Experience y Pipeline de Calidad Automatizado"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — Las fuentes anteriores del Cerebro #4 enseñan qué construir; esta enseña cómo construirlo eficientemente con las herramientas correctas."
gap_que_cubre: "Tooling moderno de frontend — completamente ausente en las 8 fuentes originales"
---

# FUENTE-411: Modern Frontend Tooling — Vite, ESLint, Prettier, Husky & CI/CD

## Tesis Central

> Las herramientas de desarrollo no son accesorias al código; son el sistema nervioso del equipo. Un setup de tooling mal configurado hace que los bugs lleguen a producción, que el código sea inconsistente, que los builds sean lentos, y que el onboarding de nuevos developers sea frustrante. Un setup correcto hace todo eso imposible por automatización.

La regla del buen tooling: **lo que se puede automatizar, se debe automatizar. Lo que no se puede automatizar, se debe hacer imposible de olvidar.**

---

## 1. Principios Fundamentales

> **P1: Shift Left — Detectar errores lo más temprano posible**
> Un error detectado en el editor cuesta segundos. El mismo error en code review cuesta minutos. En CI, cuesta horas (incluido el tiempo de espera). En producción, cuesta horas + credibilidad. El tooling debe detectar errores en el orden: editor → pre-commit → CI → producción.
> *Aplica a: configuración de ESLint, TypeScript, y pre-commit hooks.*

> **P2: Zero Configuration Like Experience — La configuración por default debe ser correcta**
> Las herramientas modernas (Vite, Prettier) tienen defaults excelentes. Empezar con los defaults y solo cambiar cuando hay una razón específica. Los equipos que personalizan demasiado el tooling desde el día 1 crean complejidad innecesaria.
> *Aplica a: configuración de cualquier herramienta nueva.*

> **P3: Consistencia sobre Preferencia Personal**
> En un proyecto de equipo, la consistencia del estilo importa más que que el estilo sea perfecto según las preferencias de cualquier individuo. Prettier elimina las discusiones de estilo porque es no-negociable: el código se formatea solo.
> *Aplica a: Prettier, ESLint rules sobre estilo.*

> **P4: Los Builds Deben ser Reproducibles**
> El mismo código debe producir el mismo output independientemente de quién hace el build, en qué máquina, y en qué momento. `package-lock.json` (o `yarn.lock`), versiones exactas de dependencias, y Docker para CI garantizan reproducibilidad.
> *Aplica a: configuración de npm/yarn, Dockerfile para CI.*

> **P5: El Pipeline de CI es la Fuente de Verdad**
> "Funciona en mi máquina" no es válido si el CI dice lo contrario. El CI es el árbitro final de si el código está listo para merge. Todo lo que puede romperse en producción debe verificarse en CI.
> *Aplica a: diseño del pipeline de CI/CD.*

---

## 2. Frameworks y Metodologías

### Framework 1: Setup de Proyecto con Vite + React + TypeScript

**Propósito:** Configurar un proyecto moderno con todas las herramientas correctas desde el día 1.

**Paso a paso:**

```bash
# 1. Crear el proyecto base
npm create vite@latest mi-proyecto -- --template react-ts
cd mi-proyecto
npm install

# 2. Instalar ESLint + plugins
npm install -D eslint @eslint/js typescript-eslint eslint-plugin-react-hooks eslint-plugin-jsx-a11y

# 3. Instalar Prettier
npm install -D prettier eslint-config-prettier

# 4. Instalar Husky (pre-commit hooks)
npm install -D husky lint-staged
npx husky init

# 5. Instalar testing
npm install -D vitest @testing-library/react @testing-library/user-event jsdom
```

**Estructura de archivos de configuración:**

```
mi-proyecto/
├── eslint.config.js       # ESLint flat config (v9+)
├── prettier.config.js     # Prettier
├── tsconfig.json          # TypeScript
├── vite.config.ts         # Vite + Vitest
├── .husky/
│   └── pre-commit         # Hook de pre-commit
├── .github/
│   └── workflows/
│       └── ci.yml         # GitHub Actions CI
└── package.json           # Scripts y lint-staged config
```

**Output esperado:** Un proyecto donde el linting, formatting, y tests corren automáticamente en pre-commit y en CI.

---

### Framework 2: Configuración de ESLint Moderno (Flat Config v9+)

**Propósito:** Definir las reglas que el equipo debe seguir, detectadas automáticamente.

```javascript
// eslint.config.js
import js from '@eslint/js';
import tsEslint from 'typescript-eslint';
import reactHooks from 'eslint-plugin-react-hooks';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import prettierConfig from 'eslint-config-prettier';

export default tsEslint.config(
  js.configs.recommended,
  ...tsEslint.configs.recommended,
  {
    plugins: {
      'react-hooks': reactHooks,
      'jsx-a11y': jsxA11y,
    },
    rules: {
      // React Hooks rules (detecta mal uso de hooks)
      ...reactHooks.configs.recommended.rules,

      // Accesibilidad básica
      'jsx-a11y/alt-text': 'error',
      'jsx-a11y/button-has-type': 'error',
      'jsx-a11y/label-has-associated-control': 'error',

      // TypeScript
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],

      // No console.log en producción
      'no-console': ['warn', { allow: ['warn', 'error'] }],
    },
  },
  prettierConfig, // Siempre al final — deshabilita reglas que Prettier maneja
);
```

**Reglas críticas que siempre incluir:**
- `react-hooks/rules-of-hooks`: Detecta llamadas inválidas a hooks
- `react-hooks/exhaustive-deps`: Detecta deps faltantes en `useEffect`
- `@typescript-eslint/no-explicit-any`: Fuerza tipado correcto
- `jsx-a11y/*`: Detecta problemas de accesibilidad en JSX

---

### Framework 3: Pipeline de CI/CD con GitHub Actions

**Propósito:** Garantizar que ningún código roto llega a producción.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci  # ci es más estricto que install — respeta el lockfile

      - name: Type check
        run: npx tsc --noEmit

      - name: Lint
        run: npm run lint

      - name: Format check
        run: npx prettier --check .

      - name: Tests
        run: npm run test -- --coverage

      - name: Build
        run: npm run build

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

**Pre-commit hook con Husky + lint-staged:**
```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md,css}": [
      "prettier --write"
    ]
  }
}
```
```bash
# .husky/pre-commit
npx lint-staged
npx tsc --noEmit --skipLibCheck
```

---

### Framework 4: Configuración de Vite para Performance de Desarrollo

**Propósito:** Maximizar la velocidad del dev server y del build.

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
    },
  },

  build: {
    // Dividir el bundle por vendor (React, etc.) y por chunk de la app
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          query: ['@tanstack/react-query'],
        },
      },
    },
    // Alerta si un chunk supera 500KB
    chunkSizeWarningLimit: 500,
  },

  // Configuración de Vitest inline
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        lines: 80,    // Mínimo 80% cobertura
        functions: 80,
        branches: 70,
      },
    },
  },
});
```

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Shift Left Pyramid** | Los errores cuestan más cuanto más tarde se detectan: editor < pre-commit < CI < producción | Configurar todas las herramientas para detectar en el nivel más temprano posible |
| **Config as Code** | La configuración del tooling es código del proyecto, no configuración personal | Commitear `.eslintrc`, `prettier.config.js`, `.husky/` — si no está en el repo, no existe |
| **Lockfile = Reproducibility** | `package-lock.json` garantiza que todos instalan exactamente las mismas versiones | Siempre usar `npm ci` en CI (no `npm install`), commitear el lockfile |
| **Build = Artifact** | El resultado del build es un artefacto que se despliega; verificarlo en CI antes de deploy | Incluir `npm run build` en CI aunque se corra en el deploy también |
| **Coverage ≠ Quality** | 80% de cobertura puede coexistir con tests que no verifican nada útil | La cobertura es un piso, no un objetivo. Los tests deben verificar comportamiento, no ejecutar líneas |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| ¿Vite o webpack? | Vite | webpack | Vite tiene HMR instantáneo vía ESM nativo. webpack es más lento en dev. Solo usar webpack si hay configs legacy que lo requieren |
| ¿Prettier o ESLint para formato? | Prettier | ESLint con reglas de estilo | Prettier es no-negociable y más rápido. ESLint para reglas de calidad de código |
| ¿npm ci o npm install en CI? | `npm ci` | `npm install` | `npm ci` respeta el lockfile exactamente, es reproducible, y es más rápido en CI |
| ¿Husky pre-commit o pre-push? | `pre-commit` con lint-staged | `pre-push` completo | pre-commit es rápido (solo archivos modificados). pre-push con todos los tests puede ser lento |
| ¿Vitest o Jest? | Vitest en proyectos con Vite | Jest | Vitest comparte la config de Vite, es más rápido, y soporta ESM nativo sin config extra |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| No usar lockfile | Diferentes developers instalan diferentes versiones → bugs que solo pasan en algunas máquinas | Commitear `package-lock.json`, usar `npm ci` en CI |
| ESLint con `--fix --max-warnings 0` en CI | Autofixa en CI en lugar de fallar → oculta los problemas | Solo reportar en CI, autofix solo en pre-commit con lint-staged |
| `any` en TypeScript sin comentario | Pierde todo el beneficio de TypeScript | Usar `unknown` + type guards, o `// eslint-disable-next-line @typescript-eslint/no-explicit-any` con comentario de por qué |
| Scripts de npm sin verificación de tipo | Los tests pasan pero hay errores de TypeScript | Agregar `tsc --noEmit` como paso separado en CI |
| Variables de entorno hardcodeadas | Diferentes valores en dev/staging/prod, y el secreto queda en el código | `.env.local` (gitignored) + `.env.example` (commiteable) + validación con `zod` al iniciar |
| Sin alias de imports (`../../..`) | Imports relativos profundos son frágiles al mover archivos | Configurar `@/` alias en Vite + TypeScript + ESLint |
| Bundle sin code splitting | Todo el código en un solo chunk enorme → primer carga lenta | `manualChunks` en Vite para vendor y chunks grandes |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Airbnb ESLint Config — El Estándar de la Industria

- **Situación:** Airbnb tenía un equipo grande de engineers JavaScript con estilos inconsistentes. Cada code review incluía discusiones sobre estilo de código.
- **Decisión:** Crear y open-sourcear `eslint-config-airbnb` con reglas estrictas basadas en sus best practices reales.
- **Resultado:** Se convirtió en el config de ESLint más descargado de npm. Los equipos que lo usan eliminan prácticamente las discusiones de estilo en code reviews.
- **Lección:** La consistencia de estilo se logra con reglas automáticas, no con guías de estilo que la gente puede ignorar.

### Caso 2: Shopify — Tooling Interno como Producto

- **Situación:** Shopify tiene cientos de frontends con diferentes equipos. Mantener consistencia de tooling era un problema de escala.
- **Decisión:** Crear `@shopify/web-configs` — un paquete que incluye configuraciones compartidas de ESLint, Prettier, TypeScript, y Babel. Un solo comando actualiza el tooling en todos los proyectos.
- **Resultado:** Los equipos dedican menos tiempo a configurar tooling y más a construir features. Las actualizaciones de seguridad de dependencias se propagan automáticamente.
- **Lección:** En empresas con múltiples proyectos frontend, un paquete de configuración compartida es una inversión de alto retorno.

### Caso 3: Vite vs CRA — La Migración que Todos Hacen

- **Situación:** Un equipo tenía una SPA con Create React App (CRA). El cold start del dev server tardaba 45 segundos. Los builds tardaban 4 minutos.
- **Decisión:** Migrar a Vite. El proceso tomó 2 días para un proyecto de tamaño medio.
- **Resultado:** Cold start: 45s → 800ms. Build: 4 minutos → 35 segundos. HMR (hot module replacement): 3-5s → instantáneo.
- **Lección:** La migración a Vite desde CRA o webpack tiene un ROI altísimo en DX (Developer Experience). Es el cambio de tooling más impactante que un equipo puede hacer en 2025.

---

## Conexión con el Cerebro #4

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| Calidad de código consistente | ESLint + Prettier + TypeScript strict como guardianes automáticos |
| Builds reproducibles | Vite config, lockfile, `npm ci` en CI |
| Testing integrado | Vitest configurado con cobertura y umbrales |
| Seguridad de dependencias | `npm audit` en CI, Dependabot para actualizaciones automáticas |
| Onboarding de nuevos developers | Un proyecto bien configurado con tooling tiene `npm install && npm run dev` funcional en minutos |

---

## Preguntas que el Cerebro puede responder

1. ¿Cómo configuro ESLint para que detecte el mal uso de hooks automáticamente?
2. ¿Por qué el build en CI falla aunque funciona en mi máquina?
3. ¿Cómo configuro code splitting para que el bundle no sea tan grande?
4. ¿Cuál es la diferencia entre `npm install` y `npm ci` y por qué importa en CI?
5. ¿Cómo configuro variables de entorno en Vite de forma segura?
6. ¿Cómo configuro Husky para que el pre-commit sea rápido y no moleste a los developers?
7. ¿Cómo migrar de CRA a Vite sin romper nada?
